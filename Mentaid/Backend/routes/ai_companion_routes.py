from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from models.ai_companion_models import (
    AIConversationCreate, AIConversationResponse, MentalHealthCondition,
    RiskLevel, CopingStrategy, CrisisIntervention, UserMentalHealthProfile,
    JournalAnalytics, MentalHealthAssessment
)
from services.ai_companion_service import AICompanionService
from services.journal_data_service import JournalDataService
from middleware.auth_middleware import get_current_user
from models.user_models import TokenData

router = APIRouter(prefix="/ai-companion", tags=["AI Companion"])
ai_service = AICompanionService()
journal_service = JournalDataService()

@router.post("/conversations", response_model=AIConversationResponse)
async def start_conversation(
    request: AIConversationCreate,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Start a new AI conversation with personalized context based on journal data
    """
    try:
        response = ai_service.start_conversation(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start conversation: {str(e)}")

@router.post("/conversations/{conversation_id}/messages", response_model=AIConversationResponse)
async def send_message(
    conversation_id: str,
    message: str = Query(..., description="User's message"),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Send a message in an existing conversation and get AI response
    """
    try:
        response = ai_service.continue_conversation(conversation_id, message)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.get("/conversations/{conversation_id}", response_model=AIConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get conversation details and current status
    """
    try:
        if conversation_id not in ai_service.conversations:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation = ai_service.conversations[conversation_id]
        user_id = conversation["user_id"]
        
        # Get current user profile and analytics
        profile = journal_service.get_user_profile(user_id)
        analytics = journal_service.get_user_analytics(user_id)
        
        # Create response with current data
        response = AIConversationResponse(
            conversation_id=conversation_id,
            user_id=user_id,
            ai_message="Conversation retrieved successfully",
            risk_assessment=conversation["risk_level"],
            suggested_actions=ai_service._get_suggested_actions(
                profile, conversation["risk_level"], analytics
            ),
            emergency_contacts=ai_service._get_emergency_contacts(
                conversation["risk_level"], profile
            ),
            next_check_in=ai_service._calculate_next_checkin(conversation["risk_level"]),
            conversation_summary=f"Current conversation - Risk: {conversation['risk_level'].value}"
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation: {str(e)}")

@router.get("/user/{user_id}/profile", response_model=UserMentalHealthProfile)
async def get_user_profile(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get comprehensive mental health profile for a user based on journal data
    """
    try:
        profile = journal_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profile: {str(e)}")

@router.get("/user/{user_id}/analytics", response_model=JournalAnalytics)
async def get_user_analytics(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get comprehensive analytics for a user based on journal entries
    """
    try:
        analytics = journal_service.get_user_analytics(user_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="User analytics not found")
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")

@router.get("/user/{user_id}/assessment", response_model=MentalHealthAssessment)
async def get_mental_health_assessment(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get comprehensive mental health assessment for a user
    """
    try:
        # Get user insights from AI service
        insights = ai_service.get_user_insights(user_id)
        
        if not insights["profile"]:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Create assessment
        assessment = MentalHealthAssessment(
            user_id=user_id,
            overall_risk=insights["profile"]["risk_trend"],
            mood_stability=insights["analytics"]["mood_trend"] if insights["analytics"] else "unknown",
            sleep_quality=insights["analytics"]["sleep_pattern"] if insights["analytics"] else "unknown",
            medication_adherence=f"{insights['medication_adherence']['adherence_rate']}%",
            therapy_engagement="Active" if insights["profile"]["therapist"] else "Not engaged",
            recommended_actions=ai_service._get_suggested_actions(
                insights["profile"], 
                RiskLevel.MEDIUM,  # Default risk level for assessment
                insights["analytics"]
            ),
            next_assessment_date=ai_service._calculate_next_checkin(RiskLevel.MEDIUM)
        )
        
        return assessment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create assessment: {str(e)}")

@router.get("/coping-strategies/{condition}", response_model=List[CopingStrategy])
async def get_coping_strategies(
    condition: MentalHealthCondition,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get coping strategies for a specific mental health condition
    """
    try:
        strategies = ai_service.get_coping_strategies(condition)
        return strategies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve coping strategies: {str(e)}")

@router.get("/crisis-intervention/{risk_level}", response_model=CrisisIntervention)
async def get_crisis_intervention(
    risk_level: RiskLevel,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get crisis intervention protocol for a specific risk level
    """
    try:
        intervention = ai_service.get_crisis_intervention(risk_level)
        if not intervention:
            raise HTTPException(status_code=404, detail="Crisis intervention not found")
        return intervention
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve crisis intervention: {str(e)}")

@router.get("/journal-data/summary")
async def get_journal_data_summary(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get summary of journal data across all users (for clinicians)
    """
    try:
        summary = {
            "total_users": len(journal_service.user_profiles),
            "total_entries": len(journal_service.journal_data),
            "high_risk_users": journal_service.get_high_risk_users(),
            "condition_distribution": {},
            "recent_activity": {}
        }
        
        # Count users by condition
        for user_id, profile in journal_service.user_profiles.items():
            condition = profile.primary_condition.value
            summary["condition_distribution"][condition] = summary["condition_distribution"].get(condition, 0) + 1
        
        # Get recent activity (last 7 days)
        for user_id in journal_service.user_profiles:
            recent_entries = journal_service.get_recent_entries(user_id, days=7)
            summary["recent_activity"][user_id] = len(recent_entries)
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve summary: {str(e)}")

@router.get("/journal-data/user/{user_id}/recent")
async def get_user_recent_entries(
    user_id: str,
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get recent journal entries for a specific user
    """
    try:
        entries = journal_service.get_recent_entries(user_id, days)
        return {
            "user_id": user_id,
            "days_requested": days,
            "entries_found": len(entries),
            "entries": [entry.dict() for entry in entries]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve entries: {str(e)}")

@router.get("/journal-data/condition/{condition}")
async def get_condition_data(
    condition: MentalHealthCondition,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get journal data for users with a specific mental health condition
    """
    try:
        entries = journal_service.get_condition_specific_data(condition)
        return {
            "condition": condition.value,
            "total_entries": len(entries),
            "unique_users": len(set(entry.user_id for entry in entries)),
            "sample_entries": [entry.dict() for entry in entries[:5]]  # First 5 entries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve condition data: {str(e)}")

@router.get("/medication-adherence/{user_id}")
async def get_medication_adherence(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get medication adherence statistics for a user
    """
    try:
        adherence = journal_service.get_medication_adherence(user_id)
        return adherence
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve adherence data: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the AI companion service
    """
    try:
        # Check if journal data is loaded
        data_loaded = len(journal_service.journal_data) > 0
        profiles_created = len(journal_service.user_profiles) > 0
        
        return {
            "status": "healthy",
            "journal_data_loaded": data_loaded,
            "user_profiles_created": profiles_created,
            "total_journal_entries": len(journal_service.journal_data),
            "total_user_profiles": len(journal_service.user_profiles),
            "ai_service_ready": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
