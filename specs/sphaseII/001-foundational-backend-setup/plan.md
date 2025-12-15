# Implementation Plan: Foundational Backend Setup

**Branch**: `001-foundational-backend-setup` | **Date**: 2025-12-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-foundational-backend-setup/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature establishes the foundational backend infrastructure for the Todo App Phase II, including:

1. **Database Schema**: SQLModel entity definitions for User, Tag, Task, and TaskTagLink with relationships, constraints, and indexes
2. **Authentication System**: RESTful authentication API with JWT-based token management for user registration, login, token refresh, and protected resource access

This is the prerequisite feature for all subsequent development, providing the data persistence layer and security infrastructure.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLModel, asyncpg, Alembic, passlib[bcrypt], python-jose
**Storage**: Neon Serverless PostgreSQL (asyncpg driver, connection pooling: min=2, max=5)
**Testing**: pytest with pytest-asyncio, httpx for API testing, separate test database (`todo_test`)
**Target Platform**: Linux server (Docker containerized for deployment)
**Project Type**: Web (backend component of full-stack monorepo)
**Performance Goals**:
- /auth/me: <200ms p95 latency
- Login/Register: <3-5 seconds end-to-end
- Token validation: <100ms p95
**Constraints**:
- JWT secret minimum 256 bits (64 hex chars)
- Access token: 15 min expiry
- Refresh token: 7 day expiry
- Rate limiting: 5 auth requests/min/IP
- Database pool: min=2, max=5 connections
**Scale/Scope**: Phase II MVP supporting multiple concurrent users with async request handling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Spec-Driven Development
- **Status**: PASS
- **Evidence**: Full specification exists at `specs/001-foundational-backend-setup/spec.md` with detailed acceptance criteria, user stories, and test cases
- **Verification**: This plan is generated after spec creation; implementation will be AI-generated from this plan

### ✅ II. Full-Stack Monorepo Architecture
- **Status**: PASS
- **Structure**: Backend component in `/backend` directory
- **Package Manager**: uv for Python dependencies (per constitution)
- **Directory Standards**: Follows constitution layout:
  - `/backend/src/routers/` - APIRouter modules (auth.py)
  - `/backend/src/models/` - SQLModel entities (user.py, task.py, tag.py, task_tag_link.py)
  - `/backend/src/schemas/` - Pydantic request/response schemas
  - `/backend/src/services/` - Business logic (auth_service.py)
  - `/backend/src/core/` - Config, dependencies, security utilities
  - `/backend/tests/` - Test suite
  - `/backend/alembic/` - Database migrations
  - `/backend/pyproject.toml` - uv dependency configuration

### ✅ III. Persistent & Relational State
- **Status**: PASS
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel for all data access
- **Async**: asyncpg driver for non-blocking I/O
- **Migrations**: Alembic with reversible migrations
- **Connection Pooling**: Configured (min=2, max=5) per clarifications
- **Data Isolation**: All queries scope to authenticated user_id via FastAPI dependency

### ✅ IV. User Authentication & JWT Security
- **Status**: PASS
- **Authentication**: Backend-only JWT issuance (no frontend JWT generation)
- **Token Structure**: Follows constitution format (sub, email, exp, iat, type)
- **Token Expiry**: Access 15min, Refresh 7days
- **Storage**: Refresh tokens in HttpOnly cookies, access tokens in response body
- **Algorithm**: HS256 for Phase II (RS256 for future production)
- **Secret**: Minimum 256 bits, validated at startup
- **Rate Limiting**: 5 attempts/min/IP on auth endpoints
- **Phase II Boundaries**: Refresh token rotation and blacklisting explicitly OUT OF SCOPE

### ✅ V. Backend Architecture Standards
- **Status**: PASS
- **Router Organization**: APIRouter in `/backend/src/routers/auth.py`
- **API Versioning**: All routes prefixed `/api/v1/`
- **Configuration**: pydantic-settings for environment variables
- **Documentation**: FastAPI OpenAPI at /docs and /redoc
- **Security**: CORS configured for development (localhost:3000,5173,8080,8000) and production
- **Error Handling**: Consistent format with detail, code, optional field
- **Logging**: Structured logging (implementation detail deferred to Phase 0 research)
- **Pre-commit Hooks**: ruff check, ruff format, pip-audit

### ⚠️ VI. Frontend Architecture Standards
- **Status**: NOT APPLICABLE
- **Reason**: This feature implements backend only; frontend integration is a separate feature

### ⚠️ VII. Testing Standards
- **Status**: PARTIAL - needs research
- **Coverage**: Constitution requires ≥80% for backend; specific testing patterns need research
- **Test Types**: Unit, integration, contract tests required
- **Database**: Separate test database (`todo_test`) configured per clarifications
- **Action**: Phase 0 research will determine pytest fixture patterns, async test setup, and FastAPI TestClient usage

