from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text
from app.config import settings
from app.db import init_db
from app.routes import auth, predictions, groups, users, admin, ai
from app.security.middleware import get_security_headers, RateLimitChecker
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime, timezone
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Application lifespan: startup and shutdown logic."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    if settings.ENABLE_JOBS:
        from app.jobs.scheduler import start_scheduler
        start_scheduler()
        logger.info("Background jobs started")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter

# Add exception handler for rate limit
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many requests. Please try again later."},
    )

# Middleware - Security Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    headers = get_security_headers()
    for key, value in headers.items():
        response.headers[key] = value
    
    # Add HSTS
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Middleware - Logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
    start = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start
    
    if settings.DEBUG:
        logger.info(f"{request.method} {request.url.path} - {response.status_code} ({duration:.2f}s)")
    
    return response

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host - Permitir Railway domains + testserver (pytest TestClient)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "testserver",   # FastAPI TestClient hostname
        "*.railway.app",
        "*.up.railway.app",
        "*.example.com",
    ]
)

# Routes
app.include_router(auth.router)
app.include_router(predictions.router)
app.include_router(groups.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(ai.router)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.db import engine
    
    try:
        # Test DB connection (SQLAlchemy 2.x requires text())
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.error(f"DB health check failed: {e}")
        db_status = "error"
    
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "version": settings.APP_VERSION,
    }

@app.get("/status")
async def status_check():
    """Status check endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

# 404
@app.get("/{path_name:path}", status_code=404)
async def not_found(path_name: str):
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
