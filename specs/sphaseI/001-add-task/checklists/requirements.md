# Requirements Checklist: Add Task

**Purpose**: Verify complete implementation of Add Task feature against specification requirements
**Created**: 2025-12-04
**Feature**: [spec.md](../spec.md)

## Setup & Infrastructure

- [ ] CHK001 Python 3.13 environment configured with UV
- [ ] CHK002 `pyproject.toml` created with project metadata
- [ ] CHK003 Project structure created (src/models, src/services, src/ui, tests/unit, tests/integration)
- [ ] CHK004 `__init__.py` files in all package directories
- [ ] CHK005 pytest and pytest-cov installed as dev dependencies
- [ ] CHK006 ruff configured in pyproject.toml for linting and formatting

## Data Model (src/models/task.py)

- [ ] CHK007 Task dataclass defined with all 6 required fields
- [ ] CHK008 Type hints for all fields: id (int), title (str), description (str), completed (bool), created_at (str), updated_at (str)
- [ ] CHK009 Google-style docstring for Task class
- [ ] CHK010 Static method `generate_timestamp()` returns ISO 8601 format (YYYY-MM-DDTHH:MM:SS.ffffffZ)
- [ ] CHK011 Timestamp uses UTC timezone

## Constants (src/constants.py)

- [ ] CHK012 MAX_TITLE_LENGTH = 200 defined
- [ ] CHK013 MAX_DESCRIPTION_LENGTH = 1000 defined
- [ ] CHK014 ERROR_TITLE_REQUIRED = "ERROR 001: Title is required and must be 1-200 characters."
- [ ] CHK015 ERROR_TITLE_TOO_LONG = "ERROR 002: Title is required and must be 1-200 characters."
- [ ] CHK016 ERROR_DESCRIPTION_TOO_LONG = "ERROR 003: Description cannot exceed 1000 characters."
- [ ] CHK017 MSG_TASK_ADDED = "Task added successfully."
- [ ] CHK018 PROMPT_TITLE = "Enter Task Title: "
- [ ] CHK019 PROMPT_DESCRIPTION = "Enter Optional Task Description (press Enter to skip): "

## Validation (src/ui/prompts.py)

- [ ] CHK020 `validate_title()` function with type hints and docstring
- [ ] CHK021 Title validation strips whitespace before checking
- [ ] CHK022 Title validation rejects empty/whitespace-only input with ERROR 001
- [ ] CHK023 Title validation rejects > 200 chars with ERROR 002
- [ ] CHK024 Title validation accepts 1-200 chars (inclusive)
- [ ] CHK025 `validate_description()` function with type hints and docstring
- [ ] CHK026 Description validation strips whitespace before checking
- [ ] CHK027 Description validation accepts empty string
- [ ] CHK028 Description validation rejects > 1000 chars with ERROR 003
- [ ] CHK029 Description validation accepts 0-1000 chars (inclusive)

## Input Prompts (src/ui/prompts.py)

- [ ] CHK030 `get_task_title()` prompts with PROMPT_TITLE constant
- [ ] CHK031 Title prompt loops until valid input received
- [ ] CHK032 Title prompt displays error message on validation failure
- [ ] CHK033 Title prompt returns stripped title on success
- [ ] CHK034 `get_task_description()` prompts with PROMPT_DESCRIPTION constant
- [ ] CHK035 Description prompt loops until valid input received
- [ ] CHK036 Description prompt displays error message on validation failure
- [ ] CHK037 Description prompt returns stripped description on success

## Task Service (src/services/task_service.py)

- [ ] CHK038 Module-level `_task_storage: list[Task] = []` defined
- [ ] CHK039 `generate_next_id()` returns 1 if storage empty
- [ ] CHK040 `generate_next_id()` returns max(existing_ids) + 1 if storage not empty
- [ ] CHK041 `create_task()` accepts title and description parameters
- [ ] CHK042 `create_task()` generates timestamp using Task.generate_timestamp()
- [ ] CHK043 `create_task()` sets id using generate_next_id()
- [ ] CHK044 `create_task()` sets completed to False
- [ ] CHK045 `create_task()` sets created_at and updated_at to same timestamp
- [ ] CHK046 `create_task()` appends task to _task_storage
- [ ] CHK047 `create_task()` returns created Task instance
- [ ] CHK048 All service functions have type hints and Google-style docstrings