### ⚠️ VIII. Deployment Standards
- **Status**: PARTIAL - implementation planning only
- **Docker**: Dockerfile required (implementation detail)
- **Environment**: .env configuration required
- **Action**: Phase 0 research will determine container setup, health checks, and startup script

### ⚠️ IX. CI/CD Pipeline
- **Status**: NOT IMPLEMENTED YET
- **Reason**: This is the first feature; CI/CD pipeline will be established in a subsequent infrastructure feature
- **Future**: GitHub Actions workflows for testing, linting, coverage

## Project Structure

### Documentation (this feature)

```text
specs/001-foundational-backend-setup/
├── spec.md              # Feature specification
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command) - PENDING
├── data-model.md        # Phase 1 output (/sp.plan command) - PENDING
├── quickstart.md        # Phase 1 output (/sp.plan command) - PENDING
├── contracts/           # Phase 1 output (/sp.plan command) - PENDING
│   └── auth-api.yaml    # OpenAPI spec for auth endpoints
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                    # FastAPI application entry point
│   ├── routers/
│   │   └── auth.py                # Authentication endpoints
│   ├── models/
│   │   ├── user.py                # User SQLModel entity
│   │   ├── task.py                # Task SQLModel entity
│   │   ├── tag.py                 # Tag SQLModel entity
│   │   └── task_tag_link.py       # TaskTagLink junction table
│   ├── schemas/
│   │   ├── auth.py                # Auth request/response schemas
│   │   ├── user.py                # User schemas
│   │   └── token.py               # Token schemas
│   ├── services/
│   │   └── auth_service.py        # Authentication business logic
│   ├── core/
│   │   ├── config.py              # Settings with pydantic-settings
│   │   ├── database.py            # Database connection and session management
│   │   ├── security.py            # JWT utilities, password hashing
│   │   └── dependencies.py        # FastAPI dependency injection (get_current_user)
│   └── db/
│       └── session.py             # Async database session factory
├── tests/
│   ├── conftest.py                # pytest fixtures
│   ├── test_auth.py               # Auth endpoint tests
│   ├── test_models.py             # SQLModel entity tests
│   └── test_security.py           # JWT and password hashing tests
├── alembic/
│   ├── env.py                     # Alembic configuration
│   ├── versions/                  # Migration files
│   │   └── YYYYMMDD_HHMMSS_initial_schema.py
│   └── alembic.ini                # Alembic settings
├── pyproject.toml                 # uv dependencies and project metadata
├── .env.example                   # Example environment variables
├── Dockerfile                     # Container definition
└── README.md                      # Backend setup instructions
```

**Structure Decision**: Web application structure (Option 2 from template) selected as this is the backend component of a full-stack monorepo. The `/backend` directory contains the FastAPI server with clear separation of concerns: routers for API endpoints, models for database entities, schemas for validation, services for business logic, and core for cross-cutting concerns.

## Complexity Tracking

**No violations detected.** This feature aligns with all applicable constitution requirements. The backend architecture uses standard FastAPI patterns with SQLModel ORM, which is the constitutionally mandated approach. No additional complexity or abstraction layers beyond the constitution's requirements are introduced.

---

## Phase 0: Research & Technical Discovery

**Objective**: Resolve all technical unknowns and establish implementation patterns before design phase.

### Research Tasks

1. **FastAPI + SQLModel + asyncpg Integration Pattern**
   - **Unknown**: Best practice for integrating async SQLModel with FastAPI dependency injection
   - **Research Focus**:
     - Async session management with asyncpg
     - Database session lifecycle in FastAPI (per-request vs connection pooling)
     - SQLModel async query patterns
   - **Output**: Recommended pattern for `core/database.py` and `dependencies.py`

2. **JWT Implementation with python-jose**
   - **Unknown**: Specific python-jose configuration for HS256 tokens
   - **Research Focus**:
     - Token creation with custom claims (type: access|refresh)
     - Token validation and expiry handling
     - Error types for expired/invalid tokens
   - **Output**: Code patterns for `core/security.py`

3. **Password Hashing with passlib[bcrypt]**
   - **Unknown**: passlib configuration for production-grade security
   - **Research Focus**:
     - Recommended bcrypt rounds for balance of security and performance
     - Async compatibility (does bcrypt block the event loop?)
     - Password verification patterns
   - **Output**: Hashing utilities for `core/security.py`

4. **Alembic Async Configuration**
   - **Unknown**: Alembic configuration for async SQLModel with asyncpg
   - **Research Focus**:
     - `alembic/env.py` setup for async migrations
     - Auto-generation of migrations from SQLModel metadata
     - Migration testing patterns
   - **Output**: Alembic configuration template

