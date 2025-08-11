from typing import Optional, Dict


class ToolInvocation:
    def __init__(self, name: str, args: Dict):
        self.name = name
        self.args = args


def route_if_needed(user_input: str) -> Optional[ToolInvocation]:
    """Very lightweight heuristic router. Extend as needed.

    - calculator: messages like "calc: 2+2" or "calculate 2+2"
    - note: messages like "note: ..."
    """
    text = user_input.strip().lower()
    if text.startswith("calc:") or text.startswith("calculate "):
        expression = user_input.split(":", 1)[-1].strip() if ":" in user_input else user_input.split(" ", 1)[-1]
        return ToolInvocation("calculator", {"expression": expression})
    if text.startswith("note:"):
        return ToolInvocation("notes.add", {"text": user_input.split(":", 1)[-1].strip()})
    return None


