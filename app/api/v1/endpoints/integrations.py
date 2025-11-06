"""
External integrations API endpoints
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime

from app.auth.auth_service import AuthService
from app.services.integration_service import IntegrationService

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()
integration_service = IntegrationService()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return payload"""
    token = credentials.credentials
    return auth_service.verify_token(token)


class IntegrationConfig(BaseModel):
    name: str
    enabled: bool
    config: Dict[str, Any]


class IntegrationStatus(BaseModel):
    name: str
    enabled: bool
    connected: bool
    last_sync: Optional[datetime]
    error: Optional[str]


class SyncRequest(BaseModel):
    integration_name: str
    force_full_sync: bool = False


@router.get("/", response_model=List[IntegrationStatus])
async def list_integrations(
    payload: dict = Depends(verify_token)
):
    """List available integrations"""
    try:
        integrations = await integration_service.list_integrations()
        return [IntegrationStatus(**integration) for integration in integrations]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list integrations: {str(e)}"
        )


@router.get("/{integration_name}/status", response_model=IntegrationStatus)
async def get_integration_status(
    integration_name: str,
    payload: dict = Depends(verify_token)
):
    """Get integration status"""
    try:
        status = await integration_service.get_integration_status(integration_name)
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        return IntegrationStatus(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integration status: {str(e)}"
        )


@router.put("/{integration_name}/config")
async def update_integration_config(
    integration_name: str,
    config: IntegrationConfig,
    payload: dict = Depends(verify_token)
):
    """Update integration configuration"""
    try:
        success = await integration_service.update_integration_config(
            integration_name, config.config, config.enabled
        )
        
        if success:
            return {"message": "Integration configuration updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update integration config: {str(e)}"
        )


@router.post("/{integration_name}/sync")
async def sync_integration(
    integration_name: str,
    request: SyncRequest,
    payload: dict = Depends(verify_token)
):
    """Trigger integration sync"""
    try:
        sync_id = await integration_service.sync_integration(
            integration_name, request.force_full_sync
        )
        
        return {
            "message": "Sync initiated",
            "sync_id": sync_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate sync: {str(e)}"
        )


@router.get("/{integration_name}/data")
async def get_integration_data(
    integration_name: str,
    limit: int = 100,
    offset: int = 0,
    payload: dict = Depends(verify_token)
):
    """Get data from integration"""
    try:
        data = await integration_service.get_integration_data(
            integration_name, limit, offset
        )
        
        return data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integration data: {str(e)}"
        )


@router.get("/{integration_name}/sync-history")
async def get_sync_history(
    integration_name: str,
    limit: int = 50,
    offset: int = 0,
    payload: dict = Depends(verify_token)
):
    """Get integration sync history"""
    try:
        history = await integration_service.get_sync_history(
            integration_name, limit, offset
        )
        
        return history
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sync history: {str(e)}"
        )
