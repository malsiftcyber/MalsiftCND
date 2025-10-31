"""
Device database model
"""
from sqlalchemy import Column, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Device(Base):
    """Device model"""
    __tablename__ = "devices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic device information
    ip = Column(String(45), unique=True, nullable=False, index=True)
    hostname = Column(String(255), nullable=True, index=True)
    device_type = Column(String(100), nullable=False, default="Unknown")
    operating_system = Column(String(100), nullable=False, default="Unknown")
    
    # Confidence and risk
    confidence = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    risk_score = Column(Float, default=0.0, nullable=False)  # 0.0 to 10.0
    
    # Discovery information
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    
    # Scan results aggregation
    scan_results = Column(JSONB, nullable=True)  # Aggregated scan data
    
    # External data sources
    runzero_data = Column(JSONB, nullable=True)
    tanium_data = Column(JSONB, nullable=True)
    armis_data = Column(JSONB, nullable=True)
    ad_data = Column(JSONB, nullable=True)
    
    # AI analysis
    ai_analysis = Column(JSONB, nullable=True)
    
    # User annotations
    tags = Column(ARRAY(String), default=[], nullable=False)
    notes = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Company and site associations
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    corrections = relationship("DeviceCorrection", back_populates="device")
    feedback = relationship("DeviceFeedback", back_populates="device")
    device_tags = relationship("DeviceTag", back_populates="device")
    company = relationship("Company", back_populates="devices")
    site = relationship("Site", back_populates="devices")
    edr_endpoints = relationship("EDREndpoint", back_populates="device")
    
    def __repr__(self):
        return f"<Device(ip='{self.ip}', type='{self.device_type}', os='{self.operating_system}')>"
