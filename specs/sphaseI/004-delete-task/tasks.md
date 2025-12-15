# Implementation Tasks: Delete Task

**Feature**: Delete Task (004-delete-task)
**Branch**: `004-delete-task`
**Created**: 2025-12-06
**Status**: Ready for Implementation

## Overview

This document defines the implementation tasks for the Delete Task feature, organized by user story to enable independent development and testing. Each user story can be implemented as a complete, testable increment.

**User Stories**:
- **User Story 1** (P1): Delete Single Task by ID - Core deletion functionality
- **User Story 2** (P1): Cancel Deletion Operation - Safety confirmation workflow
- **User Story 3** (P1): Handle Invalid Deletion Attempts - Error handling and validation

**Implementation Strategy**: All three user stories are P1 priority and tightly coupled (share validation, confirmation, and error handling logic). They will be implemented together as a single cohesive feature.

---

## Phase 1: Setup & Constants

**Goal**: Prepare constants and project structure for delete functionality

**Independent Test Criteria**: N/A (foundational setup)

### Tasks

- [X] T001 Add ERROR_INVALID_CONFIRMATION constant to src/constants.py
- [X] T002 Add MSG_TASK_DELETED constant to src/constants.py
- [X] T003 Add MSG_DELETION_CANCELED constant to src/constants.py

**Completion Criteria**:
- All 3 new constants defined in `src/constants.py`
- Constants follow existing naming convention (UPPER_SNAKE_CASE)
- Error message matches spec: "ERROR 105: Invalid input. Please enter Y or N."
- Success message matches spec: "Task deleted successfully."
- Cancellation message matches spec: "Deletion canceled."

---

## Phase 2: Business Logic Layer

**Goal**: Implement core deletion logic in service layer

**Independent Test Criteria**:
- Can delete existing task by ID (task removed from storage)
- Deletion preserves other task IDs (no renumbering)
- Raises ValueError for invalid task ID (ERROR 103)
- Raises ValueError for non-existent task ID (ERROR 101)

### Tasks

- [X] T004 [US1] [US2] [US3] Implement delete_task() function in src/services/task_service.py

**Function Specification**:
```python
def delete_task(task_id: int) -> Task:
    """Delete a task from storage by its unique ID.

    Args:
        task_id: The unique identifier of the task to delete

    Returns:
        The deleted Task object (for use in confirmation message)

    Raises:
        ValueError: If task_id <= 0 (ERROR 103)
        ValueError: If no task with task_id exists (ERROR 101)
    """
    # Reuse get_task_by_id() for validation and retrieval
    task = get_task_by_id(task_id)

    # Remove task from storage (no renumbering)
    _task_storage.remove(task)

    # Return deleted task for UI confirmation message
    return task
```

**Acceptance Criteria**:
- Function reuses `get_task_by_id()` for validation (DRY principle)
- Uses `list.remove(task)` (not index-based deletion)
- Returns deleted Task object for title display
- No ID renumbering logic (FR-017)
- Includes type hints and Google-style docstring
- Passes ruff formatting and linting

---

## Phase 3: User Interface Layer - Confirmation Prompt

**Goal**: Implement Y/N confirmation prompt with validation

**Independent Test Criteria**:
- Accepts "Y" and "y" (returns True)
- Accepts "N" and "n" (returns False)
- Strips leading/trailing whitespace
- Rejects invalid inputs with ERROR 105 and re-prompts
- Displays task title in prompt for context

### Tasks

- [X] T005 [US1] [US2] [US3] Implement prompt_for_delete_confirmation() function in src/ui/prompts.py

**Function Specification**:
```python
def prompt_for_delete_confirmation(task_title: str) -> bool:
    """Prompt user to confirm task deletion with Y/N response.

    Args:
        task_title: Title of the task to be deleted (for context)

    Returns:
        True if user confirms deletion (Y/y), False if user cancels (N/n)
    """
    prompt = f"Delete task '{task_title}'? (Y/N): "

    while True:
        response = input(prompt).strip().upper()

        if response == "Y":
            return True

        if response == "N":
            return False

        print(ERROR_INVALID_CONFIRMATION)
```

