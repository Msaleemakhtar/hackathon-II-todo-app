# Quickstart Guide: Delete Task Implementation

**Feature**: Delete Task (004-delete-task)
**Date**: 2025-12-06
**Audience**: AI agents implementing this feature

## Overview

Implement the Delete Task feature by adding 3 new functions and extending 1 existing module. This feature allows users to permanently remove tasks from the in-memory task list with confirmation.

**Total Work**: ~150 lines of new code + ~20 lines of test code

## Prerequisites

✅ Feature specification exists at `specs/004-delete-task/spec.md`
✅ Planning artifacts generated:
- `specs/004-delete-task/plan.md`
- `specs/004-delete-task/research.md`
- `specs/004-delete-task/data-model.md`
- `specs/004-delete-task/contracts/*.md`

## Implementation Checklist

### Step 1: Add Constants (1 file, ~5 minutes)

**File**: `src/constants.py`

**Action**: Add new error code and success messages to the end of the file

**New Constants**:
```python
# Error codes and messages - Delete Task feature
ERROR_INVALID_CONFIRMATION = "ERROR 105: Invalid input. Please enter Y or N."

# Success/cancellation messages - Delete Task feature
MSG_TASK_DELETED = "Task deleted successfully."
MSG_DELETION_CANCELED = "Deletion canceled."
```

**Validation**:
- [ ] Constants follow existing naming convention
- [ ] ERROR 105 is next available error code (ERROR 104 used by Update Task)
- [ ] Messages match spec exactly (FR-016, FR-020)

---

### Step 2: Implement Business Logic (1 file, ~10 minutes)

**File**: `src/services/task_service.py`

**Action**: Add `delete_task()` function at the end of the file

**New Function**:
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
    # Validate task_id and retrieve task (raises ValueError on error)
    task = get_task_by_id(task_id)

    # Remove task from storage
    _task_storage.remove(task)

    # Return deleted task (for title display in UI layer)
    return task
```

**Validation**:
- [ ] Function reuses `get_task_by_id()` for validation
- [ ] Uses `list.remove(task)` (not index-based deletion)
- [ ] Returns deleted Task object (needed for confirmation message)
- [ ] No ID renumbering logic (per FR-017)
- [ ] Follows existing code style (type hints, docstring)

---

### Step 3: Implement UI Functions (1 file, ~20 minutes)

**File**: `src/ui/prompts.py`

**Action**: Add 2 new functions at the end of the file

#### Function 3a: Confirmation Prompt

**New Function**:
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
        # Get user input and normalize (strip whitespace, uppercase)
        response = input(prompt).strip().upper()

        # Check for confirmation
        if response == "Y":
            return True

        # Check for cancellation
        if response == "N":
            return False

        # Invalid response - show error and re-prompt
        print(ERROR_INVALID_CONFIRMATION)
```

**Validation**:
- [ ] Case-insensitive (accepts Y/y/N/n per FR-010, FR-013, FR-014)
- [ ] Strips whitespace (per FR-012)
- [ ] Shows task title in prompt (per FR-008)
- [ ] Validation loop for invalid inputs (per FR-011)
- [ ] Uses ERROR_INVALID_CONFIRMATION constant

#### Function 3b: Delete Workflow Orchestration

**New Function**:
```python
def delete_task_prompt() -> None:
    """Orchestrate the complete delete task workflow with user interaction."""
    try:
        # Step 1: Get and validate task ID
        task_id = prompt_for_task_id()

        # Step 2: Retrieve task (validates existence)
        task = get_task_by_id(task_id)

    except ValueError as e:
        # Handle ID validation errors (ERROR 101, 102, 103)
        print(str(e))
        return  # Return to main menu without showing confirmation

    # Step 3: Get user confirmation (shows task title for context)
    confirmed = prompt_for_delete_confirmation(task.title)

    # Step 4: Execute deletion or cancellation
    if confirmed:
        # User confirmed with Y/y
        delete_task(task_id)
        print(MSG_TASK_DELETED)
    else:
        # User canceled with N/n
        print(MSG_DELETION_CANCELED)
```

**Validation**:
- [ ] Reuses `prompt_for_task_id()` (existing function)
- [ ] Catches ValueError for ERROR 101/102/103 (per FR-007, FR-005, FR-004)
- [ ] Returns to menu on error without confirmation (per FR-007)
- [ ] Displays success message on deletion (per FR-016)
- [ ] Displays cancellation message on cancel (per FR-020)
- [ ] Imports `delete_task` from `task_service`
- [ ] Imports constants: `MSG_TASK_DELETED`, `MSG_DELETION_CANCELED`