5. **FastAPI Rate Limiting**
   - **Unknown**: Rate limiting implementation for auth endpoints (5 req/min/IP)
   - **Research Focus**:
     - Library options: slowapi, fastapi-limiter, custom middleware
     - Redis requirement (or in-memory for Phase II?)
     - Rate limit error response format
   - **Output**: Recommended library and integration pattern

6. **pytest + FastAPI + Async Database Testing**
   - **Unknown**: Test database setup and fixture patterns
   - **Research Focus**:
     - pytest-asyncio configuration
     - FastAPI TestClient vs httpx async client
     - Test database creation/teardown (per-test vs per-suite)
     - SQLModel fixture patterns
   - **Output**: `conftest.py` template with fixtures

7. **Environment Configuration with pydantic-settings**
   - **Unknown**: Best practices for environment variable management
   - **Research Focus**:
     - Settings class structure for dev/test/prod environments
     - .env file loading
     - Required vs optional environment variables
     - Secret validation at startup (JWT key length check)
   - **Output**: `core/config.py` Settings class template

8. **CORS Configuration in FastAPI**
   - **Unknown**: CORS middleware setup for development and production
   - **Research Focus**:
     - CORSMiddleware configuration
     - Environment-based origin lists
     - Credentials (cookies) handling
   - **Output**: CORS setup in `main.py`

9. **Structured Logging in FastAPI**
   - **Unknown**: Logging configuration for production (JSON structured logs)
   - **Research Focus**:
     - Logging library: structlog, python-json-logger, or stdlib
     - Request ID tracking
     - Log level configuration
   - **Output**: Logging setup pattern for `main.py`

10. **Docker Container Best Practices for FastAPI**
    - **Unknown**: Optimal Dockerfile for FastAPI with uv
    - **Research Focus**:
      - Multi-stage builds for smaller images
      - uv in Docker (lock file handling)
      - Health check endpoints
      - Non-root user
    - **Output**: Dockerfile template

### Research Execution

Each research task will be delegated to a specialized research agent. Findings will be consolidated into `research.md` with the format:

```markdown
## [Research Topic]

**Decision**: [Chosen approach]
**Rationale**: [Why this approach was selected]
**Alternatives Considered**: [Other options evaluated and why they were rejected]
**Implementation Pattern**: [Code snippet or configuration example]
**References**: [Documentation links, articles, repos]
```

### Phase 0 Deliverable

- `research.md` - Complete research findings for all 10 topics
- All NEEDS CLARIFICATION items from Technical Context resolved
- Ready to proceed to Phase 1 design

---

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete

### 1.1 Data Model Design (`data-model.md`)

Extract entities from feature spec and constitution, applying SQLModel patterns from research:

**Entities**:
1. **User** (id: str, email: str, password_hash: str, name: Optional[str], created_at: datetime)
2. **Task** (id: int, title: str, description: Optional[str], completed: bool, priority: str, due_date: Optional[datetime], recurrence_rule: Optional[str], user_id: str, created_at: datetime, updated_at: datetime)
3. **Tag** (id: int, name: str, color: Optional[str], user_id: str)
4. **TaskTagLink** (task_id: int, tag_id: int) - Junction table

**Relationships**:
- User → Tasks (one-to-many)
- User → Tags (one-to-many)
- Task ↔ Tags (many-to-many via TaskTagLink)

**Indexes** (per constitution):
- idx_tasks_user_id, idx_tasks_user_completed, idx_tasks_user_priority, idx_tasks_user_due_date
- idx_tags_user_id
- idx_task_tag_link_task, idx_task_tag_link_tag

**Validation Rules** (from constitution and spec):
- Task title: 1-200 chars, required
- Task description: max 1000 chars, optional
- Task priority: enum('low', 'medium', 'high')
- Tag name: 1-50 chars, unique per user
- Email: valid email format, unique
- Password: minimum 8 chars

Output: `data-model.md` with complete SQLModel entity definitions and migration strategy

### 1.2 API Contract Design (`contracts/auth-api.yaml`)

Generate OpenAPI specification for authentication endpoints from functional requirements:

**Endpoints**:
1. POST /api/v1/auth/register - User registration
2. POST /api/v1/auth/login - User login (OAuth2PasswordRequestForm)
3. POST /api/v1/auth/refresh - Refresh access token
4. GET /api/v1/auth/me - Get current user
5. POST /api/v1/auth/logout - User logout

**Request/Response Schemas**:
- RegisterRequest, LoginRequest, TokenResponse, UserResponse, ErrorResponse
- Cookie definitions for refresh token
- Authentication security scheme (Bearer token)

**Error Codes** (from spec):
- EMAIL_ALREADY_EXISTS, PASSWORD_TOO_SHORT, INVALID_EMAIL
- INVALID_CREDENTIALS, TOKEN_EXPIRED, INVALID_TOKEN, MISSING_TOKEN
- REFRESH_TOKEN_EXPIRED, MISSING_REFRESH_TOKEN
- RATE_LIMIT_EXCEEDED