**Acceptance Criteria**:
- Case-insensitive (accepts Y/y/N/n per FR-010, FR-013, FR-014)
- Strips whitespace before validation (FR-012)
- Displays task title in prompt (FR-008)
- Validation loop for invalid inputs (FR-011)
- Uses ERROR_INVALID_CONFIRMATION constant
- Includes type hints and Google-style docstring

- [X] T006 Add ERROR_INVALID_CONFIRMATION import to src/ui/prompts.py

**Acceptance Criteria**:
- Import added to existing constants import block
- Follows existing import organization pattern

---

## Phase 4: User Interface Layer - Delete Workflow

**Goal**: Orchestrate complete delete workflow with all user stories

**Independent Test Criteria**:
- **US1**: Valid ID + Y confirmation → task deleted, success message shown
- **US2**: Valid ID + N response → task preserved, cancellation message shown
- **US3**: Invalid ID (non-numeric, zero, negative, non-existent) → error message, no confirmation
- Returns to main menu after all outcomes

### Tasks

- [X] T007 [US1] [US2] [US3] Implement delete_task_prompt() function in src/ui/prompts.py

**Function Specification**:
```python
def delete_task_prompt() -> None:
    """Orchestrate the complete delete task workflow with user interaction."""
    try:
        # Step 1: Get and validate task ID (ERROR 102, 103)
        task_id = prompt_for_task_id()

        # Step 2: Retrieve task and validate existence (ERROR 101)
        task = get_task_by_id(task_id)

    except ValueError as e:
        # Handle ID validation errors - return to menu
        print(str(e))
        return

    # Step 3: Get user confirmation with task title
    confirmed = prompt_for_delete_confirmation(task.title)

    # Step 4: Execute deletion or cancellation
    if confirmed:
        delete_task(task_id)
        print(MSG_TASK_DELETED)
    else:
        print(MSG_DELETION_CANCELED)
```

**Acceptance Criteria**:
- Reuses `prompt_for_task_id()` for ID input (existing function)
- Catches ValueError for ERROR 101/102/103
- Returns to menu on error without showing confirmation (FR-007)
- Displays success message on deletion (FR-016)
- Displays cancellation message on cancel (FR-020)
- Includes type hints and Google-style docstring

- [X] T008 Add delete_task import from task_service to src/ui/prompts.py
- [X] T009 Add MSG_TASK_DELETED and MSG_DELETION_CANCELED imports to src/ui/prompts.py

**Acceptance Criteria**:
- Imports added to existing import blocks
- Follows existing import organization pattern (services, then constants)

---

## Phase 5: Main Menu Integration

**Goal**: Add "Delete Task" option to main menu

**Independent Test Criteria**:
- Menu displays option 4: "Delete Task"
- Selecting option 4 calls delete_task_prompt()
- Mark Complete renumbered to option 5
- Exit renumbered to option 6

### Tasks

- [X] T010 [US1] [US2] [US3] Add delete_task_prompt import to src/main.py
- [X] T011 [US1] [US2] [US3] Add menu option 4 "Delete Task" to main menu in src/main.py
- [X] T012 [US1] [US2] [US3] Renumber Mark Complete to option 5 in src/main.py
- [X] T013 [US1] [US2] [US3] Renumber Exit to option 6 in src/main.py
- [X] T014 [US1] [US2] [US3] Add choice == "4" handler calling delete_task_prompt() in src/main.py

**Acceptance Criteria**:
- Import statement includes `delete_task_prompt`
- Menu displays: "4. Delete Task"
- Mark Complete displays as: "5. Mark Complete"
- Exit displays as: "6. Exit"
- Choice "4" calls `delete_task_prompt()`
- Choice "5" calls `mark_complete_prompt()` (renumbered from "4")
- Choice "6" breaks loop (renumbered from "5")

---

## Phase 6: Automated Testing - Unit Tests (Service Layer)

**Goal**: Verify delete_task() business logic with unit tests

**Independent Test Criteria**:
- All unit tests pass
- Code coverage ≥ 95% for delete_task() function

### Tasks

