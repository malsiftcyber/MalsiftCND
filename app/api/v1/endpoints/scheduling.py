"""
Scan scheduling API endpoints
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

from app.auth.auth_service import AuthService
from app.services.scheduling_service import SchedulingService, ScanSchedule, ScheduleType, ScheduleFrequency

router = APIRouter()
auth_service = AuthService()
scheduling_service = SchedulingService()


class ScheduleCreateRequest(BaseModel):
    name: str
    schedule_type: ScheduleType
    frequency: ScheduleFrequency
    target_networks: List[str]
    enabled: bool = True
    custom_interval_hours: Optional[int] = None
    start_time: Optional[str] = None  # Format: "HH:MM"
    days_of_week: Optional[List[int]] = None  # 0=Monday, 6=Sunday
    scanner_config: Optional[Dict[str, Any]] = None


class ScheduleUpdateRequest(BaseModel):
    name: Optional[str] = None
    schedule_type: Optional[ScheduleType] = None
    frequency: Optional[ScheduleFrequency] = None
    target_networks: Optional[List[str]] = None
    enabled: Optional[bool] = None
    custom_interval_hours: Optional[int] = None
    start_time: Optional[str] = None
    days_of_week: Optional[List[int]] = None
    scanner_config: Optional[Dict[str, Any]] = None


class ScheduleResponse(BaseModel):
    schedule_id: str
    name: str
    schedule_type: str
    frequency: str
    target_networks: List[str]
    enabled: bool
    custom_interval_hours: Optional[int]
    start_time: Optional[str]
    days_of_week: Optional[List[int]]
    scanner_config: Dict[str, Any]
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    total_runs: int
    successful_runs: int
    failed_runs: int


@router.get("/schedules", response_model=List[ScheduleResponse])
async def list_schedules(
    token: str = Depends(auth_service.verify_token)
):
    """List all scan schedules"""
    try:
        schedules = scheduling_service.list_schedules()
        return [
            ScheduleResponse(
                schedule_id=schedule.schedule_id,
                name=schedule.name,
                schedule_type=schedule.schedule_type.value,
                frequency=schedule.frequency.value,
                target_networks=schedule.target_networks,
                enabled=schedule.enabled,
                custom_interval_hours=schedule.custom_interval_hours,
                start_time=schedule.start_time,
                days_of_week=schedule.days_of_week,
                scanner_config=schedule.scanner_config,
                last_run=schedule.last_run,
                next_run=schedule.next_run,
                total_runs=schedule.total_runs,
                successful_runs=schedule.successful_runs,
                failed_runs=schedule.failed_runs
            )
            for schedule in schedules
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list schedules: {str(e)}"
        )


@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Get a specific schedule"""
    try:
        schedule = scheduling_service.get_schedule(schedule_id)
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )
        
        return ScheduleResponse(
            schedule_id=schedule.schedule_id,
            name=schedule.name,
            schedule_type=schedule.schedule_type.value,
            frequency=schedule.frequency.value,
            target_networks=schedule.target_networks,
            enabled=schedule.enabled,
            custom_interval_hours=schedule.custom_interval_hours,
            start_time=schedule.start_time,
            days_of_week=schedule.days_of_week,
            scanner_config=schedule.scanner_config,
            last_run=schedule.last_run,
            next_run=schedule.next_run,
            total_runs=schedule.total_runs,
            successful_runs=schedule.successful_runs,
            failed_runs=schedule.failed_runs
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schedule: {str(e)}"
        )


@router.post("/schedules", response_model=Dict[str, str])
async def create_schedule(
    request: ScheduleCreateRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Create a new scan schedule"""
    try:
        # Generate schedule ID
        import uuid
        schedule_id = str(uuid.uuid4())
        
        # Create schedule object
        schedule = ScanSchedule(
            schedule_id=schedule_id,
            name=request.name,
            schedule_type=request.schedule_type,
            frequency=request.frequency,
            target_networks=request.target_networks,
            enabled=request.enabled,
            custom_interval_hours=request.custom_interval_hours,
            start_time=request.start_time,
            days_of_week=request.days_of_week,
            scanner_config=request.scanner_config or {}
        )
        
        # Create the schedule
        created_id = scheduling_service.create_schedule(schedule)
        
        return {
            "schedule_id": created_id,
            "message": f"Schedule '{request.name}' created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create schedule: {str(e)}"
        )


@router.put("/schedules/{schedule_id}")
async def update_schedule(
    schedule_id: str,
    request: ScheduleUpdateRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Update an existing schedule"""
    try:
        # Convert request to dict, excluding None values
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        success = scheduling_service.update_schedule(schedule_id, **update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )
        
        return {"message": f"Schedule '{schedule_id}' updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update schedule: {str(e)}"
        )


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Delete a schedule"""
    try:
        success = scheduling_service.delete_schedule(schedule_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )
        
        return {"message": f"Schedule '{schedule_id}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete schedule: {str(e)}"
        )


@router.post("/schedules/{schedule_id}/enable")
async def enable_schedule(
    schedule_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Enable a schedule"""
    try:
        success = scheduling_service.enable_schedule(schedule_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )
        
        return {"message": f"Schedule '{schedule_id}' enabled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable schedule: {str(e)}"
        )


@router.post("/schedules/{schedule_id}/disable")
async def disable_schedule(
    schedule_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Disable a schedule"""
    try:
        success = scheduling_service.disable_schedule(schedule_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )
        
        return {"message": f"Schedule '{schedule_id}' disabled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable schedule: {str(e)}"
        )


@router.post("/schedules/{schedule_id}/run-now")
async def run_schedule_now(
    schedule_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Run a schedule immediately"""
    try:
        schedule = scheduling_service.get_schedule(schedule_id)
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )
        
        # Import the scheduler loop method to run the schedule
        from app.services.scheduling_service import SchedulingService
        temp_service = SchedulingService()
        await temp_service._run_schedule(schedule)
        
        return {"message": f"Schedule '{schedule_id}' started immediately"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run schedule: {str(e)}"
        )


@router.get("/schedules/stats")
async def get_schedule_stats(
    token: str = Depends(auth_service.verify_token)
):
    """Get scheduling statistics"""
    try:
        stats = scheduling_service.get_schedule_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schedule stats: {str(e)}"
        )


@router.post("/scheduler/start")
async def start_scheduler(
    token: str = Depends(auth_service.verify_token)
):
    """Start the scan scheduler"""
    try:
        await scheduling_service.start_scheduler()
        return {"message": "Scan scheduler started successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start scheduler: {str(e)}"
        )


@router.post("/scheduler/stop")
async def stop_scheduler(
    token: str = Depends(auth_service.verify_token)
):
    """Stop the scan scheduler"""
    try:
        await scheduling_service.stop_scheduler()
        return {"message": "Scan scheduler stopped successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop scheduler: {str(e)}"
        )


@router.get("/scheduler/status")
async def get_scheduler_status(
    token: str = Depends(auth_service.verify_token)
):
    """Get scheduler status"""
    try:
        stats = scheduling_service.get_schedule_stats()
        return {
            "running": stats["scheduler_running"],
            "total_schedules": stats["total_schedules"],
            "enabled_schedules": stats["enabled_schedules"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduler status: {str(e)}"
        )
