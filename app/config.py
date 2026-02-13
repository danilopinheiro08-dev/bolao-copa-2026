from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App
    APP_NAME: str = "Bolão da Firma - Copa 2026"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    # Database - Railway injecta DATABASE_PUBLIC_URL como env var
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/bolao_copa_2026",
        alias="DATABASE_PUBLIC_URL"  # Railway usa este nome
    )
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # Auth
    SESSION_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    EMAIL_VERIFICATION_EXPIRE_MINUTES: int = 24 * 60  # 24 hours
    PASSWORD_RESET_EXPIRE_MINUTES: int = 2 * 60  # 2 hours
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback/google"
    
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_REDIRECT_URI: str = "http://localhost:8000/auth/callback/facebook"
    
    # Email (optional - for future)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@bolao.com"
    
    # Groq AI
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    GROQ_TIMEOUT: int = 30
    AI_SUGGESTION_QUOTA_PER_DAY: int = 10
    
    # Sports Data Provider
    SPORTS_API_PROVIDER: str = "manual"  # manual, api-football, sportradar
    SPORTS_API_KEY: Optional[str] = None
    SPORTS_API_URL: Optional[str] = None
    
    # Stripe (optional)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLIC_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Security
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    CSRF_PROTECTION_ENABLED: bool = True
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    BRUTE_FORCE_LOCKOUT_THRESHOLD: int = 5
    BRUTE_FORCE_LOCKOUT_MINUTES: int = 15
    
    # Jobs
    ENABLE_JOBS: bool = True
    UPDATE_MATCHES_INTERVAL_SECONDS: int = 300  # 5 minutes
    RECALC_RANKINGS_INTERVAL_SECONDS: int = 3600  # 1 hour
    
    # Timezone
    DEFAULT_TIMEZONE: str = "UTC"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"
        populate_by_name = True  # Permite usar alias (DATABASE_PUBLIC_URL)

settings = Settings()