- [X] T015 [P] [US1] Create test class TestDeleteTask in tests/unit/test_task_service.py
- [X] T016 [P] [US1] Write test_delete_existing_task in tests/unit/test_task_service.py
- [X] T017 [P] [US3] Write test_delete_non_existent_task in tests/unit/test_task_service.py
- [X] T018 [P] [US3] Write test_delete_with_invalid_id_zero in tests/unit/test_task_service.py
- [X] T019 [P] [US3] Write test_delete_with_negative_id in tests/unit/test_task_service.py
- [X] T020 [P] [US1] Write test_delete_last_remaining_task in tests/unit/test_task_service.py
- [X] T021 [P] [US1] Write test_delete_does_not_renumber_ids in tests/unit/test_task_service.py

**Test Specifications**:

**T016 - test_delete_existing_task**:
- Setup: Create 3 tasks with IDs [1, 2, 3]
- Action: `deleted = delete_task(task_id=2)`
- Assert: Task 2 removed, tasks 1 and 3 unchanged, returns deleted task

**T017 - test_delete_non_existent_task**:
- Setup: Create tasks with IDs [1, 2]
- Action: `delete_task(task_id=99)`
- Assert: Raises ValueError with "ERROR 101"

**T018 - test_delete_with_invalid_id_zero**:
- Action: `delete_task(task_id=0)`
- Assert: Raises ValueError with "ERROR 103"

**T019 - test_delete_with_negative_id**:
- Action: `delete_task(task_id=-5)`
- Assert: Raises ValueError with "ERROR 103"

**T020 - test_delete_last_remaining_task**:
- Setup: Create 1 task with ID 5
- Action: `delete_task(task_id=5)`
- Assert: Returns deleted task, _task_storage is empty list

**T021 - test_delete_does_not_renumber_ids**:
- Setup: Create tasks with IDs [1, 2, 3, 4, 5]
- Action: `delete_task(task_id=3)`
- Assert: Remaining IDs are [1, 2, 4, 5] (not [1, 2, 3, 4])

**Acceptance Criteria**:
- All 6 test cases implemented
- Tests use pytest fixtures for setup/teardown
- Error messages validated (ERROR 101, 103)
- ID preservation tested (FR-017)

---

## Phase 7: Automated Testing - Unit Tests (UI Layer)

**Goal**: Verify confirmation prompt with unit tests

**Independent Test Criteria**:
- All unit tests pass
- Code coverage ≥ 95% for prompt_for_delete_confirmation()

### Tasks

- [X] T022 [P] Create test class TestPromptForDeleteConfirmation in tests/unit/test_prompts.py
- [X] T023 [P] [US1] [US2] Write test_confirm_with_uppercase_y in tests/unit/test_prompts.py
- [X] T024 [P] [US1] [US2] Write test_confirm_with_lowercase_y in tests/unit/test_prompts.py
- [X] T025 [P] [US2] Write test_cancel_with_uppercase_n in tests/unit/test_prompts.py
- [X] T026 [P] [US2] Write test_cancel_with_lowercase_n in tests/unit/test_prompts.py
- [X] T027 [P] [US2] Write test_strips_whitespace in tests/unit/test_prompts.py
- [X] T028 [P] [US2] [US3] Write test_invalid_then_valid_response in tests/unit/test_prompts.py

**Test Specifications**:

**T023 - test_confirm_with_uppercase_y**:
- Mock input() to return "Y"
- Assert: Returns True

**T024 - test_confirm_with_lowercase_y**:
- Mock input() to return "y"
- Assert: Returns True

**T025 - test_cancel_with_uppercase_n**:
- Mock input() to return "N"
- Assert: Returns False

**T026 - test_cancel_with_lowercase_n**:
- Mock input() to return "n"
- Assert: Returns False

**T027 - test_strips_whitespace**:
- Mock input() to return " Y "
- Assert: Returns True (whitespace stripped)

**T028 - test_invalid_then_valid_response**:
- Mock input() to return ["maybe", "Y"]
- Assert: Returns True, ERROR 105 printed once

**Acceptance Criteria**:
- All 6 test cases implemented
- Uses monkeypatch for input() mocking
- Uses capsys for error message verification
- Case insensitivity tested (FR-010, FR-013, FR-014)
- Whitespace stripping tested (FR-012)

