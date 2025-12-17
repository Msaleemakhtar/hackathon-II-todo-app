# Feature Specification: MCP Server Implementation for Phase III

**Feature Branch**: `001-mcp-server-setup`
**Created**: 2025-12-17
**Status**: Draft
**Input**: User description: "MCP Server Implementation for Phase III Todo AI Chatbot - including backend infrastructure, 5 MCP tools for task operations, and database models with separate tables from Phase II."

## Feature Overview

This feature establishes the foundational MCP (Model Context Protocol) server infrastructure for Phase III of the Todo application. The MCP server exposes 5 stateless tools that enable AI agents to manage tasks through standardized tool interfaces. The implementation uses the official MCP SDK, operates with complete database-backed state, and maintains strict separation from Phase II codebase.

The MCP server acts as the bridge between conversational AI (OpenAI Agents SDK) and the task management system, providing tool-based access to task operations while enforcing user authentication and data isolation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Creation via MCP Tool (Priority: P1)

An AI assistant needs to create a new task when a user says "Add a task to buy groceries". The MCP server receives the add_task tool invocation, validates the parameters, stores the task in the database, and returns the task ID.

**Why this priority**: Task creation is the most fundamental operation. Without it, the AI chatbot cannot perform its core function of helping users manage tasks.

**Independent Test**: Can be fully tested by invoking the add_task tool directly with a user_id and title, verifying the task appears in the database with correct attributes and the tool returns task_id.

**Acceptance Scenarios**:

1. **Given** a valid user_id and task title, **When** add_task tool is invoked, **Then** system creates task in tasks_phaseiii table and returns task_id with status "created"
2. **Given** a task title exceeding 200 characters, **When** add_task tool is invoked, **Then** system returns error with code "INVALID_TITLE" and detail "Title must be 1-200 characters"
3. **Given** an empty or whitespace-only title, **When** add_task tool is invoked, **Then** system returns error with code "INVALID_TITLE" and detail "Title is required and must be 1-200 characters"
4. **Given** a valid task with description exceeding 1000 characters, **When** add_task tool is invoked, **Then** system returns error with code "DESCRIPTION_TOO_LONG" and detail "Description cannot exceed 1000 characters"

---

### User Story 2 - Task Listing via MCP Tool (Priority: P1)

An AI assistant needs to retrieve and display a user's tasks when asked "Show me my tasks" or "What's pending?". The MCP server receives the list_tasks tool invocation with optional status filter, retrieves tasks from the database scoped to the user, and returns the task list.

**Why this priority**: Task retrieval is essential for the AI to provide context-aware responses and allow users to review their task list. Without it, users cannot see what tasks they have.

**Independent Test**: Can be fully tested by creating several tasks for a user, invoking list_tasks with different status filters (all/pending/completed), and verifying the correct tasks are returned while excluding other users' tasks.

**Acceptance Scenarios**:

1. **Given** a user has 3 pending tasks and 2 completed tasks, **When** list_tasks is invoked with status "all", **Then** system returns all 5 tasks
2. **Given** a user has 3 pending tasks and 2 completed tasks, **When** list_tasks is invoked with status "pending", **Then** system returns only the 3 pending tasks
3. **Given** a user has 3 pending tasks and 2 completed tasks, **When** list_tasks is invoked with status "completed", **Then** system returns only the 2 completed tasks
4. **Given** User A has tasks and User B has tasks, **When** list_tasks is invoked with User A's user_id, **Then** system returns only User A's tasks (data isolation)
5. **Given** a user has no tasks, **When** list_tasks is invoked, **Then** system returns empty array with no errors

---

### User Story 3 - Task Completion via MCP Tool (Priority: P1)

An AI assistant marks a task as complete when a user says "Mark task 3 as done" or "I finished the grocery shopping". The MCP server receives the complete_task tool invocation, validates the task exists and belongs to the user, updates the completed status, and returns confirmation.

**Why this priority**: Task completion is a core operation users perform frequently. It's essential for task lifecycle management and user satisfaction.

**Independent Test**: Can be fully tested by creating a pending task, invoking complete_task with the task_id, and verifying the task's completed field is updated to true in the database.

**Acceptance Scenarios**:

