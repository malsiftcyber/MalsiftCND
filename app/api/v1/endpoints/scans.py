"""
Scan management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from app.scanners.base import ScanType
from app.scanners.nmap_scanner import NmapScanner
from app.scanners.masscan_scanner import MasscanScanner
from app.services.scan_service import ScanService
from app.auth.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()
scan_service = ScanService()


class ScanRequest(BaseModel):
    targets: List[str] = Field(..., description="List of IP addresses or CIDR blocks to scan")
    scan_type: ScanType = Field(default=ScanType.PORT_SCAN, description="Type of scan to perform")
    ports: Optional[List[int]] = Field(default=None, description="Specific ports to scan")
    scanner: str = Field(default="nmap", description="Scanner to use (nmap, masscan)")
    timeout: int = Field(default=300, description="Scan timeout in seconds")
    rate_limit: Optional[int] = Field(default=None, description="Rate limit for scanning")


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    targets: List[str]
    scan_type: str
    scanner: str
    created_at: datetime
    estimated_duration: int


class ScanStatus(BaseModel):
    scan_id: str
    status: str
    progress: float
    current_target: Optional[str]
    results_count: int
    started_at: datetime
    estimated_completion: Optional[datetime]


class ScanResult(BaseModel):
    scan_id: str
    target: str
    success: bool
    data: dict
    error: Optional[str]
    scan_time: float
    completed_at: datetime


@router.post("/", response_model=ScanResponse)
async def create_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(auth_service.verify_token)
):
    """Create a new scan"""
    try:
        scan_id = await scan_service.create_scan(
            targets=request.targets,
            scan_type=request.scan_type,
            ports=request.ports,
            scanner=request.scanner,
            timeout=request.timeout,
            rate_limit=request.rate_limit,
            user_id=token.get("user_id")
        )
        
        # Start scan in background
        background_tasks.add_task(
            scan_service.execute_scan,
            scan_id
        )
        
        return ScanResponse(
            scan_id=scan_id,
            status="queued",
            targets=request.targets,
            scan_type=request.scan_type.value,
            scanner=request.scanner,
            created_at=datetime.now(),
            estimated_duration=scan_service.estimate_duration(request.targets, request.scan_type)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create scan: {str(e)}"
        )


@router.get("/{scan_id}/status", response_model=ScanStatus)
async def get_scan_status(
    scan_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Get scan status and progress"""
    try:
        status_info = await scan_service.get_scan_status(scan_id)
        return ScanStatus(**status_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan not found: {str(e)}"
        )


@router.get("/{scan_id}/results", response_model=List[ScanResult])
async def get_scan_results(
    scan_id: str,
    limit: int = 100,
    offset: int = 0,
    token: str = Depends(auth_service.verify_token)
):
    """Get scan results"""
    try:
        results = await scan_service.get_scan_results(scan_id, limit, offset)
        return [ScanResult(**result) for result in results]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan results not found: {str(e)}"
        )


@router.get("/", response_model=List[ScanResponse])
async def list_scans(
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[str] = None,
    token: str = Depends(auth_service.verify_token)
):
    """List user's scans"""
    try:
        scans = await scan_service.list_user_scans(
            user_id=token.get("user_id"),
            limit=limit,
            offset=offset,
            status_filter=status_filter
        )
        return [ScanResponse(**scan) for scan in scans]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scans: {str(e)}"
        )


@router.delete("/{scan_id}")
async def cancel_scan(
    scan_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Cancel a running scan"""
    try:
        success = await scan_service.cancel_scan(scan_id, token.get("user_id"))
        if success:
            return {"message": "Scan cancelled successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found or cannot be cancelled"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel scan: {str(e)}"
        )


@router.get("/{scan_id}/export")
async def export_scan_results(
    scan_id: str,
    format: str = "json",
    token: str = Depends(auth_service.verify_token)
):
    """Export scan results in various formats"""
    try:
        if format == "json":
            results = await scan_service.export_scan_results_json(scan_id)
            return results
        elif format == "csv":
            results = await scan_service.export_scan_results_csv(scan_id)
            return results
        elif format == "xml":
            results = await scan_service.export_scan_results_xml(scan_id)
            return results
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported export format"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to export scan results: {str(e)}"
        )
