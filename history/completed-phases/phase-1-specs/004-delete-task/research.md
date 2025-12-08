# Research: Delete Task Feature

**Date**: 2025-12-06
**Feature**: Delete Task (004-delete-task)
**Status**: Complete

## Overview

This document captures research findings and design decisions for implementing the Delete Task feature within the existing Python 3.13 CLI todo application architecture.

## Research Questions and Findings

### 1. Deletion Pattern in Python Lists

**Question**: What is the safest pattern for removing items from an in-memory Python list in a CLI application?

**Decision**: Use `list.remove(item)` after finding the task by ID

**Rationale**:
- **Direct removal**: `_task_storage.remove(task)` removes the exact object instance after retrieval, ensuring correctness
- **No index dependency**: Unlike `del _task_storage[index]` or `_task_storage.pop(index)`, using `remove()` doesn't require maintaining index positions
- **Existing pattern**: Codebase already uses `get_task_by_id()` for retrieval, which validates existence and raises appropriate errors
- **Atomic operation**: Single list operation (remove) after validation minimizes risk of inconsistent state

**Alternatives Considered**:
- **List comprehension filtering** (`_task_storage = [t for t in _task_storage if t.id != task_id]`): Rejected because it creates new list object and doesn't integrate cleanly with existing error handling pattern
- **Index-based deletion** (`del _task_storage[index]`): Rejected because it requires additional loop to find index, duplicating logic already in `get_task_by_id()`
- **Pop with index** (`_task_storage.pop(index)`): Same issue as index-based deletion

**Implementation**:
```python
def delete_task(task_id: int) -> Task:
    """Delete a task from storage by ID.

    Args:
        task_id: The unique identifier of the task to delete

    Returns:
        The deleted Task object (for confirmation message)

    Raises:
        ValueError: If task_id invalid or task not found (ERROR 101/103)
    """
    task = get_task_by_id(task_id)  # Validates and retrieves
    _task_storage.remove(task)      # Safe removal
    return task                     # Return for title display
```

### 2. Confirmation Dialog Pattern

**Question**: What is the best practice for implementing Y/N confirmation prompts in Python CLI applications?

**Decision**: Case-insensitive input with whitespace stripping and validation loop

**Rationale**:
- **User experience**: Accept both uppercase and lowercase (Y/y/N/n) reduces friction
- **Robust input handling**: Strip whitespace prevents " Y " from being rejected
- **Clear error messages**: Invalid inputs (e.g., "maybe") show specific error (ERROR 105) and re-prompt
- **Existing pattern**: Matches validation loop pattern used in `get_task_title()` and `prompt_for_task_id()`
- **Safety**: Confirmation prevents accidental deletion, which is irreversible in Phase I (no undo)

**Alternatives Considered**:
- **Case-sensitive only** (Y/N only): Rejected for poor UX (users expect case-insensitivity)
- **Default assumption** (Enter = Yes): Rejected for safety - destructive operations require explicit confirmation
- **Numeric choices** (1=Yes, 2=No): Rejected for inconsistency with industry-standard Y/N pattern

**Implementation**:
```python
def prompt_for_delete_confirmation(task_title: str) -> bool:
    """Prompt user to confirm task deletion with Y/N response.

    Args:
        task_title: Title of task to be deleted (for context)

    Returns:
        True if user confirms (Y/y), False if user cancels (N/n)
    """
    prompt = f"Delete task '{task_title}'? (Y/N): "
    while True:
        response = input(prompt).strip().upper()
        if response == "Y":
            return True
        if response == "N":
            return False
        print(ERROR_INVALID_CONFIRMATION)
```

### 3. Error Code Assignment

**Question**: Which error codes should be used for delete-task validation errors?

**Decision**: Reuse ERROR 101, 102, 103 from view-task; introduce ERROR 105 for confirmation

**Rationale**:
- **Consistency**: Errors 101-103 already exist for task ID validation (see `constants.py:11-15`)
  - ERROR 101: "Task with ID {task_id} not found."
  - ERROR 102: "Invalid input. Please enter a numeric task ID."
  - ERROR 103: "Task ID must be a positive number."
- **Reusability**: Validation logic is identical across view/update/delete operations
- **New error needed**: Confirmation prompt introduces new validation requirement not present in other features
- **Sequential numbering**: ERROR 104 already used for Update Task field selection, so ERROR 105 is next available

**Alternatives Considered**:
- **Create new error codes** (e.g., ERROR 201-205): Rejected because it duplicates existing validation errors unnecessarily
- **Generic error message**: Rejected because spec requires precise error codes for testability

**Assignment**:
- ERROR 101: Task not found (existing, reused)
- ERROR 102: Non-numeric ID input (existing, reused)
- ERROR 103: Zero or negative ID (existing, reused)
- ERROR 105: Invalid confirmation response (new for delete-task)

### 4. ID Renumbering After Deletion

**Question**: Should remaining task IDs be renumbered after deleting a task (e.g., [1,2,3,4,5] → delete 3 → [1,2,3,4])?

**Decision**: No renumbering - IDs remain unchanged with gaps

