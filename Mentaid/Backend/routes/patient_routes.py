"""
Patient routes: mood, journal, history.
"""
from fastapi import APIRouter, HTTPException, status, Request, Depends, Query
from typing import Dict
import logging
from datetime import datetime

from models.patient_models import (
    MoodCreate, 
    JournalCreate, 
    HistoryQuery,
    ConnectionRequest,
    ConnectionResponse,
    PrivacySettingsUpdate
)
from services.patient_service import PatientService
from services.analytics_service import AnalyticsService
from middleware.auth_middleware import (
    get_current_user_required,
    require_any_authenticated_user,
    rate_limiter,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patient", tags=["Patient"])


@router.post("/mood")
async def save_mood(request: Request, data: MoodCreate, current_user=get_current_user_required()):
    try:
        await rate_limiter.check_rate_limit(request, max_requests=60, window_seconds=3600)
        user_id = current_user["sub"]
        result = await PatientService.save_mood(user_id, data)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/mood error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/journal")
async def save_journal(request: Request, data: JournalCreate, current_user=get_current_user_required()):
    try:
        await rate_limiter.check_rate_limit(request, max_requests=60, window_seconds=3600)
        user_id = current_user["sub"]
        result = await PatientService.save_journal(user_id, data)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/journal error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history")
async def get_history(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = Query(None),
    current_user=get_current_user_required(),
):
    try:
        await rate_limiter.check_rate_limit(request, max_requests=120, window_seconds=3600)
        user_id = current_user["sub"]
        query = HistoryQuery(limit=limit, cursor=cursor)
        result = await PatientService.get_history(user_id, query)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/history error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/entry-by-date")
async def get_entry_by_date(
    request: Request,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    current_user=get_current_user_required(),
):
    try:
        await rate_limiter.check_rate_limit(request, max_requests=120, window_seconds=3600)
        user_id = current_user["sub"]
        result = await PatientService.get_entry_by_date(user_id, date)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/entry-by-date error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/today-entry")
async def get_today_entry(
    request: Request,
    current_user=get_current_user_required(),
):
    """Get today's journal and mood entries for editing."""
    try:
        await rate_limiter.check_rate_limit(request, max_requests=120, window_seconds=3600)
        user_id = current_user["sub"]
        today = datetime.now().strftime("%Y-%m-%d")
        result = await PatientService.get_entry_by_date(user_id, today)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/today-entry error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/today-journal")
async def save_today_journal(
    request: Request, 
    data: JournalCreate, 
    current_user=get_current_user_required()
):
    """Save or update today's journal entry."""
    try:
        await rate_limiter.check_rate_limit(request, max_requests=60, window_seconds=3600)
        user_id = current_user["sub"]
        result = await PatientService.save_or_update_journal(user_id, data)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/today-journal error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/today-mood")
async def save_today_mood(
    request: Request, 
    data: MoodCreate, 
    current_user=get_current_user_required()
):
    """Save or update today's mood entry."""
    try:
        await rate_limiter.check_rate_limit(request, max_requests=60, window_seconds=3600)
        user_id = current_user["sub"]
        result = await PatientService.save_or_update_mood(user_id, data)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/today-mood error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics")
async def get_analytics(
    request: Request,
    range: str = Query("Last 30 days", description="Time range for analytics"),
    current_user=get_current_user_required(),
):
    try:
        await rate_limiter.check_rate_limit(request, max_requests=60, window_seconds=3600)
        user_id = current_user["sub"]
        result = await AnalyticsService.get_comprehensive_analytics(user_id, range)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/analytics error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ---------------------- Clinician Connection Routes ----------------------

@router.get("/connection-code")
async def get_connection_code(
    request: Request,
    current_user=get_current_user_required(),
):
    """Get user's unique connection code for clinician connections."""
    try:
        await rate_limiter.check_rate_limit(request, max_requests=60, window_seconds=3600)
        user_id = current_user["sub"]
        result = await PatientService.get_user_connection_code(user_id)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/connection-code error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/connection-request")
async def create_connection_request(
    request: Request,
    data: ConnectionRequest,
    current_user=get_current_user_required(),
):
    """Create a connection request from clinician to patient."""
    try:
        await rate_limiter.check_rate_limit(request, max_requests=30, window_seconds=3600)
        clinician_id = current_user["sub"]
        
        # Verify user is a clinician
        if current_user.get("role") != "clinician":
            raise HTTPException(status_code=403, detail="Only clinicians can create connection requests")
        
        result = await PatientService.create_connection_request(
            clinician_id, 
            data.patient_connection_code, 
            data.patient_email
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/connection-request error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/connections")
async def get_connections(
    request: Request,
    current_user=get_current_user_required(),
):
    """Get connection requests for current user."""
    try:
        await rate_limiter.check_rate_limit(request, max_requests=60, window_seconds=3600)
        user_id = current_user["sub"]
        user_role = current_user.get("role", "regular_user")
        result = await PatientService.get_connection_requests(user_id, user_role)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/connections error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/connection/{connection_id}/respond")
async def respond_to_connection(
    request: Request,
    connection_id: str,
    data: ConnectionResponse,
    current_user=get_current_user_required(),
):
    """Respond to a connection request (patient only)."""
    try:
        await rate_limiter.check_rate_limit(request, max_requests=30, window_seconds=3600)
        patient_id = current_user["sub"]
        
        # Verify user is a patient
        if current_user.get("role") != "regular_user":
            raise HTTPException(status_code=403, detail="Only patients can respond to connection requests")
        
        result = await PatientService.respond_to_connection_request(
            connection_id, 
            patient_id, 
            data.action
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/connection/{connection_id}/respond error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ---------------------- Privacy Settings Routes ----------------------

@router.get("/privacy-settings")
async def get_privacy_settings(
    request: Request,
    current_user=get_current_user_required(),
):
    """Get user's privacy settings."""
    try:
        await rate_limiter.check_rate_limit(request, max_requests=60, window_seconds=3600)
        user_id = current_user["sub"]
        result = await PatientService.get_privacy_settings(user_id)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/privacy-settings error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/privacy-settings")
async def update_privacy_settings(
    request: Request,
    data: PrivacySettingsUpdate,
    current_user=get_current_user_required(),
):
    """Update user's privacy settings."""
    try:
        await rate_limiter.check_rate_limit(request, max_requests=30, window_seconds=3600)
        user_id = current_user["sub"]
        
        # Convert Pydantic model to dict, excluding None values
        settings_dict = {k: v for k, v in data.dict().items() if v is not None}
        
        result = await PatientService.update_privacy_settings(user_id, settings_dict)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/privacy-settings PUT error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
