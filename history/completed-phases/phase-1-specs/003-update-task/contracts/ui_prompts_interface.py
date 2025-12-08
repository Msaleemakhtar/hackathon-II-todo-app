"""
UI Layer Contract: Update Task Feature

This file defines the public interface contract for update functions in ui/prompts.py.
These functions will be added to the existing prompts module.

Feature: 003-update-task
Date: 2025-12-06
Status: Design Contract
"""

from typing import Protocol


class UpdateTaskUIProtocol(Protocol):
    """
    Protocol defining the contract for update UI functions in ui/prompts.py.

    These functions handle all console output and input collection for the
    Update Task feature. They perform validation and user interaction but
    do not contain business logic.
    """

    def display_field_selection_menu(self) -> None:
        """
        Display the field selection menu for choosing which field(s) to update.

        Returns:
            None: Outputs directly to console.

        Behavior:
            - Displays a header line: "Select fields to update:"
            - Displays three numbered options:
              1. Update Title Only
              2. Update Description Only
              3. Update Both Title and Description
            - Uses clear, numbered format matching main menu pattern

        Format Specification:
            Select fields to update:
            1. Update Title Only
            2. Update Description Only
            3. Update Both Title and Description

        Testing:
            - Test output matches exact format above
            - Test numbers are sequential 1-3
            - Test clear line breaks between header and options
        """
        ...

    def prompt_for_field_choice(self) -> int:
        """
        Prompt user to select which field(s) to update and validate the choice.

        Returns:
            int: Valid field selection choice (1, 2, or 3)

        Raises:
            None: This function loops internally until valid input is provided.
                  Does not raise exceptions; prints error and re-prompts instead.

        Behavior:
            - Displays prompt: "Select update option (1-3): "
            - Accepts user input
            - Validates input is numeric (can convert to int)
            - Validates input is in range 1-3 (inclusive)
            - If invalid: displays ERROR 104 and re-prompts
            - If valid: returns the integer choice

        Error Handling:
            - Input "abc" → displays "ERROR 104: Invalid option. Please select 1, 2, or 3." and re-prompts
            - Input "0" → displays ERROR 104 and re-prompts
            - Input "4" → displays ERROR 104 and re-prompts
            - Input "2.5" → displays ERROR 104 and re-prompts (non-integer)
            - Input "1", "2", or "3" → returns that integer

        Example:
            >>> choice = prompt_for_field_choice()
            Select update option (1-3): abc
            ERROR 104: Invalid option. Please select 1, 2, or 3.
            Select update option (1-3): 0
            ERROR 104: Invalid option. Please select 1, 2, or 3.
            Select update option (1-3): 2
            >>> print(choice)
            2

        Testing:
            - Test with valid choices (1, 2, 3) → returns int
            - Test with "0" → displays ERROR 104 and re-prompts
            - Test with "4" → displays ERROR 104 and re-prompts
            - Test with "abc" → displays ERROR 104 and re-prompts
            - Test with "-1" → displays ERROR 104 and re-prompts
            - Test error message matches exact format from spec
        """
        ...

    def get_new_task_title(self, current_title: str) -> str:
        """
        Prompt user for new task title with validation loop, showing current value.

        Args:
            current_title: The task's current title (for display context)

        Returns:
            str: Valid new task title (stripped of leading/trailing whitespace)

        Raises:
            None: This function loops internally until valid input is provided.

        Behavior:
            - Displays prompt: "Enter New Task Title: "
            - (Optionally displays current value as context)
            - Accepts user input
            - Validates using validate_title() function (reused from add-task)
            - If invalid: displays ERROR 001 or ERROR 002 and re-prompts
            - If valid: returns stripped title

        Validation Rules (via validate_title):
            - Empty or whitespace-only → ERROR 001
            - Length > 200 chars → ERROR 002
            - Otherwise → valid

        Example:
            >>> new_title = get_new_task_title("Buy groceries")
            Enter New Task Title:
            ERROR 001: Title is required and must be 1-200 characters.
            Enter New Task Title: {"a" * 250}
            ERROR 002: Title is required and must be 1-200 characters.
            Enter New Task Title: Buy groceries for the week
            >>> print(new_title)
            Buy groceries for the week

        Testing:
            - Test with empty input → displays ERROR 001 and re-prompts
            - Test with whitespace-only → displays ERROR 001 and re-prompts
            - Test with title > 200 chars → displays ERROR 002 and re-prompts
            - Test with valid title → returns stripped title
            - Test that current_title is used for context (optional display feature)
        """
        ...

    def get_new_task_description(self, current_description: str) -> str:
        """
        Prompt user for new task description with validation loop, showing current value.

        Args:
            current_description: The task's current description (for display context)

        Returns:
            str: Valid new task description (stripped, may be empty string)

        Raises:
            None: This function loops internally until valid input is provided.

        Behavior:
            - Displays prompt: "Enter New Task Description (press Enter to clear): "
            - (Optionally displays current value as context)
            - Accepts user input
            - Validates using validate_description() function (reused from add-task)
            - If invalid: displays ERROR 003 and re-prompts
            - If valid: returns stripped description (may be empty)

        Validation Rules (via validate_description):
            - Length > 1000 chars → ERROR 003
            - Empty input → valid (empty string)
            - Otherwise → valid

        Example:
            >>> new_desc = get_new_task_description("Milk and eggs")
            Enter New Task Description (press Enter to clear): {"a" * 1200}
            ERROR 003: Description cannot exceed 1000 characters.
            Enter New Task Description (press Enter to clear): Milk, eggs, bread, cheese
            >>> print(new_desc)
            Milk, eggs, bread, cheese

            >>> empty_desc = get_new_task_description("Old description")
            Enter New Task Description (press Enter to clear):
            >>> print(repr(empty_desc))
            ''

        Testing:
            - Test with description > 1000 chars → displays ERROR 003 and re-prompts
            - Test with valid description → returns stripped description
            - Test with empty input → returns empty string (valid)
            - Test that whitespace-only input returns empty string
            - Test that current_description is used for context (optional display feature)
        """
        ...

    def update_task_prompt(self) -> None:
        """
        Orchestrate the complete update task workflow with user interaction.

        Returns:
            None: Performs update operation and displays success/error messages.

        Behavior:
            1. Call prompt_for_task_id() to get task ID (with ERROR 102/103 handling)
            2. Try to get task using get_task_by_id():
               - If ValueError with ERROR 101 → display message and return to menu
               - If ValueError with ERROR 103 → caught by prompt_for_task_id(), re-prompts
            3. Display current task values using display_task_details() or similar
            4. Call display_field_selection_menu()
            5. Call prompt_for_field_choice() to get choice (1-3)
            6. Based on choice:
               - Option 1: Call get_new_task_title(task.title)
               - Option 2: Call get_new_task_description(task.description)
               - Option 3: Call both get_new_task_title() and get_new_task_description()
            7. Call service.update_task() with appropriate parameters:
               - Option 1: update_task(task_id, new_title=title, new_description=None)
               - Option 2: update_task(task_id, new_title=None, new_description=desc)
               - Option 3: update_task(task_id, new_title=title, new_description=desc)
            8. Display success message: "Task updated successfully."
            9. Return to main menu

        Error Handling Flow:
            - task_id input errors (102, 103) → handled by prompt_for_task_id() re-prompt loop
            - task_id not found (101) → display error and return to menu
            - field selection errors (104) → handled by prompt_for_field_choice() re-prompt loop
            - title validation errors (001, 002) → handled by get_new_task_title() re-prompt loop
            - description validation errors (003) → handled by get_new_task_description() re-prompt loop

        Integration:
            - Calls prompt_for_task_id() from existing UI functions (002-view-task)
            - Calls get_task_by_id() from existing service layer (002-view-task)
            - Calls update_task() from new service layer method (this feature)
            - Calls new UI functions defined in this contract

        Example Flow (Option 1 - Title Only):
            >>> update_task_prompt()
            Enter Task ID: 5
            ID: 5
            Title: Buy groceries
            Description: Milk and eggs
            Completed: No
            Created At: 2025-12-06T10:00:00.000000Z
            Updated At: 2025-12-06T10:00:00.000000Z

            Select fields to update:
            1. Update Title Only
            2. Update Description Only
            3. Update Both Title and Description
            Select update option (1-3): 1
            Enter New Task Title: Buy groceries for the week
            Task updated successfully.

        Testing:
            - Test complete flow for option 1 (title only)
            - Test complete flow for option 2 (description only)
            - Test complete flow for option 3 (both fields)
            - Test with non-existent task ID → displays ERROR 101 and returns
            - Test with invalid field selection → re-prompts until valid
            - Test with invalid title input → re-prompts until valid
            - Test with invalid description input → re-prompts until valid
            - Test that success message appears after valid update
            - Test that user returns to main menu after completion
        """
        ...


