"""
AI-based accuracy ranking service for data sources
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import statistics
import json
from collections import defaultdict

from app.core.database import SessionLocal
from app.models.accuracy_ranking import (
    DataSource, AccuracyEvaluation, AccuracyRanking, AccuracyDashboard,
    AccuracyAlert, AccuracyMetric, DataSourceType
)
from app.models.device import Device
from app.models.edr_integration import EDREndpoint
from app.models.device_correction import DeviceCorrection
from app.ai.llm_analyzer import LLMAnalyzer


class AccuracyRankingService:
    """Service for AI-based accuracy ranking of data sources"""
    
    def __init__(self):
        self.logger = logging.getLogger("services.accuracy_ranking")
        self.llm_analyzer = LLMAnalyzer()
        self.ranking_algorithm_version = "1.0"
    
    async def evaluate_data_source_accuracy(self, data_source_id: str, 
                                          evaluation_type: str = "device_identification",
                                          sample_size: int = 100) -> Dict[str, Any]:
        """Evaluate accuracy of a specific data source"""
        db = SessionLocal()
        try:
            data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
            if not data_source:
                raise ValueError("Data source not found")
            
            self.logger.info(f"Evaluating accuracy for data source: {data_source.name}")
            
            # Get sample devices for evaluation
            devices = db.query(Device).limit(sample_size).all()
            if not devices:
                return {"error": "No devices available for evaluation"}
            
            evaluations = []
            total_accuracy = 0.0
            total_confidence = 0.0
            total_response_time = 0.0
            total_completeness = 0.0
            
            for device in devices:
                try:
                    evaluation_result = await self._evaluate_device_identification(
                        data_source, device, evaluation_type
                    )
                    
                    if evaluation_result:
                        evaluations.append(evaluation_result)
                        total_accuracy += evaluation_result['accuracy_score']
                        total_confidence += evaluation_result['confidence_score']
                        total_response_time += evaluation_result.get('response_time_ms', 0)
                        total_completeness += evaluation_result.get('data_completeness', 0)
                        
                        # Store evaluation in database
                        evaluation = AccuracyEvaluation(
                            data_source_id=data_source_id,
                            evaluation_type=evaluation_type,
                            target_device_id=device.id,
                            predicted_value=evaluation_result['predicted_value'],
                            actual_value=evaluation_result['actual_value'],
                            accuracy_score=evaluation_result['accuracy_score'],
                            confidence_score=evaluation_result['confidence_score'],
                            evaluation_method=evaluation_result['evaluation_method'],
                            response_time_ms=evaluation_result.get('response_time_ms'),
                            data_completeness=evaluation_result.get('data_completeness')
                        )
                        db.add(evaluation)
                
                except Exception as e:
                    self.logger.error(f"Failed to evaluate device {device.id}: {e}")
                    continue
            
            if not evaluations:
                return {"error": "No successful evaluations"}
            
            # Calculate aggregate metrics
            avg_accuracy = total_accuracy / len(evaluations)
            avg_confidence = total_confidence / len(evaluations)
            avg_response_time = total_response_time / len(evaluations)
            avg_completeness = total_completeness / len(evaluations)
            success_rate = len(evaluations) / len(devices)
            
            # Update data source metrics
            data_source.current_accuracy_score = avg_accuracy
            data_source.confidence_level = avg_confidence
            data_source.total_evaluations += len(evaluations)
            data_source.successful_evaluations += len(evaluations)
            data_source.failed_evaluations += (len(devices) - len(evaluations))
            data_source.average_response_time_ms = avg_response_time
            data_source.success_rate = success_rate
            data_source.data_completeness_score = avg_completeness
            data_source.last_evaluation = datetime.utcnow()
            
            db.commit()
            
            return {
                "data_source_id": data_source_id,
                "evaluation_type": evaluation_type,
                "total_evaluations": len(evaluations),
                "average_accuracy": avg_accuracy,
                "average_confidence": avg_confidence,
                "average_response_time_ms": avg_response_time,
                "data_completeness": avg_completeness,
                "success_rate": success_rate
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to evaluate data source accuracy: {e}")
            raise
        finally:
            db.close()
    
    async def _evaluate_device_identification(self, data_source: DataSource, 
                                           device: Device, 
                                           evaluation_type: str) -> Optional[Dict[str, Any]]:
        """Evaluate device identification accuracy for a specific device"""
        try:
            # Get predicted value from data source
            predicted_value = self._get_predicted_value(data_source, device, evaluation_type)
            if not predicted_value:
                return None
            
            # Get actual value (ground truth)
            actual_value = self._get_actual_value(device, evaluation_type)
            if not actual_value:
                return None
            
            # Use AI to compare predicted vs actual
            accuracy_result = await self._ai_compare_values(
                predicted_value, actual_value, evaluation_type
            )
            
            if not accuracy_result:
                return None
            
            # Calculate additional metrics
            response_time = self._calculate_response_time(data_source, device)
            completeness = self._calculate_data_completeness(data_source, device)
            
            return {
                'predicted_value': predicted_value,
                'actual_value': actual_value,
                'accuracy_score': accuracy_result['accuracy_score'],
                'confidence_score': accuracy_result['confidence_score'],
                'evaluation_method': 'ai_comparison',
                'response_time_ms': response_time,
                'data_completeness': completeness
            }
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate device identification: {e}")
            return None
    
    def _get_predicted_value(self, data_source: DataSource, device: Device, 
                           evaluation_type: str) -> Optional[str]:
        """Get predicted value from data source"""
        try:
            if evaluation_type == "device_identification":
                if data_source.source_type == DataSourceType.NETWORK_SCANNER:
                    return device.device_type
                elif data_source.source_type == DataSourceType.EDR_PLATFORM:
                    # Get EDR endpoint data
                    edr_endpoint = device.edr_endpoints[0] if device.edr_endpoints else None
                    if edr_endpoint:
                        return edr_endpoint.operating_system
                elif data_source.source_type == DataSourceType.AI_ANALYSIS:
                    return device.ai_analysis.get('device_type') if device.ai_analysis else None
            
            elif evaluation_type == "os_detection":
                if data_source.source_type == DataSourceType.NETWORK_SCANNER:
                    return device.operating_system
                elif data_source.source_type == DataSourceType.EDR_PLATFORM:
                    edr_endpoint = device.edr_endpoints[0] if device.edr_endpoints else None
                    if edr_endpoint:
                        return edr_endpoint.operating_system
            
            elif evaluation_type == "service_detection":
                if data_source.source_type == DataSourceType.NETWORK_SCANNER:
                    services = device.scan_results.get('services', []) if device.scan_results else []
                    return ', '.join(services) if services else None
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get predicted value: {e}")
            return None
    
    def _get_actual_value(self, device: Device, evaluation_type: str) -> Optional[str]:
        """Get actual value (ground truth) for comparison"""
        try:
            if evaluation_type == "device_identification":
                # Use user corrections as ground truth
                corrections = device.corrections
                if corrections:
                    latest_correction = max(corrections, key=lambda c: c.created_at)
                    return latest_correction.corrected_device_type
                
                # Fallback to EDR data as ground truth
                if device.edr_endpoints:
                    edr_endpoint = device.edr_endpoints[0]
                    return edr_endpoint.operating_system
            
            elif evaluation_type == "os_detection":
                # Use EDR data as ground truth for OS
                if device.edr_endpoints:
                    edr_endpoint = device.edr_endpoints[0]
                    return edr_endpoint.operating_system
            
            elif evaluation_type == "service_detection":
                # Use EDR data as ground truth for services
                if device.edr_endpoints:
                    edr_endpoint = device.edr_endpoints[0]
                    if edr_endpoint.edr_raw_data:
                        services = edr_endpoint.edr_raw_data.get('services', [])
                        return ', '.join(services) if services else None
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get actual value: {e}")
            return None
    
    async def _ai_compare_values(self, predicted: str, actual: str, 
                               evaluation_type: str) -> Optional[Dict[str, Any]]:
        """Use AI to compare predicted vs actual values"""
        try:
            prompt = f"""
            Compare the predicted and actual values for {evaluation_type}:
            
            Predicted: {predicted}
            Actual: {actual}
            
            Please provide:
            1. Accuracy score (0.0 to 1.0) - how close is the prediction to the actual value?
            2. Confidence score (0.0 to 1.0) - how confident are you in this comparison?
            3. Brief explanation of the comparison
            
            Respond in JSON format:
            {{
                "accuracy_score": 0.85,
                "confidence_score": 0.90,
                "explanation": "The prediction is very close to the actual value with minor differences"
            }}
            """
            
            response = await self.llm_analyzer.analyze_with_llm(prompt)
            if response:
                try:
                    result = json.loads(response)
                    return {
                        'accuracy_score': float(result.get('accuracy_score', 0.0)),
                        'confidence_score': float(result.get('confidence_score', 0.0)),
                        'explanation': result.get('explanation', '')
                    }
                except json.JSONDecodeError:
                    # Fallback to simple string comparison
                    return self._fallback_comparison(predicted, actual)
            
            return self._fallback_comparison(predicted, actual)
            
        except Exception as e:
            self.logger.error(f"AI comparison failed: {e}")
            return self._fallback_comparison(predicted, actual)
    
    def _fallback_comparison(self, predicted: str, actual: str) -> Dict[str, Any]:
        """Fallback comparison method when AI fails"""
        try:
            if not predicted or not actual:
                return {'accuracy_score': 0.0, 'confidence_score': 0.0, 'explanation': 'Missing data'}
            
            # Simple string similarity
            predicted_lower = predicted.lower().strip()
            actual_lower = actual.lower().strip()
            
            if predicted_lower == actual_lower:
                return {'accuracy_score': 1.0, 'confidence_score': 0.8, 'explanation': 'Exact match'}
            
            # Check for partial matches
            if predicted_lower in actual_lower or actual_lower in predicted_lower:
                return {'accuracy_score': 0.7, 'confidence_score': 0.6, 'explanation': 'Partial match'}
            
            # Check for common words
            predicted_words = set(predicted_lower.split())
            actual_words = set(actual_lower.split())
            common_words = predicted_words.intersection(actual_words)
            
            if common_words:
                similarity = len(common_words) / max(len(predicted_words), len(actual_words))
                return {
                    'accuracy_score': similarity,
                    'confidence_score': 0.5,
                    'explanation': f'Partial match with {len(common_words)} common words'
                }
            
            return {'accuracy_score': 0.0, 'confidence_score': 0.3, 'explanation': 'No match'}
            
        except Exception as e:
            self.logger.error(f"Fallback comparison failed: {e}")
            return {'accuracy_score': 0.0, 'confidence_score': 0.0, 'explanation': 'Comparison failed'}
    
    def _calculate_response_time(self, data_source: DataSource, device: Device) -> float:
        """Calculate response time for data source"""
        try:
            # This would be calculated based on actual API response times
            # For now, return a simulated value based on source type
            base_times = {
                DataSourceType.NETWORK_SCANNER: 1000.0,  # 1 second
                DataSourceType.EDR_PLATFORM: 500.0,      # 0.5 seconds
                DataSourceType.ASM_TOOL: 2000.0,          # 2 seconds
                DataSourceType.DIRECTORY_SERVICE: 300.0,  # 0.3 seconds
                DataSourceType.AI_ANALYSIS: 3000.0,       # 3 seconds
                DataSourceType.USER_CORRECTION: 0.0       # Instant
            }
            
            return base_times.get(data_source.source_type, 1000.0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate response time: {e}")
            return 1000.0
    
    def _calculate_data_completeness(self, data_source: DataSource, device: Device) -> float:
        """Calculate data completeness score for data source"""
        try:
            completeness_score = 0.0
            total_fields = 0
            
            if data_source.source_type == DataSourceType.NETWORK_SCANNER:
                # Check network scanner data completeness
                if device.device_type and device.device_type != "Unknown":
                    completeness_score += 1
                total_fields += 1
                
                if device.operating_system and device.operating_system != "Unknown":
                    completeness_score += 1
                total_fields += 1
                
                if device.scan_results:
                    completeness_score += 1
                total_fields += 1
            
            elif data_source.source_type == DataSourceType.EDR_PLATFORM:
                # Check EDR data completeness
                if device.edr_endpoints:
                    edr_endpoint = device.edr_endpoints[0]
                    if edr_endpoint.hostname:
                        completeness_score += 1
                    total_fields += 1
                    
                    if edr_endpoint.operating_system:
                        completeness_score += 1
                    total_fields += 1
                    
                    if edr_endpoint.agent_status:
                        completeness_score += 1
                    total_fields += 1
            
            return completeness_score / total_fields if total_fields > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Failed to calculate data completeness: {e}")
            return 0.0
    
    async def calculate_rankings(self) -> Dict[str, Any]:
        """Calculate and update data source rankings"""
        db = SessionLocal()
        try:
            self.logger.info("Calculating data source rankings")
            
            # Get all active data sources
            data_sources = db.query(DataSource).filter(
                DataSource.is_active == True,
                DataSource.is_ai_evaluated == True
            ).all()
            
            if not data_sources:
                return {"error": "No data sources available for ranking"}
            
            # Calculate composite scores for each data source
            source_scores = []
            for source in data_sources:
                composite_score = self._calculate_composite_score(source)
                source_scores.append({
                    'source': source,
                    'score': composite_score,
                    'accuracy': source.current_accuracy_score,
                    'confidence': source.confidence_level,
                    'performance': source.average_response_time_ms,
                    'completeness': source.data_completeness_score
                })
            
            # Sort by composite score (descending)
            source_scores.sort(key=lambda x: x['score'], reverse=True)
            
            # Update rankings
            current_time = datetime.utcnow()
            ranking_period_start = current_time - timedelta(days=7)  # Weekly ranking
            
            for rank, source_data in enumerate(source_scores, 1):
                source = source_data['source']
                previous_rank = source.current_rank
                
                # Update current ranking
                source.previous_rank = previous_rank
                source.current_rank = rank
                source.rank_change = (previous_rank - rank) if previous_rank else 0
                source.updated_at = current_time
                
                # Create ranking record
                ranking = AccuracyRanking(
                    data_source_id=source.id,
                    rank=rank,
                    accuracy_score=source.current_accuracy_score,
                    confidence_level=source.confidence_level,
                    total_evaluations=source.total_evaluations,
                    successful_evaluations=source.successful_evaluations,
                    failed_evaluations=source.failed_evaluations,
                    average_response_time_ms=source.average_response_time_ms,
                    success_rate=source.success_rate,
                    data_completeness_score=source.data_completeness_score,
                    ranking_period_start=ranking_period_start,
                    ranking_period_end=current_time,
                    ranking_algorithm_version=self.ranking_algorithm_version
                )
                db.add(ranking)
                
                # Check for significant rank changes and create alerts
                if previous_rank and abs(source.rank_change) >= 3:
                    await self._create_ranking_alert(source, previous_rank, rank)
            
            db.commit()
            
            return {
                "ranking_calculated": True,
                "total_sources": len(data_sources),
                "ranking_period": f"{ranking_period_start.isoformat()} to {current_time.isoformat()}",
                "algorithm_version": self.ranking_algorithm_version,
                "rankings": [
                    {
                        "rank": i + 1,
                        "source_name": source_data['source'].name,
                        "source_type": source_data['source'].source_type,
                        "composite_score": source_data['score'],
                        "accuracy_score": source_data['accuracy'],
                        "confidence_level": source_data['confidence'],
                        "rank_change": source_data['source'].rank_change
                    }
                    for i, source_data in enumerate(source_scores)
                ]
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to calculate rankings: {e}")
            raise
        finally:
            db.close()
    
    def _calculate_composite_score(self, source: DataSource) -> float:
        """Calculate composite score for ranking"""
        try:
            # Weighted composite score
            weights = {
                'accuracy': 0.4,      # 40% - Most important
                'confidence': 0.2,    # 20% - Confidence in accuracy
                'completeness': 0.2,  # 20% - Data completeness
                'performance': 0.1,   # 10% - Response time (inverted)
                'success_rate': 0.1   # 10% - Success rate
            }
            
            # Normalize performance (lower is better)
            performance_score = max(0, 1 - (source.average_response_time_ms / 10000))  # Normalize to 10 seconds max
            
            composite_score = (
                weights['accuracy'] * source.current_accuracy_score +
                weights['confidence'] * source.confidence_level +
                weights['completeness'] * source.data_completeness_score +
                weights['performance'] * performance_score +
                weights['success_rate'] * source.success_rate
            )
            
            return composite_score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate composite score: {e}")
            return 0.0
    
    async def _create_ranking_alert(self, source: DataSource, previous_rank: int, current_rank: int):
        """Create alert for significant ranking changes"""
        try:
            db = SessionLocal()
            
            rank_change = previous_rank - current_rank
            if abs(rank_change) >= 3:
                severity = "high" if abs(rank_change) >= 5 else "medium"
                direction = "improved" if rank_change > 0 else "declined"
                
                alert = AccuracyAlert(
                    data_source_id=source.id,
                    alert_type="rank_change",
                    severity=severity,
                    title=f"Significant Ranking Change: {source.name}",
                    description=f"Data source ranking {direction} from {previous_rank} to {current_rank}",
                    alert_data={
                        "previous_rank": previous_rank,
                        "current_rank": current_rank,
                        "rank_change": rank_change,
                        "direction": direction
                    },
                    threshold_value=3.0,
                    actual_value=abs(rank_change),
                    change_percentage=abs(rank_change) / previous_rank * 100
                )
                
                db.add(alert)
                db.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to create ranking alert: {e}")
        finally:
            db.close()
    
    async def get_dashboard_data(self, dashboard_id: str = None) -> Dict[str, Any]:
        """Get accuracy ranking dashboard data"""
        db = SessionLocal()
        try:
            # Get all active data sources with rankings
            data_sources = db.query(DataSource).filter(
                DataSource.is_active == True
            ).order_by(DataSource.current_rank.asc()).all()
            
            # Calculate summary statistics
            total_sources = len(data_sources)
            avg_accuracy = statistics.mean([s.current_accuracy_score for s in data_sources]) if data_sources else 0
            avg_confidence = statistics.mean([s.confidence_level for s in data_sources]) if data_sources else 0
            
            # Get recent evaluations
            recent_evaluations = db.query(AccuracyEvaluation).filter(
                AccuracyEvaluation.evaluated_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            # Get active alerts
            active_alerts = db.query(AccuracyAlert).filter(
                AccuracyAlert.is_active == True
            ).count()
            
            # Prepare ranking data
            rankings = []
            for source in data_sources:
                rankings.append({
                    "rank": source.current_rank,
                    "name": source.name,
                    "source_type": source.source_type,
                    "provider": source.provider,
                    "accuracy_score": source.current_accuracy_score,
                    "confidence_level": source.confidence_level,
                    "success_rate": source.success_rate,
                    "data_completeness": source.data_completeness_score,
                    "average_response_time_ms": source.average_response_time_ms,
                    "total_evaluations": source.total_evaluations,
                    "rank_change": source.rank_change,
                    "last_evaluation": source.last_evaluation.isoformat() if source.last_evaluation else None,
                    "is_ai_evaluated": source.is_ai_evaluated,
                    "manual_rank_override": source.manual_rank_override
                })
            
            # Get accuracy trends (last 30 days)
            accuracy_trends = await self._get_accuracy_trends()
            
            # Get performance metrics
            performance_metrics = await self._get_performance_metrics()
            
            dashboard_data = {
                "summary": {
                    "total_sources": total_sources,
                    "average_accuracy": avg_accuracy,
                    "average_confidence": avg_confidence,
                    "recent_evaluations": recent_evaluations,
                    "active_alerts": active_alerts,
                    "last_ranking_update": datetime.utcnow().isoformat()
                },
                "rankings": rankings,
                "accuracy_trends": accuracy_trends,
                "performance_metrics": performance_metrics
            }
            
            # Cache dashboard data if dashboard_id provided
            if dashboard_id:
                dashboard = db.query(AccuracyDashboard).filter(AccuracyDashboard.id == dashboard_id).first()
                if dashboard:
                    dashboard.dashboard_data = dashboard_data
                    dashboard.last_refresh = datetime.utcnow()
                    dashboard.next_refresh = datetime.utcnow() + timedelta(minutes=dashboard.refresh_interval_minutes)
                    db.commit()
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard data: {e}")
            raise
        finally:
            db.close()
    
    async def _get_accuracy_trends(self) -> Dict[str, Any]:
        """Get accuracy trends over time"""
        try:
            db = SessionLocal()
            
            # Get daily accuracy metrics for last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            metrics = db.query(AccuracyMetric).filter(
                AccuracyMetric.metric_date >= start_date,
                AccuracyMetric.metric_period == "daily"
            ).order_by(AccuracyMetric.metric_date.asc()).all()
            
            # Group by date
            trends_by_date = defaultdict(list)
            for metric in metrics:
                date_key = metric.metric_date.date().isoformat()
                trends_by_date[date_key].append(metric.accuracy_score)
            
            # Calculate daily averages
            trends = []
            for date, scores in trends_by_date.items():
                trends.append({
                    "date": date,
                    "average_accuracy": statistics.mean(scores),
                    "source_count": len(scores)
                })
            
            return {
                "period": "30_days",
                "trends": trends
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get accuracy trends: {e}")
            return {"period": "30_days", "trends": []}
        finally:
            db.close()
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        try:
            db = SessionLocal()
            
            # Get all data sources
            sources = db.query(DataSource).filter(DataSource.is_active == True).all()
            
            if not sources:
                return {"error": "No data sources available"}
            
            # Calculate performance metrics
            response_times = [s.average_response_time_ms for s in sources if s.average_response_time_ms > 0]
            success_rates = [s.success_rate for s in sources if s.success_rate > 0]
            completeness_scores = [s.data_completeness_score for s in sources if s.data_completeness_score > 0]
            
            return {
                "response_time": {
                    "average_ms": statistics.mean(response_times) if response_times else 0,
                    "min_ms": min(response_times) if response_times else 0,
                    "max_ms": max(response_times) if response_times else 0
                },
                "success_rate": {
                    "average": statistics.mean(success_rates) if success_rates else 0,
                    "min": min(success_rates) if success_rates else 0,
                    "max": max(success_rates) if success_rates else 0
                },
                "data_completeness": {
                    "average": statistics.mean(completeness_scores) if completeness_scores else 0,
                    "min": min(completeness_scores) if completeness_scores else 0,
                    "max": max(completeness_scores) if completeness_scores else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return {"error": "Failed to calculate performance metrics"}
        finally:
            db.close()
    
    async def initialize_data_sources(self):
        """Initialize default data sources"""
        db = SessionLocal()
        try:
            # Check if data sources already exist
            existing_sources = db.query(DataSource).count()
            if existing_sources > 0:
                self.logger.info("Data sources already initialized")
                return
            
            # Create default data sources
            default_sources = [
                {
                    "name": "Nmap Network Scanner",
                    "source_type": DataSourceType.NETWORK_SCANNER,
                    "provider": "nmap",
                    "version": "7.94",
                    "description": "Network discovery and port scanning"
                },
                {
                    "name": "Masscan Network Scanner",
                    "source_type": DataSourceType.NETWORK_SCANNER,
                    "provider": "masscan",
                    "version": "1.3.2",
                    "description": "High-speed network port scanner"
                },
                {
                    "name": "CrowdStrike Falcon",
                    "source_type": DataSourceType.EDR_PLATFORM,
                    "provider": "crowdstrike",
                    "version": "6.45.0",
                    "description": "Endpoint detection and response platform"
                },
                {
                    "name": "Microsoft Defender for Endpoint",
                    "source_type": DataSourceType.EDR_PLATFORM,
                    "provider": "microsoft_defender",
                    "version": "10.0.19042",
                    "description": "Microsoft's comprehensive security solution"
                },
                {
                    "name": "SentinelOne EDR",
                    "source_type": DataSourceType.EDR_PLATFORM,
                    "provider": "sentinelone",
                    "version": "22.1.2.104",
                    "description": "Advanced endpoint protection platform"
                },
                {
                    "name": "TrendMicro Vision One",
                    "source_type": DataSourceType.EDR_PLATFORM,
                    "provider": "trendmicro",
                    "version": "3.0",
                    "description": "Extended detection and response platform"
                },
                {
                    "name": "AI Device Analysis",
                    "source_type": DataSourceType.AI_ANALYSIS,
                    "provider": "llm_analyzer",
                    "version": "1.0",
                    "description": "AI-powered device identification and analysis"
                },
                {
                    "name": "User Corrections",
                    "source_type": DataSourceType.USER_CORRECTION,
                    "provider": "user_input",
                    "version": "1.0",
                    "description": "Manual user corrections and verifications"
                }
            ]
            
            for source_data in default_sources:
                source = DataSource(**source_data)
                db.add(source)
            
            db.commit()
            self.logger.info(f"Initialized {len(default_sources)} data sources")
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to initialize data sources: {e}")
            raise
        finally:
            db.close()