## Main Application (src/main.py)

- [ ] CHK049 `handle_add_task()` calls get_task_title()
- [ ] CHK050 `handle_add_task()` calls get_task_description()
- [ ] CHK051 `handle_add_task()` calls create_task(title, description)
- [ ] CHK052 `handle_add_task()` prints MSG_TASK_ADDED on success
- [ ] CHK053 Main menu displays 6 options (5 features + Exit)
- [ ] CHK054 Option 1 calls handle_add_task()
- [ ] CHK055 Application returns to main menu after task added
- [ ] CHK056 Application doesn't crash on any input

## Code Quality

- [ ] CHK057 All functions have type hints for parameters and return values
- [ ] CHK058 All functions and classes have Google-style docstrings
- [ ] CHK059 `ruff check .` passes with zero errors
- [ ] CHK060 `ruff format --check .` confirms code is formatted
- [ ] CHK061 No magic numbers - all constants defined in constants.py
- [ ] CHK062 PEP 8 compliance verified
- [ ] CHK063 Optional: `mypy src/ --strict` passes

## Functional Requirements (from spec.md)

- [ ] CHK064 FR-001: System displays "Enter Task Title: " prompt
- [ ] CHK065 FR-002: Leading/trailing whitespace stripped from title
- [ ] CHK066 FR-003: Title validated between 1-200 chars
- [ ] CHK067 FR-004: Empty title rejected with ERROR 001
- [ ] CHK068 FR-005: Title > 200 chars rejected with ERROR 002
- [ ] CHK069 FR-006: System displays "Enter Optional Task Description (press Enter to skip): "
- [ ] CHK070 FR-007: Leading/trailing whitespace stripped from description
- [ ] CHK071 FR-008: Empty description allowed
- [ ] CHK072 FR-009: Description > 1000 chars rejected with ERROR 003
- [ ] CHK073 FR-010: Unique integer ID generated (starting at 1)
- [ ] CHK074 FR-011: completed field set to False
- [ ] CHK075 FR-012: created_at and updated_at set to current UTC timestamp (ISO 8601)
- [ ] CHK076 FR-013: Task stored in in-memory Python list
- [ ] CHK077 FR-014: "Task added successfully." displayed after creation
- [ ] CHK078 FR-015: Returns to main menu after operation
- [ ] CHK079 FR-016: Application doesn't crash on validation errors

## Success Criteria (from spec.md)

- [ ] CHK080 SC-001: Task creation completes in < 30 seconds
- [ ] CHK081 SC-002: 100% of valid inputs create tasks successfully
- [ ] CHK082 SC-003: 100% of invalid inputs display correct error and allow retry
- [ ] CHK083 SC-004: Sequential IDs starting from 1, no gaps
- [ ] CHK084 SC-005: ISO 8601 UTC timestamps for created_at and updated_at
- [ ] CHK085 SC-006: Empty descriptions work 100% of the time
- [ ] CHK086 SC-007: Returns to main menu 100% of the time with confirmation

## Edge Cases

- [ ] CHK087 Whitespace-only title handled correctly (ERROR 001)
- [ ] CHK088 Title exactly 200 chars accepted
- [ ] CHK089 Title 201 chars rejected (ERROR 002)
- [ ] CHK090 Description exactly 1000 chars accepted
- [ ] CHK091 Description 1001 chars rejected (ERROR 003)
- [ ] CHK092 First task receives ID 1
- [ ] CHK093 Subsequent tasks receive incremented IDs
- [ ] CHK094 Multiple validation failures allow continued retry
- [ ] CHK095 created_at and updated_at timestamps are identical for new tasks

## No Violations

- [ ] CHK096 No file I/O operations in code
- [ ] CHK097 No database connections in code
- [ ] CHK098 No external dependencies except pytest
- [ ] CHK099 No GUI components
- [ ] CHK100 All code in src/ is AI-generated (or deviations documented)

## Notes

- Mark items complete with `[x]` as implementation progresses
- Re-verify all items after any code changes
- All 100 items must pass before feature is considered complete
- Document any deviations in DEVIATIONS.md per Constitution
