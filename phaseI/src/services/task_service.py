"""Task business logic and storage operations."""

from src.constants import ERROR_INVALID_TASK_ID, ERROR_TASK_NOT_FOUND
from src.models.task import Task

# In-memory task storage (ephemeral)
_task_storage: list[Task] = []


def generate_next_id() -> int:
    """Generate the next sequential task ID.

    Returns:
        1 if task list is empty, otherwise max(existing IDs) + 1
    """
    if not _task_storage:
        return 1
    return max(task.id for task in _task_storage) + 1


def create_task(title: str, description: str) -> Task:
    """Create and store a new task.

    Args:
        title: Task title (already validated)
        description: Task description (already validated, may be empty)

    Returns:
        Newly created Task instance
    """
    timestamp = Task.generate_timestamp()
    task = Task(
        id=generate_next_id(),
        title=title,
        description=description,
        completed=False,
        created_at=timestamp,
        updated_at=timestamp,
    )
    _task_storage.append(task)
    return task


def get_all_tasks() -> list[Task]:
    """Retrieve all tasks from storage.

    Returns:
        List of all Task instances (may be empty)
    """
    return _task_storage.copy()


def get_task_by_id(task_id: int) -> Task:
    """Retrieve a single task by its unique ID.

    Args:
        task_id: The unique identifier of the task to retrieve

    Returns:
        Task object with the matching ID

    Raises:
        ValueError: If task_id <= 0 (ERROR 103)
        ValueError: If no task with task_id exists (ERROR 101)
    """
    # Validate task_id is positive
    if task_id <= 0:
        raise ValueError(ERROR_INVALID_TASK_ID)

    # Search for task with matching ID
    for task in _task_storage:
        if task.id == task_id:
            return task

    # Task not found
    raise ValueError(ERROR_TASK_NOT_FOUND.format(task_id=task_id))


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
        Updated Task object (same instance, modified in-place)

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
    # Reuse get_task_by_id() for validation and retrieval
    task = get_task_by_id(task_id)

    # Remove task from storage (no renumbering)
    _task_storage.remove(task)

    # Return deleted task for UI confirmation message
    return task


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
