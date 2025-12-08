"""User input prompts and validation."""

from datetime import datetime

from rich.console import Console
from rich.table import Table

from src.constants import (
    ERROR_DESCRIPTION_TOO_LONG,
    ERROR_INVALID_CONFIRMATION,
    ERROR_INVALID_INPUT,
    ERROR_INVALID_OPTION,
    ERROR_INVALID_TASK_ID,
    ERROR_MARK_COMPLETE_CONFIRMATION,
    ERROR_TITLE_REQUIRED,
    ERROR_TITLE_TOO_LONG,
    MAX_DESCRIPTION_LENGTH,
    MAX_TITLE_LENGTH,
    MSG_DELETION_CANCELED,
    MSG_MARK_COMPLETE_CANCELED,
    MSG_NO_TASKS,
    MSG_TASK_DELETED,
    MSG_TASK_MARKED_COMPLETE,
    MSG_TASK_MARKED_INCOMPLETE,
    MSG_TASK_UPDATED,
    PROMPT_DESCRIPTION,
    PROMPT_FIELD_SELECTION,
    PROMPT_NEW_DESCRIPTION,
    PROMPT_NEW_TITLE,
    PROMPT_TASK_ID,
    PROMPT_TITLE,
)
from src.models.task import Task
from src.services.task_service import (
    delete_task,
    get_task_by_id,
    toggle_task_completion,
    update_task,
)


def validate_title(title: str) -> tuple[bool, str | None]:
    """Validate task title according to specification rules.

    Args:
        title: Raw title input from user

    Returns:
        Tuple of (is_valid, error_message). error_message is None if valid.
    """
    stripped = title.strip()
    if len(stripped) == 0:
        return (False, ERROR_TITLE_REQUIRED)
    if len(stripped) > MAX_TITLE_LENGTH:
        return (False, ERROR_TITLE_TOO_LONG)
    return (True, None)


def validate_description(description: str) -> tuple[bool, str | None]:
    """Validate task description according to specification rules.

    Args:
        description: Raw description input from user

    Returns:
        Tuple of (is_valid, error_message). error_message is None if valid.
    """
    stripped = description.strip()
    if len(stripped) > MAX_DESCRIPTION_LENGTH:
        return (False, ERROR_DESCRIPTION_TOO_LONG)
    return (True, None)


def get_task_title() -> str:
    """Prompt user for task title with validation loop.

    Returns:
        Valid task title (stripped of leading/trailing whitespace)
    """
    while True:
        title = input(PROMPT_TITLE)
        is_valid, error = validate_title(title)
        if is_valid:
            return title.strip()
        print(error)


def get_task_description() -> str:
    """Prompt user for optional task description with validation loop.

    Returns:
        Valid task description (stripped, may be empty string)
    """
    while True:
        description = input(PROMPT_DESCRIPTION)
        is_valid, error = validate_description(description)
        if is_valid:
            return description.strip()
        print(error)


def display_task_list(tasks: list[Task]) -> None:
    """Display a formatted list of all tasks using a rich Table.

    Args:
        tasks: List of Task objects to display (may be empty)
    """
    console = Console()

    if not tasks:
        console.print(MSG_NO_TASKS)
        return

    table = Table(
        show_header=True,
        header_style="bold magenta",
        title="Tasks" if len(tasks) > 1 else f"Task Details - ID {tasks[0].id}",
    )
    table.add_column("ID", style="dim", width=6)
    table.add_column("Title", min_width=15)
    table.add_column("Description", min_width=15)
    table.add_column("Status", justify="center", width=10)
    table.add_column("Created", justify="right", width=19, no_wrap=True)
    table.add_column("Updated", justify="right", width=19, no_wrap=True)

    for task in tasks:
        description = task.description.strip() if task.description.strip() else "(No description)"
        status = "[green]Completed[/green]" if task.completed else "[yellow]Pending[/yellow]"
        created_dt = datetime.fromisoformat(task.created_at.replace("Z", "+00:00"))
        updated_dt = datetime.fromisoformat(task.updated_at.replace("Z", "+00:00"))
        created = created_dt.strftime("%Y-%m-%d %H:%M:%S")
        updated = updated_dt.strftime("%Y-%m-%d %H:%M:%S")

        table.add_row(
            str(task.id),
            task.title,
            description,
            status,
            created,
            updated,
        )

    console.print(table)


def display_task_details(task: Task) -> None:
    """Display detailed information for a single task in a rich Table.

    Args:
        task: The Task object to display in detail
    """
    display_task_list([task])


def prompt_for_task_id() -> int:
    """Prompt user to enter a task ID and validate it's a positive integer.

    Returns:
        Valid positive task ID entered by user

    Raises:
        ValueError: If input is non-numeric (ERROR 102)
        ValueError: If input is zero or negative (ERROR 103)
    """
    user_input = input(PROMPT_TASK_ID)

    # Validate input is numeric
    try:
        task_id = int(user_input)
    except ValueError:
        raise ValueError(ERROR_INVALID_INPUT)

    # Validate input is positive
    if task_id <= 0:
        raise ValueError(ERROR_INVALID_TASK_ID)

    return task_id


def display_field_selection_menu() -> None:
    """Display the field selection menu for choosing which field(s) to update."""
    print("\nSelect fields to update:")
    print("1. Update Title Only")
    print("2. Update Description Only")
    print("3. Update Both Title and Description")


def prompt_for_field_choice() -> int:
    """Prompt user to select which field(s) to update and validate the choice.

    Returns:
        Valid field selection choice (1, 2, or 3)
    """
    while True:
        try:
            choice = int(input(PROMPT_FIELD_SELECTION))
            if 1 <= choice <= 3:
                return choice
            print(ERROR_INVALID_OPTION)
        except ValueError:
            print(ERROR_INVALID_OPTION)