---

## Phase 8: Automated Testing - Integration Tests

**Goal**: Verify complete delete workflow end-to-end

**Independent Test Criteria**:
- All integration tests pass
- All user stories validated end-to-end
- All acceptance scenarios from spec covered

### Tasks

- [X] T029 Create test file tests/integration/test_delete_task_flow.py
- [X] T030 [P] Create test class TestDeleteTaskFlow in tests/integration/test_delete_task_flow.py
- [X] T031 [P] [US1] Write test_successful_deletion_with_confirmation in tests/integration/test_delete_task_flow.py
- [X] T032 [P] [US2] Write test_cancel_deletion_preserves_task in tests/integration/test_delete_task_flow.py
- [X] T033 [P] [US3] Write test_invalid_id_format_shows_error in tests/integration/test_delete_task_flow.py
- [X] T034 [P] [US3] Write test_zero_id_shows_error in tests/integration/test_delete_task_flow.py
- [X] T035 [P] [US3] Write test_negative_id_shows_error in tests/integration/test_delete_task_flow.py
- [X] T036 [P] [US3] Write test_non_existent_id_shows_error in tests/integration/test_delete_task_flow.py
- [X] T037 [P] [US2] [US3] Write test_invalid_confirmation_then_confirm in tests/integration/test_delete_task_flow.py
- [X] T038 [P] [US3] Write test_delete_from_empty_list in tests/integration/test_delete_task_flow.py

**Test Specifications**:

**T031 - test_successful_deletion_with_confirmation** (US1 Scenario 1):
- Setup: Create 3 tasks
- Mock input: ["2", "Y"]
- Call: delete_task_prompt()
- Assert: Task 2 deleted, "Task deleted successfully." printed

**T032 - test_cancel_deletion_preserves_task** (US2 Scenario 1):
- Setup: Create 2 tasks
- Mock input: ["1", "N"]
- Call: delete_task_prompt()
- Assert: Task 1 preserved, "Deletion canceled." printed

**T033 - test_invalid_id_format_shows_error** (US3 Scenario 2):
- Setup: Create tasks
- Mock input: ["abc"]
- Call: delete_task_prompt()
- Assert: ERROR 102 printed, no confirmation prompt, storage unchanged

**T034 - test_zero_id_shows_error** (US3 Scenario 3):
- Mock input: ["0"]
- Assert: ERROR 103 printed, storage unchanged

**T035 - test_negative_id_shows_error** (US3 Scenario 3):
- Mock input: ["-5"]
- Assert: ERROR 103 printed, storage unchanged

**T036 - test_non_existent_id_shows_error** (US3 Scenario 1):
- Setup: Tasks with IDs [1, 2]
- Mock input: ["99"]
- Assert: ERROR 101 printed, no confirmation prompt shown

**T037 - test_invalid_confirmation_then_confirm** (US2 Scenario 3 + US1):
- Setup: Create task ID 3
- Mock input: ["3", "maybe", "Y"]
- Assert: ERROR 105 printed, task deleted, "Task deleted successfully." printed

**T038 - test_delete_from_empty_list** (US3 Scenario 4):
- Setup: Empty task list
- Mock input: ["1"]
- Assert: ERROR 101 printed

**Acceptance Criteria**:
- All 8 test cases implemented
- Tests use real implementations (no mocking of business logic)
- All error codes verified (ERROR 101, 102, 103, 105)
- Success and cancellation messages verified
- Edge cases tested (empty list, last task)

---

## Phase 9: Quality Assurance & Polish

**Goal**: Ensure code quality and compliance with constitution

**Independent Test Criteria**:
- All tests pass: `uv run pytest`
- Code coverage ≥ 95%: `uv run pytest --cov=src`
- Linting passes: `uv run ruff check .`
- Formatting passes: `uv run ruff format --check .`

### Tasks

- [X] T039 Run full test suite and verify all tests pass
- [X] T040 Run code coverage report and verify ≥95% for delete functionality
- [X] T041 Run ruff linter and fix any errors in delete-related code
- [X] T042 Run ruff formatter and verify code formatting compliance
- [X] T043 Perform manual smoke test: delete task, cancel delete, handle errors

