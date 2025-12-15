# Data Model: View Task Feature

**Feature**: 002-view-task
**Date**: 2025-12-06
**Status**: Complete

## Overview

The View Task feature is a **read-only** feature that displays existing task data. It does not introduce new entities or modify the existing Task data model. This document describes the entities used by this feature and their relationships.

---

## Entities

### Task (Existing - No Changes)

**Source**: `src/models/task.py` (defined in feature 001-add-task)

**Description**: Represents a single todo item with metadata for tracking creation and updates.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `int` | Unique, auto-generated, > 0 | Unique identifier for the task |
| `title` | `str` | Required, 1-200 characters | Short description of the task |
| `description` | `str` | Optional, 0-1000 characters | Detailed description (can be empty) |
| `completed` | `bool` | Default: False | Completion status flag |
| `created_at` | `str` | ISO 8601 timestamp, auto-generated | UTC timestamp when task was created |
| `updated_at` | `str` | ISO 8601 timestamp, auto-updated | UTC timestamp when task was last modified |

**Implementation**:
```python
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class Task:
    id: int
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: str
```

**Validation Rules** (defined in 001-add-task, enforced at creation):
- `title`: Cannot be empty or whitespace-only, must be 1-200 characters after stripping
- `description`: Optional, maximum 1000 characters if provided
- `id`: Auto-generated, starts at 1, increments for each new task
- Timestamps: Auto-generated in ISO 8601 format (e.g., "2025-12-06T10:00:00.000000Z")

**State Transitions**: Not applicable for this feature (read-only)

---

## Entity Relationships

```text
TaskService
    │
    ├── manages → [Task, Task, Task, ...]  (in-memory list)
    │
    └── provides read access to →
            ├── get_all_tasks() → list[Task]
            └── get_task_by_id(id: int) → Task
```

**Notes**:
- TaskService maintains the authoritative in-memory list of tasks
- View Task feature only reads from this list, never modifies it
- No new relationships or entities are introduced

---

## Display Transformations

While the data model remains unchanged, the View Task feature transforms Task entities for display purposes:

### List View Transformation

**Input**: `list[Task]`
**Output**: Formatted console text

**Transformation Logic**:
```python
for task in tasks:
    completion_indicator = "[X]" if task.completed else "[ ]"
    print(f"{task.id}. {completion_indicator} {task.title}")
```

**Example Output**:
```
1. [ ] Buy groceries
2. [X] Complete project report
3. [ ] Call dentist

Total: 3 tasks
```

### Detail View Transformation

**Input**: `Task`
**Output**: Formatted console text with all fields labeled

**Transformation Logic**:
```python
print(f"ID: {task.id}")
print(f"Title: {task.title}")
print(f"Description: {task.description if task.description.strip() else '(No description)'}")
print(f"Completed: {'Yes' if task.completed else 'No'}")
print(f"Created At: {task.created_at}")
print(f"Updated At: {task.updated_at}")
```

**Example Output**:
```
ID: 2
Title: Buy groceries
Description: Milk, eggs, bread
Completed: No
Created At: 2025-12-06T10:00:00.000000Z
Updated At: 2025-12-06T10:00:00.000000Z
```

### Empty Description Handling

**Rule**: If `task.description` is empty or whitespace-only, display `"(No description)"` instead.

**Rationale**: Provides clear visual feedback that the field is intentionally empty (per FR-016).

---

## Data Access Patterns

### Pattern 1: Retrieve All Tasks

**Operation**: List View
**Service Method**: `TaskService.get_all_tasks() -> list[Task]`
**Returns**: Complete list of all tasks in insertion order
**Throws**: None (returns empty list if no tasks exist)

**Usage**:
```python
tasks = task_service.get_all_tasks()
if not tasks:
    print("No tasks found.")
else:
    display_task_list(tasks)
```

### Pattern 2: Retrieve Task by ID

**Operation**: Detail View
**Service Method**: `TaskService.get_task_by_id(task_id: int) -> Task`
**Returns**: Single Task object matching the ID
**Throws**:
- `ValueError("ERROR 103: Task ID must be a positive number.")` if task_id <= 0
- `ValueError(f"ERROR 101: Task with ID {task_id} not found.")` if task doesn't exist

**Usage**:
```python
try:
    task = task_service.get_task_by_id(task_id)
    display_task_details(task)
except ValueError as e:
    print(str(e))
```

---

## Data Integrity Constraints

Since this is a read-only feature, it relies on data integrity constraints enforced by the Add Task feature:

| Constraint | Enforcement Point | Verification |
|------------|------------------|--------------|
| Task IDs are unique | TaskService.add_task() | View feature assumes IDs are unique |
| Task IDs start at 1 and increment | TaskService.add_task() | View feature displays IDs as-is |
| Titles are 1-200 characters | Add Task validation | View feature displays without re-validation |
| Descriptions are 0-1000 characters | Add Task validation | View feature displays without re-validation |
| Timestamps are valid ISO 8601 | Add Task auto-generation | View feature displays as-is |

**View Feature Validation** (only for user input):
- Task ID input must be numeric (validated before calling service)
- Task ID input must be positive (validated in service method)
- Task ID must exist (validated in service method)

---

## Pagination Model

**Trigger**: List view with > 20 tasks
**Behavior**: Pause after every 20th task and wait for Enter keypress

**Implementation Detail**:
```python
for i, task in enumerate(tasks, start=1):
    # Display task
    if i % 20 == 0 and i < len(tasks):
        input("Press Enter to continue...")
```

**Notes**:
- Counter is 1-indexed (start=1) for natural counting
- Prompt only appears if there are more tasks to display (i < len(tasks))
- No prompt after the final batch of tasks

---

## Error States

The View Task feature handles these error states:

| Error Code | Condition | Data State | User Action |
|------------|-----------|------------|-------------|
| None | Empty task list | `tasks = []` | Display "No tasks found." |
| ERROR 102 | Non-numeric input | N/A (input validation) | Re-prompt for numeric input |
| ERROR 103 | Zero or negative ID | N/A (input validation) | Re-prompt for positive ID |
| ERROR 101 | Task ID not found | Task with given ID doesn't exist | Return to main menu |

---

## Assumptions

1. **Task Order**: Tasks are displayed in the order they appear in the `TaskService.tasks` list (assumed to be insertion order, effectively sorted by ID)
2. **Concurrent Access**: Not applicable (single-user CLI application, no concurrent access)
3. **Data Freshness**: Data is always fresh (in-memory, no caching needed)
4. **Task Persistence**: Tasks exist only during runtime; no persistence layer (per constitution)
5. **Character Encoding**: All strings are UTF-8, terminal supports Unicode (per spec assumption)

---

## Future Considerations

While out of scope for this feature, the data model supports these future enhancements:

- **Filtering**: `completed` field can be used to filter tasks by status
- **Sorting**: Timestamp fields can be used for chronological sorting
- **Search**: `title` and `description` fields can be searched
- **Statistics**: `completed` field can be used to calculate completion rate

These enhancements would require new service methods but no changes to the Task data model itself.

---

**Data Model Status**: ✅ Complete - No changes to existing Task entity required
