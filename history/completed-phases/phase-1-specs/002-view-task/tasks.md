---
description: "Task breakdown for View Task feature implementation"
---

# Tasks: View Task

**Input**: Design documents from `/specs/002-view-task/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are included per constitution requirement (100% coverage mandate)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md structure decision)
- Extending existing files: TaskService (src/services/task_service.py), prompts (src/ui/prompts.py), main (src/main.py)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing structure and prepare for view feature extension

Since the project structure already exists from feature 001-add-task, this phase focuses on validation and preparation.

- [x] T001 Verify project structure matches plan.md (src/, tests/, models/, services/, ui/)
- [x] T002 Review existing TaskService in src/services/task_service.py to understand extension points
- [x] T003 Review existing prompts in src/ui/prompts.py to understand display patterns

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

For this feature, foundational work is minimal since we're extending existing infrastructure:

- [x] T004 Add error message constants for view operations to src/constants.py (ERROR 101, 102, 103)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View All Tasks in List Format (Priority: P1) 🎯 MVP

**Goal**: Display all tasks with ID, completion indicator, and title in a formatted list with pagination support

**Independent Test**: Navigate to "View Tasks" menu option and verify all existing tasks display with correct format, completion indicators work, pagination triggers every 20 tasks, and empty list shows appropriate message

**Acceptance Scenarios** (from spec.md):
1. Given 3 tasks exist, when user selects "View Tasks", then all 3 tasks display with ID, completion indicator [ ] or [X], title, and task count summary
2. Given task list is empty, when user selects "View Tasks", then system displays "No tasks found." and returns to main menu

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T005 [P] [US1] Unit test for get_all_tasks() in tests/unit/test_task_service.py (test empty list, 1 task, multiple tasks, order preservation)
- [x] T006 [P] [US1] Unit test for display_task_list() in tests/unit/test_prompts.py (test empty list message, completion indicators, pagination at 20/21/40 tasks, task count display)
- [x] T007 [US1] Integration test for view tasks flow in tests/integration/test_view_task_flow.py (test end-to-end: menu selection → display → return to menu)

### Implementation for User Story 1

- [x] T008 [US1] Implement get_all_tasks() method in src/services/task_service.py (return copy of task list)
- [x] T009 [US1] Implement display_task_list() function in src/ui/prompts.py (format list with indicators, pagination, count)
- [x] T010 [US1] Add "View Tasks" menu option (option 2) to main menu in src/main.py
- [x] T011 [US1] Implement view_tasks_handler() in src/main.py (call service, display results, handle empty list)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can view all tasks in list format with pagination

---

## Phase 4: User Story 2 - View Single Task Details (Priority: P2)

**Goal**: Display complete details for a specific task by ID with comprehensive validation and error handling

**Independent Test**: Select "View Task Details", enter valid task ID, verify all 6 fields display with labels; test invalid inputs (non-numeric, zero, negative, non-existent ID) show correct error messages

**Acceptance Scenarios** (from spec.md):
1. Given task with ID 2 exists with all fields populated, when user enters ID "2", then all fields display with labels (ID, Title, Description, Completed, Created At, Updated At)
2. Given task with ID 5 has empty description, when user views details, then description shows "(No description)"
3. Given task ID 99 doesn't exist, when user enters "99", then ERROR 101 displays and returns to menu
4. Given user enters "abc" (non-numeric), then ERROR 102 displays and re-prompts
5. Given user enters "0" or negative, then ERROR 103 displays and re-prompts

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T012 [P] [US2] Unit test for get_task_by_id() in tests/unit/test_task_service.py (test valid ID, non-existent ID → ERROR 101, zero/negative → ERROR 103)
- [x] T013 [P] [US2] Unit test for display_task_details() in tests/unit/test_prompts.py (test all fields display, empty description placeholder, completed Yes/No format, timestamp display)
- [x] T014 [P] [US2] Unit test for prompt_for_task_id() in tests/unit/test_prompts.py (test valid input, non-numeric → ERROR 102, zero/negative → ERROR 103)
- [x] T015 [US2] Integration test for view task details flow in tests/integration/test_view_task_flow.py (test end-to-end with valid/invalid inputs, error recovery)

### Implementation for User Story 2

- [x] T016 [US2] Implement get_task_by_id() method in src/services/task_service.py (validate positive, search list, raise errors 101/103)
- [x] T017 [P] [US2] Implement display_task_details() function in src/ui/prompts.py (format all 6 fields with labels, empty description handling)
- [x] T018 [P] [US2] Implement prompt_for_task_id() function in src/ui/prompts.py (validate numeric input, validate positive, raise errors 102/103)
- [x] T019 [US2] Add "View Task Details" menu option (option 3) to main menu in src/main.py
- [x] T020 [US2] Implement view_task_details_handler() in src/main.py (prompt for ID, call service, display details, handle errors)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - complete view functionality is available

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Quality assurance and final validation across all user stories

- [x] T021 [P] Run full test suite with coverage: uv run pytest --cov=src --cov-report=term-missing
- [x] T022 Verify 100% test coverage on all view feature code (TaskService.get_all_tasks, get_task_by_id, all UI functions)
- [x] T023 [P] Run linter: uv run ruff check . (verify zero errors)
- [x] T024 [P] Run formatter check: uv run ruff format --check . (verify code is formatted)
- [ ] T025 Manual testing: Empty task list scenario (verify "No tasks found." message)
- [ ] T026 Manual testing: Single task scenario (verify list and detail views)
- [ ] T027 Manual testing: 20 tasks scenario (verify no pagination prompt)
- [ ] T028 Manual testing: 21+ tasks scenario (verify pagination prompt appears)
- [ ] T029 Manual testing: All error scenarios (ERROR 101, 102, 103 with exact message verification)
- [ ] T030 Manual testing: Special characters and Unicode in titles/descriptions (emojis, newlines, tabs)
- [ ] T031 Validate quickstart.md accuracy by following user workflows
- [ ] T032 Update README.md if new menu options need documentation
- [ ] T033 Verify constitution compliance: CLI-only, in-memory, no new dependencies, type hints present
- [ ] T034 Final regression test: Verify 001-add-task feature still works (view should not break add)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-4)**: All depend on Foundational phase completion
  - User Story 1 (Phase 3) can proceed after foundational
  - User Story 2 (Phase 4) can proceed after foundational (independent of US1)
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 (doesn't use list view)

**Key Insight**: US1 and US2 are completely independent. They can be developed in parallel by different developers after foundational phase completes.

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Service methods before UI functions (UI depends on service)
- UI functions before main.py handlers (handlers depend on UI)
- All tasks within a story before moving to next story

### Parallel Opportunities

**Within Setup (Phase 1)**:
- All review tasks (T001, T002, T003) can run in parallel

**Within User Story 1 Tests**:
- T005, T006, T007 can run in parallel (different test files)

**Within User Story 1 Implementation**:
- T008 and T009 can run in parallel (different files: task_service.py vs prompts.py)
- T010 and T011 both modify main.py, so must run sequentially

**Within User Story 2 Tests**:
- T012, T013, T014 can run in parallel (different test files or test functions)

**Within User Story 2 Implementation**:
- T017 and T018 can run in parallel (different functions in prompts.py)
- T016, T017, T018 can all run in parallel (T016 in task_service.py, T017/T018 in prompts.py)
- T019 and T020 both modify main.py, so must run sequentially

**Across User Stories**:
- **After foundational completes**: US1 (Phase 3) and US2 (Phase 4) can run in parallel

**Within Polish (Phase 5)**:
- T021, T023, T024 can run in parallel (different tools)
- Manual testing tasks (T025-T030) can be distributed in parallel
- T033 and T034 can run in parallel

---

## Parallel Example: User Story 1

```bash
# After Foundational phase completes, launch all US1 tests together:
Task: "Unit test for get_all_tasks() in tests/unit/test_task_service.py"
Task: "Unit test for display_task_list() in tests/unit/test_prompts.py"
Task: "Integration test for view tasks flow in tests/integration/test_view_task_flow.py"

