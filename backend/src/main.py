import logging
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .core.config import settings, validate_settings
from .core.exceptions import AppException
from .core.logging_config import setup_logging
from .routers import analytics, categories, reminders, subscriptions, tags, tasks, users
from .workers.scheduler import start_scheduler, stop_scheduler

setup_logging()
logger = logging.getLogger(__name__)

# Initialize Sentry for error tracking (T067, FR-034)
if settings.SENTRY_DSN and settings.ENVIRONMENT != "development":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,  # Sample 10% of transactions for performance monitoring
        profiles_sample_rate=0.1,  # Sample 10% for profiling
        send_default_pii=False,  # Don't send personally identifiable information
        attach_stacktrace=True,
        before_send=lambda event, hint: None if settings.ENVIRONMENT == "development" else event,
    )
    logger.info("Sentry error tracking initialized", extra={"environment": settings.ENVIRONMENT})

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    validate_settings()
    logger.info("Application starting", extra={"version": "1.0.0"})

    # Start reminder scheduler
    try:
        start_scheduler()
        logger.info("Reminder scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

    yield

    # Shutdown
    try:
        stop_scheduler()
        logger.info("Reminder scheduler stopped")
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {e}")


app = FastAPI(
    title=settings.APP_NAME,
    description="Todo App Phase II API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions with error codes."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Environment-configurable
    allow_credentials=True,  # Required for HttpOnly cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# GZip compression middleware for performance optimization (FR-015)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Only compress responses larger than 1KB
    compresslevel=5,  # Balance between speed and compression ratio
)


@app.get("/health")
async def health_check():
    """Provide a health check endpoint for container orchestration."""
    return {"status": "healthy"}

app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])
app.include_router(tags.router, prefix="/api/v1", tags=["Tags"])
app.include_router(categories.router, prefix="/api/v1", tags=["Categories"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(reminders.router, prefix="/api/v1/users", tags=["Reminders"])
app.include_router(subscriptions.router, prefix="/api/v1", tags=["Subscriptions"])
app.include_router(analytics.router, tags=["Analytics"])