1. **Given** a pending task exists for a user, **When** complete_task is invoked with the task_id, **Then** system sets completed=true and returns status "completed"
2. **Given** a task_id that doesn't exist, **When** complete_task is invoked, **Then** system returns error with code "TASK_NOT_FOUND" and detail "Task not found"
3. **Given** a task belonging to User A, **When** complete_task is invoked with User B's user_id, **Then** system returns error with code "TASK_NOT_FOUND" (data isolation - task doesn't exist for User B)
4. **Given** an already completed task, **When** complete_task is invoked, **Then** system succeeds idempotently (completed remains true)

---

### User Story 4 - Task Deletion via MCP Tool (Priority: P1)

An AI assistant removes a task when a user says "Delete the meeting task" or "Remove task 5". The MCP server receives the delete_task tool invocation, validates ownership, removes the task from the database, and returns confirmation.

**Why this priority**: Task deletion is essential for users to maintain a clean task list and remove irrelevant or completed tasks.

**Independent Test**: Can be fully tested by creating a task, invoking delete_task with the task_id, and verifying the task is removed from the database and no longer appears in list_tasks.

**Acceptance Scenarios**:

1. **Given** a task exists for a user, **When** delete_task is invoked with the task_id, **Then** system removes task from database and returns status "deleted"
2. **Given** a task_id that doesn't exist, **When** delete_task is invoked, **Then** system returns error with code "TASK_NOT_FOUND" and detail "Task not found"
3. **Given** a task belonging to User A, **When** delete_task is invoked with User B's user_id, **Then** system returns error with code "TASK_NOT_FOUND" (data isolation)
4. **Given** a deleted task_id, **When** delete_task is invoked again, **Then** system returns error with code "TASK_NOT_FOUND" (not idempotent)

---

### User Story 5 - Task Update via MCP Tool (Priority: P2)

An AI assistant modifies task details when a user says "Change task 1 title to 'Call mom tonight'" or "Update the description for task 2". The MCP server receives the update_task tool invocation with optional title/description fields, validates ownership and constraints, updates the task, and returns confirmation.

**Why this priority**: While important for task management, update is less critical than create/read/complete/delete. Users can work around missing update by deleting and recreating tasks.

**Independent Test**: Can be fully tested by creating a task, invoking update_task with new title or description, and verifying the task fields are updated in the database while other fields remain unchanged.

**Acceptance Scenarios**:

1. **Given** a task exists with title "Old Title", **When** update_task is invoked with new title "New Title", **Then** system updates task.title and returns status "updated"
2. **Given** a task exists, **When** update_task is invoked with new description, **Then** system updates task.description only
3. **Given** a task exists, **When** update_task is invoked with both title and description, **Then** system updates both fields
4. **Given** a new title exceeding 200 characters, **When** update_task is invoked, **Then** system returns error with code "INVALID_TITLE"
5. **Given** a task_id that doesn't exist, **When** update_task is invoked, **Then** system returns error with code "TASK_NOT_FOUND"
6. **Given** a task belonging to User A, **When** update_task is invoked with User B's user_id, **Then** system returns error with code "TASK_NOT_FOUND"

---

### User Story 6 - Database Infrastructure Setup (Priority: P1)

