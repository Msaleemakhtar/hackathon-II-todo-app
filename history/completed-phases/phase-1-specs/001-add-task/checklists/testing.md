# Testing Checklist: Add Task

**Purpose**: Verify comprehensive test coverage for Add Task feature with 100% core logic coverage
**Created**: 2025-12-04
**Feature**: [spec.md](../spec.md)

## Test Infrastructure

- [ ] CHK001 pytest installed and configured
- [ ] CHK002 pytest-cov installed for coverage reporting
- [ ] CHK003 tests/ directory structure created (unit/, integration/)
- [ ] CHK004 `__init__.py` files in all test directories
- [ ] CHK005 Test files named with `test_` prefix

## Unit Tests - Task Model (tests/unit/test_task_model.py)

- [ ] CHK006 Test Task dataclass instantiation with all fields
- [ ] CHK007 Test Task dataclass default values (completed=False)
- [ ] CHK008 Test Task.generate_timestamp() returns ISO 8601 format
- [ ] CHK009 Test timestamp includes microseconds (.ffffffZ)
- [ ] CHK010 Test timestamp uses UTC timezone (Z suffix)
- [ ] CHK011 Test Task equality (two tasks with same data are equal)
- [ ] CHK012 Test Task repr (string representation)

## Unit Tests - Validation (tests/unit/test_validation.py)

### Title Validation Tests

- [ ] CHK013 Test valid title (1-200 chars) returns (True, None)
- [ ] CHK014 Test empty string title returns (False, ERROR 001)
- [ ] CHK015 Test whitespace-only title "   " returns (False, ERROR 001)
- [ ] CHK016 Test title with 1 char passes validation
- [ ] CHK017 Test title with 200 chars passes validation
- [ ] CHK018 Test title with 201 chars returns (False, ERROR 002)
- [ ] CHK019 Test title with leading/trailing spaces gets stripped
- [ ] CHK020 Test title preserves internal whitespace

### Description Validation Tests

- [ ] CHK021 Test empty description returns (True, None)
- [ ] CHK022 Test description with 1000 chars passes validation
- [ ] CHK023 Test description with 1001 chars returns (False, ERROR 003)
- [ ] CHK024 Test description with leading/trailing spaces gets stripped
- [ ] CHK025 Test description preserves internal whitespace

## Unit Tests - Task Service (tests/unit/test_task_service.py)

### ID Generation Tests

- [ ] CHK026 Test generate_next_id() returns 1 when storage empty
- [ ] CHK027 Test generate_next_id() returns 2 when one task exists with ID 1
- [ ] CHK028 Test generate_next_id() returns max(ids) + 1 for multiple tasks
- [ ] CHK029 Test generate_next_id() handles non-sequential IDs correctly

### Task Creation Tests

- [ ] CHK030 Test create_task() with valid title and description
- [ ] CHK031 Test create_task() with valid title and empty description
- [ ] CHK032 Test created task has correct id (sequential)
- [ ] CHK033 Test created task has correct title (stripped)
- [ ] CHK034 Test created task has correct description (stripped)
- [ ] CHK035 Test created task has completed=False
- [ ] CHK036 Test created task has valid created_at timestamp
- [ ] CHK037 Test created task has valid updated_at timestamp
- [ ] CHK038 Test created_at equals updated_at for new tasks
- [ ] CHK039 Test task is appended to _task_storage
- [ ] CHK040 Test create_task() returns Task instance
- [ ] CHK041 Test multiple tasks get sequential IDs (1, 2, 3, ...)

## Unit Tests - Input Prompts (tests/unit/test_prompts.py)

### Mock Input Tests (using unittest.mock or pytest-mock)

- [ ] CHK042 Test get_task_title() with valid input returns stripped title
- [ ] CHK043 Test get_task_title() with empty input re-prompts
- [ ] CHK044 Test get_task_title() with whitespace-only input re-prompts
- [ ] CHK045 Test get_task_title() with > 200 chars re-prompts
- [ ] CHK046 Test get_task_title() displays ERROR 001 for empty input
- [ ] CHK047 Test get_task_title() displays ERROR 002 for > 200 chars
- [ ] CHK048 Test get_task_title() accepts valid input after errors
- [ ] CHK049 Test get_task_description() with valid input returns stripped description
- [ ] CHK050 Test get_task_description() with empty input returns empty string
- [ ] CHK051 Test get_task_description() with > 1000 chars re-prompts
- [ ] CHK052 Test get_task_description() displays ERROR 003 for > 1000 chars
- [ ] CHK053 Test get_task_description() accepts valid input after errors

## Integration Tests (tests/integration/test_add_task_flow.py)

