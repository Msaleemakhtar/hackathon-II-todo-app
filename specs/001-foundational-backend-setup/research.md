# Research: Foundational Backend Setup

**Date**: 2025-12-09
**Feature**: 001-foundational-backend-setup
**Phase**: 0 (Technical Discovery)

This document consolidates research findings for all technical unknowns identified in the planning phase.

---

## 1. FastAPI + SQLModel + asyncpg Integration Pattern

**Decision**: Use async context manager pattern with dependency injection for database sessions

**Rationale**:
- FastAPI's dependency injection system works perfectly with async context managers
- Per-request sessions ensure transaction isolation and prevent connection leaks
- SQLModel's async support (via SQLAlchemy 2.0) integrates cleanly with asyncpg
- Connection pooling at the engine level (not per-request) optimizes resource usage

**Alternatives Considered**:
- **Global session**: Rejected - breaks transaction isolation, not thread-safe
- **Middleware-based sessions**: Rejected - less explicit, harder to test, doesn't integrate with FastAPI's DI
- **Manual session management**: Rejected - error-prone, no automatic cleanup

**Implementation Pattern**:

```python
# core/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from core.config import settings

# Create async engine with connection pool
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_MIN,
    max_overflow=settings.DB_POOL_MAX - settings.DB_POOL_MIN,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=settings.DB_POOL_RECYCLE,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncSession:
    """FastAPI dependency that provides database session"""
    async with AsyncSessionLocal() as session:
        yield session

# Initialize database (create tables)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

```python
# routers/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db

router = APIRouter()

@router.post("/register")
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    # db is automatically managed, committed on success, rolled back on error
    ...
```

**References**:
- https://fastapi.tiangolo.com/tutorial/sql-databases/
- https://sqlmodel.tiangolo.com/tutorial/fastapi/
- https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

---

## 2. JWT Implementation with python-jose

**Decision**: Use `python-jose[cryptography]` with HS256 algorithm for Phase II

**Rationale**:
- `python-jose` is the recommended JWT library for FastAPI (used in official docs)
- HS256 (symmetric) is simpler for Phase II; secret key can be shared between instances
- Cryptography backend provides better performance than pure-Python implementation
- Well-maintained library with good FastAPI integration examples

**Alternatives Considered**:
- **PyJWT**: Viable alternative, but python-jose has better FastAPI documentation
- **authlib**: More comprehensive but heavier; overkill for our needs
- **RS256 algorithm**: Better for multi-service architecture, but Phase II is single backend

**Implementation Pattern**:

```python
# core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from core.config import settings

def create_access_token(user_id: str, email: str) -> str:
    """Create JWT access token (15 min expiry)"""
    expire = datetime.utcnow() + timedelta(minutes=15)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: str, email: str) -> str:
    """Create JWT refresh token (7 day expiry)"""
    expire = datetime.utcnow() + timedelta(days=7)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def verify_token(token: str, expected_type: str = "access") -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type}")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("TOKEN_EXPIRED")
    except JWTError:
        raise ValueError("INVALID_TOKEN")
```

**References**:
- https://github.com/mpdavis/python-jose
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

---

## 3. Password Hashing with passlib[bcrypt]

**Decision**: Use passlib CryptContext with bcrypt, 12 rounds, with async wrapper for I/O-bound operations

**Rationale**:
- Bcrypt is industry-standard for password hashing (resistant to brute-force attacks)
- 12 rounds provides good security/performance balance (~300ms on modern hardware)
- Passlib provides a clean API and supports bcrypt scheme migration if needed
- Bcrypt is CPU-intensive but not I/O-bound, so we'll use asyncio.to_thread for async compatibility

**Alternatives Considered**:
- **Argon2**: Newer, slightly better security, but bcrypt is more widely supported and battle-tested
- **PBKDF2**: Weaker than bcrypt against GPU attacks
- **Scrypt**: Good security but higher memory requirements
- **Async bcrypt libraries**: Not necessary; asyncio.to_thread is sufficient

**Implementation Pattern**:

```python
# core/security.py
import asyncio
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Balance of security and performance
)