**Required Imports** (add to top of `prompts.py`):
```python
from src.constants import (
    # ... existing imports ...
    ERROR_INVALID_CONFIRMATION,  # NEW
    MSG_TASK_DELETED,            # NEW
    MSG_DELETION_CANCELED,       # NEW
)
from src.services.task_service import get_task_by_id, update_task, delete_task  # Add delete_task
```

---

### Step 4: Integrate with Main Menu (1 file, ~5 minutes)

**File**: `src/main.py`

**Action**: Add "Delete Task" menu option at position 4

**Changes Required**:

1. **Import Statement** (top of file):
```python
from src.ui.prompts import (
    add_task_prompt,
    view_task_prompt,
    update_task_prompt,
    delete_task_prompt,  # NEW
    mark_complete_prompt,
)
```

2. **Menu Display** (in `main()` function):
```python
print("\n--- Todo App ---")
print("1. Add Task")
print("2. View Tasks")
print("3. Update Task")
print("4. Delete Task")      # NEW
print("5. Mark Complete")    # RENUMBERED (was 4)
print("6. Exit")             # RENUMBERED (was 5)
```

3. **Menu Handler** (in `main()` function):
```python
if choice == "1":
    add_task_prompt()
elif choice == "2":
    view_task_prompt()
elif choice == "3":
    update_task_prompt()
elif choice == "4":
    delete_task_prompt()     # NEW
elif choice == "5":
    mark_complete_prompt()   # RENUMBERED (was choice == "4")
elif choice == "6":
    break                    # RENUMBERED (was choice == "5")
else:
    print("Invalid option.")
```

**Validation**:
- [ ] Menu option 4 is "Delete Task"
- [ ] Mark Complete renumbered to option 5
- [ ] Exit renumbered to option 6
- [ ] `delete_task_prompt()` called when choice == "4"
- [ ] Import statement includes `delete_task_prompt`

---

## Testing Implementation

### Step 5: Unit Tests for Business Logic (~15 minutes)

**File**: `tests/unit/test_task_service.py`

**Action**: Add test class for `delete_task()` function

**Test Cases**:
```python
class TestDeleteTask:
    """Unit tests for delete_task() function."""

    def test_delete_existing_task(self):
        """Delete existing task removes it from storage and returns task."""
        # Setup: Create 3 tasks
        # Action: delete_task(task_id=2)
        # Assert: task 2 removed, tasks 1 and 3 unchanged, returns deleted task

    def test_delete_non_existent_task(self):
        """Delete non-existent task raises ValueError with ERROR 101."""
        # Setup: Create tasks with IDs [1, 2, 3]
        # Action: delete_task(task_id=99)
        # Assert: Raises ValueError, message contains "ERROR 101"

    def test_delete_with_invalid_id_zero(self):
        """Delete with ID 0 raises ValueError with ERROR 103."""
        # Action: delete_task(task_id=0)
        # Assert: Raises ValueError, message contains "ERROR 103"

    def test_delete_with_negative_id(self):
        """Delete with negative ID raises ValueError with ERROR 103."""
        # Action: delete_task(task_id=-5)
        # Assert: Raises ValueError, message contains "ERROR 103"

    def test_delete_last_remaining_task(self):
        """Delete only task in list results in empty storage."""
        # Setup: Create 1 task
        # Action: delete_task(task_id=1)
        # Assert: _task_storage is empty list

    def test_delete_does_not_renumber_ids(self):
        """Deleting middle task preserves IDs of remaining tasks."""
        # Setup: Create tasks with IDs [1, 2, 3, 4, 5]
        # Action: delete_task(task_id=3)
        # Assert: Remaining IDs are [1, 2, 4, 5] (not [1, 2, 3, 4])
```

**Validation**:
- [ ] All 6 test cases implemented
- [ ] Tests use pytest fixtures for setup/teardown
- [ ] Error messages validated (ERROR 101, 103)
- [ ] ID preservation tested (FR-017)

---

### Step 6: Unit Tests for UI Functions (~20 minutes)

**File**: `tests/unit/test_prompts.py`

**Action**: Add test class for confirmation prompt

