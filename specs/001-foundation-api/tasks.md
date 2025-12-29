# Tasks: Advanced Task Management Foundation

**Input**: Design documents from `/specs/001-foundation-api/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the feature specification, so test tasks are EXCLUDED from this task list.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This feature follows Phase V structure:
- **Backend**: `phaseV/backend/app/`
- **Tests**: `phaseV/backend/tests/`
- **Migrations**: `phaseV/backend/alembic/versions/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [X] T001 Add python-dateutil>=2.8.2 dependency to phaseV/backend/pyproject.toml for RRULE parsing
- [X] T002 [P] Verify database connection to Neon Serverless PostgreSQL instance
- [X] T003 [P] Check existing alembic migration history in phaseV/backend/alembic/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database schema evolution and base models that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Migration

- [X] T004 Generate Alembic migration script with `uv run alembic revision --autogenerate -m "add_advanced_task_fields_and_tables"`
- [X] T005 Edit migration to create priority_level ENUM type (low, medium, high, urgent)
- [X] T006 Edit migration to create categories table with constraints (uq_category_user_name, check_color_format)
- [X] T007 Edit migration to create tags_phasev table with constraints (uq_tag_user_name, check_color_format)
- [X] T008 Edit migration to create task_tags junction table with foreign keys and CASCADE
- [X] T009 Edit migration to add 7 new columns to tasks_phaseiii (priority, due_date, category_id, recurrence_rule, reminder_sent, search_vector, search_rank)
- [X] T010 Edit migration to convert priority column from VARCHAR to priority_level ENUM
- [X] T011 Edit migration to add foreign key constraint fk_category from tasks_phaseiii to categories
- [X] T012 Edit migration to create indexes (idx_tasks_category_id, idx_tasks_due_date, idx_tasks_priority, idx_tasks_search_vector GIN)
- [X] T013 Edit migration to initialize search_vector for existing tasks with to_tsvector
- [X] T014 Edit migration to create update_search_vector() trigger function and tasks_search_vector_update trigger
- [X] T015 Edit migration to create update_updated_at_column() trigger function and tasks_updated_at_trigger trigger
- [X] T016 Edit migration downgrade to drop all triggers, functions, indexes, columns, tables, and ENUM type
- [X] T017 Run migration with `uv run alembic upgrade head` and verify schema

### Base Models

- [X] T018 [P] Create PriorityLevel enum in phaseV/backend/app/models/task.py
- [X] T019 [P] Create Category model in phaseV/backend/app/models/category.py with table name "categories"
- [X] T020 [P] Create TagPhaseV model in phaseV/backend/app/models/tag.py with table name "tags_phasev"
- [X] T021 [P] Create TaskTags junction model in phaseV/backend/app/models/task_tag.py
- [X] T022 Enhance TaskPhaseIII model in phaseV/backend/app/models/task.py with 7 new fields (priority, due_date, category_id, recurrence_rule, reminder_sent, created_at, updated_at)

### Schemas & Utilities

- [X] T023 [P] Create HEX_COLOR_REGEX pattern and CategoryCreate schema in phaseV/backend/app/schemas/category.py
- [X] T024 [P] Create CategoryUpdate schema in phaseV/backend/app/schemas/category.py
- [X] T025 [P] Create CategoryResponse and CategoryWithCount schemas in phaseV/backend/app/schemas/category.py
- [X] T026 [P] Create TagCreate, TagUpdate, TagResponse schemas in phaseV/backend/app/schemas/tag.py
- [X] T027 [P] Enhance TaskCreate schema in phaseV/backend/app/schemas/task.py with new fields (priority, due_date, category_id, tag_ids, recurrence_rule)
- [X] T028 [P] Enhance TaskUpdate schema in phaseV/backend/app/schemas/task.py with new fields
- [X] T029 [P] Enhance TaskResponse schema in phaseV/backend/app/schemas/task.py to include category object and tags array
- [X] T030 Create validate_rrule() function in phaseV/backend/app/utils/rrule_parser.py using python-dateutil

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Prioritization (Priority: P1) 🎯 MVP

**Goal**: Enable users to assign priority levels (low, medium, high, urgent) to tasks with filtering and validation

**Independent Test**: Create tasks with different priorities and verify tasks display correct priority. Filter by priority and verify only matching tasks appear.

### Implementation for User Story 1

- [X] T031 [P] [US1] Create priority validation logic in task service layer (phaseV/backend/app/services/task_service.py)
- [X] T032 [US1] Enhance add_task MCP tool in phaseV/backend/app/mcp/tools.py to accept priority parameter with default "medium"
- [X] T033 [US1] Enhance update_task MCP tool in phaseV/backend/app/mcp/tools.py to support priority updates
- [X] T034 [US1] Enhance list_tasks MCP tool in phaseV/backend/app/mcp/tools.py to support priority filtering
- [X] T035 [US1] Add priority field to all task response objects returned by MCP tools

