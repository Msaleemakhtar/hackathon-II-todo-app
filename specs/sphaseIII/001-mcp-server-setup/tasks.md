# Tasks: MCP Server Implementation for Phase III

**Input**: Design documents from `/specs/sphaseIII/001-mcp-server-setup/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Tests are included per Constitution NFR-004 (≥80% test coverage required)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This feature uses web app structure:
- Backend: `phaseIII/backend/`
- Source: `phaseIII/backend/app/`
- Tests: `phaseIII/backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create Phase III backend directory structure per plan.md
- [X] T002 Initialize Python project with UV in phaseIII/backend/pyproject.toml
- [X] T003 [P] Create .env.example with DATABASE_URL, BETTER_AUTH_SECRET, DB_POOL_MIN, DB_POOL_MAX, JWT_CACHE_SIZE, JWT_CACHE_TTL, DEBUG
- [X] T004 [P] Create .gitignore for Python (venv, __pycache__, .env, *.pyc)
- [X] T005 [P] Configure ruff for linting in phaseIII/backend/pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Install core dependencies via UV: fastapi, sqlmodel, alembic, asyncpg, python-jose, pydantic-settings
- [X] T007 Install MCP Python SDK via UV: mcp (from https://github.com/modelcontextprotocol/python-sdk)
- [X] T008 [P] Install dev dependencies via UV: pytest, pytest-asyncio, pytest-cov, ruff, mypy
- [X] T009 Create app/config.py with Settings class for DATABASE_URL, BETTER_AUTH_SECRET, DB_POOL_MIN, DB_POOL_MAX, JWT_CACHE_SIZE, JWT_CACHE_TTL, DEBUG
- [X] T010 Create app/database.py with async engine, sessionmaker, and get_session dependency
- [X] T011 Initialize Alembic in phaseIII/backend/alembic.ini with Phase III configuration
- [X] T012 Configure Alembic env.py to use async engine and SQLModel metadata
- [X] T013 Create app/models/__init__.py for SQLModel imports
- [X] T014 Create app/schemas/__init__.py for Pydantic schemas
- [X] T015 Create app/mcp/__init__.py for MCP server module
- [X] T016 Create app/services/__init__.py for business logic layer
- [X] T017 Create app/auth/__init__.py for authentication utilities
- [X] T018 Create tests/conftest.py with async database fixtures and test session setup
- [X] T019 Implement JWT validation utility in app/auth/jwt.py with verify_token function using python-jose
- [X] T020 Create initial Alembic migration (001) for tasks_phaseiii, conversations, messages tables per data-model.md
- [X] T021 Run Alembic migration to create database schema: uv run alembic upgrade head (requires .env with DATABASE_URL)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 6 - Database Infrastructure Setup (Priority: P1) 🎯 FOUNDATIONAL

**Goal**: Establish database models and infrastructure for Phase III task management

**Independent Test**: Run migrations, create database records, verify table schemas match specifications with proper indexes and foreign keys

### Implementation for User Story 6

- [X] T022 [P] [US6] Create TaskPhaseIII model in app/models/task.py with fields: id, user_id, title, description, completed, created_at, updated_at per data-model.md
- [X] T023 [P] [US6] Create Conversation model in app/models/conversation.py with fields: id, user_id, created_at, updated_at per data-model.md
- [X] T024 [P] [US6] Create Message model in app/models/message.py with fields: id, conversation_id, user_id, role, content, created_at per data-model.md
- [X] T025 [US6] Verify Alembic migration created correct indexes: idx_tasks_phaseiii_user_id, idx_tasks_phaseiii_created_at, idx_conversations_user_id, idx_messages_conversation_id, idx_messages_user_id
- [X] T026 [US6] Verify foreign key constraint: messages.conversation_id → conversations.id with CASCADE on delete

### Tests for User Story 6

- [ ] T027 [P] [US6] Write model validation tests in tests/test_models.py for TaskPhaseIII field constraints
- [ ] T028 [P] [US6] Write model validation tests in tests/test_models.py for Conversation field constraints
- [ ] T029 [P] [US6] Write model validation tests in tests/test_models.py for Message field constraints and FK relationships

**Checkpoint**: Database models and migrations complete and verified

---

## Phase 4: User Story 7 - MCP Server Configuration (Priority: P1) 🎯 FOUNDATIONAL

**Goal**: Initialize MCP server using official Python SDK and register all 5 tools

**Independent Test**: Start server, verify tool registration, confirm server can process tool invocation requests

### Implementation for User Story 7

- [X] T030 [US7] Create MCP server manager in app/mcp/server.py with MCPServer initialization and tool registration logic
- [X] T031 [US7] Create app/mcp/validators.py with shared parameter validation functions for user_id, title, description, task_id, status
- [X] T032 [US7] Create FastAPI app initialization in app/main.py with MCP server startup and lifespan management
- [X] T033 [US7] Register FastAPI health check endpoint GET /health returning {"status": "ok"}

### Tests for User Story 7

- [ ] T034 [P] [US7] Write MCP server initialization test in tests/test_mcp_server.py verifying all 5 tools are registered
- [ ] T035 [P] [US7] Write stateless architecture test in tests/test_mcp_server.py verifying no in-memory conversation state exists

**Checkpoint**: MCP server infrastructure ready for tool implementations

---

## Phase 5: User Story 1 - Task Creation via MCP Tool (Priority: P1) 🎯 MVP

**Goal**: Enable AI assistant to create tasks via add_task MCP tool

**Independent Test**: Invoke add_task tool with user_id and title, verify task appears in database with correct attributes and tool returns task_id

### Implementation for User Story 1

- [X] T036 [US1] Create TaskService in app/services/task_service.py with create_task method accepting user_id, title, description
- [X] T037 [US1] Implement add_task MCP tool in app/mcp/tools/add_task.py using TaskService.create_task
- [X] T038 [US1] Add title validation in add_task tool: required, 1-200 characters after trimming, return error "INVALID_TITLE" if invalid
- [X] T039 [US1] Add description validation in add_task tool: optional, ≤1000 characters, return error "DESCRIPTION_TOO_LONG" if invalid
- [X] T040 [US1] Register add_task tool in app/mcp/server.py with contract from contracts/add_task.json
- [X] T041 [US1] Create Pydantic schemas in app/schemas/task.py: TaskCreate, TaskResponse matching add_task contract

### Tests for User Story 1

- [ ] T042 [P] [US1] Write test in tests/test_mcp_tools/test_add_task.py for valid task creation returning task_id and status "created"
- [ ] T043 [P] [US1] Write test in tests/test_mcp_tools/test_add_task.py for title exceeding 200 characters returning "INVALID_TITLE" error
- [ ] T044 [P] [US1] Write test in tests/test_mcp_tools/test_add_task.py for empty/whitespace title returning "INVALID_TITLE" error
- [ ] T045 [P] [US1] Write test in tests/test_mcp_tools/test_add_task.py for description exceeding 1000 characters returning "DESCRIPTION_TOO_LONG" error
- [ ] T046 [P] [US1] Write service layer test in tests/test_task_service.py for create_task method

**Checkpoint**: add_task tool fully functional and independently testable

---

## Phase 6: User Story 2 - Task Listing via MCP Tool (Priority: P1)

**Goal**: Enable AI assistant to retrieve and display user's tasks via list_tasks MCP tool

**Independent Test**: Create several tasks for a user, invoke list_tasks with different status filters (all/pending/completed), verify correct tasks returned while excluding other users' tasks

### Implementation for User Story 2

- [ ] T047 [US2] Add list_tasks method to TaskService in app/services/task_service.py with user_id and status filter parameters
- [ ] T048 [US2] Implement list_tasks MCP tool in app/mcp/tools/list_tasks.py using TaskService.list_tasks
- [ ] T049 [US2] Add status filter validation in list_tasks tool: must be "all", "pending", or "completed", return error "INVALID_PARAMETER" if invalid
- [ ] T050 [US2] Implement query filtering logic: status="pending" filters completed=false, status="completed" filters completed=true, status="all" returns all
- [ ] T051 [US2] Register list_tasks tool in app/mcp/server.py with contract from contracts/list_tasks.json
- [ ] T052 [US2] Add TaskList schema in app/schemas/task.py for list_tasks response

### Tests for User Story 2

- [ ] T053 [P] [US2] Write test in tests/test_mcp_tools/test_list_tasks.py for user with 3 pending and 2 completed tasks invoking status="all" returning all 5 tasks
- [ ] T054 [P] [US2] Write test in tests/test_mcp_tools/test_list_tasks.py for status="pending" returning only 3 pending tasks
- [ ] T055 [P] [US2] Write test in tests/test_mcp_tools/test_list_tasks.py for status="completed" returning only 2 completed tasks
- [ ] T056 [P] [US2] Write test in tests/test_mcp_tools/test_list_tasks.py for User A invoking list_tasks returning only User A's tasks (data isolation)
- [ ] T057 [P] [US2] Write test in tests/test_mcp_tools/test_list_tasks.py for user with no tasks returning empty array
- [ ] T058 [P] [US2] Write test in tests/test_mcp_tools/test_list_tasks.py for invalid status filter returning "INVALID_PARAMETER" error

**Checkpoint**: list_tasks tool fully functional with proper filtering and data isolation

---

## Phase 7: User Story 3 - Task Completion via MCP Tool (Priority: P1)

**Goal**: Enable AI assistant to mark tasks as complete via complete_task MCP tool

**Independent Test**: Create a pending task, invoke complete_task with task_id, verify task's completed field is updated to true in database

### Implementation for User Story 3

- [ ] T059 [US3] Add complete_task method to TaskService in app/services/task_service.py with user_id and task_id parameters
- [ ] T060 [US3] Implement complete_task MCP tool in app/mcp/tools/complete_task.py using TaskService.complete_task
- [ ] T061 [US3] Add task existence validation in complete_task: query by task_id AND user_id, return "TASK_NOT_FOUND" if not exists
- [ ] T062 [US3] Implement idempotent completion logic: if already completed, return success without error
- [ ] T063 [US3] Register complete_task tool in app/mcp/server.py with contract from contracts/complete_task.json

### Tests for User Story 3

- [ ] T064 [P] [US3] Write test in tests/test_mcp_tools/test_complete_task.py for pending task invoking complete_task setting completed=true and returning status "completed"
- [ ] T065 [P] [US3] Write test in tests/test_mcp_tools/test_complete_task.py for non-existent task_id returning "TASK_NOT_FOUND" error
- [ ] T066 [P] [US3] Write test in tests/test_mcp_tools/test_complete_task.py for User B invoking complete_task on User A's task returning "TASK_NOT_FOUND" (data isolation)
- [ ] T067 [P] [US3] Write test in tests/test_mcp_tools/test_complete_task.py for already completed task succeeding idempotently

**Checkpoint**: complete_task tool fully functional with proper ownership validation and idempotency

---

## Phase 8: User Story 4 - Task Deletion via MCP Tool (Priority: P1)

**Goal**: Enable AI assistant to remove tasks via delete_task MCP tool

**Independent Test**: Create a task, invoke delete_task with task_id, verify task is removed from database and no longer appears in list_tasks

### Implementation for User Story 4

- [ ] T068 [US4] Add delete_task method to TaskService in app/services/task_service.py with user_id and task_id parameters
- [ ] T069 [US4] Implement delete_task MCP tool in app/mcp/tools/delete_task.py using TaskService.delete_task
- [ ] T070 [US4] Add task existence validation in delete_task: query by task_id AND user_id, return "TASK_NOT_FOUND" if not exists
- [ ] T071 [US4] Implement hard delete logic: remove task from database (not soft delete)
- [ ] T072 [US4] Register delete_task tool in app/mcp/server.py with contract from contracts/delete_task.json

### Tests for User Story 4

- [ ] T073 [P] [US4] Write test in tests/test_mcp_tools/test_delete_task.py for existing task invoking delete_task removing task and returning status "deleted"
- [ ] T074 [P] [US4] Write test in tests/test_mcp_tools/test_delete_task.py for non-existent task_id returning "TASK_NOT_FOUND" error
- [ ] T075 [P] [US4] Write test in tests/test_mcp_tools/test_delete_task.py for User B invoking delete_task on User A's task returning "TASK_NOT_FOUND" (data isolation)
- [ ] T076 [P] [US4] Write test in tests/test_mcp_tools/test_delete_task.py for deleted task_id invoking delete_task again returning "TASK_NOT_FOUND" (not idempotent)

**Checkpoint**: delete_task tool fully functional with proper ownership validation

---

## Phase 9: User Story 5 - Task Update via MCP Tool (Priority: P2)

**Goal**: Enable AI assistant to modify task details via update_task MCP tool

**Independent Test**: Create a task, invoke update_task with new title or description, verify task fields are updated in database while other fields remain unchanged

### Implementation for User Story 5

- [ ] T077 [US5] Add update_task method to TaskService in app/services/task_service.py with user_id, task_id, title, description parameters
- [ ] T078 [US5] Implement update_task MCP tool in app/mcp/tools/update_task.py using TaskService.update_task
- [ ] T079 [US5] Add parameter validation in update_task: at least one field (title or description) must be provided, return "INVALID_PARAMETER" if none provided
- [ ] T080 [US5] Add title validation in update_task: if provided, must be 1-200 characters, return "INVALID_TITLE" if invalid
- [ ] T081 [US5] Add description validation in update_task: if provided, must be ≤1000 characters, return "DESCRIPTION_TOO_LONG" if invalid
- [ ] T082 [US5] Add task existence validation in update_task: query by task_id AND user_id, return "TASK_NOT_FOUND" if not exists
- [ ] T083 [US5] Implement partial update logic: only update provided fields, leave others unchanged
- [ ] T084 [US5] Register update_task tool in app/mcp/server.py with contract from contracts/update_task.json
- [ ] T085 [US5] Add TaskUpdate schema in app/schemas/task.py for update_task request

### Tests for User Story 5

- [ ] T086 [P] [US5] Write test in tests/test_mcp_tools/test_update_task.py for updating title only and verifying description unchanged
- [ ] T087 [P] [US5] Write test in tests/test_mcp_tools/test_update_task.py for updating description only and verifying title unchanged
- [ ] T088 [P] [US5] Write test in tests/test_mcp_tools/test_update_task.py for updating both title and description
- [ ] T089 [P] [US5] Write test in tests/test_mcp_tools/test_update_task.py for title exceeding 200 characters returning "INVALID_TITLE" error
- [ ] T090 [P] [US5] Write test in tests/test_mcp_tools/test_update_task.py for non-existent task_id returning "TASK_NOT_FOUND" error
- [ ] T091 [P] [US5] Write test in tests/test_mcp_tools/test_update_task.py for User B invoking update_task on User A's task returning "TASK_NOT_FOUND" (data isolation)
- [ ] T092 [P] [US5] Write test in tests/test_mcp_tools/test_update_task.py for no fields provided returning "INVALID_PARAMETER" error

**Checkpoint**: update_task tool fully functional with proper validation and partial update logic

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T093 [P] Add MCP error response schemas in app/schemas/mcp.py with MCPError class
- [X] T094 [P] Implement global error handler in app/main.py for consistent error format {detail, code, field}
- [X] T095 [P] Add logging configuration in app/main.py for request/response logging
- [ ] T096 [P] Create README.md in phaseIII/backend/ with setup instructions per quickstart.md
- [ ] T097 Write integration test in tests/test_integration.py verifying multi-user isolation across all tools
- [ ] T098 Write integration test in tests/test_integration.py for concurrent task creation handling
- [ ] T099 [P] Run pytest with coverage: uv run pytest --cov=app --cov-report=term-missing
- [ ] T100 Verify test coverage ≥80% per NFR-004 requirement
- [ ] T101 [P] Add database connection pool monitoring in app/database.py
- [ ] T102 [P] Implement graceful degradation for database unavailability in app/database.py
- [ ] T103 Run quickstart.md validation: verify all commands work end-to-end
- [ ] T104 [P] Add type hints verification: uv run mypy app/
- [X] T105 [P] Run linting: uv run ruff check app/ tests/
- [X] T106 Verify zero Phase II imports: grep -r "from phaseII" phaseIII/backend/app/ should return nothing
- [X] T107 [P] Create phaseIII/.env.example with all required environment variables
- [X] T108 [P] Update .gitignore to exclude phaseIII/backend/.env and __pycache__

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 6 - Database Infrastructure (Phase 3)**: Depends on Foundational - Provides models for all MCP tools
- **User Story 7 - MCP Server Config (Phase 4)**: Depends on Foundational - Provides server infrastructure for all tools
- **User Stories 1-5 (Phases 5-9)**: All depend on Phases 3 & 4 completion
  - Can proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4 → US5)
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 6 (Database)**: Foundational - BLOCKS all MCP tool implementations
- **User Story 7 (MCP Server)**: Foundational - BLOCKS all MCP tool implementations
- **User Story 1 (add_task)**: Can start after US6 & US7 - No dependencies on other tools
- **User Story 2 (list_tasks)**: Can start after US6 & US7 - No dependencies on other tools
- **User Story 3 (complete_task)**: Can start after US6 & US7 - No dependencies on other tools
- **User Story 4 (delete_task)**: Can start after US6 & US7 - No dependencies on other tools
- **User Story 5 (update_task)**: Can start after US6 & US7 - No dependencies on other tools

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Models before services
- Services before MCP tools
- Tool implementation before tool registration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T003, T004, T005 can run in parallel
- **Phase 2 (Foundational)**: T008 can run in parallel with T006-T007 after they complete
- **Phase 3 (US6 - Database)**: T022, T023, T024 (models) can run in parallel; T027, T028, T029 (tests) can run in parallel
- **Phase 4 (US7 - MCP Server)**: T034, T035 (tests) can run in parallel
- **Phase 5 (US1)**: T042, T043, T044, T045, T046 (tests) can run in parallel
- **Phase 6 (US2)**: T053, T054, T055, T056, T057, T058 (tests) can run in parallel
- **Phase 7 (US3)**: T064, T065, T066, T067 (tests) can run in parallel
- **Phase 8 (US4)**: T073, T074, T075, T076 (tests) can run in parallel
- **Phase 9 (US5)**: T086, T087, T088, T089, T090, T091, T092 (tests) can run in parallel
- **Phase 10 (Polish)**: T093, T094, T095, T096, T099, T101, T102, T104, T105, T107, T108 can run in parallel
- **Once Foundational completes**: User Stories 1-5 (Phases 5-9) can be worked on in parallel by different team members

