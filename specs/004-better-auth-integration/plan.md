# Implementation Plan: Better Auth Integration

**Branch**: `004-better-auth-integration` | **Date**: 2025-12-10 | **Spec**: [Better Auth Integration Specification](spec.md)
**Input**: Feature specification from `/specs/004-better-auth-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature implements Better Auth integration to replace the current custom authentication system with a standardized authentication solution that provides JWT-based security between the Next.js frontend and FastAPI backend. The implementation includes updating API endpoints to follow the `{user_id}/resources` pattern, implementing proper user data isolation and security validation, and creating proper token validation and refresh mechanisms.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/JavaScript (frontend), Next.js 16
**Primary Dependencies**: FastAPI (backend), Better Auth (frontend), SQLModel, PostgreSQL, axios
**Storage**: PostgreSQL (Neon Serverless) via SQLModel ORM
**Testing**: pytest (backend), vitest/jest (frontend), testcontainers for database isolation
**Target Platform**: Web application (Next.js frontend, FastAPI backend)
**Project Type**: Full-stack monorepo web application
**Performance Goals**: <200ms API response time (p95), JWT validation <10ms, login flow <2 seconds
**Constraints**: Must follow monorepo architecture, use shared secret for JWT validation, scope all queries to JWT user_id
**Scale/Scope**: Multi-user system supporting user data isolation, rate limiting at 5 attempts per minute per IP

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0 Compliance Check
**Status: PASS** - All requirements aligned with constitution

**Frontend Architecture Compliance**:
- ✅ Next.js 16 with App Router (VI)
- ✅ TypeScript with strict mode (II)
- ✅ shadcn/ui component library (II)
- ✅ Tailwind CSS for styling (II)
- ✅ Zustand for global state management (II)
- ✅ axios for HTTP client with interceptors (II)
- ✅ Better Auth library for authentication (VI, IV)
- ✅ API client at `@/lib/api-client` exists (VI)

**Backend Architecture Compliance**:
- ✅ Python 3.11+ with FastAPI framework (II)
- ✅ SQLModel for ORM and data validation (II, III)
- ✅ Pydantic for input/output schemas (II)
- ✅ asyncpg driver for async PostgreSQL access (III)
- ✅ Alembic for database migrations (III)
- ✅ JWT validation using Better Auth shared secret (IV)

**Security Compliance**:
- ✅ JWT tokens validated using shared secret (IV)
- ✅ Path parameter matching with JWT user_id (IV)
- ✅ All queries scoped to JWT user_id, not path parameter (III)
- ✅ Rate limiting on auth endpoints (IV)
- ✅ API endpoints follow `/api/{user_id}/{resources}` pattern (API Design Standards)

**Architecture Compliance**:
- ✅ Monorepo structure with frontend/backend separation (II)
- ✅ bun for frontend dependencies (II)
- ✅ uv for backend Python dependencies (II)
- ✅ Data isolation testing requirements (III)

### Post-Phase 1 Design Compliance Check
**Status: PASS** - Design continues to comply with constitution

**Data Model Compliance**:
- ✅ User, Task, and Tag entities use SQLModel (III)
- ✅ User.id uses UUID from Better Auth (IV)
- ✅ Foreign key relationships properly defined (III)
- ✅ Data isolation enforced at model level (III)

**API Contract Compliance**:
- ✅ OpenAPI specification created for all endpoints (V)
- ✅ All user-specific endpoints use `/api/{user_id}/{resources}` pattern (API Design Standards)
- ✅ Authentication endpoints remain at `/api/v1/auth/*` (API Design Standards)
- ✅ Path parameter validation requirements documented (API Design Standards)

**Security Design Compliance**:
- ✅ JWT token structure documented (IV)
- ✅ Token validation flow specified (IV)
- ✅ Data scoping to JWT user_id documented (IV, III)
- ✅ Rate limiting specified for auth endpoints (IV)

### Violations Check
**Status: No violations identified**

All implementation requirements continue to comply with the constitution. The design phase has validated that Better Auth integration is fully compatible with constitutional requirements.

## Project Structure

### Documentation (this feature)

```text
specs/004-better-auth-integration/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
/
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/    # Reusable UI components
│   │   ├── lib/           # Utilities, API client, stores
│   │   └── types/         # TypeScript type definitions
│   ├── public/
│   └── package.json
├── backend/
│   ├── src/
│   │   ├── routers/       # APIRouter modules
│   │   ├── models/        # SQLModel entities
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── core/          # Config, dependencies, security
│   ├── tests/
│   ├── alembic/
│   └── pyproject.toml
├── packages/
│   └── auth-sdk/      # Shared TypeScript definitions, SDKs, etc.
├── specs/
│   └── 004-better-auth-integration/
└── docker-compose.yml
```

**Structure Decision**: This feature follows the established monorepo architecture with separate frontend and backend services. The implementation will add Better Auth integration to the existing Next.js frontend and FastAPI backend, creating an API client at `@/lib/api-client` as required by the constitution.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations identified - all implementation requirements align with the constitution.*