**Rationale**:
- **Immutable IDs**: IDs are unique identifiers, not ordinal positions - renumbering breaks referential integrity
- **User expectation**: Users expect task ID to remain stable after deletion (e.g., task #5 stays #5)
- **Simplicity**: No additional logic needed - delete is a simple list removal
- **Spec alignment**: Edge case FR-017 explicitly states "preserve all other tasks in the list unchanged (no ID renumbering)"
- **Future compatibility**: ID stability required for potential features like task history, references, or persistence

**Alternatives Considered**:
- **Renumber all IDs sequentially**: Rejected because it would require updating all subsequent task IDs and complicate future features
- **Reuse deleted IDs immediately**: Rejected because ID generation already uses `max(existing IDs) + 1`, which naturally avoids immediate reuse

### 5. Integration with Main Menu

**Question**: Where should "Delete Task" be positioned in the main menu?

**Decision**: Position 4 in the main menu (after Update Task, before Mark Complete)

**Rationale**:
- **Logical flow**: CRUD order (Create→Read→Update→Delete) followed by status toggle
- **Existing pattern**: Main menu already follows this pattern:
  1. Add Task (Create)
  2. View Tasks (Read)
  3. Update Task (Update)
  4. [DELETE TASK GOES HERE] (Delete)
  5. Mark Complete (Status Toggle)
  6. Exit
- **User mental model**: Destructive action (delete) positioned after non-destructive actions (view, update)

**Alternatives Considered**:
- **After Mark Complete**: Rejected because it breaks CRUD ordering
- **Before View Tasks**: Rejected because users should view before deleting

### 6. Return to Main Menu Behavior

**Question**: When should the delete workflow return to the main menu?

**Decision**: Always return to main menu after any outcome (success, cancellation, or error)

**Rationale**:
- **Consistency**: Matches behavior of update-task feature (see `update_task_prompt()` in prompts.py:228-264)
- **User control**: User can immediately perform another action or exit
- **Spec compliance**: FR-022 states "System MUST return the user to the main menu after successful deletion, cancellation, or error handling"

**Error Scenarios**:
1. **Invalid ID format** (ERROR 102): Print error, return to menu (allow retry from menu)
2. **Invalid ID value** (ERROR 103): Print error, return to menu
3. **Task not found** (ERROR 101): Print error, return to menu (no confirmation prompt shown)
4. **Invalid confirmation** (ERROR 105): Print error, re-prompt for confirmation (stay in delete flow)
5. **Cancellation** (N/n): Print "Deletion canceled.", return to menu
6. **Success** (Y/y): Print "Task deleted successfully.", return to menu

## Technology Stack (No Changes)

**Language**: Python 3.13
**Dependencies**: Python standard library only (pytest for testing)
**Storage**: In-memory list (`_task_storage` in `task_service.py`)
**UI**: CLI with text prompts and `input()` function

## Code Organization

### New Functions Required

1. **`task_service.py`**:
   - `delete_task(task_id: int) -> Task`: Business logic for deletion

2. **`prompts.py`**:
   - `prompt_for_delete_confirmation(task_title: str) -> bool`: Confirmation dialog
   - `delete_task_prompt() -> None`: Orchestration function for delete workflow

3. **`constants.py`**:
   - `ERROR_INVALID_CONFIRMATION = "ERROR 105: Invalid input. Please enter Y or N."`
   - `MSG_TASK_DELETED = "Task deleted successfully."`
   - `MSG_DELETION_CANCELED = "Deletion canceled."`
   - `PROMPT_DELETE_CONFIRMATION = "Delete task '{title}'? (Y/N): "` (optional, can inline)

4. **`main.py`**:
   - Add menu option 4: "Delete Task"
   - Call `delete_task_prompt()` when option 4 selected

### Existing Functions to Reuse

- `get_task_by_id(task_id: int) -> Task`: For validation and retrieval (task_service.py:53-76)
- `prompt_for_task_id() -> int`: For ID input (prompts.py:145-167)

## Testing Strategy

### Unit Tests (`tests/unit/test_task_service.py`)

Test `delete_task()` function:
1. Delete existing task → task removed from list, other tasks unchanged
2. Delete non-existent ID → raises ValueError with ERROR 101
3. Delete with invalid ID (0, -5) → raises ValueError with ERROR 103
4. Delete only task in list → list becomes empty
5. Delete from multi-task list → verify IDs not renumbered

### Unit Tests (`tests/unit/test_prompts.py`)

Test `prompt_for_delete_confirmation()` function:
1. Input "Y" → returns True
2. Input "y" → returns True
3. Input "N" → returns False
4. Input "n" → returns False
5. Input " Y " (with spaces) → returns True
6. Input "maybe" → prints ERROR 105, re-prompts

### Integration Tests (`tests/integration/test_delete_task_flow.py`)

Test complete delete workflow:
1. Happy path: Valid ID + Y confirmation → task deleted, success message shown
2. Cancellation: Valid ID + N response → task preserved, cancellation message shown
3. Invalid ID format: "abc" → ERROR 102, return to menu
4. Invalid ID value: 0, -5 → ERROR 103, return to menu
5. Non-existent ID: 999 → ERROR 101, return to menu (no confirmation prompt)
6. Empty list: Try to delete any ID → ERROR 101
7. Case insensitivity: "y" and "Y" both work, "n" and "N" both work
8. Invalid confirmation: "x" → ERROR 105, re-prompt for confirmation

## Summary of Design Decisions

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Deletion method | `list.remove(task)` after retrieval | Reuses validation, atomic operation, matches existing patterns |
| Confirmation pattern | Case-insensitive Y/N with loop | User-friendly, safe for destructive operation, consistent with existing UI |
| Error codes | Reuse 101/102/103, add 105 | Avoid duplication, sequential numbering, precise error messages |
| ID renumbering | No renumbering (preserve IDs with gaps) | Immutable IDs, spec compliance (FR-017), future compatibility |
| Menu position | Position 4 (after Update, before Mark Complete) | CRUD ordering, logical flow |
| Return behavior | Always return to main menu | Consistency with update-task, spec compliance (FR-022) |

## Open Questions: None

All design decisions resolved and documented above.