---

## Parallel Example: User Story 1 (add_task)

```bash
# Launch all tests for User Story 1 together:
Task T042: "Write test for valid task creation"
Task T043: "Write test for title exceeding 200 characters"
Task T044: "Write test for empty/whitespace title"
Task T045: "Write test for description exceeding 1000 characters"
Task T046: "Write service layer test for create_task"
```

---

## Implementation Strategy

### MVP First (User Stories 6, 7, 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 6 (Database Infrastructure)
4. Complete Phase 4: User Story 7 (MCP Server Configuration)
5. Complete Phase 5: User Story 1 (add_task tool)
6. **STOP and VALIDATE**: Test add_task independently
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational + Database + MCP Server → Foundation ready
2. Add User Story 1 (add_task) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (list_tasks) → Test independently → Deploy/Demo
4. Add User Story 3 (complete_task) → Test independently → Deploy/Demo
5. Add User Story 4 (delete_task) → Test independently → Deploy/Demo
6. Add User Story 5 (update_task) → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational + Database + MCP Server together
2. Once Phases 3 & 4 are done:
   - Developer A: User Story 1 (add_task)
   - Developer B: User Story 2 (list_tasks)
   - Developer C: User Story 3 (complete_task)
   - Developer D: User Story 4 (delete_task)
   - Developer E: User Story 5 (update_task)
3. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 108

**Tasks by Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 16 tasks
- Phase 3 (US6 - Database): 8 tasks
- Phase 4 (US7 - MCP Server): 6 tasks
- Phase 5 (US1 - add_task): 11 tasks
- Phase 6 (US2 - list_tasks): 12 tasks
- Phase 7 (US3 - complete_task): 9 tasks
- Phase 8 (US4 - delete_task): 9 tasks
- Phase 9 (US5 - update_task): 16 tasks
- Phase 10 (Polish): 16 tasks

**Tasks by User Story**:
- US1 (Task Creation): 11 tasks
- US2 (Task Listing): 12 tasks
- US3 (Task Completion): 9 tasks
- US4 (Task Deletion): 9 tasks
- US5 (Task Update): 16 tasks
- US6 (Database Infrastructure): 8 tasks
- US7 (MCP Server Configuration): 6 tasks
- Setup/Foundational: 21 tasks
- Polish: 16 tasks

**Parallel Opportunities**: 47 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Invoke add_task tool, verify task in database
- US2: Create tasks, invoke list_tasks, verify filtering and isolation
- US3: Create task, invoke complete_task, verify completed=true
- US4: Create task, invoke delete_task, verify task removed
- US5: Create task, invoke update_task, verify partial updates
- US6: Run migrations, verify schemas and indexes
- US7: Start server, verify tool registration

**Suggested MVP Scope**: Phases 1-5 (Setup + Foundational + Database + MCP Server + add_task tool) = 43 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks include exact file paths for implementation
- Tests achieve ≥80% coverage per Constitution NFR-004
- Zero Phase II imports enforced by validation task T106