async def hash_password(password: str) -> str:
    """Hash password asynchronously (bcrypt is CPU-intensive)"""
    return await asyncio.to_thread(pwd_context.hash, password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password asynchronously"""
    return await asyncio.to_thread(pwd_context.verify, plain_password, hashed_password)
```

**Performance Note**: Bcrypt with 12 rounds takes ~250-350ms per hash. This is intentionally slow to prevent brute-force attacks. Using asyncio.to_thread prevents blocking the event loop during hashing operations.

**References**:
- https://passlib.readthedocs.io/en/stable/
- https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

---

## 4. Alembic Async Configuration

**Decision**: Configure Alembic with async engine support and SQLModel metadata auto-generation

**Rationale**:
- Alembic 1.7+ supports async migrations natively
- SQLModel's metadata can be imported directly for auto-generation
- Async migrations are required when using async database drivers
- Alembic's revision history provides clear audit trail of schema changes

**Alternatives Considered**:
- **Sync Alembic with sync engine**: Would require maintaining two database connection configurations
- **Manual SQL migrations**: Error-prone, no automatic model synchronization
- **SQLModel auto-create**: Not suitable for production (no migration history, no rollback)

**Implementation Pattern**:

```python
# alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from core.config import settings
from models import *  # Import all models to register with SQLModel metadata
from sqlmodel import SQLModel

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode"""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Migration Commands**:
```bash
# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# Rollback one revision
alembic downgrade -1
```

**References**:
- https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic
- https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships/

---

## 5. FastAPI Rate Limiting

**Decision**: Use `slowapi` library with in-memory storage for Phase II

**Rationale**:
- slowapi is a Flask-Limiter port for FastAPI, well-maintained and actively used
- In-memory storage is sufficient for Phase II (single-instance deployment)
- Simple decorator-based API integrates cleanly with FastAPI routes
- Can be easily upgraded to Redis storage for distributed deployments in Phase III

**Alternatives Considered**:
- **fastapi-limiter**: Requires Redis; overkill for Phase II
- **Custom middleware**: Reinventing the wheel; slowapi is battle-tested
- **No rate limiting**: Violates security requirements

**Implementation Pattern**:

```python
# main.py
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# routers/auth.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

@router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, data: RegisterRequest):
    ...

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    ...
```

**Error Response Customization**:
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many authentication attempts. Please try again later",
            "code": "RATE_LIMIT_EXCEEDED"
        }
    )
```

**References**:
- https://github.com/laurentS/slowapi
- https://flask-limiter.readthedocs.io/ (original Flask-Limiter docs)

---

## 6. pytest + FastAPI + Async Database Testing

**Decision**: Use pytest-asyncio with httpx AsyncClient and pytest fixtures for database setup/teardown

**Rationale**:
- pytest-asyncio enables async test functions with proper event loop management
- httpx.AsyncClient is the recommended async client for testing FastAPI (works with async endpoints)
- pytest fixtures provide clean setup/teardown for test database
- Transactional tests with rollback ensure test isolation without slow database resets

**Alternatives Considered**:
- **FastAPI TestClient**: Synchronous only; doesn't work with async database operations
- **Database recreation per test**: Too slow; transactional rollback is faster
- **Shared test database**: Risk of test pollution; fixtures with cleanup are cleaner

**Implementation Pattern**:

```python
# conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from main import app
from core.database import get_db
from core.config import settings

# Test database URL (separate from dev database)
TEST_DATABASE_URL = settings.TEST_DATABASE_URL or settings.DATABASE_URL.replace("_dev", "_test")

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Create test database schema once per test session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    """Provide clean database session per test with automatic rollback"""
    async with TestSessionLocal() as session:
        async with session.begin():
            yield session
            await session.rollback()  # Rollback after each test

@pytest_asyncio.fixture
async def client(db_session):
    """Provide test client with overridden database dependency"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

# Test example
@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data
```

**pytest.ini Configuration**:
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**References**:
- https://pytest-asyncio.readthedocs.io/
- https://www.encode.io/httpx/async/
- https://fastapi.tiangolo.com/advanced/testing-database/

---

## 7. Environment Configuration with pydantic-settings

**Decision**: Use pydantic-settings v2 with Settings class and .env file loading

**Rationale**:
- pydantic-settings provides type-safe configuration with validation
- Automatic .env file loading for local development
- Settings class can validate constraints (e.g., JWT key length) at startup
- Easy to override with environment variables in production
- Integrates seamlessly with FastAPI

**Alternatives Considered**:
- **python-dotenv + manual parsing**: No validation, error-prone
- **dynaconf**: More features but heavier dependency
- **Environment variables only**: Harder to manage locally

**Implementation Pattern**:

```python
# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    """Application settings with validation"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "Todo App API"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    TEST_DATABASE_URL: str | None = None
    DB_POOL_MIN: int = 2
    DB_POOL_MAX: int = 5
    DB_POOL_RECYCLE: int = 3600
    DB_CONNECTION_TIMEOUT: int = 30

    # JWT
    JWT_SECRET_KEY: str = Field(..., min_length=64, description="JWT secret (64+ hex chars)")

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 64:
            raise ValueError("JWT_SECRET_KEY must be at least 64 characters (256 bits)")
        return v

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://localhost:8000"
        ],
        description="Allowed CORS origins"
    )

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

settings = Settings()

# Startup validation
def validate_settings():
    """Validate settings on application startup"""
    assert len(settings.JWT_SECRET_KEY) >= 64, "JWT secret too short"
    print(f"✅ Settings validated: {settings.APP_NAME}")
