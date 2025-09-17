"""
Database models for AI-based accuracy ranking system
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, Float, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum

from app.core.database import Base


class DataSourceType(str, Enum):
    """Data source types for accuracy tracking"""
    NETWORK_SCANNER = "network_scanner"
    EDR_PLATFORM = "edr_platform"
    ASM_TOOL = "asm_tool"
    DIRECTORY_SERVICE = "directory_service"
    AI_ANALYSIS = "ai_analysis"
    USER_CORRECTION = "user_correction"


class DataSource(Base):
    """Data source configuration and metadata"""
    __tablename__ = "data_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    source_type = Column(String(50), nullable=False)  # DataSourceType enum
    provider = Column(String(100), nullable=True)  # e.g., "nmap", "crowdstrike", "runzero"
    version = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_ai_evaluated = Column(Boolean, default=True, nullable=False)  # Whether AI evaluates this source
    manual_rank_override = Column(Integer, nullable=True)  # Manual rank override (1-10)
    
    # Accuracy Metrics
    current_accuracy_score = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    confidence_level = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    total_evaluations = Column(Integer, default=0, nullable=False)
    successful_evaluations = Column(Integer, default=0, nullable=False)
    failed_evaluations = Column(Integer, default=0, nullable=False)
    
    # Performance Metrics
    average_response_time_ms = Column(Float, default=0.0, nullable=False)
    success_rate = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    data_completeness_score = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    
    # Ranking
    current_rank = Column(Integer, nullable=True)  # 1-10, NULL if not ranked
    previous_rank = Column(Integer, nullable=True)
    rank_change = Column(Integer, default=0, nullable=False)  # Positive = improved, negative = declined
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_evaluation = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    evaluations = relationship("AccuracyEvaluation", back_populates="data_source")
    rankings = relationship("AccuracyRanking", back_populates="data_source")


class AccuracyEvaluation(Base):
    """Individual accuracy evaluations for data sources"""
    __tablename__ = "accuracy_evaluations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_source_id = Column(UUID(as_uuid=True), ForeignKey("data_sources.id"), nullable=False)
    
    # Evaluation Context
    evaluation_type = Column(String(50), nullable=False)  # "device_identification", "os_detection", "service_detection", etc.
    target_device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True)
    evaluation_context = Column(JSONB, nullable=True)  # Additional context data
    
    # Evaluation Results
    predicted_value = Column(String(500), nullable=True)  # What the source predicted
    actual_value = Column(String(500), nullable=True)  # Ground truth value
    accuracy_score = Column(Float, nullable=False)  # 0.0 to 1.0
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    
    # Evaluation Details
    evaluation_method = Column(String(50), nullable=False)  # "ai_comparison", "user_verification", "cross_validation", etc.
    evaluation_metadata = Column(JSONB, nullable=True)  # Additional evaluation data
    
    # Performance Metrics
    response_time_ms = Column(Float, nullable=True)
    data_completeness = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Timestamps
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    data_source = relationship("DataSource", back_populates="evaluations")
    device = relationship("Device")


class AccuracyRanking(Base):
    """Historical accuracy rankings"""
    __tablename__ = "accuracy_rankings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_source_id = Column(UUID(as_uuid=True), ForeignKey("data_sources.id"), nullable=False)
    
    # Ranking Data
    rank = Column(Integer, nullable=False)  # 1-10
    accuracy_score = Column(Float, nullable=False)  # 0.0 to 1.0
    confidence_level = Column(Float, nullable=False)  # 0.0 to 1.0
    total_evaluations = Column(Integer, nullable=False)
    successful_evaluations = Column(Integer, nullable=False)
    failed_evaluations = Column(Integer, nullable=False)
    
    # Performance Metrics
    average_response_time_ms = Column(Float, nullable=False)
    success_rate = Column(Float, nullable=False)
    data_completeness_score = Column(Float, nullable=False)
    
    # Ranking Period
    ranking_period_start = Column(DateTime(timezone=True), nullable=False)
    ranking_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Metadata
    ranking_algorithm_version = Column(String(50), nullable=False)
    ranking_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    data_source = relationship("DataSource", back_populates="rankings")


class AccuracyDashboard(Base):
    """Dashboard configuration and cached data"""
    __tablename__ = "accuracy_dashboards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Dashboard Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    refresh_interval_minutes = Column(Integer, default=15, nullable=False)
    last_refresh = Column(DateTime(timezone=True), nullable=True)
    next_refresh = Column(DateTime(timezone=True), nullable=True)
    
    # Dashboard Data (cached)
    dashboard_data = Column(JSONB, nullable=True)  # Cached dashboard data
    
    # Filters
    source_type_filter = Column(JSONB, nullable=True)  # Filter by source types
    time_range_days = Column(Integer, default=30, nullable=False)
    min_accuracy_threshold = Column(Float, default=0.0, nullable=False)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")


class AccuracyAlert(Base):
    """Alerts for significant accuracy changes"""
    __tablename__ = "accuracy_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_source_id = Column(UUID(as_uuid=True), ForeignKey("data_sources.id"), nullable=False)
    
    # Alert Details
    alert_type = Column(String(50), nullable=False)  # "accuracy_drop", "rank_change", "performance_issue", etc.
    severity = Column(String(20), nullable=False)  # "low", "medium", "high", "critical"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Alert Data
    alert_data = Column(JSONB, nullable=True)  # Additional alert data
    threshold_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)
    change_percentage = Column(Float, nullable=True)
    
    # Alert Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    data_source = relationship("DataSource")
    acknowledger = relationship("User", foreign_keys=[acknowledged_by])


class AccuracyMetric(Base):
    """Aggregated accuracy metrics for reporting"""
    __tablename__ = "accuracy_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_source_id = Column(UUID(as_uuid=True), ForeignKey("data_sources.id"), nullable=False)
    
    # Metric Period
    metric_date = Column(DateTime(timezone=True), nullable=False)
    metric_period = Column(String(20), nullable=False)  # "hourly", "daily", "weekly", "monthly"
    
    # Aggregated Metrics
    total_evaluations = Column(Integer, nullable=False)
    successful_evaluations = Column(Integer, nullable=False)
    failed_evaluations = Column(Integer, nullable=False)
    accuracy_score = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=False)
    
    # Performance Metrics
    average_response_time_ms = Column(Float, nullable=False)
    success_rate = Column(Float, nullable=False)
    data_completeness_score = Column(Float, nullable=False)
    
    # Ranking Metrics
    rank = Column(Integer, nullable=True)
    rank_change = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    data_source = relationship("DataSource")