def get_new_task_title(current_title: str) -> str:
    """Prompt user for new task title with validation loop.

    Args:
        current_title: The task's current title (for display context)

    Returns:
        Valid new task title (stripped)
    """
    while True:
        title = input(PROMPT_NEW_TITLE)
        is_valid, error = validate_title(title)
        if is_valid:
            return title.strip()
        print(error)


def get_new_task_description(current_description: str) -> str:
    """Prompt user for new task description with validation loop.

    Args:
        current_description: The task's current description (for display context)

    Returns:
        Valid new task description (stripped, may be empty)
    """
    while True:
        description = input(PROMPT_NEW_DESCRIPTION)
        is_valid, error = validate_description(description)
        if is_valid:
            return description.strip()
        print(error)


def update_task_prompt() -> None:
    """Orchestrate the complete update task workflow with user interaction."""
    try:
        # Step 1: Get and validate task ID
        task_id = prompt_for_task_id()

        # Step 2: Retrieve task (may raise ERROR 101)
        task = get_task_by_id(task_id)
    except ValueError as e:
        print(str(e))
        return  # Return to main menu on error

    # Step 3: Display current values
    print()
    display_task_details(task)

    # Step 4: Get field selection
    display_field_selection_menu()
    choice = prompt_for_field_choice()

    # Step 5: Collect new value(s) based on choice
    new_title = None
    new_description = None

    if choice == 1:  # Title only
        new_title = get_new_task_title(task.title)
    elif choice == 2:  # Description only
        new_description = get_new_task_description(task.description)
    else:  # choice == 3, Both
        new_title = get_new_task_title(task.title)
        new_description = get_new_task_description(task.description)

    # Step 6: Update task
    update_task(task_id, new_title, new_description)

    # Step 7: Display success message
    print(MSG_TASK_UPDATED)


def prompt_for_delete_confirmation(task_title: str) -> bool:
    """Prompt user to confirm task deletion with Y/N response.

    Args:
        task_title: Title of the task to be deleted (for context)

    Returns:
        True if user confirms deletion (Y/y), False if user cancels (N/n)
    """
    prompt = f"Delete task '{task_title}'? (Y/N): "

    while True:
        # Get user input and normalize (strip whitespace, uppercase)
        response = input(prompt).strip().upper()

        # Check for confirmation
        if response == "Y":
            return True

        # Check for cancellation
        if response == "N":
            return False

        # Invalid response - show error and re-prompt
        print(ERROR_INVALID_CONFIRMATION)


def delete_task_prompt() -> None:
    """Orchestrate the complete delete task workflow with user interaction."""
    try:
        # Step 1: Get and validate task ID
        task_id = prompt_for_task_id()

        # Step 2: Retrieve task (validates existence)
        task = get_task_by_id(task_id)

    except ValueError as e:
        # Handle ID validation errors (ERROR 101, 102, 103)
        print(str(e))
        return  # Return to main menu without showing confirmation

    # Step 3: Get user confirmation (shows task title for context)
    confirmed = prompt_for_delete_confirmation(task.title)

    # Step 4: Execute deletion or cancellation
    if confirmed:
        # User confirmed with Y/y
        delete_task(task_id)
        print(MSG_TASK_DELETED)
    else:
        # User canceled with N/n
        print(MSG_DELETION_CANCELED)


def prompt_for_mark_complete_confirmation(task_title: str, current_status: bool) -> bool:
    """Prompt user to confirm task completion status toggle with Y/N response.

    Args:
        task_title: Title of the task to toggle (for context)
        current_status: Current completion status (True = complete, False = incomplete)

    Returns:
        True if user confirms toggle (Y/y), False if user cancels (N/n)
    """
    # Dynamic prompt based on current status
    action = "complete" if not current_status else "incomplete"
    prompt = f"Mark task '{task_title}' as {action}? (Y/N): "

    while True:
        # Get user input and normalize (strip whitespace, uppercase)
        response = input(prompt).strip().upper()

        # Check for confirmation
        if response == "Y":
            return True

        # Check for cancellation
        if response == "N":
            return False

        # Invalid response - show error and re-prompt
        print(ERROR_MARK_COMPLETE_CONFIRMATION)


def mark_complete_prompt() -> None:
    """Orchestrate the complete mark complete/incomplete workflow with user interaction.

    Workflow:
        1. Prompt for task ID and validate
        2. Retrieve task (validates existence)
        3. Display confirmation prompt with dynamic action (complete/incomplete)
        4. On confirmation: toggle status, update timestamp, show success
        5. On cancellation: show cancellation message, no changes
        6. On error: show error message, return to main menu
    """
    try:
        # Step 1: Get and validate task ID
        task_id = prompt_for_task_id()

        # Step 2: Retrieve task (validates existence)
        task = get_task_by_id(task_id)

    except ValueError as e:
        # Handle ID validation errors (ERROR 101, 102, 103)
        print(str(e))
        return  # Return to main menu without showing confirmation

    # Step 3: Get user confirmation (shows task title and action for context)
    confirmed = prompt_for_mark_complete_confirmation(task.title, task.completed)

    # Step 4: Execute toggle or cancellation
    if confirmed:
        # User confirmed with Y/y
        toggle_task_completion(task_id)

        # Determine success message based on NEW status
        # Note: task.completed was toggled inside toggle_task_completion()
        if task.completed:
            print(MSG_TASK_MARKED_COMPLETE)
        else:
            print(MSG_TASK_MARKED_INCOMPLETE)
    else:
        # User canceled with N/n
        print(MSG_MARK_COMPLETE_CANCELED)
