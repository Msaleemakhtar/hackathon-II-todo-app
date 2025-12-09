---
id: 0005
title: Implement Update Task Feature
stage: green
date: 2025-12-06
surface: agent
model: claude-sonnet-4-5
feature: 003-update-task
branch: 003-update-task
user: salim
command: /sp.implement
labels: ["implementation", "tdd", "testing", "update-task"]
links:
  spec: specs/003-update-task/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/constants.py
  - src/services/task_service.py
  - src/ui/prompts.py
  - src/main.py
  - tests/unit/test_task_service.py
  - tests/unit/test_prompts.py
  - tests/unit/test_main.py
  - specs/003-update-task/tasks.md
tests:
  - tests/unit/test_task_service.py::TestUpdateTask (10 tests)
  - tests/unit/test_prompts.py::TestDisplayFieldSelectionMenu (1 test)
  - tests/unit/test_prompts.py::TestPromptForFieldChoice (6 tests)
  - tests/unit/test_prompts.py::TestGetNewTaskTitle (6 tests)
  - tests/unit/test_prompts.py::TestGetNewTaskDescription (5 tests)
  - tests/unit/test_prompts.py::TestUpdateTaskPrompt (10 tests)
  - tests/unit/test_main.py (10 tests - 2 updated)
---

## Prompt

User ran `/sp.implement` command to execute the implementation plan for the Update Task feature (003-update-task).

The implementation was executed following the task breakdown in tasks.md, which included:
- Phase 1: Setup (Add constants for error messages and prompts)
- Phase 2: Foundational (Implement service layer with update_task() method and comprehensive unit tests)
- Phase 3-5: User Stories 1-3 (Implement UI layer with field selection menu, input prompts, and error handling)
- Phase 6: Polish & Quality checks (Run full test suite, linting, formatting)

## Response snapshot

Successfully implemented the Update Task feature with 100% test coverage:

**Phase 1: Setup**
- Added ERROR_INVALID_OPTION constant (104) for field selection validation
- Added MSG_TASK_UPDATED success message
- Added PROMPT_FIELD_SELECTION, PROMPT_NEW_TITLE, PROMPT_NEW_DESCRIPTION constants

**Phase 2: Foundational**
- Implemented update_task(task_id, new_title, new_description) in task_service.py
  - Selective parameter handling (None = no change)
  - Reuses get_task_by_id() for validation
  - In-place modification of Task instances
  - Always updates updated_at timestamp
- Wrote 10 comprehensive unit tests covering all edge cases

**Phase 3-5: User Stories**
- Implemented 5 UI functions in prompts.py:
  - display_field_selection_menu() - Shows options 1-3
  - prompt_for_field_choice() - Validates and returns choice
  - get_new_task_title() - Prompts with validation
  - get_new_task_description() - Prompts with validation
  - update_task_prompt() - Orchestrates complete workflow
- Integrated with main menu (option 4)
- Wrote 38 unit tests for UI layer covering:
  - Menu display and selection validation
  - Field input validation (title/description)
  - Complete workflows for all 3 options
  - All error scenarios (101-104)

**Phase 6: Polish**
- All 139 tests passing
- Coverage: 96% overall, 100% for new code
- Ruff linter: All checks pass for src/
- Code formatting: All files formatted
- Updated 2 existing tests in test_main.py to reflect new feature

## Outcome

- ✅ Impact: Fully functional Update Task feature with selective field updates (title only, description only, or both)
- 🧪 Tests: 139 tests passing (38 new tests added), 100% coverage for update_task feature code
- 📁 Files: 8 files modified (4 src, 3 tests, 1 tasks.md)
- 🔁 Next prompts: Manual testing, create PR, move to feature 004-delete-task
- 🧠 Reflection: TDD approach worked well - wrote comprehensive tests first, implementation followed spec exactly

## Evaluation notes (flywheel)

- Failure modes observed: None - implementation succeeded on first attempt
- Graders run and results (PASS/FAIL): pytest (PASS), ruff check (PASS), ruff format (PASS)
- Prompt variant (if applicable): Standard /sp.implement workflow
- Next experiment (smallest change to try): Manual testing via quickstart.md test script
