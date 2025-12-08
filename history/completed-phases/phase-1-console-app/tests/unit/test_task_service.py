"""Unit tests for task service operations."""

import pytest

from src.models.task import Task
from src.services import task_service


@pytest.fixture(autouse=True)
def reset_task_storage():
    """Reset task storage before each test."""
    task_service._task_storage.clear()
    yield
    task_service._task_storage.clear()


class TestGenerateNextId:
    """Tests for generate_next_id() function."""

    def test_generate_next_id_empty_storage(self):
        """Returns 1 when storage is empty."""
        next_id = task_service.generate_next_id()
        assert next_id == 1

    def test_generate_next_id_one_task(self):
        """Returns 2 when one task exists with ID 1."""
        task = Task(
            id=1,
            title="Test",
            description="",
            completed=False,
            created_at="2025-12-04T10:00:00.000000Z",
            updated_at="2025-12-04T10:00:00.000000Z",
        )
        task_service._task_storage.append(task)

        next_id = task_service.generate_next_id()
        assert next_id == 2

    def test_generate_next_id_multiple_tasks(self):
        """Returns max(ids) + 1 for multiple tasks."""
        tasks = [
            Task(
                1, "Task 1", "", False, "2025-12-04T10:00:00.000000Z", "2025-12-04T10:00:00.000000Z"
            ),
            Task(
                2, "Task 2", "", False, "2025-12-04T10:01:00.000000Z", "2025-12-04T10:01:00.000000Z"
            ),
            Task(
                3, "Task 3", "", False, "2025-12-04T10:02:00.000000Z", "2025-12-04T10:02:00.000000Z"
            ),
        ]
        task_service._task_storage.extend(tasks)

        next_id = task_service.generate_next_id()
        assert next_id == 4

    def test_generate_next_id_non_sequential(self):
        """Handles non-sequential IDs correctly (returns max + 1)."""
        tasks = [
            Task(
                1, "Task 1", "", False, "2025-12-04T10:00:00.000000Z", "2025-12-04T10:00:00.000000Z"
            ),
            Task(
                5, "Task 5", "", False, "2025-12-04T10:01:00.000000Z", "2025-12-04T10:01:00.000000Z"
            ),
            Task(
                3, "Task 3", "", False, "2025-12-04T10:02:00.000000Z", "2025-12-04T10:02:00.000000Z"
            ),
        ]
        task_service._task_storage.extend(tasks)

        next_id = task_service.generate_next_id()
        assert next_id == 6


class TestCreateTask:
    """Tests for create_task() function."""

    def test_create_task_with_title_and_description(self):
        """Create task with valid title and description."""
        task = task_service.create_task("Buy groceries", "Milk and eggs")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk and eggs"
        assert task.completed is False
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_create_task_with_empty_description(self):
        """Create task with valid title and empty description."""
        task = task_service.create_task("Buy milk", "")

        assert task.id == 1
        assert task.title == "Buy milk"
        assert task.description == ""
        assert task.completed is False

    def test_create_task_sequential_ids(self):
        """Multiple tasks get sequential IDs (1, 2, 3, ...)."""
        task1 = task_service.create_task("Task 1", "")
        task2 = task_service.create_task("Task 2", "")
        task3 = task_service.create_task("Task 3", "")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_create_task_sets_completed_false(self):
        """New task has completed=False."""
        task = task_service.create_task("Test", "")
        assert task.completed is False

    def test_create_task_generates_timestamps(self):
        """Task has valid created_at and updated_at timestamps."""
        task = task_service.create_task("Test", "")

        assert task.created_at is not None
        assert task.updated_at is not None
        assert len(task.created_at) > 0
        assert len(task.updated_at) > 0

    def test_create_task_timestamps_equal(self):
        """created_at equals updated_at for new tasks."""
        task = task_service.create_task("Test", "")
        assert task.created_at == task.updated_at

    def test_create_task_appends_to_storage(self):
        """Task is appended to _task_storage."""
        assert len(task_service._task_storage) == 0

        task = task_service.create_task("Test", "")

        assert len(task_service._task_storage) == 1
        assert task_service._task_storage[0] == task

    def test_create_task_returns_task_instance(self):
        """create_task() returns Task instance."""
        task = task_service.create_task("Test", "")
        assert isinstance(task, Task)


