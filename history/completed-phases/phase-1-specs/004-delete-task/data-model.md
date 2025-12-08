# Data Model: Delete Task Feature

**Date**: 2025-12-06
**Feature**: Delete Task (004-delete-task)

## Overview

The Delete Task feature operates on the existing Task data model with no modifications. This document describes the data structures, state transitions, and validation rules for the delete operation.

## Existing Entities

### Task (No Changes)

**Source**: `src/models/task.py`

The Task entity is already defined as a Python dataclass. Delete Task operates on this existing model without adding or modifying fields.

**Structure**:
```python
@dataclass
class Task:
    id: int                    # Unique identifier (immutable after creation)
    title: str                 # Task title (1-200 characters)
    description: str           # Optional description (0-1000 characters)
    completed: bool            # Completion status (True/False)
    created_at: str            # ISO 8601 timestamp (creation time)
    updated_at: str            # ISO 8601 timestamp (last modification)
```

**Field Usage in Delete Operation**:
- `id`: Used to identify which task to delete (validated via `get_task_by_id()`)
- `title`: Displayed in confirmation prompt: "Delete task '{title}'? (Y/N): "
- `description`, `completed`, `created_at`, `updated_at`: Not used in delete flow, but deleted along with entire task object

**Validation Rules** (Inherited from existing system):
- `id` must be positive integer (enforced by `get_task_by_id()`)
- `id` must exist in `_task_storage` list (enforced by `get_task_by_id()`)

## Storage Layer

### In-Memory Task Storage

**Source**: `src/services/task_service.py`

**Implementation**:
```python
_task_storage: list[Task] = []
```

**Delete Operation Behavior**:
1. Task is removed from `_task_storage` list using `list.remove(task)`
2. No other tasks are modified (IDs remain unchanged)
3. List size decreases by 1 (unless empty, in which case ERROR 101 raised before deletion)
4. Task object becomes unreferenced and eligible for garbage collection (no soft delete, no history)

**State Transitions**:
```
Before: _task_storage = [Task(id=1), Task(id=2), Task(id=3), Task(id=4)]
Delete: delete_task(task_id=2)
After:  _task_storage = [Task(id=1), Task(id=3), Task(id=4)]
```

**ID Gap Behavior** (FR-017):
- After deleting task ID 2, remaining tasks keep their original IDs [1, 3, 4]
- No renumbering occurs
- Future task additions use `max(existing IDs) + 1` (e.g., next task would be ID 5)

## Input Data

### Delete Task Input

**Source**: User input via CLI prompts

**Fields**:

1. **Task ID** (required)
   - **Type**: Integer
   - **Prompt**: "Enter Task ID: " (via `prompt_for_task_id()`)
   - **Validation**:
     - Must be numeric (ERROR 102: "Invalid input. Please enter a numeric task ID.")
     - Must be positive (ERROR 103: "Task ID must be a positive number.")
     - Must exist in task list (ERROR 101: "Task with ID {task_id} not found.")
   - **Reuses**: Existing `prompt_for_task_id()` function from view/update features

2. **Confirmation Response** (required)
   - **Type**: String (single character, case-insensitive)
   - **Prompt**: "Delete task '{title}'? (Y/N): "
   - **Validation**:
     - Must be Y, y, N, or n (after stripping whitespace)
     - Invalid inputs show ERROR 105: "Invalid input. Please enter Y or N."
     - Re-prompts on invalid input (validation loop)
   - **Behavior**:
     - Y or y → Proceed with deletion
     - N or n → Cancel deletion, preserve task

**Example Valid Inputs**:
```
Enter Task ID: 5
Delete task 'Buy groceries'? (Y/N): Y
→ Task deleted successfully.

Enter Task ID: 3
Delete task 'Call dentist'? (Y/N): n
→ Deletion canceled.
```

**Example Invalid Inputs**:
```
Enter Task ID: abc
ERROR 102: Invalid input. Please enter a numeric task ID.
→ Return to main menu

Enter Task ID: -5
ERROR 103: Task ID must be a positive number.
→ Return to main menu

Enter Task ID: 999
ERROR 101: Task with ID 999 not found.
→ Return to main menu (no confirmation prompt)

Enter Task ID: 2
Delete task 'Update resume'? (Y/N): maybe
ERROR 105: Invalid input. Please enter Y or N.
Delete task 'Update resume'? (Y/N): Y
→ Task deleted successfully.
```

## Output Data

### Success Case

**Condition**: Valid task ID + Y/y confirmation

**Output**:
1. Console message: "Task deleted successfully."
2. Task permanently removed from `_task_storage`
3. Return to main menu

**Example**:
```
Enter Task ID: 3
Delete task 'Finish report'? (Y/N): Y
Task deleted successfully.

[Main Menu displayed]
```

