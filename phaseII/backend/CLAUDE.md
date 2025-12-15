# Backend Implementation Guide

## Constitutional Reference

This guide provides a high-level summary of backend practices. All development **MUST** adhere to the principles and rules defined in the main constitution at `.specify/memory/constitution.md`.

## Technology Stack & Structure

The technology stack and project structure are non-negotiable and are defined in **Section II** of the constitution.

### Key Libraries
- `fastapi`, `sqlmodel`, `asyncpg`, `alembic`, `pydantic-settings`, `python-jose`, `passlib`, `pytest`, `testcontainers`.

### Project Structure
```
backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── routers/             # API routers (one per resource)
│   ├── models/              # SQLModel entities
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic layer
│   ├── core/              # Config, DB, security, dependencies
│   └── utils/               # Helper functions
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── alembic/
│   └── versions/            # Migration files
├── pyproject.toml
└── .env
```

## Key Implementation Patterns

### Routers and API Versioning
- **Location:** `/src/routers/`
- **Pattern:** Use `APIRouter` for each resource.
- **Registration:** Register all routers in `main.py` with the `/api/v1/` prefix as mandated by **Section V** of the constitution.

### Database Management
- **Rules:** All database interactions must follow the rules in **Section III** of the constitution (SQLModel, async, Alembic migrations).
- **Async Operations:** All database calls must use `async`/`await`.
- **Data Isolation:** All queries **MUST** be scoped to the authenticated user's ID as per **Section IV**.
- **Migrations:** Use `uv run alembic revision --autogenerate` to create migrations and `uv run alembic upgrade head` to apply them.

### Authentication & Authorization
- **Source of Truth:** All security logic is defined in **Section IV** of the constitution.
- **Responsibility:** The backend is solely responsible for authenticating users and issuing JWTs.
- **Validation:** A FastAPI dependency must be used to validate tokens on protected routes.
- **Path Parameter Matching:** As per **Section IV**, you **MUST** validate that any `user_id` in an API path matches the `user_id` from the JWT.

### Configuration & Error Handling
- **Configuration:** Use `pydantic-settings` loaded from environment variables as defined in **Section V**.
- **Error Handling:** Follow the standard error response format and HTTP status codes defined in **Section V**.

### Testing
- **Framework:** `pytest` with `pytest-asyncio`.
- **Database:** Use `testcontainers` for isolated test databases.
- **Structure:** Organize tests into `unit/` and `integration/` directories as per **Section VII**.
- **Execution:** Run tests via `uv run pytest`.

## Development Workflow

### Package Management (`uv`)
The constitution mandates `uv` for all Python package management.
```bash
# Install all dependencies
uv sync

# Add a new package
uv add <package-name>

# Run the dev server
uv run uvicorn src.main:app --reload --port 8000

# Run tests
uv run pytest
```

### Pre-commit Hooks
Pre-commit hooks for linting (`ruff check`), formatting (`ruff format`), and security (`pip-audit`) are enforced as per **Section V** of the constitution. They **MUST** pass before committing.

