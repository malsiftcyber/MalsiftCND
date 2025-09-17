"""
Export service for generating CSV and other format reports
"""
import csv
import io
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.core.database import SessionLocal
from app.models.device import Device
from app.models.scan import Scan, ScanResult
from app.models.device_correction import DeviceCorrection


class ExportService:
    """Service for exporting data in various formats"""
    
    def __init__(self):
        self.logger = logging.getLogger("services.export_service")
    
    async def export_devices_csv(self, device_ids: Optional[List[str]] = None,
                               include_corrections: bool = True,
                               include_services: bool = True,
                               include_ai_analysis: bool = True) -> str:
        """Export devices to CSV format"""
        db = SessionLocal()
        try:
            # Build query
            query = db.query(Device).filter(Device.is_active == True)
            
            if device_ids:
                query = query.filter(Device.id.in_(device_ids))
            
            devices = query.all()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            headers = [
                'IP Address', 'Hostname', 'Device Type', 'Operating System',
                'Confidence', 'Risk Score', 'First Seen', 'Last Seen',
                'Company Name', 'Company Code', 'Site Name', 'Site Code',
                'Tags', 'Notes', 'Is Active'
            ]
            
            if include_services:
                headers.extend(['Open Ports', 'Services', 'Service Versions'])
            
            if include_corrections:
                headers.extend(['Correction Count', 'Last Correction', 'Correction History'])
            
            if include_ai_analysis:
                headers.extend(['AI Device Type', 'AI OS', 'AI Confidence', 'AI Reasoning'])
            
            writer.writerow(headers)
            
            # Write device data
            for device in devices:
                row = [
                    device.ip,
                    device.hostname or '',
                    device.device_type,
                    device.operating_system,
                    f"{device.confidence:.2%}",
                    device.risk_score,
                    device.first_seen.isoformat() if device.first_seen else '',
                    device.last_seen.isoformat() if device.last_seen else '',
                    device.company.name if device.company else '',
                    device.company.code if device.company else '',
                    device.site.name if device.site else '',
                    device.site.code if device.site else '',
                    '; '.join(device.tags) if device.tags else '',
                    device.notes or '',
                    'Yes' if device.is_active else 'No'
                ]
                
                if include_services:
                    services_data = self._extract_services_data(device)
                    row.extend([
                        services_data['ports'],
                        services_data['services'],
                        services_data['versions']
                    ])
                
                if include_corrections:
                    corrections_data = self._extract_corrections_data(device)
                    row.extend([
                        corrections_data['count'],
                        corrections_data['last_correction'],
                        corrections_data['history']
                    ])
                
                if include_ai_analysis:
                    ai_data = self._extract_ai_data(device)
                    row.extend([
                        ai_data['device_type'],
                        ai_data['os'],
                        ai_data['confidence'],
                        ai_data['reasoning']
                    ])
                
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"Failed to export devices CSV: {e}")
            raise
        finally:
            db.close()
    
    async def export_scan_results_csv(self, scan_id: str) -> str:
        """Export scan results to CSV format"""
        db = SessionLocal()
        try:
            # Get scan and results
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                raise ValueError("Scan not found")
            
            results = db.query(ScanResult).filter(ScanResult.scan_id == scan_id).all()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            headers = [
                'Scan ID', 'Scan Type', 'Scanner', 'Target IP', 'Target Hostname',
                'Success', 'Scan Time (seconds)', 'Completed At', 'Error Message',
                'Open Ports', 'Services', 'OS Detection', 'Service Versions'
            ]
            
            writer.writerow(headers)
            
            # Write scan info
            for result in results:
                scan_data = result.scan_data or {}
                hosts = scan_data.get('hosts', {})
                
                for host_ip, host_info in hosts.items():
                    # Extract services
                    services = host_info.get('services', [])
                    ports = [str(s.get('port', '')) for s in services]
                    service_names = [s.get('service', '') for s in services]
                    versions = [s.get('version', '') for s in services]
                    
                    # Extract OS info
                    os_info = host_info.get('os', {})
                    os_name = os_info.get('name', '') if os_info else ''
                    
                    row = [
                        str(scan.id),
                        scan.scan_type,
                        scan.scanner,
                        result.target_ip,
                        result.target_hostname or '',
                        'Yes' if result.success else 'No',
                        result.scan_time or 0,
                        result.created_at.isoformat() if result.created_at else '',
                        result.error_message or '',
                        '; '.join(ports),
                        '; '.join(service_names),
                        os_name,
                        '; '.join(versions)
                    ]
                    
                    writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"Failed to export scan results CSV: {e}")
            raise
        finally:
            db.close()
    
    async def export_corrections_csv(self, device_id: Optional[str] = None) -> str:
        """Export device corrections to CSV format"""
        db = SessionLocal()
        try:
            # Build query
            query = db.query(DeviceCorrection)
            
            if device_id:
                query = query.filter(DeviceCorrection.device_id == device_id)
            
            corrections = query.order_by(DeviceCorrection.created_at.desc()).all()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            headers = [
                'Correction ID', 'Device IP', 'Device Hostname', 'Original Device Type',
                'Original OS', 'Original Confidence', 'Corrected Device Type',
                'Corrected OS', 'Correction Reason', 'Applied At', 'Applied By',
                'Is Verified', 'Verified By', 'Verified At', 'Feedback Score',
                'Learning Weight', 'Additional Tags'
            ]
            
            writer.writerow(headers)
            
            # Write correction data
            for correction in corrections:
                row = [
                    str(correction.id),
                    correction.device.ip,
                    correction.device.hostname or '',
                    correction.original_device_type,
                    correction.original_operating_system,
                    f"{correction.original_confidence:.2%}",
                    correction.corrected_device_type,
                    correction.corrected_operating_system,
                    correction.correction_reason,
                    correction.created_at.isoformat(),
                    correction.user.username if correction.user else '',
                    'Yes' if correction.is_verified else 'No',
                    correction.verifier.username if correction.verifier else '',
                    correction.verified_at.isoformat() if correction.verified_at else '',
                    correction.feedback_score or '',
                    correction.learning_weight,
                    '; '.join(correction.correction_tags) if correction.correction_tags else ''
                ]
                
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"Failed to export corrections CSV: {e}")
            raise
        finally:
            db.close()
    
    async def export_new_devices_csv(self, hours: int = 24) -> str:
        """Export newly discovered devices from the last N hours"""
        db = SessionLocal()
        try:
            from datetime import timedelta
            
            # Calculate cutoff time
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Query for devices discovered in the last N hours
            devices = db.query(Device).filter(
                Device.is_active == True,
                Device.first_seen >= cutoff_time
            ).all()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            headers = [
                'IP Address', 'Hostname', 'Device Type', 'Operating System',
                'Confidence', 'Risk Score', 'First Seen', 'Discovery Time (Hours Ago)',
                'Company Name', 'Company Code', 'Site Name', 'Site Code',
                'Tags', 'Open Ports', 'Services', 'Service Count', 'High Risk Services',
                'AI Analysis', 'Notes', 'Discovery Method'
            ]
            
            writer.writerow(headers)
            
            # Write device data
            for device in devices:
                services_data = self._extract_services_data(device)
                
                # Calculate hours since discovery
                hours_ago = (datetime.now() - device.first_seen).total_seconds() / 3600
                
                # Identify high-risk services
                high_risk_services = self._identify_high_risk_services(services_data['services'])
                
                # Determine discovery method
                discovery_method = self._determine_discovery_method(device)
                
                row = [
                    device.ip,
                    device.hostname or '',
                    device.device_type,
                    device.operating_system,
                    f"{device.confidence:.2%}",
                    device.risk_score,
                    device.first_seen.isoformat(),
                    f"{hours_ago:.1f}",
                    device.company.name if device.company else '',
                    device.company.code if device.company else '',
                    device.site.name if device.site else '',
                    device.site.code if device.site else '',
                    '; '.join(device.tags) if device.tags else '',
                    services_data['ports'],
                    services_data['services'],
                    len(services_data['services'].split('; ')) if services_data['services'] else 0,
                    '; '.join(high_risk_services),
                    device.ai_analysis.get('reasoning', '') if device.ai_analysis else '',
                    device.notes or '',
                    discovery_method
                ]
                
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"Failed to export new devices CSV: {e}")
            raise
        finally:
            db.close()

    async def export_discovery_report_csv(self, start_date: Optional[datetime] = None,
                                        end_date: Optional[datetime] = None,
                                        device_types: Optional[List[str]] = None,
                                        risk_score_min: Optional[float] = None,
                                        risk_score_max: Optional[float] = None) -> str:
        """Export comprehensive discovery report to CSV"""
        db = SessionLocal()
        try:
            # Build query
            query = db.query(Device).filter(Device.is_active == True)
            
            if start_date:
                query = query.filter(Device.first_seen >= start_date)
            
            if end_date:
                query = query.filter(Device.first_seen <= end_date)
            
            if device_types:
                query = query.filter(Device.device_type.in_(device_types))
            
            if risk_score_min is not None:
                query = query.filter(Device.risk_score >= risk_score_min)
            
            if risk_score_max is not None:
                query = query.filter(Device.risk_score <= risk_score_max)
            
            devices = query.all()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            headers = [
                'IP Address', 'Hostname', 'Device Type', 'Operating System',
                'Confidence', 'Risk Score', 'First Seen', 'Last Seen',
                'Days Since Discovery', 'Company Name', 'Company Code',
                'Site Name', 'Site Code', 'Tags', 'Open Ports', 'Services',
                'Service Count', 'High Risk Services', 'Correction Count',
                'AI Analysis', 'Notes'
            ]
            
            writer.writerow(headers)
            
            # Write device data
            for device in devices:
                services_data = self._extract_services_data(device)
                corrections_data = self._extract_corrections_data(device)
                
                # Calculate days since discovery
                days_since_discovery = ''
                if device.first_seen:
                    days_since_discovery = (datetime.now() - device.first_seen).days
                
                # Identify high-risk services
                high_risk_services = self._identify_high_risk_services(services_data['services'])
                
                row = [
                    device.ip,
                    device.hostname or '',
                    device.device_type,
                    device.operating_system,
                    f"{device.confidence:.2%}",
                    device.risk_score,
                    device.first_seen.isoformat() if device.first_seen else '',
                    device.last_seen.isoformat() if device.last_seen else '',
                    days_since_discovery,
                    device.company.name if device.company else '',
                    device.company.code if device.company else '',
                    device.site.name if device.site else '',
                    device.site.code if device.site else '',
                    '; '.join(device.tags) if device.tags else '',
                    services_data['ports'],
                    services_data['services'],
                    len(services_data['services'].split('; ')) if services_data['services'] else 0,
                    '; '.join(high_risk_services),
                    corrections_data['count'],
                    device.ai_analysis.get('reasoning', '') if device.ai_analysis else '',
                    device.notes or ''
                ]
                
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"Failed to export discovery report CSV: {e}")
            raise
        finally:
            db.close()
    
    def _extract_services_data(self, device: Device) -> Dict[str, str]:
        """Extract services data from device"""
        ports = []
        services = []
        versions = []
        
        for scanner, host_info in device.scan_results.items():
            host_services = host_info.get("services", [])
            for service in host_services:
                if service.get("port"):
                    ports.append(str(service["port"]))
                if service.get("service"):
                    services.append(service["service"])
                if service.get("version"):
                    versions.append(service["version"])
        
        return {
            'ports': '; '.join(ports),
            'services': '; '.join(services),
            'versions': '; '.join(versions)
        }
    
    def _extract_corrections_data(self, device: Device) -> Dict[str, Any]:
        """Extract corrections data from device"""
        corrections = device.corrections
        count = len(corrections)
        
        last_correction = ''
        if corrections:
            last_correction = max(corrections, key=lambda c: c.created_at).created_at.isoformat()
        
        history = []
        for correction in corrections:
            history.append(f"{correction.original_device_type}→{correction.corrected_device_type}")
        
        return {
            'count': count,
            'last_correction': last_correction,
            'history': '; '.join(history)
        }
    
    def _extract_ai_data(self, device: Device) -> Dict[str, str]:
        """Extract AI analysis data from device"""
        ai_analysis = device.ai_analysis or {}
        
        return {
            'device_type': ai_analysis.get('device_type', ''),
            'os': ai_analysis.get('operating_system', ''),
            'confidence': f"{ai_analysis.get('confidence', 0):.2%}",
            'reasoning': ai_analysis.get('reasoning', '')
        }
    
    def _identify_high_risk_services(self, services_str: str) -> List[str]:
        """Identify high-risk services from services string"""
        high_risk_services = [
            'ssh', 'telnet', 'ftp', 'tftp', 'snmp', 'ldap', 'rdp',
            'smb', 'netbios-ssn', 'microsoft-ds', 'http', 'https',
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch'
        ]
        
        services = [s.strip().lower() for s in services_str.split(';') if s.strip()]
        return [s for s in services if s in high_risk_services]
    
    def _determine_discovery_method(self, device: Device) -> str:
        """Determine how the device was discovered"""
        if not device.scan_results:
            return "Unknown"
        
        # Check which scanners found this device
        scanners = list(device.scan_results.keys())
        
        if len(scanners) == 1:
            return scanners[0].title()
        elif len(scanners) > 1:
            return f"Multiple ({', '.join(scanners).title()})"
        else:
            return "Unknown"
