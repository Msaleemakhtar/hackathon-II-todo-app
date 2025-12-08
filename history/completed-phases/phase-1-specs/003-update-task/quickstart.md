# Quickstart Guide: Implementing Update Task Feature

**Feature**: 003-update-task
**Date**: 2025-12-06
**Estimated Time**: 2-3 hours for complete implementation + testing

---

## Prerequisites

Before starting implementation:

1. ✅ Read [spec.md](./spec.md) - Feature requirements and acceptance criteria
2. ✅ Read [plan.md](./plan.md) - Architecture and constitution compliance
3. ✅ Read [research.md](./research.md) - Technical decisions and patterns
4. ✅ Read [data-model.md](./data-model.md) - Entity structure and state transitions
5. ✅ Review [contracts/](./contracts/) - Service and UI interface contracts
6. ✅ Ensure features 001-add-task and 002-view-task are implemented (dependencies for reuse)

---

## Implementation Checklist

### Step 1: Add Constants (5 minutes)

**File**: `src/constants.py`

**Action**: Add new error code and prompts for update feature

```python
# Error codes and messages - Update Task feature
ERROR_INVALID_OPTION = "ERROR 104: Invalid option. Please select 1, 2, or 3."

# Success messages - Update Task feature
MSG_TASK_UPDATED = "Task updated successfully."

# Prompts - Update Task feature
PROMPT_FIELD_SELECTION = "Select update option (1-3): "
PROMPT_NEW_TITLE = "Enter New Task Title: "
PROMPT_NEW_DESCRIPTION = "Enter New Task Description (press Enter to clear): "
```

**Verification**:
- [ ] ERROR_INVALID_OPTION constant added
- [ ] MSG_TASK_UPDATED constant added
- [ ] All three PROMPT_* constants added
- [ ] `ruff check src/constants.py` passes

---

### Step 2: Implement Service Layer (15 minutes)

**File**: `src/services/task_service.py`

**Action**: Add `update_task()` method

**Reference**: [contracts/task_service_interface.py](./contracts/task_service_interface.py)

```python
def update_task(
    task_id: int,
    new_title: str | None = None,
    new_description: str | None = None,
) -> Task:
    """Update an existing task's title and/or description fields.

    Args:
        task_id: The unique identifier of the task to update
        new_title: New title to set (None = no change)
        new_description: New description to set (None = no change)

    Returns:
        Updated Task object

    Raises:
        ValueError: If task_id invalid or task not found (ERROR 101/103)
    """
    # Reuse existing get_task_by_id for validation and lookup
    task = get_task_by_id(task_id)

    # Update fields if new values provided
    if new_title is not None:
        task.title = new_title
    if new_description is not None:
        task.description = new_description

    # Always update timestamp
    task.updated_at = Task.generate_timestamp()

    return task
```

**Verification**:
- [ ] Function signature matches contract
- [ ] Reuses `get_task_by_id()` for validation
- [ ] Updates title only if `new_title is not None`
- [ ] Updates description only if `new_description is not None`
- [ ] Always updates `updated_at` timestamp
- [ ] Returns updated Task instance
- [ ] Google-style docstring added
- [ ] Type hints for all parameters and return
- [ ] `ruff check src/services/task_service.py` passes

---

### Step 3: Implement UI Functions (30 minutes)

**File**: `src/ui/prompts.py`

**Action**: Add 4 new functions

**Reference**: [contracts/ui_prompts_interface.py](./contracts/ui_prompts_interface.py)

#### 3a. Field Selection Menu Display

```python
def display_field_selection_menu() -> None:
    """Display the field selection menu for choosing which field(s) to update."""
    print("\nSelect fields to update:")
    print("1. Update Title Only")
    print("2. Update Description Only")
    print("3. Update Both Title and Description")
```

#### 3b. Field Choice Prompt

```python
def prompt_for_field_choice() -> int:
    """Prompt user to select which field(s) to update and validate the choice.

    Returns:
        Valid field selection choice (1, 2, or 3)
    """
    while True:
        try:
            choice = int(input(PROMPT_FIELD_SELECTION))
            if 1 <= choice <= 3:
                return choice
            print(ERROR_INVALID_OPTION)
        except ValueError:
            print(ERROR_INVALID_OPTION)
```

#### 3c. New Title Prompt