```

**.env.example**:
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/todo_dev
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost/todo_test

# JWT (Generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your-256-bit-secret-here-minimum-64-hex-characters-required

# CORS (comma-separated for production)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Server
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

**References**:
- https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- https://fastapi.tiangolo.com/advanced/settings/

---

## 8. CORS Configuration in FastAPI

**Decision**: Use FastAPI's built-in CORSMiddleware with environment-based origin configuration

**Rationale**:
- FastAPI's CORSMiddleware is production-ready and well-tested
- Supports credentials (required for HttpOnly cookies)
- Easy to configure with environment variables
- Allows different origins for dev vs production

**Alternatives Considered**:
- **Custom CORS middleware**: Reinventing the wheel
- **starlette-cors**: Same as FastAPI's (FastAPI uses Starlette)
- **Wildcard (*) origins**: Security risk; not acceptable

**Implementation Pattern**:

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Todo App Phase II API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Environment-configurable
    allow_credentials=True,  # Required for HttpOnly cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600,  # Cache preflight requests for 10 minutes
)
```

**Development .env**:
```env
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8080","http://localhost:8000"]
```

**Production .env**:
```env
CORS_ORIGINS=["https://todoapp.example.com"]
```

**References**:
- https://fastapi.tiangolo.com/tutorial/cors/
- https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

---

## 9. Structured Logging in FastAPI

**Decision**: Use Python's standard logging with JSON formatter for production

**Rationale**:
- stdlib logging is sufficient for Phase II (no need for heavy dependencies)
- python-json-logger provides JSON formatting without additional complexity
- FastAPI request ID middleware can be added for request tracking
- Can be easily upgraded to structlog in Phase III if needed

**Alternatives Considered**:
- **structlog**: More powerful but heavier; overkill for Phase II
- **loguru**: Good alternative but different API; stdlib is more familiar
- **Plain text logs**: Not machine-parseable in production

**Implementation Pattern**:

```python
# core/logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger
from core.config import settings

def setup_logging():
    """Configure logging for the application"""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Create handler
    handler = logging.StreamHandler(sys.stdout)

    # JSON formatter for production, simple formatter for development
    if settings.DEBUG:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )

    handler.setFormatter(formatter)

    # Configure root logger
    logging.root.handlers = [handler]
    logging.root.setLevel(log_level)

    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# main.py
from core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting", extra={"version": "1.0.0"})
```

**Request ID Middleware** (optional for Phase II, recommended for Phase III):
```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

app.add_middleware(RequestIDMiddleware)
```

**References**:
- https://docs.python.org/3/library/logging.html
- https://github.com/madzak/python-json-logger

---

## 10. Docker Container Best Practices for FastAPI

**Decision**: Multi-stage Dockerfile with uv, non-root user, and health checks

**Rationale**:
- Multi-stage build reduces final image size (build dependencies not included)
- uv provides faster dependency installation than pip
- Non-root user improves security
- Health check enables container orchestration (Docker Compose, Kubernetes)

**Alternatives Considered**:
- **Single-stage build**: Larger image size
- **pip instead of uv**: Slower, against constitution requirements
- **Root user**: Security risk
- **No health check**: Harder to detect container failures

**Implementation Pattern**:

```dockerfile
# Dockerfile
# Stage 1: Build stage
FROM python:3.11-slim as builder

# Install uv
RUN pip install uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies with uv
RUN uv pip install --system -r pyproject.toml

# Stage 2: Runtime stage
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser ./src ./src
COPY --chown=appuser:appuser ./alembic ./alembic
COPY --chown=appuser:appuser alembic.ini ./

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Health Check Endpoint**:
```python
# main.py
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy"}
```

**.dockerignore**:
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.env
.venv
venv/
*.log
.git
.pytest_cache
.coverage
htmlcov/
```

**docker-compose.yml** (for local development):
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: todouser
      POSTGRES_PASSWORD: todopass
      POSTGRES_DB: todo_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://todouser:todopass@db/todo_dev
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    depends_on:
      - db
    volumes:
      - ./backend/src:/app/src  # Hot reload for development

volumes:
  postgres_data:
```

**References**:
- https://docs.docker.com/develop/dev-best-practices/
- https://fastapi.tiangolo.com/deployment/docker/
- https://github.com/astral-sh/uv#docker

---

## Research Summary

All 10 research tasks completed. Key decisions:

1. **Database**: Async SQLModel with asyncpg, dependency injection for sessions
2. **JWT**: python-jose with HS256, custom claims for token type
3. **Passwords**: passlib bcrypt with 12 rounds, async wrapper for event loop compatibility
4. **Migrations**: Alembic with async support and SQLModel metadata auto-generation
5. **Rate Limiting**: slowapi with in-memory storage (Redis upgrade path for Phase III)
6. **Testing**: pytest-asyncio with httpx AsyncClient and transactional test fixtures
7. **Configuration**: pydantic-settings with .env loading and startup validation
8. **CORS**: FastAPI CORSMiddleware with environment-based origins
9. **Logging**: stdlib logging with JSON formatter (python-json-logger)
10. **Docker**: Multi-stage build with uv, non-root user, health checks

**Ready to proceed to Phase 1: Design & Contracts**