# Then launch US1 implementation tasks in parallel:
Task: "Implement get_all_tasks() method in src/services/task_service.py"
Task: "Implement display_task_list() function in src/ui/prompts.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch all US2 tests together:
Task: "Unit test for get_task_by_id() in tests/unit/test_task_service.py"
Task: "Unit test for display_task_details() in tests/unit/test_prompts.py"
Task: "Unit test for prompt_for_task_id() in tests/unit/test_prompts.py"

# Then launch US2 implementation tasks in parallel:
Task: "Implement get_task_by_id() method in src/services/task_service.py"
Task: "Implement display_task_details() function in src/ui/prompts.py"
Task: "Implement prompt_for_task_id() function in src/ui/prompts.py"
```

---

## Cross-Story Parallel Example

```bash
# After Foundational phase (T004) completes, both stories can start in parallel:

# Developer A works on User Story 1:
Task: "Unit test for get_all_tasks() in tests/unit/test_task_service.py"
Task: "Unit test for display_task_list() in tests/unit/test_prompts.py"
Task: "Implement get_all_tasks() method in src/services/task_service.py"
Task: "Implement display_task_list() function in src/ui/prompts.py"
Task: "Add 'View Tasks' menu option to main.py"

# Developer B works on User Story 2 (simultaneously):
Task: "Unit test for get_task_by_id() in tests/unit/test_task_service.py"
Task: "Unit test for display_task_details() in tests/unit/test_prompts.py"
Task: "Implement get_task_by_id() method in src/services/task_service.py"
Task: "Implement display_task_details() function in src/ui/prompts.py"
Task: "Add 'View Task Details' menu option to main.py"

