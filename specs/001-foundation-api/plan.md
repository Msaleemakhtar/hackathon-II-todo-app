# Implementation Plan: Advanced Task Management Foundation

**Branch**: `001-foundation-api` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-foundation-api/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature implements the foundational backend infrastructure for Phase V advanced task management capabilities, including database schema evolution with 7 new task fields (priority, due_date, category_id, recurrence_rule, reminder_sent, search_vector, search_rank), 3 new tables (categories, tags_phasev, task_tags junction), and enhanced MCP tools suite (17 total: 5 enhanced + 12 new) to support task prioritization, categorization, tagging, due date management, recurring tasks, and full-text search with PostgreSQL tsvector + GIN indexes. This lays the groundwork for Phase V event-driven architecture (Kafka) and distributed runtime (Dapr) capabilities.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.109+, SQLModel 0.0.14+, Alembic 1.13+, asyncpg 0.29+, openai-agents 0.6.3+, openai-chatkit, mcp[cli] 1.24+
**Storage**: Neon Serverless PostgreSQL (shared database instance with Phase II/III/IV, separate tables_phaseiii table + new Phase V tables)
**Testing**: pytest 7.4+ with pytest-asyncio 0.21+, pytest-cov 4.1+, testcontainers (optional for isolated DB tests)
**Target Platform**: Linux server (containerized with Docker, orchestrated via Kubernetes/Minikube, later Oracle Cloud OKE)
**Project Type**: Web backend API (Phase V extends Phase IV which extends Phase III)
**Performance Goals**: Full-text search <200ms p95 for 10k tasks, Task list queries <200ms p95, Support 10k tasks per user without degradation
**Constraints**: Database queries must use JWT user_id (not path parameter) for data isolation, All schema changes via Alembic migrations (reversible), Search uses PostgreSQL tsvector + GIN indexes (not external search engine)
**Scale/Scope**: 17 MCP tools (5 enhanced: add_task, update_task, list_tasks, delete_task, get_task + 12 new: create_category, list_categories, update_category, delete_category, create_tag, list_tags, update_tag, delete_tag, add_tag_to_task, remove_tag_from_task, search_tasks, set_reminder), 3 new database tables, 7 enhanced task fields, full-text search indexing, iCal RRULE parsing

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅ PASS
- **Status**: This plan.md is being generated from spec.md via `/sp.plan` command
- **Verification**: Spec exists at `specs/001-foundation-api/spec.md` before implementation begins
- **AI Generation**: All code (models, MCP tools, services, migrations) will be AI-generated from specifications

### Principle II: Repository Structure ✅ PASS
- **Phase Separation**: Feature implements Phase V (`/phaseV/`) with no imports from Phase II/III/IV
- **Directory Structure**: Uses Phase V structure (`phaseV/backend/app/`, `phaseV/backend/alembic/`)
- **Specs Organization**: Located in `/specs/001-foundation-api/` (not under sphaseV/ as this is a cross-phase spec directory based on git status)

### Principle III: Persistent & Relational State ✅ PASS
- **Database**: Neon Serverless PostgreSQL (shared instance, separate tables)
- **ORM**: SQLModel for all data access
- **Async**: All operations use asyncpg driver
- **Migrations**: Alembic migration required for schema evolution (7 new fields + 3 new tables)
- **Data Isolation**: All queries scoped to JWT user_id
- **Phase Table Separation**: Uses `tasks_phaseiii` table (existing), adds `categories`, `tags_phasev`, `task_tags` (new)
- **Full-Text Search**: PostgreSQL tsvector with GIN indexes (Phase V requirement)

### Principle IV: User Authentication & JWT Security ✅ PASS
- **Authentication**: Better Auth JWT (existing in Phase III/IV)
- **JWT Validation**: Backend validates tokens using shared secret
- **Path Parameter Matching**: All endpoints validate JWT user_id matches path user_id
- **Data Scoping**: Database queries use JWT user_id, not path parameter

### Principle V: Backend Architecture Standards ✅ PASS
- **Router Organization**: Endpoints in `/backend/app/routers/` (if needed; may use existing chat.py)
- **API Versioning**: Follows `/api/{user_id}/` pattern (existing)
- **Configuration**: pydantic-settings with .env files
- **Documentation**: FastAPI OpenAPI at /docs
- **Error Handling**: Consistent JSON error responses
- **Pre-commit Hooks**: ruff check + ruff format

### Principle VII: Automated Testing Standards ✅ PASS
- **Framework**: pytest with pytest-asyncio
- **Test Categories**: Unit tests (MCP tools, services), Integration tests (database operations)
- **Coverage**: Target ≥80% for backend core logic
- **Phase V Specific**: All 17 MCP tools MUST have unit tests

### Principle X: Feature Scope Evolution ✅ PASS
- **Phase V Features**: Implements advanced features (priorities, categories, tags, due dates, search, recurring tasks)
- **MCP Tools**: 17 total tools as specified (5 enhanced + 12 new)
- **Scope Alignment**: Matches Phase V Part A requirements (advanced task management foundation)