class TestGetAllTasks:
    """Tests for get_all_tasks() function."""

    def test_get_all_tasks_empty(self):
        """Returns empty list when no tasks exist."""
        tasks = task_service.get_all_tasks()
        assert tasks == []

    def test_get_all_tasks_returns_copy(self):
        """Returns a copy of storage, not the original list."""
        task_service.create_task("Test", "")
        tasks = task_service.get_all_tasks()

        # Modifying returned list shouldn't affect storage
        tasks.append(
            Task(
                99, "Fake", "", False, "2025-12-04T10:00:00.000000Z", "2025-12-04T10:00:00.000000Z"
            )
        )

        assert len(task_service._task_storage) == 1
        assert len(tasks) == 2

    def test_get_all_tasks_multiple(self):
        """Returns all tasks from storage."""
        task1 = task_service.create_task("Task 1", "")
        task2 = task_service.create_task("Task 2", "")

        tasks = task_service.get_all_tasks()

        assert len(tasks) == 2
        assert task1 in tasks
        assert task2 in tasks


class TestGetTaskById:
    """Tests for get_task_by_id() function."""

    def test_get_task_by_id_exists(self):
        """Returns task with matching ID."""
        task = task_service.create_task("Test Task", "Description")
        retrieved = task_service.get_task_by_id(1)

        assert retrieved == task
        assert retrieved.id == 1

    def test_get_task_by_id_nonexistent(self):
        """Raises ValueError when task doesn't exist (ERROR 101)."""
        task_service.create_task("Test", "")

        with pytest.raises(ValueError, match="ERROR 101"):
            task_service.get_task_by_id(99)

    def test_get_task_by_id_zero(self):
        """Raises ValueError for task_id = 0 (ERROR 103)."""
        with pytest.raises(ValueError, match="ERROR 103"):
            task_service.get_task_by_id(0)

    def test_get_task_by_id_negative(self):
        """Raises ValueError for negative task_id (ERROR 103)."""
        with pytest.raises(ValueError, match="ERROR 103"):
            task_service.get_task_by_id(-1)


class TestUpdateTask:
    """Tests for update_task() function."""

    def test_update_task_title_only(self):
        """Test updating only the title field."""
        task = task_service.create_task("Original Title", "Original Description")
        original_description = task.description
        original_id = task.id
        original_created_at = task.created_at

        updated = task_service.update_task(1, new_title="Updated Title")

        assert updated.title == "Updated Title"
        assert updated.description == original_description
        assert updated.id == original_id
        assert updated.created_at == original_created_at

    def test_update_task_description_only(self):
        """Test updating only the description field."""
        task = task_service.create_task("Original Title", "Original Description")
        original_title = task.title
        original_id = task.id
        original_created_at = task.created_at

        updated = task_service.update_task(1, new_description="Updated Description")

        assert updated.title == original_title
        assert updated.description == "Updated Description"
        assert updated.id == original_id
        assert updated.created_at == original_created_at

    def test_update_task_both_fields(self):
        """Test updating both title and description."""
        task = task_service.create_task("Original Title", "Original Description")
        original_id = task.id
        original_created_at = task.created_at

        updated = task_service.update_task(
            1, new_title="Updated Title", new_description="Updated Description"
        )

        assert updated.title == "Updated Title"
        assert updated.description == "Updated Description"
        assert updated.id == original_id
        assert updated.created_at == original_created_at

    def test_update_task_updates_timestamp(self):
        """Test that updated_at timestamp changes on update."""
        import time

        task = task_service.create_task("Test", "Description")
        original_updated_at = task.updated_at

        # Small delay to ensure timestamp difference
        time.sleep(0.01)

        updated = task_service.update_task(1, new_title="Updated")

        assert updated.updated_at != original_updated_at

    def test_update_task_preserves_immutable_fields(self):
        """Test that id, completed, created_at are not modified."""
        task = task_service.create_task("Test", "Description")
        original_id = task.id
        original_completed = task.completed
        original_created_at = task.created_at

        task_service.update_task(1, new_title="Updated", new_description="Updated Desc")

        assert task.id == original_id
        assert task.completed == original_completed
        assert task.created_at == original_created_at

    def test_update_task_invalid_id_zero(self):
        """Test updating with task_id = 0 raises ERROR 103."""
        task_service.create_task("Test", "")

        with pytest.raises(ValueError, match="ERROR 103"):
            task_service.update_task(0, new_title="Updated")

    def test_update_task_invalid_id_negative(self):
        """Test updating with task_id = -1 raises ERROR 103."""
        task_service.create_task("Test", "")

        with pytest.raises(ValueError, match="ERROR 103"):
            task_service.update_task(-1, new_title="Updated")

    def test_update_task_nonexistent_id(self):
        """Test updating non-existent task raises ERROR 101."""
        task_service.create_task("Test", "")

        with pytest.raises(ValueError, match="ERROR 101"):
            task_service.update_task(99, new_title="Updated")

    def test_update_task_returns_same_instance(self):
        """Test that update returns the same Task object (in-place modification)."""
        task = task_service.create_task("Test", "Description")
        updated = task_service.update_task(1, new_title="Updated")

        assert updated is task

    def test_update_task_with_none_values(self):
        """Test calling update_task with both new_title=None, new_description=None."""
        task = task_service.create_task("Original", "Description")
        original_title = task.title
        original_description = task.description
        original_updated_at = task.updated_at

        import time

        time.sleep(0.01)

        updated = task_service.update_task(1)

        # Fields should be unchanged
        assert updated.title == original_title
        assert updated.description == original_description
        # But timestamp should update
        assert updated.updated_at != original_updated_at


