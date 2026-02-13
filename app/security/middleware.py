from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from app.models import AuditLog
from datetime import datetime, timezone
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies"""
    if x_forwarded_for := request.headers.get("X-Forwarded-For"):
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def get_user_agent(request: Request) -> str:
    """Get user agent from request"""
    return request.headers.get("User-Agent", "unknown")[:500]

def log_action(
    db: Session,
    user_id: Optional[int],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    request: Optional[Request] = None,
    details: Optional[dict] = None
):
    """Log an action to audit log"""
    try:
        ip = get_client_ip(request) if request else None
        user_agent = get_user_agent(request) if request else None
        
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip,
            user_agent=user_agent,
            details=details,
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"Error logging action: {e}")
        db.rollback()

# OWASP Security Headers
def get_security_headers() -> dict:
    """Return security headers for responses"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self';",
    }

# CSRF Protection
CSRF_TOKEN_LENGTH = 32

class CSRFProtection:
    """CSRF protection helper"""
    
    def __init__(self):
        self.token_key = "csrf_token"
    
    def generate_token(self) -> str:
        """Generate CSRF token"""
        import secrets
        return secrets.token_urlsafe(CSRF_TOKEN_LENGTH)
    
    def verify_token(self, request_token: str, session_token: str) -> bool:
        """Verify CSRF token"""
        if not request_token or not session_token:
            return False
        import secrets
        return secrets.compare_digest(request_token, session_token)

# Input Sanitization
def sanitize_input(value: str, max_length: int = 1000) -> str:
    """Sanitize user input"""
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Truncate
    value = value[:max_length]
    
    return value.strip()

# SQL Injection prevention - use ORM (SQLAlchemy)
# No raw queries; always use parameterized queries

# XSS Prevention
import html

def escape_html(value: str) -> str:
    """Escape HTML special characters"""
    if not isinstance(value, str):
        return ""
    return html.escape(value)

# Rate Limiting helpers
from typing import Tuple, Optional
from datetime import datetime, timedelta

class RateLimitChecker:
    """Simple rate limit checker (use Redis for production)"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.memory_store = {}  # fallback
    
    async def check_rate_limit(
        self,
        identifier: str,
        limit: int = 60,
        window_seconds: int = 60
    ) -> Tuple[bool, int, int]:
        """
        Check if request exceeds rate limit
        Returns: (is_allowed, current_count, remaining)
        """
        if self.redis:
            return await self._check_redis(identifier, limit, window_seconds)
        else:
            return self._check_memory(identifier, limit, window_seconds)
    
    async def _check_redis(self, identifier: str, limit: int, window_seconds: int):
        """Check rate limit using Redis"""
        key = f"ratelimit:{identifier}"
        current = await self.redis.incr(key)
        
        if current == 1:
            await self.redis.expire(key, window_seconds)
        
        ttl = await self.redis.ttl(key)
        
        is_allowed = current <= limit
        remaining = max(0, limit - current)
        
        return is_allowed, current, remaining
    
    def _check_memory(self, identifier: str, limit: int, window_seconds: int):
        """Check rate limit using in-memory store (development only)"""
        now = datetime.now(timezone.utc)
        
        if identifier not in self.memory_store:
            self.memory_store[identifier] = {"count": 0, "reset_at": now + timedelta(seconds=window_seconds)}
        
        entry = self.memory_store[identifier]
        
        if now >= entry["reset_at"]:
            entry["count"] = 0
            entry["reset_at"] = now + timedelta(seconds=window_seconds)
        
        entry["count"] += 1
        is_allowed = entry["count"] <= limit
        remaining = max(0, limit - entry["count"])
        
        return is_allowed, entry["count"], remaining

# Brute force protection
class BruteForceProtection:
    """Brute force protection helper"""
    
    def __init__(self, db: Session):
        self.db = db
        self.threshold = 5
        self.lockout_minutes = 15
    
    def check_lockout(self, target: str, target_type: str = "email") -> bool:
        """Check if target is locked out"""
        from app.models import BruteForceLockout
        from datetime import datetime, timezone
        
        lockout = self.db.query(BruteForceLockout).filter(
            BruteForceLockout.target == target,
            BruteForceLockout.target_type == target_type,
        ).first()
        
        if not lockout or not lockout.is_locked:
            return False
        
        if lockout.locked_until and lockout.locked_until < datetime.now(timezone.utc):
            lockout.is_locked = False
            self.db.commit()
            return False
        
        return True
    
    def record_failed_attempt(self, target: str, target_type: str = "email"):
        """Record failed login attempt"""
        from app.models import BruteForceLockout
        from datetime import datetime, timezone, timedelta
        
        lockout = self.db.query(BruteForceLockout).filter(
            BruteForceLockout.target == target,
            BruteForceLockout.target_type == target_type,
        ).first()
        
        if not lockout:
            lockout = BruteForceLockout(target=target, target_type=target_type, failed_attempts=1)
            self.db.add(lockout)
        else:
            lockout.failed_attempts += 1
        
        if lockout.failed_attempts >= self.threshold:
            lockout.is_locked = True
            lockout.locked_until = datetime.now(timezone.utc) + timedelta(minutes=self.lockout_minutes)
        
        self.db.commit()
    
    def reset_failed_attempts(self, target: str, target_type: str = "email"):
        """Reset failed attempts after successful login"""
        from app.models import BruteForceLockout
        
        lockout = self.db.query(BruteForceLockout).filter(
            BruteForceLockout.target == target,
            BruteForceLockout.target_type == target_type,
        ).first()
        
        if lockout:
            lockout.failed_attempts = 0
            lockout.is_locked = False
            self.db.commit()