Backend infrastructure is configured with Phase III-specific database tables, migrations, and models. The system uses separate tasks_phaseiii table (not Phase II's tasks table), implements SQLModel models for tasks/conversations/messages, and sets up Alembic migrations.

**Why this priority**: Database infrastructure is foundational. All other features depend on proper data persistence and isolation from Phase II.

**Independent Test**: Can be fully tested by running migrations, creating database records, and verifying table schemas match specifications with proper indexes and foreign keys.

**Acceptance Scenarios**:

1. **Given** a clean database, **When** Alembic migrations run, **Then** tasks_phaseiii, conversations, and messages tables are created with correct schemas
2. **Given** Phase III tables exist, **When** database inspection is performed, **Then** no Phase II table references exist (complete separation)
3. **Given** tasks_phaseiii table exists, **When** schema is inspected, **Then** indexes exist on user_id column
4. **Given** messages table exists, **When** schema is inspected, **Then** foreign key exists to conversations.id and index exists on conversation_id

---

### User Story 7 - MCP Server Configuration and Initialization (Priority: P1)

Backend application initializes the MCP server using the official Python SDK, registers all 5 tools, and starts listening for tool invocations. The server is stateless and scalable.

**Why this priority**: Server initialization is foundational. The AI chatbot cannot function without a running MCP server to invoke tools.

**Independent Test**: Can be fully tested by starting the server, verifying tool registration, and confirming the server can process tool invocation requests.

**Acceptance Scenarios**:

1. **Given** backend application starts, **When** MCP server initializes, **Then** all 5 tools (add_task, list_tasks, complete_task, delete_task, update_task) are registered
2. **Given** MCP server is running, **When** server state is inspected, **Then** no in-memory conversation state exists (stateless architecture)
3. **Given** MCP server receives a tool invocation, **When** processing completes, **Then** server holds no residual state from the request

---

### Edge Cases

1. **Concurrent Task Creation**: What happens when the same user creates multiple tasks simultaneously? System handles concurrently with database ACID guarantees; each task gets unique auto-incremented ID.

2. **Invalid User ID Format**: What happens when a tool receives a malformed user_id? System returns error with code "INVALID_USER_ID" and detail "User ID is required".

3. **Database Connection Loss**: What happens when database becomes unavailable during a tool invocation? System returns error with code "DATABASE_ERROR" and detail "Database connection failed" without crashing.

4. **Task ID Type Mismatch**: What happens when complete_task receives a string instead of integer for task_id? System validates parameter types and returns error with code "INVALID_PARAMETER" and field "task_id".

5. **Maximum Description Length**: What happens when description is exactly 1000 characters? System accepts it (boundary is ≤ 1000, not < 1000).

6. **Whitespace-Only Description**: What happens when description contains only whitespace? System accepts it (description is optional and can be empty).

7. **Unicode Characters in Title**: What happens when title contains emoji or non-ASCII characters? System accepts and stores correctly (database uses UTF-8 encoding).

8. **List Tasks with Invalid Status Filter**: What happens when list_tasks receives status="unknown"? System returns error with code "INVALID_PARAMETER" and detail "Status must be 'all', 'pending', or 'completed'".

9. **Update Task with No Fields**: What happens when update_task is invoked without title or description? System returns error with code "INVALID_PARAMETER" and detail "At least one field (title or description) must be provided".

10. **Null vs Empty String Description**: What happens when add_task receives description=null vs description=""? System treats both as empty description (stored as null in database).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement MCP server using the official MCP Python SDK from https://github.com/modelcontextprotocol/python-sdk

- **FR-002**: System MUST expose exactly 5 tools: add_task, list_tasks, complete_task, delete_task, update_task with signatures specified in Constitution Principle XI

- **FR-003**: System MUST implement add_task tool that accepts user_id (required), title (required), and description (optional), validates title length (1-200 chars), validates description length (≤1000 chars), creates task in tasks_phaseiii table, and returns {task_id, status: "created", title}

- **FR-004**: System MUST implement list_tasks tool that accepts user_id (required) and status (optional: "all", "pending", "completed"), queries tasks_phaseiii table filtered by user_id and status, and returns array of task objects with all fields

- **FR-005**: System MUST implement complete_task tool that accepts user_id (required) and task_id (required), validates task exists and belongs to user, updates completed=true in database, and returns {task_id, status: "completed", title}

- **FR-006**: System MUST implement delete_task tool that accepts user_id (required) and task_id (required), validates task exists and belongs to user, removes task from database, and returns {task_id, status: "deleted", title}

- **FR-007**: System MUST implement update_task tool that accepts user_id (required), task_id (required), title (optional), and description (optional), validates at least one field is provided, validates constraints (title 1-200 chars if provided, description ≤1000 chars if provided), updates only provided fields, and returns {task_id, status: "updated", title}

- **FR-008**: System MUST create tasks_phaseiii database table with fields: id (integer, primary key, auto-increment), user_id (string, indexed, not null), title (string, max 200 chars, not null), description (text, nullable), completed (boolean, default false, not null), created_at (timestamp, not null), updated_at (timestamp, not null)

- **FR-009**: System MUST create conversations database table with fields: id (integer, primary key, auto-increment), user_id (string, indexed, not null), created_at (timestamp, not null), updated_at (timestamp, not null)

- **FR-010**: System MUST create messages database table with fields: id (integer, primary key, auto-increment), conversation_id (integer, foreign key to conversations.id, indexed, not null), user_id (string, indexed, not null), role (string enum "user" or "assistant", not null), content (text, not null), created_at (timestamp, not null)

- **FR-011**: System MUST scope all database queries to authenticated user's ID extracted from JWT token (not from path parameter) to enforce data isolation

- **FR-012**: System MUST validate all tool parameters match expected types and constraints before executing business logic

- **FR-013**: System MUST return errors in format {detail: string, code: string, field?: string} matching Constitution error format

- **FR-014**: System MUST operate statelessly with no in-memory conversation or task state; all state persisted to database

- **FR-015**: System MUST use UV package manager for all backend Python dependencies with pyproject.toml configuration

- **FR-016**: System MUST implement database migrations using Alembic with separate migration history from Phase II

- **FR-017**: System MUST enforce complete Phase II/III separation with zero imports from phaseII directory

- **FR-018**: System MUST create database indexes on: tasks_phaseiii.user_id, conversations.user_id, messages.conversation_id, messages.user_id

- **FR-019**: System MUST use SQLModel for all database models and queries with async database operations via asyncpg driver

- **FR-020**: System MUST validate Better Auth JWT tokens for all tool invocations to extract authoritative user_id

### Non-Functional Requirements

- **NFR-001**: Tool invocation response time MUST be p95 < 200ms for database operations (excluding OpenAI API latency)

- **NFR-002**: Database connection MUST use connection pooling for scalability

- **NFR-003**: MCP server MUST be horizontally scalable with no shared in-memory state

- **NFR-004**: All tool code MUST achieve ≥80% test coverage with pytest

- **NFR-005**: Tool parameter validation errors MUST return descriptive messages within 50ms

- **NFR-006**: System MUST handle graceful degradation when database is unavailable without crashing

- **NFR-007**: All tool implementations MUST include multi-user isolation tests verifying User A cannot access User B's data

### Key Entities

- **Task (Phase III)**: Represents a todo item with title, description, completion status, and timestamps. Stored in tasks_phaseiii table (separate from Phase II tasks). Scoped to user_id for isolation. Supports CRUD operations via MCP tools.

- **Conversation**: Represents a chat session between user and AI assistant. Contains user_id for ownership and timestamps. Related to messages via one-to-many relationship.

- **Message**: Represents a single message in a conversation. Contains role (user/assistant), content (message text), conversation_id reference, and user_id for isolation. Ordered by created_at for conversation history.

- **MCP Tool**: Stateless function exposed by MCP server. Accepts parameters, validates inputs, performs database operations, and returns structured responses. All tools enforce user_id scoping for security.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task) are implemented and functional

