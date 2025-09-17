"""
Nmap scanner implementation
"""
import nmap
import asyncio
from typing import List, Dict, Any
from app.scanners.base import BaseScanner, ScanTarget, ScanResult, ScanType


class NmapScanner(BaseScanner):
    """Nmap-based network scanner"""
    
    def __init__(self, timeout: int = 300):
        super().__init__("nmap", timeout)
        self.nm = nmap.PortScanner()
    
    async def scan(self, target: ScanTarget) -> ScanResult:
        """Perform nmap scan"""
        if not self.validate_target(target):
            return ScanResult(
                target=target,
                success=False,
                data={},
                error="Invalid target"
            )
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Build scan arguments based on scan type
            scan_args = self._build_scan_args(target)
            
            # Perform the scan
            result = self.nm.scan(
                hosts=target.ip,
                arguments=scan_args,
                timeout=self.timeout
            )
            
            scan_time = asyncio.get_event_loop().time() - start_time
            
            # Parse results
            scan_data = self._parse_scan_result(result, target)
            
            return ScanResult(
                target=target,
                success=True,
                data=scan_data,
                scan_time=scan_time
            )
            
        except Exception as e:
            self.logger.error(f"Nmap scan failed: {e}")
            return ScanResult(
                target=target,
                success=False,
                data={},
                error=str(e)
            )
    
    def _build_scan_args(self, target: ScanTarget) -> str:
        """Build nmap scan arguments"""
        args = []
        
        if target.scan_type == ScanType.PING_SWEEP:
            args.append("-sn")
        elif target.scan_type == ScanType.PORT_SCAN:
            if target.ports:
                port_list = ",".join(map(str, target.ports))
                args.append(f"-p {port_list}")
            else:
                args.append("-p 1-65535")
            args.extend(["-sS", "-T4"])
        elif target.scan_type == ScanType.SERVICE_DETECTION:
            args.extend(["-sV", "-sS", "-T4"])
        elif target.scan_type == ScanType.OS_DETECTION:
            args.extend(["-O", "-sS", "-T4"])
        elif target.scan_type == ScanType.VULNERABILITY_SCAN:
            args.extend(["--script vuln", "-sV", "-sS", "-T4"])
        
        # Add common arguments
        args.extend([
            "--max-retries 3",
            "--host-timeout 30s",
            "--max-rtt-timeout 1s"
        ])
        
        return " ".join(args)
    
    def _parse_scan_result(self, result: Dict[str, Any], target: ScanTarget) -> Dict[str, Any]:
        """Parse nmap scan results"""
        parsed_data = {
            "hosts": {},
            "scan_info": result.get("nmap", {}),
            "command_line": result.get("nmap", {}).get("command_line", "")
        }
        
        for host_ip, host_data in result.get("scan", {}).items():
            host_info = {
                "ip": host_ip,
                "hostname": host_data.get("hostnames", [{}])[0].get("name", ""),
                "status": host_data.get("status", {}).get("state", "unknown"),
                "ports": {},
                "os": {},
                "services": []
            }
            
            # Parse ports
            for port_num, port_data in host_data.get("tcp", {}).items():
                port_info = {
                    "port": port_num,
                    "state": port_data.get("state", "unknown"),
                    "service": port_data.get("name", ""),
                    "version": port_data.get("version", ""),
                    "product": port_data.get("product", ""),
                    "extrainfo": port_data.get("extrainfo", ""),
                    "cpe": port_data.get("cpe", "")
                }
                host_info["ports"][port_num] = port_info
                
                if port_info["service"]:
                    host_info["services"].append({
                        "port": port_num,
                        "service": port_info["service"],
                        "version": port_info["version"],
                        "product": port_info["product"]
                    })
            
            # Parse OS information
            os_data = host_data.get("osmatch", [])
            if os_data:
                best_match = os_data[0]
                host_info["os"] = {
                    "name": best_match.get("name", ""),
                    "accuracy": best_match.get("accuracy", 0),
                    "type": best_match.get("type", ""),
                    "vendor": best_match.get("vendor", ""),
                    "family": best_match.get("osfamily", "")
                }
            
            parsed_data["hosts"][host_ip] = host_info
        
        return parsed_data
    
    def get_supported_scan_types(self) -> List[ScanType]:
        """Get supported scan types"""
        return [
            ScanType.PING_SWEEP,
            ScanType.PORT_SCAN,
            ScanType.SERVICE_DETECTION,
            ScanType.OS_DETECTION,
            ScanType.VULNERABILITY_SCAN
        ]
