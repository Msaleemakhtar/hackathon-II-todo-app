"""Integration tests for complete delete task workflow."""

import pytest

from src.services import task_service
from src.ui.prompts import delete_task_prompt


@pytest.fixture(autouse=True)
def reset_task_storage():
    """Reset task storage before each test."""
    task_service._task_storage.clear()
    yield
    task_service._task_storage.clear()


class TestDeleteTaskFlow:
    """Integration tests for complete delete task workflow."""

    def test_successful_deletion_with_confirmation(self, monkeypatch, capsys):
        """Valid ID + Y confirmation deletes task and shows success message."""
        # Setup: Create 3 tasks
        task_service.create_task("Task 1", "Description 1")
        task_service.create_task("Task 2", "Description 2")
        task_service.create_task("Task 3", "Description 3")

        # Mock input: ["2", "Y"]
        inputs = iter(["2", "Y"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        # Call: delete_task_prompt()
        delete_task_prompt()

        # Assert: Task 2 deleted, MSG_TASK_DELETED printed
        captured = capsys.readouterr()
        assert "Task deleted successfully." in captured.out
        assert len(task_service._task_storage) == 2
        remaining_ids = [task.id for task in task_service._task_storage]
        assert 2 not in remaining_ids
        assert 1 in remaining_ids
        assert 3 in remaining_ids

    def test_cancel_deletion_preserves_task(self, monkeypatch, capsys):
        """Valid ID + N response preserves task and shows cancellation."""
        # Setup: Create 2 tasks
        task_service.create_task("Task 1", "Description 1")
        task_service.create_task("Task 2", "Description 2")

        # Mock input: ["1", "N"]
        inputs = iter(["1", "N"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        # Call: delete_task_prompt()
        delete_task_prompt()

        # Assert: Task 1 preserved, MSG_DELETION_CANCELED printed
        captured = capsys.readouterr()
        assert "Deletion canceled." in captured.out
        assert len(task_service._task_storage) == 2
        # Verify task 1 still exists
        task = task_service.get_task_by_id(1)
        assert task.id == 1

    def test_invalid_id_format_shows_error(self, monkeypatch, capsys):
        """Non-numeric ID shows ERROR 102 and returns to menu."""
        # Setup: Create tasks
        task_service.create_task("Task 1", "")
        task_service.create_task("Task 2", "")

        # Mock input: ["abc"]
        monkeypatch.setattr("builtins.input", lambda _: "abc")

        # Call: delete_task_prompt()
        delete_task_prompt()

        # Assert: ERROR 102 printed, no confirmation prompt, storage unchanged
        captured = capsys.readouterr()
        assert "ERROR 102" in captured.out
        assert len(task_service._task_storage) == 2

    def test_zero_id_shows_error(self, monkeypatch, capsys):
        """ID 0 shows ERROR 103 and returns to menu."""
        # Setup: Create tasks
        task_service.create_task("Task 1", "")

        # Mock input: ["0"]
        monkeypatch.setattr("builtins.input", lambda _: "0")

        # Call: delete_task_prompt()
        delete_task_prompt()

        # Assert: ERROR 103 printed, storage unchanged
        captured = capsys.readouterr()
        assert "ERROR 103" in captured.out
        assert len(task_service._task_storage) == 1

    def test_negative_id_shows_error(self, monkeypatch, capsys):
        """Negative ID shows ERROR 103 and returns to menu."""
        # Setup: Create tasks
        task_service.create_task("Task 1", "")

        # Mock input: ["-5"]
        monkeypatch.setattr("builtins.input", lambda _: "-5")

        # Call: delete_task_prompt()
        delete_task_prompt()

        # Assert: ERROR 103 printed, storage unchanged
        captured = capsys.readouterr()
        assert "ERROR 103" in captured.out
        assert len(task_service._task_storage) == 1

    def test_non_existent_id_shows_error(self, monkeypatch, capsys):
        """Non-existent ID shows ERROR 101, no confirmation prompt."""
        # Setup: Tasks with IDs [1, 2]
        task_service.create_task("Task 1", "")
        task_service.create_task("Task 2", "")

        # Mock input: ["99"]
        monkeypatch.setattr("builtins.input", lambda _: "99")

        # Call: delete_task_prompt()
        delete_task_prompt()

        # Assert: ERROR 101 printed, no confirmation prompt shown
        captured = capsys.readouterr()
        assert "ERROR 101" in captured.out
        assert "Delete task" not in captured.out  # No confirmation prompt
        assert len(task_service._task_storage) == 2

    def test_invalid_confirmation_then_confirm(self, monkeypatch, capsys):
        """Invalid confirmation shows ERROR 105, re-prompts, then deletes."""
        # Setup: Create task ID 3
        task_service.create_task("Task 1", "")
        task_service.create_task("Task 2", "")
        task_service.create_task("Task 3", "")

        # Mock input: ["3", "maybe", "Y"]
        inputs = iter(["3", "maybe", "Y"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        # Call: delete_task_prompt()
        delete_task_prompt()

        # Assert: ERROR 105 printed, task deleted, MSG_TASK_DELETED printed
        captured = capsys.readouterr()
        assert "ERROR 105" in captured.out
        assert "Task deleted successfully." in captured.out
        assert len(task_service._task_storage) == 2
        remaining_ids = [task.id for task in task_service._task_storage]
        assert 3 not in remaining_ids

    def test_delete_from_empty_list(self, monkeypatch, capsys):
        """Deleting from empty list shows ERROR 101."""
        # Setup: Empty task list (no tasks created)

        # Mock input: ["1"]
        monkeypatch.setattr("builtins.input", lambda _: "1")

        # Call: delete_task_prompt()
        delete_task_prompt()

        # Assert: ERROR 101 printed
        captured = capsys.readouterr()
        assert "ERROR 101" in captured.out
        assert len(task_service._task_storage) == 0
