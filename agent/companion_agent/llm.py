import json
import time
from typing import List, Dict, Optional

from groq import Groq

from .config import CONFIG, CompanionConfig
from . import prompts


def _parse_json_list(raw_text: str) -> Optional[List[str]]:
    try:
        data = json.loads(raw_text.strip())
        if isinstance(data, list) and all(isinstance(x, str) for x in data):
            return data
        return None
    except Exception:
        return None


class LLMClient:
    def __init__(self, config: CompanionConfig = CONFIG):
        self.config = config
        if not self.config.groq_api_key:
            # Defer failures to first call with a clear message
            self._client = None
        else:
            self._client = Groq(api_key=self.config.groq_api_key)

    def _ensure_client(self):
        if self._client is None:
            if not self.config.groq_api_key:
                raise RuntimeError("GROQ_API_KEY not set in environment")
            self._client = Groq(api_key=self.config.groq_api_key)

    def _chat_completion(self, messages: List[Dict], model: str) -> str:
        self._ensure_client()
        last_err: Optional[Exception] = None
        for attempt in range(self.config.max_retries + 1):
            try:
                completion = self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                )
                return completion.choices[0].message.content
            except Exception as e:
                last_err = e
                # Lightweight backoff
                time.sleep(0.5 * (attempt + 1))
        # Fallback to secondary model when primary fails
        if model != self.config.groq_fallback_model:
            try:
                completion = self._client.chat.completions.create(
                    model=self.config.groq_fallback_model,
                    messages=messages,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                )
                return completion.choices[0].message.content
            except Exception as e:
                last_err = e
        raise RuntimeError(f"Groq chat completion failed: {last_err}")

    def generate(self, messages: List[Dict], model: Optional[str] = None) -> str:
        chosen_model = model or self.config.groq_model
        return self._chat_completion(messages, chosen_model)

    def summarize(self, transcript: str) -> str:
        messages = prompts.build_summarize_messages(transcript)
        return self._chat_completion(messages, self.config.groq_model)

    def suggest_followups(self, context_snippet: str) -> List[str]:
        messages = prompts.build_followup_messages(context_snippet)
        raw = self._chat_completion(messages, self.config.groq_model)
        parsed = _parse_json_list(raw)
        if parsed:
            return parsed[:3]
        # Fallback: split lines
        items = [line.strip("- ") for line in raw.splitlines() if line.strip()]
        return [item for item in items if item][:3]

    def yes_no_nudge(self, context_snippet: str) -> str:
        messages = prompts.build_yes_no_nudge_messages(context_snippet)
        return self._chat_completion(messages, self.config.groq_model)

    def mood_yes_no(self, mood: str, context_snippet: str) -> str:
        messages = prompts.build_mood_yes_no_messages(mood, context_snippet)
        return self._chat_completion(messages, self.config.groq_model)


