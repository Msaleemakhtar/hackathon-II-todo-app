# Tasks: Mark Complete

**Input**: Design documents from `/specs/005-mark-complete/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: All tests are included in the quickstart.md and must be implemented as part of the feature.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)
**Purpose**: Project initialization and basic structure

- [X] T001 Add constants for Mark Complete feature in `src/constants.py`

## Phase 2: Foundational (Blocking Prerequisites)
**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented
**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Add `toggle_task_completion()` function to `src/services/task_service.py`

## Phase 3: User Story 1 - Toggle Task to Complete (Priority: P1) 🎯 MVP
**Goal**: Implement the ability to mark an incomplete task as complete.
**Independent Test**: Can be fully tested by navigating to Mark Complete menu option, entering the ID of an incomplete task, and verifying the task's completed status changes to True and the updated_at timestamp is updated.

### Tests for User Story 1

- [X] T003 [P] [US1] Add `test_toggle_incomplete_to_complete()` unit test in `tests/unit/test_task_service.py`
- [X] T004 [P] [US1] Add `test_toggle_updates_timestamp()` unit test in `tests/unit/test_task_service.py`
- [X] T005 [P] [US1] Add `test_toggle_preserves_created_at()` unit test in `tests/unit/test_task_service.py`
- [X] T006 [P] [US1] Add `test_toggle_preserves_other_fields()` unit test in `tests/unit/test_task_service.py`
- [X] T007 [P] [US1] Add `test_prompt_for_mark_complete_confirmation_dynamic_prompt_incomplete()` unit test in `tests/unit/test_prompts.py`
- [X] T008 [P] [US1] Add `test_mark_complete_prompt_full_flow_confirm()` unit test in `tests/unit/test_prompts.py`
- [X] T009 [P] [US1] Add `test_mark_complete_flow_incomplete_to_complete()` integration test in `tests/integration/test_mark_complete_flow.py`
- [X] T010 [P] [US1] Add `test_mark_complete_flow_complete_to_incomplete()` integration test in `tests/integration/test_mark_complete_flow.py` (partially covers US1 and US2)

### Implementation for User Story 1

- [X] T011 [US1] Implement `prompt_for_mark_complete_confirmation()` in `src/ui/prompts.py`
- [X] T012 [US1] Implement `mark_complete_prompt()` orchestration in `src/ui/prompts.py`

## Phase 4: User Story 2 - Toggle Task to Incomplete (Priority: P1)
**Goal**: Implement the ability to mark a completed task back to incomplete.
**Independent Test**: Can be fully tested by navigating to Mark Complete menu option, entering the ID of a completed task, and verifying the task's completed status changes to False and the updated_at timestamp is updated.

### Tests for User Story 2

- [X] T013 [P] [US2] Add `test_toggle_complete_to_incomplete()` unit test in `tests/unit/test_task_service.py`
- [X] T014 [P] [US2] Add `test_prompt_for_mark_complete_confirmation_dynamic_prompt_complete()` unit test in `tests/unit/test_prompts.py`

## Phase 5: User Story 3 - Cancel Status Change Operation (Priority: P1)
**Goal**: Allow users to cancel a status change operation, preventing accidental modifications.
**Independent Test**: Can be fully tested by navigating to Mark Complete, entering a valid task ID, canceling with "N" at the confirmation prompt, and verifying the task's status remains unchanged.

### Tests for User Story 3

- [X] T015 [P] [US3] Add `test_prompt_for_mark_complete_confirmation_no_uppercase()` unit test in `tests/unit/test_prompts.py`
- [X] T016 [P] [US3] Add `test_prompt_for_mark_complete_confirmation_no_lowercase()` unit test in `tests/unit/test_prompts.py`
- [X] T017 [P] [US3] Add `test_prompt_for_mark_complete_confirmation_with_whitespace()` unit test in `tests/unit/test_prompts.py`
- [X] T018 [P] [US3] Add `test_prompt_for_mark_complete_confirmation_invalid_then_valid()` unit test in `tests/unit/test_prompts.py`
- [X] T019 [P] [US3] Add `test_mark_complete_prompt_full_flow_cancel()` unit test in `tests/unit/test_prompts.py`
- [X] T020 [P] [US3] Add `test_mark_complete_flow_cancellation()` integration test in `tests/integration/test_mark_complete_flow.py`
- [X] T021 [P] [US3] Add `test_mark_complete_flow_invalid_confirmation()` integration test in `tests/integration/test_mark_complete_flow.py`

## Phase 6: User Story 4 - Handle Invalid Status Change Attempts (Priority: P1)
**Goal**: Provide clear error feedback for invalid inputs without crashing the system.
**Independent Test**: Can be fully tested by attempting to mark complete with non-existent task ID, invalid input types, and verifying appropriate error messages are shown without system crashes.

### Tests for User Story 4

- [X] T022 [P] [US4] Add `test_toggle_nonexistent_task()` unit test in `tests/unit/test_task_service.py`
- [X] T023 [P] [US4] Add `test_toggle_zero_task_id()` unit test in `tests/unit/test_task_service.py`
- [X] T024 [P] [US4] Add `test_toggle_negative_task_id()` unit test in `tests/unit/test_task_service.py`
- [X] T025 [P] [US4] Add `test_prompt_for_mark_complete_confirmation_yes_uppercase()` unit test in `tests/unit/test_prompts.py`
- [X] T026 [P] [US4] Add `test_prompt_for_mark_complete_confirmation_yes_lowercase()` unit test in `tests/unit/test_prompts.py`
- [X] T027 [P] [US4] Add `test_mark_complete_prompt_invalid_task_id()` unit test in `tests/unit/test_prompts.py`
- [X] T028 [P] [US4] Add `test_mark_complete_flow_invalid_id_non_numeric()` integration test in `tests/integration/test_mark_complete_flow.py`
- [X] T029 [P] [US4] Add `test_mark_complete_flow_invalid_id_zero()` integration test in `tests/integration/test_mark_complete_flow.py`
- [X] T030 [P] [US4] Add `test_mark_complete_flow_nonexistent_task()` integration test in `tests/integration/test_mark_complete_flow.py`
- [X] T031 [P] [US4] Add `test_mark_complete_flow_multiple_toggles()` integration test in `tests/integration/test_mark_complete_flow.py`
- [X] T032 [P] [US4] Add `test_mark_complete_flow_empty_task_list()` integration test in `tests/integration/test_mark_complete_flow.py`

## Final Phase: Polish & Cross-Cutting Concerns
**Purpose**: Improvements that affect multiple user stories

- [X] T033 Wire `handle_mark_complete()` into main menu and update menu option 6 in `src/main.py`
- [X] T034 Implement `handle_mark_complete()` function in `src/main.py`
- [X] T035 Update imports in `src/main.py` and `src/ui/prompts.py` for new functions and constants
- [X] T036 Create `tests/integration/test_mark_complete_flow.py` and add fixture
- [X] T037 Run full test suite: `uv run pytest --cov=src --cov-report=term-missing`
- [X] T038 Verify code quality: `uv run ruff check .` and `uv run ruff format --check .`
- [X] T039 Perform manual smoke test: `uv run python src/main.py`

---
## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies
- All User Stories (P1) can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story
- Tests MUST be written and FAIL before implementation
- Models before services
- Services before UI prompts
- Core implementation before main menu integration
- Story complete before moving to next priority

### Parallel Opportunities
- Tasks marked [P] within the same phase/story can run in parallel (different files, no dependencies).
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows).

---
## Implementation Strategy

### MVP First
1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently

### Incremental Delivery
1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently
3. Add User Story 2 → Test independently
4. Add User Story 3 → Test independently
5. Add User Story 4 → Test independently
6. Complete Final Phase: Polish & Cross-Cutting Concerns → Full feature ready

---
## Notes
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
