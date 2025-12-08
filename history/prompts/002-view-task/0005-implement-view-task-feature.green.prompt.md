---
id: 0005
title: implement-view-task-feature
stage: green
date: 2025-12-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-view-task
branch: 002-view-task
user: salim
command: /sp.implement
labels: ["implementation", "view-task", "tdd", "testing"]
links:
  spec: /specs/002-view-task/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/services/task_service.py
  - src/ui/prompts.py
  - src/main.py
  - src/constants.py
  - tests/unit/test_main.py
  - tests/unit/test_main_entry.py
  - specs/002-view-task/tasks.md
tests:
  - tests/unit/test_task_service.py::TestGetAllTasks
  - tests/unit/test_prompts.py::TestDisplayTaskList
  - tests/unit/test_prompts.py::TestDisplayTaskDetails
  - tests/unit/test_prompts.py::TestPromptForTaskId
  - tests/integration/test_view_task_flow.py::TestViewTasksFlow
  - tests/integration/test_view_task_flow.py::TestViewTaskDetailsFlow
  - All 97 tests passing with 95% coverage
---

## Prompt

Resume implementation from User Story 1 where tests were already passing. User requested to continue implementation from checkpoint where test_display_task_list_empty was shown passing. The implementation needed to complete User Story 1 (View All Tasks) and User Story 2 (View Task Details), followed by polish and validation tasks.

## Response snapshot

Successfully implemented the complete View Task feature with two user stories:

**User Story 1: View All Tasks (completed T008-T011)**
- Implemented get_all_tasks() in TaskService (returns copy of task list)
- Implemented display_task_list() in prompts.py with pagination support (every 20 tasks)
- Added "View Tasks" menu option (option 2) to main menu
- Implemented handle_view_tasks() handler with error handling
- All integration tests passing

**User Story 2: View Task Details (completed T012-T020)**
- Implemented get_task_by_id() in TaskService with validation (ERROR 101, 103)
- Implemented display_task_details() in prompts.py (6 fields with labels)
- Implemented prompt_for_task_id() with input validation (ERROR 102, 103)
- Added "View Task Details" menu option (option 3, moved Exit to option 7)
- Implemented handle_view_task_details() handler with error handling
- All integration tests passing

**Polish & Validation (completed T021-T024)**
- Fixed menu test failures due to option number changes (6→7 for Exit)
- Ran full test suite: 97 tests passing with 95% coverage
- Fixed linting issues (auto-fixable import sorting)
- Formatted all files with ruff
- Verified tests still pass after formatting

**Key Implementation Details:**
1. Error handling: ValueError with specific error messages (ERROR 101, 102, 103)
2. Empty description: Shows "(No description)" placeholder
3. Completion indicator: "[ ]" incomplete, "[X]" complete
4. Pagination: Prompts every 20 tasks if more remain
5. Menu structure: Updated from 6 to 7 options

## Outcome

- ✅ Impact: Complete View Task feature implemented with two user stories, 100% test coverage on all view code (TaskService and UI functions), 95% overall coverage
- 🧪 Tests: All 97 tests passing (unit + integration), test coverage verified, linter/formatter checks passed
- 📁 Files: Modified 4 source files (task_service.py, prompts.py, main.py, constants.py), updated 2 test files for menu changes, updated tasks.md
- 🔁 Next prompts: Feature implementation complete, ready for manual testing (T025-T034) and potential commit/PR creation
- 🧠 Reflection: TDD approach with pre-written tests made implementation smooth. Menu structure change required careful test updates across multiple test files.

## Evaluation notes (flywheel)

- Failure modes observed: Test failures due to menu option number changes (Exit moved from 6 to 7); line length warnings in test files (acceptable for test code)
- Graders run and results (PASS/FAIL): PASS - All 97 tests passing, 95% coverage, linter clean (except acceptable line length in tests), formatter clean
- Prompt variant (if applicable): Standard /sp.implement workflow with resume from checkpoint
- Next experiment (smallest change to try): Consider refactoring menu to use constants for option numbers to prevent test breakage on menu changes
