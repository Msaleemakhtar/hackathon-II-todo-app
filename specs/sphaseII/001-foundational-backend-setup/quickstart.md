# Quickstart Guide: Foundational Backend Setup

**Last Updated**: 2025-12-09
**Feature**: 001-foundational-backend-setup

This guide provides step-by-step instructions for setting up and running the Todo App Phase II backend locally.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Development Workflow](#development-workflow)
7. [Testing](#testing)
8. [API Documentation](#api-documentation)
9. [Docker Deployment](#docker-deployment)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/) or use Docker
- **uv** - Fast Python package installer
  ```bash
  # Install uv
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Or with pip
  pip install uv
  ```
- **Git** - For version control
- **Docker** (optional) - For containerized deployment

**Verify installations:**

```bash
python --version  # Should be 3.11 or higher
uv --version      # Should display uv version
psql --version    # Should be PostgreSQL 15+
```

---

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/todo-app.git
cd todo-app
```

### 2. Checkout the Feature Branch

```bash
git checkout 001-foundational-backend-setup
```

### 3. Navigate to Backend Directory

```bash
cd backend
```

### 4. Install Dependencies with uv

```bash
# Install all dependencies from pyproject.toml
uv pip install -r pyproject.toml

# Or install in development mode
uv pip install -e ".[dev]"
```

**Dependencies installed:**
- FastAPI - Web framework
- SQLModel - ORM and data validation
- asyncpg - Async PostgreSQL driver
- Alembic - Database migrations
- passlib[bcrypt] - Password hashing
- python-jose[cryptography] - JWT tokens
- slowapi - Rate limiting
- pytest-asyncio - Async testing
- httpx - HTTP client for tests

---

## Environment Configuration

### 1. Create `.env` File

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Generate JWT Secret

Generate a cryptographically secure 256-bit (64 hex character) secret:

```bash
# Using openssl
openssl rand -hex 32

# Or using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it into your `.env` file.

### 3. Configure Environment Variables

Edit `.env` with your settings:

```env
# Application
APP_NAME=Todo App API
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://todouser:todopass@localhost:5432/todo_dev
TEST_DATABASE_URL=postgresql+asyncpg://todouser:todopass@localhost:5432/todo_test

# Database Connection Pool
DB_POOL_MIN=2
DB_POOL_MAX=5
DB_POOL_RECYCLE=3600
DB_CONNECTION_TIMEOUT=30

# JWT Secret (REPLACE WITH YOUR GENERATED SECRET)
JWT_SECRET_KEY=your-64-character-hex-secret-here-replace-this-with-actual-secret

# CORS (Development)
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8080","http://localhost:8000"]

# Server
HOST=0.0.0.0
PORT=8000
```

**⚠️ IMPORTANT**: Never commit the `.env` file to version control! The `.env.example` file is provided as a template.

---

## Database Setup

### Option A: PostgreSQL with Docker (Recommended for Development)

```bash
# Start PostgreSQL container
docker run --name todo-postgres \
  -e POSTGRES_USER=todouser \
  -e POSTGRES_PASSWORD=todopass \
  -e POSTGRES_DB=todo_dev \
  -p 5432:5432 \
  -d postgres:15

# Create test database
docker exec -it todo-postgres createdb -U todouser todo_test
```

### Option B: Local PostgreSQL Installation

```bash
# Connect to PostgreSQL
psql -U postgres

# Create user
CREATE USER todouser WITH PASSWORD 'todopass';

# Create databases
CREATE DATABASE todo_dev OWNER todouser;
CREATE DATABASE todo_test OWNER todouser;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE todo_dev TO todouser;
GRANT ALL PRIVILEGES ON DATABASE todo_test TO todouser;

# Exit
\q
```

### Verify Database Connection

```bash
psql -U todouser -d todo_dev -h localhost
# If successful, you should see the psql prompt
\q
```

---

## Database Migrations

### 1. Initialize Alembic (First Time Only)

Alembic should already be configured. Verify configuration:

```bash
# Check alembic.ini and alembic/env.py exist
ls alembic/

# Should show: env.py, script.py.mako, versions/
```

### 2. Generate Initial Migration

```bash
# Auto-generate migration from SQLModel definitions
alembic revision --autogenerate -m "Initial schema: users, tasks, tags, task_tag_link"
```

This creates a new migration file in `alembic/versions/`.

### 3. Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head
```

### 4. Verify Migration Success

```bash
# Check current database version
alembic current

# Should show: [revision_id] (head), Initial schema...
```

### Common Migration Commands

```bash
# View migration history
alembic history

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Show current version
alembic current

# Show SQL without applying
alembic upgrade head --sql
```

---

## Running the Application

### Development Server with Auto-Reload

```bash
# From backend/ directory
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**

```
INFO:     Will watch for changes in these directories: ['/path/to/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Production Server (No Auto-Reload)

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify Server is Running

```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status":"healthy"}
```

---

## Development Workflow

### 1. Creating a New Migration

After modifying SQLModel entities:

```bash
# Generate migration
alembic revision --autogenerate -m "Add new field to Task model"

# Review generated migration in alembic/versions/
# Edit if necessary

# Apply migration
alembic upgrade head
```

### 2. Running Linters and Formatters

```bash
# Lint code with ruff
ruff check src/

# Format code with ruff
ruff format src/

# Security audit with pip-audit
pip-audit
```

### 3. Pre-commit Hooks (Recommended)

Install pre-commit hooks to automatically run checks before commits:

```bash
pip install pre-commit
pre-commit install

# Hooks will now run automatically on git commit
```

### 4. Modifying Environment Variables

After changing `.env`, restart the server for changes to take effect:

```bash
# Stop server (CTRL+C)
# Start server again
uvicorn src.main:app --reload
```

---

## Testing

### Run All Tests

```bash
# From backend/ directory
pytest

# With coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run Specific Test Files

```bash
# Test authentication endpoints
pytest tests/test_auth.py

# Test database models
pytest tests/test_models.py

# Test security utilities
pytest tests/test_security.py
```

### Run Tests with Verbose Output

```bash
pytest -v -s
```

### Test Database Setup

The test suite automatically:
1. Creates a test database (`todo_test`)
2. Applies migrations
3. Uses transactions for test isolation
4. Rolls back changes after each test

No manual test database management required!

---

## API Documentation

FastAPI provides automatic interactive API documentation.

### Swagger UI

Navigate to: **http://localhost:8000/docs**

Features:
- Interactive API explorer
- Try out endpoints with sample requests
- View request/response schemas
- OAuth2 authentication testing

### ReDoc

Navigate to: **http://localhost:8000/redoc**

Features:
- Clean, searchable documentation
- Downloadable OpenAPI spec
- Better for reading and sharing

### OpenAPI JSON

Download the raw OpenAPI specification:

**http://localhost:8000/openapi.json**

---

## Common Development Tasks

### Test User Registration

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "name": "Test User"
  }'
```

**Expected response (201 Created):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "name": "Test User",
  "created_at": "2025-12-09T10:30:00Z"
}
```

### Test User Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"
```

**Expected response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Test Protected Endpoint

```bash
# Save access token from login response
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected response (200 OK):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "name": "Test User",
  "created_at": "2025-12-09T10:30:00Z"
}
```

---

## Docker Deployment

### Build Docker Image

```bash
# From backend/ directory
docker build -t todo-backend:latest .
```

### Run with Docker Compose

```bash
# From repository root
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### `docker-compose.yml` Example

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
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U todouser"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://todouser:todopass@db:5432/todo_dev
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      CORS_ORIGINS: '["http://localhost:3000"]'
    depends_on:
      db:
        condition: service_healthy
    command: >
      sh -c "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"

volumes:
  postgres_data:
```

### Run Migrations in Docker

```bash
# Execute migrations before starting server
docker-compose exec backend alembic upgrade head

# Or include in docker-compose.yml command (see example above)
```

---

## Troubleshooting

### Common Issues

#### 1. `ModuleNotFoundError: No module named 'sqlmodel'`

**Solution**: Install dependencies with uv

```bash
uv pip install -r pyproject.toml
```

#### 2. `sqlalchemy.exc.OperationalError: connection refused`

**Solution**: PostgreSQL is not running or connection details are incorrect

```bash
# Check PostgreSQL status
docker ps  # If using Docker
sudo systemctl status postgresql  # If using system PostgreSQL

# Verify DATABASE_URL in .env matches your PostgreSQL setup
```

#### 3. `ValueError: JWT_SECRET_KEY must be at least 64 characters`

**Solution**: Generate a proper JWT secret

```bash
openssl rand -hex 32
# Copy output to JWT_SECRET_KEY in .env
```

#### 4. `alembic.util.exc.CommandError: Can't locate revision identified by 'head'`

**Solution**: Initialize Alembic or create first migration

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

#### 5. Test failures: `asyncpg.exceptions.InvalidCatalogNameError: database "todo_test" does not exist`

**Solution**: Create test database

```bash
# Docker
docker exec -it todo-postgres createdb -U todouser todo_test

# Local PostgreSQL
createdb -U todouser todo_test
```

#### 6. Port 8000 already in use

**Solution**: Kill existing process or use different port

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn src.main:app --reload --port 8001
```

---

## Next Steps

After successfully setting up the backend:

1. **Explore API Documentation**: Visit http://localhost:8000/docs
2. **Run Tests**: Ensure all tests pass with `pytest`
3. **Review Data Model**: See `specs/001-foundational-backend-setup/data-model.md`
4. **Check API Contracts**: Review `specs/001-foundational-backend-setup/contracts/auth-api.yaml`
5. **Proceed to Implementation**: Run `/sp.tasks` to generate task breakdown

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## Support

For issues or questions:
1. Check this quickstart guide
2. Review the troubleshooting section
3. Consult the feature specification at `specs/001-foundational-backend-setup/spec.md`
4. Open an issue on GitHub
