"""
Accuracy ranking API endpoints
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime

from app.auth.auth_service import AuthService
from app.services.accuracy_ranking_service import AccuracyRankingService
from app.models.accuracy_ranking import DataSourceType

router = APIRouter()
auth_service = AuthService()
accuracy_service = AccuracyRankingService()


# Request/Response Models
class DataSourceCreateRequest(BaseModel):
    name: str
    source_type: DataSourceType
    provider: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    is_ai_evaluated: bool = True
    manual_rank_override: Optional[int] = None


class DataSourceUpdateRequest(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_ai_evaluated: Optional[bool] = None
    manual_rank_override: Optional[int] = None


class EvaluationRequest(BaseModel):
    evaluation_type: str = "device_identification"
    sample_size: int = 100


class DashboardCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    refresh_interval_minutes: int = 15
    source_type_filter: Optional[List[str]] = None
    time_range_days: int = 30
    min_accuracy_threshold: float = 0.0


@router.get("/data-sources", response_model=List[Dict[str, Any]])
async def list_data_sources(
    active_only: bool = True,
    ranked_only: bool = False,
    token: str = Depends(auth_service.verify_token)
):
    """List all data sources"""
    try:
        from app.core.database import SessionLocal
        from app.models.accuracy_ranking import DataSource
        
        db = SessionLocal()
        try:
            query = db.query(DataSource)
            
            if active_only:
                query = query.filter(DataSource.is_active == True)
            
            if ranked_only:
                query = query.filter(DataSource.current_rank.isnot(None))
            
            sources = query.order_by(DataSource.current_rank.asc()).all()
            
            return [
                {
                    "id": str(source.id),
                    "name": source.name,
                    "source_type": source.source_type,
                    "provider": source.provider,
                    "version": source.version,
                    "description": source.description,
                    "is_active": source.is_active,
                    "is_ai_evaluated": source.is_ai_evaluated,
                    "manual_rank_override": source.manual_rank_override,
                    "current_accuracy_score": source.current_accuracy_score,
                    "confidence_level": source.confidence_level,
                    "current_rank": source.current_rank,
                    "previous_rank": source.previous_rank,
                    "rank_change": source.rank_change,
                    "total_evaluations": source.total_evaluations,
                    "successful_evaluations": source.successful_evaluations,
                    "failed_evaluations": source.failed_evaluations,
                    "average_response_time_ms": source.average_response_time_ms,
                    "success_rate": source.success_rate,
                    "data_completeness_score": source.data_completeness_score,
                    "last_evaluation": source.last_evaluation.isoformat() if source.last_evaluation else None,
                    "created_at": source.created_at.isoformat(),
                    "updated_at": source.updated_at.isoformat() if source.updated_at else None
                }
                for source in sources
            ]
            
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list data sources: {str(e)}"
        )


@router.post("/data-sources", response_model=Dict[str, str])
async def create_data_source(
    request: DataSourceCreateRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Create a new data source"""
    try:
        from app.core.database import SessionLocal
        from app.models.accuracy_ranking import DataSource
        import uuid
        
        db = SessionLocal()
        try:
            source = DataSource(
                id=uuid.uuid4(),
                name=request.name,
                source_type=request.source_type,
                provider=request.provider,
                version=request.version,
                description=request.description,
                is_active=request.is_active,
                is_ai_evaluated=request.is_ai_evaluated,
                manual_rank_override=request.manual_rank_override
            )
            
            db.add(source)
            db.commit()
            db.refresh(source)
            
            return {
                "source_id": str(source.id),
                "message": f"Data source '{request.name}' created successfully"
            }
            
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create data source: {str(e)}"
        )


@router.get("/data-sources/{source_id}", response_model=Dict[str, Any])
async def get_data_source(
    source_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Get data source by ID"""
    try:
        from app.core.database import SessionLocal
        from app.models.accuracy_ranking import DataSource
        
        db = SessionLocal()
        try:
            source = db.query(DataSource).filter(DataSource.id == source_id).first()
            if not source:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Data source not found"
                )
            
            return {
                "id": str(source.id),
                "name": source.name,
                "source_type": source.source_type,
                "provider": source.provider,
                "version": source.version,
                "description": source.description,
                "is_active": source.is_active,
                "is_ai_evaluated": source.is_ai_evaluated,
                "manual_rank_override": source.manual_rank_override,
                "current_accuracy_score": source.current_accuracy_score,
                "confidence_level": source.confidence_level,
                "current_rank": source.current_rank,
                "previous_rank": source.previous_rank,
                "rank_change": source.rank_change,
                "total_evaluations": source.total_evaluations,
                "successful_evaluations": source.successful_evaluations,
                "failed_evaluations": source.failed_evaluations,
                "average_response_time_ms": source.average_response_time_ms,
                "success_rate": source.success_rate,
                "data_completeness_score": source.data_completeness_score,
                "last_evaluation": source.last_evaluation.isoformat() if source.last_evaluation else None,
                "created_at": source.created_at.isoformat(),
                "updated_at": source.updated_at.isoformat() if source.updated_at else None
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get data source: {str(e)}"
        )


@router.put("/data-sources/{source_id}")
async def update_data_source(
    source_id: str,
    request: DataSourceUpdateRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Update data source"""
    try:
        from app.core.database import SessionLocal
        from app.models.accuracy_ranking import DataSource
        
        db = SessionLocal()
        try:
            source = db.query(DataSource).filter(DataSource.id == source_id).first()
            if not source:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Data source not found"
                )
            
            # Update fields
            update_data = {k: v for k, v in request.dict().items() if v is not None}
            for key, value in update_data.items():
                if hasattr(source, key):
                    setattr(source, key, value)
            
            source.updated_at = datetime.utcnow()
            db.commit()
            
            return {"message": f"Data source '{source_id}' updated successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update data source: {str(e)}"
        )


