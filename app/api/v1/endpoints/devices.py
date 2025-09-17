"""
Device management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime

from app.auth.auth_service import AuthService
from app.services.device_service import DeviceService

router = APIRouter()
auth_service = AuthService()
device_service = DeviceService()


class DeviceResponse(BaseModel):
    ip: str
    hostname: Optional[str]
    device_type: str
    operating_system: str
    confidence: float
    last_seen: datetime
    first_seen: datetime
    tags: List[str]
    risk_score: float
    services: List[dict]
    ai_analysis: Optional[dict]


class DeviceSearchRequest(BaseModel):
    query: Optional[str] = None
    device_type: Optional[str] = None
    operating_system: Optional[str] = None
    ip_range: Optional[str] = None
    tags: Optional[List[str]] = None
    risk_score_min: Optional[float] = None
    risk_score_max: Optional[float] = None


@router.get("/", response_model=List[DeviceResponse])
async def list_devices(
    limit: int = Query(default=50, le=1000),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None),
    device_type: Optional[str] = Query(default=None),
    os: Optional[str] = Query(default=None),
    token: str = Depends(auth_service.verify_token)
):
    """List discovered devices"""
    try:
        devices = await device_service.list_devices(
            limit=limit,
            offset=offset,
            search=search,
            device_type=device_type,
            operating_system=os
        )
        
        return [DeviceResponse(**device) for device in devices]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list devices: {str(e)}"
        )


@router.get("/{device_ip}", response_model=DeviceResponse)
async def get_device(
    device_ip: str,
    token: str = Depends(auth_service.verify_token)
):
    """Get device details"""
    try:
        device = await device_service.get_device(device_ip)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        return DeviceResponse(**device)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get device: {str(e)}"
        )


@router.post("/search", response_model=List[DeviceResponse])
async def search_devices(
    request: DeviceSearchRequest,
    limit: int = Query(default=50, le=1000),
    offset: int = Query(default=0, ge=0),
    token: str = Depends(auth_service.verify_token)
):
    """Search devices with advanced filters"""
    try:
        devices = await device_service.search_devices(
            query=request.query,
            device_type=request.device_type,
            operating_system=request.operating_system,
            ip_range=request.ip_range,
            tags=request.tags,
            risk_score_min=request.risk_score_min,
            risk_score_max=request.risk_score_max,
            limit=limit,
            offset=offset
        )
        
        return [DeviceResponse(**device) for device in devices]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search devices: {str(e)}"
        )


@router.get("/{device_ip}/history")
async def get_device_history(
    device_ip: str,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    token: str = Depends(auth_service.verify_token)
):
    """Get device discovery history"""
    try:
        history = await device_service.get_device_history(
            device_ip=device_ip,
            limit=limit,
            offset=offset
        )
        
        return history
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get device history: {str(e)}"
        )


@router.put("/{device_ip}/tags")
async def update_device_tags(
    device_ip: str,
    tags: List[str],
    token: str = Depends(auth_service.verify_token)
):
    """Update device tags"""
    try:
        success = await device_service.update_device_tags(device_ip, tags)
        if success:
            return {"message": "Tags updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tags: {str(e)}"
        )


@router.put("/{device_ip}/notes")
async def update_device_notes(
    device_ip: str,
    notes: str,
    token: str = Depends(auth_service.verify_token)
):
    """Update device notes"""
    try:
        success = await device_service.update_device_notes(device_ip, notes)
        if success:
            return {"message": "Notes updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notes: {str(e)}"
        )


@router.get("/stats/summary")
async def get_device_stats(
    token: str = Depends(auth_service.verify_token)
):
    """Get device statistics summary"""
    try:
        stats = await device_service.get_device_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get device stats: {str(e)}"
        )
