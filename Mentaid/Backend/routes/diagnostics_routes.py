from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from middleware.auth_middleware import get_current_user
from models.user_models import TokenData
from services.diagnostics_service import DiagnosticsService


router = APIRouter(prefix="/diagnostics", tags=["Diagnostics"])
service = DiagnosticsService()


class PredictRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    journal_text: str = Field(..., min_length=5, description="Free-text input from the user")


@router.post("/predict")
async def predict_disorder(
    body: PredictRequest,
    current_user: TokenData = Depends(get_current_user)
):
    try:
        result = service.predict_from_text(body.user_id, body.journal_text)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


class InteractiveStartRequest(BaseModel):
    user_id: str
    context_text: Optional[str] = Field(None, description="Optional short text to seed context")


@router.post("/interactive/start")
async def start_interactive(
    body: InteractiveStartRequest,
    current_user: TokenData = Depends(get_current_user)
):
    try:
        start = service.start_interactive(body.user_id, body.context_text)
        return {"status": "in_progress", **start}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interactive flow: {str(e)}")


class InteractiveAnswerRequest(BaseModel):
    session_id: str
    answer: str = Field(..., description="yes or no")


@router.post("/interactive/answer")
async def answer_interactive(
    body: InteractiveAnswerRequest,
    current_user: TokenData = Depends(get_current_user)
):
    try:
        nxt = service.answer_interactive(body.session_id, body.answer)
        return {"status": "in_progress" if "final" not in nxt else "complete", **nxt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process answer: {str(e)}")


