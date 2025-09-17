"""
Device service for managing discovered devices
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from app.services.data_aggregator import AggregatedDevice


class DeviceService:
    """Service for managing devices"""
    
    def __init__(self):
        self.logger = logging.getLogger("services.device_service")
        self.devices: Dict[str, AggregatedDevice] = {}
    
    async def list_devices(self, limit: int = 50, offset: int = 0,
                         search: Optional[str] = None,
                         device_type: Optional[str] = None,
                         operating_system: Optional[str] = None) -> List[Dict[str, Any]]:
        """List devices with optional filtering"""
        devices = list(self.devices.values())
        
        # Apply filters
        if search:
            devices = [
                d for d in devices
                if search.lower() in d.ip.lower() or
                   (d.hostname and search.lower() in d.hostname.lower()) or
                   search.lower() in d.device_type.lower() or
                   search.lower() in d.operating_system.lower()
            ]
        
        if device_type:
            devices = [d for d in devices if d.device_type.lower() == device_type.lower()]
        
        if operating_system:
            devices = [d for d in devices if d.operating_system.lower() == operating_system.lower()]
        
        # Sort by last seen (newest first)
        devices.sort(key=lambda x: x.last_seen or datetime.min, reverse=True)
        
        # Apply pagination
        paginated_devices = devices[offset:offset + limit]
        
        return [self._device_to_dict(device) for device in paginated_devices]
    
    async def get_device(self, device_ip: str) -> Optional[Dict[str, Any]]:
        """Get device by IP"""
        device = self.devices.get(device_ip)
        if device:
            return self._device_to_dict(device)
        return None
    
    async def search_devices(self, query: Optional[str] = None,
                           device_type: Optional[str] = None,
                           operating_system: Optional[str] = None,
                           ip_range: Optional[str] = None,
                           tags: Optional[List[str]] = None,
                           risk_score_min: Optional[float] = None,
                           risk_score_max: Optional[float] = None,
                           limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Advanced device search"""
        devices = list(self.devices.values())
        
        # Apply all filters
        if query:
            devices = [
                d for d in devices
                if query.lower() in d.ip.lower() or
                   (d.hostname and query.lower() in d.hostname.lower()) or
                   query.lower() in d.device_type.lower() or
                   query.lower() in d.operating_system.lower() or
                   any(query.lower() in tag.lower() for tag in d.tags)
            ]
        
        if device_type:
            devices = [d for d in devices if d.device_type.lower() == device_type.lower()]
        
        if operating_system:
            devices = [d for d in devices if d.operating_system.lower() == operating_system.lower()]
        
        if ip_range:
            # Simple IP range filtering (would need proper CIDR parsing in production)
            devices = [d for d in devices if d.ip.startswith(ip_range.split('/')[0].rsplit('.', 1)[0])]
        
        if tags:
            devices = [
                d for d in devices
                if any(tag.lower() in [t.lower() for t in d.tags] for tag in tags)
            ]
        
        if risk_score_min is not None:
            devices = [d for d in devices if d.risk_score >= risk_score_min]
        
        if risk_score_max is not None:
            devices = [d for d in devices if d.risk_score <= risk_score_max]
        
        # Sort by risk score (highest first)
        devices.sort(key=lambda x: x.risk_score, reverse=True)
        
        # Apply pagination
        paginated_devices = devices[offset:offset + limit]
        
        return [self._device_to_dict(device) for device in paginated_devices]
    
    async def get_device_history(self, device_ip: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get device discovery history"""
        device = self.devices.get(device_ip)
        if not device:
            return []
        
        # In a real implementation, this would query historical data
        # For now, return basic history
        history = []
        
        if device.first_seen:
            history.append({
                "event": "first_discovered",
                "timestamp": device.first_seen,
                "source": "network_scan",
                "details": "Device first discovered during network scan"
            })
        
        if device.last_seen and device.last_seen != device.first_seen:
            history.append({
                "event": "last_seen",
                "timestamp": device.last_seen,
                "source": "network_scan",
                "details": "Device last seen during network scan"
            })
        
        # Add AI analysis events
        if device.ai_analysis:
            history.append({
                "event": "ai_analysis",
                "timestamp": device.last_seen or datetime.now(),
                "source": "ai_analysis",
                "details": f"AI analysis completed with {device.confidence:.2%} confidence"
            })
        
        return history[offset:offset + limit]
    
    async def update_device_tags(self, device_ip: str, tags: List[str]) -> bool:
        """Update device tags"""
        device = self.devices.get(device_ip)
        if not device:
            return False
        
        device.tags = tags
        return True
    
    async def update_device_notes(self, device_ip: str, notes: str) -> bool:
        """Update device notes"""
        device = self.devices.get(device_ip)
        if not device:
            return False
        
        device.notes = notes
        return True
    
    async def get_device_stats(self) -> Dict[str, Any]:
        """Get device statistics"""
        devices = list(self.devices.values())
        
        if not devices:
            return {
                "total_devices": 0,
                "device_types": {},
                "operating_systems": {},
                "risk_distribution": {},
                "recent_discoveries": 0
            }
        
        # Count device types
        device_types = {}
        for device in devices:
            device_types[device.device_type] = device_types.get(device.device_type, 0) + 1
        
        # Count operating systems
        operating_systems = {}
        for device in devices:
            operating_systems[device.operating_system] = operating_systems.get(device.operating_system, 0) + 1
        
        # Risk score distribution
        risk_ranges = {
            "low (0-3)": 0,
            "medium (3-7)": 0,
            "high (7-10)": 0
        }
        
        for device in devices:
            if device.risk_score < 3:
                risk_ranges["low (0-3)"] += 1
            elif device.risk_score < 7:
                risk_ranges["medium (3-7)"] += 1
            else:
                risk_ranges["high (7-10)"] += 1
        
        # Recent discoveries (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_discoveries = len([
            d for d in devices
            if d.first_seen and d.first_seen > recent_cutoff
        ])
        
        return {
            "total_devices": len(devices),
            "device_types": device_types,
            "operating_systems": operating_systems,
            "risk_distribution": risk_ranges,
            "recent_discoveries": recent_discoveries,
            "average_confidence": sum(d.confidence for d in devices) / len(devices) if devices else 0
        }
    
    def _device_to_dict(self, device: AggregatedDevice) -> Dict[str, Any]:
        """Convert device to dictionary"""
        return {
            "ip": device.ip,
            "hostname": device.hostname,
            "device_type": device.device_type,
            "operating_system": device.operating_system,
            "confidence": device.confidence,
            "last_seen": device.last_seen,
            "first_seen": device.first_seen,
            "tags": device.tags,
            "risk_score": device.risk_score,
            "services": self._extract_services(device),
            "ai_analysis": device.ai_analysis.__dict__ if device.ai_analysis else None
        }
    
    def _extract_services(self, device: AggregatedDevice) -> List[Dict[str, Any]]:
        """Extract services from scan results"""
        services = []
        
        for scanner, host_info in device.scan_results.items():
            host_services = host_info.get("services", [])
            services.extend(host_services)
        
        # Remove duplicates
        unique_services = []
        seen_services = set()
        
        for service in services:
            service_key = (service.get("port"), service.get("service"))
            if service_key not in seen_services:
                unique_services.append(service)
                seen_services.add(service_key)
        
        return unique_services
