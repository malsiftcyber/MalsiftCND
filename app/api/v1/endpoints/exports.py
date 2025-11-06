"""
Export API endpoints for CSV and other format reports
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
import io

from app.auth.auth_service import AuthService
from app.services.export_service import ExportService

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()
export_service = ExportService()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return payload"""
    token = credentials.credentials
    return auth_service.verify_token(token)


class DeviceExportRequest(BaseModel):
    device_ids: Optional[List[str]] = None
    include_corrections: bool = True
    include_services: bool = True
    include_ai_analysis: bool = True


class DiscoveryReportRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    device_types: Optional[List[str]] = None
    risk_score_min: Optional[float] = None
    risk_score_max: Optional[float] = None


@router.get("/devices")
async def export_devices(
    format: str = Query(default="csv", description="Export format (csv, json)"),
    payload: dict = Depends(verify_token)
):
    """Export devices in specified format"""
    if format.lower() == "csv":
        return await export_devices_csv(
            device_ids=None,
            include_corrections=True,
            include_services=True,
            include_ai_analysis=True,
            payload=payload
        )
    elif format.lower() == "json":
        # Get devices and return as JSON
        from app.services.device_service import DeviceService
        device_service = DeviceService()
        devices = await device_service.list_devices(limit=10000, offset=0)
        return {"devices": devices, "exported_at": datetime.now().isoformat()}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}"
        )


@router.get("/devices/csv")
async def export_devices_csv(
    device_ids: Optional[str] = Query(default=None, description="Comma-separated device IDs"),
    include_corrections: bool = Query(default=True, description="Include correction data"),
    include_services: bool = Query(default=True, description="Include service data"),
    include_ai_analysis: bool = Query(default=True, description="Include AI analysis data"),
    payload: dict = Depends(verify_token)
):
    """Export devices to CSV format"""
    try:
        # Parse device IDs if provided
        device_id_list = None
        if device_ids:
            device_id_list = [id.strip() for id in device_ids.split(',') if id.strip()]
        
        # Generate CSV content
        csv_content = await export_service.export_devices_csv(
            device_ids=device_id_list,
            include_corrections=include_corrections,
            include_services=include_services,
            include_ai_analysis=include_ai_analysis
        )
        
        # Create streaming response
        def generate():
            yield csv_content
        
        return StreamingResponse(
            generate(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=devices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export devices CSV: {str(e)}"
        )


@router.post("/devices/csv")
async def export_devices_csv_post(
    request: DeviceExportRequest,
    payload: dict = Depends(verify_token)
):
    """Export devices to CSV format (POST method for complex filters)"""
    try:
        # Generate CSV content
        csv_content = await export_service.export_devices_csv(
            device_ids=request.device_ids,
            include_corrections=request.include_corrections,
            include_services=request.include_services,
            include_ai_analysis=request.include_ai_analysis
        )
        
        # Create streaming response
        def generate():
            yield csv_content
        
        return StreamingResponse(
            generate(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=devices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export devices CSV: {str(e)}"
        )


@router.get("/scans/{scan_id}/csv")
async def export_scan_results_csv(
    scan_id: str,
    payload: dict = Depends(verify_token)
):
    """Export scan results to CSV format"""
    try:
        # Generate CSV content
        csv_content = await export_service.export_scan_results_csv(scan_id)
        
        # Create streaming response
        def generate():
            yield csv_content
        
        return StreamingResponse(
            generate(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=scan_{scan_id}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export scan results CSV: {str(e)}"
        )


@router.get("/corrections/csv")
async def export_corrections_csv(
    device_id: Optional[str] = Query(default=None, description="Device ID to filter corrections"),
    payload: dict = Depends(verify_token)
):
    """Export device corrections to CSV format"""
    try:
        # Generate CSV content
        csv_content = await export_service.export_corrections_csv(device_id)
        
        # Create streaming response
        def generate():
            yield csv_content
        
        filename = f"corrections_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if device_id:
            filename = f"device_{device_id}_corrections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            generate(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export corrections CSV: {str(e)}"
        )


@router.post("/discovery-report/csv")
async def export_discovery_report_csv(
    request: DiscoveryReportRequest,
    payload: dict = Depends(verify_token)
):
    """Export comprehensive discovery report to CSV"""
    try:
        # Generate CSV content
        csv_content = await export_service.export_discovery_report_csv(
            start_date=request.start_date,
            end_date=request.end_date,
            device_types=request.device_types,
            risk_score_min=request.risk_score_min,
            risk_score_max=request.risk_score_max
        )
        
        # Create streaming response
        def generate():
            yield csv_content
        
        return StreamingResponse(
            generate(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=discovery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export discovery report CSV: {str(e)}"
        )


@router.get("/discovery-report/csv")
async def export_discovery_report_csv_get(
    start_date: Optional[datetime] = Query(default=None, description="Start date for report"),
    end_date: Optional[datetime] = Query(default=None, description="End date for report"),
    device_types: Optional[str] = Query(default=None, description="Comma-separated device types"),
    risk_score_min: Optional[float] = Query(default=None, description="Minimum risk score"),
    risk_score_max: Optional[float] = Query(default=None, description="Maximum risk score"),
    payload: dict = Depends(verify_token)
):
    """Export comprehensive discovery report to CSV (GET method)"""
    try:
        # Parse device types if provided
        device_type_list = None
        if device_types:
            device_type_list = [t.strip() for t in device_types.split(',') if t.strip()]
        
        # Generate CSV content
        csv_content = await export_service.export_discovery_report_csv(
            start_date=start_date,
            end_date=end_date,
            device_types=device_type_list,
            risk_score_min=risk_score_min,
            risk_score_max=risk_score_max
        )
        
        # Create streaming response
        def generate():
            yield csv_content
        
        return StreamingResponse(
            generate(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=discovery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export discovery report CSV: {str(e)}"
        )


@router.get("/new-devices/csv")
async def export_new_devices_csv(
    hours: int = Query(default=24, description="Number of hours to look back for new devices", ge=1, le=168),
    payload: dict = Depends(verify_token)
):
    """Export newly discovered devices from the last N hours"""
    try:
        # Generate CSV content
        csv_content = await export_service.export_new_devices_csv(hours)
        
        # Create streaming response
        def generate():
            yield csv_content
        
        return StreamingResponse(
            generate(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=new_devices_last_{hours}h_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export new devices CSV: {str(e)}"
        )


@router.get("/formats")
async def get_export_formats(
    payload: dict = Depends(verify_token)
):
    """Get available export formats and options"""
    return {
        "formats": [
            {
                "name": "CSV",
                "description": "Comma-separated values format",
                "media_type": "text/csv",
                "supported_data": [
                    "devices",
                    "scan_results", 
                    "corrections",
                    "discovery_reports",
                    "new_devices"
                ]
            }
        ],
        "device_export_options": {
            "include_corrections": "Include device correction history",
            "include_services": "Include service and port information",
            "include_ai_analysis": "Include AI analysis details"
        },
        "discovery_report_options": {
            "date_range": "Filter by discovery date range",
            "device_types": "Filter by specific device types",
            "risk_score_range": "Filter by risk score range"
        },
        "new_devices_options": {
            "hours": "Number of hours to look back for new devices (1-168)"
        }
    }
