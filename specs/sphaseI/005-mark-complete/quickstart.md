# Quickstart Implementation Guide: Mark Complete

**Feature**: Mark Complete
**Branch**: 005-mark-complete
**Date**: 2025-12-06
**Audience**: AI Code Generator / Implementation Agent

---

## Overview

This guide provides step-by-step implementation instructions for AI-generating the Mark Complete feature. Follow the order precisely to maintain dependency resolution and enable incremental testing.

**Implementation Philosophy**:
1. **Constants first** - Define all error messages and prompts upfront
2. **Service layer second** - Implement business logic with validation
3. **UI layer third** - Build user interaction components
4. **Integration last** - Wire everything together in main menu
5. **Test continuously** - Run tests after each step

---

## Prerequisites

**Required Reading**:
- [x] `spec.md` - Feature specification with acceptance criteria
- [x] `research.md` - Existing pattern analysis and design decisions
- [x] `data-model.md` - State transitions and validation rules

**Environment Setup**:
```bash
# Verify Python version
python --version  # Must be 3.13+

# Verify dependencies
uv run pytest --version  # Should work without errors
```

**Existing Files to Understand**:
- `src/models/task.py` - Task dataclass (NO CHANGES NEEDED)
- `src/services/task_service.py` - Existing task operations (ADD toggle function)
- `src/ui/prompts.py` - Existing UI patterns (ADD mark complete prompt)
- `src/constants.py` - Error codes and messages (ADD Mark Complete constants)
- `src/main.py` - Menu handler (ADD mark complete handler, UPDATE menu)

---

## Implementation Steps

### Step 1: Add Constants (src/constants.py)

**Goal**: Define all error codes, prompts, and messages for Mark Complete feature.

**Location**: Add to end of `src/constants.py` file.

**Code to Add**:

```python
# Error codes and messages - Mark Complete feature
ERROR_MARK_COMPLETE_NOT_FOUND = "ERROR 201: Task with ID {task_id} not found."
ERROR_MARK_COMPLETE_INVALID_INPUT = "ERROR 202: Invalid input. Please enter a numeric task ID."
ERROR_MARK_COMPLETE_INVALID_ID = "ERROR 203: Task ID must be a positive number."
# ERROR 204: Reserved for future use
ERROR_MARK_COMPLETE_CONFIRMATION = "ERROR 205: Invalid input. Please enter Y or N."

# Success messages - Mark Complete feature
MSG_TASK_MARKED_COMPLETE = "Task marked as complete."
MSG_TASK_MARKED_INCOMPLETE = "Task marked as incomplete."
MSG_MARK_COMPLETE_CANCELED = "Operation canceled."

# Prompts - Mark Complete feature
PROMPT_MARK_COMPLETE_ID = "Enter Task ID to mark complete/incomplete: "
```

**Quality Checks**:
- ✅ Error codes use 201-205 range (no conflicts with 001-003, 101-105)
- ✅ Messages match spec exactly (FR-019, FR-021, error messages in spec)
- ✅ Consistent formatting with existing constants (uppercase, underscores)

**Test Command**:
```bash
python -c "from src.constants import ERROR_MARK_COMPLETE_NOT_FOUND; print(ERROR_MARK_COMPLETE_NOT_FOUND.format(task_id=42))"
# Expected output: ERROR 201: Task with ID 42 not found.
```

---

### Step 2: Add Service Layer Function (src/services/task_service.py)

**Goal**: Implement `toggle_task_completion()` business logic function.

**Location**: Add to end of `src/services/task_service.py` file (after `delete_task()`).

**Code to Add**:

```python
def toggle_task_completion(task_id: int) -> Task:
    """Toggle a task's completion status between complete and incomplete.

    Args:
        task_id: The unique identifier of the task to toggle

    Returns:
        Updated Task object with toggled completed field and new updated_at timestamp

    Raises:
        ValueError: If task_id <= 0 (ERROR 103)
        ValueError: If no task with task_id exists (ERROR 101)
    """
    # Reuse get_task_by_id() for validation and retrieval
    task = get_task_by_id(task_id)

    # Toggle completed status (False → True or True → False)
    task.completed = not task.completed

    # Update timestamp (same pattern as update_task)
    task.updated_at = Task.generate_timestamp()

    return task
```

