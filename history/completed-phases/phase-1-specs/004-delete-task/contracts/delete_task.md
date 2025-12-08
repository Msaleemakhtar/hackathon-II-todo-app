# Function Contract: delete_task()

**Module**: `src/services/task_service.py`
**Feature**: Delete Task (004-delete-task)
**Date**: 2025-12-06

## Signature

```python
def delete_task(task_id: int) -> Task:
    """Delete a task from storage by its unique ID.

    Args:
        task_id: The unique identifier of the task to delete

    Returns:
        The deleted Task object (for use in confirmation message)

    Raises:
        ValueError: If task_id <= 0 (ERROR 103: Task ID must be a positive number.)
        ValueError: If no task with task_id exists (ERROR 101: Task with ID {task_id} not found.)
    """
```

## Purpose

Permanently remove a task from the in-memory task storage after validation.

## Preconditions

1. `task_id` is an integer (enforced by type system)
2. Caller has already prompted user for confirmation (this function does NOT prompt)

## Postconditions

### Success Case
1. Task with matching `task_id` is removed from `_task_storage`
2. All other tasks remain in `_task_storage` with unchanged IDs and data
3. Returns the deleted Task object (for displaying title in success message)
4. List size decreases by 1

### Error Cases
1. If `task_id <= 0`: Raises `ValueError` with message `ERROR_INVALID_TASK_ID`
2. If task not found: Raises `ValueError` with message `ERROR_TASK_NOT_FOUND.format(task_id=task_id)`
3. `_task_storage` remains unchanged on error

## Implementation Strategy

```python
def delete_task(task_id: int) -> Task:
    # Step 1: Validate task_id and retrieve task (reuses existing function)
    # This raises ValueError with ERROR 103 if task_id <= 0
    # This raises ValueError with ERROR 101 if task not found
    task = get_task_by_id(task_id)

    # Step 2: Remove task from storage
    _task_storage.remove(task)

    # Step 3: Return deleted task (for title display in UI layer)
    return task
```

## Behavior Examples

### Example 1: Successful Deletion

**Initial State**:
```python
_task_storage = [
    Task(id=1, title="Task A", ...),
    Task(id=2, title="Task B", ...),
    Task(id=3, title="Task C", ...)
]
```

**Call**:
```python
deleted = delete_task(task_id=2)
```

**Result**:
```python
# Returns: Task(id=2, title="Task B", ...)
# _task_storage now contains:
[
    Task(id=1, title="Task A", ...),
    Task(id=3, title="Task C", ...)
]
```

### Example 2: Task Not Found

**Initial State**:
```python
_task_storage = [Task(id=1, ...), Task(id=2, ...)]
```

**Call**:
```python
deleted = delete_task(task_id=99)
```

**Result**:
```python
# Raises: ValueError("ERROR 101: Task with ID 99 not found.")
# _task_storage unchanged
```

### Example 3: Invalid Task ID

**Initial State**:
```python
_task_storage = [Task(id=1, ...), Task(id=2, ...)]
```

**Call**:
```python
deleted = delete_task(task_id=0)
```

**Result**:
```python
# Raises: ValueError("ERROR 103: Task ID must be a positive number.")
# _task_storage unchanged
```

### Example 4: Delete Last Remaining Task

**Initial State**:
```python
_task_storage = [Task(id=5, title="Only task", ...)]
```

**Call**:
```python
deleted = delete_task(task_id=5)
```

**Result**:
```python
# Returns: Task(id=5, title="Only task", ...)
# _task_storage now: []
```

## Dependencies

### Internal Dependencies
- `get_task_by_id(task_id: int) -> Task`: For validation and retrieval
- `_task_storage: list[Task]`: Module-level storage (modified in-place)

### External Dependencies
- `src/constants.py`: ERROR_INVALID_TASK_ID, ERROR_TASK_NOT_FOUND
- `src/models/task.py`: Task dataclass

## Error Codes

| Code | Constant | Message | Trigger |
|------|----------|---------|---------|
| 103 | `ERROR_INVALID_TASK_ID` | "Task ID must be a positive number." | `task_id <= 0` |
| 101 | `ERROR_TASK_NOT_FOUND` | "Task with ID {task_id} not found." | Task not in storage |

## Invariants

1. **No ID Renumbering**: Remaining tasks retain their original IDs
2. **Atomic Operation**: Task is either fully deleted or unchanged (no partial deletion)
3. **Single Task Removal**: Exactly one task removed on success (never 0, never >1)
4. **No Side Effects on Error**: If error raised, `_task_storage` is not modified

## Edge Cases

| Case | Behavior |
|------|----------|
| Empty task list | Raises ERROR 101 (task not found) |
| Delete last task | List becomes empty `[]` |
| ID gap creation | Remaining tasks keep their IDs (e.g., [1,2,4,5] after deleting 3) |
| Multiple deletes | Each delete is independent (no cumulative state) |

## Testing Requirements

### Unit Tests (Minimal Set)

1. **Delete existing task**: Verify task removed, others unchanged, returns deleted task
2. **Delete non-existent ID**: Verify ValueError with ERROR 101 raised
3. **Delete with invalid ID (0, -5)**: Verify ValueError with ERROR 103 raised
4. **Delete last task**: Verify list becomes empty
5. **Verify no renumbering**: Delete middle task, check remaining IDs unchanged

### Property-Based Tests

1. **Idempotency**: Deleting same ID twice raises ERROR 101 on second attempt
2. **List size**: `len(_task_storage)` always decreases by exactly 1 on success
3. **No mutation**: Non-deleted tasks have identical `id`, `title`, `description`, `completed`, timestamps

## Performance Characteristics

- **Time Complexity**: O(n) where n = number of tasks (due to `get_task_by_id()` linear search and `list.remove()` linear search)
- **Space Complexity**: O(1) (no additional memory allocated, modifies existing list)
- **Worst Case**: n=1000 tasks, delete first task → ~2000 comparisons (acceptable for Phase I in-memory storage)

## Thread Safety

**Not thread-safe**: `_task_storage` is module-level mutable state with no locking mechanism.

**Rationale**: Phase I is single-threaded CLI application. Thread safety will be addressed in future phases if needed.

## Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2025-12-06 | Initial contract | Delete Task feature specification |
