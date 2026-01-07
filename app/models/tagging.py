"""
Database models for company and site tagging
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Company(Base):
    """Company model for multi-tenant data segregation"""
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True)  # Short company code
    description = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    sites = relationship("Site", back_populates="company", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="company")
    scans = relationship("Scan", back_populates="company")
    users = relationship("User", back_populates="company")
    edr_integrations = relationship("EDRIntegration", back_populates="company")
    edr_endpoints = relationship("EDREndpoint", back_populates="company")
    discovery_agents = relationship("DiscoveryAgent", back_populates="company")


class Site(Base):
    """Site model for location-based data segregation"""
    __tablename__ = "sites"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)  # Short site code
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    timezone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="sites")
    devices = relationship("Device", back_populates="site")
    scans = relationship("Scan", back_populates="site")
    edr_integrations = relationship("EDRIntegration", back_populates="site")
    edr_endpoints = relationship("EDREndpoint", back_populates="site")
    discovery_agents = relationship("DiscoveryAgent", back_populates="site")


class DeviceTag(Base):
    """Device tagging model for custom tags"""
    __tablename__ = "device_tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    tag_type = Column(String(50), nullable=False)  # 'company', 'site', 'custom', 'department', etc.
    tag_key = Column(String(100), nullable=False)  # 'company_name', 'site_code', 'department', etc.
    tag_value = Column(String(255), nullable=False)  # Actual tag value
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    device = relationship("Device", back_populates="device_tags")
    creator = relationship("User", foreign_keys=[created_by])


class ScanTag(Base):
    """Scan tagging model for scan-level tags"""
    __tablename__ = "scan_tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    tag_type = Column(String(50), nullable=False)
    tag_key = Column(String(100), nullable=False)
    tag_value = Column(String(255), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scan = relationship("Scan", back_populates="scan_tags")
    creator = relationship("User", foreign_keys=[created_by])
