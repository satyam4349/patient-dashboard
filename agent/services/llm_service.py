import os
import requests
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class LLMService:
    def __init__(self):
        self.grok_api_key = GROK_API_KEY
        self.gemini_api_key = GEMINI_API_KEY

    def query_grok(self, prompt: str) -> Optional[str]:
        if not self.grok_api_key:
            return "Grok API key not set."
        url = "https://api.grok.com/v1/chat/completions"  # Example endpoint
        headers = {
            "Authorization": f"Bearer {self.grok_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "grok-1",
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            return f"Grok API error: {e}"

    def query_gemini(self, prompt: str) -> Optional[str]:
        if not self.gemini_api_key:
            return "Gemini API key not set."
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "key": self.gemini_api_key
        }
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        try:
            response = requests.post(url, params=params, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        except Exception as e:
            return f"Gemini API error: {e}"

    def query(self, prompt: str, backend: str = "grok") -> str:
        if backend == "grok":
            return self.query_grok(prompt)
        elif backend == "gemini":
            return self.query_gemini(prompt)
        else:
            return "Invalid backend specified. Use 'grok' or 'gemini'."
