---

description: "Task list for Rich UI Integration feature implementation"
---

# Tasks: Rich UI Integration

**Input**: Design documents from `/specs/006-rich-ui/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: This feature requires maintaining 100% backward compatibility with existing tests. No new test files are created - existing tests must pass without modification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure as per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency verification

- [X] T001 Verify rich library dependency in pyproject.toml (confirm rich==14.1.0 is present)
- [X] T002 Verify Python 3.13 environment and UV package manager installation
- [X] T003 Run existing test suite to establish baseline (uv run pytest) - all tests must pass

**Checkpoint**: Environment ready - dependencies verified, baseline tests passing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core imports and helper function setup that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add rich library imports to src/ui/prompts.py (from rich.console import Console, from rich.table import Table)
- [X] T005 Verify existing imports in src/ui/prompts.py are preserved (datetime, Task model, service functions)

**Checkpoint**: Foundation ready - imports added, no syntax errors, user story implementation can now begin

---

## Phase 3: User Story 1 - View Tasks in Formatted Table (Priority: P1) 🎯 MVP

**Goal**: Display all tasks in a formatted table with 5 columns (ID, Title, Status, Creation Time, Last Updated Time)

**Independent Test**: Start application, add 3 tasks with varying title lengths, select "View Tasks" from menu, verify formatted table displays with proper column alignment

### Implementation for User Story 1

- [X] T006 [US1] Refactor display_task_list() function in src/ui/prompts.py to create rich Table with 5 columns
- [X] T007 [US1] Add table column definitions with proper styling (ID=dim width 6, Title=min_width 20, Status=center-justified, timestamps=right-justified)
- [X] T008 [US1] Implement table header styling (bold magenta) and title ("Tasks") in src/ui/prompts.py
- [X] T009 [US1] Implement title truncation logic for titles exceeding 50 characters (truncate at 47 chars + "...") in src/ui/prompts.py
- [X] T010 [US1] Implement timestamp formatting from ISO 8601 to "YYYY-MM-DD HH:MM:SS" format in src/ui/prompts.py
- [X] T011 [US1] Add Console.print(table) rendering in src/ui/prompts.py
- [X] T012 [US1] Run existing test suite (uv run pytest tests/test_prompts.py) and verify 100% backward compatibility

**Checkpoint**: At this point, User Story 1 should be fully functional - tasks display in formatted table with proper columns

---

## Phase 4: User Story 2 - Distinguish Task Status Visually (Priority: P2)

**Goal**: Users can quickly identify completed vs pending tasks through clear status labels

**Independent Test**: Add 2 completed tasks and 3 pending tasks, view task list, verify Status column shows "Completed" or "Pending" labels (not boolean values)

### Implementation for User Story 2

- [X] T013 [US2] Implement status label mapping (task.completed=True → "Completed", task.completed=False → "Pending") in src/ui/prompts.py display_task_list()
- [X] T014 [US2] Add status value to table.add_row() calls in src/ui/prompts.py
- [X] T015 [US2] Test with mixed completed/pending tasks and verify status labels display correctly

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - tasks display in table with clear status labels

---

## Phase 5: User Story 3 - View Empty Task List with Clear Messaging (Priority: P3)

**Goal**: Display friendly, formatted message when task list is empty instead of showing blank screen or error

**Independent Test**: Start application with no tasks (or delete all tasks), select "View Tasks", verify formatted empty state message appears

### Implementation for User Story 3

- [X] T016 [US3] Add empty list check at start of display_task_list() in src/ui/prompts.py
- [X] T017 [US3] Implement rich-formatted empty state message ("📋 No tasks found. Add a task to get started!" with italic cyan styling) in src/ui/prompts.py
- [X] T018 [US3] Add early return after empty state message to prevent table rendering in src/ui/prompts.py
- [X] T019 [US3] Test empty state by calling display_task_list([]) and verifying message displays correctly

**Checkpoint**: All user stories should now be independently functional - empty state handled gracefully

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and ensure production readiness

- [X] T020 [P] Implement graceful degradation with try-except wrapper around Console.print(table) in src/ui/prompts.py
- [X] T021 [P] Add plain text fallback logic for unsupported terminal environments in src/ui/prompts.py
- [X] T022 [P] Add warning message ("⚠️ Rich formatting unavailable, using plain text.") for degradation case in src/ui/prompts.py
- [X] T023 Run complete test suite (uv run pytest) and verify 100% test pass rate
- [X] T024 Run code quality checks (uv run ruff check . && uv run ruff format --check .)
- [X] T025 Manual end-to-end testing following quickstart.md verification steps
- [ ] T026 Performance validation - verify 1000 tasks render in <1 second (optional stress test)

**Checkpoint**: All tasks complete - feature ready for commit and pull request

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (P1 → P2 → P3)
  - Each story builds on previous but remains independently testable
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after User Story 1 completion - Adds status mapping to existing table
- **User Story 3 (P3)**: Can start after User Story 1 completion - Adds empty state handling to same function

### Within Each User Story

- Tasks within User Story 1 must be sequential (all modify same display_task_list() function)
- Tasks within User Story 2 build on User Story 1's table implementation
- Tasks within User Story 3 add edge case handling to existing implementation
- Polish tasks marked [P] can run in parallel (different concerns)

### Parallel Opportunities

- Phase 1 tasks can be verified in parallel (dependencies, tests)
- Phase 2 imports can be added together in single edit
- Phase 6 polish tasks marked [P] can run in parallel (degradation handling, quality checks)
- **Note**: Most implementation tasks are NOT parallelizable because they all modify the same function (display_task_list() in src/ui/prompts.py)

---

## Parallel Example: Phase 6 Polish Tasks

```bash
# These Phase 6 tasks can run in parallel (different concerns):
Task T020: "Implement graceful degradation wrapper"
Task T021: "Add plain text fallback logic"
Task T022: "Add warning message for degradation"

