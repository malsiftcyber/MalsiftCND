"""
Device correction model for handling mis-identifications
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class DeviceCorrection(Base):
    """Device correction model for handling mis-identifications"""
    __tablename__ = "device_corrections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Original AI analysis
    original_device_type = Column(String(100), nullable=False)
    original_operating_system = Column(String(100), nullable=False)
    original_confidence = Column(Float, nullable=False)
    original_reasoning = Column(Text, nullable=True)
    
    # Corrected information
    corrected_device_type = Column(String(100), nullable=False)
    corrected_operating_system = Column(String(100), nullable=False)
    correction_reason = Column(Text, nullable=False)
    
    # Additional context
    scan_data_snapshot = Column(JSONB, nullable=True)  # Store scan data at time of correction
    correction_tags = Column(JSONB, nullable=True)  # Additional tags added during correction
    
    # Status
    is_applied = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Learning system
    learning_weight = Column(Float, default=1.0, nullable=False)  # Weight for ML learning
    feedback_score = Column(Float, nullable=True)  # User feedback on correction quality
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    device = relationship("Device", back_populates="corrections")
    user = relationship("User", foreign_keys=[user_id], back_populates="corrections_made")
    verifier = relationship("User", foreign_keys=[verified_by], back_populates="corrections_verified")
    
    def __repr__(self):
        return f"<DeviceCorrection(device_id='{self.device_id}', corrected_type='{self.corrected_device_type}')>"


class CorrectionPattern(Base):
    """Pattern learning for future device identification"""
    __tablename__ = "correction_patterns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Pattern identification
    pattern_type = Column(String(50), nullable=False)  # service_pattern, banner_pattern, port_pattern
    pattern_key = Column(String(255), nullable=False)  # The actual pattern (service name, banner, etc.)
    pattern_value = Column(String(255), nullable=False)  # The pattern value
    
    # Corrected information
    correct_device_type = Column(String(100), nullable=False)
    correct_operating_system = Column(String(100), nullable=False)
    
    # Pattern metadata
    confidence_score = Column(Float, default=0.0, nullable=False)
    usage_count = Column(Integer, default=1, nullable=False)
    success_rate = Column(Float, default=1.0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<CorrectionPattern(pattern='{self.pattern_key}', correct_type='{self.correct_device_type}')>"


class DeviceFeedback(Base):
    """User feedback on device identifications"""
    __tablename__ = "device_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Feedback type
    feedback_type = Column(String(50), nullable=False)  # accurate, inaccurate, partially_accurate
    accuracy_score = Column(Float, nullable=False)  # 0.0 to 1.0
    
    # Specific feedback
    device_type_accurate = Column(Boolean, nullable=True)
    os_accurate = Column(Boolean, nullable=True)
    services_accurate = Column(Boolean, nullable=True)
    
    # Comments
    feedback_comment = Column(Text, nullable=True)
    suggestions = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    device = relationship("Device", back_populates="feedback")
    user = relationship("User", back_populates="device_feedback")
    
    def __repr__(self):
        return f"<DeviceFeedback(device_id='{self.device_id}', type='{self.feedback_type}', score={self.accuracy_score})>"
