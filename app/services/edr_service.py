"""
EDR (Endpoint Detection and Response) integration service
"""
import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import base64
from abc import ABC, abstractmethod

from app.core.database import SessionLocal
from app.models.edr_integration import EDRIntegration, EDREndpoint, EDRAlert, EDRSyncLog, EDRProvider
from app.models.device import Device


class EDRServiceBase(ABC):
    """Base class for EDR service implementations"""
    
    def __init__(self, integration: EDRIntegration):
        self.integration = integration
        self.logger = logging.getLogger(f"services.edr.{integration.provider}")
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the EDR platform"""
        pass
    
    @abstractmethod
    async def get_endpoints(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get endpoints from the EDR platform"""
        pass
    
    @abstractmethod
    async def get_alerts(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get alerts from the EDR platform"""
        pass
    
    @abstractmethod
    def normalize_endpoint_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize endpoint data from EDR platform to standard format"""
        pass
    
    @abstractmethod
    def normalize_alert_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize alert data from EDR platform to standard format"""
        pass


class CrowdStrikeService(EDRServiceBase):
    """CrowdStrike Falcon EDR integration"""
    
    async def authenticate(self) -> bool:
        """Authenticate with CrowdStrike Falcon API"""
        try:
            auth_url = f"{self.integration.api_base_url}/oauth2/token"
            auth_data = {
                'client_id': self.integration.client_id,
                'client_secret': self.integration.client_secret
            }
            
            async with self.session.post(auth_url, data=auth_data) as response:
                if response.status == 200:
                    auth_result = await response.json()
                    self.integration.auth_token = auth_result.get('access_token')
                    return True
                else:
                    self.logger.error(f"CrowdStrike authentication failed: {response.status}")
                    return False
        except Exception as e:
            self.logger.error(f"CrowdStrike authentication error: {e}")
            return False
    
    async def get_endpoints(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get endpoints from CrowdStrike Falcon"""
        try:
            if not await self.authenticate():
                return []
            
            url = f"{self.integration.api_base_url}/devices/queries/devices/v1"
            headers = {
                'Authorization': f'Bearer {self.integration.auth_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'limit': limit,
                'offset': offset
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    device_ids = result.get('resources', [])
                    
                    if not device_ids:
                        return []
                    
                    # Get detailed device information
                    details_url = f"{self.integration.api_base_url}/devices/entities/devices/v2"
                    details_data = {'ids': device_ids}
                    
                    async with self.session.post(details_url, headers=headers, json=details_data) as details_response:
                        if details_response.status == 200:
                            details_result = await details_response.json()
                            return details_result.get('resources', [])
                
                return []
        except Exception as e:
            self.logger.error(f"CrowdStrike get_endpoints error: {e}")
            return []
    
    async def get_alerts(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get alerts from CrowdStrike Falcon"""
        try:
            if not await self.authenticate():
                return []
            
            url = f"{self.integration.api_base_url}/alerts/queries/alerts/v1"
            headers = {
                'Authorization': f'Bearer {self.integration.auth_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'limit': limit,
                'offset': offset
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    alert_ids = result.get('resources', [])
                    
                    if not alert_ids:
                        return []
                    
                    # Get detailed alert information
                    details_url = f"{self.integration.api_base_url}/alerts/entities/alerts/v2"
                    details_data = {'ids': alert_ids}
                    
                    async with self.session.post(details_url, headers=headers, json=details_data) as details_response:
                        if details_response.status == 200:
                            details_result = await details_response.json()
                            return details_result.get('resources', [])
                
                return []
        except Exception as e:
            self.logger.error(f"CrowdStrike get_alerts error: {e}")
            return []
    
    def normalize_endpoint_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize CrowdStrike endpoint data"""
        return {
            'edr_endpoint_id': raw_data.get('device_id'),
            'edr_hostname': raw_data.get('hostname'),
            'edr_ip_addresses': raw_data.get('external_ip') and [raw_data['external_ip']] or [],
            'hostname': raw_data.get('hostname'),
            'operating_system': raw_data.get('os_version'),
            'os_version': raw_data.get('os_version'),
            'architecture': raw_data.get('architecture'),
            'processor': raw_data.get('processor'),
            'memory_gb': raw_data.get('total_memory'),
            'mac_addresses': raw_data.get('mac_address') and [raw_data['mac_address']] or [],
            'agent_version': raw_data.get('agent_version'),
            'agent_status': raw_data.get('status'),
            'last_seen_by_agent': raw_data.get('last_seen'),
            'risk_score': raw_data.get('risk_score'),
            'threat_level': raw_data.get('threat_level'),
            'edr_raw_data': raw_data,
            'edr_tags': raw_data.get('tags', []),
            'edr_groups': raw_data.get('groups', [])
        }
    
    def normalize_alert_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize CrowdStrike alert data"""
        return {
            'edr_alert_id': raw_data.get('id'),
            'edr_incident_id': raw_data.get('incident_id'),
            'alert_type': raw_data.get('technique'),
            'severity': raw_data.get('severity'),
            'status': raw_data.get('status'),
            'title': raw_data.get('title'),
            'description': raw_data.get('description'),
            'threat_name': raw_data.get('threat_name'),
            'threat_type': raw_data.get('threat_type'),
            'threat_category': raw_data.get('threat_category'),
            'detected_at': raw_data.get('created_timestamp'),
            'edr_raw_data': raw_data
        }


class MicrosoftDefenderService(EDRServiceBase):
    """Microsoft Defender for Endpoint integration"""
    
    async def authenticate(self) -> bool:
        """Authenticate with Microsoft Graph API"""
        try:
            auth_url = f"https://login.microsoftonline.com/{self.integration.tenant_id}/oauth2/v2.0/token"
            auth_data = {
                'client_id': self.integration.client_id,
                'client_secret': self.integration.client_secret,
                'scope': 'https://graph.microsoft.com/.default',
                'grant_type': 'client_credentials'
            }
            
            async with self.session.post(auth_url, data=auth_data) as response:
                if response.status == 200:
                    auth_result = await response.json()
                    self.integration.auth_token = auth_result.get('access_token')
                    return True
                else:
                    self.logger.error(f"Microsoft Defender authentication failed: {response.status}")
                    return False
        except Exception as e:
            self.logger.error(f"Microsoft Defender authentication error: {e}")
            return False
    
    async def get_endpoints(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get endpoints from Microsoft Defender for Endpoint"""
        try:
            if not await self.authenticate():
                return []
            
            url = "https://graph.microsoft.com/v1.0/security/machines"
            headers = {
                'Authorization': f'Bearer {self.integration.auth_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                '$top': limit,
                '$skip': offset
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('value', [])
                
                return []
        except Exception as e:
            self.logger.error(f"Microsoft Defender get_endpoints error: {e}")
            return []
    
    async def get_alerts(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get alerts from Microsoft Defender for Endpoint"""
        try:
            if not await self.authenticate():
                return []
            
            url = "https://graph.microsoft.com/v1.0/security/alerts"
            headers = {
                'Authorization': f'Bearer {self.integration.auth_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                '$top': limit,
                '$skip': offset
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('value', [])
                
                return []
        except Exception as e:
            self.logger.error(f"Microsoft Defender get_alerts error: {e}")
            return []
    
    def normalize_endpoint_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Microsoft Defender endpoint data"""
        return {
            'edr_endpoint_id': raw_data.get('id'),
            'edr_hostname': raw_data.get('computerDnsName'),
            'edr_ip_addresses': raw_data.get('ipAddresses', []),
            'hostname': raw_data.get('computerDnsName'),
            'operating_system': raw_data.get('osPlatform'),
            'os_version': raw_data.get('osVersion'),
            'architecture': raw_data.get('processorArchitecture'),
            'processor': raw_data.get('processor'),
            'memory_gb': raw_data.get('totalMemorySize'),
            'mac_addresses': raw_data.get('macAddresses', []),
            'agent_version': raw_data.get('agentVersion'),
            'agent_status': raw_data.get('healthStatus'),
            'last_seen_by_agent': raw_data.get('lastSeen'),
            'risk_score': raw_data.get('riskScore'),
            'threat_level': raw_data.get('threatLevel'),
            'edr_raw_data': raw_data,
            'edr_tags': raw_data.get('tags', []),
            'edr_groups': raw_data.get('machineGroups', [])
        }
    
    def normalize_alert_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Microsoft Defender alert data"""
        return {
            'edr_alert_id': raw_data.get('id'),
            'edr_incident_id': raw_data.get('incidentId'),
            'alert_type': raw_data.get('alertType'),
            'severity': raw_data.get('severity'),
            'status': raw_data.get('status'),
            'title': raw_data.get('title'),
            'description': raw_data.get('description'),
            'threat_name': raw_data.get('threatDisplayName'),
            'threat_type': raw_data.get('threatType'),
            'threat_category': raw_data.get('category'),
            'detected_at': raw_data.get('createdDateTime'),
            'edr_raw_data': raw_data
        }


class SentinelOneService(EDRServiceBase):
    """SentinelOne EDR integration"""
    
    async def authenticate(self) -> bool:
        """Authenticate with SentinelOne API"""
        try:
            auth_url = f"{self.integration.api_base_url}/web/api/v2.1/users/login"
            auth_data = {
                'username': self.integration.client_id,
                'password': self.integration.client_secret
            }
            
            async with self.session.post(auth_url, data=auth_data) as response:
                if response.status == 200:
                    auth_result = await response.json()
                    self.integration.auth_token = auth_result.get('data', {}).get('token')
                    return True
                else:
                    self.logger.error(f"SentinelOne authentication failed: {response.status}")
                    return False
        except Exception as e:
            self.logger.error(f"SentinelOne authentication error: {e}")
            return False
    
    async def get_endpoints(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get endpoints from SentinelOne"""
        try:
            if not await self.authenticate():
                return []
            
            url = f"{self.integration.api_base_url}/web/api/v2.1/agents"
            headers = {
                'Authorization': f'ApiToken {self.integration.auth_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'limit': limit,
                'offset': offset
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('data', [])
                
                return []
        except Exception as e:
            self.logger.error(f"SentinelOne get_endpoints error: {e}")
            return []
    
    async def get_alerts(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get alerts from SentinelOne"""
        try:
            if not await self.authenticate():
                return []
            
            url = f"{self.integration.api_base_url}/web/api/v2.1/threats"
            headers = {
                'Authorization': f'ApiToken {self.integration.auth_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'limit': limit,
                'offset': offset
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('data', [])
                
                return []
        except Exception as e:
            self.logger.error(f"SentinelOne get_alerts error: {e}")
            return []
    
    def normalize_endpoint_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize SentinelOne endpoint data"""
        return {
            'edr_endpoint_id': raw_data.get('id'),
            'edr_hostname': raw_data.get('computerName'),
            'edr_ip_addresses': raw_data.get('networkInterfaces', {}).get('inet', []),
            'hostname': raw_data.get('computerName'),
            'operating_system': raw_data.get('osType'),
            'os_version': raw_data.get('osVersion'),
            'architecture': raw_data.get('architecture'),
            'processor': raw_data.get('cpuId'),
            'memory_gb': raw_data.get('totalMemory'),
            'mac_addresses': raw_data.get('networkInterfaces', {}).get('physical', []),
            'agent_version': raw_data.get('agentVersion'),
            'agent_status': raw_data.get('agentStatus'),
            'last_seen_by_agent': raw_data.get('lastActiveDate'),
            'risk_score': raw_data.get('threatCount'),
            'threat_level': raw_data.get('threatLevel'),
            'edr_raw_data': raw_data,
            'edr_tags': raw_data.get('tags', []),
            'edr_groups': raw_data.get('groupName', [])
        }
    
    def normalize_alert_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize SentinelOne alert data"""
        return {
            'edr_alert_id': raw_data.get('id'),
            'edr_incident_id': raw_data.get('incidentId'),
            'alert_type': raw_data.get('threatType'),
            'severity': raw_data.get('threatLevel'),
            'status': raw_data.get('status'),
            'title': raw_data.get('threatName'),
            'description': raw_data.get('threatDescription'),
            'threat_name': raw_data.get('threatName'),
            'threat_type': raw_data.get('threatType'),
            'threat_category': raw_data.get('threatCategory'),
            'detected_at': raw_data.get('createdAt'),
            'edr_raw_data': raw_data
        }


class TrendMicroService(EDRServiceBase):
    """TrendMicro Vision One EDR integration"""
    
    async def authenticate(self) -> bool:
        """Authenticate with TrendMicro Vision One API"""
        try:
            auth_url = f"{self.integration.api_base_url}/v3.0/auth/token"
            headers = {
                'Authorization': f'Bearer {self.integration.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.post(auth_url, headers=headers) as response:
                if response.status == 200:
                    auth_result = await response.json()
                    self.integration.auth_token = auth_result.get('access_token')
                    return True
                else:
                    self.logger.error(f"TrendMicro authentication failed: {response.status}")
                    return False
        except Exception as e:
            self.logger.error(f"TrendMicro authentication error: {e}")
            return False
    
    async def get_endpoints(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get endpoints from TrendMicro Vision One"""
        try:
            if not await self.authenticate():
                return []
            
            url = f"{self.integration.api_base_url}/v3.0/endpoints"
            headers = {
                'Authorization': f'Bearer {self.integration.auth_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'limit': limit,
                'offset': offset
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('data', [])
                
                return []
        except Exception as e:
            self.logger.error(f"TrendMicro get_endpoints error: {e}")
            return []
    
    async def get_alerts(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get alerts from TrendMicro Vision One"""
        try:
            if not await self.authenticate():
                return []
            
            url = f"{self.integration.api_base_url}/v3.0/alerts"
            headers = {
                'Authorization': f'Bearer {self.integration.auth_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'limit': limit,
                'offset': offset
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('data', [])
                
                return []
        except Exception as e:
            self.logger.error(f"TrendMicro get_alerts error: {e}")
            return []
    
    def normalize_endpoint_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize TrendMicro endpoint data"""
        return {
            'edr_endpoint_id': raw_data.get('id'),
            'edr_hostname': raw_data.get('hostname'),
            'edr_ip_addresses': raw_data.get('ipAddresses', []),
            'hostname': raw_data.get('hostname'),
            'operating_system': raw_data.get('osName'),
            'os_version': raw_data.get('osVersion'),
            'architecture': raw_data.get('architecture'),
            'processor': raw_data.get('processor'),
            'memory_gb': raw_data.get('memorySize'),
            'mac_addresses': raw_data.get('macAddresses', []),
            'agent_version': raw_data.get('agentVersion'),
            'agent_status': raw_data.get('status'),
            'last_seen_by_agent': raw_data.get('lastSeen'),
            'risk_score': raw_data.get('riskScore'),
            'threat_level': raw_data.get('threatLevel'),
            'edr_raw_data': raw_data,
            'edr_tags': raw_data.get('tags', []),
            'edr_groups': raw_data.get('groups', [])
        }
    
    def normalize_alert_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize TrendMicro alert data"""
        return {
            'edr_alert_id': raw_data.get('id'),
            'edr_incident_id': raw_data.get('incidentId'),
            'alert_type': raw_data.get('alertType'),
            'severity': raw_data.get('severity'),
            'status': raw_data.get('status'),
            'title': raw_data.get('title'),
            'description': raw_data.get('description'),
            'threat_name': raw_data.get('threatName'),
            'threat_type': raw_data.get('threatType'),
            'threat_category': raw_data.get('category'),
            'detected_at': raw_data.get('createdAt'),
            'edr_raw_data': raw_data
        }


class EDRIntegrationService:
    """Service for managing EDR integrations"""
    
    def __init__(self):
        self.logger = logging.getLogger("services.edr_integration")
    
    def get_edr_service(self, integration: EDRIntegration) -> EDRServiceBase:
        """Get the appropriate EDR service implementation"""
        if integration.provider == EDRProvider.CROWDSTRIKE:
            return CrowdStrikeService(integration)
        elif integration.provider == EDRProvider.MICROSOFT_DEFENDER:
            return MicrosoftDefenderService(integration)
        elif integration.provider == EDRProvider.SENTINELONE:
            return SentinelOneService(integration)
        elif integration.provider == EDRProvider.TRENDMICRO:
            return TrendMicroService(integration)
        else:
            raise ValueError(f"Unsupported EDR provider: {integration.provider}")
    
    async def sync_integration(self, integration_id: str) -> Dict[str, Any]:
        """Sync data from an EDR integration"""
        db = SessionLocal()
        try:
            integration = db.query(EDRIntegration).filter(EDRIntegration.id == integration_id).first()
            if not integration:
                raise ValueError("EDR integration not found")
            
            if not integration.is_active:
                raise ValueError("EDR integration is not active")
            
            # Create sync log
            sync_log = EDRSyncLog(
                integration_id=integration_id,
                sync_type="endpoints",
                status="started"
            )
            db.add(sync_log)
            db.commit()
            
            start_time = datetime.utcnow()
            records_processed = 0
            records_created = 0
            records_updated = 0
            records_failed = 0
            
            try:
                edr_service = self.get_edr_service(integration)
                
                async with edr_service:
                    # Sync endpoints
                    if integration.sync_endpoints:
                        endpoints_data = await edr_service.get_endpoints()
                        records_processed += len(endpoints_data)
                        
                        for endpoint_data in endpoints_data:
                            try:
                                normalized_data = edr_service.normalize_endpoint_data(endpoint_data)
                                
                                # Check if endpoint already exists
                                existing_endpoint = db.query(EDREndpoint).filter(
                                    EDREndpoint.integration_id == integration_id,
                                    EDREndpoint.edr_endpoint_id == normalized_data['edr_endpoint_id']
                                ).first()
                                
                                if existing_endpoint:
                                    # Update existing endpoint
                                    for key, value in normalized_data.items():
                                        if hasattr(existing_endpoint, key):
                                            setattr(existing_endpoint, key, value)
                                    existing_endpoint.last_updated = datetime.utcnow()
                                    records_updated += 1
                                else:
                                    # Create new endpoint
                                    endpoint = EDREndpoint(
                                        integration_id=integration_id,
                                        company_id=integration.company_id,
                                        site_id=integration.site_id,
                                        **normalized_data
                                    )
                                    db.add(endpoint)
                                    records_created += 1
                                
                                # Try to match with existing device
                                if normalized_data.get('edr_ip_addresses'):
                                    for ip in normalized_data['edr_ip_addresses']:
                                        device = db.query(Device).filter(Device.ip == ip).first()
                                        if device:
                                            endpoint.device_id = device.id
                                            # Update device with EDR data
                                            if normalized_data.get('operating_system'):
                                                device.operating_system = normalized_data['operating_system']
                                            if normalized_data.get('hostname'):
                                                device.hostname = normalized_data['hostname']
                                            break
                                
                            except Exception as e:
                                self.logger.error(f"Failed to process endpoint {endpoint_data.get('id', 'unknown')}: {e}")
                                records_failed += 1
                    
                    # Sync alerts if enabled
                    if integration.sync_alerts:
                        alerts_data = await edr_service.get_alerts()
                        records_processed += len(alerts_data)
                        
                        for alert_data in alerts_data:
                            try:
                                normalized_data = edr_service.normalize_alert_data(alert_data)
                                
                                # Check if alert already exists
                                existing_alert = db.query(EDRAlert).filter(
                                    EDRAlert.integration_id == integration_id,
                                    EDRAlert.edr_alert_id == normalized_data['edr_alert_id']
                                ).first()
                                
                                if not existing_alert:
                                    # Create new alert
                                    alert = EDRAlert(
                                        integration_id=integration_id,
                                        **normalized_data
                                    )
                                    db.add(alert)
                                    records_created += 1
                                
                            except Exception as e:
                                self.logger.error(f"Failed to process alert {alert_data.get('id', 'unknown')}: {e}")
                                records_failed += 1
                
                # Update integration sync time
                integration.last_sync = start_time
                integration.next_sync = start_time + timedelta(minutes=integration.sync_interval_minutes)
                
                # Update sync log
                sync_log.status = "success"
                sync_log.completed_at = datetime.utcnow()
                sync_log.duration_seconds = int((datetime.utcnow() - start_time).total_seconds())
                sync_log.records_processed = records_processed
                sync_log.records_created = records_created
                sync_log.records_updated = records_updated
                sync_log.records_failed = records_failed
                
                db.commit()
                
                return {
                    "status": "success",
                    "records_processed": records_processed,
                    "records_created": records_created,
                    "records_updated": records_updated,
                    "records_failed": records_failed,
                    "duration_seconds": sync_log.duration_seconds
                }
                
            except Exception as e:
                # Update sync log with error
                sync_log.status = "failed"
                sync_log.completed_at = datetime.utcnow()
                sync_log.duration_seconds = int((datetime.utcnow() - start_time).total_seconds())
                sync_log.error_message = str(e)
                
                db.commit()
                raise
                
        except Exception as e:
            db.rollback()
            self.logger.error(f"EDR sync failed: {e}")
            raise
        finally:
            db.close()
    
    async def test_integration(self, integration_id: str) -> Dict[str, Any]:
        """Test EDR integration connectivity"""
        db = SessionLocal()
        try:
            integration = db.query(EDRIntegration).filter(EDRIntegration.id == integration_id).first()
            if not integration:
                raise ValueError("EDR integration not found")
            
            edr_service = self.get_edr_service(integration)
            
            async with edr_service:
                # Test authentication
                auth_success = await edr_service.authenticate()
                
                if auth_success:
                    # Test endpoint retrieval
                    endpoints = await edr_service.get_endpoints(limit=1)
                    
                    return {
                        "status": "success",
                        "authentication": "success",
                        "endpoints_accessible": len(endpoints) > 0,
                        "endpoint_count": len(endpoints)
                    }
                else:
                    return {
                        "status": "failed",
                        "authentication": "failed",
                        "error": "Authentication failed"
                    }
                    
        except Exception as e:
            self.logger.error(f"EDR test failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
        finally:
            db.close()
