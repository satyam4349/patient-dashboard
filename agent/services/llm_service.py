import os
import requests
from typing import Optional
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq

# Load environment variables from .env file
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class LLMService:
    def __init__(self):
        self.groq_api_key = GROQ_API_KEY
        self.google_api_key = GOOGLE_API_KEY
        
        # Validate API keys
        if not self.groq_api_key:
            print("Warning: GROQ_API_KEY not found in environment variables")
        if not self.google_api_key:
            print("Warning: GOOGLE_API_KEY not found in environment variables")
        
        # Initialize Gemini only if API key is available
        if self.google_api_key:
            try:
                genai.configure(api_key=self.google_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
        
        # Initialize Groq only if API key is available
        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
            except Exception as e:
                print(f"Failed to initialize Groq: {e}")
                self.groq_client = None
        else:
            self.groq_client = None

    def query_groq(self, prompt: str) -> Optional[str]:
        if not self.groq_api_key:
            return "GROQ API key not set. Please check your .env file."
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"GROQ API error: {str(e)}. Please check your API key and try again."

    def query_gemini(self, prompt: str) -> Optional[str]:
        if not self.google_api_key:
            return "Google API key not set. Please check your .env file."
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini API error: {str(e)}. Please check your API key and try again."

    def query(self, prompt: str, backend: str = "groq") -> str:
        if backend == "groq":
            return self.query_groq(prompt)
        elif backend == "gemini":
            return self.query_gemini(prompt)
        else:
            return "Invalid backend specified. Use 'groq' or 'gemini'."
