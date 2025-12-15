"""Tests for main module entry point."""

import subprocess
import sys
from pathlib import Path


def test_main_module_entry_point():
    """Test that running the module as __main__ works correctly."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent

    # Run the module with input piped in (select option 7 to exit immediately)
    result = subprocess.run(
        [sys.executable, "-m", "src.main"],
        input="7\n",
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=5,
    )

    # Verify the module executed successfully
    assert result.returncode == 0
    assert "TODO APP" in result.stdout
    assert "ADD TASK" in result.stdout
    assert "EXIT" in result.stdout
    assert "Goodbye!" in result.stdout


def test_main_module_with_add_task_operation():
    """Test running the module and performing an add task operation."""
    project_root = Path(__file__).parent.parent.parent

    # Simulate: option 1 (Add Task), title, description, then option 7 (Exit)
    input_sequence = "1\nTest Task\nTest Description\n7\n"

    result = subprocess.run(
        [sys.executable, "-m", "src.main"],
        input=input_sequence,
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=5,
    )

    assert result.returncode == 0
    assert "Enter Task Title:" in result.stdout
    assert "Enter Optional Task Description" in result.stdout
    assert "Task added successfully." in result.stdout
    assert "Goodbye!" in result.stdout
