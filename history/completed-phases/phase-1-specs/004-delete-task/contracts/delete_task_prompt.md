# Function Contract: delete_task_prompt()

**Module**: `src/ui/prompts.py`
**Feature**: Delete Task (004-delete-task)
**Date**: 2025-12-06

## Signature

```python
def delete_task_prompt() -> None:
    """Orchestrate the complete delete task workflow with user interaction.

    This function coordinates the entire delete operation from prompting for
    task ID through confirmation to final deletion or cancellation.

    Args:
        None

    Returns:
        None - always returns to main menu after completion

    Raises:
        None - all exceptions caught and handled internally
    """
```

## Purpose

Provide the main entry point for the Delete Task feature, orchestrating all user interactions, validations, and business logic calls to complete the delete workflow.

## Workflow Steps

```
1. Prompt for Task ID (prompt_for_task_id)
   ↓
2. Validate and Retrieve Task (get_task_by_id)
   ↓ [if error: print message, return to menu]
   ↓
3. Prompt for Confirmation (prompt_for_delete_confirmation)
   ↓
4a. If confirmed (True):
    - Delete task (delete_task)
    - Print success message
    - Return to menu

4b. If canceled (False):
    - Print cancellation message
    - Return to menu
```

## Implementation Strategy

```python
def delete_task_prompt() -> None:
    try:
        # Step 1: Get and validate task ID
        # May raise ValueError with ERROR 102 or ERROR 103
        task_id = prompt_for_task_id()

        # Step 2: Retrieve task (validates existence)
        # May raise ValueError with ERROR 101
        task = get_task_by_id(task_id)

    except ValueError as e:
        # Handle ID validation errors (ERROR 101, 102, 103)
        print(str(e))
        return  # Return to main menu without showing confirmation

    # Step 3: Get user confirmation (shows task title for context)
    # Always returns True or False (never raises exception)
    confirmed = prompt_for_delete_confirmation(task.title)

    # Step 4: Execute deletion or cancellation
    if confirmed:
        # User confirmed with Y/y
        delete_task(task_id)
        print(MSG_TASK_DELETED)
    else:
        # User canceled with N/n
        print(MSG_DELETION_CANCELED)

    # Implicit return to main menu (function ends)
```

## Behavior Examples

### Example 1: Successful Deletion

**Initial State**:
```python
_task_storage = [Task(id=1, ...), Task(id=2, title="Buy milk", ...), Task(id=3, ...)]
```

**User Interaction**:
```
Enter Task ID: 2
Delete task 'Buy milk'? (Y/N): Y
Task deleted successfully.
```

**Final State**:
```python
_task_storage = [Task(id=1, ...), Task(id=3, ...)]
```

### Example 2: Canceled Deletion

**Initial State**:
```python
_task_storage = [Task(id=5, title="Call dentist", ...)]
```

**User Interaction**:
```
Enter Task ID: 5
Delete task 'Call dentist'? (Y/N): N
Deletion canceled.
```

**Final State**:
```python
_task_storage = [Task(id=5, title="Call dentist", ...)]  # Unchanged
```

### Example 3: Invalid Task ID Format

**User Interaction**:
```
Enter Task ID: abc
ERROR 102: Invalid input. Please enter a numeric task ID.
[Returns to main menu]
```

**Final State**:
```python
_task_storage unchanged
```

### Example 4: Invalid Task ID Value

**User Interaction**:
```
Enter Task ID: -5
ERROR 103: Task ID must be a positive number.
[Returns to main menu]
```

**Final State**:
```python
_task_storage unchanged
```

### Example 5: Task Not Found

**Initial State**:
```python
_task_storage = [Task(id=1, ...), Task(id=2, ...)]
```

**User Interaction**:
```
Enter Task ID: 99
ERROR 101: Task with ID 99 not found.
[Returns to main menu - no confirmation prompt shown]
```

**Final State**:
```python
_task_storage unchanged
```

### Example 6: Invalid Confirmation with Retry

**Initial State**:
```python
_task_storage = [Task(id=3, title="Finish report", ...)]
```

**User Interaction**:
```
Enter Task ID: 3
Delete task 'Finish report'? (Y/N): maybe
ERROR 105: Invalid input. Please enter Y or N.
Delete task 'Finish report'? (Y/N): Y
Task deleted successfully.
```

**Final State**:
```python
_task_storage = []  # Task deleted
```

## Error Handling Strategy

### Try-Catch Block Scope

**Errors Caught**:
- ValueError from `prompt_for_task_id()` (ERROR 102, 103)
- ValueError from `get_task_by_id()` (ERROR 101)

**Errors NOT Caught**:
- `prompt_for_delete_confirmation()` never raises exceptions (validation loop ensures valid return)
- `delete_task()` exceptions already handled by `get_task_by_id()` call above (task validated before deletion)

### Return Points

| Error Type | Error Code | Action |
|------------|------------|--------|
| Non-numeric ID | ERROR 102 | Print error, return to menu |
| Zero/negative ID | ERROR 103 | Print error, return to menu |
| Task not found | ERROR 101 | Print error, return to menu |
| Invalid confirmation | ERROR 105 | Print error, re-prompt (handled in `prompt_for_delete_confirmation`) |
| User cancels | N/A | Print cancellation message, return to menu |
| Success | N/A | Print success message, return to menu |

