import csv
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from models.agent_companion_models import JournalEntry

class JournalDataService:
    def __init__(self, 
                 csv_file_path: str = None,
                 csv_file_with_questions: str = None):
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        agent_dir = os.path.dirname(current_dir)  # Go up one level to agent folder
        
        # Set default paths relative to agent directory
        if csv_file_path is None:
            csv_file_path = os.path.join(agent_dir, "mock_data", "mock_user_journal_data.csv")
        if csv_file_with_questions is None:
            csv_file_with_questions = os.path.join(agent_dir, "mock_data", "mock_user_journal_data_with_questions.csv")
            
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
                    # Safely parse detected_markers from string representation
                    detected_markers = []
                    if row['detected_markers']:
                        try:
                            # Try to parse as JSON first
                            detected_markers = json.loads(row['detected_markers'].replace("'", '"'))
                        except json.JSONDecodeError:
                            # Fallback: split by comma if it's a simple comma-separated string
                            detected_markers = [marker.strip().strip("'\"") for marker in row['detected_markers'].strip("[]").split(",")]
                    
                    entry = JournalEntry(
                        user_id=str(row['user_id']),
                        disorder_prediction=row['disorder_prediction'],
                        journal_entry=row['journal_entry'],
                        detected_markers=detected_markers,
                        check_in_question=row['check_in_question'] if with_questions and 'check_in_question' in row else None
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
