# Implementation Plan: MCP Server Implementation for Phase III

**Branch**: `001-mcp-server-setup` | **Date**: 2025-12-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/sphaseIII/001-mcp-server-setup/spec.md`

**Note**: This plan establishes the foundational MCP server infrastructure for Phase III, implementing 5 stateless tools for task management with complete database-backed state and strict separation from Phase II.

## Summary

This feature implements the Model Context Protocol (MCP) server as the core infrastructure for Phase III's AI-powered todo chatbot. The MCP server exposes 5 stateless tools (add_task, list_tasks, complete_task, delete_task, update_task) that enable OpenAI agents to manage tasks through standardized interfaces. All tools enforce user authentication via Better Auth JWT tokens, maintain complete data isolation per user, and persist all state to PostgreSQL using SQLModel with async operations. The implementation uses the official MCP Python SDK, operates with zero in-memory state for horizontal scalability, and maintains complete separation from Phase II codebase through dedicated tables (tasks_phaseiii, conversations, messages) and independent Alembic migration history.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Official MCP Python SDK, FastAPI, SQLModel, Alembic, asyncpg, pydantic-settings, Better Auth JWT validation
**Storage**: Neon Serverless PostgreSQL (shared instance with Phase II, separate tables)
**Testing**: pytest with pytest-asyncio, pytest-cov for coverage reporting
**Target Platform**: Linux server (containerized with Docker)
**Project Type**: Backend service (Phase III backend only - frontend is separate feature)
**Performance Goals**: p95 < 200ms for tool invocations (database operations only), p95 < 5s including OpenAI API latency
**Constraints**: Stateless architecture (horizontally scalable), ≥80% test coverage, zero Phase II imports, JWT-based user isolation
**Scale/Scope**: Multi-user system, ~5 core entities (Task, Conversation, Message, User from Better Auth, MCP Tool abstraction), 5 MCP tools, foundational feature blocking all Phase III development

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase III Constitutional Requirements

✅ **Principle I - Spec-Driven Development**: This implementation plan derives from approved spec.md
✅ **Principle II - Phase Separation**: Zero imports from phaseII/; uses tasks_phaseiii table (not tasks table)
✅ **Principle III - Database Persistence**: SQLModel + asyncpg + Alembic migrations (independent from Phase II)
✅ **Principle IV - JWT Security**: Better Auth JWT validation; user_id from token is authoritative
✅ **Principle V - Backend Architecture**: FastAPI routers; standard error format {detail, code, field}
✅ **Principle XI - MCP Server Architecture**: Official MCP SDK; 5 stateless tools; database-backed state
✅ **Principle XIII - Conversational AI Standards**: Stateless server design; conversation/message persistence

### Technology Constraints Compliance

✅ **Backend Language**: Python with FastAPI
✅ **MCP Server**: Official MCP SDK (https://github.com/modelcontextprotocol/python-sdk)
✅ **ORM**: SQLModel with async operations
✅ **Database**: Neon PostgreSQL (separate tables: tasks_phaseiii, conversations, messages)
✅ **Package Manager**: UV (uv add <package>)
✅ **Authentication**: Better Auth JWT validation

### Data Model Compliance

✅ **Task Entity**: tasks_phaseiii table (id, user_id, title, description, completed, created_at, updated_at)
✅ **Conversation Entity**: conversations table (id, user_id, created_at, updated_at)
✅ **Message Entity**: messages table (id, conversation_id, user_id, role, content, created_at)
✅ **Indexes**: user_id on tasks_phaseiii/conversations, conversation_id on messages

### API Design Compliance

✅ **MCP Tools**: 5 tools with signatures matching Constitution Principle XI
✅ **Error Format**: {detail: string, code: string, field?: string}
✅ **User Isolation**: All queries scoped to JWT user_id (not path parameter)

### Gate Status: **PASS** ✅

All constitutional requirements are satisfied. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/sphaseIII/001-mcp-server-setup/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress - /sp.plan output)
├── research.md          # Phase 0 research findings (to be generated)
├── data-model.md        # Phase 1 entity models (to be generated)
├── quickstart.md        # Phase 1 developer guide (to be generated)
├── contracts/           # Phase 1 MCP tool schemas (to be generated)
│   ├── add_task.json
│   ├── list_tasks.json
│   ├── complete_task.json
│   ├── delete_task.json
│   └── update_task.json
└── tasks.md             # Phase 2 task breakdown (/sp.tasks - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
phaseIII/
├── backend/                           # Python FastAPI backend
│   ├── pyproject.toml                # UV package manager config
│   ├── .env.example                  # Environment template
│   ├── alembic.ini                   # Alembic configuration
│   ├── alembic/                      # Database migrations (Phase III only)
│   │   ├── env.py                    # Migration environment
│   │   ├── script.py.mako           # Migration template
│   │   └── versions/                 # Migration files
│   │       └── 20251217_initial_phase_iii_schema.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry + MCP server init
│   │   ├── config.py                 # Settings (pydantic-settings)
│   │   ├── database.py               # Async database session management
│   │   ├── models/                   # SQLModel entities
│   │   │   ├── __init__.py
│   │   │   ├── task.py               # TaskPhaseIII model (tasks_phaseiii table)
│   │   │   ├── conversation.py       # Conversation model
│   │   │   └── message.py            # Message model
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── task.py               # Task schemas
│   │   │   └── mcp.py                # MCP tool schemas
│   │   ├── mcp/                      # MCP Server implementation
│   │   │   ├── __init__.py
│   │   │   ├── server.py             # MCP server manager + tool registration
│   │   │   ├── tools/                # Individual tool implementations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── add_task.py
│   │   │   │   ├── list_tasks.py
│   │   │   │   ├── complete_task.py
│   │   │   │   ├── delete_task.py
│   │   │   │   └── update_task.py
│   │   │   └── validators.py         # Shared parameter validation
│   │   ├── services/                 # Business logic layer
│   │   │   ├── __init__.py
│   │   │   └── task_service.py       # Task CRUD operations
│   │   └── auth/                     # Authentication utilities
│   │       ├── __init__.py
│   │       └── jwt.py                # Better Auth JWT validation
│   └── tests/                        # Pytest test suite
│       ├── conftest.py               # Test fixtures + async DB setup
│       ├── test_models.py            # Model validation tests
│       ├── test_mcp_tools/           # MCP tool tests
│       │   ├── test_add_task.py
│       │   ├── test_list_tasks.py
│       │   ├── test_complete_task.py
│       │   ├── test_delete_task.py
│       │   └── test_update_task.py
│       ├── test_task_service.py      # Service layer tests
│       └── test_integration.py       # Multi-user isolation tests
└── README.md                          # Phase III setup instructions
```