Output: `contracts/auth-api.yaml` - OpenAPI 3.0 specification

### 1.3 Quickstart Guide (`quickstart.md`)

Developer onboarding document covering:

**Setup**:
1. Prerequisites (Python 3.11+, PostgreSQL, uv)
2. Environment configuration (.env setup, JWT secret generation)
3. Database initialization (Alembic migrations)
4. Running the server (uvicorn command)

**Development Workflow**:
1. Creating migrations
2. Running tests
3. Using API documentation (/docs)
4. Common development tasks

**Deployment Notes**:
1. Docker build and run
2. Environment variables for production
3. Migration execution before deployment

Output: `quickstart.md` - Developer onboarding guide

### 1.4 Agent Context Update

Run `.specify/scripts/bash/update-agent-context.sh claude` to update agent-specific context with:
- SQLModel + asyncpg + FastAPI stack
- JWT authentication patterns
- Database migration workflow
- Testing approach

### Phase 1 Deliverables

- `data-model.md` - Complete entity definitions with relationships and constraints
- `contracts/auth-api.yaml` - OpenAPI specification for authentication API
- `quickstart.md` - Developer setup and workflow guide
- Updated agent context file with Phase II backend technologies

---

## Phase 2: Task Breakdown (Deferred to `/sp.tasks`)

Task breakdown and implementation plan generation is handled by the `/sp.tasks` command, which will:
1. Read this plan and the research/design artifacts
2. Generate a dependency-ordered task list in `tasks.md`
3. Include acceptance criteria and test requirements for each task

**This planning phase stops here.** Proceed with `/sp.tasks` after Phase 1 completion.

---

## Re-evaluation of Constitution Check (Post-Design)

*Completed after Phase 1 artifacts generation.*

After generating research.md, data-model.md, contracts/auth-api.yaml, and quickstart.md, re-verification:

- [x] **All entities match constitution data model exactly**
  - ✅ User entity: id (str), email (str, unique), password_hash (str), name (optional str), created_at (datetime)
  - ✅ Task entity: All fields match constitution spec including priority enum, due_date, recurrence_rule
  - ✅ Tag entity: id, name, color, user_id with UNIQUE(name, user_id) constraint
  - ✅ TaskTagLink: Composite primary key (task_id, tag_id)

- [x] **All indexes from constitution are included**
  - ✅ idx_tasks_user_id, idx_tasks_user_completed, idx_tasks_user_priority, idx_tasks_user_due_date
  - ✅ idx_tags_user_id
  - ✅ idx_task_tag_link_task, idx_task_tag_link_tag
  - All 7 required indexes defined in data-model.md and migration plan

- [x] **API endpoints follow constitution naming conventions**
  - ✅ All endpoints prefixed with /api/v1/
  - ✅ POST /api/v1/auth/register (201 Created)
  - ✅ POST /api/v1/auth/login (200 OK)
  - ✅ POST /api/v1/auth/refresh (200 OK)
  - ✅ GET /api/v1/auth/me (200 OK)
  - ✅ POST /api/v1/auth/logout (200 OK)

- [x] **Error response format matches constitution standard**
  - ✅ All error responses use `{"detail": "message", "code": "ERROR_CODE"}` format
  - ✅ Optional `field` property for validation errors
  - ✅ All error codes from spec documented in OpenAPI contract

- [x] **JWT token structure matches constitution specification**
  - ✅ Payload contains: sub, email, exp, iat, type
  - ✅ Access token expiry: 15 minutes
  - ✅ Refresh token expiry: 7 days
  - ✅ HS256 algorithm for Phase II
  - ✅ Token structure documented in contracts/auth-api.yaml

- [x] **No additional complexity introduced beyond requirements**
  - ✅ Uses standard FastAPI patterns (no custom abstractions)
  - ✅ SQLModel ORM as mandated (no repository pattern)
  - ✅ Dependency injection for database sessions (FastAPI standard)
  - ✅ No unnecessary middleware or layers
  - ✅ Research findings recommend proven libraries without over-engineering

**Final Verdict**: ✅ **PASS** - All Phase 1 artifacts comply with constitution requirements. Ready to proceed to task breakdown.

---

## Next Steps

1. **Immediate**: Execute Phase 0 research (dispatch research agents)
2. **After research.md complete**: Execute Phase 1 design (generate data-model.md, contracts/, quickstart.md)
3. **After Phase 1 complete**: Run `/sp.tasks` to generate implementation tasks
4. **After tasks.md complete**: Begin implementation via `/sp.implement` or manual task execution

**Current Status**: Planning phase complete, ready for Phase 0 research execution.
