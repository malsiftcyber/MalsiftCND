"""
Scan database model
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Scan(Base):
    """Scan model"""
    __tablename__ = "scans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Scan configuration
    targets = Column(JSONB, nullable=False)  # List of target IPs/CIDRs
    scan_type = Column(String(50), nullable=False)  # ping_sweep, port_scan, etc.
    scanner = Column(String(20), nullable=False)  # nmap, masscan
    ports = Column(JSONB, nullable=True)  # List of ports to scan
    timeout = Column(Integer, default=300, nullable=False)
    rate_limit = Column(Integer, nullable=True)
    
    # Company and site associations
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=True)
    
    # Scan status
    status = Column(String(20), default="queued", nullable=False)  # queued, running, completed, failed, cancelled
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    current_target = Column(String(45), nullable=True)  # Current IP being scanned
    
    # Results
    results_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="scans")
    scan_results = relationship("ScanResult", back_populates="scan", cascade="all, delete-orphan")
    scan_tags = relationship("ScanTag", back_populates="scan")
    company = relationship("Company", back_populates="scans")
    site = relationship("Site", back_populates="scans")
    
    def __repr__(self):
        return f"<Scan(id='{self.id}', status='{self.status}', targets={len(self.targets)})>"


class ScanResult(Base):
    """Scan result model"""
    __tablename__ = "scan_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    
    # Target information
    target_ip = Column(String(45), nullable=False, index=True)
    target_hostname = Column(String(255), nullable=True)
    
    # Scan results
    success = Column(Boolean, nullable=False)
    scan_data = Column(JSONB, nullable=True)  # Raw scan results
    error_message = Column(Text, nullable=True)
    scan_time = Column(Integer, nullable=True)  # Scan duration in seconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scan = relationship("Scan", back_populates="scan_results")
    
    def __repr__(self):
        return f"<ScanResult(target='{self.target_ip}', success={self.success})>"