### Cancellation Case

**Condition**: Valid task ID + N/n response

**Output**:
1. Console message: "Deletion canceled."
2. Task remains in `_task_storage` unchanged
3. Return to main menu

**Example**:
```
Enter Task ID: 7
Delete task 'Team meeting'? (Y/N): N
Deletion canceled.

[Main Menu displayed]
```

### Error Cases

**Condition**: Invalid input at any validation step

**Output**:
1. Console message with specific error code (101, 102, 103, or 105)
2. Return to main menu (for ID errors) or re-prompt (for confirmation errors)
3. No changes to `_task_storage`

## State Transitions

### Delete Task State Machine

```
START
  ↓
[Prompt for Task ID]
  ↓
[Validate ID format] → ERROR 102 → END (return to menu)
  ↓
[Validate ID value] → ERROR 103 → END (return to menu)
  ↓
[Check task exists] → ERROR 101 → END (return to menu)
  ↓
[Display confirmation prompt with title]
  ↓
[Validate confirmation] → ERROR 105 → [Re-prompt confirmation]
  ↓
[User confirms (Y/y)?]
  ├─ Yes → [Remove from storage] → [Display success] → END
  └─ No  → [Preserve task] → [Display canceled] → END
```

### Storage State Transitions

**Initial State**: Task list with N tasks
```python
_task_storage = [Task(id=1, ...), Task(id=2, ...), Task(id=3, ...)]
```

**After Successful Delete** (task_id=2):
```python
_task_storage = [Task(id=1, ...), Task(id=3, ...)]
```

**After Canceled Delete** (task_id=2):
```python
_task_storage = [Task(id=1, ...), Task(id=2, ...), Task(id=3, ...)]  # Unchanged
```

**After Error** (any ERROR 101/102/103/105):
```python
_task_storage = [Task(id=1, ...), Task(id=2, ...), Task(id=3, ...)]  # Unchanged
```

## Invariants

### Data Integrity Constraints

1. **ID Uniqueness**: After deletion, all remaining task IDs remain unique
2. **ID Immutability**: Deletion does not modify IDs of other tasks (no renumbering)
3. **Atomic Deletion**: Task is either fully deleted or fully preserved (no partial deletion)
4. **Reference Integrity**: Deleted task object is fully removed from `_task_storage` (no dangling references)

### Error Handling Constraints

1. **No Confirmation for Invalid IDs**: If task ID fails validation (ERROR 101/102/103), confirmation prompt is never shown
2. **Confirmation Loop**: Invalid confirmation responses (ERROR 105) re-prompt without returning to menu
3. **No Side Effects on Error**: Any error leaves `_task_storage` in original state

### Edge Case Handling

1. **Empty List Deletion**:
   - Attempting to delete from empty list raises ERROR 101
   - No special "empty list" message (consistent with view/update behavior)

2. **Last Task Deletion**:
   - Deleting the only task in list results in empty list
   - No special handling required (list becomes `[]`)

3. **ID Gap Preservation**:
   - After deleting task ID 3 from [1, 2, 3, 4, 5], list becomes [1, 2, 4, 5]
   - Gap at ID 3 is preserved permanently (unless new task reuses that ID via max() calculation)

## Relationships

### Function Call Flow

```
main.py::main()
  ↓
prompts.py::delete_task_prompt()
  ↓
prompts.py::prompt_for_task_id()  # Validates numeric, positive
  ↓
task_service.py::get_task_by_id()  # Validates existence, retrieves task
  ↓
prompts.py::prompt_for_delete_confirmation(task.title)  # Y/N validation
  ↓
task_service.py::delete_task(task_id)  # Business logic (remove from list)
  ↓
main.py::main()  # Return to menu
```

### Module Dependencies

- `prompts.py` → depends on `task_service.py` (calls `get_task_by_id`, `delete_task`)
- `prompts.py` → depends on `constants.py` (error messages, prompts)
- `task_service.py` → depends on `models/task.py` (Task type)
- `main.py` → depends on `prompts.py` (calls `delete_task_prompt()`)

## No Schema Changes

**Database**: N/A (in-memory only)
**File Format**: N/A (no persistence)
**API Contract**: N/A (CLI application)

This feature requires **zero** modifications to existing data structures. All changes are additive (new functions) and operational (new menu option).

## Summary

- **Entities Modified**: None (operates on existing Task dataclass)
- **Storage Changes**: Removal from in-memory list only (no persistence)
- **New Validation**: Confirmation response (Y/N) validation only
- **Reused Validation**: Task ID validation (ERROR 101/102/103) from existing features
- **Invariants**: ID immutability, atomic deletion, no renumbering
- **Edge Cases**: Empty list, last task, ID gaps (all handled per spec)
