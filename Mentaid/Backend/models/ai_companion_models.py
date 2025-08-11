from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MentalHealthCondition(str, Enum):
    SCHIZOPHRENIA = "schizophrenia"
    DEPRESSION = "depression"
    ANXIETY = "anxiety"
    SUICIDAL_THOUGHTS = "suicidal_thoughts"
    BIPOLAR = "bipolar"
    PTSD = "ptsd"
    OCD = "ocd"
    EATING_DISORDER = "eating_disorder"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ConversationType(str, Enum):
    GENERAL_SUPPORT = "general_support"
    CRISIS_INTERVENTION = "crisis_intervention"
    COPING_STRATEGIES = "coping_strategies"
    MEDICATION_REMINDER = "medication_reminder"
    THERAPY_SUPPORT = "therapy_support"

class JournalEntry(BaseModel):
    user_id: str
    entry_id: str
    entry_date: datetime
    mood_score: int = Field(..., ge=1, le=5)
    energy_level: int = Field(..., ge=1, le=6)
    sleep_hours: float = Field(..., ge=0, le=24)
    stress_level: int = Field(..., ge=1, le=5)
    anxiety_level: int = Field(..., ge=1, le=5)
    depression_level: int = Field(..., ge=1, le=5)
    content: str
    triggers: str
    coping_strategies: str
    medication_taken: str
    therapy_session: str
    risk_flags: str

class UserMentalHealthProfile(BaseModel):
    user_id: str
    primary_condition: MentalHealthCondition
    current_medication: str
    therapist: Optional[str] = None
    recent_entries: List[JournalEntry]
    risk_trend: str
    mood_trend: str
    sleep_trend: str

class AIConversationCreate(BaseModel):
    user_id: str = Field(..., description="ID of the user starting the conversation")
    condition_focus: Optional[MentalHealthCondition] = Field(None, description="Primary mental health condition to focus on")
    conversation_type: ConversationType = Field(ConversationType.GENERAL_SUPPORT, description="Type of conversation to initiate")
    initial_message: Optional[str] = Field(None, max_length=1000, description="User's initial message or concern")

class AIConversationResponse(BaseModel):
    conversation_id: str
    user_id: str
    ai_message: str
    risk_assessment: RiskLevel
    suggested_actions: List[str]
    emergency_contacts: List[str]
    next_check_in: Optional[datetime] = None
    conversation_summary: str

class CopingStrategy(BaseModel):
    condition: MentalHealthCondition
    strategy_name: str
    description: str
    effectiveness_rating: int = Field(..., ge=1, le=5)
    when_to_use: str

class CrisisIntervention(BaseModel):
    risk_level: RiskLevel
    immediate_actions: List[str]
    professional_help_required: bool
    emergency_contacts: List[str]
    follow_up_plan: str

class MentalHealthAssessment(BaseModel):
    user_id: str
    overall_risk: RiskLevel
    mood_stability: str
    sleep_quality: str
    medication_adherence: str
    therapy_engagement: str
    recommended_actions: List[str]
    next_assessment_date: datetime

class JournalAnalytics(BaseModel):
    user_id: str
    mood_trend: str
    sleep_pattern: str
    stress_triggers: List[str]
    effective_coping_strategies: List[str]
    risk_patterns: str
    improvement_areas: List[str]
    positive_progress: List[str]
