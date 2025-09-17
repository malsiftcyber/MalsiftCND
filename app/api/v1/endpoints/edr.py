"""
EDR integration API endpoints
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

from app.auth.auth_service import AuthService
from app.services.edr_service import EDRIntegrationService
from app.models.edr_integration import EDRProvider

router = APIRouter()
auth_service = AuthService()
edr_service = EDRIntegrationService()


# Request/Response Models
class EDRIntegrationCreateRequest(BaseModel):
    name: str
    provider: EDRProvider
    api_base_url: str
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    tenant_id: Optional[str] = None
    auth_type: str = "api_key"
    sync_enabled: bool = True
    sync_interval_minutes: int = 60
    sync_endpoints: bool = True
    sync_alerts: bool = False
    sync_vulnerabilities: bool = False
    sync_network_connections: bool = False
    include_tags: Optional[List[str]] = None
    exclude_tags: Optional[List[str]] = None
    include_hostnames: Optional[List[str]] = None
    exclude_hostnames: Optional[List[str]] = None
    company_id: Optional[str] = None
    site_id: Optional[str] = None
    description: Optional[str] = None


class EDRIntegrationUpdateRequest(BaseModel):
    name: Optional[str] = None
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    tenant_id: Optional[str] = None
    auth_type: Optional[str] = None
    is_active: Optional[bool] = None
    sync_enabled: Optional[bool] = None
    sync_interval_minutes: Optional[int] = None
    sync_endpoints: Optional[bool] = None
    sync_alerts: Optional[bool] = None
    sync_vulnerabilities: Optional[bool] = None
    sync_network_connections: Optional[bool] = None
    include_tags: Optional[List[str]] = None
    exclude_tags: Optional[List[str]] = None
    include_hostnames: Optional[List[str]] = None
    exclude_hostnames: Optional[List[str]] = None
    company_id: Optional[str] = None
    site_id: Optional[str] = None
    description: Optional[str] = None


@router.post("/integrations", response_model=Dict[str, str])
async def create_edr_integration(
    request: EDRIntegrationCreateRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Create a new EDR integration"""
    try:
        from app.core.database import SessionLocal
        from app.models.edr_integration import EDRIntegration
        import uuid
        
        db = SessionLocal()
        try:
            integration = EDRIntegration(
                id=uuid.uuid4(),
                name=request.name,
                provider=request.provider,
                api_base_url=request.api_base_url,
                api_key=request.api_key,
                client_id=request.client_id,
                client_secret=request.client_secret,
                tenant_id=request.tenant_id,
                auth_type=request.auth_type,
                sync_enabled=request.sync_enabled,
                sync_interval_minutes=request.sync_interval_minutes,
                sync_endpoints=request.sync_endpoints,
                sync_alerts=request.sync_alerts,
                sync_vulnerabilities=request.sync_vulnerabilities,
                sync_network_connections=request.sync_network_connections,
                include_tags=request.include_tags,
                exclude_tags=request.exclude_tags,
                include_hostnames=request.include_hostnames,
                exclude_hostnames=request.exclude_hostnames,
                company_id=request.company_id,
                site_id=request.site_id,
                description=request.description,
                created_by=auth_service.get_current_user_id(token)  # You'll need to implement this
            )
            
            db.add(integration)
            db.commit()
            db.refresh(integration)
            
            return {
                "integration_id": str(integration.id),
                "message": f"EDR integration '{request.name}' created successfully"
            }
            
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create EDR integration: {str(e)}"
        )


@router.get("/integrations", response_model=List[Dict[str, Any]])
async def list_edr_integrations(
    active_only: bool = True,
    token: str = Depends(auth_service.verify_token)
):
    """List all EDR integrations"""
    try:
        from app.core.database import SessionLocal
        from app.models.edr_integration import EDRIntegration
        
        db = SessionLocal()
        try:
            query = db.query(EDRIntegration)
            if active_only:
                query = query.filter(EDRIntegration.is_active == True)
            
            integrations = query.all()
            
            return [
                {
                    "id": str(integration.id),
                    "name": integration.name,
                    "provider": integration.provider,
                    "api_base_url": integration.api_base_url,
                    "auth_type": integration.auth_type,
                    "is_active": integration.is_active,
                    "sync_enabled": integration.sync_enabled,
                    "sync_interval_minutes": integration.sync_interval_minutes,
                    "sync_endpoints": integration.sync_endpoints,
                    "sync_alerts": integration.sync_alerts,
                    "last_sync": integration.last_sync.isoformat() if integration.last_sync else None,
                    "next_sync": integration.next_sync.isoformat() if integration.next_sync else None,
                    "company_id": str(integration.company_id) if integration.company_id else None,
                    "site_id": str(integration.site_id) if integration.site_id else None,
                    "description": integration.description,
                    "created_at": integration.created_at.isoformat(),
                    "updated_at": integration.updated_at.isoformat() if integration.updated_at else None
                }
                for integration in integrations
            ]
            
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list EDR integrations: {str(e)}"
        )


