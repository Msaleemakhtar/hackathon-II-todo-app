"""Unit tests for main application menu."""

from unittest.mock import patch, MagicMock

from src.main import handle_add_task, main


class TestHandleAddTask:
    """Tests for handle_add_task function."""

    @patch("src.main.print")
    @patch("src.main.create_task")
    @patch("src.main.get_task_description")
    @patch("src.main.get_task_title")
    def test_handle_add_task_full_flow(
        self, mock_get_title, mock_get_desc, mock_create, mock_print
    ):
        """Test complete add task flow with mocked inputs."""
        mock_get_title.return_value = "Test Task"
        mock_get_desc.return_value = "Test Description"

        handle_add_task()

        mock_get_title.assert_called_once()
        mock_get_desc.assert_called_once()
        mock_create.assert_called_once_with("Test Task", "Test Description")
        mock_print.assert_called_once_with("Task added successfully.")


class TestMainMenu:
    """Tests for main menu loop."""

    @patch("builtins.input")
    @patch("src.main.Console")
    @patch("src.main.handle_add_task")
    def test_main_menu_option_1_add_task(self, mock_handle, mock_console, mock_input):
        """Test selecting option 1 calls handle_add_task."""
        # Mock the console instance and its print method
        console_instance = mock_console.return_value
        console_instance.print = MagicMock()

        mock_input.side_effect = ["1", "7"]  # Select Add Task, then Exit

        main()

        mock_handle.assert_called_once()
        # Check if "Goodbye!" was printed using console
        goodbye_calls = [call for call in console_instance.print.call_args_list
                        if "Goodbye!" in str(call)]
        assert len(goodbye_calls) > 0

    @patch("builtins.input")
    @patch("src.main.Console")
    def test_main_menu_option_7_exit(self, mock_console, mock_input):
        """Test selecting option 7 exits with goodbye message."""
        # Mock the console instance and its print method
        console_instance = mock_console.return_value
        console_instance.print = MagicMock()

        mock_input.return_value = "7"

        main()

        # Check if "Goodbye!" was printed using console
        goodbye_calls = [call for call in console_instance.print.call_args_list
                        if "Goodbye!" in str(call)]
        assert len(goodbye_calls) > 0

    @patch("builtins.input")
    @patch("src.main.Console")
    def test_main_menu_invalid_option(self, mock_console, mock_input):
        """Test invalid option shows error message."""
        # Mock the console instance and its print method
        console_instance = mock_console.return_value
        console_instance.print = MagicMock()

        mock_input.side_effect = ["99", "7"]  # Invalid option, then Exit

        main()

        print_calls = [str(call) for call in console_instance.print.call_args_list]
        assert any("Invalid option. Please select 1-7." in call for call in print_calls)

    @patch("builtins.input")
    @patch("src.main.Console")
    def test_main_menu_displays_all_options(self, mock_console, mock_input):
        """Test main menu displays all 7 options."""
        # Mock the console instance and its print method
        console_instance = mock_console.return_value
        console_instance.print = MagicMock()

        mock_input.return_value = "7"

        main()

        # Check that console.print was called (includes Panel for "Todo App" and menu options)
        assert console_instance.print.call_count >= 8  # Panel + 7 options + goodbye
        print_calls = [str(call) for call in console_instance.print.call_args_list]
        # The menu options should be printed with console.print
        assert any("ADD TASK" in call for call in print_calls)
        assert any("VIEW TASKS" in call for call in print_calls)
        assert any("VIEW TASK DETAILS" in call for call in print_calls)
        assert any("UPDATE TASK" in call for call in print_calls)
        assert any("DELETE TASK" in call for call in print_calls)
        assert any("MARK COMPLETE" in call for call in print_calls)
        assert any("EXIT" in call for call in print_calls)

    @patch("builtins.input")
    @patch("src.main.Console")
    @patch("src.main.handle_add_task")
    def test_main_menu_multiple_operations(self, mock_handle, mock_console, mock_input):
        """Test multiple operations in sequence."""
        # Mock the console instance and its print method
        console_instance = mock_console.return_value
        console_instance.print = MagicMock()

        # Add task twice, try invalid option, then exit
        mock_input.side_effect = ["1", "1", "invalid", "7"]

        main()

        assert mock_handle.call_count == 2
        # Check if "Goodbye!" was printed using console
        goodbye_calls = [call for call in console_instance.print.call_args_list
                        if "Goodbye!" in str(call)]
        assert len(goodbye_calls) > 0

    @patch("builtins.input")
    @patch("src.main.Console")
    def test_main_menu_empty_input(self, mock_console, mock_input):
        """Test empty input treated as invalid option."""
        # Mock the console instance and its print method
        console_instance = mock_console.return_value
        console_instance.print = MagicMock()

        mock_input.side_effect = ["", "7"]

        main()

        print_calls = [str(call) for call in console_instance.print.call_args_list]
        assert any("Invalid option. Please select 1-7." in call for call in print_calls)

    @patch("builtins.input")
    @patch("src.main.Console")
    def test_main_menu_whitespace_input(self, mock_console, mock_input):
        """Test whitespace input treated as invalid option."""
        # Mock the console instance and its print method
        console_instance = mock_console.return_value
        console_instance.print = MagicMock()

        mock_input.side_effect = ["   ", "7"]

        main()

        print_calls = [str(call) for call in console_instance.print.call_args_list]
        assert any("Invalid option. Please select 1-7." in call for call in print_calls)

    @patch("builtins.input")
    @patch("src.main.Console")
    @patch("src.main.update_task_prompt")
    def test_main_menu_loop_continues_after_operation(self, mock_update, mock_console, mock_input):
        """Test menu loop continues after each operation."""
        # Mock the console instance and its print method
        console_instance = mock_console.return_value
        console_instance.print = MagicMock()

        # Option 2: View Tasks, Option 4: Update Task, Exit
        mock_input.side_effect = ["2", "4", "7"]

        main()

        # Update task should be called once
        mock_update.assert_called_once()
        # Check that menu was displayed 3 times by counting Panel objects (one per menu display)
        # Each menu iteration prints a Panel, so we count Panel objects in the calls
        from rich.panel import Panel
        panel_count = sum(1 for call in console_instance.print.call_args_list
                         if call[0] and isinstance(call[0][0], Panel))
        assert panel_count == 3
