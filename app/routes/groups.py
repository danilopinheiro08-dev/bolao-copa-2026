from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Group, GroupMember, User, Prediction, Match, GroupMemberRole
from app.schemas import GroupCreate, GroupResponse, GroupDetailResponse, GroupUpdate
from app.services.business import GroupService, UserService
from app.security.middleware import log_action
from app.routes.predictions import get_current_user
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/groups", tags=["groups"])

@router.post("", response_model=GroupResponse)
async def create_group(
    group_data: GroupCreate,
    request: Request,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new group"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    group = GroupService.create_group(db, user.id, group_data)
    
    log_action(
        db=db,
        user_id=user.id,
        action="group_created",
        resource_type="group",
        resource_id=group.id,
        request=request
    )
    
    return group

@router.get("", response_model=List[GroupResponse])
async def list_my_groups(
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List groups user is member of"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    groups = GroupService.get_user_groups(db, user.id, limit, offset)
    return groups

@router.get("/{group_id}", response_model=GroupDetailResponse)
async def get_group(
    group_id: int,
    db: Session = Depends(get_db)
):
    """Get group details"""
    group = GroupService.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    member_responses = []
    
    for member in members:
        user = UserService.get_user_by_id(db, member.user_id)
        if user:
            member_responses.append({
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "role": member.role.value,
                "joined_at": member.joined_at,
            })
    
    return {
        **GroupResponse.from_orm(group).dict(),
        "owner_id": group.owner_id,
        "members": member_responses,
        "member_count": len(member_responses),
    }

@router.post("/{group_id}/join")
async def join_group(
    group_id: int,
    join_code: Optional[str] = None,
    request: Request = None,
    user: Optional[User] = Depends(get_current_user) = None,
    db: Session = Depends(get_db) = None
):
    """Join a group"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    group = GroupService.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check join code if required
    if not group.is_public and group.join_code != join_code:
        raise HTTPException(status_code=403, detail="Invalid join code")
    
    # Add member
    member = GroupService.add_member_to_group(
        db=db,
        group_id=group_id,
        user_id=user.id,
        pending=group.requires_approval
    )
    
    if not member:
        raise HTTPException(status_code=400, detail="Already a member")
    
    log_action(
        db=db,
        user_id=user.id,
        action="group_joined",
        resource_type="group",
        resource_id=group_id,
        request=request
    )
    
    return {"message": "Joined group successfully" if not group.requires_approval else "Request sent for approval"}

@router.post("/{group_id}/leave")
async def leave_group(
    group_id: int,
    request: Request,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a group"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user.id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Not a member")
    
    # Can't leave if owner
    if member.role == GroupMemberRole.OWNER:
        raise HTTPException(status_code=400, detail="Owner cannot leave group")
    
    db.delete(member)
    db.commit()
    
    log_action(
        db=db,
        user_id=user.id,
        action="group_left",
        resource_type="group",
        resource_id=group_id,
        request=request
    )
    
    return {"message": "Left group"}

@router.get("/{group_id}/standings")
async def get_group_standings(
    group_id: int,
    db: Session = Depends(get_db)
):
    """Get group standings/ranking"""
    from app.services.ranking import RankingService
    
    standings = RankingService.get_group_standings(db, group_id)
    if not standings:
        # Return empty standings if not computed yet
        standings = {
            "scope": f"GROUP:{group_id}",
            "standings": [],
            "computed_at": None,
            "match_count": 0,
        }
    
    return standings
