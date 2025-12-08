# Todo App

A feature-rich command-line todo application built with Python 3.13 following Test-Driven Development principles and Spec-Driven Development methodology.

## Features

- ✅ **Add Task**: Create tasks with title (1-200 chars) and optional description (0-1000 chars)
- ✅ **View Tasks**: Display all tasks in a formatted list with completion indicators
- ✅ **View Task Details**: View complete details of a specific task including description and timestamps
- ✅ **Update Task**: Modify existing task title and description
- ✅ **Delete Task**: Remove tasks from storage with confirmation
- ✅ **Mark Complete**: Toggle task completion status with dynamic confirmation prompts
- ✅ **Rich UI Integration**: Enhanced console interface with formatted tables and visual feedback (in development)
- ✅ **Input Validation**: Comprehensive validation with clear error messages
- ✅ **Sequential IDs**: Auto-generated sequential task IDs starting from 1
- ✅ **UTC Timestamps**: ISO 8601 format timestamps for created_at and updated_at
- ✅ **In-Memory Storage**: Ephemeral task storage (cleared on app exit)

## Requirements

- **Python**: 3.13 or newer
- **UV**: Package and environment manager ([installation](https://github.com/astral-sh/uv))

## Quick Start

### 1. Setup

```bash
# Clone repository
git clone https://github.com/Msaleemakhtar/Phase-I-Hackathon-Todo-App.git
cd Phase-I-Hackathon-Todo-App

# Install dependencies
uv sync

# Verify installation
uv run python --version  # Should show Python 3.13+
```

### 2. Run Application

```bash
uv run python -m src.main
```

### 3. Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run with verbose output
uv run pytest -v
```

### 4. Code Quality

```bash
# Check linting
uv run ruff check .

# Format code
uv run ruff format .
```

## Usage

When you run the application, you'll see a main menu:

```
✨ WELCOME TO TODO APP ✨
┌─────────────────────────────────────┐
│          TODO APP                   │
│     (ASCII art banner)              │
└─────────────────────────────────────┘
Manage your tasks efficiently

  1.  ADD TASK
  2.  VIEW TASKS
  3.  VIEW TASK DETAILS
  4.  UPDATE TASK
  5.  DELETE TASK
  6.  MARK COMPLETE
  7.  EXIT

Select option:
```

### Available Operations

#### 1. Add Task
Create a new task with title and optional description.
- Enter a task title (1-200 characters required)
- Enter an optional description (0-1000 characters, or press Enter to skip)
- Task is created with auto-generated ID and timestamps

#### 2. View Tasks
Display all tasks in a formatted list showing ID, title, and completion status.
- Shows completion indicators: `[ ]` for incomplete, `[X]` for complete
- Displays task count summary
- Shows "No tasks found" if task list is empty

#### 3. View Task Details
View complete details of a specific task.
- Prompts for task ID
- Displays all fields: ID, title, description, completion status, timestamps
- Shows error message for invalid or non-existent task IDs

#### 4. Update Task
Modify an existing task's title and/or description.
- Prompts for task ID
- Shows current values
- Enter new values or press Enter to keep current values
- Updates the `updated_at` timestamp

#### 5. Delete Task
Remove a task from storage.
- Prompts for task ID
- Shows task details and asks for confirmation
- Permanently deletes task on confirmation
- IDs are not reused after deletion

#### 6. Mark Complete
Toggle a task's completion status.
- Prompts for task ID
- Shows dynamic confirmation message (mark complete/incomplete)
- Toggles completion status on confirmation
- Updates the `updated_at` timestamp

## Validation Rules

### Title
- **Required**: Must be 1-200 characters after whitespace stripping
- **Empty/whitespace-only**: `ERROR 001: Title is required and must be 1-200 characters.`
- **Too long (>200 chars)**: `ERROR 002: Title is required and must be 1-200 characters.`

### Description
- **Optional**: Can be empty (press Enter to skip)
- **Max length**: 1000 characters after whitespace stripping
- **Too long (>1000 chars)**: `ERROR 003: Description cannot exceed 1000 characters.`

## Project Structure

```
todo-app/
├── src/
│   ├── __init__.py
│   ├── constants.py           # Validation limits and messages
│   ├── main.py                # Application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py            # Task dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py    # Business logic and storage
│   └── ui/
│       ├── __init__.py
│       └── prompts.py         # Input validation and prompts
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_task_model.py
│   │   ├── test_validation.py
│   │   └── test_task_service.py
│   └── integration/
│       ├── __init__.py
│       └── test_add_task_flow.py
├── specs/                     # Feature specifications
├── history/                   # Prompt history and ADRs
├── .gitignore
├── pyproject.toml             # Project configuration
├── uv.lock
└── README.md                  # This file
```

## Test Coverage

- **Comprehensive test suite** across unit and integration tests
- **100% coverage** on all core business logic:
  - `src/constants.py`: 100%
  - `src/models/task.py`: 100%
  - `src/services/task_service.py`: 100%
  - `src/ui/prompts.py`: 100%
  - `src/main.py`: High coverage on all menu handlers
- **Test Types**:
  - Unit tests for models, services, and validation logic
  - Integration tests for complete user workflows
  - Edge case and error handling tests

## Development

### Technology Stack

- **Language**: Python 3.13
- **Package Manager**: UV
- **Testing**: pytest, pytest-cov
- **Linting/Formatting**: ruff
- **UI Enhancement**: rich (formatted tables, panels, styling), pyfiglet (ASCII art)
- **Type Hints**: Full type annotation coverage

### Design Principles

- **TDD**: Test-Driven Development (tests written before implementation)
- **Separation of Concerns**: Clear boundaries between models, services, and UI
- **Type Safety**: Type hints on all function signatures
- **100% Core Logic Coverage**: Comprehensive test coverage
- **PEP 8 Compliance**: Code formatted per Python standards

### Task Data Model

Each task has the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Unique sequential identifier (starts at 1) |
| `title` | `str` | Task title (1-200 characters) |
| `description` | `str` | Optional description (0-1000 characters) |
| `completed` | `bool` | Completion status (default: False) |
| `created_at` | `str` | UTC timestamp when task was created (ISO 8601) |
| `updated_at` | `str` | UTC timestamp of last modification (ISO 8601) |

## Success Criteria

All core success criteria verified across implemented features:

- ✅ **Performance**: All operations complete in < 30 seconds
- ✅ **Reliability**: 100% of valid inputs succeed, 100% of invalid inputs show clear errors
- ✅ **Data Integrity**: Sequential IDs with no gaps or duplicates, proper timestamp handling
- ✅ **User Experience**: Clear confirmation messages, graceful error handling, intuitive navigation
- ✅ **Test Coverage**: 100% coverage on core business logic with comprehensive test suites
- ✅ **Code Quality**: PEP 8 compliance, full type annotations, Google-style docstrings

## Constitutional Compliance

This project adheres to strict development principles:

- ✅ **Python 3.13+** exclusively
- ✅ **Minimal dependencies** (pytest for testing, rich/pyfiglet for UI enhancement)
- ✅ **In-memory storage** (Python list of dataclass instances)
- ✅ **No file I/O, database, or external persistence**
- ✅ **UV for dependency management**
- ✅ **100% test coverage** on core business logic
- ✅ **Type hints** on all function signatures
- ✅ **Google-style docstrings**
- ✅ **Ruff for linting and formatting**
- ✅ **Spec-Driven Development** methodology with documented features

## Implementation History

All features developed following TDD and Spec-Driven Development:

- ✅ **001-add-task**: Create tasks with validation ([spec](specs/001-add-task/spec.md))
- ✅ **002-view-task**: List and view task details ([spec](specs/002-view-task/spec.md))
- ✅ **003-update-task**: Modify existing tasks ([spec](specs/003-update-task/spec.md))
- ✅ **004-delete-task**: Remove tasks with confirmation ([spec](specs/004-delete-task/spec.md))
- ✅ **005-mark-complete**: Toggle completion status ([spec](specs/005-mark-complete/spec.md))
- 🚧 **006-rich-ui**: Enhanced console interface ([spec](specs/006-rich-ui/spec.md)) - In Development

## Contributing

This is a learning project following structured development practices. See the [constitution](.specify/memory/constitution.md) for development guidelines.

## License

This project is part of a structured development learning exercise.

## Support

For issues or questions, refer to:

- **Feature Specifications**: See `specs/` directory for all feature documentation
- **Constitution & Principles**: `.specify/memory/constitution.md`
- **Prompt History**: `history/prompts/` for development decision records
- **Architecture Decisions**: `history/adr/` for significant technical choices
- **GitHub Issues**: [Report a bug](https://github.com/Msaleemakhtar/Phase-I-Hackathon-Todo-App/issues)

## Development Workflow

This project follows Spec-Driven Development (SDD):

1. **Specification**: Each feature starts with a detailed spec in `specs/<feature-name>/spec.md`
2. **Planning**: Architecture and implementation plan documented in `specs/<feature-name>/plan.md`
3. **Tasks**: Breakdown into testable tasks in `specs/<feature-name>/tasks.md`
4. **Implementation**: TDD approach with tests written before code
5. **Documentation**: Prompt History Records (PHRs) and ADRs capture decisions

---

**Built with Python 3.13 | Powered by UV | Enhanced with Rich UI | 100% Test Coverage**
