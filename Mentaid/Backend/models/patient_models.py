"""
Pydantic models for patient mood and journal features.
Includes request/response schemas and pagination models.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, List
from datetime import datetime


class MoodCreate(BaseModel):
    """Request model to create a mood entry (emoji scale 1–5) with optional sleep tracking."""
    emoji: int = Field(..., ge=1, le=5, description="Emoji/mood level from 1 (low) to 5 (high)")
    note: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional short note to accompany the mood entry",
    )
    sleep_hours: Optional[float] = Field(
        None,
        ge=0,
        le=24,
        description="Hours of sleep (0-24 hours, can include decimals for minutes)"
    )


class JournalCreate(BaseModel):
    """Request model to create a journal entry."""
    text: str = Field(..., min_length=1, max_length=5000)

    @validator("text")
    def validate_text(cls, v: str) -> str:
        # Simple normalization; sanitization happens server-side in services.
        v = v.strip()
        if not v:
            raise ValueError("Journal text cannot be empty")
        return v


class EncryptResult(BaseModel):
    """Internal structure to represent encryption output."""
    ciphertext: str
    nonce: str
    version: str = "v1"


class HistoryQuery(BaseModel):
    """Query model for paginated history requests."""
    limit: int = Field(20, ge=1, le=100, description="Number of items to return")
    cursor: Optional[str] = Field(
        None,
        description="Opaque pagination cursor (e.g., created_at|id)",
    )


class HistoryItem(BaseModel):
    """Unified history item for either mood or journal entries."""
    item_type: Literal["mood", "journal"]
    ciphertext: str
    nonce: str
    version: str
    created_at: datetime


class HistoryResponse(BaseModel):
    """Paginated response for history API."""
    items: List[HistoryItem]
    next_cursor: Optional[str] = None


# Optional response models for save operations (kept minimal and consistent)
class SaveResult(BaseModel):
    """Standard save result payload without exposing plaintext."""
    id: str
    created_at: datetime
    version: str = "v1"


# Clinician Connection Models
class ConnectionRequest(BaseModel):
    """Request model to create a clinician-patient connection."""
    patient_connection_code: Optional[str] = Field(None, description="Patient's unique connection code")
    patient_email: Optional[str] = Field(None, description="Patient's email for search")
    
    @validator('patient_connection_code', 'patient_email')
    def validate_connection_method(cls, v, values):
        """Ensure at least one connection method is provided."""
        if not v and not values.get('patient_connection_code') and not values.get('patient_email'):
            raise ValueError("Either patient_connection_code or patient_email must be provided")
        return v


class ConnectionResponse(BaseModel):
    """Response model for connection requests."""
    action: Literal["accept", "reject", "block"]


class ConnectionInfo(BaseModel):
    """Model for connection information."""
    id: str
    clinician_id: str
    patient_id: str
    clinician_name: Optional[str] = None
    patient_name: Optional[str] = None
    clinician_email: Optional[str] = None
    patient_email: Optional[str] = None
    status: str
    requested_at: datetime
    responded_at: Optional[datetime] = None


class UserConnectionCode(BaseModel):
    """Model for user connection code."""
    connection_code: str
    created_at: datetime


# Privacy Settings Models
class PrivacySettingsUpdate(BaseModel):
    """Request model to update privacy settings."""
    share_raw_text: Optional[bool] = None
    share_summaries_only: Optional[bool] = None
    allow_clinician_access: Optional[bool] = None


class PrivacySettings(BaseModel):
    """Model for privacy settings."""
    id: str
    user_id: str
    share_raw_text: bool
    share_summaries_only: bool
    allow_clinician_access: bool
    created_at: datetime
    updated_at: datetime
