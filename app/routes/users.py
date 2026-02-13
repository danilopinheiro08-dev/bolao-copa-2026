from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User, Match, MatchStatus
from app.schemas import UserResponse, UserProfileUpdate
from app.services.ai import AIService
from app.routes.predictions import get_current_user
from app.security.middleware import log_action
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    user: Optional[User] = Depends(get_current_user)
):
    """Get current user profile"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return user

@router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserProfileUpdate,
    request: Request,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if update_data.name:
        user.name = update_data.name
    if update_data.avatar_url:
        user.avatar_url = update_data.avatar_url
    if update_data.timezone:
        user.timezone = update_data.timezone
    
    db.commit()
    db.refresh(user)
    
    log_action(
        db=db,
        user_id=user.id,
        action="profile_updated",
        request=request
    )
    
    return user

@router.get("/me/stats")
async def get_user_stats(
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from app.models import Prediction
    from sqlalchemy import func
    
    # Count predictions
    total_predictions = db.query(Prediction).filter(Prediction.user_id == user.id).count()
    
    # Count exact matches
    exact_matches = db.query(Prediction).filter(
        Prediction.user_id == user.id,
        Prediction.score_details['exact'].astext == 'true'
    ).count()
    
    # Sum points
    total_points = db.query(func.sum(Prediction.points_awarded)).filter(
        Prediction.user_id == user.id
    ).scalar() or 0
    
    # Count groups
    from app.models import GroupMember
    group_count = db.query(GroupMember).filter(
        GroupMember.user_id == user.id,
        GroupMember.is_active == True
    ).count()
    
    return {
        "total_predictions": total_predictions,
        "exact_matches": exact_matches,
        "total_points": total_points,
        "groups_count": group_count,
    }

@router.get("/me/ai-quota")
async def check_ai_quota(
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check AI suggestion quota"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    remaining = AIService.check_quota(db, user.id)
    quota_per_day = 10  # From config
    
    return {
        "remaining": remaining,
        "quota_per_day": quota_per_day,
        "has_quota": remaining > 0,
    }

@router.get("/rankings/global")
async def get_global_standings(
    db: Session = Depends(get_db)
):
    """Get global standings"""
    from app.services.ranking import RankingService
    
    standings = RankingService.get_global_standings(db)
    if not standings:
        standings = {
            "scope": "GLOBAL",
            "standings": [],
            "computed_at": None,
            "match_count": 0,
        }
    
    return standings