**Structure Decision**: Backend-only structure for Phase III MCP server implementation. Frontend (OpenAI ChatKit) is a separate feature. This structure follows Constitution Principle II (Phase Separation) with phaseIII/ as the root directory, completely independent from phaseII/. The MCP server is organized as a FastAPI application with dedicated mcp/ module for tool implementations, following single-responsibility principle with one file per tool.

## Complexity Tracking

> **No constitutional violations - this section intentionally left empty.**

All design decisions align with constitutional requirements. No complexity justifications needed.

---

## Phase 0: Research & Technology Decisions ✅

**Status**: COMPLETE

**Research Completed**:
1. ✅ MCP Python SDK integration patterns for stateless tool server
2. ✅ SQLModel + asyncpg best practices for Phase III (separate from Phase II)
3. ✅ Better Auth JWT validation with FastAPI dependencies
4. ✅ Alembic migration strategy independent of Phase II
5. ✅ Multi-user data isolation patterns with user_id scoping

**Research Agents Dispatched**: 3 comprehensive research documents generated

**Key Findings**:
- **MCP SDK**: Use official Python SDK with stateless tool registration
- **Database**: Async SQLModel + asyncpg with connection pooling (5-10 connections)
- **Authentication**: FastAPI dependency injection with python-jose JWT validation
- **Migrations**: Independent Alembic setup for Phase III (separate from Phase II)
- **Security**: Three-layer isolation (JWT extraction → path validation → query scoping)

---

## Phase 1: Data Model & Contracts ✅

**Status**: COMPLETE

**Deliverables Generated**:
1. ✅ **data-model.md**: Complete entity models for TaskPhaseIII, Conversation, Message with:
   - Field types, constraints, and validation rules
   - SQLModel class definitions
   - Indexes for performance (user_id, conversation_id, created_at)
   - Alembic migration script
   - Query patterns and security isolation examples

2. ✅ **contracts/**: JSON schemas for all 5 MCP tools:
   - ✅ `add_task.json` - Create task with title/description validation
   - ✅ `list_tasks.json` - Retrieve tasks with status filter
   - ✅ `complete_task.json` - Mark task complete (idempotent)
   - ✅ `delete_task.json` - Remove task (non-idempotent)
   - ✅ `update_task.json` - Modify task title/description

3. ✅ **quickstart.md**: Complete developer guide with:
   - Prerequisites and environment setup
   - Installation and database initialization
   - Running server in dev/production modes
   - Testing strategy and commands
   - Common issues and solutions
   - API documentation links

---

## Next Steps

1. ✅ **Constitution Check**: PASSED - all requirements satisfied
2. ✅ **Phase 0 Research**: COMPLETE - all research objectives met
3. ✅ **Phase 1 Design**: COMPLETE - data model, contracts, and quickstart ready
4. ⏭️  **Phase 2 Tasks**: Run `/sp.tasks` to generate implementation task breakdown
5. ⏭️  **Implementation**: Run `/sp.implement` after tasks ready

---

## Planning Artifacts Summary

| Artifact | Status | Location |
|----------|--------|----------|
| Specification | ✅ Complete | `specs/sphaseIII/001-mcp-server-setup/spec.md` |
| Implementation Plan | ✅ Complete | `specs/sphaseIII/001-mcp-server-setup/plan.md` (this file) |
| Research Findings | ✅ Complete | Research agents generated comprehensive documentation |
| Data Model | ✅ Complete | `specs/sphaseIII/001-mcp-server-setup/data-model.md` |
| Tool Contracts | ✅ Complete | `specs/sphaseIII/001-mcp-server-setup/contracts/*.json` (5 files) |
| Quickstart Guide | ✅ Complete | `specs/sphaseIII/001-mcp-server-setup/quickstart.md` |
| Task Breakdown | ⏳ Pending | Run `/sp.tasks` to generate `tasks.md` |

---

**Planning Status**: ✅ COMPLETE

All planning artifacts generated successfully. Phase 0 research and Phase 1 design complete with:
- 3 comprehensive research documents covering MCP SDK, SQLModel async patterns, and Better Auth JWT validation
- Complete data model with SQLModel definitions and Alembic migration
- 5 JSON schema contracts for all MCP tools
- Developer quickstart guide with setup, testing, and debugging instructions

**Ready for**: Task breakdown generation via `/sp.tasks` command.
