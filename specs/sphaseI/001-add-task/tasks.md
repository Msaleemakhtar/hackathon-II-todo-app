# Tasks: Add Task

**Input**: Design documents from `/specs/001-add-task/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, research.md, quickstart.md

**Tests**: Constitution Principle VI mandates 100% test coverage. All test tasks included per requirement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Initialize Python 3.13 project with UV (`uv init` or create pyproject.toml manually)
- [X] T002 [P] Create project directory structure (src/models, src/services, src/ui, tests/unit, tests/integration)
- [X] T003 [P] Create __init__.py files in src/, src/models/, src/services/, src/ui/, tests/, tests/unit/, tests/integration/
- [X] T004 Add pytest and pytest-cov as dev dependencies in pyproject.toml
- [X] T005 [P] Add ruff as dev dependency and configure in pyproject.toml (line-length, target-version)
- [X] T006 [P] Create .gitignore with Python patterns (__pycache__, *.pyc, .pytest_cache, .coverage, .venv)

**Checkpoint**: Project structure ready - code implementation can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Define constants in src/constants.py (MAX_TITLE_LENGTH=200, MAX_DESCRIPTION_LENGTH=1000, error messages, prompts)
- [X] T008 Create Task dataclass in src/models/task.py with all 6 fields and type hints
- [X] T009 Add generate_timestamp() static method to Task class in src/models/task.py (returns ISO 8601 UTC format)
- [X] T010 Create module-level _task_storage list in src/services/task_service.py
- [X] T011 Implement generate_next_id() function in src/services/task_service.py (returns 1 or max+1)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Task with Title and Description (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks with both title and detailed description

**Independent Test**: Navigate to Add Task, enter valid title and description, verify task created with correct data

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation (TDD)**

- [X] T012 [P] [US1] Write unit test for Task dataclass instantiation in tests/unit/test_task_model.py
- [X] T013 [P] [US1] Write unit test for Task.generate_timestamp() format in tests/unit/test_task_model.py
- [X] T014 [P] [US1] Write unit test for validate_title() with valid input in tests/unit/test_validation.py
- [X] T015 [P] [US1] Write unit test for validate_title() with empty input (ERROR 001) in tests/unit/test_validation.py
- [X] T016 [P] [US1] Write unit test for validate_title() with >200 chars (ERROR 002) in tests/unit/test_validation.py
- [X] T017 [P] [US1] Write unit test for validate_description() with valid input in tests/unit/test_validation.py
- [X] T018 [P] [US1] Write unit test for validate_description() with >1000 chars (ERROR 003) in tests/unit/test_validation.py
- [X] T019 [P] [US1] Write unit test for create_task() function in tests/unit/test_task_service.py
- [X] T020 [P] [US1] Write unit test for generate_next_id() with empty storage in tests/unit/test_task_service.py
- [X] T021 [P] [US1] Write unit test for generate_next_id() with existing tasks in tests/unit/test_task_service.py
- [X] T022 [P] [US1] Write integration test for complete add task flow with title+description in tests/integration/test_add_task_flow.py

### Implementation for User Story 1

- [X] T023 [P] [US1] Implement validate_title() function in src/ui/prompts.py with whitespace stripping and length check
- [X] T024 [P] [US1] Implement validate_description() function in src/ui/prompts.py with whitespace stripping and length check
- [X] T025 [US1] Implement get_task_title() function in src/ui/prompts.py with retry loop and error display
- [X] T026 [US1] Implement get_task_description() function in src/ui/prompts.py with retry loop and error display
- [X] T027 [US1] Implement create_task() function in src/services/task_service.py (generate ID, timestamps, append to storage)
- [X] T028 [US1] Implement get_all_tasks() function in src/services/task_service.py (return copy of storage)
- [X] T029 [US1] Create handle_add_task() function in src/main.py (calls get_task_title, get_task_description, create_task, prints success)
- [X] T030 [US1] Add main menu with 6 options in src/main.py main() function
- [X] T031 [US1] Wire up menu option 1 to call handle_add_task() in src/main.py
- [X] T032 [US1] Add menu loop with exit option in src/main.py
- [X] T033 [US1] Verify all tests pass: `uv run pytest tests/unit/ tests/integration/`
- [X] T034 [US1] Run code quality checks: `uv run ruff check .` and `uv run ruff format --check .`
- [X] T035 [US1] Run coverage check: `uv run pytest --cov=src --cov-report=term-missing` (verify ≥95%)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Add Task with Title Only (Priority: P1)

**Goal**: Enable users to quickly capture tasks with just a title (no description)

**Independent Test**: Navigate to Add Task, enter title, press Enter at description prompt, verify task created with empty description

### Tests for User Story 2

- [X] T036 [P] [US2] Write unit test for validate_description() with empty string in tests/unit/test_validation.py
- [X] T037 [P] [US2] Write unit test for create_task() with empty description in tests/unit/test_task_service.py
- [X] T038 [P] [US2] Write integration test for add task flow with title only in tests/integration/test_add_task_flow.py

### Implementation for User Story 2

- [X] T039 [US2] Verify get_task_description() accepts empty input (press Enter) - should already work from US1
- [X] T040 [US2] Verify create_task() handles empty description correctly - should already work from US1
- [X] T041 [US2] Test sequential ID generation: add task with existing tasks, verify ID = max+1
- [X] T042 [US2] Verify all tests pass: `uv run pytest`
- [X] T043 [US2] Run coverage check: `uv run pytest --cov=src --cov-report=term-missing` (verify 100%)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: Edge Cases & Validation

**Purpose**: Verify boundary conditions and error handling

- [X] T044 [P] Write test for title exactly 200 chars (boundary) in tests/unit/test_validation.py
- [X] T045 [P] Write test for title exactly 201 chars (boundary) in tests/unit/test_validation.py
- [X] T046 [P] Write test for description exactly 1000 chars (boundary) in tests/unit/test_validation.py
- [X] T047 [P] Write test for description exactly 1001 chars (boundary) in tests/unit/test_validation.py
- [X] T048 [P] Write test for whitespace-only title in tests/unit/test_validation.py
- [X] T049 [P] Write test for title with leading/trailing spaces (verify stripping) in tests/unit/test_validation.py
- [X] T050 [P] Write test for description with leading/trailing spaces (verify stripping) in tests/unit/test_validation.py
- [X] T051 [P] Write test for first task gets ID 1 in tests/unit/test_task_service.py
- [X] T052 [P] Write test for timestamps are identical for created_at and updated_at in tests/unit/test_task_service.py
- [X] T053 [P] Write test for multiple validation failures with retry in tests/integration/test_add_task_flow.py
- [X] T054 Verify all edge case tests pass: `uv run pytest`

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T055 [P] Add Google-style docstrings to all functions and classes
- [X] T056 [P] Add type hints to all function parameters and return values
- [X] T057 [P] Verify PEP 8 compliance: `uv run ruff check .` (fix any errors)
- [X] T058 [P] Format code: `uv run ruff format .`
- [X] T059 [P] Optional: Run mypy type checking: `uv run mypy src/ --strict`
- [X] T060 [P] Create README.md with setup instructions (uv init, uv run pytest, uv run python src/main.py)
- [X] T061 Verify final test coverage: `uv run pytest --cov=src --cov-report=html` (100% core logic)
- [X] T062 Manual testing: Run application and test all user flows
- [X] T063 Verify all success criteria from spec.md (SC-001 through SC-007)
- [X] T064 Verify no constitutional violations (no file I/O, no DB, no external deps except pytest)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - MVP implementation
- **User Story 2 (Phase 4)**: Depends on Foundational - Can proceed after US1 or in parallel (mostly verification)
- **Edge Cases (Phase 5)**: Depends on US1 and US2 completion
- **Polish (Phase 6)**: Depends on all implementation complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Mostly reuses US1 implementation, adds empty description tests

### Within Each User Story

- Tests (T012-T022 for US1) MUST be written and FAIL before implementation
- Validation functions before prompt functions
- Service functions before UI integration
- Integration tests after all components implemented
- Story complete before moving to next phase

### Parallel Opportunities

- **Setup phase**: All tasks marked [P] can run in parallel (T002, T003, T005, T006)
- **Foundational phase**: All tasks are sequential (build on each other)
- **User Story 1 tests**: All test tasks marked [P] (T012-T022) can run in parallel
- **User Story 1 implementation**: Validation functions (T023, T024) can run in parallel, prompts (T025, T026) can run in parallel
- **Edge cases**: All test tasks marked [P] (T044-T052) can run in parallel
- **Polish**: All tasks marked [P] (T055-T060) can run in parallel

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all unit tests for User Story 1 together (TDD - Red phase):
Task T012: "Write unit test for Task dataclass instantiation"
Task T013: "Write unit test for Task.generate_timestamp() format"
Task T014: "Write unit test for validate_title() with valid input"
Task T015: "Write unit test for validate_title() with empty input"
Task T016: "Write unit test for validate_title() with >200 chars"
Task T017: "Write unit test for validate_description() with valid input"
Task T018: "Write unit test for validate_description() with >1000 chars"
Task T019: "Write unit test for create_task() function"
Task T020: "Write unit test for generate_next_id() with empty storage"
Task T021: "Write unit test for generate_next_id() with existing tasks"
Task T022: "Write integration test for complete add task flow"

# Then launch validation implementations together (Green phase):
Task T023: "Implement validate_title() function"
Task T024: "Implement validate_description() function"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (6 tasks)
2. Complete Phase 2: Foundational (5 tasks - CRITICAL blocking)
3. Complete Phase 3: User Story 1 (24 tasks - tests + implementation)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Demo/review before proceeding

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (11 tasks)
2. Add User Story 1 → Test independently → Demo (MVP with 35 tasks total!)
3. Add User Story 2 → Test independently → Demo (43 tasks total)
4. Add Edge Cases → Comprehensive validation (54 tasks total)
5. Polish → Production ready (64 tasks total)
6. Each phase adds value without breaking previous functionality

### TDD Workflow (Test-Driven Development)

For each user story phase:

1. **Red Phase**: Write all tests first (tasks marked with "Write unit test...")
   - Run `uv run pytest` - tests should FAIL
2. **Green Phase**: Implement code to pass tests (tasks marked with "Implement...")
   - Run `uv run pytest` - tests should PASS
3. **Refactor Phase**: Clean up code while keeping tests green
   - Run quality checks (ruff, coverage)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability (US1, US2)
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD principle)
- Commit after each logical group or checkpoint
- Stop at any checkpoint to validate story independently
- Total tasks: 64 (11 setup/foundational + 24 US1 + 8 US2 + 11 edge cases + 10 polish)
- MVP scope: 35 tasks (setup + foundational + US1)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
