import csv
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from models.ai_companion_models import JournalEntry, UserMentalHealthProfile, MentalHealthCondition, RiskLevel, JournalAnalytics
import os

class JournalDataService:
    def __init__(self, csv_file_path: str = "data/mock_user_journal_data.csv"):
        self.csv_file_path = csv_file_path
        self.journal_data = self._load_journal_data()
        self.user_profiles = self._create_user_profiles()
    
    def _load_journal_data(self) -> List[JournalEntry]:
        """Load journal data from CSV file"""
        entries = []
        
        if not os.path.exists(self.csv_file_path):
            print(f"Warning: CSV file not found at {self.csv_file_path}")
            return entries
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    entry = JournalEntry(
                        user_id=row['user_id'],
                        entry_id=row['entry_id'],
                        entry_date=datetime.strptime(row['entry_date'], '%Y-%m-%d'),
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
                        risk_flags=row['risk_flags']
                    )
                    entries.append(entry)
            
            print(f"✅ Loaded {len(entries)} journal entries from CSV")
            return entries
            
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            return entries
    
    def _create_user_profiles(self) -> Dict[str, UserMentalHealthProfile]:
        """Create mental health profiles for each user based on journal data"""
        profiles = {}
        
        # Map user IDs to conditions based on medication patterns
        user_condition_map = {
            'user_001': MentalHealthCondition.SCHIZOPHRENIA,
            'user_002': MentalHealthCondition.DEPRESSION,
            'user_003': MentalHealthCondition.ANXIETY,
            'user_004': MentalHealthCondition.SUICIDAL_THOUGHTS,
            'user_005': MentalHealthCondition.BIPOLAR,
            'user_006': MentalHealthCondition.PTSD,
            'user_007': MentalHealthCondition.OCD,
            'user_008': MentalHealthCondition.EATING_DISORDER
        }
        
        for user_id in user_condition_map:
            user_entries = [e for e in self.journal_data if e.user_id == user_id]
            if user_entries:
                # Get most recent medication info
                latest_entry = max(user_entries, key=lambda x: x.entry_date)
                medication = latest_entry.medication_taken
                
                # Get therapist info
                therapist = None
                for entry in user_entries:
                    if entry.therapy_session != "No":
                        therapist = entry.therapy_session
                        break
                
                # Analyze trends
                risk_trend = self._analyze_risk_trend(user_entries)
                mood_trend = self._analyze_mood_trend(user_entries)
                sleep_trend = self._analyze_sleep_trend(user_entries)
                
                profile = UserMentalHealthProfile(
                    user_id=user_id,
                    primary_condition=user_condition_map[user_id],
                    current_medication=medication,
                    therapist=therapist,
                    recent_entries=user_entries,
                    risk_trend=risk_trend,
                    mood_trend=mood_trend,
                    sleep_trend=sleep_trend
                )
                profiles[user_id] = profile
        
        return profiles
    
    def _analyze_risk_trend(self, entries: List[JournalEntry]) -> str:
        """Analyze risk level trend over time"""
        if len(entries) < 2:
            return "insufficient_data"
        
        # Convert risk flags to numeric values
        risk_values = []
        for entry in entries:
            if entry.risk_flags == "Critical":
                risk_values.append(4)
            elif entry.risk_flags == "High":
                risk_values.append(3)
            elif entry.risk_flags == "Medium":
                risk_values.append(2)
            else:
                risk_values.append(1)
        
        if len(risk_values) >= 2:
            if risk_values[-1] < risk_values[0]:
                return "improving"
            elif risk_values[-1] > risk_values[0]:
                return "worsening"
            else:
                return "stable"
        return "stable"
    
    def _analyze_mood_trend(self, entries: List[JournalEntry]) -> str:
        """Analyze mood trend over time"""
        if len(entries) < 2:
            return "insufficient_data"
        
        mood_scores = [e.mood_score for e in entries]
        if len(mood_scores) >= 2:
            if mood_scores[-1] > mood_scores[0]:
                return "improving"
            elif mood_scores[-1] < mood_scores[0]:
                return "worsening"
            else:
                return "stable"
        return "stable"
    
    def _analyze_sleep_trend(self, entries: List[JournalEntry]) -> str:
        """Analyze sleep pattern trend over time"""
        if len(entries) < 2:
            return "insufficient_data"
        
        sleep_hours = [e.sleep_hours for e in entries]
        if len(sleep_hours) >= 2:
            avg_recent = sum(sleep_hours[-3:]) / min(3, len(sleep_hours))
            avg_earlier = sum(sleep_hours[:3]) / min(3, len(sleep_hours))
            
            if avg_recent > avg_earlier + 0.5:
                return "improving"
            elif avg_recent < avg_earlier - 0.5:
                return "worsening"
            else:
                return "stable"
        return "stable"
    
    def get_user_profile(self, user_id: str) -> Optional[UserMentalHealthProfile]:
        """Get mental health profile for a specific user"""
        return self.user_profiles.get(user_id)
    
    def get_recent_entries(self, user_id: str, days: int = 7) -> List[JournalEntry]:
        """Get recent journal entries for a user"""
        cutoff_date = datetime.now() - timedelta(days=days)
        user_entries = [e for e in self.journal_data if e.user_id == user_id]
        recent_entries = [e for e in user_entries if e.entry_date >= cutoff_date]
        return sorted(recent_entries, key=lambda x: x.entry_date, reverse=True)
    
    def get_user_analytics(self, user_id: str) -> Optional[JournalAnalytics]:
        """Get comprehensive analytics for a user"""
        user_entries = [e for e in self.journal_data if e.user_id == user_id]
        if not user_entries:
            return None
        
        # Analyze patterns
        mood_trend = self._analyze_mood_trend(user_entries)
        sleep_pattern = self._analyze_sleep_trend(user_entries)
        
        # Extract triggers and coping strategies
        all_triggers = []
        all_coping = []
        for entry in user_entries:
            if entry.triggers and entry.triggers != "None significant":
                all_triggers.extend([t.strip() for t in entry.triggers.split(',')])
            if entry.coping_strategies:
                all_coping.extend([c.strip() for c in entry.coping_strategies.split(',')])
        
        # Count frequency
        trigger_counts = {}
        for trigger in all_triggers:
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        coping_counts = {}
        for coping in all_coping:
            coping_counts[coping] = coping_counts.get(coping, 0) + 1
        
        # Get most common
        stress_triggers = [k for k, v in sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
        effective_coping = [k for k, v in sorted(coping_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        # Risk patterns
        risk_levels = [e.risk_flags for e in user_entries]
        risk_patterns = f"Most common: {max(set(risk_levels), key=risk_levels.count)}"
        
        # Improvement areas
        improvement_areas = []
        if mood_trend == "worsening":
            improvement_areas.append("Mood management")
        if sleep_pattern == "worsening":
            improvement_areas.append("Sleep hygiene")
        
        # Positive progress
        positive_progress = []
        if mood_trend == "improving":
            positive_progress.append("Mood stabilization")
        if sleep_pattern == "improving":
            positive_progress.append("Better sleep patterns")
        
        return JournalAnalytics(
            user_id=user_id,
            mood_trend=mood_trend,
            sleep_pattern=sleep_pattern,
            stress_triggers=stress_triggers,
            effective_coping_strategies=effective_coping,
            risk_patterns=risk_patterns,
            improvement_areas=improvement_areas,
            positive_progress=positive_progress
        )
    
    def get_condition_specific_data(self, condition: MentalHealthCondition) -> List[JournalEntry]:
        """Get journal entries for users with a specific condition"""
        condition_users = []
        for user_id, profile in self.user_profiles.items():
            if profile.primary_condition == condition:
                condition_users.append(user_id)
        
        entries = []
        for user_id in condition_users:
            entries.extend([e for e in self.journal_data if e.user_id == user_id])
        
        return entries
    
    def get_high_risk_users(self) -> List[str]:
        """Get list of users with high or critical risk levels"""
        high_risk_users = []
        for user_id, profile in self.user_profiles.items():
            recent_entries = self.get_recent_entries(user_id, days=3)
            if recent_entries:
                latest_risk = recent_entries[0].risk_flags
                if latest_risk in ["High", "Critical"]:
                    high_risk_users.append(user_id)
        
        return high_risk_users
    
    def get_medication_adherence(self, user_id: str) -> Dict[str, Any]:
        """Get medication adherence statistics for a user"""
        user_entries = [e for e in self.journal_data if e.user_id == user_id]
        if not user_entries:
            return {"adherence_rate": 0, "total_entries": 0, "missed_doses": 0}
        
        total_entries = len(user_entries)
        taken_entries = len([e for e in user_entries if "Yes" in e.medication_taken])
        adherence_rate = (taken_entries / total_entries) * 100
        missed_doses = total_entries - taken_entries
        
        return {
            "adherence_rate": round(adherence_rate, 1),
            "total_entries": total_entries,
            "missed_doses": missed_doses,
            "current_medication": user_entries[-1].medication_taken if user_entries else "Unknown"
        }
