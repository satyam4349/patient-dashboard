from typing import List, Dict


def system_prompt() -> str:
    return (
        "You are a compassionate AI mental health companion.\n"
        "Your responsibilities:\n"
        "1) Provide empathetic, supportive responses.\n"
        "2) Personalize using the user's recent context.\n"
        "3) Offer practical, evidence-informed coping strategies when appropriate.\n"
        "4) Encourage professional help when needed.\n"
        "5) Never provide diagnoses or replace professional therapy.\n\n"
        "Safety:\n"
        "- Avoid clinical claims.\n"
        "- If user indicates crisis, provide emergency resources and encourage immediate help.\n\n"
        "Conversation policy:\n"
        "- Prioritize the last few user turns (recency).\n"
        "- If a summary is provided, use it for older context.\n"
        "- Ask concise clarifying questions when needed.\n"
    )


def build_summarize_messages(transcript: str) -> List[Dict]:
    return [
        {"role": "system", "content": "Summarize the conversation for future context. Be concise (<=120 words)."},
        {"role": "user", "content": transcript},
    ]


def build_followup_messages(context_snippet: str) -> List[Dict]:
    instruction = (
        "Based on the recent conversation, propose 2-3 concise follow-up suggestions that the user can select. "
        "They must be short (<=12 words each), empathetic, and non-clinical. Return ONLY a JSON array of strings."
    )
    return [
        {"role": "system", "content": instruction},
        {"role": "user", "content": context_snippet},
    ]


def build_yes_no_nudge_messages(context_snippet: str) -> List[Dict]:
    instruction = (
        "Craft a single yes/no question to gently move the conversation forward. "
        "It must be safe, empathetic, and strictly a yes/no format. Return ONLY the question text."
    )
    return [
        {"role": "system", "content": instruction},
        {"role": "user", "content": context_snippet},
    ]


