import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.db import Base, get_db
from app.models import User, Match, Prediction, MatchStage, MatchStatus
from app.services.business import ScoringService
from app.security.crypto import hash_password, create_access_token
from datetime import datetime, timezone, timedelta

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture
def test_user(db: Session = next(override_get_db())):
    """Create a test user"""
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash=hash_password("password123"),
        provider="email",
        email_verified=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_match(db: Session = next(override_get_db())):
    """Create a test match"""
    match = Match(
        fifa_match_code="TEST001",
        stage=MatchStage.GROUP,
        group_name="A",
        match_order=1,
        home_team="Team A",
        away_team="Team B",
        kickoff_at_utc=datetime.now(timezone.utc) + timedelta(hours=2),
        status=MatchStatus.SCHEDULED
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match

@pytest.fixture
def auth_headers(test_user):
    """Get auth headers with token"""
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}

# Tests

def test_scoring_exact_match():
    """Test scoring - exact match"""
    prediction = Prediction(
        user_id=1,
        match_id=1,
        home_pred=2,
        away_pred=1
    )
    
    match = Match(
        id=1,
        home_team="Team A",
        away_team="Team B",
        home_score=2,
        away_score=1,
        status=MatchStatus.FINISHED
    )
    
    points, details = ScoringService.calculate_points(prediction, match)
    
    assert points == ScoringService.POINTS_EXACT
    assert details["exact"] == True

def test_scoring_result_and_balance():
    """Test scoring - correct result and balance"""
    prediction = Prediction(
        user_id=1,
        match_id=1,
        home_pred=3,
        away_pred=1
    )
    
    match = Match(
        id=1,
        home_team="Team A",
        away_team="Team B",
        home_score=2,
        away_score=0,
        status=MatchStatus.FINISHED
    )
    
    points, details = ScoringService.calculate_points(prediction, match)
    
    assert points == ScoringService.POINTS_RESULT_BALANCE
    assert details["result"] == True
    assert details["balance"] == True

def test_scoring_result_only():
    """Test scoring - correct result only"""
    prediction = Prediction(
        user_id=1,
        match_id=1,
        home_pred=3,
        away_pred=1
    )
    
    match = Match(
        id=1,
        home_team="Team A",
        away_team="Team B",
        home_score=2,
        away_score=1,
        status=MatchStatus.FINISHED
    )
    
    points, details = ScoringService.calculate_points(prediction, match)
    
    assert points == ScoringService.POINTS_RESULT_ONLY
    assert details["result"] == True
    assert details["balance"] == False

def test_scoring_no_points():
    """Test scoring - no points"""
    prediction = Prediction(
        user_id=1,
        match_id=1,
        home_pred=2,
        away_pred=1
    )
    
    match = Match(
        id=1,
        home_team="Team A",
        away_team="Team B",
        home_score=1,
        away_score=2,
        status=MatchStatus.FINISHED
    )
    
    points, details = ScoringService.calculate_points(prediction, match)
    
    assert points == 0

def test_register_user():
    """Test user registration"""
    response = client.post(
        "/api/auth/register",
        json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "securepass123"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"

def test_login_user():
    """Test user login"""
    # First create user
    client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "login@example.com",
            "password": "password123"
        }
    )
    
    # Then login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_password():
    """Test login with wrong password"""
    # Create user
    client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "wrong@example.com",
            "password": "password123"
        }
    )
    
    # Try wrong password
    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401

def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert "status" in response.json()

def test_status_check():
    """Test status endpoint"""
    response = client.get("/status")
    
    assert response.status_code == 200
    assert response.json()["service"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
