"""
Analytics service for patient wellness trends and insights.
Integrates with AI/ML models for language analysis and provides comprehensive analytics.
"""
import os
import json
import base64
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

# Import the patch before supabase to avoid realtime import issues
from utils.supabase_patch import patch_supabase_realtime
from supabase import create_client, Client
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env
load_dotenv()

# Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if not all([supabase_url, supabase_service_key]):
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required for AnalyticsService")

supabase_admin: Client = create_client(supabase_url, supabase_service_key)

# Encryption key
DATA_ENCRYPTION_KEY_B64 = os.getenv("DATA_ENCRYPTION_KEY_B64")
if not DATA_ENCRYPTION_KEY_B64:
    logger.warning("DATA_ENCRYPTION_KEY_B64 not set. Using a weak fallback key for development only.")
    DATA_ENCRYPTION_KEY = b"\x00" * 32
else:
    try:
        DATA_ENCRYPTION_KEY = base64.b64decode(DATA_ENCRYPTION_KEY_B64)
        if len(DATA_ENCRYPTION_KEY) != 32:
            raise ValueError("DATA_ENCRYPTION_KEY_B64 must decode to 32 bytes for AES-256-GCM")
    except Exception as e:
        raise ValueError(f"Invalid DATA_ENCRYPTION_KEY_B64: {e}")


