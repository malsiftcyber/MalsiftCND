"""
Masscan scanner implementation for high-speed port scanning
"""
import subprocess
import json
import asyncio
from typing import List, Dict, Any
from app.scanners.base import BaseScanner, ScanTarget, ScanResult, ScanType


class MasscanScanner(BaseScanner):
    """Masscan-based high-speed port scanner"""
    
    def __init__(self, timeout: int = 300, rate: int = 1000):
        super().__init__("masscan", timeout)
        self.rate = rate  # packets per second
    
    async def scan(self, target: ScanTarget) -> ScanResult:
        """Perform masscan scan"""
        if not self.validate_target(target):
            return ScanResult(
                target=target,
                success=False,
                data={},
                error="Invalid target"
            )
        
        if target.scan_type not in [ScanType.PORT_SCAN, ScanType.PING_SWEEP]:
            return ScanResult(
                target=target,
                success=False,
                data={},
                error=f"Masscan does not support {target.scan_type.value}"
            )
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Build masscan command
            cmd = self._build_masscan_command(target)
            
            # Run masscan
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            
            scan_time = asyncio.get_event_loop().time() - start_time
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown masscan error"
                return ScanResult(
                    target=target,
                    success=False,
                    data={},
                    error=error_msg
                )
            
            # Parse results
            scan_data = self._parse_masscan_output(stdout.decode(), target)
            
            return ScanResult(
                target=target,
                success=True,
                data=scan_data,
                scan_time=scan_time
            )
            
        except asyncio.TimeoutError:
            return ScanResult(
                target=target,
                success=False,
                data={},
                error=f"Masscan timeout after {self.timeout} seconds"
            )
        except Exception as e:
            self.logger.error(f"Masscan scan failed: {e}")
            return ScanResult(
                target=target,
                success=False,
                data={},
                error=str(e)
            )
    
    def _build_masscan_command(self, target: ScanTarget) -> List[str]:
        """Build masscan command"""
        cmd = ["masscan"]
        
        # Add target
        cmd.append(target.ip)
        
        # Add ports
        if target.ports:
            port_list = ",".join(map(str, target.ports))
            cmd.extend(["-p", port_list])
        else:
            cmd.extend(["-p", "1-65535"])
        
        # Add rate
        cmd.extend(["--rate", str(self.rate)])
        
        # Add output format
        cmd.extend(["-oJ", "-"])  # JSON output to stdout
        
        # Add timeout
        cmd.extend(["--max-rate", str(self.rate)])
        
        return cmd
    
    def _parse_masscan_output(self, output: str, target: ScanTarget) -> Dict[str, Any]:
        """Parse masscan JSON output"""
        parsed_data = {
            "hosts": {},
            "scan_info": {
                "scanner": "masscan",
                "rate": self.rate
            }
        }
        
        try:
            # Masscan outputs one JSON object per line
            lines = output.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                
                try:
                    data = json.loads(line)
                    
                    if data.get("ip") == target.ip:
                        host_ip = data["ip"]
                        
                        if host_ip not in parsed_data["hosts"]:
                            parsed_data["hosts"][host_ip] = {
                                "ip": host_ip,
                                "ports": {},
                                "services": []
                            }
                        
                        # Parse port information
                        port_info = {
                            "port": data.get("port", 0),
                            "state": "open",  # Masscan only reports open ports
                            "protocol": data.get("proto", "tcp"),
                            "service": "",  # Masscan doesn't do service detection
                            "version": "",
                            "product": "",
                            "extrainfo": ""
                        }
                        
                        parsed_data["hosts"][host_ip]["ports"][port_info["port"]] = port_info
                        
                        if port_info["port"]:
                            parsed_data["hosts"][host_ip]["services"].append({
                                "port": port_info["port"],
                                "protocol": port_info["protocol"],
                                "state": port_info["state"]
                            })
                
                except json.JSONDecodeError:
                    continue
        
        except Exception as e:
            self.logger.error(f"Error parsing masscan output: {e}")
        
        return parsed_data
    
    def get_supported_scan_types(self) -> List[ScanType]:
        """Get supported scan types"""
        return [ScanType.PORT_SCAN, ScanType.PING_SWEEP]
    
    def set_rate(self, rate: int):
        """Set scan rate (packets per second)"""
        self.rate = max(1, min(rate, 100000))  # Limit between 1 and 100k pps
