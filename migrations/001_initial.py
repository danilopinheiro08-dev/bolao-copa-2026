"""Create initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('provider', sa.String(50), nullable=True),
        sa.Column('provider_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='UTC'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('email'),
        sa.Index('idx_users_email', 'email'),
        sa.Index('idx_users_provider', 'provider', 'provider_id'),
    )
    
    # Create groups table
    op.create_table('groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('join_code', sa.String(20), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('max_members', sa.Integer(), nullable=True),
        sa.Column('scoring_system', sa.String(50), nullable=False, server_default='standard'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('owner_id', 'slug', name='uq_group_owner_slug'),
        sa.Index('idx_groups_slug', 'slug'),
        sa.Index('idx_groups_join_code', 'join_code'),
    )
    
    # Create group_members table
    op.create_table('group_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('owner', 'admin', 'member', name='groupmemberrole'), nullable=False, server_default='member'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('pending_approval', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('group_id', 'user_id', name='uq_group_member'),
        sa.Index('idx_group_members_user', 'user_id'),
    )
    
    # Create matches table
    op.create_table('matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('fifa_match_code', sa.String(50), nullable=True),
        sa.Column('stage', sa.Enum('GROUP', 'R32', 'R16', 'QF', 'SF', 'THIRD', 'FINAL', name='matchstage'), nullable=False),
        sa.Column('group_name', sa.String(2), nullable=True),
        sa.Column('match_order', sa.Integer(), nullable=False),
        sa.Column('home_team', sa.String(100), nullable=False),
        sa.Column('away_team', sa.String(100), nullable=False),
        sa.Column('home_team_code', sa.String(3), nullable=True),
        sa.Column('away_team_code', sa.String(3), nullable=True),
        sa.Column('kickoff_at_utc', sa.DateTime(timezone=True), nullable=False),
        sa.Column('venue', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('status', sa.Enum('SCHEDULED', 'LIVE', 'FT', 'CANCELLED', 'POSTPONED', name='matchstatus'), nullable=False, server_default='SCHEDULED'),
        sa.Column('home_score', sa.Integer(), nullable=True),
        sa.Column('away_score', sa.Integer(), nullable=True),
        sa.Column('home_score_et', sa.Integer(), nullable=True),
        sa.Column('away_score_et', sa.Integer(), nullable=True),
        sa.Column('home_score_pen', sa.Integer(), nullable=True),
        sa.Column('away_score_pen', sa.Integer(), nullable=True),
        sa.Column('attendance', sa.Integer(), nullable=True),
        sa.Column('referee', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('fifa_match_code'),
        sa.Index('idx_matches_kickoff', 'kickoff_at_utc'),
        sa.Index('idx_matches_stage', 'stage'),
        sa.Index('idx_matches_group_name', 'group_name'),
        sa.Index('idx_matches_status', 'status'),
    )
    
    # Create predictions table
    op.create_table('predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('home_pred', sa.Integer(), nullable=False),
        sa.Column('away_pred', sa.Integer(), nullable=False),
        sa.Column('advance_team', sa.String(100), nullable=True),
        sa.Column('points_awarded', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('score_details', postgresql.JSON(), nullable=True),
        sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('user_id', 'match_id', 'group_id', name='uq_user_match_group_pred'),
        sa.Index('idx_predictions_user', 'user_id'),
        sa.Index('idx_predictions_match', 'match_id'),
        sa.Index('idx_predictions_group', 'group_id'),
    )
    
    # Create standings_cache table
    op.create_table('standings_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scope', sa.String(50), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('standings_data', postgresql.JSON(), nullable=False),
        sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('scope'),
        sa.Index('idx_standings_scope', 'scope'),
    )
    
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(255), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('details', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_audit_logs_user', 'user_id'),
        sa.Index('idx_audit_logs_action', 'action'),
        sa.Index('idx_audit_logs_created', 'created_at'),
    )
    
    # Create ai_usage_logs table
    op.create_table('ai_usage_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=True),
        sa.Column('prompt', sa.Text(), nullable=True),
        sa.Column('suggestion', postgresql.JSON(), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_ai_usage_user_date', 'user_id', 'created_at'),
    )
    
    # Create rate_limit_logs table
    op.create_table('rate_limit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('identifier', sa.String(255), nullable=False),
        sa.Column('identifier_type', sa.String(20), nullable=False),
        sa.Column('endpoint', sa.String(255), nullable=False),
        sa.Column('request_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('limit', sa.Integer(), nullable=False),
        sa.Column('is_limited', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reset_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create brute_force_lockouts table
    op.create_table('brute_force_lockouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('target', sa.String(255), nullable=False),
        sa.Column('target_type', sa.String(20), nullable=False),
        sa.Column('failed_attempts', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('target', 'target_type', name='uq_brute_force_target'),
    )

def downgrade() -> None:
    op.drop_table('brute_force_lockouts')
    op.drop_table('rate_limit_logs')
    op.drop_table('ai_usage_logs')
    op.drop_table('audit_logs')
    op.drop_table('standings_cache')
    op.drop_table('predictions')
    op.drop_table('matches')
    op.drop_table('group_members')
    op.drop_table('groups')
    op.drop_table('users')
