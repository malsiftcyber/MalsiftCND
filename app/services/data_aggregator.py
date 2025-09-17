"""
Data aggregation service for combining scan results and external data
"""
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

from app.ai.llm_analyzer import LLMAnalyzer, DeviceAnalysis


@dataclass
class AggregatedDevice:
    """Aggregated device information"""
    ip: str
    hostname: Optional[str] = None
    device_type: str = "Unknown"
    operating_system: str = "Unknown"
    confidence: float = 0.0
    
    # Scan data
    scan_results: Dict[str, Any] = field(default_factory=dict)
    last_seen: Optional[datetime] = None
    first_seen: Optional[datetime] = None
    
    # External data
    runzero_data: Optional[Dict[str, Any]] = None
    tanium_data: Optional[Dict[str, Any]] = None
    armis_data: Optional[Dict[str, Any]] = None
    ad_data: Optional[Dict[str, Any]] = None
    
    # AI analysis
    ai_analysis: Optional[DeviceAnalysis] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    risk_score: float = 0.0


class DataAggregator:
    """Service for aggregating data from multiple sources"""
    
    def __init__(self):
        self.logger = logging.getLogger("services.data_aggregator")
        self.llm_analyzer = LLMAnalyzer()
        self.devices: Dict[str, AggregatedDevice] = {}
    
    async def aggregate_scan_data(self, scan_results: List[Dict[str, Any]]) -> List[AggregatedDevice]:
        """Aggregate multiple scan results"""
        aggregated_devices = []
        
        for scan_result in scan_results:
            devices = await self._process_scan_result(scan_result)
            aggregated_devices.extend(devices)
        
        # Merge devices with same IP
        merged_devices = self._merge_devices_by_ip(aggregated_devices)
        
        # Perform AI analysis on merged devices
        for device in merged_devices:
            await self._analyze_device_with_ai(device)
        
        return merged_devices
    
    async def _process_scan_result(self, scan_result: Dict[str, Any]) -> List[AggregatedDevice]:
        """Process individual scan result"""
        devices = []
        hosts = scan_result.get("hosts", {})
        
        for host_ip, host_info in hosts.items():
            device = AggregatedDevice(
                ip=host_ip,
                hostname=host_info.get("hostname"),
                scan_results={scan_result.get("scanner", "unknown"): host_info},
                last_seen=datetime.now(),
                first_seen=datetime.now()
            )
            
            # Extract basic information
            os_info = host_info.get("os", {})
            if os_info:
                device.operating_system = os_info.get("name", "Unknown")
                device.confidence = os_info.get("accuracy", 0) / 100.0
            
            # Extract services for device type hints
            services = host_info.get("services", [])
            device.device_type = self._infer_device_type(services)
            
            devices.append(device)
        
        return devices
    
    def _merge_devices_by_ip(self, devices: List[AggregatedDevice]) -> List[AggregatedDevice]:
        """Merge devices with the same IP address"""
        merged = {}
        
        for device in devices:
            if device.ip in merged:
                # Merge with existing device
                existing = merged[device.ip]
                existing.scan_results.update(device.scan_results)
                existing.last_seen = max(existing.last_seen or datetime.now(), 
                                       device.last_seen or datetime.now())
                existing.first_seen = min(existing.first_seen or datetime.now(),
                                        device.first_seen or datetime.now())
                
                # Update with more confident data
                if device.confidence > existing.confidence:
                    existing.device_type = device.device_type
                    existing.operating_system = device.operating_system
                    existing.confidence = device.confidence
                
                # Merge hostnames
                if device.hostname and not existing.hostname:
                    existing.hostname = device.hostname
                
            else:
                merged[device.ip] = device
        
        return list(merged.values())
    
    async def _analyze_device_with_ai(self, device: AggregatedDevice):
        """Analyze device using AI/LLM"""
        try:
            # Prepare scan data for AI analysis
            scan_data = {
                "hosts": {
                    device.ip: {
                        "hostname": device.hostname,
                        "os": {"name": device.operating_system},
                        "services": self._extract_services_from_scan_results(device.scan_results),
                        "ports": self._extract_ports_from_scan_results(device.scan_results)
                    }
                }
            }
            
            # Get AI analysis
            ai_analysis = await self.llm_analyzer.analyze_device(scan_data)
            device.ai_analysis = ai_analysis
            
            # Update device with AI insights if confidence is higher
            if ai_analysis.confidence > device.confidence:
                device.device_type = ai_analysis.device_type
                device.operating_system = ai_analysis.operating_system
                device.confidence = ai_analysis.confidence
            
        except Exception as e:
            self.logger.error(f"AI analysis failed for {device.ip}: {e}")
    
    def _infer_device_type(self, services: List[Dict[str, Any]]) -> str:
        """Infer device type from services"""
        service_names = [s.get("service", "").lower() for s in services]
        
        # Common service patterns
        if any(svc in service_names for svc in ["ssh", "telnet"]):
            return "Linux Server"
        elif any(svc in service_names for svc in ["rdp", "smb", "netbios-ssn"]):
            return "Windows Server"
        elif any(svc in service_names for svc in ["http", "https", "apache", "nginx"]):
            return "Web Server"
        elif any(svc in service_names for svc in ["ftp", "tftp"]):
            return "File Server"
        elif any(svc in service_names for svc in ["snmp", "dhcp"]):
            return "Network Device"
        elif any(svc in service_names for svc in ["mysql", "postgresql", "mongodb"]):
            return "Database Server"
        elif any(svc in service_names for svc in ["dns", "domain"]):
            return "DNS Server"
        else:
            return "Unknown Device"
    
    def _extract_services_from_scan_results(self, scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract services from all scan results"""
        all_services = []
        
        for scanner, host_info in scan_results.items():
            services = host_info.get("services", [])
            all_services.extend(services)
        
        return all_services
    
    def _extract_ports_from_scan_results(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract port information from all scan results"""
        all_ports = {}
        
        for scanner, host_info in scan_results.items():
            ports = host_info.get("ports", {})
            all_ports.update(ports)
        
        return all_ports
    
    async def enrich_with_external_data(self, device: AggregatedDevice, 
                                      external_data: Dict[str, Any]):
        """Enrich device with external data sources"""
        # RunZero data
        if "runzero" in external_data:
            device.runzero_data = external_data["runzero"]
            await self._apply_runzero_data(device)
        
        # Tanium data
        if "tanium" in external_data:
            device.tanium_data = external_data["tanium"]
            await self._apply_tanium_data(device)
        
        # Armis data
        if "armis" in external_data:
            device.armis_data = external_data["armis"]
            await self._apply_armis_data(device)
        
        # Active Directory data
        if "ad" in external_data:
            device.ad_data = external_data["ad"]
            await self._apply_ad_data(device)
    
    async def _apply_runzero_data(self, device: AggregatedDevice):
        """Apply RunZero enrichment data"""
        if not device.runzero_data:
            return
        
        # Extract device information from RunZero
        runzero_info = device.runzero_data
        
        # Update device type if RunZero has better information
        if runzero_info.get("device_type") and not device.device_type:
            device.device_type = runzero_info["device_type"]
        
        # Update OS information
        if runzero_info.get("os") and not device.operating_system:
            device.operating_system = runzero_info["os"]
        
        # Add tags
        if runzero_info.get("tags"):
            device.tags.extend(runzero_info["tags"])
    
    async def _apply_tanium_data(self, device: AggregatedDevice):
        """Apply Tanium enrichment data"""
        if not device.tanium_data:
            return
        
        tanium_info = device.tanium_data
        
        # Update device information
        if tanium_info.get("computer_name"):
            device.hostname = tanium_info["computer_name"]
        
        # Add Tanium-specific tags
        if tanium_info.get("compliance_status"):
            device.tags.append(f"tanium_compliance:{tanium_info['compliance_status']}")
    
    async def _apply_armis_data(self, device: AggregatedDevice):
        """Apply Armis enrichment data"""
        if not device.armis_data:
            return
        
        armis_info = device.armis_data
        
        # Update device information
        if armis_info.get("device_type"):
            device.device_type = armis_info["device_type"]
        
        # Add risk score
        if armis_info.get("risk_score"):
            device.risk_score = armis_info["risk_score"]
    
    async def _apply_ad_data(self, device: AggregatedDevice):
        """Apply Active Directory enrichment data"""
        if not device.ad_data:
            return
        
        ad_info = device.ad_data
        
        # Update hostname
        if ad_info.get("name"):
            device.hostname = ad_info["name"]
        
        # Add AD-specific information
        if ad_info.get("operating_system"):
            device.operating_system = ad_info["operating_system"]
        
        # Add organizational unit tags
        if ad_info.get("ou"):
            device.tags.append(f"ou:{ad_info['ou']}")
