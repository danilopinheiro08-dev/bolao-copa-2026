from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User, Match, MatchStatus, Group
from app.schemas import MatchUpdateAdmin
from app.routes.predictions import get_current_user
from app.security.middleware import log_action
from app.providers.data import FixtureImporter, ManualProvider, APIProvider
from app.services.ranking import RankingService
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Admin middleware
async def require_admin(
    user: Optional[User] = Depends(get_current_user)
):
    """Require admin user"""
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.put("/matches/{match_id}", response_model=dict)
async def update_match_admin(
    match_id: int,
    update_data: MatchUpdateAdmin,
    request: Request,
    admin: Optional[User] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Update match result manually"""
    
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Update score
    match.home_score = update_data.home_score
    match.away_score = update_data.away_score
    match.status = MatchStatus.FINISHED if update_data.status == "FT" else MatchStatus(update_data.status)
    
    if update_data.home_score_et is not None:
        match.home_score_et = update_data.home_score_et
    if update_data.away_score_et is not None:
        match.away_score_et = update_data.away_score_et
    if update_data.home_score_pen is not None:
        match.home_score_pen = update_data.home_score_pen
    if update_data.away_score_pen is not None:
        match.away_score_pen = update_data.away_score_pen
    
    from datetime import datetime, timezone
    match.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(match)
    
    # Recalculate ranking
    RankingService.recalculate_global_ranking(db)
    
    # Get affected groups and recalculate
    from app.models import Prediction
    affected_groups = db.query(Prediction.group_id).filter(
        Prediction.match_id == match_id,
        Prediction.group_id.isnot(None)
    ).distinct().all()
    
    for (group_id,) in affected_groups:
        if group_id:
            RankingService.recalculate_group_ranking(db, group_id)
    
    log_action(
        db=db,
        user_id=admin.id,
        action="match_updated_admin",
        resource_type="match",
        resource_id=match_id,
        request=request,
        details=update_data.dict()
    )
    
    return {
        "message": "Match updated",
        "match_id": match_id,
        "status": match.status.value,
        "score": f"{match.home_score}-{match.away_score}",
    }

@router.post("/fixtures/import-json")
async def import_fixtures_json(
    file: UploadFile = File(...),
    admin: Optional[User] = Depends(require_admin) = None,
    db: Session = Depends(get_db) = None
):
    """Admin: Import fixtures from JSON file"""
    
    try:
        content = await file.read()
        data = json.loads(content)
        
        # Create manual provider and import
        provider = ManualProvider()
        provider.fixtures = data.get('matches', [])
        
        importer = FixtureImporter(provider)
        count = importer.import_fixtures(db)
        
        log_action(
            db=db,
            user_id=admin.id,
            action="fixtures_imported",
            details={"count": count, "filename": file.filename}
        )
        
        return {
            "message": f"Imported {count} fixtures",
            "count": count
        }
    
    except Exception as e:
        logger.error(f"Error importing fixtures: {e}")
        raise HTTPException(status_code=400, detail=f"Import error: {str(e)}")

@router.post("/fixtures/update-results")
async def update_results_from_api(
    admin: Optional[User] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Update results from sports API"""
    
    from app.config import settings
    
    if settings.SPORTS_API_PROVIDER == "manual":
        raise HTTPException(status_code=400, detail="Manual provider - cannot auto-update")
    
    try:
        # Create API provider
        provider = APIProvider(
            api_key=settings.SPORTS_API_KEY or "demo",
            api_url=settings.SPORTS_API_URL
        )
        
        importer = FixtureImporter(provider)
        count = importer.update_results(db)
        
        # Recalculate rankings
        RankingService.recalculate_global_ranking(db)
        
        log_action(
            db=db,
            user_id=admin.id,
            action="results_updated_api",
            details={"count": count}
        )
        
        return {
            "message": f"Updated {count} results",
            "count": count
        }
    
    except Exception as e:
        logger.error(f"Error updating results: {e}")
        raise HTTPException(status_code=400, detail=f"Update error: {str(e)}")

@router.post("/recalculate-rankings")
async def recalculate_all_rankings(
    admin: Optional[User] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Recalculate all rankings"""
    
    try:
        # Global
        RankingService.recalculate_global_ranking(db)
        
        # All groups
        groups = db.query(Group).all()
        for group in groups:
            RankingService.recalculate_group_ranking(db, group.id)
        
        log_action(
            db=db,
            user_id=admin.id,
            action="rankings_recalculated"
        )
        
        return {
            "message": "Rankings recalculated",
            "groups_count": len(groups)
        }
    
    except Exception as e:
        logger.error(f"Error recalculating rankings: {e}")
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@router.get("/status")
async def get_system_status(
    admin: Optional[User] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get system status"""
    
    from datetime import datetime, timezone
    from app.models import Match
    
    finished_matches = db.query(Match).filter(Match.status == MatchStatus.FINISHED).count()
    total_matches = db.query(Match).count()
    
    from app.models import Prediction
    total_predictions = db.query(Prediction).count()
    
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "matches": {
            "total": total_matches,
            "finished": finished_matches,
            "pending": total_matches - finished_matches,
        },
        "predictions": {
            "total": total_predictions,
        },
        "ai_service": {
            "available": True,  # TODO: Check Groq availability
        }
    }
