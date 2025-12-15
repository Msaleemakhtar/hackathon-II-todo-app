# Data Model: Rich UI Integration

**Feature**: 006-rich-ui
**Date**: 2025-12-06

## Overview

This feature does **not introduce new entities or modify existing data structures**. It is purely a **UI enhancement** that changes how existing Task entities are displayed to users. The Task data model remains unchanged.

---

## Existing Entities (No Modifications)

### Task (src/models/task.py)

**Status**: ✅ **No Changes Required**

**Definition**:
```python
@dataclass
class Task:
    """Represents a single todo item."""
    id: int                  # Unique identifier (sequential, starts at 1)
    title: str               # Task title (1-200 characters, required)
    description: str         # Optional description (0-1000 characters)
    completed: bool          # Completion status (default: False)
    created_at: str          # UTC timestamp (ISO 8601 format)
    updated_at: str          # UTC timestamp (ISO 8601 format)
```

**Attributes**:
- `id`: Unique integer identifier, auto-generated sequentially starting at 1
- `title`: Task title string, validated to be 1-200 characters (after stripping whitespace)
- `description`: Optional task description, 0-1000 characters (may be empty string)
- `completed`: Boolean flag indicating completion status (default: False)
- `created_at`: ISO 8601 timestamp string (generated via `Task.generate_timestamp()`)
- `updated_at`: ISO 8601 timestamp string (auto-updated on modification)

**Validation Rules** (enforced at input layer, not model layer):
- Title: Required, 1-200 characters after stripping
- Description: Optional, max 1000 characters
- ID: Must be positive integer for update/delete/complete operations

**No changes needed**: The existing Task model fully supports all feature requirements.

---

## UI Display Model (New Concept)

While the Task entity itself is unchanged, this feature introduces a **display transformation** layer in the UI code:

### TaskDisplayRow

**Type**: Transient display object (not persisted, not a separate class)

**Concept**: Each Task is transformed into a display row with 5 columns for table rendering:

| Column | Source | Transformation |
|--------|--------|----------------|
| **ID** | `task.id` | Convert to string: `str(task.id)` |
| **Title** | `task.title` | Truncate at 50 chars if needed: `title[:47] + "..."` if `len(title) > 50` |
| **Status** | `task.completed` | Map boolean to label: `"Completed"` if `True`, `"Pending"` if `False` |
| **Creation Time** | `task.created_at` | Parse ISO 8601 string and format: `datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")` |
| **Last Updated Time** | `task.updated_at` | Parse ISO 8601 string and format: `datetime.fromisoformat(updated_at.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")` |

**Implementation Location**: `src/ui/prompts.py` in the `display_task_list()` function.

**Example Transformation**:
```python
# Original Task object
task = Task(
    id=1,
    title="Implement user authentication system with OAuth 2.0 and JWT tokens",
    description="Set up OAuth flow...",
    completed=False,
    created_at="2025-12-06T14:30:45.123456Z",
    updated_at="2025-12-06T15:00:00.654321Z"
)

# Display row (5 columns for table)
row = [
    "1",                                           # ID (string)
    "Implement user authentication system with...",# Title (truncated)
    "Pending",                                     # Status (label)
    "2025-12-06 14:30:45",                         # Creation Time (formatted)
    "2025-12-06 15:00:00"                          # Last Updated Time (formatted)
]
```

---

## Data Flow

```text
┌─────────────────────┐
│   Task Storage      │
│  (in-memory list)   │
│                     │
│  [Task, Task, ...]  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  display_task_list()│
│   (UI function)     │
│                     │
│  Transforms each    │
│  Task into 5 cols   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Rich Table        │
│                     │
│  │ID│Title│Status  │
│  │1 │Buy  │Pending │
│  │2 │Call │Complete│
└─────────────────────┘
```

**Key Points**:
1. **No data mutation**: The Task objects in storage are never modified by display logic
2. **Read-only transformation**: Display transformations are applied during rendering only
3. **Ephemeral output**: The rich table is rendered to terminal and immediately discarded (no persistence)

---

## State Transitions

**No state transitions introduced**. This feature does not change how Task entities transition between states (pending ↔ completed). State transitions remain controlled by the `toggle_task_completion()` function in `src/services/task_service.py` (unchanged).

---

## Relationships

**No new relationships**. Tasks remain independent entities stored in a flat list structure with no foreign keys or associations.

---

## Data Constraints Summary

| Constraint | Enforced By | Validation Location |
|------------|-------------|---------------------|
| Title length (1-200 chars) | Input validation | `src/ui/prompts.py:validate_title()` |
| Description length (0-1000 chars) | Input validation | `src/ui/prompts.py:validate_description()` |
| Unique ID generation | Service layer | `src/services/task_service.py:add_task()` |
| Timestamp format | Model layer | `src/models/task.py:Task.generate_timestamp()` |
| **Display truncation (50 chars)** | **UI layer (new)** | **`src/ui/prompts.py:display_task_list()`** |

---

## Migration Notes

**No migration required**. This is a UI-only change with no impact on data structures or storage.

---

## Future Considerations

**Potential Future Enhancements** (out of scope for this feature):
- Color-coding by status (green for completed, yellow for pending)
- Sortable columns (click to sort by ID, date, etc.)
- Pagination for large task lists (e.g., 50 tasks per page)
- Customizable column visibility (hide/show columns)

**Data Model Impact of Future Features**: None of the above would require Task model changes. All enhancements would remain UI-layer only.

---

## Summary

✅ **No data model changes required**
✅ **Task entity remains unchanged**
✅ **Display transformations applied in UI layer only**
✅ **No new entities introduced**
✅ **No state transitions modified**

**Readiness**: ✅ Ready to proceed to contracts definition (Phase 1 continuation)