@router.post("/data-sources/{source_id}/evaluate")
async def evaluate_data_source(
    source_id: str,
    request: EvaluationRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Evaluate data source accuracy"""
    try:
        result = await accuracy_service.evaluate_data_source_accuracy(
            source_id, request.evaluation_type, request.sample_size
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate data source: {str(e)}"
        )


@router.post("/rankings/calculate")
async def calculate_rankings(
    token: str = Depends(auth_service.verify_token)
):
    """Calculate and update data source rankings"""
    try:
        result = await accuracy_service.calculate_rankings()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate rankings: {str(e)}"
        )


@router.get("/rankings", response_model=List[Dict[str, Any]])
async def get_rankings(
    limit: int = Query(default=50, description="Number of rankings to return", ge=1, le=100),
    offset: int = Query(default=0, description="Number of rankings to skip", ge=0),
    token: str = Depends(auth_service.verify_token)
):
    """Get historical rankings"""
    try:
        from app.core.database import SessionLocal
        from app.models.accuracy_ranking import AccuracyRanking
        
        db = SessionLocal()
        try:
            rankings = db.query(AccuracyRanking).order_by(
                AccuracyRanking.ranking_period_end.desc()
            ).offset(offset).limit(limit).all()
            
            return [
                {
                    "id": str(ranking.id),
                    "data_source_id": str(ranking.data_source_id),
                    "data_source_name": ranking.data_source.name,
                    "rank": ranking.rank,
                    "accuracy_score": ranking.accuracy_score,
                    "confidence_level": ranking.confidence_level,
                    "total_evaluations": ranking.total_evaluations,
                    "successful_evaluations": ranking.successful_evaluations,
                    "failed_evaluations": ranking.failed_evaluations,
                    "average_response_time_ms": ranking.average_response_time_ms,
                    "success_rate": ranking.success_rate,
                    "data_completeness_score": ranking.data_completeness_score,
                    "ranking_period_start": ranking.ranking_period_start.isoformat(),
                    "ranking_period_end": ranking.ranking_period_end.isoformat(),
                    "ranking_algorithm_version": ranking.ranking_algorithm_version,
                    "created_at": ranking.created_at.isoformat()
                }
                for ranking in rankings
            ]
            
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rankings: {str(e)}"
        )


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_data(
    dashboard_id: Optional[str] = None,
    token: str = Depends(auth_service.verify_token)
):
    """Get accuracy ranking dashboard data"""
    try:
        result = await accuracy_service.get_dashboard_data(dashboard_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard data: {str(e)}"
        )


@router.post("/dashboard", response_model=Dict[str, str])
async def create_dashboard(
    request: DashboardCreateRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Create a new accuracy dashboard"""
    try:
        from app.core.database import SessionLocal
        from app.models.accuracy_ranking import AccuracyDashboard
        import uuid
        
        db = SessionLocal()
        try:
            dashboard = AccuracyDashboard(
                id=uuid.uuid4(),
                name=request.name,
                description=request.description,
                refresh_interval_minutes=request.refresh_interval_minutes,
                source_type_filter=request.source_type_filter,
                time_range_days=request.time_range_days,
                min_accuracy_threshold=request.min_accuracy_threshold,
                created_by=auth_service.get_current_user_id(token)  # You'll need to implement this
            )
            
            db.add(dashboard)
            db.commit()
            db.refresh(dashboard)
            
            return {
                "dashboard_id": str(dashboard.id),
                "message": f"Dashboard '{request.name}' created successfully"
            }
            
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create dashboard: {str(e)}"
        )


