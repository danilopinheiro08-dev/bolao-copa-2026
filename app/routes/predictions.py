from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Match, MatchStatus, Prediction, User
from app.schemas import MatchResponse, PredictionResponse, PredictionCreate, PredictionUpdate
from app.services.business import PredictionService, UserService
from app.security.middleware import log_action, get_client_ip
from datetime import datetime, timezone
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["matches", "predictions"])

# Dependency for current user
async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Get current user from token"""
    from app.security.crypto import decode_token
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    
    if not payload:
        return None
    
    user_id = int(payload.get("sub"))
    return UserService.get_user_by_id(db, user_id)

@router.get("/matches", response_model=List[MatchResponse])
async def list_matches(
    stage: Optional[str] = Query(None),
    group: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """List matches with filters"""
    query = db.query(Match)
    
    if stage:
        query = query.filter(Match.stage == stage)
    
    if group:
        query = query.filter(Match.group_name == group)
    
    matches = query.order_by(Match.kickoff_at_utc).limit(limit).offset(offset).all()
    return matches

@router.get("/matches/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: int,
    db: Session = Depends(get_db)
):
    """Get single match"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@router.get("/matches/{match_id}/predictions")
async def get_match_predictions(
    match_id: int,
    group_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all predictions for a match (by group)"""
    query = db.query(Prediction).filter(Prediction.match_id == match_id)
    
    if group_id:
        query = query.filter(Prediction.group_id == group_id)
    else:
        query = query.filter(Prediction.group_id.is_(None))
    
    predictions = query.all()
    
    result = []
    for pred in predictions:
        user = db.query(User).filter(User.id == pred.user_id).first()
        result.append({
            "user_id": pred.user_id,
            "user_name": user.name if user else "Unknown",
            "home_pred": pred.home_pred,
            "away_pred": pred.away_pred,
            "points": pred.points_awarded,
        })
    
    return result

# Predictions
@router.post("/predictions", response_model=PredictionResponse)
async def create_prediction(
    pred_data: PredictionCreate,
    request: Request,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update prediction"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    prediction = PredictionService.create_prediction(db, user.id, pred_data)
    
    if not prediction:
        raise HTTPException(status_code=400, detail="Cannot create prediction - match locked or invalid")
    
    log_action(
        db=db,
        user_id=user.id,
        action="prediction_created",
        resource_type="prediction",
        resource_id=prediction.id,
        request=request
    )
    
    return prediction

@router.put("/predictions/{prediction_id}", response_model=PredictionResponse)
async def update_prediction(
    prediction_id: int,
    update_data: PredictionUpdate,
    request: Request,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update prediction"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    prediction = PredictionService.get_prediction(db, prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    if prediction.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    if prediction.is_locked:
        raise HTTPException(status_code=400, detail="Prediction is locked")
    
    # Update fields
    prediction.home_pred = update_data.home_pred
    prediction.away_pred = update_data.away_pred
    if update_data.advance_team:
        prediction.advance_team = update_data.advance_team
    prediction.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(prediction)
    
    log_action(
        db=db,
        user_id=user.id,
        action="prediction_updated",
        resource_type="prediction",
        resource_id=prediction.id,
        request=request
    )
    
    return prediction

@router.get("/my/predictions")
async def get_my_predictions(
    match_id: Optional[int] = None,
    group_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's predictions"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    query = db.query(Prediction).filter(Prediction.user_id == user.id)
    
    if match_id:
        query = query.filter(Prediction.match_id == match_id)
    
    if group_id is not None:
        query = query.filter(Prediction.group_id == group_id)
    
    predictions = query.limit(limit).offset(offset).all()
    
    result = []
    for pred in predictions:
        match = db.query(Match).filter(Match.id == pred.match_id).first()
        result.append({
            "prediction": PredictionResponse.model_validate(pred).model_dump(mode="json"),
            "match": MatchResponse.model_validate(match).model_dump(mode="json") if match else None,
        })

    return result

@router.get("/my/upcoming")
async def get_my_upcoming_matches(
    limit: int = 5,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming matches without predictions for current user"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    matches = PredictionService.get_upcoming_matches_without_prediction(db, user.id, limit)
    
    return [MatchResponse.model_validate(m).model_dump(mode="json") for m in matches]