**Checkpoint**: At this point, User Story 1 (Task Prioritization) should be fully functional and testable independently

---

## Phase 4: User Story 2 - Category Organization (Priority: P1)

**Goal**: Enable users to create categories and assign tasks to categories for organizational structure

**Independent Test**: Create categories, assign tasks to them, filter by category. Delete category and verify tasks remain but lose category assignment.

### Implementation for User Story 2

- [X] T036 [P] [US2] Create create_category() service function in phaseV/backend/app/services/category_service.py with 50-category limit enforcement
- [X] T037 [P] [US2] Create list_categories() service function in phaseV/backend/app/services/category_service.py with task_count JOIN
- [X] T038 [P] [US2] Create update_category() service function in phaseV/backend/app/services/category_service.py
- [X] T039 [P] [US2] Create delete_category() service function in phaseV/backend/app/services/category_service.py with tasks_affected count
- [X] T040 [US2] Implement create_category MCP tool in phaseV/backend/app/mcp/tools.py
- [X] T041 [US2] Implement list_categories MCP tool in phaseV/backend/app/mcp/tools.py
- [X] T042 [US2] Implement update_category MCP tool in phaseV/backend/app/mcp/tools.py
- [X] T043 [US2] Implement delete_category MCP tool in phaseV/backend/app/mcp/tools.py
- [X] T044 [US2] Enhance add_task and update_task MCP tools to support category_id parameter
- [X] T045 [US2] Enhance list_tasks MCP tool to support category_id filtering
- [X] T046 [US2] Enhance task response objects to include category object (id, name, color)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Flexible Tagging (Priority: P2)

**Goal**: Enable users to apply multiple tags to tasks for cross-categorical organization

**Independent Test**: Create tags, apply multiple tags to tasks, filter by tag. Delete tag and verify it's removed from all tasks without deleting tasks.

### Implementation for User Story 3

- [X] T047 [P] [US3] Create create_tag() service function in phaseV/backend/app/services/tag_service.py with 100-tag limit enforcement
- [X] T048 [P] [US3] Create list_tags() service function in phaseV/backend/app/services/tag_service.py with task_count JOIN
- [X] T049 [P] [US3] Create update_tag() service function in phaseV/backend/app/services/tag_service.py
- [X] T050 [P] [US3] Create delete_tag() service function in phaseV/backend/app/services/tag_service.py with tasks_affected count
- [X] T051 [P] [US3] Create add_tag_to_task() service function in phaseV/backend/app/services/tag_service.py with 10-tag limit enforcement
- [X] T052 [P] [US3] Create remove_tag_from_task() service function in phaseV/backend/app/services/tag_service.py
- [X] T053 [US3] Implement create_tag MCP tool in phaseV/backend/app/mcp/tools.py
- [X] T054 [US3] Implement list_tags MCP tool in phaseV/backend/app/mcp/tools.py
- [X] T055 [US3] Implement update_tag MCP tool in phaseV/backend/app/mcp/tools.py
- [X] T056 [US3] Implement delete_tag MCP tool in phaseV/backend/app/mcp/tools.py
- [X] T057 [US3] Implement add_tag_to_task MCP tool in phaseV/backend/app/mcp/tools.py
- [X] T058 [US3] Implement remove_tag_from_task MCP tool in phaseV/backend/app/mcp/tools.py
- [X] T059 [US3] Enhance add_task MCP tool to support tag_ids parameter with atomic transaction
- [X] T060 [US3] Enhance list_tasks MCP tool to support tag_ids filtering with OR logic
- [X] T061 [US3] Enhance task response objects to include tags array with (id, name, color)

**Checkpoint**: All P1 and P2 priority stories should now be independently functional

---

## Phase 6: User Story 4 - Due Date Management (Priority: P2)

**Goal**: Enable users to set due dates on tasks with timezone handling and date-based filtering

**Independent Test**: Set due dates, view tasks sorted by due date, filter by date ranges. Verify overdue tasks display correctly.

### Implementation for User Story 4

- [X] T062 [P] [US4] Create timezone conversion validator in phaseV/backend/app/schemas/task.py to convert ISO 8601 to UTC
- [X] T063 [US4] Enhance add_task MCP tool to accept due_date parameter (ISO 8601) and convert to UTC
- [X] T064 [US4] Enhance update_task MCP tool to support due_date updates (including setting to null)
- [X] T065 [US4] Enhance list_tasks MCP tool to support due_before and due_after filtering
- [X] T066 [US4] Enhance list_tasks MCP tool to support sort_by='due_date' with proper null handling
- [X] T067 [US4] Add due_date field to all task response objects in ISO 8601 UTC format