```python
def get_new_task_title(current_title: str) -> str:
    """Prompt user for new task title with validation loop.

    Args:
        current_title: The task's current title (for display context)

    Returns:
        Valid new task title (stripped)
    """
    while True:
        title = input(PROMPT_NEW_TITLE)
        is_valid, error = validate_title(title)  # Reuse from add-task
        if is_valid:
            return title.strip()
        print(error)
```

#### 3d. New Description Prompt

```python
def get_new_task_description(current_description: str) -> str:
    """Prompt user for new task description with validation loop.

    Args:
        current_description: The task's current description (for display context)

    Returns:
        Valid new task description (stripped, may be empty)
    """
    while True:
        description = input(PROMPT_NEW_DESCRIPTION)
        is_valid, error = validate_description(description)  # Reuse from add-task
        if is_valid:
            return description.strip()
        print(error)
```

#### 3e. Update Task Workflow Orchestrator

```python
def update_task_prompt() -> None:
    """Orchestrate the complete update task workflow with user interaction."""
    try:
        # Step 1: Get and validate task ID
        task_id = prompt_for_task_id()  # Reuse from view-task

        # Step 2: Retrieve task (may raise ERROR 101)
        task = get_task_by_id(task_id)
    except ValueError as e:
        print(str(e))
        return  # Return to main menu on error

    # Step 3: Display current values
    print()
    display_task_details(task)  # Reuse from view-task

    # Step 4: Get field selection
    display_field_selection_menu()
    choice = prompt_for_field_choice()

    # Step 5: Collect new value(s) based on choice
    new_title = None
    new_description = None

    if choice == 1:  # Title only
        new_title = get_new_task_title(task.title)
    elif choice == 2:  # Description only
        new_description = get_new_task_description(task.description)
    else:  # choice == 3, Both
        new_title = get_new_task_title(task.title)
        new_description = get_new_task_description(task.description)

    # Step 6: Update task
    update_task(task_id, new_title, new_description)

    # Step 7: Display success message
    print(MSG_TASK_UPDATED)
```

**Verification**:
- [ ] All 5 functions added to `src/ui/prompts.py`
- [ ] Imports updated (ERROR_INVALID_OPTION, MSG_TASK_UPDATED, PROMPT_* constants, update_task service)
- [ ] Reuses `validate_title()` and `validate_description()`
- [ ] Reuses `prompt_for_task_id()` and `get_task_by_id()`
- [ ] Reuses `display_task_details()`
- [ ] All functions have Google-style docstrings
- [ ] Type hints for all parameters and returns
- [ ] `ruff check src/ui/prompts.py` passes

---

### Step 4: Integrate with Main Menu (10 minutes)

**File**: `src/main.py`

**Action**: Add menu option 3 for "Update Task"

**Before** (example structure):
```python
def display_main_menu():
    print("\n=== Todo Application ===")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. [Not yet implemented]")
    print("4. [Not yet implemented]")
    print("5. [Not yet implemented]")
    print("6. Exit")

def main():
    while True:
        display_main_menu()
        choice = input("Select an option: ")

        if choice == "1":
            add_task_prompt()
        elif choice == "2":
            # View tasks sub-menu
            ...
        elif choice == "6":
            break
```

**After** (add update task):
```python
from src.ui.prompts import add_task_prompt, update_task_prompt, ...

def display_main_menu():
    print("\n=== Todo Application ===")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")  # ← ADDED
    print("4. [Not yet implemented]")
    print("5. [Not yet implemented]")
    print("6. Exit")

def main():
    while True:
        display_main_menu()
        choice = input("Select an option: ")

        if choice == "1":
            add_task_prompt()
        elif choice == "2":
            # View tasks sub-menu
            ...
        elif choice == "3":  # ← ADDED
            update_task_prompt()
        elif choice == "6":
            break
```

**Verification**:
- [ ] `update_task_prompt` imported from `src.ui.prompts`
- [ ] Menu displays "3. Update Task"
- [ ] Selecting "3" calls `update_task_prompt()`
- [ ] Returns to main menu after update completes
- [ ] `ruff check src/main.py` passes

---

### Step 5: Write Tests (60-90 minutes)

**File**: `tests/unit/test_task_service.py`

**Action**: Add test functions for `update_task()`

