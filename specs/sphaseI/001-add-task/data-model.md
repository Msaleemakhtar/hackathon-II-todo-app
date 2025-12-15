# Data Model: Add Task Feature

**Feature**: Add Task
**Date**: 2025-12-04
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the data structures, relationships, and validation rules for the Add Task feature. All models use Python dataclasses with type hints per Constitution Principle V.

## Entities

### Task

**Description**: Represents a single todo item in the task management system.

**Implementation**: Python `dataclass` with type hints

**Lifecycle**: Created via Add Task feature, persists in memory during application session, lost on termination per Constitution Principle III.

#### Fields

| Field | Type | Required | Constraints | Default | Description |
|-------|------|----------|-------------|---------|-------------|
| `id` | `int` | Yes | Must be positive integer ≥ 1, unique across all tasks | Auto-generated | Unique identifier, sequential starting from 1 |
| `title` | `str` | Yes | 1-200 characters (after whitespace stripping), non-empty | None | Task title, primary description |
| `description` | `str` | No | 0-1000 characters (after whitespace stripping) | `""` | Optional detailed description |
| `completed` | `bool` | Yes | True or False | `False` | Completion status flag |
| `created_at` | `str` | Yes | ISO 8601 format: `YYYY-MM-DDTHH:MM:SS.ffffffZ` | Auto-generated | UTC timestamp of task creation |
| `updated_at` | `str` | Yes | ISO 8601 format: `YYYY-MM-DDTHH:MM:SS.ffffffZ` | Auto-generated | UTC timestamp of last modification (initially same as created_at) |

#### Field Details

**`id` (integer)**
- **Generation Strategy**: Sequential increment starting from 1
- **Algorithm**:
  - If task list empty: `id = 1`
  - Else: `id = max(existing_task_ids) + 1`
- **Uniqueness**: Guaranteed by sequential generation from max existing ID
- **Range**: 1 to sys.maxsize (practical limit: millions of tasks)
- **Immutable**: Once assigned, ID never changes

**`title` (string)**
- **Validation Rules**:
  1. Input is stripped of leading/trailing whitespace before validation
  2. After stripping, length must be 1-200 characters (inclusive)
  3. Cannot be empty or whitespace-only
- **Error Messages**:
  - Empty/whitespace: "ERROR 001: Title is required and must be 1-200 characters."
  - > 200 chars: "ERROR 002: Title is required and must be 1-200 characters."
- **Character Encoding**: Unicode (UTF-8), character count not byte count
- **Internal Whitespace**: Preserved (e.g., "Buy  groceries" keeps double space)
- **Special Characters**: Allowed (no restrictions on character set)

**`description` (string)**
- **Validation Rules**:
  1. Input is stripped of leading/trailing whitespace before validation
  2. After stripping, length must be 0-1000 characters (inclusive)
  3. Empty string allowed (optional field)
- **Error Messages**:
  - > 1000 chars: "ERROR 003: Description cannot exceed 1000 characters."
- **Default Behavior**: If user presses Enter without text, stored as empty string `""`
- **Character Encoding**: Unicode (UTF-8), character count not byte count
- **Internal Whitespace**: Preserved
- **Special Characters**: Allowed (no restrictions on character set)

**`completed` (boolean)**
- **Creation Default**: Always `False` for new tasks
- **Values**: `True` (completed) or `False` (not completed)
- **Modification**: Changed by Mark Complete feature (not Add Task)

**`created_at` (string)**
- **Format**: ISO 8601 with microseconds and UTC timezone
- **Pattern**: `YYYY-MM-DDTHH:MM:SS.ffffffZ`
- **Example**: `2025-12-04T14:32:15.123456Z`
- **Generation**: Captured at moment of task creation using `datetime.now(timezone.utc)`
- **Timezone**: Always UTC (Z suffix indicates Zero UTC offset)
- **Precision**: Microseconds (6 decimal places)
- **Immutable**: Never changes after creation

**`updated_at` (string)**
- **Format**: Same as `created_at` - ISO 8601 with microseconds and UTC timezone
- **Initial Value**: Set to same timestamp as `created_at` during task creation
- **Modification**: Updated by Update Task feature when title/description modified (not Add Task)
- **Timezone**: Always UTC
- **Precision**: Microseconds (6 decimal places)

## Validation Rules

### Title Validation

**Function Signature**: `validate_title(title: str) -> tuple[bool, str | None]`

**Input Processing**:
1. Strip leading and trailing whitespace: `title = title.strip()`
2. Check length constraints on stripped value

