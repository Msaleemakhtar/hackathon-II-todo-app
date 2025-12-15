"""
Service Layer Contract: Update Task Feature

This file defines the public interface contract for update operations in TaskService.
This method will be added to the existing TaskService module in src/services/task_service.py.

Feature: 003-update-task
Date: 2025-12-06
Status: Design Contract
"""

from typing import Protocol

from src.models.task import Task


class UpdateTaskServiceProtocol(Protocol):
    """
    Protocol defining the contract for update operations in TaskService.

    This protocol extends the existing TaskService with write operations
    for modifying existing tasks. Implementation must adhere to this contract.
    """

    def update_task(
        self,
        task_id: int,
        new_title: str | None = None,
        new_description: str | None = None,
    ) -> Task:
        """
        Update an existing task's title and/or description fields.

        This method locates the task by ID, updates the specified field(s),
        refreshes the updated_at timestamp, and returns the modified task.

        Args:
            task_id (int): The unique identifier of the task to update.
                          Must be a positive integer (> 0).
            new_title (str | None): New title to set. If None, title is unchanged.
                                   If provided, must be non-empty and 1-200 chars after strip.
            new_description (str | None): New description to set. If None, description is unchanged.
                                         If provided, must be 0-1000 chars after strip.

        Returns:
            Task: The updated Task object with modified field(s) and refreshed updated_at.

        Raises:
            ValueError: If task_id <= 0 with message:
                       "ERROR 103: Task ID must be a positive number."
            ValueError: If no task with task_id exists with message:
                       "ERROR 101: Task with ID {task_id} not found."

        Behavior:
            - Calls get_task_by_id(task_id) to locate and validate task existence
            - Updates task.title if new_title is not None (direct attribute assignment)
            - Updates task.description if new_description is not None (direct attribute assignment)
            - Always sets task.updated_at to current UTC time in ISO 8601 format
            - Does NOT modify task.id, task.completed, or task.created_at
            - Returns the same Task instance (modified in-place)
            - Performance: O(n) for task lookup, O(1) for field updates

        Validation:
            - Task ID validation handled by get_task_by_id() (reused from 002-view-task)
            - Title/description validation performed by UI layer before calling this method
            - This method assumes inputs are pre-validated when non-None

        Design Decisions:
            - Uses selective parameters (None = no change) rather than requiring all fields
            - Modifies task in-place rather than creating new Task instance
            - Always updates updated_at timestamp regardless of which fields changed
            - Reuses existing get_task_by_id() for DRY and consistent error handling

        Example:
            >>> service = TaskService()
            >>> # Update title only
            >>> updated_task = service.update_task(task_id=5, new_title="Updated Title")
            >>> print(f"Title: {updated_task.title}, Description: {updated_task.description}")
            Title: Updated Title, Description: Original description

            >>> # Update description only
            >>> updated_task = service.update_task(task_id=5, new_description="New description")
            >>> print(f"Title: {updated_task.title}, Description: {updated_task.description}")
            Title: Updated Title, Description: New description

            >>> # Update both
            >>> updated_task = service.update_task(
            ...     task_id=5,
            ...     new_title="Both Updated",
            ...     new_description="Both fields changed"
            ... )
            >>> assert updated_task.updated_at > updated_task.created_at

        Testing:
            - Test with title only update (new_title provided, new_description=None)
            - Test with description only update (new_description provided, new_title=None)
            - Test with both fields update (both parameters provided)
            - Test with task_id = 0 → raises ERROR 103
            - Test with task_id = -1 → raises ERROR 103
            - Test with non-existent task_id → raises ERROR 101
            - Test that updated_at changes after update
            - Test that id, completed, created_at remain unchanged
            - Test that original task object is returned (same reference)
        """
        ...


# Contract Verification Notes:
# =============================
#
# 1. Type Safety:
#    - All parameters have type hints (task_id: int, optional str | None)
#    - Return type is explicit (Task)
#    - Exceptions are documented in raises section
#
# 2. Error Codes:
#    - ERROR 101: Task not found (reused from 002-view-task)
#    - ERROR 103: Invalid task ID (reused from 002-view-task)
#    - No ERROR 102 in service layer (handled at UI layer during input conversion)
#    - Title/description validation (ERROR 001-003) handled at UI layer
#
# 3. Immutability Guarantees:
#    - id: Never modified (not a parameter)
#    - completed: Never modified (not a parameter, separate Mark Complete feature)
#    - created_at: Never modified (not a parameter, historical timestamp)
#    - updated_at: Always modified (set to current time)
#
# 4. Selective Update Pattern:
#    - None values mean "do not change this field"
#    - Allows partial updates without re-specifying unchanged fields
#    - Clearer than boolean flags or separate methods
#
# 5. Performance:
#    - O(n) task lookup via linear search (acceptable for in-memory list)
#    - O(1) field updates (direct assignment)
#    - No list rebuilding or reordering
#
# 6. Reuse Strategy:
#    - Delegates to get_task_by_id() for validation and lookup
#    - Reuses Task.generate_timestamp() for updated_at
#    - No duplication of validation logic
#
# 7. In-Place Modification:
#    - Modifies existing Task instance rather than creating new one
#    - Preserves object identity in _task_storage list
#    - More efficient than remove/append pattern
#
# 8. Timestamp Semantics:
#    - updated_at changes on every update operation
#    - Even if field values are identical to current values
#    - Provides audit trail of update attempts
#
# 9. Thread Safety:
#    - Not required (single-threaded CLI application per constitution)
#    - Not addressed in this contract
#
# 10. Integration:
#     - Extends existing TaskService module (same file)
#     - Uses existing _task_storage module-level variable
#     - Compatible with existing create_task(), get_all_tasks(), get_task_by_id()
