"""
Scan service for managing and executing scans
"""
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

from app.scanners.base import ScanTarget, ScanType
from app.scanners.nmap_scanner import NmapScanner
from app.scanners.masscan_scanner import MasscanScanner
from app.services.data_aggregator import DataAggregator


class ScanStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScanService:
    """Service for managing scans"""
    
    def __init__(self):
        self.logger = logging.getLogger("services.scan_service")
        self.scanners = {
            "nmap": NmapScanner(),
            "masscan": MasscanScanner()
        }
        self.data_aggregator = DataAggregator()
        self.active_scans: Dict[str, Dict[str, Any]] = {}
        self.scan_results: Dict[str, List[Dict[str, Any]]] = {}
    
    async def create_scan(self, targets: List[str], scan_type: ScanType, 
                         ports: Optional[List[int]] = None, scanner: str = "nmap",
                         timeout: int = 300, rate_limit: Optional[int] = None,
                         user_id: str = None) -> str:
        """Create a new scan"""
        scan_id = str(uuid.uuid4())
        
        scan_info = {
            "scan_id": scan_id,
            "targets": targets,
            "scan_type": scan_type,
            "ports": ports,
            "scanner": scanner,
            "timeout": timeout,
            "rate_limit": rate_limit,
            "user_id": user_id,
            "status": ScanStatus.QUEUED,
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None,
            "progress": 0.0,
            "current_target": None,
            "results_count": 0
        }
        
        self.active_scans[scan_id] = scan_info
        self.scan_results[scan_id] = []
        
        self.logger.info(f"Created scan {scan_id} with {len(targets)} targets")
        return scan_id
    
    async def execute_scan(self, scan_id: str):
        """Execute a scan"""
        if scan_id not in self.active_scans:
            self.logger.error(f"Scan {scan_id} not found")
            return
        
        scan_info = self.active_scans[scan_id]
        scanner_name = scan_info["scanner"]
        
        if scanner_name not in self.scanners:
            self.logger.error(f"Unknown scanner: {scanner_name}")
            await self._update_scan_status(scan_id, ScanStatus.FAILED, error="Unknown scanner")
            return
        
        scanner = self.scanners[scanner_name]
        scan_type = scan_info["scan_type"]
        targets = scan_info["targets"]
        
        # Update status to running
        await self._update_scan_status(scan_id, ScanStatus.RUNNING)
        
        try:
            total_targets = len(targets)
            completed_targets = 0
            
            for target_ip in targets:
                if scan_id not in self.active_scans:
                    # Scan was cancelled
                    break
                
                # Update current target
                await self._update_scan_progress(scan_id, target_ip, completed_targets / total_targets)
                
                # Create scan target
                scan_target = ScanTarget(
                    ip=target_ip,
                    ports=scan_info["ports"],
                    scan_type=scan_type
                )
                
                # Execute scan
                result = await scanner.scan_with_timeout(scan_target)
                
                # Store result
                result_data = {
                    "scan_id": scan_id,
                    "target": target_ip,
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                    "scan_time": result.scan_time,
                    "completed_at": datetime.now()
                }
                
                self.scan_results[scan_id].append(result_data)
                completed_targets += 1
                
                # Rate limiting
                if scan_info["rate_limit"]:
                    await asyncio.sleep(1.0 / scan_info["rate_limit"])
            
            # Mark scan as completed
            await self._update_scan_status(scan_id, ScanStatus.COMPLETED)
            
            # Perform data aggregation
            await self._aggregate_scan_results(scan_id)
            
        except Exception as e:
            self.logger.error(f"Scan {scan_id} failed: {e}")
            await self._update_scan_status(scan_id, ScanStatus.FAILED, error=str(e))
    
    async def _update_scan_status(self, scan_id: str, status: ScanStatus, error: str = None):
        """Update scan status"""
        if scan_id in self.active_scans:
            self.active_scans[scan_id]["status"] = status
            
            if status == ScanStatus.RUNNING:
                self.active_scans[scan_id]["started_at"] = datetime.now()
            elif status in [ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.CANCELLED]:
                self.active_scans[scan_id]["completed_at"] = datetime.now()
            
            if error:
                self.active_scans[scan_id]["error"] = error
    
    async def _update_scan_progress(self, scan_id: str, current_target: str, progress: float):
        """Update scan progress"""
        if scan_id in self.active_scans:
            self.active_scans[scan_id]["current_target"] = current_target
            self.active_scans[scan_id]["progress"] = progress
    
    async def _aggregate_scan_results(self, scan_id: str):
        """Aggregate scan results using AI analysis"""
        try:
            results = self.scan_results.get(scan_id, [])
            scan_data = [result["data"] for result in results if result["success"]]
            
            if scan_data:
                aggregated_devices = await self.data_aggregator.aggregate_scan_data(scan_data)
                
                # Store aggregated results
                self.active_scans[scan_id]["aggregated_devices"] = [
                    {
                        "ip": device.ip,
                        "hostname": device.hostname,
                        "device_type": device.device_type,
                        "operating_system": device.operating_system,
                        "confidence": device.confidence,
                        "ai_analysis": device.ai_analysis.__dict__ if device.ai_analysis else None
                    }
                    for device in aggregated_devices
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to aggregate results for scan {scan_id}: {e}")
    
    async def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """Get scan status"""
        if scan_id not in self.active_scans:
            raise ValueError("Scan not found")
        
        scan_info = self.active_scans[scan_id]
        
        # Calculate estimated completion
        estimated_completion = None
        if scan_info["status"] == ScanStatus.RUNNING and scan_info["started_at"]:
            elapsed = datetime.now() - scan_info["started_at"]
            if scan_info["progress"] > 0:
                total_estimated = elapsed / scan_info["progress"]
                estimated_completion = scan_info["started_at"] + total_estimated
        
        return {
            "scan_id": scan_id,
            "status": scan_info["status"].value,
            "progress": scan_info["progress"],
            "current_target": scan_info["current_target"],
            "results_count": len(self.scan_results.get(scan_id, [])),
            "started_at": scan_info["started_at"],
            "estimated_completion": estimated_completion
        }
    
    async def get_scan_results(self, scan_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get scan results"""
        if scan_id not in self.scan_results:
            raise ValueError("Scan results not found")
        
        results = self.scan_results[scan_id]
        return results[offset:offset + limit]
    
    async def list_user_scans(self, user_id: str, limit: int = 50, offset: int = 0,
                            status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List user's scans"""
        user_scans = [
            scan for scan in self.active_scans.values()
            if scan["user_id"] == user_id
        ]
        
        if status_filter:
            user_scans = [
                scan for scan in user_scans
                if scan["status"].value == status_filter
            ]
        
        # Sort by creation date (newest first)
        user_scans.sort(key=lambda x: x["created_at"], reverse=True)
        
        return user_scans[offset:offset + limit]
    
    async def cancel_scan(self, scan_id: str, user_id: str) -> bool:
        """Cancel a scan"""
        if scan_id not in self.active_scans:
            return False
        
        scan_info = self.active_scans[scan_id]
        
        # Check if user owns the scan
        if scan_info["user_id"] != user_id:
            return False
        
        # Check if scan can be cancelled
        if scan_info["status"] not in [ScanStatus.QUEUED, ScanStatus.RUNNING]:
            return False
        
        await self._update_scan_status(scan_id, ScanStatus.CANCELLED)
        return True
    
    def estimate_duration(self, targets: List[str], scan_type: ScanType) -> int:
        """Estimate scan duration in seconds"""
        base_time_per_target = {
            ScanType.PING_SWEEP: 5,
            ScanType.PORT_SCAN: 30,
            ScanType.SERVICE_DETECTION: 60,
            ScanType.OS_DETECTION: 90,
            ScanType.VULNERABILITY_SCAN: 300
        }
        
        time_per_target = base_time_per_target.get(scan_type, 30)
        return len(targets) * time_per_target
    
    async def export_scan_results_json(self, scan_id: str) -> Dict[str, Any]:
        """Export scan results as JSON"""
        if scan_id not in self.scan_results:
            raise ValueError("Scan results not found")
        
        scan_info = self.active_scans.get(scan_id, {})
        results = self.scan_results[scan_id]
        
        return {
            "scan_info": scan_info,
            "results": results,
            "exported_at": datetime.now().isoformat()
        }
    
    async def export_scan_results_csv(self, scan_id: str) -> str:
        """Export scan results as CSV"""
        # This would generate CSV format
        # For now, return a placeholder
        return "CSV export not implemented yet"
    
    async def export_scan_results_xml(self, scan_id: str) -> str:
        """Export scan results as XML"""
        # This would generate XML format
        # For now, return a placeholder
        return "XML export not implemented yet"