@router.get("/integrations/{integration_id}", response_model=Dict[str, Any])
async def get_edr_integration(
    integration_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Get EDR integration by ID"""
    try:
        from app.core.database import SessionLocal
        from app.models.edr_integration import EDRIntegration
        
        db = SessionLocal()
        try:
            integration = db.query(EDRIntegration).filter(EDRIntegration.id == integration_id).first()
            if not integration:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="EDR integration not found"
                )
            
            return {
                "id": str(integration.id),
                "name": integration.name,
                "provider": integration.provider,
                "api_base_url": integration.api_base_url,
                "auth_type": integration.auth_type,
                "is_active": integration.is_active,
                "sync_enabled": integration.sync_enabled,
                "sync_interval_minutes": integration.sync_interval_minutes,
                "sync_endpoints": integration.sync_endpoints,
                "sync_alerts": integration.sync_alerts,
                "sync_vulnerabilities": integration.sync_vulnerabilities,
                "sync_network_connections": integration.sync_network_connections,
                "include_tags": integration.include_tags,
                "exclude_tags": integration.exclude_tags,
                "include_hostnames": integration.include_hostnames,
                "exclude_hostnames": integration.exclude_hostnames,
                "company_id": str(integration.company_id) if integration.company_id else None,
                "site_id": str(integration.site_id) if integration.site_id else None,
                "description": integration.description,
                "last_sync": integration.last_sync.isoformat() if integration.last_sync else None,
                "next_sync": integration.next_sync.isoformat() if integration.next_sync else None,
                "created_at": integration.created_at.isoformat(),
                "updated_at": integration.updated_at.isoformat() if integration.updated_at else None
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get EDR integration: {str(e)}"
        )


@router.put("/integrations/{integration_id}")
async def update_edr_integration(
    integration_id: str,
    request: EDRIntegrationUpdateRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Update EDR integration"""
    try:
        from app.core.database import SessionLocal
        from app.models.edr_integration import EDRIntegration
        
        db = SessionLocal()
        try:
            integration = db.query(EDRIntegration).filter(EDRIntegration.id == integration_id).first()
            if not integration:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="EDR integration not found"
                )
            
            # Update fields
            update_data = {k: v for k, v in request.dict().items() if v is not None}
            for key, value in update_data.items():
                if hasattr(integration, key):
                    setattr(integration, key, value)
            
            integration.updated_at = datetime.utcnow()
            db.commit()
            
            return {"message": f"EDR integration '{integration_id}' updated successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update EDR integration: {str(e)}"
        )


