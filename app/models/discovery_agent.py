"""
Database models for discovery agent management
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, Float, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum

from app.core.database import Base


class AgentStatus(str, Enum):
    """Agent status types"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    OFFLINE = "offline"
    ERROR = "error"
    UPDATING = "updating"


class AgentPlatform(str, Enum):
    """Supported agent platforms"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"


class DiscoveryAgent(Base):
    """Discovery agent model"""
    __tablename__ = "discovery_agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Agent Identification
    agent_id = Column(String(255), unique=True, nullable=False, index=True)  # Unique agent identifier
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Platform Information
    platform = Column(String(20), nullable=False)  # AgentPlatform enum
    architecture = Column(String(20), nullable=False)  # x86, x64, arm64
    os_version = Column(String(100), nullable=True)
    agent_version = Column(String(50), nullable=False)
    
    # Network Information
    ip_address = Column(String(45), nullable=True, index=True)
    hostname = Column(String(255), nullable=True, index=True)
    network_interface = Column(String(100), nullable=True)
    
    # Agent Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(String(20), default=AgentStatus.OFFLINE, nullable=False)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    heartbeat_interval = Column(Integer, default=60, nullable=False)  # seconds
    
    # Communication Configuration
    server_url = Column(String(500), nullable=False)
    ssl_enabled = Column(Boolean, default=True, nullable=False)
    ssl_cert_path = Column(String(500), nullable=True)
    api_key = Column(String(500), nullable=True)  # Encrypted
    
    # Scanning Configuration
    scan_enabled = Column(Boolean, default=True, nullable=False)
    scan_interval_minutes = Column(Integer, default=60, nullable=False)
    max_concurrent_scans = Column(Integer, default=5, nullable=False)
    scan_timeout_seconds = Column(Integer, default=300, nullable=False)
    
    # Target Configuration
    target_networks = Column(JSONB, nullable=True)  # List of networks to scan
    excluded_networks = Column(JSONB, nullable=True)  # List of networks to exclude
    target_ports = Column(JSONB, nullable=True)  # List of ports to scan
    excluded_ports = Column(JSONB, nullable=True)  # List of ports to exclude
    
    # Company/Site Association
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=True)
    
    # Performance Metrics
    total_scans = Column(Integer, default=0, nullable=False)
    successful_scans = Column(Integer, default=0, nullable=False)
    failed_scans = Column(Integer, default=0, nullable=False)
    devices_discovered = Column(Integer, default=0, nullable=False)
    last_scan_duration = Column(Float, nullable=True)  # seconds
    average_scan_duration = Column(Float, nullable=True)  # seconds
    
    # Error Information
    last_error = Column(Text, nullable=True)
    error_count = Column(Integer, default=0, nullable=False)
    last_error_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_scan = Column(DateTime(timezone=True), nullable=True)
    last_update_check = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="discovery_agents")
    site = relationship("Site", back_populates="discovery_agents")
    scans = relationship("AgentScan", back_populates="agent")
    heartbeats = relationship("AgentHeartbeat", back_populates="agent")


class AgentScan(Base):
    """Agent scan execution model"""
    __tablename__ = "agent_scans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("discovery_agents.id"), nullable=False)
    
    # Scan Configuration
    scan_type = Column(String(50), nullable=False)  # ping_sweep, port_scan, service_scan, etc.
    targets = Column(JSONB, nullable=False)  # List of targets
    ports = Column(JSONB, nullable=True)  # List of ports
    scanner = Column(String(20), nullable=False)  # nmap, masscan, etc.
    
    # Scan Execution
    status = Column(String(20), default="queued", nullable=False)  # queued, running, completed, failed, cancelled
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Results
    devices_found = Column(Integer, default=0, nullable=False)
    ports_found = Column(Integer, default=0, nullable=False)
    services_found = Column(Integer, default=0, nullable=False)
    scan_results = Column(JSONB, nullable=True)  # Raw scan results
    
    # Error Information
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    agent = relationship("DiscoveryAgent", back_populates="scans")


class AgentHeartbeat(Base):
    """Agent heartbeat model"""
    __tablename__ = "agent_heartbeats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("discovery_agents.id"), nullable=False)
    
    # Heartbeat Data
    status = Column(String(20), nullable=False)  # AgentStatus enum
    cpu_usage = Column(Float, nullable=True)  # percentage
    memory_usage = Column(Float, nullable=True)  # percentage
    disk_usage = Column(Float, nullable=True)  # percentage
    network_usage = Column(Float, nullable=True)  # bytes per second
    
    # Agent Information
    agent_version = Column(String(50), nullable=True)
    os_version = Column(String(100), nullable=True)
    uptime_seconds = Column(Integer, nullable=True)
    
    # Performance Metrics
    active_scans = Column(Integer, default=0, nullable=False)
    queued_scans = Column(Integer, default=0, nullable=False)
    last_scan_duration = Column(Float, nullable=True)
    
    # Error Information
    error_count = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    
    # Heartbeat Data
    heartbeat_data = Column(JSONB, nullable=True)  # Additional heartbeat data
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    agent = relationship("DiscoveryAgent", back_populates="heartbeats")


class AgentUpdate(Base):
    """Agent update management model"""
    __tablename__ = "agent_updates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Update Information
    version = Column(String(50), nullable=False)
    platform = Column(String(20), nullable=False)  # AgentPlatform enum
    architecture = Column(String(20), nullable=False)
    
    # Update Details
    release_notes = Column(Text, nullable=True)
    download_url = Column(String(500), nullable=False)
    checksum = Column(String(128), nullable=False)  # SHA-256 checksum
    file_size = Column(Integer, nullable=False)  # bytes
    
    # Update Configuration
    is_required = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    min_agent_version = Column(String(50), nullable=True)  # Minimum version required
    
    # Deployment
    rollout_percentage = Column(Integer, default=100, nullable=False)  # 0-100
    rollout_groups = Column(JSONB, nullable=True)  # List of rollout groups
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    released_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    deployments = relationship("AgentDeployment", back_populates="update")


class AgentDeployment(Base):
    """Agent deployment tracking model"""
    __tablename__ = "agent_deployments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("discovery_agents.id"), nullable=False)
    update_id = Column(UUID(as_uuid=True), ForeignKey("agent_updates.id"), nullable=False)
    
    # Deployment Status
    status = Column(String(20), default="pending", nullable=False)  # pending, downloading, installing, completed, failed
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    
    # Deployment Details
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Error Information
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    agent = relationship("DiscoveryAgent")
    update = relationship("AgentUpdate", back_populates="deployments")


class AgentConfiguration(Base):
    """Agent configuration template model"""
    __tablename__ = "agent_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration Data
    configuration = Column(JSONB, nullable=False)  # Agent configuration JSON
    
    # Platform Support
    supported_platforms = Column(JSONB, nullable=True)  # List of supported platforms
    
    # Company/Site Association
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=True)
    
    # Configuration Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company")
    site = relationship("Site")
