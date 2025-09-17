"""
Main API router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, scans, devices, integrations, admin, device_corrections, exports, scheduling

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(device_corrections.router, prefix="/device-corrections", tags=["device-corrections"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
api_router.include_router(scheduling.router, prefix="/scheduling", tags=["scheduling"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