@router.delete("/integrations/{integration_id}")
async def delete_edr_integration(
    integration_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Delete EDR integration (soft delete)"""
    try:
        from app.core.database import SessionLocal
        from app.models.edr_integration import EDRIntegration
        
        db = SessionLocal()
        try:
            integration = db.query(EDRIntegration).filter(EDRIntegration.id == integration_id).first()
            if not integration:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="EDR integration not found"
                )
            
            integration.is_active = False
            integration.updated_at = datetime.utcnow()
            db.commit()
            
            return {"message": f"EDR integration '{integration_id}' deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete EDR integration: {str(e)}"
        )


@router.post("/integrations/{integration_id}/test")
async def test_edr_integration(
    integration_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Test EDR integration connectivity"""
    try:
        result = await edr_service.test_integration(integration_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test EDR integration: {str(e)}"
        )


@router.post("/integrations/{integration_id}/sync")
async def sync_edr_integration(
    integration_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Manually sync EDR integration"""
    try:
        result = await edr_service.sync_integration(integration_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync EDR integration: {str(e)}"
        )


@router.get("/integrations/{integration_id}/endpoints", response_model=List[Dict[str, Any]])
async def get_edr_endpoints(
    integration_id: str,
    limit: int = 100,
    offset: int = 0,
    token: str = Depends(auth_service.verify_token)
):
    """Get endpoints from EDR integration"""
    try:
        from app.core.database import SessionLocal
        from app.models.edr_integration import EDREndpoint
        
        db = SessionLocal()
        try:
            endpoints = db.query(EDREndpoint).filter(
                EDREndpoint.integration_id == integration_id
            ).offset(offset).limit(limit).all()
            
            return [
                {
                    "id": str(endpoint.id),
                    "edr_endpoint_id": endpoint.edr_endpoint_id,
                    "edr_hostname": endpoint.edr_hostname,
                    "edr_ip_addresses": endpoint.edr_ip_addresses,
                    "hostname": endpoint.hostname,
                    "operating_system": endpoint.operating_system,
                    "os_version": endpoint.os_version,
                    "architecture": endpoint.architecture,
                    "processor": endpoint.processor,
                    "memory_gb": endpoint.memory_gb,
                    "mac_addresses": endpoint.mac_addresses,
                    "agent_version": endpoint.agent_version,
                    "agent_status": endpoint.agent_status,
                    "last_seen_by_agent": endpoint.last_seen_by_agent.isoformat() if endpoint.last_seen_by_agent else None,
                    "risk_score": endpoint.risk_score,
                    "threat_level": endpoint.threat_level,
                    "compliance_status": endpoint.compliance_status,
                    "edr_tags": endpoint.edr_tags,
                    "edr_groups": endpoint.edr_groups,
                    "device_id": str(endpoint.device_id) if endpoint.device_id else None,
                    "company_id": str(endpoint.company_id) if endpoint.company_id else None,
                    "site_id": str(endpoint.site_id) if endpoint.site_id else None,
                    "first_seen": endpoint.first_seen.isoformat(),
                    "last_seen": endpoint.last_seen.isoformat(),
                    "last_updated": endpoint.last_updated.isoformat() if endpoint.last_updated else None
                }
                for endpoint in endpoints
            ]
            
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get EDR endpoints: {str(e)}"
        )


@router.get("/integrations/{integration_id}/alerts", response_model=List[Dict[str, Any]])
async def get_edr_alerts(
    integration_id: str,
    limit: int = 100,
    offset: int = 0,
    token: str = Depends(auth_service.verify_token)
):
    """Get alerts from EDR integration"""
    try:
        from app.core.database import SessionLocal
        from app.models.edr_integration import EDRAlert
        
        db = SessionLocal()
        try:
            alerts = db.query(EDRAlert).filter(
                EDRAlert.integration_id == integration_id
            ).offset(offset).limit(limit).all()
            
            return [
                {
                    "id": str(alert.id),
                    "edr_alert_id": alert.edr_alert_id,
                    "edr_incident_id": alert.edr_incident_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "status": alert.status,
                    "title": alert.title,
                    "description": alert.description,
                    "threat_name": alert.threat_name,
                    "threat_type": alert.threat_type,
                    "threat_category": alert.threat_category,
                    "ioc_count": alert.ioc_count,
                    "detected_at": alert.detected_at.isoformat() if alert.detected_at else None,
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                    "endpoint_id": str(alert.endpoint_id) if alert.endpoint_id else None,
                    "created_at": alert.created_at.isoformat(),
                    "updated_at": alert.updated_at.isoformat() if alert.updated_at else None
                }
                for alert in alerts
            ]
            
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get EDR alerts: {str(e)}"
        )


@router.get("/integrations/{integration_id}/sync-logs", response_model=List[Dict[str, Any]])
async def get_edr_sync_logs(
    integration_id: str,
    limit: int = 50,
    offset: int = 0,
    token: str = Depends(auth_service.verify_token)
):
    """Get sync logs for EDR integration"""
    try:
        from app.core.database import SessionLocal
        from app.models.edr_integration import EDRSyncLog
        
        db = SessionLocal()
        try:
            logs = db.query(EDRSyncLog).filter(
                EDRSyncLog.integration_id == integration_id
            ).order_by(EDRSyncLog.started_at.desc()).offset(offset).limit(limit).all()
            
            return [
                {
                    "id": str(log.id),
                    "sync_type": log.sync_type,
                    "status": log.status,
                    "started_at": log.started_at.isoformat(),
                    "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                    "duration_seconds": log.duration_seconds,
                    "records_processed": log.records_processed,
                    "records_created": log.records_created,
                    "records_updated": log.records_updated,
                    "records_failed": log.records_failed,
                    "error_message": log.error_message,
                    "error_details": log.error_details
                }
                for log in logs
            ]
            
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get EDR sync logs: {str(e)}"
        )


@router.get("/providers")
async def get_edr_providers(
    token: str = Depends(auth_service.verify_token)
):
    """Get available EDR providers and their configuration requirements"""
    return {
        "providers": [
            {
                "name": "CrowdStrike Falcon",
                "value": "crowdstrike",
                "description": "CrowdStrike Falcon EDR platform",
                "auth_types": ["oauth"],
                "required_fields": ["api_base_url", "client_id", "client_secret"],
                "optional_fields": ["tenant_id"],
                "api_documentation": "https://falcon.crowdstrike.com/documentation"
            },
            {
                "name": "Microsoft Defender for Endpoint",
                "value": "microsoft_defender",
                "description": "Microsoft Defender for Endpoint EDR platform",
                "auth_types": ["oauth"],
                "required_fields": ["tenant_id", "client_id", "client_secret"],
                "optional_fields": [],
                "api_documentation": "https://docs.microsoft.com/en-us/microsoft-365/security/defender-endpoint/"
            },
            {
                "name": "SentinelOne",
                "value": "sentinelone",
                "description": "SentinelOne EDR platform",
                "auth_types": ["api_key"],
                "required_fields": ["api_base_url", "client_id", "client_secret"],
                "optional_fields": [],
                "api_documentation": "https://usea1-partners.sentinelone.net/api-doc/"
            },
            {
                "name": "TrendMicro Vision One",
                "value": "trendmicro",
                "description": "TrendMicro Vision One EDR platform",
                "auth_types": ["api_key"],
                "required_fields": ["api_base_url", "api_key"],
                "optional_fields": [],
                "api_documentation": "https://automation.trendmicro.com/vision-one/api"
            }
        ]
    }