**Test Coverage Needed**:
```python
def test_update_task_title_only():
    """Test updating only the title field."""
    # Create task, update title only, verify title changed, description unchanged

def test_update_task_description_only():
    """Test updating only the description field."""
    # Create task, update description only, verify description changed, title unchanged

def test_update_task_both_fields():
    """Test updating both title and description."""
    # Create task, update both, verify both changed

def test_update_task_updates_timestamp():
    """Test that updated_at timestamp changes on update."""
    # Create task, save original updated_at, update task, verify updated_at changed

def test_update_task_preserves_immutable_fields():
    """Test that id, completed, created_at are not modified."""
    # Create task, save originals, update task, verify id/completed/created_at unchanged

def test_update_task_invalid_id_zero():
    """Test updating with task_id = 0 raises ERROR 103."""
    # Expect ValueError with ERROR_INVALID_TASK_ID

def test_update_task_invalid_id_negative():
    """Test updating with task_id = -1 raises ERROR 103."""
    # Expect ValueError with ERROR_INVALID_TASK_ID

def test_update_task_nonexistent_id():
    """Test updating non-existent task raises ERROR 101."""
    # Expect ValueError with ERROR_TASK_NOT_FOUND

def test_update_task_returns_same_instance():
    """Test that update returns the same Task object (in-place modification)."""
    # Create task, update, verify returned task is same object reference

def test_update_task_with_none_values():
    """Test calling update_task with both new_title=None, new_description=None."""
    # Should update timestamp only, leave fields unchanged
```

**File**: `tests/unit/test_prompts.py`

**Action**: Add test functions for UI prompts

**Test Coverage Needed**:
```python
def test_display_field_selection_menu(capsys):
    """Test field selection menu displays correct format."""

def test_prompt_for_field_choice_valid_options(monkeypatch):
    """Test valid choices (1, 2, 3) are accepted."""

def test_prompt_for_field_choice_invalid_option(monkeypatch, capsys):
    """Test invalid choice displays ERROR 104 and re-prompts."""

def test_get_new_task_title_valid(monkeypatch):
    """Test valid title input."""

def test_get_new_task_title_empty_reprompts(monkeypatch, capsys):
    """Test empty title displays ERROR 001 and re-prompts."""

def test_get_new_task_title_too_long_reprompts(monkeypatch, capsys):
    """Test title > 200 chars displays ERROR 002 and re-prompts."""

def test_get_new_task_description_valid(monkeypatch):
    """Test valid description input."""

def test_get_new_task_description_empty_allowed(monkeypatch):
    """Test empty description is valid."""

def test_get_new_task_description_too_long_reprompts(monkeypatch, capsys):
    """Test description > 1000 chars displays ERROR 003 and re-prompts."""

def test_update_task_prompt_complete_flow_option_1(monkeypatch, capsys):
    """Test complete update flow for option 1 (title only)."""

def test_update_task_prompt_complete_flow_option_2(monkeypatch, capsys):
    """Test complete update flow for option 2 (description only)."""

def test_update_task_prompt_complete_flow_option_3(monkeypatch, capsys):
    """Test complete update flow for option 3 (both fields)."""

def test_update_task_prompt_task_not_found(monkeypatch, capsys):
    """Test ERROR 101 displayed when task doesn't exist."""
```

**File**: `tests/unit/test_main.py` (if integration tests exist)

**Action**: Add integration test for update task flow

```python
def test_main_menu_option_3_calls_update_task_prompt(monkeypatch):
    """Test selecting option 3 from main menu calls update_task_prompt."""
```

**Verification**:
- [ ] All service layer tests pass (`pytest tests/unit/test_task_service.py`)
- [ ] All UI layer tests pass (`pytest tests/unit/test_prompts.py`)
- [ ] Test coverage for update_task >= 100% (`pytest --cov=src.services.task_service`)
- [ ] Test coverage for UI functions >= 100% (`pytest --cov=src.ui.prompts`)
- [ ] All edge cases covered (per acceptance scenarios in spec.md)

---

### Step 6: Manual Testing (15 minutes)

**Action**: Run application and test update scenarios

