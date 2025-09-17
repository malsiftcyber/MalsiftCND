"""
Scan scheduling service for automated discovery scans
"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from app.core.database import SessionLocal
from app.models.scan import Scan
from app.services.scan_service import ScanService


class ScheduleType(str, Enum):
    """Types of scan schedules"""
    DISCOVERY = "discovery"
    MONITORING = "monitoring"
    COMPLIANCE = "compliance"


class ScheduleFrequency(str, Enum):
    """Schedule frequency options"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class ScanSchedule:
    """Scan schedule configuration"""
    
    def __init__(self, 
                 schedule_id: str,
                 name: str,
                 schedule_type: ScheduleType,
                 frequency: ScheduleFrequency,
                 target_networks: List[str],
                 enabled: bool = True,
                 custom_interval_hours: Optional[int] = None,
                 start_time: Optional[str] = None,
                 days_of_week: Optional[List[int]] = None,
                 scanner_config: Optional[Dict] = None):
        self.schedule_id = schedule_id
        self.name = name
        self.schedule_type = schedule_type
        self.frequency = frequency
        self.target_networks = target_networks
        self.enabled = enabled
        self.custom_interval_hours = custom_interval_hours
        self.start_time = start_time  # Format: "HH:MM"
        self.days_of_week = days_of_week  # 0=Monday, 6=Sunday
        self.scanner_config = scanner_config or {}
        self.last_run = None
        self.next_run = None
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0


