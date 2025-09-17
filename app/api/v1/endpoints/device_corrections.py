"""
Device correction API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime

from app.auth.auth_service import AuthService
from app.services.device_correction_service import DeviceCorrectionService

router = APIRouter()
auth_service = AuthService()
correction_service = DeviceCorrectionService()


class DeviceCorrectionRequest(BaseModel):
    corrected_device_type: str = Field(..., description="Corrected device type")
    corrected_operating_system: str = Field(..., description="Corrected operating system")
    correction_reason: str = Field(..., description="Reason for correction")
    additional_tags: Optional[List[str]] = Field(default=None, description="Additional tags to add")


class DeviceFeedbackRequest(BaseModel):
    feedback_type: str = Field(..., description="Type of feedback: accurate, inaccurate, partially_accurate")
    accuracy_score: float = Field(..., ge=0.0, le=1.0, description="Accuracy score from 0.0 to 1.0")
    device_type_accurate: Optional[bool] = Field(default=None, description="Was device type accurate?")
    os_accurate: Optional[bool] = Field(default=None, description="Was OS accurate?")
    services_accurate: Optional[bool] = Field(default=None, description="Were services accurate?")
    feedback_comment: Optional[str] = Field(default=None, description="Additional feedback comments")
    suggestions: Optional[str] = Field(default=None, description="Suggestions for improvement")


class CorrectionVerificationRequest(BaseModel):
    feedback_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Feedback score for correction quality")


@router.post("/{device_id}/correct")
async def correct_device(
    device_id: str,
    request: DeviceCorrectionRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Correct device identification"""
    try:
        result = await correction_service.correct_device(
            device_id=device_id,
            user_id=token.get("user_id"),
            corrected_device_type=request.corrected_device_type,
            corrected_os=request.corrected_operating_system,
            correction_reason=request.correction_reason,
            additional_tags=request.additional_tags
        )
        
        return {
            "message": "Device correction applied successfully",
            "correction": result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to correct device: {str(e)}"
        )


@router.get("/{device_id}/corrections")
async def get_device_corrections(
    device_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Get correction history for a device"""
    try:
        corrections = await correction_service.get_device_corrections(device_id)
        return {
            "device_id": device_id,
            "corrections": corrections,
            "total_corrections": len(corrections)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get device corrections: {str(e)}"
        )


@router.post("/{device_id}/feedback")
async def submit_device_feedback(
    device_id: str,
    request: DeviceFeedbackRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Submit feedback on device identification"""
    try:
        result = await correction_service.submit_feedback(
            device_id=device_id,
            user_id=token.get("user_id"),
            feedback_type=request.feedback_type,
            accuracy_score=request.accuracy_score,
            device_type_accurate=request.device_type_accurate,
            os_accurate=request.os_accurate,
            services_accurate=request.services_accurate,
            comment=request.feedback_comment,
            suggestions=request.suggestions
        )
        
        return {
            "message": "Feedback submitted successfully",
            "feedback": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.post("/corrections/{correction_id}/verify")
async def verify_correction(
    correction_id: str,
    request: CorrectionVerificationRequest,
    token: str = Depends(auth_service.verify_token)
):
    """Verify a device correction (admin only)"""
    try:
        success = await correction_service.verify_correction(
            correction_id=correction_id,
            verifier_id=token.get("user_id"),
            feedback_score=request.feedback_score
        )
        
        if success:
            return {"message": "Correction verified successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Correction not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify correction: {str(e)}"
        )


@router.get("/patterns")
async def get_correction_patterns(
    pattern_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    token: str = Depends(auth_service.verify_token)
):
    """Get learned correction patterns"""
    try:
        patterns = await correction_service.get_correction_patterns(pattern_type)
        
        # Apply pagination
        paginated_patterns = patterns[offset:offset + limit]
        
        return {
            "patterns": paginated_patterns,
            "total_patterns": len(patterns),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get correction patterns: {str(e)}"
        )


@router.post("/{device_id}/apply-patterns")
async def apply_patterns_to_device(
    device_id: str,
    token: str = Depends(auth_service.verify_token)
):
    """Apply learned patterns to improve device identification"""
    try:
        # Get device from database
        from app.core.database import SessionLocal
        from app.models.device import Device
        
        db = SessionLocal()
        try:
            device = db.query(Device).filter(Device.id == device_id).first()
            if not device:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Device not found"
                )
            
            result = await correction_service.apply_patterns_to_device(device)
            return result
            
        finally:
            db.close()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply patterns: {str(e)}"
        )


@router.get("/stats/corrections")
async def get_correction_stats(
    token: str = Depends(auth_service.verify_token)
):
    """Get correction statistics"""
    try:
        from app.core.database import SessionLocal
        from app.models.device_correction import DeviceCorrection, CorrectionPattern
        
        db = SessionLocal()
        try:
            # Get correction statistics
            total_corrections = db.query(DeviceCorrection).count()
            verified_corrections = db.query(DeviceCorrection).filter(
                DeviceCorrection.is_verified == True
            ).count()
            
            # Get pattern statistics
            total_patterns = db.query(CorrectionPattern).filter(
                CorrectionPattern.is_active == True
            ).count()
            
            # Get recent corrections
            recent_corrections = db.query(DeviceCorrection).order_by(
                DeviceCorrection.created_at.desc()
            ).limit(10).all()
            
            return {
                "total_corrections": total_corrections,
                "verified_corrections": verified_corrections,
                "verification_rate": verified_corrections / total_corrections if total_corrections > 0 else 0,
                "total_patterns": total_patterns,
                "recent_corrections": [
                    {
                        "id": str(correction.id),
                        "device_id": str(correction.device_id),
                        "original_type": correction.original_device_type,
                        "corrected_type": correction.corrected_device_type,
                        "created_at": correction.created_at.isoformat(),
                        "is_verified": correction.is_verified
                    }
                    for correction in recent_corrections
                ]
            }
            
        finally:
            db.close()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get correction stats: {str(e)}"
        )
