from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class JournalEntry(BaseModel):
    user_id: str
    disorder_prediction: str
    journal_entry: str
    detected_markers: List[str]
    check_in_question: Optional[str] = None  # For _with_questions.csv

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
