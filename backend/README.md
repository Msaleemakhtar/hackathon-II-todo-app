# Todo App Backend

This is the backend service for the Todo App, built with FastAPI, SQLModel, and PostgreSQL. This project follows **Spec-Driven Development (SDD)** principles as defined in the [Phase II Constitution](../.specify/memory/constitution.md).

## Features

- User Registration & Authentication (JWT based)
- User Login & Token Refresh with secure token management
- Access Protected Resources with JWT validation
- Database with SQLModel entities (User, Task, Tag)
- Alembic for database migrations
- Rate limiting on authentication endpoints
- RESTful API with `/api/v1/` versioning
- Comprehensive async database operations

## Constitutional Reference

All backend development **MUST** adhere to the principles defined in:
- **Main Constitution**: `../.specify/memory/constitution.md`
- **Backend Guide**: `./CLAUDE.md`

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Python package manager - **required**)
- PostgreSQL 15+ (Neon Serverless recommended, or local/Docker)
- Docker (optional, for local PostgreSQL)

### Local Development Setup

1.  **Navigate to the backend directory:**

    ```bash
    cd backend
    ```

2.  **Install dependencies using uv:**

    ```bash
    uv sync
    ```

    This creates a virtual environment and installs all dependencies from `pyproject.toml`.

3.  **Environment Configuration:**

    Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```

    Edit `.env` and configure:
    - `JWT_SECRET_KEY`: Generate using `openssl rand -hex 32` (required, minimum 64 hex characters)
    - `DATABASE_URL`: Your PostgreSQL connection string (see Database Setup below)
    - `TEST_DATABASE_URL`: SQLite URL for testing (default: `sqlite+aiosqlite:///./test.db`)
    - `CORS_ORIGINS`: Allowed origins as JSON array (default includes localhost ports)
    - `ENVIRONMENT`: `development` or `production`
    - `DEBUG`: `true` for development, `false` for production

### Database Setup

#### Option 1: Neon Serverless PostgreSQL (Recommended)

