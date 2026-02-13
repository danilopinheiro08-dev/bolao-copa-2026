from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Float, ForeignKey, 
    Text, Enum as SQLEnum, JSON, UniqueConstraint, Index, DECIMAL
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid

from app.db import Base

class MatchStage(str, enum.Enum):
    GROUP = "GROUP"
    ROUND_32 = "R32"
    ROUND_16 = "R16"
    QUARTER_FINAL = "QF"
    SEMI_FINAL = "SF"
    THIRD_PLACE = "THIRD"
    FINAL = "FINAL"

class MatchStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    FINISHED = "FT"
    CANCELLED = "CANCELLED"
    POSTPONED = "POSTPONED"

class GroupMemberRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # null if OAuth
    email_verified = Column(Boolean, default=False)
    avatar_url = Column(String(500), nullable=True)
    
    # OAuth
    provider = Column(String(50), nullable=True)  # google, facebook, email
    provider_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Timezone preference
    timezone = Column(String(50), default="UTC")
    
    # Relations
    groups = relationship("Group", back_populates="owner", foreign_keys="Group.owner_id")
    group_memberships = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    ai_usage = relationship("AIUsageLog", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_provider", "provider", "provider_id"),
    )

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="groups", foreign_keys=[owner_id])
    
    # Privacy & Access
    is_public = Column(Boolean, default=False)
    join_code = Column(String(20), unique=True, nullable=True, index=True)
    requires_approval = Column(Boolean, default=False)
    
    # Settings
    max_members = Column(Integer, nullable=True)  # null = unlimited
    scoring_system = Column(String(50), default="standard")  # standard, custom
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relations
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="group", cascade="all, delete-orphan")
    standings_cache = relationship("StandingsCache", back_populates="group", uselist=False, cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("owner_id", "slug", name="uq_group_owner_slug"),
        Index("idx_groups_slug", "slug"),
        Index("idx_groups_join_code", "join_code"),
    )

class GroupMember(Base):
    __tablename__ = "group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(GroupMemberRole), default=GroupMemberRole.MEMBER)
    
    # Status
    is_active = Column(Boolean, default=True)
    pending_approval = Column(Boolean, default=False)
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relations
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships")
    
    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_member"),
        Index("idx_group_members_user", "user_id"),
    )

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Match identification
    fifa_match_code = Column(String(50), unique=True, nullable=True, index=True)
    
    # Tournament structure
    stage = Column(SQLEnum(MatchStage), nullable=False)
    group_name = Column(String(2), nullable=True)  # A-L for group stage, null for knockout
    match_order = Column(Integer, nullable=False)  # order in tournament
    
    # Teams
    home_team = Column(String(100), nullable=False)
    away_team = Column(String(100), nullable=False)
    home_team_code = Column(String(3), nullable=True)  # ISO code
    away_team_code = Column(String(3), nullable=True)
    
    # Match timing
    kickoff_at_utc = Column(DateTime(timezone=True), nullable=False, index=True)
    venue = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Status & Score
    status = Column(SQLEnum(MatchStatus), default=MatchStatus.SCHEDULED, index=True)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    home_score_et = Column(Integer, nullable=True)  # Extra time (if applicable)
    away_score_et = Column(Integer, nullable=True)
    
    # Penalty shootout (for knockout)
    home_score_pen = Column(Integer, nullable=True)
    away_score_pen = Column(Integer, nullable=True)
    
    # Metadata
    attendance = Column(Integer, nullable=True)
    referee = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    predictions = relationship("Prediction", back_populates="match", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_matches_kickoff", "kickoff_at_utc"),
        Index("idx_matches_stage", "stage"),
        Index("idx_matches_group_name", "group_name"),
        Index("idx_matches_status", "status"),
    )

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)  # null = global prediction
    
    # Prediction
    home_pred = Column(Integer, nullable=False)
    away_pred = Column(Integer, nullable=False)
    advance_team = Column(String(100), nullable=True)  # for knockout: who advances
    
    # Scoring
    points_awarded = Column(Integer, default=0)
    score_details = Column(JSON, nullable=True)  # {"exact": false, "result": true, "balance": true}
    
    # Status
    is_locked = Column(Boolean, default=False)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="predictions")
    match = relationship("Match", back_populates="predictions")
    group = relationship("Group", back_populates="predictions")
    
    __table_args__ = (
        UniqueConstraint("user_id", "match_id", "group_id", name="uq_user_match_group_pred"),
        Index("idx_predictions_user", "user_id"),
        Index("idx_predictions_match", "match_id"),
        Index("idx_predictions_group", "group_id"),
    )

class StandingsCache(Base):
    __tablename__ = "standings_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Scope: GLOBAL or GROUP:123
    scope = Column(String(50), unique=True, nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    
    # Cache data
    standings_data = Column(JSON, nullable=False)  # [{"user_id": 1, "name": "", "points": 100, ...}]
    
    # Timestamps
    computed_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    group = relationship("Group", back_populates="standings_cache")
    
    __table_args__ = (
        Index("idx_standings_scope", "scope"),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User & action
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)  # login, prediction_created, etc.
    resource_type = Column(String(50), nullable=True)  # user, group, match, etc.
    resource_id = Column(Integer, nullable=True)
    
    # Request info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Details
    details = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relations
    user = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        Index("idx_audit_logs_user", "user_id"),
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_created", "created_at"),
    )

class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User & usage
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    
    # AI response
    prompt = Column(Text, nullable=True)
    suggestion = Column(JSON, nullable=False)  # {home_pred, away_pred, reasoning, confidence}
    
    # Request info
    ip_address = Column(String(45), nullable=True)
    latency_ms = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relations
    user = relationship("User", back_populates="ai_usage")
    
    __table_args__ = (
        Index("idx_ai_usage_user_date", "user_id", "created_at"),
    )

class RateLimitLog(Base):
    __tablename__ = "rate_limit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifier
    identifier = Column(String(255), nullable=False)  # IP or user_id
    identifier_type = Column(String(20), nullable=False)  # ip, user
    endpoint = Column(String(255), nullable=False)
    
    # Rate limit
    request_count = Column(Integer, default=1)
    limit = Column(Integer, nullable=False)
    
    # Status
    is_limited = Column(Boolean, default=False)
    
    # Timestamps
    reset_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class BruteForceLockout(Base):
    __tablename__ = "brute_force_lockouts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Target
    target = Column(String(255), nullable=False)  # email or IP
    target_type = Column(String(20), nullable=False)  # email, ip
    
    # Lockout
    failed_attempts = Column(Integer, default=1)
    is_locked = Column(Boolean, default=False)
    
    # Timestamps
    locked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint("target", "target_type", name="uq_brute_force_target"),
    )
