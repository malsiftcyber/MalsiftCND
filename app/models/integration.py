"""
Integration database model
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Integration(Base):
    """Integration model"""
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Integration information
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    integration_type = Column(String(50), nullable=False)  # runzero, tanium, armis, ad, azure_ad
    
    # Configuration
    enabled = Column(Boolean, default=False, nullable=False)
    config = Column(JSONB, nullable=True)  # Encrypted configuration
    
    # Status
    connected = Column(Boolean, default=False, nullable=False)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    
    # Sync settings
    auto_sync_enabled = Column(Boolean, default=False, nullable=False)
    sync_interval = Column(Integer, default=3600, nullable=False)  # seconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Integration(name='{self.name}', type='{self.integration_type}', enabled={self.enabled})>"


class IntegrationSync(Base):
    """Integration sync history model"""
    __tablename__ = "integration_syncs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Sync information
    sync_type = Column(String(20), nullable=False)  # full, incremental
    status = Column(String(20), nullable=False)  # running, completed, failed
    
    # Results
    records_synced = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<IntegrationSync(integration_id='{self.integration_id}', status='{self.status}')>"