class TestDeleteTask:
    """Tests for delete_task() function."""

    def test_delete_existing_task(self):
        """Delete existing task removes it from storage and returns task."""
        # Setup: Create 3 tasks
        task1 = task_service.create_task("Task 1", "Description 1")
        task2 = task_service.create_task("Task 2", "Description 2")
        task3 = task_service.create_task("Task 3", "Description 3")

        # Action: delete task 2
        deleted = task_service.delete_task(task_id=2)

        # Assert: Task 2 removed, tasks 1 and 3 unchanged, returns deleted task
        assert deleted == task2
        assert deleted.id == 2
        assert deleted.title == "Task 2"
        assert len(task_service._task_storage) == 2
        assert task1 in task_service._task_storage
        assert task2 not in task_service._task_storage
        assert task3 in task_service._task_storage

    def test_delete_non_existent_task(self):
        """Delete non-existent task raises ValueError with ERROR 101."""
        # Setup: Create tasks with IDs [1, 2]
        task_service.create_task("Task 1", "")
        task_service.create_task("Task 2", "")

        # Action: delete task 99
        with pytest.raises(ValueError, match="ERROR 101"):
            task_service.delete_task(task_id=99)

        # Assert: Storage unchanged
        assert len(task_service._task_storage) == 2

    def test_delete_with_invalid_id_zero(self):
        """Delete with ID 0 raises ValueError with ERROR 103."""
        # Action: delete task 0
        with pytest.raises(ValueError, match="ERROR 103"):
            task_service.delete_task(task_id=0)

    def test_delete_with_negative_id(self):
        """Delete with negative ID raises ValueError with ERROR 103."""
        # Action: delete task -5
        with pytest.raises(ValueError, match="ERROR 103"):
            task_service.delete_task(task_id=-5)

    def test_delete_last_remaining_task(self):
        """Delete only task in list results in empty storage."""
        # Setup: Create 1 task with ID 5 (non-sequential for thoroughness)
        task_service.create_task("Task 1", "")
        task_service.create_task("Task 2", "")
        task_service.create_task("Task 3", "")
        task_service.create_task("Task 4", "")
        task = task_service.create_task("Last Task", "")

        # Delete all but the last one
        task_service.delete_task(1)
        task_service.delete_task(2)
        task_service.delete_task(3)
        task_service.delete_task(4)

        # Action: delete last task
        deleted = task_service.delete_task(task_id=5)

        # Assert: Returns deleted task, _task_storage is empty list
        assert deleted == task
        assert deleted.id == 5
        assert len(task_service._task_storage) == 0
        assert task_service._task_storage == []

    def test_delete_does_not_renumber_ids(self):
        """Deleting middle task preserves IDs of remaining tasks."""
        # Setup: Create tasks with IDs [1, 2, 3, 4, 5]
        task1 = task_service.create_task("Task 1", "")
        task2 = task_service.create_task("Task 2", "")
        task_service.create_task("Task 3", "")  # Will be deleted
        task4 = task_service.create_task("Task 4", "")
        task5 = task_service.create_task("Task 5", "")

        # Action: delete task 3
        task_service.delete_task(task_id=3)

        # Assert: Remaining IDs are [1, 2, 4, 5] (not [1, 2, 3, 4])
        remaining_ids = [task.id for task in task_service._task_storage]
        assert remaining_ids == [1, 2, 4, 5]
        assert task1.id == 1
        assert task2.id == 2
        assert task4.id == 4
        assert task5.id == 5


