# Quickstart Guide: Add Task Feature

**Feature**: Add Task
**Date**: 2025-12-04
**Phase**: Phase 1 - Design & Contracts

## Overview

This guide helps developers quickly understand and implement the Add Task feature for the Todo App Phase I project. Follow this guide to set up your environment, understand the architecture, and begin implementation.

## Prerequisites

- **Python**: Version 3.13 or newer (required by Constitution)
- **UV**: Package and environment manager ([installation](https://github.com/astral-sh/uv))
- **Git**: For version control and branch management
- **Text Editor/IDE**: VS Code, PyCharm, or similar with Python support

## Quick Setup (5 minutes)

### 1. Clone and Navigate

```bash
# Clone repository (if not already done)
git clone <repo-url>
cd todo-app

# Switch to feature branch
git checkout 001-add-task
```

### 2. Initialize Project with UV

```bash
# Initialize UV project (creates pyproject.toml and virtual environment)
uv init

# Add dependencies
uv add --dev pytest pytest-cov ruff

# Verify Python version
uv run python --version  # Should show 3.13 or newer
```

### 3. Create Project Structure

```bash
# Create source directories
mkdir -p src/models src/services src/ui tests/unit tests/integration

# Create __init__.py files
touch src/__init__.py src/models/__init__.py src/services/__init__.py src/ui/__init__.py
touch tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py
```

### 4. Verify Setup

```bash
# Run tests (should pass even if empty)
uv run pytest

# Check linting configuration
uv run ruff check .

# Check formatting
uv run ruff format --check .
```

## Architecture Overview

### Component Layers

```
┌─────────────────────────────────────┐
│  main.py (Application Entry)       │
│  - Main menu orchestration          │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│  ui/ (User Interface Layer)         │
│  - prompts.py: Input collection     │
│  - messages.py: Message constants   │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│  services/ (Business Logic)         │
│  - task_service.py: Operations      │
│    - create_task()                  │
│    - generate_next_id()             │
│    - store_task()                   │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│  models/ (Data Structures)          │
│  - task.py: Task dataclass          │
└─────────────────────────────────────┘
```

### File Responsibilities

| File | Purpose | Key Functions/Classes |
|------|---------|----------------------|
| `src/constants.py` | Configuration constants | `MAX_TITLE_LENGTH`, error messages |
| `src/models/task.py` | Task data structure | `Task` dataclass |
| `src/services/task_service.py` | Task operations | `create_task()`, `generate_next_id()` |
| `src/ui/prompts.py` | Input collection & validation | `get_task_title()`, `get_task_description()` |
| `src/ui/messages.py` | User-facing messages | Error codes, success messages |
| `src/main.py` | Application entry point | `main()`, menu loop |

## Implementation Steps

### Step 1: Define Constants

**File**: `src/constants.py`

```python
"""Application constants for validation and messaging."""

# Validation limits
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000

# Error codes and messages
ERROR_TITLE_REQUIRED = "ERROR 001: Title is required and must be 1-200 characters."
ERROR_TITLE_TOO_LONG = "ERROR 002: Title is required and must be 1-200 characters."
ERROR_DESCRIPTION_TOO_LONG = "ERROR 003: Description cannot exceed 1000 characters."

# Success messages
MSG_TASK_ADDED = "Task added successfully."

# Prompts
PROMPT_TITLE = "Enter Task Title: "
PROMPT_DESCRIPTION = "Enter Optional Task Description (press Enter to skip): "
```

### Step 2: Create Task Model

**File**: `src/models/task.py`

```python
"""Task data model."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Task:
    """Represents a single todo item.

    Attributes:
        id: Unique integer identifier (sequential, starts at 1)
        title: Task title (1-200 characters, required)
        description: Optional description (0-1000 characters)
        completed: Completion status (default: False)
        created_at: UTC timestamp when task was created (ISO 8601)
        updated_at: UTC timestamp of last modification (ISO 8601)
    """
    id: int
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: str

    @staticmethod
    def generate_timestamp() -> str:
        """Generate current UTC timestamp in ISO 8601 format.

        Returns:
            Timestamp string in format: YYYY-MM-DDTHH:MM:SS.ffffffZ
        """
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
```

### Step 3: Implement Task Service

**File**: `src/services/task_service.py`

```python
"""Task business logic and storage operations."""

from typing import List
from src.models.task import Task

# In-memory task storage (ephemeral)
_task_storage: List[Task] = []


def generate_next_id() -> int:
    """Generate the next sequential task ID.

    Returns:
        1 if task list is empty, otherwise max(existing IDs) + 1
    """
    if not _task_storage:
        return 1
    return max(task.id for task in _task_storage) + 1


def create_task(title: str, description: str) -> Task:
    """Create and store a new task.

    Args:
        title: Task title (already validated)
        description: Task description (already validated, may be empty)

    Returns:
        Newly created Task instance
    """
    timestamp = Task.generate_timestamp()
    task = Task(
        id=generate_next_id(),
        title=title,
        description=description,
        completed=False,
        created_at=timestamp,
        updated_at=timestamp
    )
    _task_storage.append(task)
    return task


def get_all_tasks() -> List[Task]:
    """Retrieve all tasks from storage.

    Returns:
        List of all Task instances (may be empty)
    """
    return _task_storage.copy()
```

### Step 4: Implement UI Layer

**File**: `src/ui/prompts.py`

```python
"""User input prompts and validation."""

from src.constants import (
    MAX_TITLE_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    ERROR_TITLE_REQUIRED,
    ERROR_TITLE_TOO_LONG,
    ERROR_DESCRIPTION_TOO_LONG,
    PROMPT_TITLE,
    PROMPT_DESCRIPTION
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
```

### Step 5: Integrate with Main Menu

**File**: `src/main.py` (Add Task option integration)

```python
"""Application entry point and main menu."""

from src.services.task_service import create_task
from src.ui.prompts import get_task_title, get_task_description
from src.constants import MSG_TASK_ADDED


def handle_add_task() -> None:
    """Handle Add Task user flow.

    Prompts user for title and description, validates inputs,
    creates task, and displays success message.
    """
    title = get_task_title()
    description = get_task_description()
    task = create_task(title, description)
    print(MSG_TASK_ADDED)


def main() -> None:
    """Main application loop."""
    while True:
        print("\n=== Todo App ===")
        print("1. Add Task")
        print("2. View Tasks")  # Future feature
        print("3. Update Task")  # Future feature
        print("4. Delete Task")  # Future feature
        print("5. Mark Complete")  # Future feature
        print("6. Exit")

        choice = input("\nSelect option: ")

        if choice == "1":
            handle_add_task()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Feature not yet implemented or invalid option.")


if __name__ == "__main__":
    main()
```

## Testing Strategy

### Test Pyramid

```
       ┌────────────────┐
       │  Integration   │  (1 test)
       │  Full flow     │
       └────────────────┘
      ┌──────────────────┐
      │   Unit Tests     │  (15-20 tests)
      │  Components      │
      └──────────────────┘
```

### Unit Test Examples

**File**: `tests/unit/test_validation.py`

```python
"""Unit tests for validation functions."""

import pytest
from src.ui.prompts import validate_title, validate_description


def test_validate_title_valid():
    """Valid title should pass validation."""
    is_valid, error = validate_title("Buy groceries")
    assert is_valid is True
    assert error is None


def test_validate_title_empty():
    """Empty title should fail with ERROR 001."""
    is_valid, error = validate_title("")
    assert is_valid is False
    assert "ERROR 001" in error


def test_validate_title_too_long():
    """Title > 200 chars should fail with ERROR 002."""
    long_title = "A" * 201
    is_valid, error = validate_title(long_title)
    assert is_valid is False
    assert "ERROR 002" in error
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_validation.py

# Run with verbose output
uv run pytest -v
```

## Development Workflow

### 1. Red Phase (Write Failing Tests)

```bash
# Create test file
touch tests/unit/test_task_model.py

# Write tests based on spec acceptance criteria
# Run tests - they should FAIL
uv run pytest tests/unit/test_task_model.py
```

### 2. Green Phase (Implement to Pass)

```bash
# Implement feature in source files
# Run tests - they should PASS
uv run pytest tests/unit/test_task_model.py
```

### 3. Refactor Phase (Clean Up)

```bash
# Improve code quality while keeping tests green
uv run ruff format .
uv run ruff check . --fix
uv run pytest  # Ensure still passing
```

## Code Quality Checks

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check . --fix

# Type checking (optional but recommended)
uv run mypy src/ --strict
```

## Common Issues & Solutions

### Issue: Import errors

**Solution**: Ensure `__init__.py` files exist in all package directories

```bash
find src tests -type d -exec touch {}/__init__.py \;
```

### Issue: Tests not discovering

**Solution**: Run pytest from project root

```bash
cd /path/to/todo-app
uv run pytest
```

### Issue: Type hint errors

**Solution**: Use `from __future__ import annotations` for forward references

```python
from __future__ import annotations
from typing import List

def get_tasks() -> List[Task]:  # Now works even if Task defined later
    pass
```

## Key Design Principles

1. **Separation of Concerns**: Keep models, services, and UI separate
2. **Single Responsibility**: Each function does one thing well
3. **Type Safety**: Use type hints for all function signatures
4. **Explicit Over Implicit**: Clear variable names, no magic numbers
5. **Test-Driven**: Write tests first, implement second
6. **Constitution Compliance**: Follow all seven core principles

## Success Criteria Checklist

Before marking feature complete, verify:

- [ ] SC-001: Task creation completes in < 30 seconds
- [ ] SC-002: 100% valid inputs create tasks successfully
- [ ] SC-003: 100% invalid inputs show correct error message
- [ ] SC-004: IDs are sequential starting from 1, no gaps
- [ ] SC-005: Timestamps are valid ISO 8601 UTC format
- [ ] SC-006: Empty descriptions work correctly
- [ ] SC-007: Returns to main menu after task addition

## Next Steps

1. **Review** this quickstart and [data-model.md](./data-model.md)
2. **Implement** following the step-by-step guide above
3. **Test** using TDD approach (Red → Green → Refactor)
4. **Verify** all success criteria met
5. **Commit** with message: "feat: implement Add Task feature"

## References

- [Feature Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Data Model](./data-model.md)
- [Research Document](./research.md)
- [Constitution](../../.specify/memory/constitution.md)

## Support

For questions or issues:
1. Review specification documents in `specs/001-add-task/`
2. Check Constitution for principles and constraints
3. Consult research.md for design decision rationale
