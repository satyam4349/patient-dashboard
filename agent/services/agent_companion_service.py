import uuid
from datetime import datetime
from typing import List, Optional

from models.agent_companion_models import AgentConversation, ChatMessage
from services.journal_data_service import JournalDataService
from services.llm_service import LLMService

class AgentCompanionService:
    def __init__(self):
        self.journal_service = JournalDataService()
        self.llm_service = LLMService()
        self.conversations = {}  # conversation_id -> AgentConversation

    def start_conversation(self, user_id: str, initial_message: str, llm_backend: str = "groq") -> AgentConversation:
        conversation_id = str(uuid.uuid4())
        now = datetime.utcnow()
        messages = [
            ChatMessage(sender="user", message=initial_message, timestamp=now)
        ]
        journal_entries = self.journal_service.get_entries_for_user(user_id)
        context = self._build_context(journal_entries)
        prompt = self._build_prompt(initial_message, context)
        ai_response = self.llm_service.query(prompt, backend=llm_backend)
        messages.append(ChatMessage(sender="agent", message=ai_response, timestamp=datetime.utcnow()))
        conversation = AgentConversation(
            conversation_id=conversation_id,
            user_id=user_id,
            messages=messages,
            context=context,
            llm_backend=llm_backend
        )
        self.conversations[conversation_id] = conversation
        return conversation

    def continue_conversation(self, conversation_id: str, user_message: str) -> Optional[AgentConversation]:
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return None
        now = datetime.utcnow()
        conversation.messages.append(ChatMessage(sender="user", message=user_message, timestamp=now))
        context = conversation.context
        prompt = self._build_prompt(user_message, context)
        ai_response = self.llm_service.query(prompt, backend=conversation.llm_backend)
        conversation.messages.append(ChatMessage(sender="agent", message=ai_response, timestamp=datetime.utcnow()))
        return conversation

    def _build_context(self, journal_entries: List) -> str:
        if not journal_entries:
            return ""
        recent = journal_entries[-3:]  # Get last 3 entries
        context_lines = []
        for entry in recent:
            markers_str = ", ".join(entry.detected_markers) if entry.detected_markers else "None"
            context_lines.append(
                f"Disorder: {entry.disorder_prediction}, Entry: {entry.journal_entry[:100]}..., Markers: {markers_str}"
            )
        return " | ".join(context_lines)

    def _build_prompt(self, user_message: str, context: str) -> str:
        system_prompt = """You are a compassionate AI mental health companion. Your role is to:
1. Provide empathetic, supportive responses
2. Use the user's journal context to personalize your responses
3. Offer practical coping strategies when appropriate
4. Encourage professional help when needed
5. Never provide medical diagnoses or replace professional therapy

Be warm, understanding, and helpful while maintaining appropriate boundaries."""
        
        if context:
            return f"""{system_prompt}

User's recent journal context: {context}

User: {user_message}

Respond as a caring mental health companion:"""
        else:
            return f"""{system_prompt}

User: {user_message}

Respond as a caring mental health companion:"""

    def get_conversation(self, conversation_id: str) -> Optional[AgentConversation]:
        return self.conversations.get(conversation_id)
