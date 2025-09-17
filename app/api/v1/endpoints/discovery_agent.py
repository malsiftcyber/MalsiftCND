"""
Discovery agent API endpoints
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime

from app.auth.auth_service import AuthService
from app.services.discovery_agent_service import DiscoveryAgentService
from app.models.discovery_agent import AgentPlatform, AgentStatus

router = APIRouter()
auth_service = AuthService()
agent_service = DiscoveryAgentService()


# Request/Response Models
class AgentRegistrationRequest(BaseModel):
    name: str
    description: Optional[str] = None
    platform: AgentPlatform
    architecture: str
    os_version: Optional[str] = None
    agent_version: str
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    network_interface: Optional[str] = None
    server_url: str
    ssl_enabled: bool = True
    api_key: Optional[str] = None
    company_id: Optional[str] = None
    site_id: Optional[str] = None
    target_networks: Optional[List[str]] = None
    excluded_networks: Optional[List[str]] = None
    target_ports: Optional[List[int]] = None
    excluded_ports: Optional[List[int]] = None


class HeartbeatRequest(BaseModel):
    status: AgentStatus
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    network_usage: Optional[float] = None
    agent_version: Optional[str] = None
    os_version: Optional[str] = None
    uptime_seconds: Optional[int] = None
    active_scans: int = 0
    queued_scans: int = 0
    last_scan_duration: Optional[float] = None
    error_count: int = 0
    last_error: Optional[str] = None
    heartbeat_data: Optional[Dict[str, Any]] = None


class ScanResultsRequest(BaseModel):
    scan_type: str
    targets: List[str]
    ports: Optional[List[int]] = None
    scanner: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    devices_found: int = 0
    ports_found: int = 0
    services_found: int = 0
    scan_results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


class AgentUpdateRequest(BaseModel):
    version: str
    platform: AgentPlatform
    architecture: str
    release_notes: Optional[str] = None
    download_url: str
    checksum: str
    file_size: int
    is_required: bool = False
    rollout_percentage: int = 100
    rollout_groups: Optional[List[str]] = None


@router.post("/agents/register", response_model=Dict[str, Any])
async def register_agent(
    request: AgentRegistrationRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Register a new discovery agent"""
    try:
        result = await agent_service.register_agent(request.dict())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register agent: {str(e)}"
        )


@router.post("/agents/{agent_id}/heartbeat")
async def update_heartbeat(
    agent_id: str,
    request: HeartbeatRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Update agent heartbeat"""
    try:
        result = await agent_service.update_agent_heartbeat(agent_id, request.dict())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update heartbeat: {str(e)}"
        )


@router.post("/agents/{agent_id}/scan-results")
async def submit_scan_results(
    agent_id: str,
    request: ScanResultsRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Submit scan results from agent"""
    try:
        result = await agent_service.submit_scan_results(agent_id, request.dict())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit scan results: {str(e)}"
        )


@router.get("/agents/{agent_id}/configuration", response_model=Dict[str, Any])
async def get_agent_configuration(
    agent_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Get agent configuration"""
    try:
        result = await agent_service.get_agent_configuration(agent_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent configuration: {str(e)}"
        )


@router.get("/agents/{agent_id}/status", response_model=Dict[str, Any])
async def get_agent_status(
    agent_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Get agent status and metrics"""
    try:
        result = await agent_service.get_agent_status(agent_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.get("/agents", response_model=List[Dict[str, Any]])
async def list_agents(
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    site_id: Optional[str] = Query(None, description="Filter by site ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    token: str = Depends(auth_service.verify_token)
):
    """List all agents with optional filtering"""
    try:
        result = await agent_service.list_agents(company_id, site_id, status)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.get("/agents/{agent_id}/updates")
async def check_for_updates(
    agent_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Check for available updates for an agent"""
    try:
        result = await agent_service.check_for_updates(agent_id)
        if result:
            return result
        else:
            return {"message": "No updates available"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check for updates: {str(e)}"
        )


@router.post("/updates", response_model=Dict[str, Any])
async def create_agent_update(
    request: AgentUpdateRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Create a new agent update"""
    try:
        result = await agent_service.create_agent_update(request.dict())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent update: {str(e)}"
        )


@router.get("/installers/{platform}/{architecture}")
async def get_agent_installer(
    platform: str,
    architecture: str,
    token: str = Depends(auth_service.verify_token)
):
    """Get agent installer script for platform"""
    try:
        if platform not in [p.value for p in AgentPlatform]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {platform}"
            )
        
        installer_script = agent_service.generate_agent_installer(platform, architecture)
        
        return {
            "platform": platform,
            "architecture": architecture,
            "installer_script": installer_script,
            "download_url": f"https://github.com/malsiftcyber/MalsiftCND/releases/latest/download/malsift-agent-{platform}-{architecture}",
            "instructions": f"Download and run the installer script to install the MalsiftCND Discovery Agent on {platform} {architecture}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate installer: {str(e)}"
        )


@router.get("/platforms")
async def get_supported_platforms(
    token: str = Depends(auth_service.verify_token)
):
    """Get supported platforms and architectures"""
    return {
        "platforms": [
            {
                "platform": "windows",
                "name": "Windows",
                "architectures": ["x86", "x64"],
                "installer_types": ["exe", "msi"],
                "service_type": "Windows Service"
            },
            {
                "platform": "linux",
                "name": "Linux",
                "architectures": ["x86", "x64", "arm64"],
                "installer_types": ["sh", "deb", "rpm"],
                "service_type": "systemd"
            },
            {
                "platform": "macos",
                "name": "macOS",
                "architectures": ["x64", "arm64"],
                "installer_types": ["sh", "pkg"],
                "service_type": "launchd"
            }
        ]
    }


@router.get("/releases")
async def get_agent_releases(
    token: str = Depends(auth_service.verify_token)
):
    """Get available agent releases"""
    try:
        from app.core.database import SessionLocal
        from app.models.discovery_agent import AgentUpdate
        
        db = SessionLocal()
        try:
            updates = db.query(AgentUpdate).filter(
                AgentUpdate.is_active == True
            ).order_by(AgentUpdate.released_at.desc()).all()
            
            releases = []
            for update in updates:
                releases.append({
                    "version": update.version,
                    "platform": update.platform,
                    "architecture": update.architecture,
                    "release_notes": update.release_notes,
                    "download_url": update.download_url,
                    "checksum": update.checksum,
                    "file_size": update.file_size,
                    "is_required": update.is_required,
                    "released_at": update.released_at.isoformat() if update.released_at else None
                })
            
            return {
                "releases": releases,
                "total_count": len(releases)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent releases: {str(e)}"
        )


@router.get("/agents/{agent_id}/scans", response_model=List[Dict[str, Any]])
async def get_agent_scans(
    agent_id: str,
    limit: int = Query(default=50, description="Number of scans to return", ge=1, le=100),
    offset: int = Query(default=0, description="Number of scans to skip", ge=0),
    token: str = Depends(auth_service.verify_token)
):
    """Get scans performed by an agent"""
    try:
        from app.core.database import SessionLocal
        from app.models.discovery_agent import DiscoveryAgent, AgentScan
        
        db = SessionLocal()
        try:
            agent = db.query(DiscoveryAgent).filter(DiscoveryAgent.agent_id == agent_id).first()
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agent not found"
                )
            
            scans = db.query(AgentScan).filter(
                AgentScan.agent_id == agent.id
            ).order_by(AgentScan.created_at.desc()).offset(offset).limit(limit).all()
            
            return [
                {
                    "id": str(scan.id),
                    "scan_type": scan.scan_type,
                    "targets": scan.targets,
                    "ports": scan.ports,
                    "scanner": scan.scanner,
                    "status": scan.status,
                    "progress": scan.progress,
                    "started_at": scan.started_at.isoformat() if scan.started_at else None,
                    "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
                    "duration_seconds": scan.duration_seconds,
                    "devices_found": scan.devices_found,
                    "ports_found": scan.ports_found,
                    "services_found": scan.services_found,
                    "error_message": scan.error_message,
                    "created_at": scan.created_at.isoformat()
                }
                for scan in scans
            ]
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent scans: {str(e)}"
        )


@router.get("/agents/{agent_id}/heartbeats", response_model=List[Dict[str, Any]])
async def get_agent_heartbeats(
    agent_id: str,
    limit: int = Query(default=100, description="Number of heartbeats to return", ge=1, le=500),
    offset: int = Query(default=0, description="Number of heartbeats to skip", ge=0),
    token: str = Depends(auth_service.verify_token)
):
    """Get heartbeats from an agent"""
    try:
        from app.core.database import SessionLocal
        from app.models.discovery_agent import DiscoveryAgent, AgentHeartbeat
        
        db = SessionLocal()
        try:
            agent = db.query(DiscoveryAgent).filter(DiscoveryAgent.agent_id == agent_id).first()
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agent not found"
                )
            
            heartbeats = db.query(AgentHeartbeat).filter(
                AgentHeartbeat.agent_id == agent.id
            ).order_by(AgentHeartbeat.received_at.desc()).offset(offset).limit(limit).all()
            
            return [
                {
                    "id": str(hb.id),
                    "status": hb.status,
                    "cpu_usage": hb.cpu_usage,
                    "memory_usage": hb.memory_usage,
                    "disk_usage": hb.disk_usage,
                    "network_usage": hb.network_usage,
                    "agent_version": hb.agent_version,
                    "os_version": hb.os_version,
                    "uptime_seconds": hb.uptime_seconds,
                    "active_scans": hb.active_scans,
                    "queued_scans": hb.queued_scans,
                    "last_scan_duration": hb.last_scan_duration,
                    "error_count": hb.error_count,
                    "last_error": hb.last_error,
                    "received_at": hb.received_at.isoformat()
                }
                for hb in heartbeats
            ]
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent heartbeats: {str(e)}"
        )


@router.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Delete an agent (soft delete)"""
    try:
        from app.core.database import SessionLocal
        from app.models.discovery_agent import DiscoveryAgent
        
        db = SessionLocal()
        try:
            agent = db.query(DiscoveryAgent).filter(DiscoveryAgent.agent_id == agent_id).first()
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agent not found"
                )
            
            agent.is_active = False
            agent.status = AgentStatus.INACTIVE
            agent.updated_at = datetime.utcnow()
            
            db.commit()
            
            return {"message": f"Agent '{agent.name}' deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}"
        )
