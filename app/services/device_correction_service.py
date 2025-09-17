"""
Device correction service for handling mis-identifications and learning
"""
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from app.models.device_correction import DeviceCorrection, CorrectionPattern, DeviceFeedback
from app.models.device import Device
from app.models.user import User
from app.core.database import SessionLocal


class DeviceCorrectionService:
    """Service for managing device corrections and learning patterns"""
    
    def __init__(self):
        self.logger = logging.getLogger("services.device_correction")
    
    async def correct_device(self, device_id: str, user_id: str, 
                           corrected_device_type: str, corrected_os: str,
                           correction_reason: str, additional_tags: List[str] = None) -> Dict[str, Any]:
        """Correct device identification"""
        db = SessionLocal()
        try:
            # Get device
            device = db.query(Device).filter(Device.id == device_id).first()
            if not device:
                raise ValueError("Device not found")
            
            # Store original values
            original_device_type = device.device_type
            original_os = device.operating_system
            original_confidence = device.confidence
            original_reasoning = device.ai_analysis.get("reasoning", "") if device.ai_analysis else ""
            
            # Create correction record
            correction = DeviceCorrection(
                device_id=device_id,
                user_id=user_id,
                original_device_type=original_device_type,
                original_operating_system=original_os,
                original_confidence=original_confidence,
                original_reasoning=original_reasoning,
                corrected_device_type=corrected_device_type,
                corrected_operating_system=corrected_os,
                correction_reason=correction_reason,
                scan_data_snapshot=device.scan_results,
                correction_tags=additional_tags or []
            )
            
            db.add(correction)
            
            # Update device with corrected information
            device.device_type = corrected_device_type
            device.operating_system = corrected_os
            device.confidence = 1.0  # Human corrections have 100% confidence
            device.updated_at = datetime.now()
            
            # Add correction tags
            if additional_tags:
                device.tags.extend(additional_tags)
                device.tags = list(set(device.tags))  # Remove duplicates
            
            db.commit()
            
            # Extract patterns for learning
            await self._extract_patterns(correction, device.scan_results)
            
            self.logger.info(f"Device {device.ip} corrected by user {user_id}: {original_device_type} -> {corrected_device_type}")
            
            return {
                "correction_id": str(correction.id),
                "device_id": device_id,
                "original": {
                    "device_type": original_device_type,
                    "operating_system": original_os,
                    "confidence": original_confidence
                },
                "corrected": {
                    "device_type": corrected_device_type,
                    "operating_system": corrected_os,
                    "confidence": 1.0
                },
                "reason": correction_reason,
                "applied_at": correction.created_at.isoformat()
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to correct device {device_id}: {e}")
            raise
        finally:
            db.close()
    
    async def get_device_corrections(self, device_id: str) -> List[Dict[str, Any]]:
        """Get correction history for a device"""
        db = SessionLocal()
        try:
            corrections = db.query(DeviceCorrection).filter(
                DeviceCorrection.device_id == device_id
            ).order_by(DeviceCorrection.created_at.desc()).all()
            
            return [
                {
                    "id": str(correction.id),
                    "user_id": str(correction.user_id),
                    "original": {
                        "device_type": correction.original_device_type,
                        "operating_system": correction.original_operating_system,
                        "confidence": correction.original_confidence
                    },
                    "corrected": {
                        "device_type": correction.corrected_device_type,
                        "operating_system": correction.corrected_operating_system
                    },
                    "reason": correction.correction_reason,
                    "applied_at": correction.created_at.isoformat(),
                    "is_verified": correction.is_verified,
                    "verified_by": str(correction.verified_by) if correction.verified_by else None
                }
                for correction in corrections
            ]
            
        finally:
            db.close()
    
    async def verify_correction(self, correction_id: str, verifier_id: str, 
                              feedback_score: float = None) -> bool:
        """Verify a device correction"""
        db = SessionLocal()
        try:
            correction = db.query(DeviceCorrection).filter(
                DeviceCorrection.id == correction_id
            ).first()
            
            if not correction:
                return False
            
            correction.is_verified = True
            correction.verified_by = verifier_id
            correction.verified_at = datetime.now()
            
            if feedback_score is not None:
                correction.feedback_score = feedback_score
            
            db.commit()
            
            self.logger.info(f"Correction {correction_id} verified by {verifier_id}")
            return True
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to verify correction {correction_id}: {e}")
            return False
        finally:
            db.close()
    
    async def submit_feedback(self, device_id: str, user_id: str, 
                            feedback_type: str, accuracy_score: float,
                            device_type_accurate: bool = None, os_accurate: bool = None,
                            services_accurate: bool = None, comment: str = None,
                            suggestions: str = None) -> Dict[str, Any]:
        """Submit feedback on device identification"""
        db = SessionLocal()
        try:
            feedback = DeviceFeedback(
                device_id=device_id,
                user_id=user_id,
                feedback_type=feedback_type,
                accuracy_score=accuracy_score,
                device_type_accurate=device_type_accurate,
                os_accurate=os_accurate,
                services_accurate=services_accurate,
                feedback_comment=comment,
                suggestions=suggestions
            )
            
            db.add(feedback)
            db.commit()
            
            self.logger.info(f"Feedback submitted for device {device_id} by user {user_id}")
            
            return {
                "feedback_id": str(feedback.id),
                "device_id": device_id,
                "feedback_type": feedback_type,
                "accuracy_score": accuracy_score,
                "submitted_at": feedback.created_at.isoformat()
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to submit feedback for device {device_id}: {e}")
            raise
        finally:
            db.close()
    
    async def get_correction_patterns(self, pattern_type: str = None) -> List[Dict[str, Any]]:
        """Get learned correction patterns"""
        db = SessionLocal()
        try:
            query = db.query(CorrectionPattern).filter(CorrectionPattern.is_active == True)
            
            if pattern_type:
                query = query.filter(CorrectionPattern.pattern_type == pattern_type)
            
            patterns = query.order_by(CorrectionPattern.confidence_score.desc()).all()
            
            return [
                {
                    "id": str(pattern.id),
                    "pattern_type": pattern.pattern_type,
                    "pattern_key": pattern.pattern_key,
                    "pattern_value": pattern.pattern_value,
                    "correct_device_type": pattern.correct_device_type,
                    "correct_operating_system": pattern.correct_operating_system,
                    "confidence_score": pattern.confidence_score,
                    "usage_count": pattern.usage_count,
                    "success_rate": pattern.success_rate,
                    "created_at": pattern.created_at.isoformat(),
                    "last_used": pattern.last_used.isoformat() if pattern.last_used else None
                }
                for pattern in patterns
            ]
            
        finally:
            db.close()
    
    async def apply_patterns_to_device(self, device: Device) -> Dict[str, Any]:
        """Apply learned patterns to improve device identification"""
        db = SessionLocal()
        try:
            applied_patterns = []
            
            # Extract patterns from device data
            services = self._extract_services_from_device(device)
            banners = self._extract_banners_from_device(device)
            ports = self._extract_ports_from_device(device)
            
            # Check service patterns
            for service in services:
                pattern = db.query(CorrectionPattern).filter(
                    CorrectionPattern.pattern_type == "service_pattern",
                    CorrectionPattern.pattern_key == service.get("service", ""),
                    CorrectionPattern.is_active == True
                ).first()
                
                if pattern:
                    applied_patterns.append({
                        "type": "service_pattern",
                        "pattern": service.get("service", ""),
                        "suggested_device_type": pattern.correct_device_type,
                        "suggested_os": pattern.correct_operating_system,
                        "confidence": pattern.confidence_score
                    })
                    
                    # Update usage count
                    pattern.usage_count += 1
                    pattern.last_used = datetime.now()
            
            # Check banner patterns
            for banner in banners:
                pattern = db.query(CorrectionPattern).filter(
                    CorrectionPattern.pattern_type == "banner_pattern",
                    CorrectionPattern.pattern_key.like(f"%{banner}%"),
                    CorrectionPattern.is_active == True
                ).first()
                
                if pattern:
                    applied_patterns.append({
                        "type": "banner_pattern",
                        "pattern": banner,
                        "suggested_device_type": pattern.correct_device_type,
                        "suggested_os": pattern.correct_operating_system,
                        "confidence": pattern.confidence_score
                    })
            
            db.commit()
            
            return {
                "device_id": str(device.id),
                "applied_patterns": applied_patterns,
                "pattern_count": len(applied_patterns)
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to apply patterns to device {device.id}: {e}")
            return {"device_id": str(device.id), "applied_patterns": [], "pattern_count": 0}
        finally:
            db.close()
    
    async def _extract_patterns(self, correction: DeviceCorrection, scan_data: Dict[str, Any]):
        """Extract patterns from correction for future learning"""
        db = SessionLocal()
        try:
            # Extract service patterns
            services = self._extract_services_from_scan_data(scan_data)
            for service in services:
                pattern_key = service.get("service", "")
                if pattern_key:
                    await self._create_or_update_pattern(
                        db, "service_pattern", pattern_key, service.get("version", ""),
                        correction.corrected_device_type, correction.corrected_operating_system
                    )
            
            # Extract banner patterns
            banners = self._extract_banners_from_scan_data(scan_data)
            for banner in banners:
                if banner:
                    await self._create_or_update_pattern(
                        db, "banner_pattern", banner, "",
                        correction.corrected_device_type, correction.corrected_operating_system
                    )
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Failed to extract patterns from correction: {e}")
        finally:
            db.close()
    
    async def _create_or_update_pattern(self, db, pattern_type: str, pattern_key: str, 
                                      pattern_value: str, device_type: str, os: str):
        """Create or update a correction pattern"""
        pattern = db.query(CorrectionPattern).filter(
            CorrectionPattern.pattern_type == pattern_type,
            CorrectionPattern.pattern_key == pattern_key,
            CorrectionPattern.correct_device_type == device_type,
            CorrectionPattern.correct_operating_system == os
        ).first()
        
        if pattern:
            # Update existing pattern
            pattern.usage_count += 1
            pattern.success_rate = (pattern.success_rate * (pattern.usage_count - 1) + 1.0) / pattern.usage_count
            pattern.confidence_score = min(pattern.confidence_score + 0.1, 1.0)
            pattern.updated_at = datetime.now()
        else:
            # Create new pattern
            pattern = CorrectionPattern(
                pattern_type=pattern_type,
                pattern_key=pattern_key,
                pattern_value=pattern_value,
                correct_device_type=device_type,
                correct_operating_system=os,
                confidence_score=0.8,  # Start with high confidence for human corrections
                usage_count=1,
                success_rate=1.0
            )
            db.add(pattern)
    
    def _extract_services_from_device(self, device: Device) -> List[Dict[str, Any]]:
        """Extract services from device scan results"""
        services = []
        for scanner, host_info in device.scan_results.items():
            host_services = host_info.get("services", [])
            services.extend(host_services)
        return services
    
    def _extract_banners_from_device(self, device: Device) -> List[str]:
        """Extract banners from device scan results"""
        banners = []
        for scanner, host_info in device.scan_results.items():
            ports = host_info.get("ports", {})
            for port_info in ports.values():
                if port_info.get("extrainfo"):
                    banners.append(port_info["extrainfo"])
        return banners
    
    def _extract_ports_from_device(self, device: Device) -> List[int]:
        """Extract open ports from device scan results"""
        ports = []
        for scanner, host_info in device.scan_results.items():
            port_data = host_info.get("ports", {})
            for port_num, port_info in port_data.items():
                if port_info.get("state") == "open":
                    ports.append(int(port_num))
        return ports
    
    def _extract_services_from_scan_data(self, scan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract services from scan data"""
        services = []
        hosts = scan_data.get("hosts", {})
        for host_info in hosts.values():
            host_services = host_info.get("services", [])
            services.extend(host_services)
        return services
    
    def _extract_banners_from_scan_data(self, scan_data: Dict[str, Any]) -> List[str]:
        """Extract banners from scan data"""
        banners = []
        hosts = scan_data.get("hosts", {})
        for host_info in hosts.values():
            ports = host_info.get("ports", {})
            for port_info in ports.values():
                if port_info.get("extrainfo"):
                    banners.append(port_info["extrainfo"])
        return banners
