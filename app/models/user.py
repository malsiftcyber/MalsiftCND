"""
User database model
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # MFA fields
    mfa_secret = Column(String(32), nullable=True)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    backup_codes = Column(Text, nullable=True)  # JSON array of backup codes
    
    # Company association
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Authentication type
    auth_type = Column(String(20), default="local", nullable=False)  # local, ad, azure
    
    # Relationships
    corrections_made = relationship("DeviceCorrection", foreign_keys="DeviceCorrection.user_id", back_populates="user")
    corrections_verified = relationship("DeviceCorrection", foreign_keys="DeviceCorrection.verified_by", back_populates="verifier")
    device_feedback = relationship("DeviceFeedback", back_populates="user")
    company = relationship("Company", back_populates="users")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
