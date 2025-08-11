from typing import Dict, List


class NotesStore:
    def __init__(self):
        self._notes: Dict[str, List[str]] = {}

    def add(self, conversation_id: str, text: str) -> None:
        self._notes.setdefault(conversation_id, []).append(text)

    def get_all(self, conversation_id: str) -> List[str]:
        return list(self._notes.get(conversation_id, []))