**Design Rationale**:
- **Reuses `get_task_by_id()`**: Inherits validation for task ID and existence (DRY principle)
- **Idiomatic toggle**: `not task.completed` is Pythonic and clear
- **Timestamp pattern**: Matches `update_task()` pattern exactly (consistency)
- **Returns Task**: Allows caller to access new status/timestamp if needed

**Quality Checks**:
- ✅ Type hints on all parameters and return type
- ✅ Google-style docstring with Args, Returns, Raises sections
- ✅ Reuses existing helper function (no code duplication)
- ✅ Updates `updated_at` unconditionally (spec requirement FR-016)
- ✅ Does NOT modify `created_at` (spec requirement FR-017)

**Test Command**:
```bash
uv run pytest tests/unit/test_task_service.py::test_toggle_task_completion -v
# (Create test first in Step 5)
```

---

### Step 3: Add UI Layer Functions (src/ui/prompts.py)

**Goal**: Implement confirmation prompt and orchestration function for Mark Complete workflow.

**Location**: Add to end of `src/ui/prompts.py` file (after `delete_task_prompt()`).

**Import Updates** (add to top of file):

```python
from src.constants import (
    # ... existing imports ...
    ERROR_MARK_COMPLETE_CONFIRMATION,
    MSG_MARK_COMPLETE_CANCELED,
    MSG_TASK_MARKED_COMPLETE,
    MSG_TASK_MARKED_INCOMPLETE,
    PROMPT_MARK_COMPLETE_ID,
)
from src.services.task_service import (
    # ... existing imports ...
    toggle_task_completion,
)
```

**Code to Add**:

```python
def prompt_for_mark_complete_confirmation(task_title: str, current_status: bool) -> bool:
    """Prompt user to confirm task completion status toggle with Y/N response.

    Args:
        task_title: Title of the task to toggle (for context)
        current_status: Current completion status (True = complete, False = incomplete)

    Returns:
        True if user confirms toggle (Y/y), False if user cancels (N/n)
    """
    # Dynamic prompt based on current status
    action = "complete" if not current_status else "incomplete"
    prompt = f"Mark task '{task_title}' as {action}? (Y/N): "

    while True:
        # Get user input and normalize (strip whitespace, uppercase)
        response = input(prompt).strip().upper()

        # Check for confirmation
        if response == "Y":
            return True

        # Check for cancellation
        if response == "N":
            return False

        # Invalid response - show error and re-prompt
        print(ERROR_MARK_COMPLETE_CONFIRMATION)


def mark_complete_prompt() -> None:
    """Orchestrate the complete mark complete/incomplete workflow with user interaction.

    Workflow:
        1. Prompt for task ID and validate
        2. Retrieve task (validates existence)
        3. Display confirmation prompt with dynamic action (complete/incomplete)
        4. On confirmation: toggle status, update timestamp, show success
        5. On cancellation: show cancellation message, no changes
        6. On error: show error message, return to main menu
    """
    try:
        # Step 1: Get and validate task ID
        task_id = prompt_for_task_id()

        # Step 2: Retrieve task (validates existence)
        task = get_task_by_id(task_id)

    except ValueError as e:
        # Handle ID validation errors (ERROR 101, 102, 103)
        print(str(e))
        return  # Return to main menu without showing confirmation

    # Step 3: Get user confirmation (shows task title and action for context)
    confirmed = prompt_for_mark_complete_confirmation(task.title, task.completed)

    # Step 4: Execute toggle or cancellation
    if confirmed:
        # User confirmed with Y/y
        toggle_task_completion(task_id)

        # Determine success message based on NEW status
        # Note: task.completed was toggled inside toggle_task_completion()
        if task.completed:
            print(MSG_TASK_MARKED_COMPLETE)
        else:
            print(MSG_TASK_MARKED_INCOMPLETE)
    else:
        # User canceled with N/n
        print(MSG_MARK_COMPLETE_CANCELED)
```