**Test Script**:
```bash
# Start application
uv run python src/main.py

# Create test tasks
1 → Add Task → "Original Title" + "Original Description"
1 → Add Task → "Second Task" + "Test"

# Test Option 1: Title Only
3 → Update Task → ID: 1 → Option 1 → "Updated Title"
2 → View Tasks → Verify task 1 title changed, description unchanged

# Test Option 2: Description Only
3 → Update Task → ID: 1 → Option 2 → "Updated Description"
2 → View Tasks → Verify task 1 description changed, title unchanged

# Test Option 3: Both
3 → Update Task → ID: 2 → Option 3 → "Both Title" + "Both Description"
2 → View Tasks → Verify task 2 both fields changed

# Test Error Handling
3 → Update Task → ID: 99 → Verify ERROR 101 displayed
3 → Update Task → ID: 0 → Verify ERROR 103 displayed
3 → Update Task → ID: abc → Verify ERROR 102 displayed
3 → Update Task → ID: 1 → Option: 5 → Verify ERROR 104 displayed
3 → Update Task → ID: 1 → Option: 1 → Title: (empty) → Verify ERROR 001
3 → Update Task → ID: 1 → Option: 1 → Title: {250 chars} → Verify ERROR 002
3 → Update Task → ID: 1 → Option: 2 → Desc: {1200 chars} → Verify ERROR 003
```

**Verification**:
- [ ] All success paths work as expected
- [ ] All error codes display correctly
- [ ] Updated_at timestamp changes after each update
- [ ] Immutable fields (id, completed, created_at) never change
- [ ] User can return to main menu from all paths

---

### Step 7: Code Quality Checks (5 minutes)

**Action**: Run linters and formatters

```bash
# Run ruff linter
uv run ruff check .

# Run ruff formatter check
uv run ruff format --check .

# Run type checker (optional but recommended)
uv run mypy src/

# Run full test suite
uv run pytest

# Run test coverage
uv run pytest --cov=src --cov-report=term-missing
```

**Verification**:
- [ ] `ruff check .` passes with zero errors
- [ ] `ruff format --check .` passes
- [ ] `mypy src/` passes (if type checking enabled)
- [ ] `pytest` all tests pass
- [ ] Coverage >= 100% for update task code

---

## Common Pitfalls & Solutions

### Pitfall 1: Forgetting to update timestamp

**Problem**: Not updating `updated_at` on every update operation

**Solution**: Always call `task.updated_at = Task.generate_timestamp()` regardless of which fields are updated

### Pitfall 2: Not handling None parameters correctly

**Problem**: Updating fields when None is passed (should preserve current value)

**Solution**: Use `if new_title is not None:` checks before updating fields

### Pitfall 3: Breaking immutability guarantees

**Problem**: Accidentally modifying `id`, `completed`, or `created_at`

**Solution**: Never touch these fields in `update_task()` function

### Pitfall 4: Inconsistent error codes

**Problem**: Using wrong error codes or messages

**Solution**: Reuse constants from `src/constants.py`, verify exact messages match spec

### Pitfall 5: Not reusing existing validation

**Problem**: Duplicating validation logic

**Solution**: Reuse `validate_title()`, `validate_description()`, `prompt_for_task_id()`, `get_task_by_id()`

---

## Success Criteria

✅ **Feature is complete when**:

1. All Step 1-7 verification checkboxes are checked
2. `uv run pytest` shows 100% passing tests
3. `uv run pytest --cov=src` shows >=100% coverage for new code
4. `ruff check .` and `ruff format --check .` pass
5. Manual testing script completes successfully
6. All acceptance scenarios from spec.md pass
7. Constitution compliance confirmed (all 7 principles)

---

## Next Steps

After implementation is complete:

1. Run `/sp.tasks` to generate detailed task breakdown (if not already done)
2. Create pull request with implementation
3. Request code review focusing on:
   - Constitution compliance
   - Test coverage
   - Code quality
   - Spec adherence
4. Merge to main branch
5. Proceed to feature 004-delete-task

---

## Support Resources

- **Specification**: [spec.md](./spec.md)
- **Architecture Plan**: [plan.md](./plan.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Service Contract**: [contracts/task_service_interface.py](./contracts/task_service_interface.py)
- **UI Contract**: [contracts/ui_prompts_interface.py](./contracts/ui_prompts_interface.py)
- **Constitution**: `.specify/memory/constitution.md`

---

**Happy Coding! Remember: AI generates the implementation, you architect the specification.** 🚀
