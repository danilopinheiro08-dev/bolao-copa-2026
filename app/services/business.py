from sqlalchemy.orm import Session
from app.models import User, Group, GroupMember, GroupMemberRole, Match, Prediction, MatchStatus
from app.schemas import GroupCreate, GroupUpdate, PredictionCreate, PredictionUpdate
from app.security.crypto import hash_password, verify_password, generate_join_code, generate_session_token
from datetime import datetime, timezone, timedelta
import logging
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

class UserService:
    """Service for user operations"""
    
    @staticmethod
    def create_user(db: Session, email: str, name: str, password: str, provider: str = "email") -> Optional[User]:
        """Create new user"""
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return None
        
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password) if password else None,
            provider=provider,
            email_verified=provider != "email"  # OAuth users auto-verified
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = db.query(User).filter(User.email == email, User.is_active == True).first()
        if not user or not user.password_hash:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email, User.is_active == True).first()

class GroupService:
    """Service for group operations"""
    
    @staticmethod
    def create_group(db: Session, owner_id: int, create_data: GroupCreate) -> Group:
        """Create new group"""
        # Generate slug from name
        slug = create_data.name.lower().replace(" ", "-")[:50]
        
        # Ensure unique slug
        existing = db.query(Group).filter(
            Group.owner_id == owner_id,
            Group.slug == slug
        ).first()
        
        if existing:
            slug = f"{slug}-{generate_join_code(4)}"
        
        group = Group(
            name=create_data.name,
            slug=slug,
            description=create_data.description,
            owner_id=owner_id,
            is_public=create_data.is_public,
            requires_approval=create_data.requires_approval,
            max_members=create_data.max_members,
            join_code=generate_join_code() if not create_data.is_public else None,
        )
        
        db.add(group)
        db.flush()
        
        # Add owner as member
        member = GroupMember(
            group_id=group.id,
            user_id=owner_id,
            role=GroupMemberRole.OWNER,
        )
        db.add(member)
        db.commit()
        db.refresh(group)
        
        return group
    
    @staticmethod
    def get_group(db: Session, group_id: int) -> Optional[Group]:
        """Get group by ID"""
        return db.query(Group).filter(Group.id == group_id, Group.is_active == True).first()
    
    @staticmethod
    def get_group_by_slug_and_code(db: Session, slug: str, join_code: str) -> Optional[Group]:
        """Get group by slug and join code"""
        return db.query(Group).filter(
            Group.slug == slug,
            Group.join_code == join_code,
            Group.is_active == True
        ).first()
    
    @staticmethod
    def add_member_to_group(db: Session, group_id: int, user_id: int, role: str = "member", pending: bool = False) -> Optional[GroupMember]:
        """Add member to group"""
        # Check if already member
        existing = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        ).first()
        
        if existing:
            return None
        
        member = GroupMember(
            group_id=group_id,
            user_id=user_id,
            role=GroupMemberRole(role),
            pending_approval=pending,
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member
    
    @staticmethod
    def get_user_groups(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> List[Group]:
        """Get groups user is member of"""
        return db.query(Group).join(GroupMember).filter(
            GroupMember.user_id == user_id,
            GroupMember.is_active == True,
            Group.is_active == True
        ).limit(limit).offset(offset).all()

class PredictionService:
    """Service for prediction operations"""
    
    @staticmethod
    def create_prediction(db: Session, user_id: int, create_data: PredictionCreate) -> Optional[Prediction]:
        """Create new prediction"""
        # Check if match exists and get it
        match = db.query(Match).filter(Match.id == create_data.match_id).first()
        if not match:
            return None
        
        # Check if prediction already exists
        existing = db.query(Prediction).filter(
            Prediction.user_id == user_id,
            Prediction.match_id == create_data.match_id,
            Prediction.group_id == create_data.group_id
        ).first()
        
        if existing and existing.is_locked:
            return None  # Can't modify locked prediction
        
        # Check if match is locked (too close to kickoff)
        if PredictionService.is_match_locked(match):
            return None
        
        if existing:
            # Update existing
            existing.home_pred = create_data.home_pred
            existing.away_pred = create_data.away_pred
            existing.advance_team = create_data.advance_team
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new
            prediction = Prediction(
                user_id=user_id,
                match_id=create_data.match_id,
                group_id=create_data.group_id,
                home_pred=create_data.home_pred,
                away_pred=create_data.away_pred,
                advance_team=create_data.advance_team,
            )
            db.add(prediction)
            db.commit()
            db.refresh(prediction)
            return prediction
    
    @staticmethod
    def is_match_locked(match: Match, lock_minutes: int = 10) -> bool:
        """Check if match prediction is locked (10 minutes before kickoff)."""
        now = datetime.now(timezone.utc)
        kickoff = match.kickoff_at_utc

        # SQLite stores datetimes without timezone info; normalise to UTC
        if kickoff.tzinfo is None:
            kickoff = kickoff.replace(tzinfo=timezone.utc)

        lock_threshold = kickoff - timedelta(minutes=lock_minutes)
        return now >= lock_threshold
    
    @staticmethod
    def get_prediction(db: Session, prediction_id: int) -> Optional[Prediction]:
        """Get prediction by ID"""
        return db.query(Prediction).filter(Prediction.id == prediction_id).first()
    
    @staticmethod
    def get_user_predictions_for_match(db: Session, user_id: int, match_id: int) -> List[Prediction]:
        """Get all user predictions for a match (global + per group)"""
        return db.query(Prediction).filter(
            Prediction.user_id == user_id,
            Prediction.match_id == match_id
        ).all()
    
    @staticmethod
    def get_upcoming_matches_without_prediction(db: Session, user_id: int, limit: int = 5) -> List[Match]:
        """Get upcoming matches where user hasn't made predictions"""
        now = datetime.now(timezone.utc)
        
        # Find all upcoming matches
        upcoming = db.query(Match).filter(
            Match.kickoff_at_utc > now,
            Match.status == MatchStatus.SCHEDULED
        ).order_by(Match.kickoff_at_utc).limit(limit).all()
        
        # Filter to ones without predictions
        matches_without_pred = []
        for match in upcoming:
            has_pred = db.query(Prediction).filter(
                Prediction.user_id == user_id,
                Prediction.match_id == match.id
            ).first()
            
            if not has_pred:
                matches_without_pred.append(match)
        
        return matches_without_pred[:limit]

class ScoringService:
    """Service for scoring predictions"""
    
    # Scoring rules
    POINTS_EXACT = 5
    POINTS_RESULT_BALANCE = 3
    POINTS_RESULT_ONLY = 2
    POINTS_ADVANCE = 2
    
    @staticmethod
    def calculate_points(prediction: Prediction, match: Match) -> Tuple[int, dict]:
        """Calculate points for a prediction"""
        if match.status != MatchStatus.FINISHED or match.home_score is None:
            return 0, {}
        
        home_score = match.home_score
        away_score = match.away_score
        home_pred = prediction.home_pred
        away_pred = prediction.away_pred
        
        details = {
            "exact": False,
            "result": False,
            "balance": False,
        }
        
        points = 0
        
        # Exact score
        if home_pred == home_score and away_pred == away_score:
            points = ScoringService.POINTS_EXACT
            details["exact"] = True
            return points, details
        
        # Result (winner/draw)
        pred_result = "draw" if home_pred == away_pred else ("home" if home_pred > away_pred else "away")
        actual_result = "draw" if home_score == away_score else ("home" if home_score > away_score else "away")
        
        if pred_result == actual_result:
            details["result"] = True
            
            # Balance (goal difference)
            pred_balance = home_pred - away_pred
            actual_balance = home_score - away_score
            
            if pred_balance == actual_balance:
                points = ScoringService.POINTS_RESULT_BALANCE
                details["balance"] = True
            else:
                points = ScoringService.POINTS_RESULT_ONLY
        
        return points, details
    
    @staticmethod
    def get_tiebreaker_order(
        users_with_points: List[Tuple[int, int]],
        db: Optional[Session] = None,
    ) -> List[int]:
        """
        Sort users by tiebreaker rules.

        Input: [(user_id, total_points), ...]
        Returns: sorted list of user_ids (best first)

        Tiebreaker criteria (in order):
          1. Total points (desc)
          2. Exact score count (desc)
          3. Correct result count (desc)
          4. Absolute goal-difference error sum (asc — lower is better)
        """
        if not db:
            # Fallback: sort by points only
            return [uid for uid, _ in sorted(users_with_points, key=lambda x: x[1], reverse=True)]

        enriched = []
        for user_id, total_points in users_with_points:
            preds = db.query(Prediction).filter(Prediction.user_id == user_id).all()
            exact_count = 0
            result_count = 0
            abs_error_sum = 0

            for pred in preds:
                details = pred.score_details or {}
                if details.get("exact"):
                    exact_count += 1
                if details.get("result"):
                    result_count += 1
                # Absolute error = |home_diff_pred - home_diff_actual|
                if pred.match and pred.match.home_score is not None:
                    abs_error_sum += abs(
                        (pred.home_pred - pred.away_pred)
                        - (pred.match.home_score - pred.match.away_score)
                    )

            enriched.append((user_id, total_points, exact_count, result_count, abs_error_sum))

        enriched.sort(key=lambda x: (-x[1], -x[2], -x[3], x[4]))
        return [row[0] for row in enriched]
