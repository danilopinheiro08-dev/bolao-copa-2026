from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import secrets
import string
from typing import Optional
import jwt
from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using Argon2"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

# JWT tokens
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# CSRF Protection
def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(32)

def verify_csrf_token(token: str, stored_token: str) -> bool:
    """Verify CSRF token"""
    if not token or not stored_token:
        return False
    return secrets.compare_digest(token, stored_token)

# Join codes for groups
def generate_join_code(length: int = 8) -> str:
    """Generate a short join code for groups"""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(secrets.choice(chars) for _ in range(length))
    return code

# Session tokens
def generate_session_token() -> str:
    """Generate secure session token"""
    return secrets.token_urlsafe(32)

# Email verification & password reset tokens
def generate_verification_token(email: str) -> str:
    """Generate email verification token"""
    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRE_MINUTES)
    data = {"email": email, "exp": expiry}
    return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")

def verify_verification_token(token: str) -> Optional[str]:
    """Verify email verification token and return email"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("email")
        if email:
            return email
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    return None

def generate_password_reset_token(user_id: int) -> str:
    """Generate password reset token"""
    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES)
    data = {"user_id": user_id, "exp": expiry, "type": "password_reset"}
    return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")

def verify_password_reset_token(token: str) -> Optional[int]:
    """Verify password reset token and return user_id"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") == "password_reset":
            user_id = payload.get("user_id")
            if user_id:
                return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    return None
