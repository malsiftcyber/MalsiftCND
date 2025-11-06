"""
Admin API endpoints
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime

from app.auth.auth_service import AuthService
from app.services.admin_service import AdminService

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()
admin_service = AdminService()


class SystemConfig(BaseModel):
    scan_timeout: int
    max_concurrent_scans: int
    scan_throttle_rate: int
    ai_analysis_enabled: bool
    auto_sync_enabled: bool
    sync_interval: int


class ScannerConfig(BaseModel):
    scanner_name: str
    enabled: bool
    timeout: int
    rate_limit: Optional[int]
    custom_args: Optional[str]


class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: str
    is_admin: bool = False


class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Require admin privileges"""
    # Extract token from Bearer credentials
    token = credentials.credentials
    # Verify token and extract payload
    payload = auth_service.verify_token(token)
    # In a real implementation, this would check the user's admin status from the payload
    # For now, we'll assume all authenticated users are admins
    return payload


@router.get("/system/config", response_model=SystemConfig)
async def get_system_config(
    payload: dict = Depends(require_admin)
):
    """Get system configuration"""
    try:
        config = await admin_service.get_system_config()
        return SystemConfig(**config)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system config: {str(e)}"
        )


@router.put("/system/config")
async def update_system_config(
    config: SystemConfig,
    payload: dict = Depends(require_admin)
):
    """Update system configuration"""
    try:
        success = await admin_service.update_system_config(config.model_dump())
        if success:
            return {"message": "System configuration updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update system configuration"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update system config: {str(e)}"
        )


@router.get("/scanners", response_model=List[ScannerConfig])
async def list_scanners(
    payload: dict = Depends(require_admin)
):
    """List scanner configurations"""
    try:
        scanners = await admin_service.list_scanners()
        return [ScannerConfig(**scanner) for scanner in scanners]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scanners: {str(e)}"
        )


@router.put("/scanners/{scanner_name}")
async def update_scanner_config(
    scanner_name: str,
    config: ScannerConfig,
    payload: dict = Depends(require_admin)
):
    """Update scanner configuration"""
    try:
        success = await admin_service.update_scanner_config(scanner_name, config.model_dump())
        if success:
            return {"message": "Scanner configuration updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scanner not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scanner config: {str(e)}"
        )


@router.get("/users")
async def list_users(
    limit: int = 50,
    offset: int = 0,
    payload: dict = Depends(require_admin)
):
    """List system users"""
    try:
        users = await admin_service.list_users(limit, offset)
        return users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )


@router.post("/users")
async def create_user(
    request: UserCreateRequest,
    payload: dict = Depends(require_admin)
):
    """Create new user"""
    try:
        user_id = await admin_service.create_user(
            username=request.username,
            email=request.email,
            password=request.password,
            is_admin=request.is_admin
        )
        
        return {
            "message": "User created successfully",
            "user_id": user_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    payload: dict = Depends(require_admin)
):
    """Update user"""
    try:
        success = await admin_service.update_user(user_id, request.model_dump(exclude_unset=True))
        if success:
            return {"message": "User updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    payload: dict = Depends(require_admin)
):
    """Delete user"""
    try:
        success = await admin_service.delete_user(user_id)
        if success:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


@router.get("/system/stats")
async def get_system_stats(
    payload: dict = Depends(require_admin)
):
    """Get system statistics"""
    try:
        stats = await admin_service.get_system_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system stats: {str(e)}"
        )


@router.get("/logs")
async def get_system_logs(
    level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    payload: dict = Depends(require_admin)
):
    """Get system logs"""
    try:
        logs = await admin_service.get_system_logs(level, limit, offset)
        return logs
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system logs: {str(e)}"
        )


@router.get("/scheduling")
async def get_scheduling_config(
    payload: dict = Depends(require_admin)
):
    """Get scan scheduling configuration"""
    try:
        config = await admin_service.get_scheduling_config()
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduling config: {str(e)}"
        )
