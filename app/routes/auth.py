from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User, MatchStatus, Match
from app.schemas import UserResponse, UserCreate, UserLogin, UserPasswordReset, UserPasswordResetConfirm
from app.security.crypto import hash_password, verify_password, generate_session_token, create_access_token
from app.security.middleware import log_action, get_client_ip, BruteForceProtection
from app.services.business import UserService
from datetime import timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register new user with email and password"""
    
    # Check for brute force
    bf = BruteForceProtection(db)
    if bf.check_lockout(user_data.email, "email"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Try again later."
        )
    
    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        bf.record_failed_attempt(user_data.email, "email")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = UserService.create_user(
        db=db,
        email=user_data.email,
        name=user_data.name,
        password=user_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user"
        )
    
    # Log action
    log_action(
        db=db,
        user_id=user.id,
        action="user_registered",
        request=request
    )
    
    return user

@router.post("/login")
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    
    # Check brute force
    bf = BruteForceProtection(db)
    if bf.check_lockout(credentials.email, "email"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later."
        )
    
    # Authenticate
    user = UserService.authenticate_user(
        db=db,
        email=credentials.email,
        password=credentials.password
    )
    
    if not user:
        bf.record_failed_attempt(credentials.email, "email")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Reset brute force on success
    bf.reset_failed_attempts(credentials.email, "email")
    
    # Update last login
    from datetime import datetime, timezone
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    
    # Create token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(days=7)
    )
    
    # Log action
    log_action(
        db=db,
        user_id=user.id,
        action="user_login",
        request=request
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user).model_dump(mode="json"),
    }

@router.post("/password-reset")
async def request_password_reset(
    reset_data: UserPasswordReset,
    request: Request,
    db: Session = Depends(get_db)
):
    """Request password reset email"""
    
    user = UserService.get_user_by_email(db, reset_data.email)
    if not user:
        # Don't reveal if email exists
        return {"message": "If email exists, password reset link sent"}
    
    # Generate token
    from app.security.crypto import generate_password_reset_token
    token = generate_password_reset_token(user.id)
    
    # TODO: Send email with token
    # For now, just log
    log_action(
        db=db,
        user_id=user.id,
        action="password_reset_requested",
        request=request
    )
    
    return {"message": "If email exists, password reset link sent"}

@router.post("/password-reset-confirm")
async def confirm_password_reset(
    reset_data: UserPasswordResetConfirm,
    request: Request,
    db: Session = Depends(get_db)
):
    """Confirm password reset with token"""
    
    from app.security.crypto import verify_password_reset_token
    
    user_id = verify_password_reset_token(reset_data.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.password_hash = hash_password(reset_data.new_password)
    db.commit()
    
    log_action(
        db=db,
        user_id=user.id,
        action="password_reset_confirmed",
        request=request
    )
    
    return {"message": "Password updated successfully"}

# OAuth routes (Google, Facebook) - simplified placeholders
@router.get("/callback/google")
async def google_callback(code: str, request: Request, db: Session = Depends(get_db)):
    """Google OAuth callback"""
    # TODO: Implement OAuth flow
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.get("/callback/facebook")
async def facebook_callback(code: str, request: Request, db: Session = Depends(get_db)):
    """Facebook OAuth callback"""
    # TODO: Implement OAuth flow
    raise HTTPException(status_code=501, detail="Not implemented yet")
