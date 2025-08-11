from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class JournalEntry(BaseModel):
    user_id: str
    entry_id: str
    entry_date: datetime
    mood_score: int
    energy_level: int
    sleep_hours: float
    stress_level: int
    anxiety_level: int
    depression_level: int
    content: str
    triggers: str
    coping_strategies: str
    medication_taken: str
    therapy_session: str
    risk_flags: str
    question: Optional[str] = None  # For _with_questions.csv

class ChatMessage(BaseModel):
    sender: str  # 'user' or 'agent'
    message: str
    timestamp: datetime

class AgentConversation(BaseModel):
    conversation_id: str
    user_id: str
    messages: List[ChatMessage]
    context: Optional[str] = None
    llm_backend: Optional[str] = None  # 'grok' or 'gemini'
