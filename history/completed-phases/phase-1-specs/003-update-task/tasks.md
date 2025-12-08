# Tasks: Update Task

**Input**: Design documents from `/specs/003-update-task/`
**Prerequisites**: plan.md, spec.md (user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included per pytest requirement with 100% coverage goal

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths assume single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add constants and prepare infrastructure for update feature

- [X] T001 Add ERROR_INVALID_OPTION constant (104) to src/constants.py
- [X] T002 [P] Add MSG_TASK_UPDATED success message constant to src/constants.py
- [X] T003 [P] Add PROMPT_FIELD_SELECTION constant to src/constants.py
- [X] T004 [P] Add PROMPT_NEW_TITLE constant to src/constants.py
- [X] T005 [P] Add PROMPT_NEW_DESCRIPTION constant to src/constants.py

**Checkpoint**: Constants ready for service and UI implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core service layer that MUST be complete before ANY user story UI can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implement update_task() method in src/services/task_service.py with selective parameter handling (new_title, new_description as Optional)
- [X] T007 Write unit test for update_task() with title only update in tests/unit/test_task_service.py
- [X] T008 [P] Write unit test for update_task() with description only update in tests/unit/test_task_service.py
- [X] T009 [P] Write unit test for update_task() with both fields update in tests/unit/test_task_service.py
- [X] T010 [P] Write unit test for update_task() verifying updated_at timestamp changes in tests/unit/test_task_service.py
- [X] T011 [P] Write unit test for update_task() verifying immutable fields preserved (id, completed, created_at) in tests/unit/test_task_service.py
- [X] T012 [P] Write unit test for update_task() with invalid task_id zero (ERROR 103) in tests/unit/test_task_service.py
- [X] T013 [P] Write unit test for update_task() with invalid task_id negative (ERROR 103) in tests/unit/test_task_service.py
- [X] T014 [P] Write unit test for update_task() with non-existent task_id (ERROR 101) in tests/unit/test_task_service.py
- [X] T015 [P] Write unit test for update_task() verifying same instance returned (in-place modification) in tests/unit/test_task_service.py
- [X] T016 [P] Write unit test for update_task() with both None values (timestamp only update) in tests/unit/test_task_service.py

**Checkpoint**: Service layer ready with 100% test coverage - user story UI implementation can now begin in parallel

---

## Phase 3: User Story 1 - Update Task Title and Description (Priority: P1) 🎯 MVP

**Goal**: Enable users to modify both the title and description of an existing task in under 30 seconds

**Independent Test**: Navigate to Update Task menu, enter valid task ID, provide new title and description, verify task updated with new values and updated_at timestamp changes

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T017 [P] [US1] Write unit test for display_field_selection_menu() output format in tests/unit/test_prompts.py
- [X] T018 [P] [US1] Write unit test for prompt_for_field_choice() with valid choices (1, 2, 3) in tests/unit/test_prompts.py
- [X] T019 [P] [US1] Write unit test for prompt_for_field_choice() with invalid option (ERROR 104) and re-prompt in tests/unit/test_prompts.py
- [X] T020 [P] [US1] Write unit test for get_new_task_title() with valid input in tests/unit/test_prompts.py
- [X] T021 [P] [US1] Write unit test for get_new_task_title() with empty input (ERROR 001) and re-prompt in tests/unit/test_prompts.py
- [X] T022 [P] [US1] Write unit test for get_new_task_title() with >200 chars (ERROR 002) and re-prompt in tests/unit/test_prompts.py
- [X] T023 [P] [US1] Write unit test for get_new_task_description() with valid input in tests/unit/test_prompts.py
- [X] T024 [P] [US1] Write unit test for get_new_task_description() with empty input (valid) in tests/unit/test_prompts.py
- [X] T025 [P] [US1] Write unit test for get_new_task_description() with >1000 chars (ERROR 003) and re-prompt in tests/unit/test_prompts.py
- [X] T026 [P] [US1] Write unit test for update_task_prompt() complete flow option 3 (both fields) in tests/unit/test_prompts.py
- [X] T027 [P] [US1] Write unit test for update_task_prompt() with task not found (ERROR 101) in tests/unit/test_prompts.py

### Implementation for User Story 1

- [X] T028 [P] [US1] Implement display_field_selection_menu() function in src/ui/prompts.py
- [X] T029 [P] [US1] Implement prompt_for_field_choice() function with validation loop in src/ui/prompts.py
- [X] T030 [P] [US1] Implement get_new_task_title() function reusing validate_title() in src/ui/prompts.py
- [X] T031 [P] [US1] Implement get_new_task_description() function reusing validate_description() in src/ui/prompts.py
- [X] T032 [US1] Implement update_task_prompt() orchestrator for option 3 (both fields) flow in src/ui/prompts.py (depends on T028-T031)
- [X] T033 [US1] Add menu option 3 "Update Task" to main menu display in src/main.py
- [X] T034 [US1] Add menu choice handler for option 3 calling update_task_prompt() in src/main.py
- [X] T035 [US1] Write integration test for main menu option 3 calls update_task_prompt() in tests/unit/test_main.py

**Checkpoint**: User Story 1 complete - users can update both title and description together (option 3). Manual test: Select Update Task → enter ID → select option 3 → enter new title and description → verify success message and updated values

---

## Phase 4: User Story 2 - Update Task with Selective Field Updates (Priority: P1)

**Goal**: Enable users to update only the title or only the description without modifying the other field

**Independent Test**: Navigate to Update Task, enter task ID, select option 1 (title only), provide new title, verify only title changes and description remains unchanged

### Tests for User Story 2

- [X] T036 [P] [US2] Write unit test for update_task_prompt() complete flow option 1 (title only) in tests/unit/test_prompts.py
- [X] T037 [P] [US2] Write unit test for update_task_prompt() complete flow option 2 (description only) in tests/unit/test_prompts.py
- [X] T038 [P] [US2] Write unit test verifying title unchanged when option 2 selected in tests/unit/test_prompts.py
- [X] T039 [P] [US2] Write unit test verifying description unchanged when option 1 selected in tests/unit/test_prompts.py

### Implementation for User Story 2

- [X] T040 [US2] Extend update_task_prompt() to handle option 1 (title only) branch in src/ui/prompts.py
- [X] T041 [US2] Extend update_task_prompt() to handle option 2 (description only) branch in src/ui/prompts.py
- [X] T042 [US2] Verify correct None parameter passing for selective updates (option 1: new_description=None, option 2: new_title=None) in src/ui/prompts.py

**Checkpoint**: User Stories 1 AND 2 complete - users can selectively update title only, description only, or both. Manual test: Update task with option 1 → verify description preserved; option 2 → verify title preserved

---

## Phase 5: User Story 3 - Handle Invalid Update Attempts (Priority: P1)

**Goal**: Provide clear error feedback for invalid inputs without crashing

**Independent Test**: Attempt updates with non-existent task ID, invalid input types, and data exceeding validation limits, verify appropriate error messages shown

### Tests for User Story 3

- [X] T043 [P] [US3] Write unit test for invalid task ID input (non-numeric, ERROR 102) in tests/unit/test_prompts.py
- [X] T044 [P] [US3] Write unit test for task ID zero (ERROR 103) in tests/unit/test_prompts.py
- [X] T045 [P] [US3] Write unit test for task ID negative (ERROR 103) in tests/unit/test_prompts.py
- [X] T046 [P] [US3] Write unit test for invalid field selection (0, 4, "abc") with ERROR 104 in tests/unit/test_prompts.py
- [X] T047 [P] [US3] Write unit test for whitespace-only title (ERROR 001) in tests/unit/test_prompts.py
- [X] T048 [P] [US3] Write unit test for title boundary (exactly 200 chars - valid) in tests/unit/test_prompts.py
- [X] T049 [P] [US3] Write unit test for title boundary (201 chars - ERROR 002) in tests/unit/test_prompts.py
- [X] T050 [P] [US3] Write unit test for description boundary (exactly 1000 chars - valid) in tests/unit/test_prompts.py
- [X] T051 [P] [US3] Write unit test for description boundary (1001 chars - ERROR 003) in tests/unit/test_prompts.py

### Implementation for User Story 3

- [X] T052 [US3] Verify all error handling paths in update_task_prompt() return to main menu after displaying errors in src/ui/prompts.py
- [X] T053 [US3] Verify all validation re-prompt loops use existing validate_title(), validate_description(), prompt_for_task_id() functions in src/ui/prompts.py
- [X] T054 [US3] Add error handling for ValueError from get_task_by_id() with ERROR 101 message display in src/ui/prompts.py

**Checkpoint**: All three user stories complete and independently functional. All error paths tested and verified to not crash.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, coverage verification, and code quality

- [X] T055 [P] Run pytest --cov=src --cov-report=term-missing to verify 100% coverage
- [X] T056 [P] Run ruff check . to verify code quality standards
- [X] T057 [P] Run ruff format --check . to verify formatting compliance
- [X] T058 Manual testing following quickstart.md test script for all acceptance scenarios
- [X] T059 Verify all error codes (001-003, 101-104) match spec.md exactly
- [X] T060 [P] Verify constitution compliance (all 7 principles checked in plan.md)
- [X] T061 Code review focusing on immutability guarantees (id, completed, created_at never modified)
- [X] T062 Verify updated_at timestamp changes on every update operation across all manual tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001-T005) completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational (T006-T016) completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3)
- **Polish (Phase 6)**: Depends on all user stories (US1, US2, US3) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Depends on User Story 1 implementation (T032) - extends update_task_prompt() with options 1 and 2
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Tests existing error paths, minimal new implementation