class TestToggleTaskCompletion:
    """Tests for toggle_task_completion() function."""

    def test_toggle_incomplete_to_complete(self):
        """Test toggling task from incomplete to complete updates status and timestamp."""
        # Setup: Create incomplete task
        task = task_service.create_task("Buy groceries", "Milk and eggs")
        original_updated_at = task.updated_at
        assert task.completed is False

        # Execute: Toggle to complete
        result = task_service.toggle_task_completion(task.id)

        # Verify: Status changed to True
        assert result.completed is True
        # Verify: Timestamp updated
        assert result.updated_at != original_updated_at
        # Verify: Other fields unchanged
        assert result.id == task.id
        assert result.title == "Buy groceries"
        assert result.description == "Milk and eggs"
        assert result.created_at == task.created_at

    def test_toggle_complete_to_incomplete(self):
        """Test toggling task from complete to incomplete updates status and timestamp."""
        # Setup: Create task and mark it complete
        task = task_service.create_task("Finish project", "Submit by Friday")
        task_service.toggle_task_completion(task.id)  # Now complete
        original_updated_at = task.updated_at
        assert task.completed is True

        # Execute: Toggle back to incomplete
        result = task_service.toggle_task_completion(task.id)

        # Verify: Status changed to False
        assert result.completed is False
        # Verify: Timestamp updated
        assert result.updated_at != original_updated_at
        # Verify: Other fields unchanged
        assert result.id == task.id
        assert result.title == "Finish project"

    def test_toggle_updates_timestamp(self):
        """Test that toggle always updates updated_at timestamp."""
        # Setup
        task = task_service.create_task("Test task", "Description")
        original_updated_at = task.updated_at

        # Execute: Toggle (doesn't matter which direction)
        task_service.toggle_task_completion(task.id)

        # Verify: Timestamp is different
        assert task.updated_at != original_updated_at

    def test_toggle_preserves_created_at(self):
        """Test that toggle never modifies created_at timestamp."""
        # Setup
        task = task_service.create_task("Test task", "Description")
        original_created_at = task.created_at

        # Execute: Toggle multiple times
        task_service.toggle_task_completion(task.id)
        task_service.toggle_task_completion(task.id)
        task_service.toggle_task_completion(task.id)

        # Verify: created_at never changed
        assert task.created_at == original_created_at

    def test_toggle_preserves_other_fields(self):
        """Test that id, title, description are not modified."""
        task = task_service.create_task("Test task", "Description")
        original_id = task.id
        original_title = task.title
        original_description = task.description

        task_service.toggle_task_completion(task.id)

        assert task.id == original_id
        assert task.title == original_title
        assert task.description == original_description

    def test_toggle_nonexistent_task(self):
        """Test toggling non-existent task raises ValueError with ERROR 101."""
        # Setup: Empty task list
        task_service._task_storage.clear()

        # Execute & Verify: Raises ValueError with task not found message
        with pytest.raises(ValueError, match="ERROR 101: Task with ID 999 not found"):
            task_service.toggle_task_completion(999)

    def test_toggle_zero_task_id(self):
        """Test toggling with zero task ID raises ValueError with ERROR 103."""
        # Execute & Verify: Raises ValueError for invalid ID
        with pytest.raises(ValueError, match="ERROR 103: Task ID must be a positive number"):
            task_service.toggle_task_completion(0)

    def test_toggle_negative_task_id(self):
        """Test toggling with negative task ID raises ValueError with ERROR 103."""
        # Execute & Verify: Raises ValueError for invalid ID
        with pytest.raises(ValueError, match="ERROR 103: Task ID must be a positive number"):
            task_service.toggle_task_completion(-5)
