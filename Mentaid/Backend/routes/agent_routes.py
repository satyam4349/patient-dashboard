"""
AI Agent routes for Patient Companion Agent and Clinical Assistant Agent.
"""
from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel
from typing import Dict, Optional
import logging

from services.agent_service import AgentService
from middleware.auth_middleware import (
    get_current_user_required,
    rate_limiter,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["AI Agents"])

# Initialize agent service
agent_service = AgentService()


class PatientChatRequest(BaseModel):
    message: str
    context: Optional[Dict] = None


class ClinicalAnalysisRequest(BaseModel):
    patient_id: str
    analysis_type: str = "comprehensive"  # comprehensive, risk_assessment, diagnostic


class ReportGenerationRequest(BaseModel):
    patient_id: str
    report_type: str = "soap"  # soap, progress


@router.post("/patient/chat")
async def patient_chat(
    request: Request,
    data: PatientChatRequest,
    current_user=get_current_user_required()
):
    """
    Chat with Patient Companion Agent (PCA).
    Available to patients only.
    """
    try:
        await rate_limiter.check_rate_limit(request, max_requests=100, window_seconds=3600)
        
        # Ensure only patients can use this endpoint
        if current_user.get("role") != "regular_user":
            raise HTTPException(status_code=403, detail="This endpoint is for patients only")
        
        user_id = current_user["sub"]
        result = await agent_service.patient_chat(user_id, data.message, data.context)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Chat processing failed"))
        
        # Handle crisis detection
        if result.get("status") == "crisis_detected":
            logger.warning(f"Crisis detected for user {user_id}: {data.message}")
            # TODO: Implement crisis intervention protocols
            # - Notify emergency contacts
            # - Alert clinical staff
            # - Provide crisis resources
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/patient/chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/clinical/analyze")
async def clinical_analysis(
    request: Request,
    data: ClinicalAnalysisRequest,
    current_user=get_current_user_required()
):
    """
    Get clinical analysis from Clinical Assistant Agent (CAA).
    Available to clinicians only.
    """
    try:
        await rate_limiter.check_rate_limit(request, max_requests=60, window_seconds=3600)
        
        # Ensure only clinicians can use this endpoint
        if current_user.get("role") != "clinician":
            raise HTTPException(status_code=403, detail="This endpoint is for clinicians only")
        
        result = await agent_service.clinical_analysis(data.patient_id, data.analysis_type)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Analysis failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/clinical/analyze error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/clinical/report")
async def generate_report(
    request: Request,
    data: ReportGenerationRequest,
    current_user=get_current_user_required()
):
    """
    Generate clinical report using Clinical Assistant Agent (CAA).
    Available to clinicians only.
    """
    try:
        await rate_limiter.check_rate_limit(request, max_requests=30, window_seconds=3600)
        
        # Ensure only clinicians can use this endpoint
        if current_user.get("role") != "clinician":
            raise HTTPException(status_code=403, detail="This endpoint is for clinicians only")
        
        result = await agent_service.generate_report(data.patient_id, data.report_type)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Report generation failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/clinical/report error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/clinical/patients")
async def get_patient_list(
    request: Request,
    current_user=get_current_user_required()
):
    """
    Get list of patients for the clinician.
    Available to clinicians only.
    """
    try:
        await rate_limiter.check_rate_limit(request, max_requests=60, window_seconds=3600)
        
        # Ensure only clinicians can use this endpoint
        if current_user.get("role") != "clinician":
            raise HTTPException(status_code=403, detail="This endpoint is for clinicians only")
        
        # TODO: Implement actual patient list retrieval
        # For now, return mock data
        mock_patients = [
            {
                "id": "patient_001",
                "name": "John D.",
                "last_activity": "2024-12-15T10:30:00Z",
                "risk_level": "low",
                "mood_trend": "stable",
                "engagement_score": 85
            },
            {
                "id": "patient_002", 
                "name": "Sarah M.",
                "last_activity": "2024-12-15T09:15:00Z",
                "risk_level": "medium",
                "mood_trend": "declining",
                "engagement_score": 72
            },
            {
                "id": "patient_003",
                "name": "Mike R.",
                "last_activity": "2024-12-14T16:45:00Z",
                "risk_level": "high",
                "mood_trend": "concerning",
                "engagement_score": 45
            }
        ]
        
        return {
            "status": "success",
            "patients": mock_patients,
            "total_count": len(mock_patients)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/clinical/patients error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/clinical/dashboard")
async def get_clinical_dashboard(
    request: Request,
    current_user=get_current_user_required()
):
    """
    Get clinical dashboard data with population analytics.
    Available to clinicians only.
    """
    try:
        await rate_limiter.check_rate_limit(request, max_requests=60, window_seconds=3600)
        
        # Ensure only clinicians can use this endpoint
        if current_user.get("role") != "clinician":
            raise HTTPException(status_code=403, detail="This endpoint is for clinicians only")
        
        # TODO: Implement actual dashboard data retrieval
        # For now, return mock data
        dashboard_data = {
            "overview": {
                "total_patients": 45,
                "active_patients": 38,
                "high_risk_patients": 3,
                "new_patients_this_month": 8
            },
            "engagement_metrics": {
                "daily_journal_completion": 78,
                "mood_tracking_compliance": 85,
                "session_attendance": 92
            },
            "condition_distribution": {
                "major_depressive_disorder": 18,
                "anxiety_disorders": 15,
                "bipolar_disorder": 7,
                "ptsd": 3,
                "other": 2
            },
            "recent_alerts": [
                {
                    "patient_id": "patient_003",
                    "alert_type": "high_risk",
                    "message": "Patient showing concerning mood decline",
                    "timestamp": "2024-12-15T08:30:00Z"
                },
                {
                    "patient_id": "patient_007",
                    "alert_type": "missed_session",
                    "message": "Patient missed scheduled appointment",
                    "timestamp": "2024-12-14T14:00:00Z"
                }
            ]
        }
        
        return {
            "status": "success",
            "dashboard": dashboard_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/clinical/dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")