**Validation Logic**:
```python
# Pseudocode
if len(title.strip()) == 0:
    return (False, "ERROR 001: Title is required and must be 1-200 characters.")
if len(title.strip()) > MAX_TITLE_LENGTH:  # 200
    return (False, "ERROR 002: Title is required and must be 1-200 characters.")
return (True, None)
```

**Constants**: `MAX_TITLE_LENGTH = 200` (defined in constants.py)

### Description Validation

**Function Signature**: `validate_description(description: str) -> tuple[bool, str | None]`

**Input Processing**:
1. Strip leading and trailing whitespace: `description = description.strip()`
2. Check length constraints on stripped value

**Validation Logic**:
```python
# Pseudocode
if len(description.strip()) > MAX_DESCRIPTION_LENGTH:  # 1000
    return (False, "ERROR 003: Description cannot exceed 1000 characters.")
return (True, None)  # Empty string is valid
```

**Constants**: `MAX_DESCRIPTION_LENGTH = 1000` (defined in constants.py)

## State Transitions

### Task Creation Flow

```
[No Task] → (Add Task Feature) → [Task Created]

Initial State: Task does not exist
Action: User provides title and optional description
Validation: Title and description pass validation rules
Creation: New Task instance created with:
  - id: Generated (max existing ID + 1, or 1 if first)
  - title: Validated user input (stripped)
  - description: Validated user input (stripped, or empty string)
  - completed: False
  - created_at: Current UTC timestamp (ISO 8601)
  - updated_at: Same as created_at
Final State: Task exists in memory with status "not completed"
```

## Data Relationships

### Task → Task List (One-to-Many)

**Relationship**: A task list contains zero or more Task instances

**Implementation**:
- Task list stored as `list[Task]` in memory
- Module-level variable: `_task_storage: list[Task] = []`
- Managed by `task_service.py`

**Cardinality**:
- One task list (global/singleton)
- Zero to N tasks (practical limit: memory capacity)

**Operations**:
- **Add**: Append new Task to list
- **Query**: Linear search through list (O(n))
- **ID Lookup**: `next((t for t in tasks if t.id == target_id), None)`

## Storage Specifications

### In-Memory Storage

**Structure**: Python `list[Task]`

**Location**: Module-level variable in `src/services/task_service.py`

**Persistence**: Ephemeral - lost on application termination per Constitution

**Access Pattern**: Service functions operate on shared list

**Concurrency**: Not required (single-threaded CLI application)

**Capacity**: Limited only by available system memory (practical limit: thousands of tasks)

## Constants

Defined in `src/constants.py`:

```python
# Validation limits
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000

# Error codes and messages
ERROR_TITLE_REQUIRED = "ERROR 001: Title is required and must be 1-200 characters."
ERROR_TITLE_TOO_LONG = "ERROR 002: Title is required and must be 1-200 characters."
ERROR_DESCRIPTION_TOO_LONG = "ERROR 003: Description cannot exceed 1000 characters."

# Success messages
MSG_TASK_ADDED = "Task added successfully."
```

## Example Data

### Valid Task Examples

**Minimal Task (title only)**:
```python
Task(
    id=1,
    title="Buy milk",
    description="",
    completed=False,
    created_at="2025-12-04T10:15:30.123456Z",
    updated_at="2025-12-04T10:15:30.123456Z"
)
```

**Full Task (title + description)**:
```python
Task(
    id=2,
    title="Complete project report",
    description="Include Q4 metrics and team feedback",
    completed=False,
    created_at="2025-12-04T10:20:45.789012Z",
    updated_at="2025-12-04T10:20:45.789012Z"
)
```

**Boundary Cases**:
```python
# Title at maximum length (200 chars)
Task(
    id=3,
    title="A" * 200,
    description="",
    completed=False,
    created_at="2025-12-04T10:25:00.000000Z",
    updated_at="2025-12-04T10:25:00.000000Z"
)

# Description at maximum length (1000 chars)
Task(
    id=4,
    title="Large description task",
    description="B" * 1000,
    completed=False,
    created_at="2025-12-04T10:30:00.000000Z",
    updated_at="2025-12-04T10:30:00.000000Z"
)
```

## Immutability Rules

**Immutable Fields** (never change after creation):
- `id`
- `created_at`

**Mutable Fields** (modified by Update Task feature):
- `title` (via Update Task)
- `description` (via Update Task)
- `updated_at` (auto-updated when title/description change)

**Toggle Fields** (modified by Mark Complete feature):
- `completed` (toggled True ↔ False)
- `updated_at` (auto-updated when completed changes)

## References

- [Feature Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Research Document](./research.md)
- [Constitution](../../.specify/memory/constitution.md) - Task Data Model Specification
