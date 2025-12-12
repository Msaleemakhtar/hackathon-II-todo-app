# Todo App Backend

This is the backend service for the Todo App, built with FastAPI, SQLModel, and PostgreSQL. This project follows **Spec-Driven Development (SDD)** principles as defined in the [Phase II Constitution](../.specify/memory/constitution.md).

## Features

- **Better Auth Integration** - Frontend handles authentication, backend validates JWT tokens
- User Registration & Authentication (JWT based)
- User Login & Token Refresh with secure token management
- Access Protected Resources with JWT validation
- User Profile Management API with CRUD operations
- Task Management API with CRUD operations, filtering, sorting, and search
- Category Management API for task organization and grouping
- Tag Management API for task categorization and labeling
- Task-Tag Association API for many-to-many relationships
- Database with SQLModel entities (User, Task, Category, Tag, TaskTagLink)
  - Task: title (max 200 chars), description (max 1000 chars), status (pending/in_progress/completed), priority (low/medium/high), due_date, category, recurrence_rule (iCal RRULE), timestamps
  - Category: name (max 100 chars, unique per user), description (max 500 chars), color (hex format #RRGGBB or #RGB)
  - Tag: name (max 50 chars, unique per user), color (hex format #RRGGBB or #RGB)
  - TaskTagLink: Many-to-many association table with composite primary key (task_id, tag_id)
- Alembic for database migrations
- Performance-optimized indexes for common queries
- Rate limiting on authentication endpoints
- RESTful API with `/api/v1/` versioning
- Comprehensive async database operations
- Strict data isolation - users can only access their own resources

## Constitutional Reference

All backend development **MUST** adhere to the principles defined in:
- **Main Constitution**: `../.specify/memory/constitution.md`
- **Backend Guide**: `./CLAUDE.md`
- **Better Auth Integration**: `../BETTER_AUTH_IMPLEMENTATION.md`

## Better Auth Integration Flow

This backend integrates with a **Better Auth frontend** and validates JWT tokens for API authentication.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         AUTHENTICATION FLOW                      │
└─────────────────────────────────────────────────────────────────┘

  Frontend (Next.js)              Backend (FastAPI)          Database
  ──────────────────              ─────────────────          ────────

1. User Signup/Login
   │
   ├─> Better Auth (/api/auth)
   │   Creates session
   │   Stores in PostgreSQL ───────────────────────────> [Better Auth]
   │                                                       [Sessions]
   │
2. API Request
   │
   ├─> GET /api/auth/token
   │   (generates JWT from session)
   │
   │<── JWT Token (15 min expiry)
   │    Signed with BETTER_AUTH_SECRET
   │    Payload: {user_id, email, exp}
   │
3. Backend API Call
   │
   ├─> GET /api/v1/tasks
   │   Header: Authorization: Bearer <JWT>
   │                            │
   │                            ├──> JWT Validation
   │                            │    (python-jose)
   │                            │    - Verify signature
   │                            │    - Check expiration
   │                            │    - Extract user_id
   │                            │
   │                            ├──> Query Database
   │                            │    WHERE user_id = <from_jwt>
   │                            │    (Data Isolation) ──────> [Tasks]
   │                            │                             [Tags]
   │<─────────────────────────-┘                             [Categories]
   │   Response: User's tasks only
   │

┌─────────────────────────────────────────────────────────────────┐
│                         KEY COMPONENTS                           │
└─────────────────────────────────────────────────────────────────┘

Frontend:
  • Better Auth server (Next.js API routes)
  • Session management (PostgreSQL storage)
  • JWT token generation endpoint (/api/auth/token)
  • Axios interceptor (auto-adds JWT to requests)

Backend:
  • JWT validation dependency (src/core/dependencies.py)
  • User ID extraction from token
  • Data isolation enforcement (all queries scoped to user_id)
  • No session storage (stateless authentication)

Shared:
  • BETTER_AUTH_SECRET (must match between frontend & backend)
  • PostgreSQL database (separate tables for auth vs. app data)

Security:
  • JWT tokens expire after 15 minutes
  • Better Auth sessions persist for 7 days
  • Automatic token refresh on API calls
  • HTTPS required in production
  • CORS configured for frontend origin only
```

### JWT Token Structure

```json
{
  "user_id": "ba_user_abc123",
  "email": "user@example.com",
  "exp": 1702345678
}
```

### Backend Validation Logic

The backend validates JWT tokens on every protected endpoint:

1. **Extract Token**: From `Authorization: Bearer <token>` header
2. **Verify Signature**: Using `BETTER_AUTH_SECRET` (python-jose)
3. **Check Expiration**: Reject if `exp` < current time
4. **Extract User ID**: Get `user_id` from token payload
5. **Enforce Data Isolation**: All queries filtered by `user_id`

See `backend/src/core/security.py` and `backend/src/core/dependencies.py` for implementation details.

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
   DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]/[database]?ssl=require
   ```

**IMPORTANT**: For asyncpg (async PostgreSQL driver), use `?ssl=require` instead of `?sslmode=require`. The `sslmode` parameter is for psycopg2 (sync driver) only.

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

**IMPORTANT**: Ensure all models are imported in `alembic/env.py` before generating migrations:
- ✅ User
- ✅ Task
- ✅ Tag
- ✅ TaskTagLink
- ✅ Category (added in migration fix)

Apply existing migrations:
```bash
uv run alembic upgrade head
```

To create new migrations after model changes:
```bash
# Generate migration
uv run alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in alembic/versions/
# IMPORTANT: Check for any references to Better Auth tables (user, account, session, verification)
# Remove any DROP TABLE statements for Better Auth tables

# Apply the migration
uv run alembic upgrade head
```

**Migration Best Practices**:
1. Always review auto-generated migrations before applying
2. Never drop Better Auth tables (user, account, session, verification)
3. Import `sqlmodel.sql.sqltypes` if using AutoString types
4. Test migrations on a development database first

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

**Note**: Authentication is handled by **Better Auth** on the frontend. The backend validates JWT tokens.

- `POST /api/v1/auth/register` - Register a new user (legacy, use Better Auth instead)
- `POST /api/v1/auth/login` - Login and receive JWT tokens (legacy, use Better Auth instead)
- `POST /api/v1/auth/refresh` - Refresh access token using refresh token (legacy)
- `GET /api/v1/auth/me` - Get current authenticated user profile (protected)

**Rate Limiting**: Authentication endpoints are rate-limited to prevent abuse.

**Recommended Flow**: Use Better Auth on the frontend (`/api/auth/*` routes) for all authentication operations.

### Users (`/api/v1/users`)
All user endpoints require authentication via Bearer token.

- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile (name, email, preferences)
- `DELETE /api/v1/users/me` - Delete current user account

### Tasks (`/api/v1/tasks`)
All task endpoints require authentication via Bearer token.

- `POST /api/v1/tasks` - Create a new task
- `GET /api/v1/tasks` - List tasks with filtering, sorting, and pagination
  - Query params: `page`, `limit`, `q` (search), `status` (all/pending/in_progress/completed), `priority` (low/medium/high), `category_id` (integer), `tag` (ID or name), `sort` (due_date/priority/created_at/title, prefix with `-` for descending)
- `GET /api/v1/tasks/{task_id}` - Get a specific task
- `PUT /api/v1/tasks/{task_id}` - Update all fields of a task
- `PATCH /api/v1/tasks/{task_id}` - Partially update a task (e.g., mark complete, change status)
- `DELETE /api/v1/tasks/{task_id}` - Delete a task

### Categories (`/api/v1/categories`)
All category endpoints require authentication via Bearer token.
- `GET /api/v1/categories/{category_id}` - Get a specific category with task count
- `PUT /api/v1/categories/{category_id}` - Update a category
- `DELETE /api/v1/categories/{category_id}` - Delete a category (sets category_id to NULL for associated tasks)

### Tags (`/api/v1/tags`)
All tag endpoints require authentication via Bearer token.

- `POST /api/v1/tags` - Create a new tag
- `GET /api/v1/tags` - List all tags for the authenticated user
- `GET /api/v1/tags/{tag_id}` - Get a specific tag
- `PUT /api/v1/tags/{tag_id}` - Update a tag
- `DELETE /api/v1/tags/{tag_id}` - Delete a tag (removes tag associations from tasks)

### Task-Tag Association (`/api/v1/tasks/{task_id}/tags/{tag_id}`)
Endpoints for managing many-to-many relationships between tasks and tags.

- `POST /api/v1/tasks/{task_id}/tags/{tag_id}` - Associate a tag with a task
- `DELETE /api/v1/tasks/{task_id}/tags/{tag_id}` - Dissociate a tag from a task

**Data Isolation**: All endpoints enforce strict data isolation. Users can ONLY access their own tasks and tags. Attempts to access another user's resources return `404 Not Found`.

### API Response Formats

**Task Response (`TaskRead`):**
```json
{
  "id": 1,
  "title": "Complete project",
  "description": "Finish the todo app",
  "status": "in_progress",
  "completed": false,
  "priority": "high",
  "due_date": "2025-12-31T23:59:59Z",
  "recurrence_rule": null,
  "category_id": 2,
  "user_id": "ba_user_abc123",
  "created_at": "2025-12-09T10:00:00Z",
  "updated_at": "2025-12-09T10:00:00Z",
  "tags": [
    {"id": 1, "name": "work", "color": "#FF5733", "user_id": "ba_user_abc123"}
  ]
}
```

**Category Response (`CategoryRead`):**
```json
{
  "id": 2,
  "name": "Work Projects",
  "description": "Tasks related to work and professional development",
  "color": "#3B82F6",
  "user_id": "ba_user_abc123",
  "created_at": "2025-12-09T10:00:00Z",
  "updated_at": "2025-12-09T10:00:00Z"
}
```

**Paginated Tasks Response:**
```json
{
  "items": [/* array of TaskRead objects */],
  "total": 42,
  "page": 1,
  "limit": 20,
  "pages": 3
}
```

**Tag Response (`TagRead`):**
```json
{
  "id": 1,
  "name": "work",
  "color": "#FF5733",
  "user_id": "user-uuid"
}
```

### HTTP Status Codes

The API uses standard HTTP status codes:

**Success:**
- `200 OK` - Successful GET, PUT, PATCH requests
- `201 Created` - Successful POST requests (resource created)
- `204 No Content` - Successful DELETE requests

**Client Errors:**
- `400 Bad Request` - Invalid request body or parameters
- `401 Unauthorized` - Missing or invalid authentication token
- `404 Not Found` - Resource doesn't exist or user doesn't own it
- `409 Conflict` - Resource conflict (e.g., duplicate tag name)
- `422 Unprocessable Entity` - Validation error (detailed error messages provided)
- `429 Too Many Requests` - Rate limit exceeded (auth endpoints)

**Server Errors:**
- `500 Internal Server Error` - Unexpected server error

All error responses include a descriptive message in JSON format:
```json
{
  "detail": "Error description here"
}
```

### Validation Rules

**Task Validation:**
- `title`: Required, 1-200 characters
- `description`: Optional, max 1000 characters
- `status`: Must be one of: "pending", "in_progress", "completed" (defaults to "pending")
- `completed`: Boolean (auto-computed from status: status == "completed")
- `priority`: Must be one of: "low", "medium", "high" (defaults to "medium")
- `due_date`: Optional ISO 8601 datetime
- `recurrence_rule`: Optional string in iCal RRULE format (e.g., "FREQ=DAILY;COUNT=10")
- `category_id`: Optional integer (foreign key to categories)

**Category Validation:**
- `name`: Required, max 100 characters, must be unique per user
- `description`: Optional, max 500 characters
- `color`: Optional, must match hex color format: #RRGGBB or #RGB (e.g., "#3B82F6" or "#38F")

**Tag Validation:**
- `name`: Required, max 50 characters, must be unique per user
- `color`: Optional, must match hex color format: #RRGGBB or #RGB (e.g., "#FF5733" or "#F73")

**Query Parameters (Task Listing):**
- `page`: Integer >= 1 (default: 1)
- `limit`: Integer 1-100 (default: 20, capped at 100)
- `status`: One of "all", "pending", "in_progress", "completed" (default: "all")
- `priority`: One of "low", "medium", "high"
- `category_id`: Integer (filter by category)
- `tag`: Tag ID (integer) or tag name (string)
- `q`: Search string (searches title and description)
- `sort`: One of "due_date", "priority", "created_at", "title" (prefix with "-" for descending, e.g., "-created_at")

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

### Data Model Details

**Task Entity:**
- `id`: Integer primary key (auto-increment)
- `title`: String (1-200 chars, indexed, required)
- `description`: String (max 1000 chars, optional)
- `status`: Enum string ("pending" | "in_progress" | "completed", default: "pending", indexed)
- `completed`: Boolean (computed property: status == "completed")
- `priority`: Enum string ("low" | "medium" | "high", default: "medium", indexed)
- `due_date`: DateTime (optional, indexed for sorting)
- `recurrence_rule`: String (iCal RRULE format for recurring tasks, optional)
- `category_id`: Integer (foreign key to categories.id, optional, indexed, nullable)
- `user_id`: String (foreign key to users.id, indexed, required)
- `created_at`: DateTime (auto-set on creation, indexed)
- `updated_at`: DateTime (auto-updated on modification)
- **Relationships**: Belongs to one User, belongs to one Category (optional), has many Tags (via TaskTagLink)
- **Indexes**: Composite index on (user_id, status, priority) for efficient filtering

**Category Entity:**
- `id`: Integer primary key (auto-increment)
- `name`: String (max 100 chars, indexed, required)
- `description`: String (max 500 chars, optional)
- `color`: String (hex color #RRGGBB or #RGB, optional)
- `user_id`: String (foreign key to users.id, indexed, required)
- `created_at`: DateTime (auto-set on creation)
- `updated_at`: DateTime (auto-updated on modification)
- **Constraints**: Unique constraint on (name, user_id) - users cannot have duplicate category names
- **Relationships**: Belongs to one User, has many Tasks
- **Indexes**: Composite index on (user_id, name) for efficient lookups

**Tag Entity:**
- `id`: Integer primary key (auto-increment)
- `name`: String (max 50 chars, indexed, required)
- `color`: String (hex color #RRGGBB or #RGB, optional)
- `user_id`: String (foreign key to users.id, indexed, required)
- **Constraints**: Unique constraint on (name, user_id) - users cannot have duplicate tag names
- **Relationships**: Belongs to one User, has many Tasks (via TaskTagLink)
- **Indexes**: Composite index on (user_id, name) for efficient lookups

**TaskTagLink Entity:**
- `task_id`: Integer (foreign key to tasks.id, composite primary key)
- `tag_id`: Integer (foreign key to tags.id, composite primary key)
- **Purpose**: Many-to-many join table between Tasks and Tags

**Database Indexes:**
- Tasks: Indexed on `user_id` and `title` for efficient queries
- Tags: Indexed on `user_id` and `name` for efficient lookups
- TaskTagLink: Composite primary key on (task_id, tag_id) provides automatic indexing

**Timestamps:**
- All timestamps stored in UTC
- `created_at`: Auto-set on record creation
- `updated_at`: Auto-updated on any modification using database trigger

### Security Features
- Password hashing with bcrypt (bcrypt>=4.0.0)
- JWT tokens with expiration (access: 30 min, refresh: 7 days) using python-jose[cryptography]
- Rate limiting on authentication endpoints (slowapi)
- CORS configuration for cross-origin requests
- Email validation for user registration (email-validator>=2.3.0)
- Environment-based configuration (no hardcoded secrets)

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app entry point, CORS, rate limiting
│   ├── routers/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── tasks.py         # Task CRUD endpoints
│   │   └── tags.py          # Tag CRUD endpoints
│   ├── models/
│   │   ├── user.py          # User entity (SQLModel)
│   │   ├── task.py          # Task entity
│   │   ├── tag.py           # Tag entity
│   │   └── task_tag_link.py # Many-to-many relationship
│   ├── schemas/
│   │   ├── auth.py          # Authentication request/response schemas
│   │   ├── user.py          # User schemas
│   │   ├── token.py         # JWT token schemas
│   │   ├── task.py          # Task request/response schemas
│   │   └── tag.py           # Tag request/response schemas
│   ├── services/
│   │   ├── auth_service.py  # Authentication business logic
│   │   ├── task_service.py  # Task CRUD business logic
│   │   └── tag_service.py   # Tag CRUD business logic
│   └── core/
│       ├── config.py        # Pydantic settings from environment
│       ├── database.py      # Database engine and session management
│       ├── security.py      # JWT and password utilities
│       ├── dependencies.py  # FastAPI dependencies (auth, DB)
│       ├── exceptions.py    # Custom exception classes
│       └── logging_config.py # Structured logging setup
├── tests/
│   ├── conftest.py          # Pytest fixtures (test DB setup)
│   ├── test_auth.py         # Authentication endpoint tests
│   ├── test_tasks.py        # Task endpoint tests
│   ├── test_tags.py         # Tag endpoint tests
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

## Key Dependencies

**Core Framework & Database:**
- `fastapi` - Modern, fast web framework for building APIs
- `sqlmodel` - SQL databases using Python objects (combines SQLAlchemy + Pydantic)
- `asyncpg` - High-performance PostgreSQL driver for async operations
- `aiosqlite` - Async SQLite driver (used for testing)
- `alembic` - Database migration tool
- `uvicorn[standard]` - ASGI server for running FastAPI

**Authentication & Security:**
- `bcrypt>=4.0.0` - Password hashing
- `python-jose[cryptography]` - JWT token creation and validation
- `email-validator>=2.3.0` - Email address validation

**API Enhancement:**
- `pydantic-settings` - Settings management from environment variables
- `slowapi` - Rate limiting for API endpoints
- `python-multipart>=0.0.20` - Support for file uploads and form data

**Logging & Monitoring:**
- `python-json-logger` - Structured JSON logging

**Development & Testing:**
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Code coverage reporting
- `pytest-xdist` - Parallel test execution
- `httpx` - HTTP client for testing API endpoints
- `ruff` - Fast Python linter and formatter
- `pip-audit` - Security vulnerability scanner
- `pre-commit` - Git hook framework for pre-commit checks

## Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Verify DATABASE_URL is correct and uses ssl=require (NOT sslmode=require)
echo $DATABASE_URL

# Test PostgreSQL connection (if using Neon)
psql $DATABASE_URL -c "SELECT version();"

# Check if migrations are applied
uv run alembic current
uv run alembic upgrade head

# If no migrations exist, check alembic/versions/ directory
ls -la alembic/versions/
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

**5. Tasks/Categories Creation Fails**
```bash
# Symptom: 404 errors or "table does not exist" when creating tasks/categories
# Cause: Database migrations not applied

# Solution: Apply migrations
uv run alembic upgrade head

# Verify tables exist
uv run python -c "
import asyncio
from sqlalchemy import text
from src.core.database import engine

async def check_tables():
    async with engine.begin() as conn:
        result = await conn.execute(text(
            \"SELECT table_name FROM information_schema.tables WHERE table_schema='public'\"
        ))
        print('Tables:', [r[0] for r in result])
    await engine.dispose()

asyncio.run(check_tables())
"

# Expected tables: users, tasks, categories, tags, task_tag_link, user, account, session, verification
```

**6. Category Model Not in Migrations**
```bash
# Symptom: Categories table not created even after running migrations
# Cause: Missing import in alembic/env.py

# Solution: Check alembic/env.py includes all models:
grep "from src.models" alembic/env.py

# Should see:
# from src.models.user import User
# from src.models.task import Task
# from src.models.tag import Tag
# from src.models.task_tag_link import TaskTagLink
# from src.models.category import Category  # This was missing!
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

### Migration Issues and Fixes

#### Issue 1: Missing Database Schema (FIXED - December 2025)

**Problem**: Tasks and categories creation failed because no database migrations existed.

**Root Cause**:
- Empty `alembic/versions/` directory (no migration files)
- Missing Category model import in `alembic/env.py`
- Invalid SSL parameter in DATABASE_URL (`sslmode` instead of `ssl`)

**Solution Applied**:
1. ✅ Added `from src.models.category import Category` to `alembic/env.py:20`
2. ✅ Fixed DATABASE_URL to use `?ssl=require` for asyncpg compatibility
3. ✅ Generated initial migration: `dfd778d535ec_initial_migration_with_all_tables.py`
4. ✅ Removed Better Auth table drops from migration
5. ✅ Applied migration successfully

**Current Database Schema**:
```
✅ users          - FastAPI user records (synced from Better Auth)
✅ tasks          - Task entities with status, priority, due dates
✅ categories     - Custom task categories (priority/status types)
✅ tags           - Task tags with colors
✅ task_tag_link  - Many-to-many task-tag relationships
✅ user           - Better Auth user accounts (DO NOT DROP)
✅ account        - Better Auth credentials (DO NOT DROP)
✅ session        - Better Auth sessions (DO NOT DROP)
✅ verification   - Better Auth tokens (DO NOT DROP)
```

#### Issue 2: Better Auth Table Conflicts

**⚠️ CRITICAL**: Never drop Better Auth tables in migrations:
- `user` - User account information
- `account` - Authentication credentials
- `session` - Active user sessions
- `verification` - Verification tokens

**Prevention**:
1. Always review auto-generated migrations before applying
2. Remove any `op.drop_table()` calls for Better Auth tables
3. Add comment: `# Note: Better Auth tables are NOT managed by this migration`

**Example of Safe Migration**:
```python
def upgrade():
    # Note: Better Auth tables (user, account, session, verification) are NOT managed by this migration

    # Only modify FastAPI backend tables
    op.alter_column('categories', 'name', ...)
    op.create_index('ix_tasks_title', 'tasks', ['title'])
```

#### Issue 3: AsyncPG SSL Parameter Error

**Problem**: `TypeError: connect() got an unexpected keyword argument 'sslmode'`

**Solution**: Use `ssl=require` instead of `sslmode=require` for asyncpg:
```bash
# ❌ Wrong (psycopg2 syntax)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require

# ✅ Correct (asyncpg syntax)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?ssl=require
```

#### Issue 4: Missing sqlmodel Import in Migration

**Problem**: `NameError: name 'sqlmodel' is not defined`

**Solution**: Add import to migration file:
```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel.sql.sqltypes  # Add this line
```

---
