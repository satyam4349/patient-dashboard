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

    # ---------------- Heuristic screening and tailored support ---------------- #
    def _detect_crisis(self, text: str) -> bool:
        content = (text or "").lower()
        crisis_terms = [
            "suicide", "kill myself", "end my life", "end it all", "hurt myself",
            "self-harm", "won't wake up", "no reason to live", "give up"
        ]
        return any(term in content for term in crisis_terms)

    def _classify_category(self, text: str) -> str:
        content = (text or "").lower()
        if any(k in content for k in ["hallucination", "voices", "hearing voices", "paranoid", "delusion"]):
            return "psychosis"
        if any(k in content for k in ["anxious", "panic", "worried", "tense", "on edge", "nervous"]):
            return "anxiety"
        if any(k in content for k in ["sad", "down", "hopeless", "worthless", "numb", "no interest", "can't enjoy"]):
            return "depression"
        if any(k in content for k in ["stress", "overwhelmed", "burnt out", "burnout", "pressure"]):
            return "stress"
        return "general"

    def _pick_yes_no_question(self, category: str) -> str:
        if category == "psychosis":
            return "Have you recently heard or seen things that others do not?"
        if category == "anxiety":
            return "Have you felt on edge or unable to control worrying most days?"
        if category == "depression":
            return "Have you felt down or lost interest in activities most days for 2+ weeks?"
        if category == "stress":
            return "Would setting small daily goals help reduce your current stress?"
        return "Would a brief check-in help you feel a bit better right now?"

    def _targeted_support_block(self, category: str) -> str:
        if category == "psychosis":
            return (
                "I hear you're dealing with very unsettling experiences. Grounding can help. "
                "Try 5-4-3-2-1 (five things you see, four you feel, three you hear, two you smell, one you taste). "
                "If these experiences are frequent or worsening, contacting your clinician promptly is important."
            )
        if category == "anxiety":
            return (
                "Anxiety can be intense. A quick exercise: 4-7-8 breathing (inhale 4, hold 7, exhale 8) for 4 cycles. "
                "You can also try scheduling a 10-minute 'worry time' to contain spirals and then refocus."
            )
        if category == "depression":
            return (
                "That sounds really heavy. A gentle first step is Behavioral Activation: pick one small, meaningful action today "
                "(e.g., 5-minute walk, shower, text a friend). Small wins can re-start momentum."
            )
        if category == "stress":
            return (
                "Feeling overwhelmed is tough. Break today into 2-3 small tasks, set a 20-minute timer per task, then take a 5-minute break. "
                "Also consider one boundary you can set to protect time or energy."
            )
        return "I'm here with you. We can take this one step at a time."

    def _build_response(self, user_message: str) -> str:
        # Crisis-first policy
        if self._detect_crisis(user_message):
            return (
                "I'm really concerned about your safety. If you're in immediate danger, please call local emergency services or 112 (India). "
                "You're not alone—if you can, reach out to someone you trust right now."
            )

        category = self._classify_category(user_message)
        support = self._targeted_support_block(category)
        question = self._pick_yes_no_question(category)
        return f"{support}\n\n{question}"

    def start_conversation(self, user_id: str, initial_message: str) -> ConversationState:
        conversation_id = str(uuid.uuid4())
        state = self.memory.create(conversation_id, user_id)
        state.append_user(initial_message)

        # Optional: immediate summarization if long introduction (rare)
        self._maybe_update_summary(state)

        # If very short input, lead with a simple yes/no to get clarity
        if len(initial_message.strip().split()) < 5:
            q = self._pick_yes_no_question(self._classify_category(initial_message))
            state.pending_yes_no = True
            state.pending_yes_no_question = q
            assistant_reply = q
        else:
            # First attempt: targeted rule-based support
            assistant_reply = self._build_response(initial_message)
            # If it's very generic, back up with LLM augmentation
            if assistant_reply.strip() == "I'm here with you. We can take this one step at a time.":
                try:
                    assistant_reply = self._generate_reply(state)
                except Exception:
                    # Keep heuristic reply if LLM fails
                    pass

        # Always ask for mood at the start of the conversation (emoji only at start of question)
        state.pending_mood = True
        state.pending_mood_prompt = (
            "🙂 How are you feeling right now? Please pick a mood."
        )
        assistant_reply = f"{assistant_reply}\n\n{state.pending_mood_prompt}"
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

        # Short inputs -> ask a yes/no to clarify
        if len(user_message.strip().split()) < 5:
            q = self._pick_yes_no_question(self._classify_category(user_message))
            state.pending_yes_no = True
            state.pending_yes_no_question = q
            assistant_reply = q
        else:
            # Targeted heuristics first, then LLM if needed
            assistant_reply = self._build_response(user_message)
            if assistant_reply.strip() == "I'm here with you. We can take this one step at a time.":
                try:
                    assistant_reply = self._generate_reply(state)
                except Exception:
                    # Keep heuristic reply if LLM fails
                    pass

        # If mood was chosen earlier, tailor response and build mood-specific yes/no; if not, remind gently after a few turns
        if state.current_mood:
            mood = state.current_mood
            if mood in ("sad", "down"):
                assistant_reply += "\n\nI appreciate you sharing that. Let’s keep it gentle and small-step today."
            elif mood in ("anxious",):
                assistant_reply += "\n\nLet’s keep breaths slow and steady as we talk."
            elif mood in ("angry",):
                assistant_reply += "\n\nIt’s okay to feel angry. We can channel it into constructive steps."
            # Mood-specific yes/no follow-up using LLM
            recent_texts = [t.content for t in state.messages[-4:]]
            snippet = "\n".join(recent_texts)[-600:]
            try:
                mood_q = self.llm.mood_yes_no(mood, snippet)
                if mood_q:
                    state.pending_yes_no = True
                    state.pending_yes_no_question = mood_q
                    assistant_reply += f"\n\n{mood_q}"
            except Exception:
                pass
        elif len(state.messages) <= 4:  # early reminder if not provided yet
            state.pending_mood = True
            state.pending_mood_prompt = (
                "🙂 How's your mood now? Please choose one."
            )
            assistant_reply += f"\n\n{state.pending_mood_prompt}"
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


