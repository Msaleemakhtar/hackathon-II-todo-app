"""Integration tests for Mark Complete feature end-to-end workflows."""

from unittest.mock import patch

import pytest

from src.services.task_service import _task_storage, create_task


@pytest.fixture(autouse=True)
def reset_storage():
    """Clear task storage before each test."""
    _task_storage.clear()
    yield
    _task_storage.clear()


def test_mark_complete_flow_incomplete_to_complete():
    """Test complete flow: create task → mark complete → verify status changed."""
    # Setup: Create incomplete task
    task = create_task("Buy groceries", "Milk and eggs")
    assert task.completed is False
    original_updated_at = task.updated_at

    # Execute: Simulate user selecting Mark Complete, entering ID 1, confirming Y
    with patch("builtins.input", side_effect=["1", "Y"]):
        from src.ui.prompts import mark_complete_prompt

        mark_complete_prompt()

    # Verify: Task is now marked complete
    assert task.completed is True
    # Verify: Timestamp updated
    assert task.updated_at != original_updated_at
    # Verify: Other fields unchanged
    assert task.title == "Buy groceries"
    assert task.description == "Milk and eggs"


def test_mark_complete_flow_complete_to_incomplete():
    """Test complete flow: create task → mark complete → mark incomplete → verify toggle."""
    # Setup: Create task and mark it complete
    task = create_task("Finish project", "Submit by Friday")
    with patch("builtins.input", side_effect=["1", "Y"]):
        from src.ui.prompts import mark_complete_prompt

        mark_complete_prompt()  # Now complete

    assert task.completed is True

    # Execute: Mark incomplete
    with patch("builtins.input", side_effect=["1", "Y"]):
        mark_complete_prompt()

    # Verify: Task is back to incomplete
    assert task.completed is False


def test_mark_complete_flow_cancellation():
    """Test complete flow: create task → attempt mark complete → cancel → verify no change."""
    # Setup: Create incomplete task
    task = create_task("Write tests", "Unit and integration")
    assert task.completed is False
    original_updated_at = task.updated_at

    # Execute: Simulate user canceling with N
    with patch("builtins.input", side_effect=["1", "N"]):
        from src.ui.prompts import mark_complete_prompt

        mark_complete_prompt()

    # Verify: Task status unchanged
    assert task.completed is False
    # Verify: Timestamp unchanged
    assert task.updated_at == original_updated_at


def test_mark_complete_flow_invalid_id_non_numeric():
    """Test error handling for non-numeric task ID input."""
    # Setup: Create task
    create_task("Test task", "Description")

    # Execute: Simulate user entering non-numeric ID, then numeric, then canceling
    with patch("builtins.input", side_effect=["abc", "1", "N"]):
        with patch("builtins.print") as mock_print:
            from src.ui.prompts import mark_complete_prompt

            mark_complete_prompt()

            # Verify: Error message printed for "abc" (first call)
            # Note: exact call order depends on implementation
            error_calls = [call for call in mock_print.call_args_list if "ERROR 102" in str(call)]
            assert len(error_calls) >= 1


def test_mark_complete_flow_invalid_id_zero():
    """Test error handling for zero task ID input."""
    # Setup: Create task
    create_task("Test task", "Description")

    # Execute: Simulate user entering 0, then 1, then canceling
    with patch("builtins.input", side_effect=["0", "1", "N"]):
        with patch("builtins.print") as mock_print:
            from src.ui.prompts import mark_complete_prompt

            mark_complete_prompt()

            # Verify: Error message printed for "0"
            error_calls = [call for call in mock_print.call_args_list if "ERROR 103" in str(call)]
            assert len(error_calls) >= 1


def test_mark_complete_flow_nonexistent_task():
    """Test error handling for non-existent task ID."""
    # Setup: Create task with ID 1
    create_task("Test task", "Description")

    # Execute: Simulate user entering ID 999 (doesn't exist)
    with patch("builtins.input", return_value="999"):
        with patch("builtins.print") as mock_print:
            from src.ui.prompts import mark_complete_prompt

            mark_complete_prompt()

            # Verify: Error message printed and no confirmation prompt shown
            mock_print.assert_called_with("ERROR 101: Task with ID 999 not found.")


def test_mark_complete_flow_invalid_confirmation():
    """Test error handling for invalid confirmation input (retries until valid)."""
    # Setup: Create task
    create_task("Test task", "Description")

    # Execute: Simulate user entering ID 1, then invalid confirmations, then N
    with patch("builtins.input", side_effect=["1", "yes", "maybe", "1", "N"]):
        with patch("builtins.print") as mock_print:
            from src.ui.prompts import mark_complete_prompt

            mark_complete_prompt()

            # Verify: Error message printed for invalid confirmations
            error_calls = [call for call in mock_print.call_args_list if "ERROR 205" in str(call)]
            assert len(error_calls) >= 2  # "yes" and "maybe"


def test_mark_complete_flow_multiple_toggles():
    """Test multiple consecutive toggles alternate status correctly."""
    # Setup: Create task
    task = create_task("Toggle test", "Test description")

    # Execute: Toggle 5 times
    for i in range(5):
        expected_status = (i + 1) % 2 == 1  # Odd iterations = complete, even = incomplete
        with patch("builtins.input", side_effect=["1", "Y"]):
            from src.ui.prompts import mark_complete_prompt

            mark_complete_prompt()

        # Verify: Status matches expected
        assert task.completed is expected_status


def test_mark_complete_flow_empty_task_list():
    """Test error handling when attempting to mark complete with no tasks."""
    # Setup: Empty task list (cleared by fixture)

    # Execute: Simulate user entering any task ID
    with patch("builtins.input", return_value="1"):
        with patch("builtins.print") as mock_print:
            from src.ui.prompts import mark_complete_prompt

            mark_complete_prompt()

            # Verify: Error message printed
            mock_print.assert_called_with("ERROR 101: Task with ID 1 not found.")