**Test Cases**:
```python
class TestPromptForDeleteConfirmation:
    """Unit tests for prompt_for_delete_confirmation() function."""

    def test_confirm_with_uppercase_y(self, monkeypatch):
        """Input 'Y' returns True."""
        # Mock input() to return "Y"
        # Assert: returns True

    def test_confirm_with_lowercase_y(self, monkeypatch):
        """Input 'y' returns True."""
        # Mock input() to return "y"
        # Assert: returns True

    def test_cancel_with_uppercase_n(self, monkeypatch):
        """Input 'N' returns False."""
        # Mock input() to return "N"
        # Assert: returns False

    def test_cancel_with_lowercase_n(self, monkeypatch):
        """Input 'n' returns False."""
        # Mock input() to return "n"
        # Assert: returns False

    def test_strips_whitespace(self, monkeypatch):
        """Input ' Y ' (with spaces) returns True."""
        # Mock input() to return " Y "
        # Assert: returns True

    def test_invalid_then_valid_response(self, monkeypatch, capsys):
        """Invalid input shows ERROR 105, then re-prompts."""
        # Mock input() to return ["maybe", "Y"]
        # Assert: returns True, ERROR 105 printed once
```

**Validation**:
- [ ] All 6 test cases implemented
- [ ] Uses monkeypatch for input() mocking
- [ ] Uses capsys for error message verification
- [ ] Case insensitivity tested (FR-010, FR-013, FR-014)
- [ ] Whitespace stripping tested (FR-012)

---

### Step 7: Integration Tests (~25 minutes)

**File**: `tests/integration/test_delete_task_flow.py`

**Action**: Create new file with end-to-end delete workflow tests

**Test Cases**:
```python
class TestDeleteTaskFlow:
    """Integration tests for complete delete task workflow."""

    def test_successful_deletion_with_confirmation(self, monkeypatch, capsys):
        """Valid ID + Y confirmation deletes task and shows success message."""
        # Setup: Create 3 tasks
        # Mock input: ["2", "Y"]
        # Call: delete_task_prompt()
        # Assert: Task 2 deleted, MSG_TASK_DELETED printed

    def test_cancel_deletion_preserves_task(self, monkeypatch, capsys):
        """Valid ID + N response preserves task and shows cancellation."""
        # Setup: Create 2 tasks
        # Mock input: ["1", "N"]
        # Call: delete_task_prompt()
        # Assert: Task 1 preserved, MSG_DELETION_CANCELED printed

    def test_invalid_id_format_shows_error(self, monkeypatch, capsys):
        """Non-numeric ID shows ERROR 102 and returns to menu."""
        # Setup: Create tasks
        # Mock input: ["abc"]
        # Call: delete_task_prompt()
        # Assert: ERROR 102 printed, no confirmation prompt, storage unchanged

    def test_zero_id_shows_error(self, monkeypatch, capsys):
        """ID 0 shows ERROR 103 and returns to menu."""
        # Mock input: ["0"]
        # Assert: ERROR 103 printed, storage unchanged

    def test_negative_id_shows_error(self, monkeypatch, capsys):
        """Negative ID shows ERROR 103 and returns to menu."""
        # Mock input: ["-5"]
        # Assert: ERROR 103 printed, storage unchanged

    def test_non_existent_id_shows_error(self, monkeypatch, capsys):
        """Non-existent ID shows ERROR 101, no confirmation prompt."""
        # Setup: Tasks with IDs [1, 2]
        # Mock input: ["99"]
        # Assert: ERROR 101 printed, no confirmation prompt shown

    def test_invalid_confirmation_then_confirm(self, monkeypatch, capsys):
        """Invalid confirmation shows ERROR 105, re-prompts, then deletes."""
        # Setup: Create task ID 3
        # Mock input: ["3", "maybe", "Y"]
        # Assert: ERROR 105 printed, task deleted, MSG_TASK_DELETED printed

    def test_delete_from_empty_list(self, monkeypatch, capsys):
        """Deleting from empty list shows ERROR 101."""
        # Setup: Empty task list
        # Mock input: ["1"]
        # Assert: ERROR 101 printed
```

**Validation**:
- [ ] All 8 test cases implemented
- [ ] Tests use real implementations (no mocking of business logic)
- [ ] All error codes verified (ERROR 101, 102, 103, 105)
- [ ] Success and cancellation messages verified
- [ ] Edge cases tested (empty list, last task)

---

## Running Tests

### Execute Test Suite

```bash
# Run all tests
uv run pytest

# Run delete-task specific tests
uv run pytest tests/unit/test_task_service.py::TestDeleteTask -v
uv run pytest tests/unit/test_prompts.py::TestPromptForDeleteConfirmation -v
uv run pytest tests/integration/test_delete_task_flow.py -v

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing
```

