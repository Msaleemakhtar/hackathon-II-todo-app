"""Integration tests for complete add task flow."""

from unittest.mock import patch

import pytest

from src.constants import (
    ERROR_DESCRIPTION_TOO_LONG,
    ERROR_TITLE_REQUIRED,
    ERROR_TITLE_TOO_LONG,
    MSG_TASK_ADDED,
)
from src.main import handle_add_task
from src.services import task_service


@pytest.fixture(autouse=True)
def reset_task_storage():
    """Reset task storage before each test."""
    task_service._task_storage.clear()
    yield
    task_service._task_storage.clear()


class TestAddTaskIntegration:
    """Integration tests for complete add task user flow."""

    @patch("builtins.input")
    @patch("builtins.print")
    def test_add_task_with_title_and_description(self, mock_print, mock_input):
        """Complete flow: valid title + valid description → task created."""
        mock_input.side_effect = ["Buy groceries", "Milk and eggs"]

        handle_add_task()

        tasks = task_service.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].id == 1
        assert tasks[0].title == "Buy groceries"
        assert tasks[0].description == "Milk and eggs"
        assert tasks[0].completed is False

        # Verify success message printed
        mock_print.assert_called_with(MSG_TASK_ADDED)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_add_task_with_title_only(self, mock_print, mock_input):
        """Complete flow: valid title + empty description → task created."""
        mock_input.side_effect = ["Buy milk", ""]

        handle_add_task()

        tasks = task_service.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Buy milk"
        assert tasks[0].description == ""

        mock_print.assert_called_with(MSG_TASK_ADDED)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_add_task_empty_title_retry(self, mock_print, mock_input):
        """Flow handles empty title → displays error → accepts valid retry."""
        mock_input.side_effect = ["", "Valid Title", "Description"]

        handle_add_task()

        tasks = task_service.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Valid Title"

        # Verify error was printed before success
        assert any(ERROR_TITLE_REQUIRED in str(call) for call in mock_print.call_args_list)
        assert mock_print.call_args_list[-1][0][0] == MSG_TASK_ADDED

    @patch("builtins.input")
    @patch("builtins.print")
    def test_add_task_title_too_long_retry(self, mock_print, mock_input):
        """Flow handles title > 200 chars → displays error → accepts valid retry."""
        long_title = "A" * 201
        mock_input.side_effect = [long_title, "Valid Title", ""]

        handle_add_task()

        tasks = task_service.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Valid Title"

        # Verify ERROR 002 was printed
        assert any(ERROR_TITLE_TOO_LONG in str(call) for call in mock_print.call_args_list)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_add_task_description_too_long_retry(self, mock_print, mock_input):
        """Flow handles description > 1000 chars → displays error → accepts valid retry."""
        long_description = "B" * 1001
        mock_input.side_effect = ["Valid Title", long_description, "Valid description"]

        handle_add_task()

        tasks = task_service.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].description == "Valid description"

        # Verify ERROR 003 was printed
        assert any(ERROR_DESCRIPTION_TOO_LONG in str(call) for call in mock_print.call_args_list)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_add_task_first_task_gets_id_1(self, mock_print, mock_input):
        """First task gets ID 1."""
        mock_input.side_effect = ["First Task", ""]

        handle_add_task()

        tasks = task_service.get_all_tasks()
        assert tasks[0].id == 1

    @patch("builtins.input")
    @patch("builtins.print")
    def test_add_task_second_task_gets_id_2(self, mock_print, mock_input):
        """Second task gets ID 2."""
        # Add first task
        mock_input.side_effect = ["First Task", ""]
        handle_add_task()

        # Add second task
        mock_input.side_effect = ["Second Task", ""]
        handle_add_task()

        tasks = task_service.get_all_tasks()
        assert len(tasks) == 2
        assert tasks[0].id == 1
        assert tasks[1].id == 2

    @patch("builtins.input")
    @patch("builtins.print")
    def test_add_task_appears_in_storage(self, mock_print, mock_input):
        """Task appears in storage after creation."""
        assert len(task_service.get_all_tasks()) == 0

        mock_input.side_effect = ["Test Task", "Test Description"]
        handle_add_task()

        tasks = task_service.get_all_tasks()
        assert len(tasks) == 1

    @patch("builtins.input")
    @patch("builtins.print")
    def test_add_task_success_message_displayed(self, mock_print, mock_input):
        """Success message displayed after task created."""
        mock_input.side_effect = ["Test", ""]

        handle_add_task()

        mock_print.assert_called_with(MSG_TASK_ADDED)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_add_task_multiple_validation_failures(self, mock_print, mock_input):
        """Multiple validation failures allow continued retry."""
        mock_input.side_effect = [
            "",  # Empty title
            "A" * 201,  # Title too long
            "Valid Title",  # Valid title
            "B" * 1001,  # Description too long
            "Valid description",  # Valid description
        ]

        handle_add_task()

        tasks = task_service.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Valid Title"
        assert tasks[0].description == "Valid description"

        # Verify both error types were printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any(ERROR_TITLE_REQUIRED in call for call in print_calls)
        assert any(ERROR_TITLE_TOO_LONG in call for call in print_calls)
        assert any(ERROR_DESCRIPTION_TOO_LONG in call for call in print_calls)