**Checkpoint**: Due date management should be fully functional and testable independently

---

## Phase 7: User Story 5 - Keyword Search (Priority: P2)

**Goal**: Enable full-text search across task titles and descriptions with relevance ranking

**Independent Test**: Create tasks with various content, search for keywords, verify results are ranked by relevance with title matches ranked higher.

### Implementation for User Story 5

- [X] T068 [P] [US5] Create search_tasks() service function in phaseV/backend/app/services/search_service.py using PostgreSQL ts_rank()
- [X] T069 [P] [US5] Implement query parsing logic to handle empty queries (return all tasks)
- [X] T070 [P] [US5] Implement relevance scoring with title weight higher than description
- [X] T071 [US5] Implement search_tasks MCP tool in phaseV/backend/app/mcp/tools.py
- [X] T072 [US5] Add support for combining search with filters (category_id, priority, tag_ids) using AND logic
- [X] T073 [US5] Add relevance_score field to search results response
- [X] T074 [US5] Enhance list_tasks MCP tool to support optional search query parameter for combined search+filter

**Checkpoint**: Full-text search should be fully functional with <200ms p95 latency for 10k tasks

---

## Phase 8: User Story 6 - Recurring Task Setup (Priority: P3)

**Goal**: Enable users to set recurrence rules on tasks using iCalendar RRULE format with validation

**Independent Test**: Create task with recurrence rule, verify rule is stored and displayed correctly. Attempt invalid RRULE and verify validation error.

### Implementation for User Story 6

- [X] T075 [P] [US6] Create recurrence_rule validation in task service using validate_rrule() from utils
- [X] T076 [US6] Enhance add_task MCP tool to accept recurrence_rule parameter with validation
- [X] T077 [US6] Enhance update_task MCP tool to support recurrence_rule updates (including setting to null)
- [X] T078 [US6] Add recurrence_rule field to all task response objects
- [X] T079 [US6] Add warning logic when creating recurring task without due_date

**Checkpoint**: Recurring task setup should be fully functional (storage and validation only; instance generation deferred to 002-event-streaming)

---

## Phase 9: Advanced Feature - Reminders (Complementary)

**Goal**: Implement set_reminder MCP tool for storing reminder metadata (actual notification sending deferred to 002-event-streaming)

**Independent Test**: Set reminder on task with due_date, verify remind_at timestamp is calculated correctly. Attempt on task without due_date and verify error.

### Implementation for Reminders

- [X] T080 [P] Create validate_reminder() function in task service to check due_date exists
- [X] T081 [P] Create calculate_remind_at() function to compute remind_at = due_date - remind_before_minutes
- [X] T082 Implement set_reminder MCP tool in phaseV/backend/app/mcp/tools.py with validation
- [X] T083 Add reminder metadata storage logic (implementation TBD - placeholder for 002-event-streaming)

**Checkpoint**: Reminder tool should validate inputs correctly (actual notification logic deferred)

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Error Handling & Validation

- [X] T084 [P] Implement consistent error response format across all 17 MCP tools
- [X] T085 [P] Add data isolation validation to all service functions (user_id scoping)
- [X] T086 [P] Add multi-user isolation checks across all MCP tools
- [X] T087 Add input validation error messages for all schema validations

### Documentation & Code Quality

- [X] T088 [P] Add docstrings to all 17 MCP tools following contract specifications
- [X] T089 [P] Add docstrings to all service functions with parameter descriptions
- [X] T090 [P] Run ruff check on phaseV/backend/app/ and fix any linting errors
- [X] T091 [P] Run ruff format on phaseV/backend/app/ for code formatting

### Validation & Verification

- [X] T092 Verify all 17 MCP tools are registered in phaseV/backend/app/mcp/server.py
- [X] T093 Run quickstart.md validation workflows (create category, create tag, create task with all features)
- [X] T094 Verify database indexes exist using `\d+ tasks_phaseiii` in psql
- [X] T095 Verify GIN index on search_vector is being used in search queries
- [X] T096 Run manual data isolation test (create User A and User B data, verify no cross-access)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Task Prioritization): Can start after Foundational - No story dependencies
  - US2 (Category Organization): Can start after Foundational - No story dependencies
  - US3 (Flexible Tagging): Can start after Foundational - No story dependencies
  - US4 (Due Date Management): Can start after Foundational - No story dependencies
  - US5 (Keyword Search): Can start after Foundational - No story dependencies
  - US6 (Recurring Tasks): Can start after Foundational - No story dependencies
- **Reminders (Phase 9)**: Depends on US4 (Due Date Management) for due_date field
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

All user stories are **independently implementable** after Foundational phase completes. Stories can be worked on:
- **Sequentially** in priority order: P1 (US1, US2) → P2 (US3, US4, US5) → P3 (US6)
- **In parallel** by different team members (recommended for P1 stories)