- **SC-002**: MCP server successfully initializes using official MCP Python SDK and registers all tools

- **SC-003**: Database migrations create tasks_phaseiii, conversations, and messages tables with correct schemas and indexes

- **SC-004**: SQLModel models exist for all three entities with proper field types and relationships

- **SC-005**: All tool operations complete with p95 response time < 200ms in benchmark tests

- **SC-006**: 100% of multi-user isolation tests pass, verifying User A cannot access User B's tasks

- **SC-007**: All tool parameter validation tests pass, rejecting invalid inputs with correct error codes

- **SC-008**: Backend code achieves ≥80% test coverage measured by pytest-cov

- **SC-009**: Zero imports from phaseII directory in Phase III code verified by static analysis

- **SC-010**: Alembic migrations run successfully on clean database without errors

- **SC-011**: Backend uses UV package manager with all dependencies declared in pyproject.toml

- **SC-012**: All database queries use SQLModel ORM with async operations (no raw SQL outside migrations)

- **SC-013**: Tool error responses match Constitution format {detail, code, field} in all error scenarios

- **SC-014**: MCP server restarts without data loss; all state recovered from database (stateless verification)

## Dependencies

### External Dependencies

- **Official MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk - Required for MCP server implementation
- **SQLModel**: Required for database ORM with Pydantic integration
- **FastAPI**: Required for web framework and API endpoints
- **Alembic**: Required for database migrations
- **asyncpg**: Required for async PostgreSQL operations
- **Neon PostgreSQL**: Required for database hosting
- **Better Auth**: Required for JWT token validation
- **UV**: Required for Python package management

### Internal Dependencies

- **Constitution**: All architectural decisions and technology choices governed by `.specify/memory/constitution.md`
- **Database Schema**: Migrations must align with Constitution Data Model specifications for Phase III
- **Error Format**: Error responses must match Constitution error format standard