**Design Rationale**:
- **Mirrors `delete_task_prompt()` structure**: Consistent workflow pattern (ID → retrieve → confirm → execute/cancel)
- **Dynamic confirmation prompt**: Changes "complete" vs "incomplete" based on current status (clear user intent)
- **Dynamic success message**: Reflects new status, not action verb (confirms outcome)
- **Reuses `prompt_for_task_id()`**: No duplication of validation logic
- **Early return on error**: Prevents confirmation prompt if task doesn't exist (UX improvement)

**Quality Checks**:
- ✅ Type hints on all parameters and return types
- ✅ Google-style docstrings with detailed workflow documentation
- ✅ Follows existing patterns (delete_task_prompt structure)
- ✅ Indefinite retry loop for invalid confirmation (spec requirement)
- ✅ Whitespace stripped, case-insensitive comparison (spec requirement FR-012, FR-010)

**Test Command**:
```bash
uv run pytest tests/unit/test_prompts.py::test_mark_complete_prompt -v
# (Create test first in Step 5)
```

---

### Step 4: Wire Into Main Menu (src/main.py)

**Goal**: Add menu handler and enable menu option 6 for Mark Complete.

**Import Updates** (add to top of file):

```python
from src.ui.prompts import (
    # ... existing imports ...
    mark_complete_prompt,
)
```

**Code to Add** (insert before `main()` function):

```python
def handle_mark_complete() -> None:
    """Handle Mark Complete user flow.

    Prompts user for task ID, displays confirmation with dynamic action
    (complete/incomplete), toggles task status on confirmation, and updates
    timestamp. Returns to main menu after completion or cancellation.
    """
    mark_complete_prompt()
```

**Code to Modify** (in `main()` function):

**BEFORE**:
```python
        elif choice == "5":
            delete_task_prompt()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Feature not yet implemented or invalid option.")
```

**AFTER**:
```python
        elif choice == "5":
            delete_task_prompt()
        elif choice == "6":
            handle_mark_complete()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please select 1-7.")
```

**Design Rationale**:
- **Consistent handler pattern**: Mirrors `handle_add_task()`, `handle_view_tasks()`, etc.
- **Delegates to UI layer**: Handler only calls prompt function (separation of concerns)
- **Updated error message**: Changes "Feature not yet implemented" to "Invalid option" (all features complete)

**Quality Checks**:
- ✅ Handler function has type hints and docstring
- ✅ Menu option 6 now calls handler (was placeholder)
- ✅ Error message updated to reflect completion of all features

**Manual Test**:
```bash
uv run python src/main.py
# Select option 6
# Should see: "Enter Task ID to mark complete/incomplete: "
```

---

### Step 5: Write Unit Tests

**Goal**: Create comprehensive unit tests for service and UI layers.

#### 5a. Service Layer Tests (tests/unit/test_task_service.py)

**Location**: Add to end of `tests/unit/test_task_service.py`.

**Code to Add**:

```python
def test_toggle_incomplete_to_complete():
    """Test toggling task from incomplete to complete updates status and timestamp."""
    # Setup: Create incomplete task
    task = create_task("Buy groceries", "Milk and eggs")
    original_updated_at = task.updated_at
    assert task.completed is False

    # Execute: Toggle to complete
    result = toggle_task_completion(task.id)

    # Verify: Status changed to True
    assert result.completed is True
    # Verify: Timestamp updated
    assert result.updated_at != original_updated_at
    # Verify: Other fields unchanged
    assert result.id == task.id
    assert result.title == "Buy groceries"
    assert result.description == "Milk and eggs"
    assert result.created_at == task.created_at


def test_toggle_complete_to_incomplete():
    """Test toggling task from complete to incomplete updates status and timestamp."""
    # Setup: Create task and mark it complete
    task = create_task("Finish project", "Submit by Friday")
    toggle_task_completion(task.id)  # Now complete
    original_updated_at = task.updated_at
    assert task.completed is True

    # Execute: Toggle back to incomplete
    result = toggle_task_completion(task.id)

    # Verify: Status changed to False
    assert result.completed is False
    # Verify: Timestamp updated
    assert result.updated_at != original_updated_at
    # Verify: Other fields unchanged
    assert result.id == task.id
    assert result.title == "Finish project"


def test_toggle_updates_timestamp():
    """Test that toggle always updates updated_at timestamp."""
    # Setup
    task = create_task("Test task", "Description")
    original_updated_at = task.updated_at

    # Execute: Toggle (doesn't matter which direction)
    toggle_task_completion(task.id)

    # Verify: Timestamp is different
    assert task.updated_at != original_updated_at


def test_toggle_preserves_created_at():
    """Test that toggle never modifies created_at timestamp."""
    # Setup
    task = create_task("Test task", "Description")
    original_created_at = task.created_at

    # Execute: Toggle multiple times
    toggle_task_completion(task.id)
    toggle_task_completion(task.id)
    toggle_task_completion(task.id)

    # Verify: created_at never changed
    assert task.created_at == original_created_at


def test_toggle_nonexistent_task():
    """Test toggling non-existent task raises ValueError with ERROR 101."""
    # Setup: Empty task list
    from src.services.task_service import _task_storage
    _task_storage.clear()

    # Execute & Verify: Raises ValueError with task not found message
    with pytest.raises(ValueError, match="ERROR 101: Task with ID 999 not found"):
        toggle_task_completion(999)


def test_toggle_zero_task_id():
    """Test toggling with zero task ID raises ValueError with ERROR 103."""
    # Execute & Verify: Raises ValueError for invalid ID
    with pytest.raises(ValueError, match="ERROR 103: Task ID must be a positive number"):
        toggle_task_completion(0)


def test_toggle_negative_task_id():
    """Test toggling with negative task ID raises ValueError with ERROR 103."""
    # Execute & Verify: Raises ValueError for invalid ID
    with pytest.raises(ValueError, match="ERROR 103: Task ID must be a positive number"):
        toggle_task_completion(-5)
```

#### 5b. UI Layer Tests (tests/unit/test_prompts.py)

**Location**: Add to end of `tests/unit/test_prompts.py`.

**Code to Add**:

```python
from unittest.mock import patch, call
from src.ui.prompts import prompt_for_mark_complete_confirmation, mark_complete_prompt


def test_prompt_for_mark_complete_confirmation_yes_uppercase():
    """Test confirmation returns True for 'Y' input."""
    with patch("builtins.input", return_value="Y"):
        result = prompt_for_mark_complete_confirmation("Test task", False)
        assert result is True


def test_prompt_for_mark_complete_confirmation_yes_lowercase():
    """Test confirmation returns True for 'y' input."""
    with patch("builtins.input", return_value="y"):
        result = prompt_for_mark_complete_confirmation("Test task", False)
        assert result is True


def test_prompt_for_mark_complete_confirmation_no_uppercase():
    """Test confirmation returns False for 'N' input."""
    with patch("builtins.input", return_value="N"):
        result = prompt_for_mark_complete_confirmation("Test task", True)
        assert result is False


def test_prompt_for_mark_complete_confirmation_no_lowercase():
    """Test confirmation returns False for 'n' input."""
    with patch("builtins.input", return_value="n"):
        result = prompt_for_mark_complete_confirmation("Test task", True)
        assert result is False


def test_prompt_for_mark_complete_confirmation_with_whitespace():
    """Test confirmation strips whitespace before validation."""
    with patch("builtins.input", return_value="  Y  "):
        result = prompt_for_mark_complete_confirmation("Test task", False)
        assert result is True


def test_prompt_for_mark_complete_confirmation_invalid_then_valid():
    """Test confirmation retries on invalid input then accepts valid."""
    with patch("builtins.input", side_effect=["yes", "maybe", "Y"]):
        with patch("builtins.print") as mock_print:
            result = prompt_for_mark_complete_confirmation("Test task", False)
            assert result is True
            # Verify error message printed twice (for "yes" and "maybe")
            assert mock_print.call_count == 2


def test_prompt_for_mark_complete_confirmation_dynamic_prompt_incomplete():
    """Test confirmation prompt shows 'complete' for incomplete tasks."""
    with patch("builtins.input", return_value="Y") as mock_input:
        prompt_for_mark_complete_confirmation("Buy milk", False)
        # Verify prompt includes "as complete"
        mock_input.assert_called_with("Mark task 'Buy milk' as complete? (Y/N): ")


def test_prompt_for_mark_complete_confirmation_dynamic_prompt_complete():
    """Test confirmation prompt shows 'incomplete' for complete tasks."""
    with patch("builtins.input", return_value="Y") as mock_input:
        prompt_for_mark_complete_confirmation("Buy milk", True)
        # Verify prompt includes "as incomplete"
        mock_input.assert_called_with("Mark task 'Buy milk' as incomplete? (Y/N): ")


def test_mark_complete_prompt_full_flow_confirm():
    """Test mark complete prompt with valid ID and confirmation."""
    # Setup: Create task
    from src.services.task_service import create_task
    task = create_task("Test task", "Description")

    # Mock user inputs: task ID "1", then "Y"
    with patch("builtins.input", side_effect=["1", "Y"]):
        with patch("builtins.print") as mock_print:
            mark_complete_prompt()
            # Verify success message printed
            mock_print.assert_called_with("Task marked as complete.")


def test_mark_complete_prompt_full_flow_cancel():
    """Test mark complete prompt with valid ID and cancellation."""
    # Setup: Create task
    from src.services.task_service import create_task
    task = create_task("Test task", "Description")

    # Mock user inputs: task ID "1", then "N"
    with patch("builtins.input", side_effect=["1", "N"]):
        with patch("builtins.print") as mock_print:
            mark_complete_prompt()
            # Verify cancellation message printed
            mock_print.assert_called_with("Operation canceled.")


def test_mark_complete_prompt_invalid_task_id():
    """Test mark complete prompt with non-existent task ID."""
    # Mock user input: non-existent task ID
    with patch("builtins.input", return_value="999"):
        with patch("builtins.print") as mock_print:
            mark_complete_prompt()
            # Verify error message printed
            mock_print.assert_called_with("ERROR 101: Task with ID 999 not found.")
```

**Test Execution**:
```bash
uv run pytest tests/unit/test_task_service.py -v
uv run pytest tests/unit/test_prompts.py -v
```

---

### Step 6: Write Integration Tests

**Goal**: Create end-to-end integration tests for complete user workflows.

**Location**: Create new file `tests/integration/test_mark_complete_flow.py`.

**Code to Create**:

```python
"""Integration tests for Mark Complete feature end-to-end workflows."""

from unittest.mock import patch

import pytest

from src.services.task_service import _task_storage, create_task


@pytest.fixture(autouse=True)
def reset_storage():
    """Clear task storage before each test."""
    _task_storage.clear()
    yield
    _task_storage.clear()


def test_mark_complete_flow_incomplete_to_complete():
    """Test complete flow: create task → mark complete → verify status changed."""
    # Setup: Create incomplete task
    task = create_task("Buy groceries", "Milk and eggs")
    assert task.completed is False
    original_updated_at = task.updated_at

    # Execute: Simulate user selecting Mark Complete, entering ID 1, confirming Y
    with patch("builtins.input", side_effect=["1", "Y"]):
        from src.ui.prompts import mark_complete_prompt

        mark_complete_prompt()

    # Verify: Task is now marked complete
    assert task.completed is True
    # Verify: Timestamp updated
    assert task.updated_at != original_updated_at
    # Verify: Other fields unchanged
    assert task.title == "Buy groceries"
    assert task.description == "Milk and eggs"


def test_mark_complete_flow_complete_to_incomplete():
    """Test complete flow: create task → mark complete → mark incomplete → verify toggle."""
    # Setup: Create task and mark it complete
    task = create_task("Finish project", "Submit by Friday")
    with patch("builtins.input", side_effect=["1", "Y"]):
        from src.ui.prompts import mark_complete_prompt

        mark_complete_prompt()  # Now complete

    assert task.completed is True

    # Execute: Mark incomplete
    with patch("builtins.input", side_effect=["1", "Y"]):
        mark_complete_prompt()

    # Verify: Task is back to incomplete
    assert task.completed is False


def test_mark_complete_flow_cancellation():
    """Test complete flow: create task → attempt mark complete → cancel → verify no change."""
    # Setup: Create incomplete task
    task = create_task("Write tests", "Unit and integration")
    assert task.completed is False
    original_updated_at = task.updated_at

    # Execute: Simulate user canceling with N
    with patch("builtins.input", side_effect=["1", "N"]):
        from src.ui.prompts import mark_complete_prompt

        mark_complete_prompt()

    # Verify: Task status unchanged
    assert task.completed is False
    # Verify: Timestamp unchanged
    assert task.updated_at == original_updated_at


def test_mark_complete_flow_invalid_id_non_numeric():
    """Test error handling for non-numeric task ID input."""
    # Setup: Create task
    create_task("Test task", "Description")

    # Execute: Simulate user entering non-numeric ID, then numeric, then canceling
    with patch("builtins.input", side_effect=["abc", "1", "N"]):
        with patch("builtins.print") as mock_print:
            from src.ui.prompts import mark_complete_prompt

            mark_complete_prompt()

            # Verify: Error message printed for "abc" (first call)
            # Note: exact call order depends on implementation
            error_calls = [call for call in mock_print.call_args_list if "ERROR 102" in str(call)]
            assert len(error_calls) >= 1


def test_mark_complete_flow_invalid_id_zero():
    """Test error handling for zero task ID input."""
    # Setup: Create task
    create_task("Test task", "Description")

    # Execute: Simulate user entering 0, then 1, then canceling
    with patch("builtins.input", side_effect=["0", "1", "N"]):
        with patch("builtins.print") as mock_print:
            from src.ui.prompts import mark_complete_prompt

            mark_complete_prompt()

            # Verify: Error message printed for "0"
            error_calls = [call for call in mock_print.call_args_list if "ERROR 103" in str(call)]
            assert len(error_calls) >= 1


def test_mark_complete_flow_nonexistent_task():
    """Test error handling for non-existent task ID."""
    # Setup: Create task with ID 1
    create_task("Test task", "Description")

    # Execute: Simulate user entering ID 999 (doesn't exist)
    with patch("builtins.input", return_value="999"):
        with patch("builtins.print") as mock_print:
            from src.ui.prompts import mark_complete_prompt

            mark_complete_prompt()

            # Verify: Error message printed and no confirmation prompt shown
            mock_print.assert_called_with("ERROR 101: Task with ID 999 not found.")


def test_mark_complete_flow_invalid_confirmation():
    """Test error handling for invalid confirmation input (retries until valid)."""
    # Setup: Create task
    create_task("Test task", "Description")

    # Execute: Simulate user entering ID 1, then invalid confirmations, then N
    with patch("builtins.input", side_effect=["1", "yes", "maybe", "1", "N"]):
        with patch("builtins.print") as mock_print:
            from src.ui.prompts import mark_complete_prompt

            mark_complete_prompt()

            # Verify: Error message printed for invalid confirmations
            error_calls = [call for call in mock_print.call_args_list if "ERROR 205" in str(call)]
            assert len(error_calls) >= 2  # "yes" and "maybe"


def test_mark_complete_flow_multiple_toggles():
    """Test multiple consecutive toggles alternate status correctly."""
    # Setup: Create task
    task = create_task("Toggle test", "Test description")

    # Execute: Toggle 5 times
    for i in range(5):
        expected_status = (i + 1) % 2 == 1  # Odd iterations = complete, even = incomplete
        with patch("builtins.input", side_effect=["1", "Y"]):
            from src.ui.prompts import mark_complete_prompt

            mark_complete_prompt()

        # Verify: Status matches expected
        assert task.completed is expected_status


def test_mark_complete_flow_empty_task_list():
    """Test error handling when attempting to mark complete with no tasks."""
    # Setup: Empty task list (cleared by fixture)

    # Execute: Simulate user entering any task ID
    with patch("builtins.input", return_value="1"):
        with patch("builtins.print") as mock_print:
            from src.ui.prompts import mark_complete_prompt

            mark_complete_prompt()

            # Verify: Error message printed
            mock_print.assert_called_with("ERROR 101: Task with ID 1 not found.")
```