**Manual Smoke Test Checklist** (T043):
1. Start app: `uv run python src/main.py`
2. Add a task (ID 1)
3. Select "4. Delete Task"
4. Enter ID: 1, Confirm: Y → Verify "Task deleted successfully."
5. View tasks → Verify empty list
6. Add 2 tasks (IDs 2, 3)
7. Select "4. Delete Task"
8. Enter ID: 2, Confirm: N → Verify "Deletion canceled."
9. View tasks → Verify both tasks still exist
10. Select "4. Delete Task"
11. Enter ID: abc → Verify ERROR 102
12. Select "4. Delete Task"
13. Enter ID: 0 → Verify ERROR 103
14. Select "4. Delete Task"
15. Enter ID: 99 → Verify ERROR 101

**Acceptance Criteria**:
- `uv run pytest` shows all tests passing
- Coverage report shows ≥95% for src/services/task_service.py and src/ui/prompts.py
- `ruff check .` shows zero errors
- `ruff format --check .` shows code is formatted
- Manual smoke test completes all 15 steps successfully

---

## Dependencies & Execution Order

### User Story Dependencies

All three user stories are **tightly coupled** and must be implemented together:

```
Phase 1 (Setup) → Phase 2 (Business Logic) → Phase 3 (Confirmation) → Phase 4 (Workflow) → Phase 5 (Menu)
                                                                                                    ↓
Phase 6 (Unit Tests - Service) ← ← ← ← ← ← ← Can run in parallel → → → → → → Phase 7 (Unit Tests - UI)
                                                                                                    ↓
                                                                         Phase 8 (Integration Tests)
                                                                                                    ↓
                                                                         Phase 9 (QA & Polish)
```

**Rationale**: US1, US2, and US3 share the same code paths:
- All use `delete_task_prompt()` orchestration
- US1 (delete) and US2 (cancel) both require confirmation prompt
- US3 (error handling) is embedded in validation for US1 and US2

**Independent Testing**: While implementation is coupled, each user story has distinct test scenarios that verify its specific acceptance criteria.

### Phase-Level Dependencies

- **Phase 1** → Blocking for all subsequent phases (constants required)
- **Phase 2** → Blocking for Phase 4, 6 (service layer needed)
- **Phase 3** → Blocking for Phase 4, 7 (confirmation needed)
- **Phase 4** → Blocking for Phase 8 (workflow orchestration needed)
- **Phase 5** → Blocking for manual testing only
- **Phase 6, 7** → Can run in parallel after Phase 2, 3 complete
- **Phase 8** → Requires Phase 4 complete
- **Phase 9** → Requires all previous phases complete

### Parallel Execution Opportunities

**Phase 6 and Phase 7 can run in parallel**:
- Phase 6: Unit tests for service layer (T015-T021)
- Phase 7: Unit tests for UI layer (T022-T028)
- No dependencies between these test phases

**Within Phase 6** (T016-T021): All 6 test tasks can be written in parallel
**Within Phase 7** (T023-T028): All 6 test tasks can be written in parallel
**Within Phase 8** (T031-T038): All 8 test tasks can be written in parallel

---

## Task Summary

**Total Tasks**: 43 tasks across 9 phases

**Breakdown by Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Business Logic): 1 task
- Phase 3 (Confirmation UI): 2 tasks
- Phase 4 (Workflow UI): 3 tasks
- Phase 5 (Menu Integration): 5 tasks
- Phase 6 (Unit Tests - Service): 7 tasks
- Phase 7 (Unit Tests - UI): 7 tasks
- Phase 8 (Integration Tests): 10 tasks
- Phase 9 (QA): 5 tasks

**Breakdown by User Story**:
- User Story 1 (Delete): Covered by T004-T043 (all phases)
- User Story 2 (Cancel): Covered by T004-T043 (all phases)
- User Story 3 (Error Handling): Covered by T004-T043 (all phases)

**Parallelizable Tasks**: 21 tasks marked with [P]

