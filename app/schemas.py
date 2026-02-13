from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Enums
class MatchStageEnum(str, Enum):
    GROUP = "GROUP"
    R32 = "R32"
    R16 = "R16"
    QF = "QF"
    SF = "SF"
    THIRD = "THIRD"
    FINAL = "FINAL"

class MatchStatusEnum(str, Enum):
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    FT = "FT"
    CANCELLED = "CANCELLED"

# User Schemas
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserPasswordReset(BaseModel):
    email: EmailStr

class UserPasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    uuid: str
    name: str
    email: str
    email_verified: bool
    avatar_url: Optional[str]
    timezone: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Group Schemas
class GroupCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    is_public: bool = False
    requires_approval: bool = False
    max_members: Optional[int] = None

class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    requires_approval: Optional[bool] = None
    max_members: Optional[int] = None

class GroupMemberResponse(BaseModel):
    user_id: int
    name: str
    email: str
    avatar_url: Optional[str]
    role: str
    joined_at: datetime

class GroupResponse(BaseModel):
    id: int
    uuid: str
    name: str
    slug: str
    description: Optional[str]
    is_public: bool
    requires_approval: bool
    max_members: Optional[int]
    join_code: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class GroupDetailResponse(GroupResponse):
    owner_id: int
    members: List[GroupMemberResponse]
    member_count: int

# Match Schemas
class MatchResponse(BaseModel):
    id: int
    uuid: str
    fifa_match_code: Optional[str]
    stage: str
    group_name: Optional[str]
    match_order: int
    home_team: str
    away_team: str
    home_team_code: Optional[str]
    away_team_code: Optional[str]
    kickoff_at_utc: datetime
    venue: Optional[str]
    city: Optional[str]
    status: str
    home_score: Optional[int]
    away_score: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Prediction Schemas
class PredictionCreate(BaseModel):
    match_id: int
    home_pred: int = Field(..., ge=0, le=20)
    away_pred: int = Field(..., ge=0, le=20)
    advance_team: Optional[str] = None
    group_id: Optional[int] = None

class PredictionUpdate(BaseModel):
    home_pred: int = Field(..., ge=0, le=20)
    away_pred: int = Field(..., ge=0, le=20)
    advance_team: Optional[str] = None

class PredictionResponse(BaseModel):
    id: int
    uuid: str
    user_id: int
    match_id: int
    group_id: Optional[int]
    home_pred: int
    away_pred: int
    advance_team: Optional[str]
    points_awarded: int
    is_locked: bool
    locked_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PredictionWithMatchResponse(PredictionResponse):
    match: MatchResponse
    user_name: Optional[str]

# AI Suggestion Schema
class AISuggestionResponse(BaseModel):
    home_pred: int
    away_pred: int
    confidence: float = Field(..., ge=0, le=1)
    reasoning: str
    warning: str = "Use this as reference only, not as guaranteed prediction"
    alternatives: Optional[List[dict]] = None

# Standings Schema
class StandingsUserRow(BaseModel):
    user_id: int
    name: str
    avatar_url: Optional[str]
    exact_matches: int
    correct_results: int
    total_points: int
    points_from_group: Optional[int] = None
    rank: int

class StandingsResponse(BaseModel):
    scope: str  # GLOBAL or GROUP:123
    standings: List[StandingsUserRow]
    computed_at: datetime
    match_count: int

# Admin Schemas
class MatchUpdateAdmin(BaseModel):
    home_score: int = Field(..., ge=0)
    away_score: int = Field(..., ge=0)
    status: str = "FT"
    home_score_et: Optional[int] = None
    away_score_et: Optional[int] = None
    home_score_pen: Optional[int] = None
    away_score_pen: Optional[int] = None

class FixtureImportRequest(BaseModel):
    matches: List[dict]

# Health/Status Schemas
class HealthCheckResponse(BaseModel):
    status: str  # ok, degraded, error
    database: str
    redis: Optional[str] = None
    groq: Optional[str] = None
    timestamp: datetime

class ServiceStatusResponse(BaseModel):
    service_name: str
    status: str  # ok, error, unknown
    last_check: Optional[datetime]
    details: Optional[str]
