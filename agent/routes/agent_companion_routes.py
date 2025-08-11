from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.agent_companion_service import AgentCompanionService

router = APIRouter(prefix="/agent-companion", tags=["Agent Companion"])
agent_service = AgentCompanionService()

class StartConversationRequest(BaseModel):
    user_id: str
    initial_message: str
    llm_backend: Optional[str] = "grok"  # or "gemini"

class ContinueConversationRequest(BaseModel):
    conversation_id: str
    user_message: str

@router.post("/start")
def start_conversation(request: StartConversationRequest):
    conversation = agent_service.start_conversation(
        user_id=request.user_id,
        initial_message=request.initial_message,
        llm_backend=request.llm_backend
    )
    return conversation

@router.post("/continue")
def continue_conversation(request: ContinueConversationRequest):
    conversation = agent_service.continue_conversation(
        conversation_id=request.conversation_id,
        user_message=request.user_message
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.get("/conversation/{conversation_id}")
def get_conversation(conversation_id: str):
    conversation = agent_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation
