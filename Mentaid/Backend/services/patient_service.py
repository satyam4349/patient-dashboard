"""
Patient service for mood and journal features with Supabase integration
and AES-GCM encryption.
"""
import os
import json
import base64
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

from dotenv import load_dotenv

# Import the patch before supabase to avoid realtime import issues
from utils.supabase_patch import patch_supabase_realtime
from supabase import create_client, Client
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from models.patient_models import (
    MoodCreate,
    JournalCreate,
    EncryptResult,
    HistoryQuery,
    HistoryItem,
    HistoryResponse,
    SaveResult,
    ConnectionRequest,
    ConnectionResponse,
    ConnectionInfo,
    UserConnectionCode,
    PrivacySettingsUpdate,
    PrivacySettings,
)

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env
load_dotenv()

# Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if not all([supabase_url, supabase_service_key]):
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required for PatientService")

supabase_admin: Client = create_client(supabase_url, supabase_service_key)

# Encryption key (32-byte key, base64-encoded)
DATA_ENCRYPTION_KEY_B64 = os.getenv("DATA_ENCRYPTION_KEY_B64")
if not DATA_ENCRYPTION_KEY_B64:
    logger.warning("DATA_ENCRYPTION_KEY_B64 not set. Using a weak fallback key for development only.")
    # Fallback (development only): 32 zero bytes
    DATA_ENCRYPTION_KEY = b"\x00" * 32
else:
    try:
        DATA_ENCRYPTION_KEY = base64.b64decode(DATA_ENCRYPTION_KEY_B64)
        if len(DATA_ENCRYPTION_KEY) != 32:
            raise ValueError("DATA_ENCRYPTION_KEY_B64 must decode to 32 bytes for AES-256-GCM")
    except Exception as e:
        raise ValueError(f"Invalid DATA_ENCRYPTION_KEY_B64: {e}")