### End-to-End User Flow Tests

- [ ] CHK054 Test complete flow: valid title + valid description → task created
- [ ] CHK055 Test complete flow: valid title + empty description → task created
- [ ] CHK056 Test flow handles empty title → displays error → accepts valid retry
- [ ] CHK057 Test flow handles title > 200 chars → displays error → accepts valid retry
- [ ] CHK058 Test flow handles description > 1000 chars → displays error → accepts valid retry
- [ ] CHK059 Test first task gets ID 1
- [ ] CHK060 Test second task gets ID 2
- [ ] CHK061 Test task appears in storage after creation
- [ ] CHK062 Test success message displayed after task created
- [ ] CHK063 Test application returns to main menu after task added

### Integration with Main Menu

- [ ] CHK064 Test selecting option 1 calls handle_add_task()
- [ ] CHK065 Test menu displays after task creation
- [ ] CHK066 Test application doesn't crash on any input sequence

## Edge Case Tests

- [ ] CHK067 Test title exactly 200 characters (boundary)
- [ ] CHK068 Test title exactly 201 characters (boundary)
- [ ] CHK069 Test description exactly 1000 characters (boundary)
- [ ] CHK070 Test description exactly 1001 characters (boundary)
- [ ] CHK071 Test title with only spaces and tabs
- [ ] CHK072 Test description with only spaces and tabs
- [ ] CHK073 Test title with unicode characters
- [ ] CHK074 Test description with unicode characters
- [ ] CHK075 Test title with newlines (should be stripped or handled)
- [ ] CHK076 Test multiple sequential task creations (ID sequence)
- [ ] CHK077 Test task storage persists across multiple adds (same session)
- [ ] CHK078 Test maximum retry attempts (multiple validation failures)

## Coverage Requirements

- [ ] CHK079 Run `uv run pytest --cov=src --cov-report=term-missing`
- [ ] CHK080 Verify 100% coverage of src/models/task.py
- [ ] CHK081 Verify 100% coverage of src/services/task_service.py
- [ ] CHK082 Verify 100% coverage of src/ui/prompts.py (validation functions)
- [ ] CHK083 Verify 100% coverage of src/constants.py (if contains logic)
- [ ] CHK084 Overall coverage ≥ 100% for core business logic
- [ ] CHK085 No untested code paths in core logic

## Test Execution

- [ ] CHK086 All unit tests pass: `uv run pytest tests/unit/`
- [ ] CHK087 All integration tests pass: `uv run pytest tests/integration/`
- [ ] CHK088 All tests pass: `uv run pytest`
- [ ] CHK089 Tests run in < 10 seconds total
- [ ] CHK090 No test warnings or deprecation notices
- [ ] CHK091 Tests are deterministic (same results on every run)
- [ ] CHK092 Tests are isolated (order-independent)

## Test Quality

- [ ] CHK093 Test names clearly describe what is being tested
- [ ] CHK094 Each test tests one specific behavior
- [ ] CHK095 Tests use arrange-act-assert pattern
- [ ] CHK096 Tests have clear failure messages
- [ ] CHK097 Mock/patch only external dependencies (input/print)
- [ ] CHK098 No hardcoded dates/times in tests (use freezegun or similar if needed)
- [ ] CHK099 Tests clean up state between runs (reset _task_storage)
- [ ] CHK100 All test assertions are meaningful (not just "assert True")

## Test Documentation

- [ ] CHK101 All test functions have docstrings
- [ ] CHK102 Test file has module-level docstring
- [ ] CHK103 Complex test setup is commented
- [ ] CHK104 Parametrized tests document parameter meanings

## Acceptance Criteria from Spec

### Success Criteria Verification

- [ ] CHK105 SC-001: Verified task creation < 30 seconds (performance test)
- [ ] CHK106 SC-002: 100% valid inputs succeed (tested all valid cases)
- [ ] CHK107 SC-003: 100% invalid inputs show correct error (tested all error cases)
- [ ] CHK108 SC-004: Sequential IDs verified (tested ID generation)
- [ ] CHK109 SC-005: ISO 8601 timestamps verified (tested timestamp format)
- [ ] CHK110 SC-006: Empty descriptions verified (tested empty description)
- [ ] CHK111 SC-007: Main menu return verified (tested navigation)

## Notes

- Mark items complete with `[x]` as tests are written and pass
- Red phase: Write tests first, verify they fail
- Green phase: Implement code, verify tests pass
- Refactor phase: Clean up code, verify tests still pass
- All 111 test checklist items must pass before feature is complete
- Coverage report should show 100% for all core business logic files
