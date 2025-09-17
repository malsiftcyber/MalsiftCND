"""
Discovery agent service for managing cross-platform agents
"""
import asyncio
import logging
import ssl
import json
import hashlib
import secrets
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
import subprocess
import platform
import psutil
import os

from app.core.database import SessionLocal
from app.models.discovery_agent import (
    DiscoveryAgent, AgentScan, AgentHeartbeat, AgentUpdate, 
    AgentDeployment, AgentConfiguration, AgentStatus, AgentPlatform
)


class DiscoveryAgentService:
    """Service for managing discovery agents"""
    
    def __init__(self):
        self.logger = logging.getLogger("services.discovery_agent")
        self.ssl_context = self._create_ssl_context()
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for secure communication"""
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False  # For self-signed certificates
        context.verify_mode = ssl.CERT_NONE  # For development, should be CERT_REQUIRED in production
        return context
    
    async def register_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new discovery agent"""
        db = SessionLocal()
        try:
            # Generate unique agent ID
            agent_id = secrets.token_urlsafe(32)
            
            # Create agent record
            agent = DiscoveryAgent(
                agent_id=agent_id,
                name=agent_data.get('name', f"Agent-{agent_id[:8]}"),
                description=agent_data.get('description'),
                platform=agent_data.get('platform'),
                architecture=agent_data.get('architecture'),
                os_version=agent_data.get('os_version'),
                agent_version=agent_data.get('agent_version'),
                ip_address=agent_data.get('ip_address'),
                hostname=agent_data.get('hostname'),
                network_interface=agent_data.get('network_interface'),
                server_url=agent_data.get('server_url'),
                ssl_enabled=agent_data.get('ssl_enabled', True),
                api_key=agent_data.get('api_key'),
                company_id=agent_data.get('company_id'),
                site_id=agent_data.get('site_id'),
                target_networks=agent_data.get('target_networks'),
                excluded_networks=agent_data.get('excluded_networks'),
                target_ports=agent_data.get('target_ports'),
                excluded_ports=agent_data.get('excluded_ports')
            )
            
            db.add(agent)
            db.commit()
            db.refresh(agent)
            
            self.logger.info(f"Registered new agent: {agent.name} ({agent.agent_id})")
            
            return {
                "agent_id": agent.agent_id,
                "agent_uuid": str(agent.id),
                "status": "registered",
                "message": f"Agent '{agent.name}' registered successfully"
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to register agent: {e}")
            raise
        finally:
            db.close()
    
    async def update_agent_heartbeat(self, agent_id: str, heartbeat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update agent heartbeat"""
        db = SessionLocal()
        try:
            agent = db.query(DiscoveryAgent).filter(DiscoveryAgent.agent_id == agent_id).first()
            if not agent:
                raise ValueError("Agent not found")
            
            # Update agent status and last heartbeat
            agent.status = heartbeat_data.get('status', AgentStatus.ACTIVE)
            agent.last_heartbeat = datetime.utcnow()
            agent.updated_at = datetime.utcnow()
            
            # Create heartbeat record
            heartbeat = AgentHeartbeat(
                agent_id=agent.id,
                status=agent.status,
                cpu_usage=heartbeat_data.get('cpu_usage'),
                memory_usage=heartbeat_data.get('memory_usage'),
                disk_usage=heartbeat_data.get('disk_usage'),
                network_usage=heartbeat_data.get('network_usage'),
                agent_version=heartbeat_data.get('agent_version'),
                os_version=heartbeat_data.get('os_version'),
                uptime_seconds=heartbeat_data.get('uptime_seconds'),
                active_scans=heartbeat_data.get('active_scans', 0),
                queued_scans=heartbeat_data.get('queued_scans', 0),
                last_scan_duration=heartbeat_data.get('last_scan_duration'),
                error_count=heartbeat_data.get('error_count', 0),
                last_error=heartbeat_data.get('last_error'),
                heartbeat_data=heartbeat_data
            )
            
            db.add(heartbeat)
            db.commit()
            
            # Check for offline agents
            await self._check_offline_agents()
            
            return {
                "status": "success",
                "message": "Heartbeat updated successfully",
                "next_heartbeat": datetime.utcnow() + timedelta(seconds=agent.heartbeat_interval)
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to update heartbeat: {e}")
            raise
        finally:
            db.close()
    
    async def submit_scan_results(self, agent_id: str, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit scan results from agent"""
        db = SessionLocal()
        try:
            agent = db.query(DiscoveryAgent).filter(DiscoveryAgent.agent_id == agent_id).first()
            if not agent:
                raise ValueError("Agent not found")
            
            # Create scan record
            scan = AgentScan(
                agent_id=agent.id,
                scan_type=scan_data.get('scan_type'),
                targets=scan_data.get('targets'),
                ports=scan_data.get('ports'),
                scanner=scan_data.get('scanner'),
                status=scan_data.get('status', 'completed'),
                progress=100,
                started_at=scan_data.get('started_at'),
                completed_at=scan_data.get('completed_at'),
                duration_seconds=scan_data.get('duration_seconds'),
                devices_found=scan_data.get('devices_found', 0),
                ports_found=scan_data.get('ports_found', 0),
                services_found=scan_data.get('services_found', 0),
                scan_results=scan_data.get('scan_results'),
                error_message=scan_data.get('error_message'),
                error_details=scan_data.get('error_details')
            )
            
            db.add(scan)
            
            # Update agent metrics
            agent.total_scans += 1
            if scan.status == 'completed':
                agent.successful_scans += 1
                agent.devices_discovered += scan.devices_found
            else:
                agent.failed_scans += 1
                agent.error_count += 1
                agent.last_error = scan.error_message
                agent.last_error_at = datetime.utcnow()
            
            agent.last_scan = datetime.utcnow()
            agent.last_scan_duration = scan.duration_seconds
            
            # Update average scan duration
            if agent.average_scan_duration:
                agent.average_scan_duration = (agent.average_scan_duration + scan.duration_seconds) / 2
            else:
                agent.average_scan_duration = scan.duration_seconds
            
            db.commit()
            
            self.logger.info(f"Scan results submitted for agent {agent.name}: {scan.devices_found} devices found")
            
            return {
                "status": "success",
                "message": "Scan results submitted successfully",
                "scan_id": str(scan.id),
                "devices_found": scan.devices_found
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to submit scan results: {e}")
            raise
        finally:
            db.close()
    
    async def get_agent_configuration(self, agent_id: str) -> Dict[str, Any]:
        """Get agent configuration"""
        db = SessionLocal()
        try:
            agent = db.query(DiscoveryAgent).filter(DiscoveryAgent.agent_id == agent_id).first()
            if not agent:
                raise ValueError("Agent not found")
            
            # Get default configuration
            default_config = await self._get_default_configuration(agent.platform)
            
            # Merge with agent-specific configuration
            configuration = {
                "agent_id": agent.agent_id,
                "server_url": agent.server_url,
                "ssl_enabled": agent.ssl_enabled,
                "heartbeat_interval": agent.heartbeat_interval,
                "scan_enabled": agent.scan_enabled,
                "scan_interval_minutes": agent.scan_interval_minutes,
                "max_concurrent_scans": agent.max_concurrent_scans,
                "scan_timeout_seconds": agent.scan_timeout_seconds,
                "target_networks": agent.target_networks or default_config.get('target_networks', []),
                "excluded_networks": agent.excluded_networks or default_config.get('excluded_networks', []),
                "target_ports": agent.target_ports or default_config.get('target_ports', []),
                "excluded_ports": agent.excluded_ports or default_config.get('excluded_ports', []),
                "company_id": str(agent.company_id) if agent.company_id else None,
                "site_id": str(agent.site_id) if agent.site_id else None
            }
            
            return configuration
            
        except Exception as e:
            self.logger.error(f"Failed to get agent configuration: {e}")
            raise
        finally:
            db.close()
    
    async def _get_default_configuration(self, platform: str) -> Dict[str, Any]:
        """Get default configuration for platform"""
        db = SessionLocal()
        try:
            config = db.query(AgentConfiguration).filter(
                AgentConfiguration.is_default == True,
                AgentConfiguration.is_active == True
            ).first()
            
            if config:
                return config.configuration
            
            # Return platform-specific defaults
            defaults = {
                "target_networks": ["192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"],
                "excluded_networks": ["127.0.0.0/8", "169.254.0.0/16"],
                "target_ports": [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5900],
                "excluded_ports": [],
                "scan_timeout_seconds": 300,
                "max_concurrent_scans": 5
            }
            
            if platform == AgentPlatform.WINDOWS:
                defaults["target_ports"].extend([135, 139, 445, 1433, 3389])
            elif platform == AgentPlatform.LINUX:
                defaults["target_ports"].extend([21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995])
            elif platform == AgentPlatform.MACOS:
                defaults["target_ports"].extend([22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 548])
            
            return defaults
            
        finally:
            db.close()
    
    async def _check_offline_agents(self):
        """Check for agents that haven't sent heartbeat recently"""
        db = SessionLocal()
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)  # 5 minutes timeout
            
            offline_agents = db.query(DiscoveryAgent).filter(
                DiscoveryAgent.last_heartbeat < cutoff_time,
                DiscoveryAgent.status != AgentStatus.OFFLINE
            ).all()
            
            for agent in offline_agents:
                agent.status = AgentStatus.OFFLINE
                agent.updated_at = datetime.utcnow()
            
            if offline_agents:
                db.commit()
                self.logger.info(f"Marked {len(offline_agents)} agents as offline")
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to check offline agents: {e}")
        finally:
            db.close()
    
    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get agent status and metrics"""
        db = SessionLocal()
        try:
            agent = db.query(DiscoveryAgent).filter(DiscoveryAgent.agent_id == agent_id).first()
            if not agent:
                raise ValueError("Agent not found")
            
            # Get recent heartbeats
            recent_heartbeats = db.query(AgentHeartbeat).filter(
                AgentHeartbeat.agent_id == agent.id
            ).order_by(AgentHeartbeat.received_at.desc()).limit(10).all()
            
            # Get recent scans
            recent_scans = db.query(AgentScan).filter(
                AgentScan.agent_id == agent.id
            ).order_by(AgentScan.created_at.desc()).limit(10).all()
            
            return {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "status": agent.status,
                "platform": agent.platform,
                "architecture": agent.architecture,
                "agent_version": agent.agent_version,
                "last_heartbeat": agent.last_heartbeat.isoformat() if agent.last_heartbeat else None,
                "last_scan": agent.last_scan.isoformat() if agent.last_scan else None,
                "total_scans": agent.total_scans,
                "successful_scans": agent.successful_scans,
                "failed_scans": agent.failed_scans,
                "devices_discovered": agent.devices_discovered,
                "average_scan_duration": agent.average_scan_duration,
                "error_count": agent.error_count,
                "last_error": agent.last_error,
                "recent_heartbeats": [
                    {
                        "status": hb.status,
                        "cpu_usage": hb.cpu_usage,
                        "memory_usage": hb.memory_usage,
                        "received_at": hb.received_at.isoformat()
                    }
                    for hb in recent_heartbeats
                ],
                "recent_scans": [
                    {
                        "scan_type": scan.scan_type,
                        "targets": scan.targets,
                        "status": scan.status,
                        "devices_found": scan.devices_found,
                        "duration_seconds": scan.duration_seconds,
                        "created_at": scan.created_at.isoformat()
                    }
                    for scan in recent_scans
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get agent status: {e}")
            raise
        finally:
            db.close()
    
    async def list_agents(self, company_id: str = None, site_id: str = None, status: str = None) -> List[Dict[str, Any]]:
        """List all agents with optional filtering"""
        db = SessionLocal()
        try:
            query = db.query(DiscoveryAgent)
            
            if company_id:
                query = query.filter(DiscoveryAgent.company_id == company_id)
            
            if site_id:
                query = query.filter(DiscoveryAgent.site_id == site_id)
            
            if status:
                query = query.filter(DiscoveryAgent.status == status)
            
            agents = query.all()
            
            return [
                {
                    "id": str(agent.id),
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "description": agent.description,
                    "platform": agent.platform,
                    "architecture": agent.architecture,
                    "status": agent.status,
                    "agent_version": agent.agent_version,
                    "ip_address": agent.ip_address,
                    "hostname": agent.hostname,
                    "last_heartbeat": agent.last_heartbeat.isoformat() if agent.last_heartbeat else None,
                    "last_scan": agent.last_scan.isoformat() if agent.last_scan else None,
                    "total_scans": agent.total_scans,
                    "devices_discovered": agent.devices_discovered,
                    "company_id": str(agent.company_id) if agent.company_id else None,
                    "site_id": str(agent.site_id) if agent.site_id else None,
                    "created_at": agent.created_at.isoformat()
                }
                for agent in agents
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to list agents: {e}")
            raise
        finally:
            db.close()
    
    async def create_agent_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent update"""
        db = SessionLocal()
        try:
            update = AgentUpdate(
                version=update_data['version'],
                platform=update_data['platform'],
                architecture=update_data['architecture'],
                release_notes=update_data.get('release_notes'),
                download_url=update_data['download_url'],
                checksum=update_data['checksum'],
                file_size=update_data['file_size'],
                is_required=update_data.get('is_required', False),
                rollout_percentage=update_data.get('rollout_percentage', 100),
                rollout_groups=update_data.get('rollout_groups'),
                released_at=datetime.utcnow()
            )
            
            db.add(update)
            db.commit()
            db.refresh(update)
            
            self.logger.info(f"Created agent update: {update.version} for {update.platform}/{update.architecture}")
            
            return {
                "update_id": str(update.id),
                "version": update.version,
                "platform": update.platform,
                "architecture": update.architecture,
                "message": f"Update {update.version} created successfully"
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to create agent update: {e}")
            raise
        finally:
            db.close()
    
    async def check_for_updates(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Check for available updates for an agent"""
        db = SessionLocal()
        try:
            agent = db.query(DiscoveryAgent).filter(DiscoveryAgent.agent_id == agent_id).first()
            if not agent:
                raise ValueError("Agent not found")
            
            # Find available updates for this agent's platform and architecture
            update = db.query(AgentUpdate).filter(
                AgentUpdate.platform == agent.platform,
                AgentUpdate.architecture == agent.architecture,
                AgentUpdate.is_active == True,
                AgentUpdate.version > agent.agent_version
            ).order_by(AgentUpdate.version.desc()).first()
            
            if not update:
                return None
            
            # Check if agent is eligible for this update
            if update.rollout_percentage < 100:
                # Simple rollout logic based on agent ID hash
                agent_hash = int(hashlib.md5(agent.agent_id.encode()).hexdigest(), 16)
                if (agent_hash % 100) >= update.rollout_percentage:
                    return None
            
            return {
                "update_id": str(update.id),
                "version": update.version,
                "platform": update.platform,
                "architecture": update.architecture,
                "release_notes": update.release_notes,
                "download_url": update.download_url,
                "checksum": update.checksum,
                "file_size": update.file_size,
                "is_required": update.is_required,
                "released_at": update.released_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check for updates: {e}")
            raise
        finally:
            db.close()
    
    def generate_agent_installer(self, platform: str, architecture: str) -> str:
        """Generate agent installer script for platform"""
        if platform == AgentPlatform.WINDOWS:
            return self._generate_windows_installer(architecture)
        elif platform == AgentPlatform.LINUX:
            return self._generate_linux_installer(architecture)
        elif platform == AgentPlatform.MACOS:
            return self._generate_macos_installer(architecture)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def _generate_windows_installer(self, architecture: str) -> str:
        """Generate Windows installer script"""
        return f"""@echo off
echo Installing MalsiftCND Discovery Agent for Windows {architecture}...

REM Download agent binary
curl -L -o malsift-agent.exe "https://github.com/malsiftcyber/MalsiftCND/releases/latest/download/malsift-agent-windows-{architecture}.exe"

REM Verify checksum
echo Verifying checksum...
REM Add checksum verification here

REM Install as Windows service
sc create MalsiftAgent binPath= "%CD%\\malsift-agent.exe" start= auto
sc start MalsiftAgent

echo MalsiftCND Discovery Agent installed successfully!
echo The agent will start automatically on system boot.
pause
"""
    
    def _generate_linux_installer(self, architecture: str) -> str:
        """Generate Linux installer script"""
        return f"""#!/bin/bash
echo "Installing MalsiftCND Discovery Agent for Linux {architecture}..."

# Download agent binary
curl -L -o malsift-agent "https://github.com/malsiftcyber/MalsiftCND/releases/latest/download/malsift-agent-linux-{architecture}"

# Make executable
chmod +x malsift-agent

# Verify checksum
echo "Verifying checksum..."
# Add checksum verification here

# Create systemd service
sudo tee /etc/systemd/system/malsift-agent.service > /dev/null <<EOF
[Unit]
Description=MalsiftCND Discovery Agent
After=network.target

[Service]
Type=simple
User=malsift
Group=malsift
WorkingDirectory=/opt/malsift
ExecStart=/opt/malsift/malsift-agent
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create user and directory
sudo useradd -r -s /bin/false malsift
sudo mkdir -p /opt/malsift
sudo mv malsift-agent /opt/malsift/
sudo chown -R malsift:malsift /opt/malsift

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable malsift-agent
sudo systemctl start malsift-agent

echo "MalsiftCND Discovery Agent installed successfully!"
echo "The agent will start automatically on system boot."
"""
    
    def _generate_macos_installer(self, architecture: str) -> str:
        """Generate macOS installer script"""
        return f"""#!/bin/bash
echo "Installing MalsiftCND Discovery Agent for macOS {architecture}..."

# Download agent binary
curl -L -o malsift-agent "https://github.com/malsiftcyber/MalsiftCND/releases/latest/download/malsift-agent-macos-{architecture}"

# Make executable
chmod +x malsift-agent

# Verify checksum
echo "Verifying checksum..."
# Add checksum verification here

# Create launchd plist
sudo tee /Library/LaunchDaemons/com.malsift.agent.plist > /dev/null <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.malsift.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/malsift/malsift-agent</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/malsift-agent.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/malsift-agent.error.log</string>
</dict>
</plist>
EOF

# Create directory and move binary
sudo mkdir -p /opt/malsift
sudo mv malsift-agent /opt/malsift/
sudo chown root:wheel /opt/malsift/malsift-agent
sudo chmod 755 /opt/malsift/malsift-agent

# Load and start service
sudo launchctl load /Library/LaunchDaemons/com.malsift.agent.plist
sudo launchctl start com.malsift.agent

echo "MalsiftCND Discovery Agent installed successfully!"
echo "The agent will start automatically on system boot."
"""