class AnalyticsService:
    """Service for generating patient analytics and wellness trends."""
    
    @staticmethod
    def _decrypt(ciphertext: str, nonce: str) -> str:
        """Decrypt ciphertext using AES-256-GCM."""
        try:
            aesgcm = AESGCM(DATA_ENCRYPTION_KEY)
            ct_bytes = base64.b64decode(ciphertext)
            nonce_bytes = base64.b64decode(nonce)
            plaintext_bytes = aesgcm.decrypt(nonce_bytes, ct_bytes, None)
            return plaintext_bytes.decode("utf-8")
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return ""
    
    @staticmethod
    def _get_date_range(range_str: str) -> Tuple[datetime, datetime]:
        """Get start and end dates based on range string."""
        end_date = datetime.now(timezone.utc)
        
        if range_str == "Last 7 days":
            start_date = end_date - timedelta(days=7)
        elif range_str == "Last 30 days":
            start_date = end_date - timedelta(days=30)
        elif range_str == "Last 90 days":
            start_date = end_date - timedelta(days=90)
        else:  # All time
            start_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        
        return start_date, end_date
    
    @staticmethod
    async def get_mood_analytics(user_id: str, date_range: str) -> Dict:
        """Get mood analytics for the specified date range."""
        try:
            start_date, end_date = AnalyticsService._get_date_range(date_range)
            
            # Fetch mood data
            result = supabase_admin.table("moods")\
                .select("ciphertext, nonce, created_at")\
                .eq("user_id", user_id)\
                .gte("created_at", start_date.isoformat())\
                .lte("created_at", end_date.isoformat())\
                .order("created_at", desc=False)\
                .execute()
            
            mood_data = []
            mood_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            
            for row in result.data or []:
                decrypted = AnalyticsService._decrypt(row["ciphertext"], row["nonce"])
                try:
                    data = json.loads(decrypted)
                    emoji = data.get("emoji", 3)
                    created_at = datetime.fromisoformat(row["created_at"].replace('Z', '+00:00'))
                    
                    mood_data.append({
                        "date": created_at.strftime("%Y-%m-%d"),
                        "emoji": emoji,
                        "note": data.get("note", "")
                    })
                    
                    mood_counts[emoji] = mood_counts.get(emoji, 0) + 1
                except json.JSONDecodeError:
                    continue
            
            # Calculate statistics
            total_entries = len(mood_data)
            if total_entries > 0:
                avg_mood = sum(entry["emoji"] for entry in mood_data) / total_entries
                mood_trend = "improving" if len(mood_data) > 1 and mood_data[-1]["emoji"] > mood_data[0]["emoji"] else "stable"
            else:
                avg_mood = 0
                mood_trend = "no_data"
            
            return {
                "status": "success",
                "data": {
                    "mood_data": mood_data,
                    "mood_counts": mood_counts,
                    "stats": {
                        "total_entries": total_entries,
                        "average_mood": round(avg_mood, 2),
                        "trend": mood_trend,
                        "most_common_mood": max(mood_counts, key=mood_counts.get) if total_entries > 0 else 3
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"get_mood_analytics error: {e}")
            return {"status": "error", "message": f"Failed to get mood analytics: {e}"}
    
    @staticmethod
    async def get_journal_analytics(user_id: str, date_range: str) -> Dict:
        """Get journal analytics including streaks and word counts."""
        try:
            start_date, end_date = AnalyticsService._get_date_range(date_range)
            
            # Fetch journal data
            result = supabase_admin.table("journals")\
                .select("ciphertext, nonce, created_at")\
                .eq("user_id", user_id)\
                .gte("created_at", start_date.isoformat())\
                .lte("created_at", end_date.isoformat())\
                .order("created_at", desc=False)\
                .execute()
            
            journal_data = []
            daily_entries = {}
            
            for row in result.data or []:
                decrypted = AnalyticsService._decrypt(row["ciphertext"], row["nonce"])
                try:
                    data = json.loads(decrypted)
                    text = data.get("text", "")
                    created_at = datetime.fromisoformat(row["created_at"].replace('Z', '+00:00'))
                    date_str = created_at.strftime("%Y-%m-%d")
                    
                    word_count = len(text.split()) if text else 0
                    char_count = len(text)
                    
                    journal_data.append({
                        "date": date_str,
                        "word_count": word_count,
                        "char_count": char_count,
                        "has_entry": True
                    })
                    
                    daily_entries[date_str] = True
                    
                except json.JSONDecodeError:
                    continue
            
            # Calculate streaks
            current_streak = 0
            longest_streak = 0
            temp_streak = 0
            
            # Generate all dates in range for streak calculation
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                date_str = current_date.strftime("%Y-%m-%d")
                if date_str in daily_entries:
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 0
                current_date += timedelta(days=1)
            
            # Current streak (from today backwards)
            today = datetime.now(timezone.utc).date()
            check_date = today
            while check_date >= start_date.date():
                date_str = check_date.strftime("%Y-%m-%d")
                if date_str in daily_entries:
                    current_streak += 1
                else:
                    break
                check_date -= timedelta(days=1)
            
            # Calculate statistics
            total_entries = len(journal_data)
            total_words = sum(entry["word_count"] for entry in journal_data)
            avg_words = total_words / total_entries if total_entries > 0 else 0
            
            return {
                "status": "success",
                "data": {
                    "journal_data": journal_data,
                    "stats": {
                        "total_entries": total_entries,
                        "total_words": total_words,
                        "average_words": round(avg_words, 2),
                        "current_streak": current_streak,
                        "longest_streak": longest_streak,
                        "consistency_rate": round((total_entries / max(1, (end_date.date() - start_date.date()).days)) * 100, 2)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"get_journal_analytics error: {e}")
            return {"status": "error", "message": f"Failed to get journal analytics: {e}"}
    
    @staticmethod
    async def get_language_analytics(user_id: str, date_range: str) -> Dict:
        """Get language analysis including coherence and LIWC analysis."""
        try:
            start_date, end_date = AnalyticsService._get_date_range(date_range)
            
            # Fetch journal data for analysis
            result = supabase_admin.table("journals")\
                .select("ciphertext, nonce, created_at")\
                .eq("user_id", user_id)\
                .gte("created_at", start_date.isoformat())\
                .lte("created_at", end_date.isoformat())\
                .order("created_at", desc=False)\
                .execute()
            
            texts = []
            dates = []
            
            for row in result.data or []:
                decrypted = AnalyticsService._decrypt(row["ciphertext"], row["nonce"])
                try:
                    data = json.loads(decrypted)
                    text = data.get("text", "")
                    if text.strip():
                        texts.append(text)
                        created_at = datetime.fromisoformat(row["created_at"].replace('Z', '+00:00'))
                        dates.append(created_at.strftime("%Y-%m-%d"))
                except json.JSONDecodeError:
                    continue
            
            if not texts:
                return {
                    "status": "success",
                    "data": {
                        "coherence_data": [],
                        "liwc_data": {},
                        "stats": {
                            "avg_coherence": 0,
                            "coherence_trend": "no_data",
                            "dominant_themes": []
                        }
                    }
                }
            
            # TODO: Integrate with actual AI models
            # For now, return mock data structure
            coherence_data = []
            for i, (text, date) in enumerate(zip(texts, dates)):
                # Mock coherence score (0-1)
                coherence_score = min(1.0, max(0.0, 0.5 + (len(text.split()) / 200) * 0.3))
                coherence_data.append({
                    "date": date,
                    "coherence": round(coherence_score, 3)
                })
            
            # Mock LIWC data
            liwc_data = {
                "positive_emotion": 0.15,
                "negative_emotion": 0.08,
                "anxiety": 0.05,
                "sadness": 0.03,
                "anger": 0.02,
                "social": 0.12,
                "family": 0.08,
                "friends": 0.06,
                "work": 0.10,
                "achievement": 0.07,
                "power": 0.04,
                "reward": 0.05
            }
            
            avg_coherence = sum(item["coherence"] for item in coherence_data) / len(coherence_data)
            coherence_trend = "improving" if len(coherence_data) > 1 and coherence_data[-1]["coherence"] > coherence_data[0]["coherence"] else "stable"
            
            # Find dominant themes (top 3 LIWC categories)
            dominant_themes = sorted(liwc_data.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                "status": "success",
                "data": {
                    "coherence_data": coherence_data,
                    "liwc_data": liwc_data,
                    "stats": {
                        "avg_coherence": round(avg_coherence, 3),
                        "coherence_trend": coherence_trend,
                        "dominant_themes": [{"theme": theme, "score": score} for theme, score in dominant_themes]
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"get_language_analytics error: {e}")
            return {"status": "error", "message": f"Failed to get language analytics: {e}"}
    
    @staticmethod
    async def get_comprehensive_analytics(user_id: str, date_range: str) -> Dict:
        """Get comprehensive analytics combining all analysis types."""
        try:
            mood_analytics = await AnalyticsService.get_mood_analytics(user_id, date_range)
            journal_analytics = await AnalyticsService.get_journal_analytics(user_id, date_range)
            language_analytics = await AnalyticsService.get_language_analytics(user_id, date_range)
            
            if any(result["status"] == "error" for result in [mood_analytics, journal_analytics, language_analytics]):
                return {"status": "error", "message": "Failed to generate comprehensive analytics"}
            
            return {
                "status": "success",
                "data": {
                    "mood_analytics": mood_analytics["data"],
                    "journal_analytics": journal_analytics["data"],
                    "language_analytics": language_analytics["data"],
                    "summary": {
                        "total_mood_entries": mood_analytics["data"]["stats"]["total_entries"],
                        "total_journal_entries": journal_analytics["data"]["stats"]["total_entries"],
                        "average_mood": mood_analytics["data"]["stats"]["average_mood"],
                        "current_streak": journal_analytics["data"]["stats"]["current_streak"],
                        "avg_coherence": language_analytics["data"]["stats"]["avg_coherence"]
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"get_comprehensive_analytics error: {e}")
            return {"status": "error", "message": f"Failed to get comprehensive analytics: {e}"}