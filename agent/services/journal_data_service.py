import csv
import os
from typing import List, Dict, Optional
from datetime import datetime
from models.agent_companion_models import JournalEntry

class JournalDataService:
    def __init__(self, 
                 csv_file_path: str = "mock_user_journal_data.csv",
                 csv_file_with_questions: str = "mock_user_journal_data_with_questions.csv"):
        self.csv_file_path = csv_file_path
        self.csv_file_with_questions = csv_file_with_questions
        self.entries = self._load_journal_data(self.csv_file_path)
        self.entries_with_questions = self._load_journal_data(self.csv_file_with_questions, with_questions=True)

    def _load_journal_data(self, file_path: str, with_questions: bool = False) -> List[JournalEntry]:
        entries = []
        if not os.path.exists(file_path):
            print(f"Warning: CSV file not found at {file_path}")
            return entries
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    entry = JournalEntry(
                        user_id=row['user_id'],
                        entry_id=row['entry_id'],
                        entry_date=datetime.strptime(row['entry_date'], "%Y-%m-%d"),
                        mood_score=int(row['mood_score']),
                        energy_level=int(row['energy_level']),
                        sleep_hours=float(row['sleep_hours']),
                        stress_level=int(row['stress_level']),
                        anxiety_level=int(row['anxiety_level']),
                        depression_level=int(row['depression_level']),
                        content=row['content'],
                        triggers=row['triggers'],
                        coping_strategies=row['coping_strategies'],
                        medication_taken=row['medication_taken'],
                        therapy_session=row['therapy_session'],
                        risk_flags=row['risk_flags'],
                        question=row['question'] if with_questions and 'question' in row else None
                    )
                    entries.append(entry)
                except Exception as e:
                    print(f"Error parsing row: {row}\n{e}")
        return entries

    def get_entries_for_user(self, user_id: str, with_questions: bool = False) -> List[JournalEntry]:
        data = self.entries_with_questions if with_questions else self.entries
        return [entry for entry in data if entry.user_id == user_id]

    def get_all_users(self) -> List[str]:
        user_ids = set(entry.user_id for entry in self.entries)
        user_ids.update(entry.user_id for entry in self.entries_with_questions)
        return list(user_ids)