### Principle XIV: Containerization & Orchestration (Phase IV/V) ✅ PASS
- **Container Runtime**: Docker Desktop (existing Phase V setup)
- **Kubernetes**: Deployable to Minikube (Phase IV/V namespace: `todo-phasev`)
- **Service Communication**: ClusterIP and internal DNS

### Principle XVI: Event-Driven Architecture with Kafka (Phase V Only) ⚠️ DEFERRED
- **Status**: NOT IMPLEMENTED IN THIS FEATURE (001-foundation-api)
- **Rationale**: This feature (001) establishes the data model and MCP tools foundation. Event publishing (Kafka producers) will be added in a separate feature (002-event-streaming or similar) after the foundation is stable.
- **Future Work**: After 001 completes, Kafka producers will be added to MCP tools to publish task-events, reminders, task-updates

### Principle XVII: Distributed Application Runtime with Dapr (Phase V Only) ⚠️ DEFERRED
- **Status**: NOT IMPLEMENTED IN THIS FEATURE (001-foundation-api)
- **Rationale**: Dapr integration (Pub/Sub, State Store, Jobs API) will be added in a separate feature (002-dapr-integration or similar)
- **Future Work**: After Kafka integration (002) is complete, Dapr components will abstract infrastructure

### Principle XVIII: Production Cloud Deployment (Phase V Only) ⚠️ DEFERRED
- **Status**: NOT IMPLEMENTED IN THIS FEATURE (001-foundation-api)
- **Rationale**: Oracle Cloud OKE deployment, cert-manager, CI/CD pipelines will be added in a separate feature (003-cloud-deployment or similar)
- **Future Work**: Cloud deployment follows after local Kubernetes validation

### Summary: ✅ PASS WITH DEFERRED ITEMS
All applicable constitutional principles are satisfied for Feature 001. Principles XVI, XVII, XVIII are Phase V-specific and explicitly deferred to subsequent features as this is the foundation API layer. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-foundation-api/
├── spec.md              # Feature specification (input)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command - API contracts)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

This feature enhances the existing Phase V backend structure. No new top-level directories created.

```text
phaseV/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── task.py                 # ENHANCED: Add 7 new fields (priority, due_date, etc.)
│   │   │   ├── category.py             # NEW: Category model
│   │   │   ├── tag.py                  # NEW: Tag model (tags_phasev table)
│   │   │   └── task_tag.py             # NEW: Task-Tag junction table
│   │   ├── mcp/
│   │   │   ├── tools.py                # ENHANCED: 17 MCP tools (5 enhanced + 12 new)
│   │   │   └── server.py               # UNCHANGED: MCP server manager
│   │   ├── services/
│   │   │   ├── task_service.py         # ENHANCED: Support new fields, validations
│   │   │   ├── category_service.py     # NEW: Category CRUD operations
│   │   │   ├── tag_service.py          # NEW: Tag CRUD operations
│   │   │   └── search_service.py       # NEW: Full-text search with tsvector
│   │   ├── schemas/
│   │   │   ├── task.py                 # ENHANCED: New field schemas (priority, due_date, etc.)
│   │   │   ├── category.py             # NEW: Category request/response schemas
│   │   │   └── tag.py                  # NEW: Tag request/response schemas
│   │   ├── utils/
│   │   │   └── rrule_parser.py         # NEW: iCal RRULE validation & parsing
│   │   ├── config.py                   # UNCHANGED: Configuration management
│   │   ├── database.py                 # UNCHANGED: Database connection
│   │   └── main.py                     # UNCHANGED: FastAPI application entry
│   ├── alembic/
│   │   └── versions/
│   │       └── YYYYMMDD_add_advanced_task_fields.py  # NEW: Migration script
│   └── tests/
│       ├── test_mcp_tools.py           # ENHANCED: Tests for 17 MCP tools
│       ├── test_task_service.py        # ENHANCED: Tests for enhanced task operations
│       ├── test_category_service.py    # NEW: Category service tests
│       ├── test_tag_service.py         # NEW: Tag service tests
│       └── test_search_service.py      # NEW: Full-text search tests
└── frontend/
    └── (No changes in this feature - frontend enhancements deferred)
```

**Structure Decision**: Web application (Phase V backend). This feature enhances the existing Phase V backend (`phaseV/backend/`) with new database models, enhanced MCP tools, new service layers, and comprehensive testing. Frontend changes (ChatKit prompt enhancements) are deferred to a separate feature.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations. All complexity is justified by requirements:
- 3 new tables required for categories, tags, and many-to-many relationships
- 7 new task fields required for advanced features (priority, due_date, category assignment, recurrence, reminders, search indexing)
- 17 MCP tools required for comprehensive task management API
- Full-text search via PostgreSQL native capabilities (simpler than external search engine)