**Test Execution**:
```bash
uv run pytest tests/integration/test_mark_complete_flow.py -v
```

---

### Step 7: Run Full Test Suite

**Goal**: Verify all tests pass before committing.

**Commands**:

```bash
# Run all tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Verify code quality
uv run ruff check .
uv run ruff format --check .

# Manual smoke test
uv run python src/main.py
```

**Expected Results**:
- ✅ All unit tests pass (test_task_service.py, test_prompts.py)
- ✅ All integration tests pass (test_mark_complete_flow.py)
- ✅ 100% test coverage on new code
- ✅ Ruff linter: 0 errors
- ✅ Ruff formatter: all files correctly formatted
- ✅ Manual test: Menu option 6 works end-to-end

---

## Testing Checklist

Before marking implementation complete, verify ALL acceptance scenarios from spec.md:

### User Story 1: Toggle Task to Complete

- [ ] **Scenario 1**: Incomplete task + ID "2" + confirm "Y" → Task marked complete, timestamp updated
- [ ] **Scenario 2**: 3 tasks, mark task 2 complete → Task 2 complete, tasks 1 and 3 unchanged
- [ ] **Scenario 3**: Confirm with "y" (lowercase) → Treated as "Y", task marked complete

### User Story 2: Toggle Task to Incomplete

- [ ] **Scenario 1**: Complete task + ID "3" + confirm "Y" → Task marked incomplete, timestamp updated
- [ ] **Scenario 2**: 3 tasks, toggle task 2 (complete→incomplete) → Task 2 incomplete, others unchanged

### User Story 3: Cancel Status Change Operation

- [ ] **Scenario 1**: Valid ID + cancel "N" → Operation canceled, task unchanged
- [ ] **Scenario 2**: Cancel with "n" (lowercase) → Treated as "N", operation canceled
- [ ] **Scenario 3**: Invalid confirmation ("yes", "no", "1") → ERROR 205, re-prompt

### User Story 4: Handle Invalid Status Change Attempts

- [ ] **Scenario 1**: Non-existent task ID 3 → ERROR 201, return to menu (no confirmation)
- [ ] **Scenario 2**: Non-numeric ID "abc" → ERROR 202, re-prompt for ID
- [ ] **Scenario 3**: Zero or negative ID → ERROR 203, re-prompt for ID
- [ ] **Scenario 4**: Empty task list, any ID → ERROR 201, return to menu

---

## Common Implementation Errors to Avoid

### Error 1: Using Wrong Error Codes
❌ **WRONG**: Reusing ERROR 101, 102, 103 directly
✅ **CORRECT**: Use ERROR 201, 202, 203 (feature-specific codes per spec)

### Error 2: Static Confirmation Prompt
❌ **WRONG**: `prompt = "Mark task complete? (Y/N): "` (always same text)
✅ **CORRECT**: `action = "complete" if not current_status else "incomplete"` (dynamic)