# Merge strategy: Both stories modify main.py, so coordinate menu option numbers or merge sequentially
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004)
3. Complete Phase 3: User Story 1 (T005-T011)
4. **STOP and VALIDATE**: Test US1 independently
   - View empty list → "No tasks found."
   - Add task, view list → 1 task displays
   - Add 25 tasks, view list → pagination works
5. Run basic polish (T021-T024)
6. Deploy/demo MVP (View All Tasks feature working)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **Deploy/Demo (MVP!)**
   - Users can now view all their tasks
3. Add User Story 2 → Test independently → **Deploy/Demo**
   - Users can now view detailed task information
4. Complete Polish → Final validation → **Deploy/Demo (Complete Feature)**
   - All quality gates passed, ready for production

### Parallel Team Strategy

With 2 developers:

1. **Together**: Complete Setup (Phase 1) and Foundational (Phase 2)
2. **Split after foundational**:
   - **Developer A**: User Story 1 (T005-T011) - List view
   - **Developer B**: User Story 2 (T012-T020) - Detail view
3. **Coordinate**: main.py changes (ensure menu options don't conflict)
4. **Together**: Polish and validation (Phase 5)

---

## Task Summary

- **Total Tasks**: 34
- **Setup Tasks**: 3
- **Foundational Tasks**: 1
- **User Story 1 Tasks**: 7 (3 tests + 4 implementation)
- **User Story 2 Tasks**: 9 (4 tests + 5 implementation)
- **Polish Tasks**: 14
- **Parallelizable Tasks**: 18 (marked with [P])
- **User Stories**: 2 (both independently testable)

### Task Count by Phase

| Phase | Task Count | Parallelizable |
|-------|------------|----------------|
| Phase 1: Setup | 3 | 3 |
| Phase 2: Foundational | 1 | 0 |
| Phase 3: User Story 1 | 7 | 3 |
| Phase 4: User Story 2 | 9 | 6 |
| Phase 5: Polish | 14 | 6 |

### Suggested MVP Scope

**Minimum Viable Product**: User Story 1 only (View All Tasks)
- Task range: T001-T011 + basic polish (T021-T024)
- Total MVP tasks: 15
- Delivers core value: Users can see their task list

**Full Feature**: User Stories 1 + 2
- Task range: T001-T034
- Total tasks: 34
- Delivers complete view functionality

---

## Notes

- [P] tasks = different files or different functions, no dependencies
- [US1] or [US2] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Tests must fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution compliance verified in polish phase (T033)
- Regression testing ensures existing features not broken (T034)
- Special attention to error message exactness (ERROR 101, 102, 103)
- Pagination implementation tested with 20, 21, and 40+ task scenarios
