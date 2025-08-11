from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ChatTurn:
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    timestamp: datetime


@dataclass
class ConversationState:
    conversation_id: str
    user_id: str
    messages: List[ChatTurn] = field(default_factory=list)
    summary: str = ""
    suggested_followups: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)
    last_user_ts: Optional[datetime] = None
    last_assistant_ts: Optional[datetime] = None
    last_nudge_ts: Optional[datetime] = None

    def append_user(self, content: str) -> None:
        now = utc_now()
        self.messages.append(ChatTurn(role="user", content=content, timestamp=now))
        self.last_user_ts = now

    def append_assistant(self, content: str) -> None:
        now = utc_now()
        self.messages.append(ChatTurn(role="assistant", content=content, timestamp=now))
        self.last_assistant_ts = now

    def mark_nudge(self) -> None:
        self.last_nudge_ts = utc_now()


class MemoryManager:
    def __init__(self):
        self._store: Dict[str, ConversationState] = {}

    def create(self, conversation_id: str, user_id: str) -> ConversationState:
        state = ConversationState(conversation_id=conversation_id, user_id=user_id)
        self._store[conversation_id] = state
        return state

    def get(self, conversation_id: str) -> Optional[ConversationState]:
        return self._store.get(conversation_id)

    def build_context_messages(
        self, state: ConversationState, window_turns: int, include_summary: bool, system_text: Optional[str] = None
    ) -> List[Dict]:
        messages: List[Dict] = []
        if system_text:
            messages.append({"role": "system", "content": system_text})

        if include_summary and state.summary:
            messages.append({
                "role": "system",
                "content": f"Conversation summary (for context only): {state.summary}",
            })

        # Take last 'window_turns' turns (both user and assistant turns count)
        recent_turns = state.messages[-window_turns:]
        for turn in recent_turns:
            if turn.role in ("user", "assistant"):  # omit prior system entries if any
                messages.append({"role": turn.role, "content": turn.content})

        return messages

    def needs_summarization(self, state: ConversationState, threshold_turns: int) -> bool:
        return len(state.messages) >= threshold_turns