# These are independent modifications to the same function's error handling
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verify environment)
2. Complete Phase 2: Foundational (add imports)
3. Complete Phase 3: User Story 1 (basic table display)
4. **STOP and VALIDATE**: Test table displays correctly with multiple tasks
5. Demo formatted table feature

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test table display → Demo MVP
3. Add User Story 2 → Test status labels → Demo enhanced version
4. Add User Story 3 → Test empty state → Demo complete feature
5. Add Polish → Test degradation, run quality checks → Deploy production-ready

### Sequential Implementation (Recommended)

Since all tasks modify the same file/function (src/ui/prompts.py::display_task_list()):

1. Complete Setup + Foundational together
2. Implement User Story 1 completely (tasks T006-T012)
3. Implement User Story 2 completely (tasks T013-T015)
4. Implement User Story 3 completely (tasks T016-T019)
5. Add Polish features together (tasks T020-T026)

---

## Critical Implementation Notes

### Single File Modification
**All implementation tasks modify the same file**: `src/ui/prompts.py` (specifically the `display_task_list()` function)

This means:
- Most tasks cannot be parallelized (sequential implementation required)
- Each user story enhances the same function incrementally
- Careful testing after each phase is critical to avoid regressions

### Backward Compatibility Requirement
**FR-006 mandates 100% existing test pass rate**:
- After T012 (User Story 1 complete): Run tests and verify all pass
- After T015 (User Story 2 complete): Run tests and verify all pass
- After T019 (User Story 3 complete): Run tests and verify all pass
- After T023 (Final validation): All tests must pass before commit

### Title Truncation Formula
**Exactly 50 characters total** (not 50 + ellipsis):
```python
# Correct:
title[:47] + "..." if len(title) > 50 else title

# Incorrect:
title[:50] + "..."  # This creates 53-char strings!
```

### Timestamp Format Conversion
**Handle ISO 8601 'Z' suffix**:
```python
# Correct:
datetime.fromisoformat(task.created_at.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")

# Incorrect:
datetime.fromisoformat(task.created_at).strftime("%Y-%m-%d %H:%M:%S")  # Fails on 'Z'
```

### Graceful Degradation Location
**Add try-except AROUND table rendering** (not around entire function):
- Empty state check must happen BEFORE try block
- Fallback should print warning + plain text
- Do not raise exceptions to caller

---

## Validation Checklist

Before marking feature complete, verify:

### Functional Requirements (from spec.md)
- [ ] **FR-001**: Tasks displayed in rich.table.Table format ✓
- [ ] **FR-002**: Table has exactly 5 columns (ID, Title, Status, Creation Time, Last Updated Time) ✓
- [ ] **FR-003**: Status shows "Completed"/"Pending" (not True/False) ✓
- [ ] **FR-004**: rich library is in pyproject.toml (already complete) ✓
- [ ] **FR-005**: prompt_view_all_tasks refactored to use rich.table.Table ✓
- [ ] **FR-006**: All existing tests pass 100% ✓
- [ ] **FR-007**: Empty state uses rich formatting ✓
- [ ] **FR-008**: Timestamps in "YYYY-MM-DD HH:MM:SS" format ✓
- [ ] **FR-009**: Table is responsive to terminal width ✓
- [ ] **FR-010**: Titles >50 chars truncated with "..." ✓
- [ ] **FR-011**: Graceful degradation to plain text if rich fails ✓

### Success Criteria (from spec.md)
- [ ] **SC-001**: All task info viewable in single table without horizontal scrolling (80+ column terminal) ✓
- [ ] **SC-002**: Task status immediately distinguishable ("Completed" vs "Pending") ✓
- [ ] **SC-003**: All existing tests pass 100% ✓
- [ ] **SC-004**: Table displays correctly on varying terminal widths (80-200 columns) ✓
- [ ] **SC-005**: Timestamps in standardized "YYYY-MM-DD HH:MM:SS" format ✓

### Manual Testing Scenarios
- [ ] Add 3 tasks with titles: 20 chars, 50 chars, 100 chars
- [ ] View tasks - verify table displays with proper truncation
- [ ] Mark 1 task complete, view again - verify status shows "Completed"
- [ ] Delete all tasks, view - verify empty state message displays
- [ ] Test on 80-column terminal window - verify no horizontal scrolling

---

## Notes

- All tasks modify single file: `src/ui/prompts.py`
- User Story 1 is MVP - delivers core table display functionality
- User Story 2 enhances MVP with status labels
- User Story 3 adds edge case handling (empty state)
- Phase 6 adds production hardening (graceful degradation)
- Commit after completing all phases (single atomic commit for this feature)
- No new test files created - existing tests must pass as-is
- Avoid: modifying test files, changing function signatures, adding new dependencies beyond rich