# Contract Verification Notes:
# =============================
#
# 1. Separation of Concerns:
#    - UI functions only handle user interaction and display
#    - Validation performed using reused functions (validate_title, validate_description)
#    - Business logic delegated to service layer (update_task)
#
# 2. Error Handling:
#    - ERROR 104: Invalid field selection (UI layer responsibility)
#    - ERROR 001-003: Title/description validation (UI layer, reused validators)
#    - ERROR 101-103: Task ID validation (UI layer for 102, 103; service layer for 101)
#    - All errors handled with re-prompt loops (no exceptions propagated to caller)
#
# 3. User Experience:
#    - Clear field selection menu with numbered options
#    - Current values displayed for context before prompting for new values
#    - Helpful prompts ("press Enter to clear")
#    - Success confirmation message
#    - Seamless return to main menu
#
# 4. Function Reuse:
#    - Reuses prompt_for_task_id() from 002-view-task
#    - Reuses validate_title() from 001-add-task
#    - Reuses validate_description() from 001-add-task
#    - Reuses display_task_details() from 002-view-task (or similar pattern)
#    - Calls new service layer update_task()
#
# 5. Input Handling:
#    - Uses input() for user prompts
#    - Validates using try-except with int() conversion for numeric choices
#    - Re-prompts on validation failures with specific error messages
#    - Strips whitespace from text inputs
#
# 6. Field Selection Logic:
#    - Option 1: Title only → pass new_title, None for description
#    - Option 2: Description only → pass None for title, new_description
#    - Option 3: Both → pass both new values
#    - None values signal "do not change" to service layer
#
# 7. Display Formatting:
#    - Numbered menu format consistent with main menu
#    - Clear line breaks and spacing
#    - Terminal handles text wrapping
#    - No external libraries (no rich, colorama)
#
# 8. Orchestration:
#    - update_task_prompt() is the main entry point from main menu
#    - Coordinates all sub-functions in correct sequence
#    - Handles error cases at each step
#    - Ensures user always returns to main menu
#
# 9. Testability:
#    - Functions can be tested with mock stdin/stdout
#    - pytest capsys fixture can capture output
#    - monkeypatch can provide mock input
#    - Each function has clear, testable behavior
#
# 10. Constants Required (src/constants.py):
#     - ERROR_INVALID_OPTION = "ERROR 104: Invalid option. Please select 1, 2, or 3."
#     - PROMPT_FIELD_SELECTION = "Select update option (1-3): "
#     - PROMPT_NEW_TITLE = "Enter New Task Title: "
#     - PROMPT_NEW_DESCRIPTION = "Enter New Task Description (press Enter to clear): "
#     - MSG_TASK_UPDATED = "Task updated successfully."
