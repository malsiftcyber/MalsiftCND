"""
Admin service for system management
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import uuid

from app.core.config import settings


class AdminService:
    """Service for admin operations"""
    
    def __init__(self):
        self.logger = logging.getLogger("services.admin_service")
        self.system_config = {
            "scan_timeout": settings.DEFAULT_SCAN_TIMEOUT,
            "max_concurrent_scans": settings.MAX_CONCURRENT_SCANS,
            "scan_throttle_rate": settings.SCAN_THROTTLE_RATE,
            "ai_analysis_enabled": True,
            "auto_sync_enabled": False,
            "sync_interval": 3600  # 1 hour
        }
        
        self.scanner_configs = {
            "nmap": {
                "scanner_name": "nmap",
                "enabled": True,
                "timeout": 300,
                "rate_limit": None,
                "custom_args": ""
            },
            "masscan": {
                "scanner_name": "masscan",
                "enabled": True,
                "timeout": 300,
                "rate_limit": 1000,
                "custom_args": ""
            }
        }
        
        self.users = {}  # In-memory user storage (replace with database)
    
    async def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration"""
        return self.system_config.copy()
    
    async def update_system_config(self, config: Dict[str, Any]) -> bool:
        """Update system configuration"""
        try:
            # Validate configuration
            if "scan_timeout" in config and config["scan_timeout"] < 30:
                raise ValueError("Scan timeout must be at least 30 seconds")
            
            if "max_concurrent_scans" in config and config["max_concurrent_scans"] < 1:
                raise ValueError("Max concurrent scans must be at least 1")
            
            if "scan_throttle_rate" in config and config["scan_throttle_rate"] < 1:
                raise ValueError("Scan throttle rate must be at least 1")
            
            # Update configuration
            self.system_config.update(config)
            
            # Update settings
            settings.DEFAULT_SCAN_TIMEOUT = self.system_config["scan_timeout"]
            settings.MAX_CONCURRENT_SCANS = self.system_config["max_concurrent_scans"]
            settings.SCAN_THROTTLE_RATE = self.system_config["scan_throttle_rate"]
            
            self.logger.info("System configuration updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update system config: {e}")
            return False
    
    async def list_scanners(self) -> List[Dict[str, Any]]:
        """List scanner configurations"""
        return list(self.scanner_configs.values())
    
    async def update_scanner_config(self, scanner_name: str, config: Dict[str, Any]) -> bool:
        """Update scanner configuration"""
        if scanner_name not in self.scanner_configs:
            return False
        
        try:
            # Validate configuration
            if "timeout" in config and config["timeout"] < 30:
                raise ValueError("Scanner timeout must be at least 30 seconds")
            
            if "rate_limit" in config and config["rate_limit"] is not None and config["rate_limit"] < 1:
                raise ValueError("Rate limit must be at least 1")
            
            # Update configuration
            self.scanner_configs[scanner_name].update(config)
            
            self.logger.info(f"Scanner {scanner_name} configuration updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update scanner config: {e}")
            return False
    
    async def list_users(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List system users"""
        user_list = list(self.users.values())
        
        # Remove sensitive information
        for user in user_list:
            if "hashed_password" in user:
                del user["hashed_password"]
        
        return user_list[offset:offset + limit]
    
    async def create_user(self, username: str, email: str, password: str, is_admin: bool = False) -> str:
        """Create new user"""
        if username in self.users:
            raise ValueError("Username already exists")
        
        user_id = str(uuid.uuid4())
        
        # Hash password
        from app.auth.auth_service import AuthService
        auth_service = AuthService()
        hashed_password = auth_service.get_password_hash(password)
        
        user = {
            "id": user_id,
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_admin": is_admin,
            "created_at": datetime.now(),
            "last_login": None
        }
        
        self.users[username] = user
        
        self.logger.info(f"User {username} created")
        return user_id
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user"""
        # Find user by ID
        user = None
        for u in self.users.values():
            if u["id"] == user_id:
                user = u
                break
        
        if not user:
            return False
        
        try:
            # Update user fields
            for key, value in updates.items():
                if key in ["email", "is_active", "is_admin"]:
                    user[key] = value
            
            self.logger.info(f"User {user['username']} updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update user: {e}")
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        # Find user by ID
        user_to_delete = None
        username_to_delete = None
        
        for username, user in self.users.items():
            if user["id"] == user_id:
                user_to_delete = user
                username_to_delete = username
                break
        
        if not user_to_delete:
            return False
        
        try:
            del self.users[username_to_delete]
            self.logger.info(f"User {username_to_delete} deleted")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete user: {e}")
            return False
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            "system_info": {
                "version": settings.VERSION,
                "uptime": "N/A",  # Would calculate actual uptime
                "memory_usage": "N/A",  # Would get actual memory usage
                "cpu_usage": "N/A"  # Would get actual CPU usage
            },
            "scanning": {
                "active_scans": 0,  # Would get from scan service
                "total_scans_today": 0,
                "total_devices_discovered": 0
            },
            "integrations": {
                "total_integrations": 5,
                "active_integrations": 0,  # Would count enabled integrations
                "last_sync": None
            },
            "users": {
                "total_users": len(self.users),
                "active_users": len([u for u in self.users.values() if u["is_active"]]),
                "admin_users": len([u for u in self.users.values() if u["is_admin"]])
            }
        }
    
    async def get_system_logs(self, level: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get system logs"""
        # Placeholder for log retrieval
        # In production, this would read from actual log files or log aggregation system
        
        logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "System started",
                "module": "main",
                "user": None
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Database connection established",
                "module": "database",
                "user": None
            }
        ]
        
        # Filter by level if specified
        if level:
            logs = [log for log in logs if log["level"].lower() == level.lower()]
        
        return logs[offset:offset + limit]