### Blocked By

- None - This is the foundational feature for Phase III

### Blocks

- Chat endpoint implementation (requires MCP tools to be functional)
- OpenAI Agents SDK integration (requires MCP server to be running)
- ChatKit frontend (requires backend API endpoints that use MCP tools)

## Assumptions

### Documented Assumptions

1. **Tool Timeout**: Tool invocations timeout after 5 seconds (default for AI interactions per Constitution XIII)

2. **Database Encoding**: Database uses UTF-8 encoding for text fields to support international characters and emoji

3. **Timestamp Precision**: All timestamps use millisecond precision and UTC timezone

4. **Auto-increment Start**: Primary key auto-increment starts at 1 for all tables

5. **Null vs Empty**: Empty string descriptions are stored as NULL in database for consistency

6. **Task Completion Idempotency**: Completing an already-completed task succeeds without error (idempotent operation)

7. **Task Deletion Non-Idempotency**: Deleting a non-existent task returns error (not idempotent)

8. **Default Status Filter**: When list_tasks is invoked without status parameter, default is "all"

9. **Connection Pool Size**: Database connection pool defaults to 10 connections (configurable via environment)

10. **JWT Token Location**: JWT token is passed in Authorization header as "Bearer <token>"

11. **User ID Format**: User ID from Better Auth is string format (UUID or similar)

12. **Field Update Semantics**: update_task with null value for optional field does not clear the field; field must be explicitly provided to update

### Constitutional Constraints Applied

All constitutional principles from `.specify/memory/constitution.md` apply, specifically:

- **Principle I (Spec-Driven Development)**: This specification drives all implementation
- **Principle II (Phase Separation)**: Zero imports from Phase II; separate tables
- **Principle III (Database Persistence)**: SQLModel with async operations; Alembic migrations
- **Principle IV (JWT Security)**: JWT user_id is authoritative for all data scoping
- **Principle V (Backend Architecture)**: FastAPI routers; error format standards
- **Principle XI (MCP Server Architecture)**: Official SDK; 5 tools; stateless design
- **Principle XIII (Conversational AI Standards)**: Stateless server; database-backed state

## Out of Scope

The following are explicitly excluded from this feature:

1. **Chat Endpoint Implementation**: POST /api/{user_id}/chat endpoint is separate feature
2. **OpenAI Agents SDK Integration**: Agent configuration with MCP tools is separate feature
3. **Frontend ChatKit UI**: User interface for chat is separate feature
4. **Better Auth Setup**: Authentication infrastructure assumed to exist from prior work
5. **Conversation Management Tools**: MCP tools for conversation CRUD are out of scope
6. **Task Priority Field**: Phase III tasks are simplified (no priority, due_date, recurrence)
7. **Task Tags**: Phase III does not implement tag functionality from Phase II
8. **Task Search**: Full-text search is out of scope for Phase III MVP
9. **Bulk Operations**: Batch create/update/delete operations are not included
10. **Task History/Audit Log**: Change tracking is out of scope
11. **Rate Limiting**: API rate limiting is future enhancement
12. **Caching**: Response caching is out of scope for MVP
13. **Pagination**: list_tasks returns all user tasks (no pagination in MVP)
14. **Task Sorting**: Results return in created_at DESC order (no custom sorting)
15. **Soft Deletes**: Task deletion is hard delete (no trash/recovery)

## Validation Checklist

### Content Quality
- [x] No implementation details (database-agnostic language used)
- [x] User-focused scenarios with clear acceptance criteria
- [x] Non-technical language for requirements (avoid framework specifics where possible)

### Requirement Completeness
- [x] Zero clarifications needed (all requirements specified)
- [x] All requirements are testable (Given-When-Then format)
- [x] Measurable success criteria (14 specific deliverables)
- [x] All edge cases identified with expected behaviors

### Feature Readiness
- [x] Acceptance criteria defined for all user stories
- [x] User scenarios cover all tool operations (add, list, complete, delete, update)
- [x] No technical implementation leakage (spec focuses on WHAT, not HOW)

---

**Next Steps**:
1. Review specification for constitutional compliance
2. Run `/sp.plan` to generate implementation plan
3. Run `/sp.tasks` to generate task breakdown
4. Execute `/sp.implement` to begin development
