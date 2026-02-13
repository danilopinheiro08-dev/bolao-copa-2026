from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Match, User
from app.schemas import AISuggestionResponse
from app.services.ai import AIService
from app.routes.predictions import get_current_user
from app.security.middleware import log_action, get_client_ip
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai"])

@router.get("/suggest/{match_id}", response_model=Optional[AISuggestionResponse])
async def get_ai_suggestion(
    match_id: int,
    style: str = Query("balanced", regex="^(conservative|balanced|aggressive)$"),
    request: Request = None,
    user: Optional[User] = Depends(get_current_user) = None,
    db: Session = Depends(get_db) = None
):
    """Get AI score suggestion for a match"""
    
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check quota
    if not AIService.has_quota(db, user.id):
        raise HTTPException(
            status_code=429,
            detail="Daily AI quota exceeded. You have 10 suggestions per day.",
            headers={"X-RateLimit-Reset": "tomorrow"}
        )
    
    # Get match
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Get suggestion
    ai_service = AIService()
    
    if not ai_service.is_available():
        logger.warning("AI service not available")
        raise HTTPException(
            status_code=503,
            detail="AI service currently unavailable. Please try again later."
        )
    
    suggestion = ai_service.get_match_suggestion(
        match=match,
        style=style,
        db=db,
        user_id=user.id,
        ip_address=get_client_ip(request)
    )
    
    if not suggestion:
        raise HTTPException(status_code=500, detail="Failed to generate suggestion")
    
    log_action(
        db=db,
        user_id=user.id,
        action="ai_suggestion_requested",
        resource_type="match",
        resource_id=match_id,
        request=request
    )
    
    return {
        "home_pred": suggestion.get("home_score", 1),
        "away_pred": suggestion.get("away_score", 1),
        "confidence": suggestion.get("confidence", 0.5),
        "reasoning": suggestion.get("reasoning", "AI suggestion based on available data"),
        "warning": "Use as reference only. Not guaranteed to be accurate.",
        "alternatives": suggestion.get("alternatives", [])
    }

@router.get("/health")
async def ai_service_health():
    """Check AI service health"""
    
    ai_service = AIService()
    
    return {
        "service": "groq_llama",
        "available": ai_service.is_available(),
        "status": "ok" if ai_service.is_available() else "unavailable",
    }
