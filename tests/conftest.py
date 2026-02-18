"""
Shared test fixtures for Bolão Copa 2026.
Uses SQLite in-memory via StaticPool for full test isolation.

IMPORTANT: The DATABASE_URL env var must be set BEFORE app.db is imported,
because SQLAlchemy creates the engine at module load time.
"""
import os

# Override before any app imports so app.db uses SQLite instead of PostgreSQL
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["ENABLE_JOBS"] = "False"  # Disable background scheduler during tests

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone, timedelta

from app.main import app
from app.db import Base, get_db
from app.models import User, Match, Group, GroupMember, GroupMemberRole, MatchStage, MatchStatus
from app.security.crypto import hash_password, create_access_token

# ---------------------------------------------------------------------------
# Test database engine — SQLite pure in-memory with StaticPool so the same
# connection is shared across the session (required for SQLite in-memory).
# ---------------------------------------------------------------------------
TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create all tables before each test and drop after."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture(scope="function")
def db(setup_db):
    """Provide a clean database session per test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db):
    """
    FastAPI TestClient with the test DB injected via dependency override.
    Each test gets its own isolated client + DB.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass  # session lifecycle managed by `db` fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create and return a regular test user."""
    user = User(
        name="Test User",
        email="testuser@example.com",
        password_hash=hash_password("Password123!"),
        provider="email",
        email_verified=True,
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db):
    """Create and return an admin test user."""
    user = User(
        name="Admin User",
        email="admin@example.com",
        password_hash=hash_password("AdminPass123!"),
        provider="email",
        email_verified=True,
        is_active=True,
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_match(db):
    """Create and return a scheduled match 2 hours in the future."""
    match = Match(
        fifa_match_code="TEST001",
        stage=MatchStage.GROUP,
        group_name="A",
        match_order=1,
        home_team="Brasil",
        away_team="Argentina",
        home_team_code="BRA",
        away_team_code="ARG",
        kickoff_at_utc=datetime.now(timezone.utc) + timedelta(hours=2),
        venue="Estadio X",
        city="São Paulo",
        status=MatchStatus.SCHEDULED,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@pytest.fixture
def finished_match(db):
    """Create and return a finished match with score 2-1 (home win)."""
    match = Match(
        fifa_match_code="FIN001",
        stage=MatchStage.GROUP,
        group_name="A",
        match_order=2,
        home_team="França",
        away_team="Alemanha",
        home_team_code="FRA",
        away_team_code="GER",
        kickoff_at_utc=datetime.now(timezone.utc) - timedelta(hours=3),
        status=MatchStatus.FINISHED,
        home_score=2,
        away_score=1,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@pytest.fixture
def test_group(db, test_user):
    """Create and return a private group owned by test_user."""
    from app.security.crypto import generate_join_code
    group = Group(
        name="Grupo Teste",
        slug="grupo-teste",
        description="Grupo para testes",
        owner_id=test_user.id,
        is_public=False,
        join_code=generate_join_code(),
        requires_approval=False,
        is_active=True,
    )
    db.add(group)
    db.flush()

    # Add owner as OWNER member
    member = GroupMember(
        group_id=group.id,
        user_id=test_user.id,
        role=GroupMemberRole.OWNER,
    )
    db.add(member)
    db.commit()
    db.refresh(group)
    return group


@pytest.fixture
def auth_headers(test_user):
    """Return Authorization headers for test_user."""
    token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(test_admin_user):
    """Return Authorization headers for admin user."""
    token = create_access_token(
        data={"sub": str(test_admin_user.id), "email": test_admin_user.email},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}