### Error 3: Wrong Success Message
❌ **WRONG**: Always print "Task marked as complete."
✅ **CORRECT**: Check new status: `if task.completed: print(MSG_TASK_MARKED_COMPLETE)`

### Error 4: Forgetting Timestamp Update
❌ **WRONG**: Only toggle `task.completed = not task.completed`
✅ **CORRECT**: Also update `task.updated_at = Task.generate_timestamp()`

### Error 5: Modifying created_at
❌ **WRONG**: Updating `task.created_at` during toggle
✅ **CORRECT**: NEVER modify `created_at` (spec requirement FR-017)

### Error 6: Limited Retry on Confirmation
❌ **WRONG**: `for i in range(3): # retry 3 times`
✅ **CORRECT**: `while True:` (indefinite retry per spec FR-011)

### Error 7: Not Stripping Whitespace
❌ **WRONG**: `if response == "Y":`
✅ **CORRECT**: `if response.strip().upper() == "Y":`

---

## File Modification Summary

| File | Change Type | Lines Modified (Approx) |
|------|-------------|-------------------------|
| `src/constants.py` | Add | +10 lines |
| `src/services/task_service.py` | Add | +25 lines |
| `src/ui/prompts.py` | Add | +75 lines |
| `src/main.py` | Modify + Add | +10 lines |
| `tests/unit/test_task_service.py` | Add | +80 lines |
| `tests/unit/test_prompts.py` | Add | +90 lines |
| `tests/integration/test_mark_complete_flow.py` | Create | +150 lines |
| **TOTAL** | | **~440 lines** |

---

## Post-Implementation Checklist

- [ ] All constants added to `src/constants.py`
- [ ] `toggle_task_completion()` function added to `src/services/task_service.py`
- [ ] `prompt_for_mark_complete_confirmation()` and `mark_complete_prompt()` added to `src/ui/prompts.py`
- [ ] `handle_mark_complete()` handler added to `src/main.py`
- [ ] Menu option 6 enabled in `main()` function
- [ ] Unit tests created for service layer (7 tests)
- [ ] Unit tests created for UI layer (10 tests)
- [ ] Integration tests created (10 tests)
- [ ] All tests pass: `uv run pytest`
- [ ] Code quality checks pass: `uv run ruff check .` and `uv run ruff format --check .`
- [ ] Manual smoke test completed successfully
- [ ] Test coverage 100% on new code: `uv run pytest --cov=src`

---

## Completion Criteria

**Definition of Done**:
1. ✅ All functional requirements (FR-001 to FR-024) implemented
2. ✅ All acceptance scenarios (4 user stories, 11 scenarios) pass
3. ✅ All edge cases handled (empty list, invalid inputs, rapid toggles)
4. ✅ 100% test coverage on new code
5. ✅ Code quality checks pass (Ruff linter + formatter)
6. ✅ Manual testing confirms expected behavior
7. ✅ No violations of constitution principles

**When all criteria met**: Feature is ready for pull request and merge to main.

---

## Support Resources

**Specification Files**:
- `specs/005-mark-complete/spec.md` - Detailed requirements and acceptance criteria
- `specs/005-mark-complete/research.md` - Existing pattern analysis
- `specs/005-mark-complete/data-model.md` - State transitions and validation rules
- `.specify/memory/constitution.md` - Project principles and constraints

**Code References**:
- `src/ui/prompts.py:270-322` - `delete_task_prompt()` pattern to mirror
- `src/services/task_service.py:79-109` - `update_task()` timestamp pattern
- `src/models/task.py:28-34` - `Task.generate_timestamp()` method

**Test References**:
- `tests/unit/test_task_service.py` - Existing service layer test patterns
- `tests/integration/test_delete_task_flow.py` - Existing integration test patterns

---

**Status**: ✅ Quickstart guide complete - Ready for AI code generation