### Within Each User Story

- Models/schemas before services
- Services before MCP tools
- Core implementation before enhancements
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: All 3 tasks can run in parallel
- **Phase 2 (Foundational)**:
  - Migration edit tasks (T005-T016) are sequential within migration file
  - Models (T018-T022) can run in parallel AFTER migration completes
  - Schemas (T023-T029) can run in parallel
- **User Stories**: After Foundational completes, US1-US6 can all start in parallel (if team capacity allows)
- **Within each story**: Tasks marked [P] can run in parallel

---

## Parallel Example: Phase 2 Foundational

```bash
# After migration (T004-T017) completes, launch all base models in parallel:
Task: "Create PriorityLevel enum in phaseV/backend/app/models/task.py"
Task: "Create Category model in phaseV/backend/app/models/category.py"
Task: "Create TagPhaseV model in phaseV/backend/app/models/tag.py"
Task: "Create TaskTags junction model in phaseV/backend/app/models/task_tag.py"

# Then launch all schema files in parallel:
Task: "Create HEX_COLOR_REGEX and CategoryCreate schema in phaseV/backend/app/schemas/category.py"
Task: "Create TagCreate, TagUpdate, TagResponse schemas in phaseV/backend/app/schemas/tag.py"
Task: "Enhance TaskCreate schema in phaseV/backend/app/schemas/task.py"
```

---

## Parallel Example: User Story 2 (Category Organization)

```bash
# Launch all category service functions in parallel (different functionality, no conflicts):
Task: "Create create_category() service function in phaseV/backend/app/services/category_service.py"
Task: "Create list_categories() service function in phaseV/backend/app/services/category_service.py"
Task: "Create update_category() service function in phaseV/backend/app/services/category_service.py"
Task: "Create delete_category() service function in phaseV/backend/app/services/category_service.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only - Both P1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Task Prioritization)
4. Complete Phase 4: User Story 2 (Category Organization)
5. **STOP and VALIDATE**: Test both stories independently
6. Deploy/demo if ready

### Incremental Delivery (Recommended)

1. Setup + Foundational → Foundation ready
2. Add US1 (Priority) + US2 (Categories) → Test independently → Deploy/Demo (MVP with P1 features!)
3. Add US3 (Tags) → Test independently → Deploy/Demo
4. Add US4 (Due Dates) → Test independently → Deploy/Demo
5. Add US5 (Search) → Test independently → Deploy/Demo
6. Add US6 (Recurring) → Test independently → Deploy/Demo
7. Add Phase 9 (Reminders) → Test independently → Deploy/Demo
8. Phase 10: Polish → Final validation
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Task Prioritization)
   - Developer B: User Story 2 (Category Organization)
   - Developer C: User Story 3 (Flexible Tagging)
   - Developer D: User Story 4 (Due Date Management)
3. Stories complete and integrate independently
4. Developer E: User Story 5 (Keyword Search) + User Story 6 (Recurring Tasks)
5. All developers: Phase 10 (Polish)

---

## Task Completion Summary

**Total Tasks**: 96

**Tasks by Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 27 tasks
- Phase 3 (US1 - Task Prioritization): 5 tasks
- Phase 4 (US2 - Category Organization): 11 tasks
- Phase 5 (US3 - Flexible Tagging): 15 tasks
- Phase 6 (US4 - Due Date Management): 6 tasks
- Phase 7 (US5 - Keyword Search): 7 tasks
- Phase 8 (US6 - Recurring Tasks): 5 tasks
- Phase 9 (Reminders): 4 tasks
- Phase 10 (Polish): 13 tasks

**Tasks by User Story**:
- US1 (Task Prioritization - P1): 5 tasks
- US2 (Category Organization - P1): 11 tasks
- US3 (Flexible Tagging - P2): 15 tasks
- US4 (Due Date Management - P2): 6 tasks
- US5 (Keyword Search - P2): 7 tasks
- US6 (Recurring Tasks - P3): 5 tasks
- Shared/Infrastructure: 47 tasks

**Parallel Opportunities Identified**:
- Phase 1: 3 parallel tasks (all setup tasks)
- Phase 2: 17 parallel tasks (models, schemas, utilities)
- User Stories: 6 stories can run in parallel after Foundational
- Within stories: 35+ tasks marked [P] can run in parallel

**Suggested MVP Scope**:
- Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (US1) + Phase 4 (US2) = 46 tasks
- Delivers core prioritization and categorization capabilities (both P1 features)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label (US1-US6) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are NOT included (not requested in spec)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Database migration (T004-T017) is sequential and must complete before any model/service work
- All 17 MCP tools must be implemented as per contracts/mcp-tools.md
- Performance target: Search <200ms p95 for 10k tasks, List queries <200ms p95
