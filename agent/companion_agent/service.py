import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from .config import CONFIG
from .llm import LLMClient
from .memory import MemoryManager, ConversationState
from . import prompts
from .tool_router import route_if_needed
from .tools import safe_calculate, NotesStore


class CompanionService:
    """High-level orchestrator for the Companion Agent."""

    def __init__(self):
        self.llm = LLMClient(CONFIG)
        self.memory = MemoryManager()
        self._notes = NotesStore()

    def start_conversation(self, user_id: str, initial_message: str) -> ConversationState:
        conversation_id = str(uuid.uuid4())
        state = self.memory.create(conversation_id, user_id)
        state.append_user(initial_message)

        # Optional: immediate summarization if long introduction (rare)
        self._maybe_update_summary(state)

        assistant_reply = self._generate_reply(state)
        state.append_assistant(assistant_reply)
        state.suggested_followups = self._generate_followups(state)
        return state

    def continue_conversation(self, conversation_id: str, user_message: str) -> Optional[ConversationState]:
        state = self.memory.get(conversation_id)
        if not state:
            return None

        # Tool routing (simple heuristics)
        invocation = route_if_needed(user_message)
        tool_result: Optional[str] = None
        if invocation:
            if invocation.name == "calculator":
                tool_result = safe_calculate(invocation.args.get("expression", ""))
            elif invocation.name == "notes.add":
                text = invocation.args.get("text", "").strip()
                if text:
                    self._notes.add(conversation_id, text)
                    tool_result = "Saved your note."

        # Append user message (include tool result info if any)
        if tool_result:
            user_message = f"{user_message}\n\n(Tool result: {tool_result})"
        state.append_user(user_message)

        self._maybe_update_summary(state)

        assistant_reply = self._generate_reply(state)
        state.append_assistant(assistant_reply)
        state.suggested_followups = self._generate_followups(state)
        return state

    def _generate_reply(self, state: ConversationState) -> str:
        messages = self.memory.build_context_messages(
            state,
            window_turns=CONFIG.window_turns,
            include_summary=True,
            system_text=prompts.system_prompt(),
        )
        return self.llm.generate(messages)

    def _generate_followups(self, state: ConversationState):
        # Use a small context snippet from the latest user and assistant turns
        recent_texts = [turn.content for turn in state.messages[-4:]]
        snippet = "\n".join(recent_texts)[-800:]
        return self.llm.suggest_followups(snippet)

    def _maybe_update_summary(self, state: ConversationState) -> None:
        if self.memory.needs_summarization(state, CONFIG.summary_trigger_turns):
            # Build a plain transcript for summarization
            pairs = []
            for turn in state.messages[-(CONFIG.summary_trigger_turns + 8):]:
                prefix = "User" if turn.role == "user" else ("Assistant" if turn.role == "assistant" else "System")
                pairs.append(f"{prefix}: {turn.content}")
            transcript = "\n".join(pairs)
            state.summary = self.llm.summarize(transcript)

    def maybe_yes_no_nudge(self, conversation_id: str, now: Optional[datetime] = None) -> Optional[str]:
        state = self.memory.get(conversation_id)
        if not state:
            return None
        now = now or datetime.now(timezone.utc)
        # Only nudge if last message was from assistant and user has been silent
        if state.last_assistant_ts and (len(state.messages) == 0 or state.messages[-1].role == "assistant"):
            last_user = state.last_user_ts or state.created_at
            idle_seconds = (now - last_user).total_seconds()
            if idle_seconds >= CONFIG.yes_no_idle_seconds:
                # Build short context snippet
                recent_texts = [turn.content for turn in state.messages[-4:]]
                snippet = "\n".join(recent_texts)[-600:]
                return self.llm.yes_no_nudge(snippet)
        return None


