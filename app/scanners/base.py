"""
Base scanner interface and common functionality
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging


class ScanType(Enum):
    """Types of scans supported"""
    PING_SWEEP = "ping_sweep"
    PORT_SCAN = "port_scan"
    SERVICE_DETECTION = "service_detection"
    OS_DETECTION = "os_detection"
    VULNERABILITY_SCAN = "vulnerability_scan"


@dataclass
class ScanTarget:
    """Represents a scan target"""
    ip: str
    hostname: Optional[str] = None
    ports: Optional[List[int]] = None
    scan_type: ScanType = ScanType.PORT_SCAN


@dataclass
class ScanResult:
    """Base scan result"""
    target: ScanTarget
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    scan_time: float = 0.0


class BaseScanner(ABC):
    """Base class for all scanners"""
    
    def __init__(self, name: str, timeout: int = 300):
        self.name = name
        self.timeout = timeout
        self.logger = logging.getLogger(f"scanner.{name}")
    
    @abstractmethod
    async def scan(self, target: ScanTarget) -> ScanResult:
        """Perform a scan on the target"""
        pass
    
    @abstractmethod
    def get_supported_scan_types(self) -> List[ScanType]:
        """Get list of supported scan types"""
        pass
    
    def validate_target(self, target: ScanTarget) -> bool:
        """Validate scan target"""
        if not target.ip:
            return False
        return True
    
    async def scan_with_timeout(self, target: ScanTarget) -> ScanResult:
        """Scan with timeout protection"""
        try:
            return await asyncio.wait_for(
                self.scan(target), 
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            return ScanResult(
                target=target,
                success=False,
                data={},
                error=f"Scan timeout after {self.timeout} seconds"
            )
        except Exception as e:
            self.logger.error(f"Scan error: {e}")
            return ScanResult(
                target=target,
                success=False,
                data={},
                error=str(e)
            )