class SchedulingService:
    """Service for managing automated scan schedules"""
    
    def __init__(self):
        self.logger = logging.getLogger("services.scheduling_service")
        self.scan_service = ScanService()
        self.schedules: Dict[str, ScanSchedule] = {}
        self.running = False
        self.scheduler_task = None
        
        # Load default schedules
        self._load_default_schedules()
    
    def _load_default_schedules(self):
        """Load default scan schedules"""
        # Default discovery schedule - every 6 hours
        discovery_schedule = ScanSchedule(
            schedule_id="default_discovery",
            name="Default Discovery Scan",
            schedule_type=ScheduleType.DISCOVERY,
            frequency=ScheduleFrequency.CUSTOM,
            target_networks=["192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"],
            custom_interval_hours=6,
            start_time="00:00",
            scanner_config={
                "scanner": "nmap",
                "scan_type": "discovery",
                "ports": "1-1000",
                "timing": "T4",
                "max_hosts": 1000
            }
        )
        
        # Default monitoring schedule - daily
        monitoring_schedule = ScanSchedule(
            schedule_id="default_monitoring",
            name="Default Monitoring Scan",
            schedule_type=ScheduleType.MONITORING,
            frequency=ScheduleFrequency.DAILY,
            target_networks=["192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"],
            start_time="02:00",
            scanner_config={
                "scanner": "nmap",
                "scan_type": "monitoring",
                "ports": "1-1000",
                "timing": "T3",
                "max_hosts": 1000
            }
        )
        
        self.schedules[discovery_schedule.schedule_id] = discovery_schedule
        self.schedules[monitoring_schedule.schedule_id] = monitoring_schedule
        
        # Calculate next run times
        self._calculate_next_runs()
    
    def _calculate_next_runs(self):
        """Calculate next run times for all schedules"""
        now = datetime.now()
        
        for schedule in self.schedules.values():
            if not schedule.enabled:
                continue
                
            if schedule.frequency == ScheduleFrequency.HOURLY:
                schedule.next_run = now + timedelta(hours=1)
            elif schedule.frequency == ScheduleFrequency.DAILY:
                # Schedule for next day at start_time
                next_run = now + timedelta(days=1)
                if schedule.start_time:
                    hour, minute = map(int, schedule.start_time.split(':'))
                    next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
                schedule.next_run = next_run
            elif schedule.frequency == ScheduleFrequency.WEEKLY:
                # Schedule for next occurrence of specified day
                if schedule.days_of_week:
                    days_ahead = (schedule.days_of_week[0] - now.weekday()) % 7
                    if days_ahead == 0:  # Today
                        days_ahead = 7
                    next_run = now + timedelta(days=days_ahead)
                    if schedule.start_time:
                        hour, minute = map(int, schedule.start_time.split(':'))
                        next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    schedule.next_run = next_run
            elif schedule.frequency == ScheduleFrequency.CUSTOM:
                if schedule.custom_interval_hours:
                    schedule.next_run = now + timedelta(hours=schedule.custom_interval_hours)
    
    async def start_scheduler(self):
        """Start the scan scheduler"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        self.logger.info("Scan scheduler started")
    
    async def stop_scheduler(self):
        """Stop the scan scheduler"""
        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Scan scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                await self._check_and_run_schedules()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def _check_and_run_schedules(self):
        """Check if any schedules need to run"""
        now = datetime.now()
        
        for schedule in self.schedules.values():
            if not schedule.enabled or not schedule.next_run:
                continue
            
            if now >= schedule.next_run:
                await self._run_schedule(schedule)
    
    async def _run_schedule(self, schedule: ScanSchedule):
        """Run a scheduled scan"""
        try:
            self.logger.info(f"Running scheduled scan: {schedule.name}")
            
            # Create scan request
            scan_request = {
                "scan_type": schedule.scanner_config.get("scan_type", "discovery"),
                "scanner": schedule.scanner_config.get("scanner", "nmap"),
                "target_networks": schedule.target_networks,
                "ports": schedule.scanner_config.get("ports", "1-1000"),
                "timing": schedule.scanner_config.get("timing", "T3"),
                "max_hosts": schedule.scanner_config.get("max_hosts", 1000),
                "scheduled": True,
                "schedule_id": schedule.schedule_id
            }
            
            # Start the scan
            scan_id = await self.scan_service.start_scan(scan_request)
            
            # Update schedule statistics
            schedule.last_run = now
            schedule.total_runs += 1
            
            # Calculate next run time
            self._calculate_next_run_for_schedule(schedule)
            
            self.logger.info(f"Scheduled scan {schedule.name} started with ID: {scan_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to run scheduled scan {schedule.name}: {e}")
            schedule.failed_runs += 1
    
    def _calculate_next_run_for_schedule(self, schedule: ScanSchedule):
        """Calculate next run time for a specific schedule"""
        now = datetime.now()
        
        if schedule.frequency == ScheduleFrequency.HOURLY:
            schedule.next_run = now + timedelta(hours=1)
        elif schedule.frequency == ScheduleFrequency.DAILY:
            next_run = now + timedelta(days=1)
            if schedule.start_time:
                hour, minute = map(int, schedule.start_time.split(':'))
                next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            schedule.next_run = next_run
        elif schedule.frequency == ScheduleFrequency.WEEKLY:
            if schedule.days_of_week:
                days_ahead = (schedule.days_of_week[0] - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                next_run = now + timedelta(days=days_ahead)
                if schedule.start_time:
                    hour, minute = map(int, schedule.start_time.split(':'))
                    next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
                schedule.next_run = next_run
        elif schedule.frequency == ScheduleFrequency.CUSTOM:
            if schedule.custom_interval_hours:
                schedule.next_run = now + timedelta(hours=schedule.custom_interval_hours)
    
    def create_schedule(self, schedule: ScanSchedule) -> str:
        """Create a new scan schedule"""
        self.schedules[schedule.schedule_id] = schedule
        self._calculate_next_run_for_schedule(schedule)
        self.logger.info(f"Created schedule: {schedule.name}")
        return schedule.schedule_id
    
    def update_schedule(self, schedule_id: str, **kwargs) -> bool:
        """Update an existing schedule"""
        if schedule_id not in self.schedules:
            return False
        
        schedule = self.schedules[schedule_id]
        
        for key, value in kwargs.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)
        
        self._calculate_next_run_for_schedule(schedule)
        self.logger.info(f"Updated schedule: {schedule.name}")
        return True
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule"""
        if schedule_id in self.schedules:
            schedule_name = self.schedules[schedule_id].name
            del self.schedules[schedule_id]
            self.logger.info(f"Deleted schedule: {schedule_name}")
            return True
        return False
    
    def get_schedule(self, schedule_id: str) -> Optional[ScanSchedule]:
        """Get a specific schedule"""
        return self.schedules.get(schedule_id)
    
    def list_schedules(self) -> List[ScanSchedule]:
        """List all schedules"""
        return list(self.schedules.values())
    
    def enable_schedule(self, schedule_id: str) -> bool:
        """Enable a schedule"""
        if schedule_id in self.schedules:
            self.schedules[schedule_id].enabled = True
            self._calculate_next_run_for_schedule(self.schedules[schedule_id])
            return True
        return False
    
    def disable_schedule(self, schedule_id: str) -> bool:
        """Disable a schedule"""
        if schedule_id in self.schedules:
            self.schedules[schedule_id].enabled = False
            self.schedules[schedule_id].next_run = None
            return True
        return False
    
    def get_schedule_stats(self) -> Dict:
        """Get scheduling statistics"""
        total_schedules = len(self.schedules)
        enabled_schedules = sum(1 for s in self.schedules.values() if s.enabled)
        total_runs = sum(s.total_runs for s in self.schedules.values())
        successful_runs = sum(s.successful_runs for s in self.schedules.values())
        failed_runs = sum(s.failed_runs for s in self.schedules.values())
        
        return {
            "total_schedules": total_schedules,
            "enabled_schedules": enabled_schedules,
            "disabled_schedules": total_schedules - enabled_schedules,
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "success_rate": successful_runs / total_runs if total_runs > 0 else 0,
            "scheduler_running": self.running
        }
