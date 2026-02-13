from sqlalchemy.orm import Session
from app.models import Prediction, Match, MatchStatus, Group, User, StandingsCache
from app.services.business import ScoringService
from datetime import datetime, timezone
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class RankingService:
    """Service for calculating and caching rankings"""
    
    @staticmethod
    def recalculate_global_ranking(db: Session):
        """Recalculate global ranking"""
        try:
            # Get all finished matches
            finished_matches = db.query(Match).filter(
                Match.status == MatchStatus.FINISHED
            ).all()
            
            if not finished_matches:
                logger.info("No finished matches to calculate ranking")
                return
            
            # Get all predictions
            all_predictions = db.query(Prediction).all()
            
            # Calculate scores for each user
            user_scores = {}
            for pred in all_predictions:
                if pred.user_id not in user_scores:
                    user_scores[pred.user_id] = {
                        "total_points": 0,
                        "exact_matches": 0,
                        "correct_results": 0,
                    }
                
                # Find matching match
                match = next((m for m in finished_matches if m.id == pred.match_id), None)
                if match:
                    points, details = ScoringService.calculate_points(pred, match)
                    user_scores[pred.user_id]["total_points"] += points
                    
                    if details.get("exact"):
                        user_scores[pred.user_id]["exact_matches"] += 1
                    if details.get("result"):
                        user_scores[pred.user_id]["correct_results"] += 1
                    
                    # Update prediction points
                    pred.points_awarded = points
                    pred.score_details = details
            
            db.commit()
            
            # Build standings
            standings = []
            for user_id, scores in user_scores.items():
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    standings.append({
                        "user_id": user_id,
                        "name": user.name,
                        "avatar_url": user.avatar_url,
                        "exact_matches": scores["exact_matches"],
                        "correct_results": scores["correct_results"],
                        "total_points": scores["total_points"],
                        "rank": 0,  # Will be assigned after sorting
                    })
            
            # Sort by points (and apply tiebreakers)
            standings.sort(
                key=lambda x: (x["total_points"], x["exact_matches"], x["correct_results"]),
                reverse=True
            )
            
            # Assign ranks
            for idx, s in enumerate(standings):
                s["rank"] = idx + 1
            
            # Save to cache
            cache = db.query(StandingsCache).filter(StandingsCache.scope == "GLOBAL").first()
            if not cache:
                cache = StandingsCache(scope="GLOBAL")
                db.add(cache)
            
            cache.standings_data = standings
            cache.computed_at = datetime.now(timezone.utc)
            db.commit()
            
            logger.info(f"Global ranking recalculated with {len(standings)} users")
        
        except Exception as e:
            logger.error(f"Error calculating global ranking: {e}")
            db.rollback()
    
    @staticmethod
    def recalculate_group_ranking(db: Session, group_id: int):
        """Recalculate ranking for a group"""
        try:
            group = db.query(Group).filter(Group.id == group_id).first()
            if not group:
                return
            
            # Get all predictions for this group
            group_predictions = db.query(Prediction).filter(
                Prediction.group_id == group_id
            ).all()
            
            # Get finished matches
            finished_matches = db.query(Match).filter(
                Match.status == MatchStatus.FINISHED
            ).all()
            
            # Calculate scores
            user_scores = {}
            for pred in group_predictions:
                if pred.user_id not in user_scores:
                    user_scores[pred.user_id] = {
                        "total_points": 0,
                        "exact_matches": 0,
                        "correct_results": 0,
                    }
                
                # Find matching match
                match = next((m for m in finished_matches if m.id == pred.match_id), None)
                if match:
                    points, details = ScoringService.calculate_points(pred, match)
                    user_scores[pred.user_id]["total_points"] += points
                    
                    if details.get("exact"):
                        user_scores[pred.user_id]["exact_matches"] += 1
                    if details.get("result"):
                        user_scores[pred.user_id]["correct_results"] += 1
            
            # Build standings
            standings = []
            for user_id, scores in user_scores.items():
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    standings.append({
                        "user_id": user_id,
                        "name": user.name,
                        "avatar_url": user.avatar_url,
                        "exact_matches": scores["exact_matches"],
                        "correct_results": scores["correct_results"],
                        "total_points": scores["total_points"],
                        "rank": 0,
                    })
            
            # Sort
            standings.sort(
                key=lambda x: (x["total_points"], x["exact_matches"], x["correct_results"]),
                reverse=True
            )
            
            # Assign ranks
            for idx, s in enumerate(standings):
                s["rank"] = idx + 1
            
            # Save to cache
            scope = f"GROUP:{group_id}"
            cache = db.query(StandingsCache).filter(StandingsCache.scope == scope).first()
            if not cache:
                cache = StandingsCache(scope=scope, group_id=group_id)
                db.add(cache)
            
            cache.standings_data = standings
            cache.computed_at = datetime.now(timezone.utc)
            db.commit()
            
            logger.info(f"Group {group_id} ranking recalculated with {len(standings)} users")
        
        except Exception as e:
            logger.error(f"Error calculating group {group_id} ranking: {e}")
            db.rollback()
    
    @staticmethod
    def get_global_standings(db: Session) -> Optional[Dict]:
        """Get cached global standings"""
        cache = db.query(StandingsCache).filter(StandingsCache.scope == "GLOBAL").first()
        if cache:
            return {
                "scope": "GLOBAL",
                "standings": cache.standings_data,
                "computed_at": cache.computed_at,
                "match_count": db.query(Match).filter(Match.status == MatchStatus.FINISHED).count(),
            }
        return None
    
    @staticmethod
    def get_group_standings(db: Session, group_id: int) -> Optional[Dict]:
        """Get cached group standings"""
        scope = f"GROUP:{group_id}"
        cache = db.query(StandingsCache).filter(StandingsCache.scope == scope).first()
        if cache:
            return {
                "scope": f"GROUP:{group_id}",
                "standings": cache.standings_data,
                "computed_at": cache.computed_at,
                "match_count": db.query(Match).filter(Match.status == MatchStatus.FINISHED).count(),
            }
        return None