**Estimated Total Time**: ~2.5 hours (110 min implementation + 40 min validation)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Recommended First Iteration**: Phases 1-5 (Tasks T001-T014)
- Implements all 3 user stories (tightly coupled)
- Provides working delete functionality
- Menu integration complete
- No tests (manual testing only)
- **Estimated Time**: ~40 minutes

### Full Feature Scope

**Complete Implementation**: Phases 1-9 (Tasks T001-T043)
- All user stories implemented
- Full test coverage (unit + integration)
- Code quality verified
- Production-ready
- **Estimated Time**: ~2.5 hours

### Incremental Delivery Milestones

**Milestone 1** (Phases 1-2): Business logic layer complete
- Constants defined
- `delete_task()` function implemented
- Can be tested via Python REPL

**Milestone 2** (Phases 1-4): UI layer complete
- Confirmation prompt implemented
- Workflow orchestration complete
- Can be tested via function calls (no menu yet)

**Milestone 3** (Phases 1-5): Feature complete (no tests)
- Menu integration done
- End-to-end manual testing possible
- Ready for automated test development

**Milestone 4** (Phases 1-9): Production-ready
- All tests passing
- Code quality verified
- Ready for pull request

---

## Validation Checklist

Use this checklist to verify task completion:

### Functional Requirements
- [ ] FR-001: "Delete Task" menu option exists at position 4
- [ ] FR-002: Prompt "Enter Task ID: " displayed (reuses existing)
- [ ] FR-003: Input validated as positive integer
- [ ] FR-004: Zero/negative integers rejected with ERROR 103
- [ ] FR-005: Non-numeric input rejected with ERROR 102
- [ ] FR-006: Task ID existence verified
- [ ] FR-007: Non-existent ID shows ERROR 101, no confirmation
- [ ] FR-008: Task title displayed in confirmation prompt
- [ ] FR-009: Waits for user confirmation before deletion
- [ ] FR-010: Accepts Y/y/N/n (case-insensitive)
- [ ] FR-011: Invalid confirmation rejected with ERROR 105
- [ ] FR-012: Whitespace stripped from confirmation input
- [ ] FR-013: Y/y confirms deletion
- [ ] FR-014: N/n cancels deletion
- [ ] FR-015: Task permanently removed on confirmation
- [ ] FR-016: "Task deleted successfully." displayed
- [ ] FR-017: Other tasks unchanged (no ID renumbering)
- [ ] FR-018: Deleted IDs not immediately reused
- [ ] FR-019: Task preserved on cancellation
- [ ] FR-020: "Deletion canceled." displayed on cancel
- [ ] FR-021: Returns to menu after cancellation
- [ ] FR-022: Returns to menu after all outcomes
- [ ] FR-023: No crashes on invalid input
- [ ] FR-024: Deletes both completed and incomplete tasks

### Success Criteria
- [ ] SC-001: Can delete task in <15 seconds
- [ ] SC-002: 100% of confirmed deletions succeed
- [ ] SC-003: 100% of cancellations preserve task
- [ ] SC-004: 100% of invalid inputs show error and allow retry
- [ ] SC-005: 100% return to main menu
- [ ] SC-006: 100% show task title in confirmation
- [ ] SC-007: 100% preserve non-deleted task IDs/data
- [ ] SC-008: Empty list handled gracefully

### Code Quality
- [ ] All functions have type hints
- [ ] All functions have Google-style docstrings
- [ ] `ruff check .` passes with zero errors
- [ ] `ruff format --check .` confirms formatting
- [ ] No magic numbers or hardcoded strings
- [ ] Error constants in constants.py

### Testing
- [ ] 100% of unit tests pass
- [ ] 100% of integration tests pass
- [ ] Code coverage ≥95% for new functions
- [ ] Manual smoke test completed

---

## Next Steps

1. **Start Implementation**: Begin with Phase 1 (Setup & Constants)
2. **Follow Sequential Order**: Complete phases 1-5 before testing phases
3. **Leverage Parallelism**: Run Phase 6 and Phase 7 tests concurrently
4. **Validate Incrementally**: Run tests after each phase completion
5. **Final Verification**: Execute Phase 9 QA checklist before PR

**Ready to Begin**: All planning artifacts complete, tasks clearly defined, acceptance criteria established.