## Dependencies

### Internal Dependencies
- `prompt_for_task_id() -> int`: Get and validate task ID
- `get_task_by_id(task_id: int) -> Task`: Validate existence and retrieve task
- `prompt_for_delete_confirmation(task_title: str) -> bool`: Get user confirmation
- `delete_task(task_id: int) -> Task`: Execute deletion

### External Dependencies
- `src/constants.py`: MSG_TASK_DELETED, MSG_DELETION_CANCELED
- `src/models/task.py`: Task type

## Constants Required

**New constants in `constants.py`**:
```python
MSG_TASK_DELETED = "Task deleted successfully."
MSG_DELETION_CANCELED = "Deletion canceled."
```

## Preconditions

1. Function called from main menu (user selected "Delete Task" option)
2. Task storage (`_task_storage`) is initialized (may be empty)
3. All required constants defined in `constants.py`

## Postconditions

### All Cases
1. Function returns control to main menu (no exceptions propagated)
2. Console displays appropriate message (success, cancellation, or error)
3. Storage is either modified (success) or unchanged (error/cancellation)

### Success Case (Y/y confirmation)
1. Task removed from `_task_storage`
2. "Task deleted successfully." message displayed
3. Other tasks unchanged (no ID renumbering)

### Cancellation Case (N/n response)
1. Task remains in `_task_storage` unchanged
2. "Deletion canceled." message displayed

### Error Cases (ERROR 101/102/103)
1. Error message displayed
2. No confirmation prompt shown (early return)
3. `_task_storage` unchanged

## User Flow Diagram

```
START (user selects "Delete Task" from menu)
  ↓
Prompt: "Enter Task ID: "
  ↓
[Validate numeric] → FAIL → Display ERROR 102 → END
  ↓ PASS
[Validate positive] → FAIL → Display ERROR 103 → END
  ↓ PASS
[Validate exists] → FAIL → Display ERROR 101 → END
  ↓ PASS
Prompt: "Delete task '{title}'? (Y/N): "
  ↓
[Validate Y/y/N/n] → FAIL → Display ERROR 105 → Re-prompt confirmation
  ↓ PASS
[User confirmed?]
  ├─ YES (Y/y) → Delete task → Display success → END
  └─ NO (N/n) → Display canceled → END

END (return to main menu)
```

## Invariants

1. **No Partial Deletion**: Task is either fully deleted or fully preserved (atomic operation)
2. **Always Returns**: Function never raises unhandled exceptions
3. **Message Always Shown**: Every exit path displays a message (success, error, or cancellation)
4. **No Confirmation on Error**: If task ID validation fails, confirmation is never shown

## Edge Cases

| Case | Behavior |
|------|----------|
| Empty task list | Enter any ID → ERROR 101, return to menu |
| Delete last task | Successful deletion leaves `_task_storage = []` |
| Confirmation after ID error | Not possible (early return before confirmation) |
| Multiple invalid confirmations | Re-prompt indefinitely until valid Y/N entered |

## Integration Points

### Main Menu Integration

**File**: `src/main.py`

**Integration Code**:
```python
from src.ui.prompts import delete_task_prompt

def main():
    while True:
        print("\n--- Todo App ---")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Update Task")
        print("4. Delete Task")  # NEW
        print("5. Mark Complete")
        print("6. Exit")

        choice = input("Select option: ")

        if choice == "1":
            add_task_prompt()
        elif choice == "2":
            view_task_prompt()
        elif choice == "3":
            update_task_prompt()
        elif choice == "4":
            delete_task_prompt()  # NEW
        elif choice == "5":
            mark_complete_prompt()
        elif choice == "6":
            break
        else:
            print("Invalid option.")
```

## Testing Requirements

### Unit Tests

Mock all dependencies (`prompt_for_task_id`, `get_task_by_id`, `prompt_for_delete_confirmation`, `delete_task`):

1. **ID prompt raises ERROR 102**: Verify error printed, function returns
2. **ID prompt raises ERROR 103**: Verify error printed, function returns
3. **get_task_by_id raises ERROR 101**: Verify error printed, function returns
4. **Confirmation returns True**: Verify delete_task called, success message printed
5. **Confirmation returns False**: Verify delete_task NOT called, cancellation message printed

### Integration Tests

Test complete workflow with real implementations:

1. **Valid ID + Y**: Verify task deleted, success message shown
2. **Valid ID + N**: Verify task preserved, cancellation message shown
3. **Invalid ID format**: Verify ERROR 102, no confirmation prompt, task unchanged
4. **Invalid ID value**: Verify ERROR 103, no confirmation prompt, task unchanged
5. **Non-existent ID**: Verify ERROR 101, no confirmation prompt, task unchanged
6. **Valid ID + invalid confirmation + Y**: Verify ERROR 105, re-prompt, then delete

## Performance Characteristics

- **Time Complexity**: O(n) where n = number of tasks (due to `get_task_by_id` and `delete_task` linear searches)
- **Space Complexity**: O(1) (no additional memory allocated)
- **User Latency**: Depends on user input speed (no artificial delays)

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2025-12-06 | Initial contract | Delete Task feature specification |
