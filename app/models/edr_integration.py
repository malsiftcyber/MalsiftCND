"""
Database models for EDR (Endpoint Detection and Response) integrations
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, Float, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum

from app.core.database import Base


class EDRProvider(str, Enum):
    """EDR provider types"""
    CROWDSTRIKE = "crowdstrike"
    MICROSOFT_DEFENDER = "microsoft_defender"
    SENTINELONE = "sentinelone"
    TRENDMICRO = "trendmicro"


class EDRIntegration(Base):
    """EDR integration configuration"""
    __tablename__ = "edr_integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    provider = Column(String(50), nullable=False)  # EDRProvider enum
    is_active = Column(Boolean, default=True, nullable=False)
    
    # API Configuration
    api_base_url = Column(String(500), nullable=False)
    api_key = Column(String(500), nullable=True)  # Encrypted
    client_id = Column(String(255), nullable=True)  # For OAuth
    client_secret = Column(String(500), nullable=True)  # Encrypted
    tenant_id = Column(String(255), nullable=True)  # For Microsoft Defender
    
    # Authentication Configuration
    auth_type = Column(String(50), default="api_key", nullable=False)  # api_key, oauth, bearer
    auth_token = Column(String(1000), nullable=True)  # Encrypted
    
    # Sync Configuration
    sync_enabled = Column(Boolean, default=True, nullable=False)
    sync_interval_minutes = Column(Integer, default=60, nullable=False)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    next_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Data Configuration
    sync_endpoints = Column(Boolean, default=True, nullable=False)
    sync_alerts = Column(Boolean, default=False, nullable=False)
    sync_vulnerabilities = Column(Boolean, default=False, nullable=False)
    sync_network_connections = Column(Boolean, default=False, nullable=False)
    
    # Filtering Configuration
    include_tags = Column(JSONB, nullable=True)  # Tags to include
    exclude_tags = Column(JSONB, nullable=True)  # Tags to exclude
    include_hostnames = Column(JSONB, nullable=True)  # Hostname patterns to include
    exclude_hostnames = Column(JSONB, nullable=True)  # Hostname patterns to exclude
    
    # Company/Site Association
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="edr_integrations")
    site = relationship("Site", back_populates="edr_integrations")
    creator = relationship("User", foreign_keys=[created_by])
    endpoints = relationship("EDREndpoint", back_populates="integration")


class EDREndpoint(Base):
    """EDR endpoint data"""
    __tablename__ = "edr_endpoints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("edr_integrations.id"), nullable=False)
    
    # EDR-specific identifiers
    edr_endpoint_id = Column(String(255), nullable=False, index=True)  # EDR's internal ID
    edr_hostname = Column(String(255), nullable=True, index=True)
    edr_ip_addresses = Column(JSONB, nullable=True)  # Array of IP addresses
    
    # Device Information
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True)
    
    # Endpoint Details
    hostname = Column(String(255), nullable=True, index=True)
    operating_system = Column(String(100), nullable=True)
    os_version = Column(String(100), nullable=True)
    architecture = Column(String(50), nullable=True)
    processor = Column(String(100), nullable=True)
    memory_gb = Column(Float, nullable=True)
    disk_space_gb = Column(Float, nullable=True)
    
    # Network Information
    mac_addresses = Column(JSONB, nullable=True)  # Array of MAC addresses
    network_interfaces = Column(JSONB, nullable=True)  # Network interface details
    
    # Agent Information
    agent_version = Column(String(50), nullable=True)
    agent_status = Column(String(50), nullable=True)  # online, offline, error
    last_seen_by_agent = Column(DateTime(timezone=True), nullable=True)
    
    # Security Information
    risk_score = Column(Float, nullable=True)  # EDR's risk score
    threat_level = Column(String(50), nullable=True)  # low, medium, high, critical
    compliance_status = Column(String(50), nullable=True)
    
    # EDR-specific Data
    edr_raw_data = Column(JSONB, nullable=True)  # Raw data from EDR
    edr_tags = Column(JSONB, nullable=True)  # EDR-specific tags
    edr_groups = Column(JSONB, nullable=True)  # EDR groups/policies
    
    # Company/Site Association
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=True)
    
    # Timestamps
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    integration = relationship("EDRIntegration", back_populates="endpoints")
    device = relationship("Device", back_populates="edr_endpoints")
    company = relationship("Company", back_populates="edr_endpoints")
    site = relationship("Site", back_populates="edr_endpoints")


class EDRAlert(Base):
    """EDR security alerts"""
    __tablename__ = "edr_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("edr_integrations.id"), nullable=False)
    endpoint_id = Column(UUID(as_uuid=True), ForeignKey("edr_endpoints.id"), nullable=True)
    
    # EDR-specific identifiers
    edr_alert_id = Column(String(255), nullable=False, index=True)
    edr_incident_id = Column(String(255), nullable=True, index=True)
    
    # Alert Details
    alert_type = Column(String(100), nullable=True)
    severity = Column(String(50), nullable=True)  # low, medium, high, critical
    status = Column(String(50), nullable=True)  # open, investigating, resolved, false_positive
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    # Threat Information
    threat_name = Column(String(255), nullable=True)
    threat_type = Column(String(100), nullable=True)
    threat_category = Column(String(100), nullable=True)
    ioc_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # EDR-specific Data
    edr_raw_data = Column(JSONB, nullable=True)
    
    # Relationships
    integration = relationship("EDRIntegration")
    endpoint = relationship("EDREndpoint")


class EDRSyncLog(Base):
    """EDR sync operation logs"""
    __tablename__ = "edr_sync_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("edr_integrations.id"), nullable=False)
    
    # Sync Details
    sync_type = Column(String(50), nullable=False)  # endpoints, alerts, vulnerabilities
    status = Column(String(50), nullable=False)  # success, failed, partial
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Results
    records_processed = Column(Integer, default=0, nullable=False)
    records_created = Column(Integer, default=0, nullable=False)
    records_updated = Column(Integer, default=0, nullable=False)
    records_failed = Column(Integer, default=0, nullable=False)
    
    # Error Information
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)
    
    # Relationships
    integration = relationship("EDRIntegration")