@router.get("/alerts", response_model=List[Dict[str, Any]])
async def get_accuracy_alerts(
    active_only: bool = True,
    severity: Optional[str] = None,
    limit: int = Query(default=50, description="Number of alerts to return", ge=1, le=100),
    offset: int = Query(default=0, description="Number of alerts to skip", ge=0),
    token: str = Depends(auth_service.verify_token)
):
    """Get accuracy alerts"""
    try:
        from app.core.database import SessionLocal
        from app.models.accuracy_ranking import AccuracyAlert
        
        db = SessionLocal()
        try:
            query = db.query(AccuracyAlert)
            
            if active_only:
                query = query.filter(AccuracyAlert.is_active == True)
            
            if severity:
                query = query.filter(AccuracyAlert.severity == severity)
            
            alerts = query.order_by(AccuracyAlert.triggered_at.desc()).offset(offset).limit(limit).all()
            
            return [
                {
                    "id": str(alert.id),
                    "data_source_id": str(alert.data_source_id),
                    "data_source_name": alert.data_source.name,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "title": alert.title,
                    "description": alert.description,
                    "alert_data": alert.alert_data,
                    "threshold_value": alert.threshold_value,
                    "actual_value": alert.actual_value,
                    "change_percentage": alert.change_percentage,
                    "is_active": alert.is_active,
                    "is_acknowledged": alert.is_acknowledged,
                    "acknowledged_by": str(alert.acknowledged_by) if alert.acknowledged_by else None,
                    "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                    "triggered_at": alert.triggered_at.isoformat(),
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                    "created_at": alert.created_at.isoformat()
                }
                for alert in alerts
            ]
            
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get accuracy alerts: {str(e)}"
        )


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Acknowledge an accuracy alert"""
    try:
        from app.core.database import SessionLocal
        from app.models.accuracy_ranking import AccuracyAlert
        
        db = SessionLocal()
        try:
            alert = db.query(AccuracyAlert).filter(AccuracyAlert.id == alert_id).first()
            if not alert:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Alert not found"
                )
            
            alert.is_acknowledged = True
            alert.acknowledged_by = auth_service.get_current_user_id(token)  # You'll need to implement this
            alert.acknowledged_at = datetime.utcnow()
            
            db.commit()
            
            return {"message": f"Alert '{alert_id}' acknowledged successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to acknowledge alert: {str(e)}"
        )


@router.get("/metrics", response_model=Dict[str, Any])
async def get_accuracy_metrics(
    period: str = Query(default="daily", description="Metric period", regex="^(hourly|daily|weekly|monthly)$"),
    days: int = Query(default=30, description="Number of days to include", ge=1, le=365),
    token: str = Depends(auth_service.verify_token)
):
    """Get accuracy metrics over time"""
    try:
        from app.core.database import SessionLocal
        from app.models.accuracy_ranking import AccuracyMetric
        
        db = SessionLocal()
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            metrics = db.query(AccuracyMetric).filter(
                AccuracyMetric.metric_date >= start_date,
                AccuracyMetric.metric_period == period
            ).order_by(AccuracyMetric.metric_date.asc()).all()
            
            # Group by data source
            metrics_by_source = {}
            for metric in metrics:
                source_id = str(metric.data_source_id)
                if source_id not in metrics_by_source:
                    metrics_by_source[source_id] = {
                        "source_name": metric.data_source.name,
                        "source_type": metric.data_source.source_type,
                        "metrics": []
                    }
                
                metrics_by_source[source_id]["metrics"].append({
                    "date": metric.metric_date.isoformat(),
                    "accuracy_score": metric.accuracy_score,
                    "confidence_level": metric.confidence_level,
                    "total_evaluations": metric.total_evaluations,
                    "success_rate": metric.success_rate,
                    "data_completeness": metric.data_completeness_score,
                    "rank": metric.rank,
                    "rank_change": metric.rank_change
                })
            
            return {
                "period": period,
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "metrics_by_source": metrics_by_source
            }
            
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get accuracy metrics: {str(e)}"
        )


@router.post("/initialize")
async def initialize_accuracy_system(
    token: str = Depends(auth_service.verify_token)
):
    """Initialize the accuracy ranking system with default data sources"""
    try:
        await accuracy_service.initialize_data_sources()
        return {"message": "Accuracy ranking system initialized successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize accuracy system: {str(e)}"
        )


@router.get("/source-types")
async def get_source_types(
    token: str = Depends(auth_service.verify_token)
):
    """Get available data source types"""
    return {
        "source_types": [
            {
                "value": "network_scanner",
                "name": "Network Scanner",
                "description": "Network discovery and port scanning tools"
            },
            {
                "value": "edr_platform",
                "name": "EDR Platform",
                "description": "Endpoint detection and response platforms"
            },
            {
                "value": "asm_tool",
                "name": "ASM Tool",
                "description": "Attack surface management tools"
            },
            {
                "value": "directory_service",
                "name": "Directory Service",
                "description": "Active Directory and Azure AD services"
            },
            {
                "value": "ai_analysis",
                "name": "AI Analysis",
                "description": "AI-powered analysis and identification"
            },
            {
                "value": "user_correction",
                "name": "User Correction",
                "description": "Manual user corrections and verifications"
            }
        ]
    }
