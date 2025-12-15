"""Application entry point and main menu."""

from pyfiglet import figlet_format
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.constants import MSG_TASK_ADDED
from src.services.task_service import create_task, get_all_tasks, get_task_by_id
from src.ui.prompts import (
    delete_task_prompt,
    display_task_details,
    display_task_list,
    get_task_description,
    get_task_title,
    mark_complete_prompt,
    prompt_for_task_id,
    update_task_prompt,
)


def handle_add_task() -> None:
    """Handle Add Task user flow.

    Prompts user for title and description, validates inputs,
    creates task, and displays success message.
    """
    title = get_task_title()
    description = get_task_description()
    create_task(title, description)
    print(MSG_TASK_ADDED)


def handle_view_tasks() -> None:
    """Handle View Tasks user flow.

    Retrieves all tasks and displays them in a formatted list
    with completion indicators and pagination.
    """
    tasks = get_all_tasks()
    display_task_list(tasks)


def handle_view_task_details() -> None:
    """Handle View Task Details user flow.

    Prompts user for task ID, validates input, retrieves task,
    and displays detailed information. Handles errors gracefully.
    """
    try:
        task_id = prompt_for_task_id()
        task = get_task_by_id(task_id)
        display_task_details(task)
    except ValueError as e:
        print(e)


def handle_mark_complete() -> None:
    """Handle Mark Complete user flow.

    Prompts user for task ID, displays confirmation with dynamic action
    (complete/incomplete), toggles task status on confirmation, and updates
    timestamp. Returns to main menu after completion or cancellation.
    """
    mark_complete_prompt()


def main() -> None:
    """Main application loop."""
    console = Console()
    while True:
        # Create large ASCII art title
        title_art = figlet_format("TODO APP", font="standard")
        title_text = Text(title_art, style="bold cyan", justify="center")

        console.print(
            Panel(
                title_text,
                title="[bold green]✨ WELCOME TO TODO APP ✨[/bold green]",
                subtitle="[italic]Manage your tasks efficiently[/italic]",
                border_style="cyan",
                padding=(1, 2),
            )
        )
        console.print("\n")
        console.print("  [bold green]1.  ADD TASK[/bold green]")
        console.print("  [bold yellow]2.  VIEW TASKS[/bold yellow]")
        console.print("  [bold blue]3.  VIEW TASK DETAILS[/bold blue]")
        console.print("  [bold magenta]4.  UPDATE TASK[/bold magenta]")
        console.print("  [bold red]5.  DELETE TASK[/bold red]")
        console.print("  [bold cyan]6.  MARK COMPLETE[/bold cyan]")
        console.print("  [bold white]7.  EXIT[/bold white]")

        choice = input("\nSelect option: ")

        if choice == "1":
            handle_add_task()
        elif choice == "2":
            handle_view_tasks()
        elif choice == "3":
            handle_view_task_details()
        elif choice == "4":
            update_task_prompt()
        elif choice == "5":
            delete_task_prompt()
        elif choice == "6":
            handle_mark_complete()
        elif choice == "7":
            console.print("Goodbye!")
            break
        else:
            console.print("[bold red]Invalid option. Please select 1-7.[/bold red]")


if __name__ == "__main__":
    main()