**Success Criteria**:
- [ ] All tests pass
- [ ] Code coverage ≥ 95% for new functions
- [ ] No linter errors: `uv run ruff check .`
- [ ] Code formatted: `uv run ruff format --check .`

---

## Manual Testing

### Test Scenario 1: Successful Deletion

```bash
uv run python src/main.py
```

**Steps**:
1. Select "1. Add Task"
2. Enter title: "Test task for deletion"
3. Press Enter (skip description)
4. Select "4. Delete Task"
5. Enter ID: 1
6. Confirm: Y
7. Expected: "Task deleted successfully."
8. Select "2. View Tasks"
9. Expected: "No tasks found."

### Test Scenario 2: Canceled Deletion

**Steps**:
1. Add a task
2. Select "4. Delete Task"
3. Enter valid ID
4. Confirm: N
5. Expected: "Deletion canceled."
6. View tasks
7. Expected: Task still exists

### Test Scenario 3: Error Handling

**Steps**:
1. Select "4. Delete Task"
2. Enter ID: abc → Expected: ERROR 102
3. Select "4. Delete Task"
4. Enter ID: 0 → Expected: ERROR 103
5. Select "4. Delete Task"
6. Enter ID: 999 → Expected: ERROR 101

---

## Definition of Done

### Code Quality
- [ ] All 3 new functions implemented with type hints
- [ ] Google-style docstrings for all functions
- [ ] `ruff check .` passes with zero errors
- [ ] `ruff format --check .` confirms code is formatted
- [ ] No magic numbers or hardcoded strings (all in constants.py)

### Functionality
- [ ] Delete Task menu option appears at position 4
- [ ] Valid ID + Y confirmation deletes task
- [ ] Valid ID + N response preserves task
- [ ] Invalid ID formats show ERROR 102, 103
- [ ] Non-existent ID shows ERROR 101
- [ ] Invalid confirmation shows ERROR 105 and re-prompts
- [ ] Task title displayed in confirmation prompt
- [ ] IDs not renumbered after deletion

### Testing
- [ ] 100% test coverage for new functions
- [ ] All acceptance scenarios from spec tested
- [ ] Unit tests pass (test_task_service.py, test_prompts.py)
- [ ] Integration tests pass (test_delete_task_flow.py)
- [ ] Manual testing scenarios verified

### Documentation
- [ ] Code comments explain non-obvious logic
- [ ] Docstrings describe all parameters, returns, and raises
- [ ] Spec cross-references (FR-XXX) in tests where applicable

---

## Common Pitfalls

❌ **Don't**: Use index-based deletion (`del _task_storage[index]`)
✅ **Do**: Use `_task_storage.remove(task)` after retrieval

❌ **Don't**: Show confirmation prompt before validating task ID exists
✅ **Do**: Return to menu immediately on ERROR 101 (per FR-007)

❌ **Don't**: Accept "yes", "no", "1", "0" as confirmation
✅ **Do**: Accept only Y/y/N/n (per FR-010)

❌ **Don't**: Renumber task IDs after deletion
✅ **Do**: Preserve all other task IDs unchanged (per FR-017)

❌ **Don't**: Use separate error codes for delete-specific ID validation
✅ **Do**: Reuse ERROR 101, 102, 103 from existing features

---

## Time Estimates

| Step | Estimated Time | Validation Time |
|------|----------------|-----------------|
| Step 1: Constants | 5 min | 2 min |
| Step 2: Business Logic | 10 min | 5 min |
| Step 3: UI Functions | 20 min | 10 min |
| Step 4: Main Menu | 5 min | 3 min |
| Step 5: Unit Tests (service) | 15 min | 5 min |
| Step 6: Unit Tests (prompts) | 20 min | 5 min |
| Step 7: Integration Tests | 25 min | 10 min |
| Manual Testing | 10 min | - |
| **Total** | **110 min** | **40 min** |

**Total Implementation Time**: ~2.5 hours

---

## Next Steps After Implementation

1. Run `/sp.tasks` to generate tasks.md from this plan
2. Execute implementation following generated tasks
3. Create commit: "feat: implement Delete Task feature with comprehensive test coverage"
4. Create pull request referencing spec and tasks

## Support

If implementation questions arise, refer to:
- Feature spec: `specs/004-delete-task/spec.md`
- Function contracts: `specs/004-delete-task/contracts/*.md`
- Research decisions: `specs/004-delete-task/research.md`
- Data model: `specs/004-delete-task/data-model.md`