### Within Each User Story

- Tests (T017-T027 for US1, T036-T039 for US2, T043-T051 for US3) MUST be written and FAIL before implementation
- UI helper functions (T028-T031) can run in parallel
- Orchestrator function (T032) depends on helper functions completion
- Main menu integration (T033-T034) depends on orchestrator completion
- Error handling verification (T052-T054) depends on US1 orchestrator being implemented

### Parallel Opportunities

- **Setup (Phase 1)**: All constants (T002-T005) can be added in parallel after T001
- **Foundational (Phase 2)**: All unit tests (T007-T016) can be written in parallel after service implementation (T006)
- **User Story 1 Tests**: All test tasks (T017-T027) can be written in parallel
- **User Story 1 Implementation**: Helper functions (T028-T031) can be implemented in parallel
- **User Story 2 Tests**: All test tasks (T036-T039) can be written in parallel
- **User Story 3 Tests**: All test tasks (T043-T051) can be written in parallel
- **Polish (Phase 6)**: T055-T057 and T060 can run in parallel

---

## Parallel Example: User Story 1 Implementation

```bash
# Launch all tests for User Story 1 together:
Task: "Write unit test for display_field_selection_menu() output format in tests/unit/test_prompts.py"
Task: "Write unit test for prompt_for_field_choice() with valid choices in tests/unit/test_prompts.py"
Task: "Write unit test for get_new_task_title() with valid input in tests/unit/test_prompts.py"
Task: "Write unit test for get_new_task_description() with valid input in tests/unit/test_prompts.py"

# Launch all UI helper functions for User Story 1 together (after tests fail):
Task: "Implement display_field_selection_menu() function in src/ui/prompts.py"
Task: "Implement prompt_for_field_choice() function in src/ui/prompts.py"
Task: "Implement get_new_task_title() function in src/ui/prompts.py"
Task: "Implement get_new_task_description() function in src/ui/prompts.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only - Option 3: Both Fields)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T016) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T017-T035)
4. **STOP and VALIDATE**: Test updating both title and description independently
5. Verify acceptance scenario: User selects "Update Task", enters valid ID, chooses option 3, provides new title and description, sees "Task updated successfully."

### Incremental Delivery

1. Complete Setup + Foundational → Service layer ready with 100% coverage
2. Add User Story 1 (option 3: both fields) → Test independently → Users can update both fields (MVP!)
3. Add User Story 2 (options 1 & 2: selective updates) → Test independently → Users can update individual fields
4. Add User Story 3 (error handling validation) → Test independently → Robust error handling verified
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T016)
2. Once Foundational is done:
   - Developer A: User Story 1 (T017-T035)
   - Developer B: User Story 3 (T043-T054) - can work in parallel since it's mostly test coverage
3. After User Story 1 complete:
   - Developer A or C: User Story 2 (T036-T042) - extends US1 implementation
4. Stories integrate independently with main menu

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach per pytest requirement)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All validation reuses existing functions from 001-add-task and 002-view-task
- Service layer update_task() reuses get_task_by_id() for DRY and consistent error handling
- updated_at timestamp MUST change on every update regardless of which fields are modified
- Immutability guarantees: id, completed, created_at are NEVER modified by update operations
- Error codes: 001-003 (reused from add-task), 101-103 (reused from view-task), 104 (new for update-task)