class PatientService:
    VERSION = "v1"

    @staticmethod
    def _encrypt(plaintext: str) -> EncryptResult:
        """Encrypt plaintext using AES-256-GCM with random 12-byte nonce."""
        aesgcm = AESGCM(DATA_ENCRYPTION_KEY)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        return EncryptResult(
            ciphertext=base64.b64encode(ct).decode("utf-8"),
            nonce=base64.b64encode(nonce).decode("utf-8"),
            version=PatientService.VERSION,
        )

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    async def _check_daily_limit(user_id: str, entry_type: str) -> bool:
        """Check if user already has entry for today."""
        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        table_name = "moods" if entry_type == "mood" else "journals"
        
        result = supabase_admin.table(table_name)\
            .select("id")\
            .eq("user_id", user_id)\
            .gte("created_at", today_start.isoformat())\
            .lte("created_at", today_end.isoformat())\
            .execute()
        
        return len(result.data or []) > 0

    # ---------------------- Save operations ----------------------
    @staticmethod
    async def save_mood(user_id: str, data: MoodCreate) -> Dict:
        try:
            # Check daily limit
            if await PatientService._check_daily_limit(user_id, "mood"):
                return {"status": "error", "message": "You have already recorded your mood today. Only one mood entry per day is allowed."}
            
            # Build plaintext JSON for encryption (include sleep data)
            mood_data = {
                "emoji": data.emoji, 
                "note": (data.note or "")
            }
            if data.sleep_hours is not None:
                mood_data["sleep_hours"] = data.sleep_hours
            
            plaintext = json.dumps(mood_data)
            enc = PatientService._encrypt(plaintext)

            payload = {
                "user_id": user_id,
                "ciphertext": enc.ciphertext,
                "nonce": enc.nonce,
                "version": enc.version,
                "created_at": PatientService._now_iso(),
            }

            result = supabase_admin.table("moods").insert(payload).execute()
            if not result.data:
                return {"status": "error", "message": "Failed to save mood"}

            row = result.data[0]
            return {
                "status": "success",
                "result": SaveResult(
                    id=str(row.get("id")),
                    created_at=datetime.fromisoformat(row.get("created_at") or payload["created_at"]),
                    version=enc.version,
                ).dict()
            }
        except Exception as e:
            logger.error(f"save_mood error: {e}")
            return {"status": "error", "message": f"save_mood failed: {e}"}

    @staticmethod
    async def save_journal(user_id: str, data: JournalCreate) -> Dict:
        try:
            # Check daily limit
            if await PatientService._check_daily_limit(user_id, "journal"):
                return {"status": "error", "message": "You have already written your journal today. Only one journal entry per day is allowed."}
            
            # Basic normalization; further sanitization can be added server-side
            text = data.text.strip()
            plaintext = json.dumps({"text": text})
            enc = PatientService._encrypt(plaintext)

            payload = {
                "user_id": user_id,
                "ciphertext": enc.ciphertext,
                "nonce": enc.nonce,
                "version": enc.version,
                "created_at": PatientService._now_iso(),
            }

            result = supabase_admin.table("journals").insert(payload).execute()
            if not result.data:
                return {"status": "error", "message": "Failed to save journal"}

            row = result.data[0]
            return {
                "status": "success",
                "result": SaveResult(
                    id=str(row.get("id")),
                    created_at=datetime.fromisoformat(row.get("created_at") or payload["created_at"]),
                    version=enc.version,
                ).dict()
            }
        except Exception as e:
            logger.error(f"save_journal error: {e}")
            return {"status": "error", "message": f"save_journal failed: {e}"}

    # ---------------------- History ----------------------
    @staticmethod
    def _parse_cursor(cursor: Optional[str]) -> Optional[str]:
        # For now, cursor is just an ISO created_at string
        return cursor

    @staticmethod
    async def get_history(user_id: str, query: HistoryQuery) -> Dict:
        try:
            limit = query.limit
            cursor_dt_iso = PatientService._parse_cursor(query.cursor)

            # Fetch moods
            moods_q = supabase_admin.table("moods").select("id, created_at, ciphertext, nonce, version").eq("user_id", user_id).order("created_at", desc=True)
            journals_q = supabase_admin.table("journals").select("id, created_at, ciphertext, nonce, version").eq("user_id", user_id).order("created_at", desc=True)

            if cursor_dt_iso:
                # Return records older than the cursor timestamp
                moods_q = moods_q.lt("created_at", cursor_dt_iso)
                journals_q = journals_q.lt("created_at", cursor_dt_iso)

            moods_res = moods_q.limit(limit).execute()
            journals_res = journals_q.limit(limit).execute()

            items: List[HistoryItem] = []
            for row in moods_res.data or []:
                try:
                    created_at = datetime.fromisoformat(row["created_at"]) if isinstance(row.get("created_at"), str) else row.get("created_at")
                except Exception:
                    created_at = datetime.now(timezone.utc)
                items.append(HistoryItem(
                    item_type="mood",
                    ciphertext=row.get("ciphertext", ""),
                    nonce=row.get("nonce", ""),
                    version=row.get("version", PatientService.VERSION),
                    created_at=created_at,
                ))
            for row in journals_res.data or []:
                try:
                    created_at = datetime.fromisoformat(row["created_at"]) if isinstance(row.get("created_at"), str) else row.get("created_at")
                except Exception:
                    created_at = datetime.now(timezone.utc)
                items.append(HistoryItem(
                    item_type="journal",
                    ciphertext=row.get("ciphertext", ""),
                    nonce=row.get("nonce", ""),
                    version=row.get("version", PatientService.VERSION),
                    created_at=created_at,
                ))

            # Merge-sort by created_at desc and take limit
            items.sort(key=lambda i: i.created_at, reverse=True)
            items = items[:limit]

            next_cursor = items[-1].created_at.isoformat() if len(items) == limit else None

            return {
                "status": "success",
                "result": HistoryResponse(items=items, next_cursor=next_cursor).dict()
            }
        except Exception as e:
            logger.error(f"get_history error: {e}")
            return {"status": "error", "message": f"get_history failed: {e}"}

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
    async def get_entry_by_date(user_id: str, date_str: str) -> Dict:
        """Get journal and mood entries for a specific date."""
        try:
            # Parse date
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            date_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            date_end = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
            
            # Fetch mood for the date
            mood_result = supabase_admin.table("moods")\
                .select("id, ciphertext, nonce, created_at")\
                .eq("user_id", user_id)\
                .gte("created_at", date_start.isoformat())\
                .lte("created_at", date_end.isoformat())\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            # Fetch journal for the date
            journal_result = supabase_admin.table("journals")\
                .select("id, ciphertext, nonce, created_at")\
                .eq("user_id", user_id)\
                .gte("created_at", date_start.isoformat())\
                .lte("created_at", date_end.isoformat())\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            data = {}
            
            # Process mood data
            if mood_result.data:
                mood_row = mood_result.data[0]
                decrypted_mood = PatientService._decrypt(mood_row["ciphertext"], mood_row["nonce"])
                try:
                    mood_data = json.loads(decrypted_mood)
                    data["mood"] = {
                        "id": mood_row["id"],
                        "emoji": mood_data.get("emoji", 3),
                        "note": mood_data.get("note", ""),
                        "created_at": mood_row["created_at"]
                    }
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse mood data for date {date_str}")
            
            # Process journal data
            if journal_result.data:
                journal_row = journal_result.data[0]
                decrypted_journal = PatientService._decrypt(journal_row["ciphertext"], journal_row["nonce"])
                try:
                    journal_data = json.loads(decrypted_journal)
                    data["journal"] = journal_data.get("text", "")
                    data["journal_id"] = journal_row["id"]
                    data["journal_created_at"] = journal_row["created_at"]
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse journal data for date {date_str}")
            
            return {
                "status": "success",
                "data": data
            }
            
        except ValueError as e:
            return {"status": "error", "message": f"Invalid date format. Use YYYY-MM-DD: {e}"}
        except Exception as e:
            logger.error(f"get_entry_by_date error: {e}")
            return {"status": "error", "message": f"get_entry_by_date failed: {e}"}

    # ---------------------- Upsert operations for today's entries ----------------------
    @staticmethod
    async def save_or_update_journal(user_id: str, data: JournalCreate) -> Dict:
        """Save or update today's journal entry (upsert)."""
        try:
            today = datetime.now(timezone.utc).date()
            date_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
            date_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
            
            # Check if entry exists for today
            existing_result = supabase_admin.table("journals")\
                .select("id")\
                .eq("user_id", user_id)\
                .gte("created_at", date_start.isoformat())\
                .lte("created_at", date_end.isoformat())\
                .limit(1)\
                .execute()
            
            # Prepare encrypted data
            text = data.text.strip()
            plaintext = json.dumps({"text": text})
            enc = PatientService._encrypt(plaintext)
            
            if existing_result.data:
                # Update existing entry
                entry_id = existing_result.data[0]["id"]
                update_payload = {
                    "ciphertext": enc.ciphertext,
                    "nonce": enc.nonce,
                    "version": enc.version,
                    "created_at": PatientService._now_iso(),  # Update timestamp
                }
                
                result = supabase_admin.table("journals")\
                    .update(update_payload)\
                    .eq("id", entry_id)\
                    .execute()
                
                if not result.data:
                    return {"status": "error", "message": "Failed to update journal"}
                
                return {
                    "status": "success",
                    "message": "Journal entry updated successfully",
                    "result": SaveResult(
                        id=str(entry_id),
                        created_at=datetime.fromisoformat(update_payload["created_at"]),
                        version=enc.version,
                    ).dict()
                }
            else:
                # Create new entry
                payload = {
                    "user_id": user_id,
                    "ciphertext": enc.ciphertext,
                    "nonce": enc.nonce,
                    "version": enc.version,
                    "created_at": PatientService._now_iso(),
                }
                
                result = supabase_admin.table("journals").insert(payload).execute()
                if not result.data:
                    return {"status": "error", "message": "Failed to save journal"}
                
                row = result.data[0]
                return {
                    "status": "success",
                    "message": "Journal entry saved successfully",
                    "result": SaveResult(
                        id=str(row.get("id")),
                        created_at=datetime.fromisoformat(row.get("created_at") or payload["created_at"]),
                        version=enc.version,
                    ).dict()
                }
                
        except Exception as e:
            logger.error(f"save_or_update_journal error: {e}")
            return {"status": "error", "message": f"save_or_update_journal failed: {e}"}

    @staticmethod
    async def save_or_update_mood(user_id: str, data: MoodCreate) -> Dict:
        """Save or update today's mood entry (upsert)."""
        try:
            today = datetime.now(timezone.utc).date()
            date_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
            date_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
            
            # Check if entry exists for today
            existing_result = supabase_admin.table("moods")\
                .select("id")\
                .eq("user_id", user_id)\
                .gte("created_at", date_start.isoformat())\
                .lte("created_at", date_end.isoformat())\
                .limit(1)\
                .execute()
            
            # Prepare encrypted data (include sleep data)
            mood_data = {
                "emoji": data.emoji, 
                "note": (data.note or "")
            }
            if data.sleep_hours is not None:
                mood_data["sleep_hours"] = data.sleep_hours
            
            plaintext = json.dumps(mood_data)
            enc = PatientService._encrypt(plaintext)
            
            if existing_result.data:
                # Update existing entry
                entry_id = existing_result.data[0]["id"]
                update_payload = {
                    "ciphertext": enc.ciphertext,
                    "nonce": enc.nonce,
                    "version": enc.version,
                    "created_at": PatientService._now_iso(),  # Update timestamp
                }
                
                result = supabase_admin.table("moods")\
                    .update(update_payload)\
                    .eq("id", entry_id)\
                    .execute()
                
                if not result.data:
                    return {"status": "error", "message": "Failed to update mood"}
                
                return {
                    "status": "success",
                    "message": "Mood updated successfully",
                    "result": SaveResult(
                        id=str(entry_id),
                        created_at=datetime.fromisoformat(update_payload["created_at"]),
                        version=enc.version,
                    ).dict()
                }
            else:
                # Create new entry
                payload = {
                    "user_id": user_id,
                    "ciphertext": enc.ciphertext,
                    "nonce": enc.nonce,
                    "version": enc.version,
                    "created_at": PatientService._now_iso(),
                }
                
                result = supabase_admin.table("moods").insert(payload).execute()
                if not result.data:
                    return {"status": "error", "message": "Failed to save mood"}
                
                row = result.data[0]
                return {
                    "status": "success",
                    "message": "Mood saved successfully",
                    "result": SaveResult(
                        id=str(row.get("id")),
                        created_at=datetime.fromisoformat(row.get("created_at") or payload["created_at"]),
                        version=enc.version,
                    ).dict()
                }
                
        except Exception as e:
            logger.error(f"save_or_update_mood error: {e}")
            return {"status": "error", "message": f"save_or_update_mood failed: {e}"}

    # ---------------------- Clinician Connections ----------------------
    @staticmethod
    async def get_user_connection_code(user_id: str) -> Dict:
        """Get user's unique connection code."""
        try:
            result = supabase_admin.table("user_connection_codes")\
                .select("connection_code, created_at")\
                .eq("user_id", user_id)\
                .limit(1)\
                .execute()
            
            if not result.data:
                return {"status": "error", "message": "Connection code not found"}
            
            return {
                "status": "success",
                "data": {
                    "connection_code": result.data[0]["connection_code"],
                    "created_at": result.data[0]["created_at"]
                }
            }
        except Exception as e:
            logger.error(f"get_user_connection_code error: {e}")
            return {"status": "error", "message": f"Failed to get connection code: {e}"}

    @staticmethod
    async def create_connection_request(clinician_id: str, patient_connection_code: Optional[str] = None, patient_email: Optional[str] = None) -> Dict:
        """Create a connection request from clinician to patient."""
        try:
            # Find patient by connection code or email
            patient_id = None
            
            if patient_connection_code:
                result = supabase_admin.table("user_connection_codes")\
                    .select("user_id")\
                    .eq("connection_code", patient_connection_code)\
                    .limit(1)\
                    .execute()
                
                if result.data:
                    patient_id = result.data[0]["user_id"]
            
            elif patient_email:
                # Query auth.users table for patient by email
                result = supabase_admin.auth.admin.list_users()
                for user in result:
                    if user.email == patient_email and user.user_metadata.get("role") == "regular_user":
                        patient_id = user.id
                        break
            
            if not patient_id:
                return {"status": "error", "message": "Patient not found"}
            
            # Check if connection already exists
            existing = supabase_admin.table("clinician_connections")\
                .select("id, status")\
                .eq("clinician_id", clinician_id)\
                .eq("patient_id", patient_id)\
                .limit(1)\
                .execute()
            
            if existing.data:
                status = existing.data[0]["status"]
                if status == "pending":
                    return {"status": "error", "message": "Connection request already pending"}
                elif status == "accepted":
                    return {"status": "error", "message": "Already connected to this patient"}
                elif status == "blocked":
                    return {"status": "error", "message": "Connection blocked by patient"}
            
            # Create connection request
            payload = {
                "clinician_id": clinician_id,
                "patient_id": patient_id,
                "status": "pending",
                "requested_at": PatientService._now_iso()
            }
            
            result = supabase_admin.table("clinician_connections").insert(payload).execute()
            
            if not result.data:
                return {"status": "error", "message": "Failed to create connection request"}
            
            return {
                "status": "success",
                "message": "Connection request sent successfully",
                "data": result.data[0]
            }
            
        except Exception as e:
            logger.error(f"create_connection_request error: {e}")
            return {"status": "error", "message": f"Failed to create connection request: {e}"}

    @staticmethod
    async def get_connection_requests(user_id: str, user_role: str) -> Dict:
        """Get connection requests for a user (clinician or patient)."""
        try:
            if user_role == "clinician":
                # Get requests sent by this clinician
                result = supabase_admin.table("clinician_connections")\
                    .select("*, patient:patient_id(email, full_name)")\
                    .eq("clinician_id", user_id)\
                    .order("requested_at", desc=True)\
                    .execute()
            else:
                # Get requests received by this patient
                result = supabase_admin.table("clinician_connections")\
                    .select("*, clinician:clinician_id(email, full_name)")\
                    .eq("patient_id", user_id)\
                    .order("requested_at", desc=True)\
                    .execute()
            
            return {
                "status": "success",
                "data": result.data or []
            }
            
        except Exception as e:
            logger.error(f"get_connection_requests error: {e}")
            return {"status": "error", "message": f"Failed to get connection requests: {e}"}

    @staticmethod
    async def respond_to_connection_request(connection_id: str, patient_id: str, action: str) -> Dict:
        """Patient responds to a connection request."""
        try:
            if action not in ["accept", "reject", "block"]:
                return {"status": "error", "message": "Invalid action"}
            
            # Verify the connection belongs to this patient
            existing = supabase_admin.table("clinician_connections")\
                .select("id, status")\
                .eq("id", connection_id)\
                .eq("patient_id", patient_id)\
                .limit(1)\
                .execute()
            
            if not existing.data:
                return {"status": "error", "message": "Connection request not found"}
            
            if existing.data[0]["status"] != "pending":
                return {"status": "error", "message": "Connection request is no longer pending"}
            
            # Update connection status
            update_payload = {
                "status": "accepted" if action == "accept" else action,
                "responded_at": PatientService._now_iso()
            }
            
            result = supabase_admin.table("clinician_connections")\
                .update(update_payload)\
                .eq("id", connection_id)\
                .execute()
            
            if not result.data:
                return {"status": "error", "message": "Failed to update connection request"}
            
            return {
                "status": "success",
                "message": f"Connection request {action}ed successfully",
                "data": result.data[0]
            }
            
        except Exception as e:
            logger.error(f"respond_to_connection_request error: {e}")
            return {"status": "error", "message": f"Failed to respond to connection request: {e}"}

    # ---------------------- Privacy Settings ----------------------
    @staticmethod
    async def get_privacy_settings(user_id: str) -> Dict:
        """Get user's privacy settings."""
        try:
            result = supabase_admin.table("privacy_settings")\
                .select("*")\
                .eq("user_id", user_id)\
                .limit(1)\
                .execute()
            
            if not result.data:
                # Create default privacy settings if they don't exist
                default_settings = {
                    "user_id": user_id,
                    "share_raw_text": False,
                    "share_summaries_only": True,
                    "allow_clinician_access": False
                }
                
                create_result = supabase_admin.table("privacy_settings").insert(default_settings).execute()
                
                if create_result.data:
                    return {"status": "success", "data": create_result.data[0]}
                else:
                    return {"status": "error", "message": "Failed to create default privacy settings"}
            
            return {"status": "success", "data": result.data[0]}
            
        except Exception as e:
            logger.error(f"get_privacy_settings error: {e}")
            return {"status": "error", "message": f"Failed to get privacy settings: {e}"}

    @staticmethod
    async def update_privacy_settings(user_id: str, settings: Dict) -> Dict:
        """Update user's privacy settings."""
        try:
            # Get existing settings
            existing = supabase_admin.table("privacy_settings")\
                .select("id")\
                .eq("user_id", user_id)\
                .limit(1)\
                .execute()
            
            update_payload = {
                "updated_at": PatientService._now_iso()
            }
            
            # Only update provided fields
            if "share_raw_text" in settings:
                update_payload["share_raw_text"] = settings["share_raw_text"]
            if "share_summaries_only" in settings:
                update_payload["share_summaries_only"] = settings["share_summaries_only"]
            if "allow_clinician_access" in settings:
                update_payload["allow_clinician_access"] = settings["allow_clinician_access"]
            
            if existing.data:
                # Update existing settings
                result = supabase_admin.table("privacy_settings")\
                    .update(update_payload)\
                    .eq("user_id", user_id)\
                    .execute()
            else:
                # Create new settings
                update_payload.update({
                    "user_id": user_id,
                    "share_raw_text": settings.get("share_raw_text", False),
                    "share_summaries_only": settings.get("share_summaries_only", True),
                    "allow_clinician_access": settings.get("allow_clinician_access", False)
                })
                result = supabase_admin.table("privacy_settings").insert(update_payload).execute()
            
            if not result.data:
                return {"status": "error", "message": "Failed to update privacy settings"}
            
            return {
                "status": "success",
                "message": "Privacy settings updated successfully",
                "data": result.data[0]
            }
            
        except Exception as e:
            logger.error(f"update_privacy_settings error: {e}")
            return {"status": "error", "message": f"Failed to update privacy settings: {e}"}