1. Create a Neon account at [neon.tech](https://neon.tech)
2. Create a new project and database
3. Copy the connection string to your `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]/[database]
   ```

**Connection Pooling**: The application uses asyncpg with connection pooling configured for optimal performance:
- Minimum pool size: 2 connections
- Maximum pool size: 5 connections
- Suitable for serverless PostgreSQL (Neon)

#### Option 2: Local PostgreSQL (Docker)

From the project root:
```bash
docker compose up -d db
```

Update `DATABASE_URL` in `backend/.env`:
```
DATABASE_URL=postgresql+asyncpg://todouser:todopass@localhost:5432/todo_dev
```

### Run Database Migrations

```bash
uv run alembic upgrade head
```

To create new migrations after model changes:
```bash
uv run alembic revision --autogenerate -m "Description of changes"
uv run alembic upgrade head
```

### Run the Application

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint for monitoring and orchestration

### Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and receive JWT tokens
- `POST /api/v1/auth/refresh` - Refresh access token using refresh token
- `GET /api/v1/auth/me` - Get current authenticated user profile (protected)

**Rate Limiting**: Authentication endpoints are rate-limited to prevent abuse.

For detailed API documentation, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

The project uses `pytest` with `pytest-asyncio` for async tests. Tests use SQLite with transaction rollback for database isolation.

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_auth.py

# Run with verbose output
uv run pytest -v

# Run tests in parallel (faster)
uv run pytest -n auto
```

**Test Database**: Configured via `TEST_DATABASE_URL` in `.env` (defaults to SQLite for speed and isolation).

**Coverage Requirements** (enforced in nightly CI):
- Backend core logic: >= 80%

## Code Quality

### Pre-commit Hooks

The project enforces pre-commit hooks that **MUST** pass before committing:

- `ruff check` - Linting
- `ruff format` - Code formatting
- `pip-audit` - Security vulnerability scanning

Run manually:
```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Fix auto-fixable issues
uv run ruff check --fix .
```

### Development Best Practices

**Before Committing:**
1. Run tests: `uv run pytest`
2. Check linting: `uv run ruff check .`
3. Format code: `uv run ruff format .`
4. Review changes: `git diff`

**Code Style:**
- Line length: 88 characters (Black-compatible)
- Follow PEP 8 guidelines
- Use type hints for function signatures
- Write docstrings for public APIs

**Common Commands:**
```bash
# Add new dependency
uv add <package-name>

# Add dev dependency
uv add --dev <package-name>

# Update dependencies
uv sync

# Create database migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t todo-backend:latest .

# Run with docker-compose (from project root)
cd ..
docker compose up -d backend
```

## Architecture & Design Patterns

### Layered Architecture
The backend follows a clean layered architecture:

1. **Routers** (`/src/routers/`): Handle HTTP requests/responses, validation, and route definitions
2. **Services** (`/src/services/`): Contain business logic and orchestration
3. **Models** (`/src/models/`): SQLModel entities representing database tables
4. **Schemas** (`/src/schemas/`): Pydantic schemas for request/response validation
5. **Core** (`/src/core/`): Configuration, database, security, and shared utilities

### Key Design Principles
- **Async-First**: All database operations use `async`/`await` for non-blocking I/O
- **Dependency Injection**: FastAPI's dependency system for database sessions and authentication
- **Data Isolation**: All queries scoped to authenticated user's ID (enforced in constitution)
- **JWT Authentication**: Stateless authentication with access and refresh tokens
- **API Versioning**: All endpoints prefixed with `/api/v1/` for future compatibility

### Security Features
- Password hashing with bcrypt (via passlib)
- JWT tokens with expiration (access: 30 min, refresh: 7 days)
- Rate limiting on authentication endpoints
- CORS configuration for cross-origin requests
- Environment-based configuration (no hardcoded secrets)

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app entry point, CORS, rate limiting
│   ├── routers/
│   │   └── auth.py          # Authentication endpoints
│   ├── models/
│   │   ├── user.py          # User entity (SQLModel)
│   │   ├── task.py          # Task entity
│   │   ├── tag.py           # Tag entity
│   │   └── task_tag_link.py # Many-to-many relationship
│   ├── schemas/
│   │   ├── auth.py          # Authentication request/response schemas
│   │   ├── user.py          # User schemas
│   │   └── token.py         # JWT token schemas
│   ├── services/
│   │   └── auth_service.py  # Authentication business logic
│   └── core/
│       ├── config.py        # Pydantic settings from environment
│       ├── database.py      # Database engine and session management
│       ├── security.py      # JWT and password utilities
│       ├── dependencies.py  # FastAPI dependencies (auth, DB)
│       └── logging_config.py # Structured logging setup
├── tests/
│   ├── conftest.py          # Pytest fixtures (test DB setup)
│   ├── test_auth.py         # Authentication endpoint tests
│   └── test_models.py       # Database model tests
├── alembic/
│   ├── env.py               # Alembic configuration
│   ├── script.py.mako       # Migration template
│   └── versions/            # Migration files
├── pyproject.toml           # Project dependencies (uv)
├── pytest.ini               # Pytest configuration
├── .env.example             # Environment variable template
├── .env                     # Local environment (not committed)
├── Dockerfile               # Container image definition
└── README.md                # This file
```

## Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Verify DATABASE_URL is correct
echo $DATABASE_URL

# Test PostgreSQL connection (if using Neon)
psql $DATABASE_URL -c "SELECT version();"

# Check if migrations are applied
uv run alembic current
uv run alembic upgrade head
```

**2. JWT Token Errors**
```bash
# Ensure JWT_SECRET_KEY is properly set (64+ hex characters)
openssl rand -hex 32

# Verify .env file is loaded
python -c "from src.core.config import settings; print(settings.JWT_SECRET_KEY[:10])"
```

**3. Import Errors**
```bash
# Reinstall dependencies
uv sync --reinstall

# Check Python version
python --version  # Should be 3.11+
```

**4. Test Failures**
```bash
# Clear test database
rm -f test.db

# Run with verbose output
uv run pytest -v -s

# Check if aiosqlite is installed
uv pip list | grep aiosqlite
```

**5. Port Already in Use**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)

# Or use a different port
uv run uvicorn src.main:app --reload --port 8001
```

### Getting Help

- Check the [Phase II Constitution](../.specify/memory/constitution.md) for architectural rules
- Review [Backend Implementation Guide](./CLAUDE.md) for development patterns
- Consult API documentation at http://localhost:8000/docs
- Check ADRs in `history/adr/` for architectural decisions

---
