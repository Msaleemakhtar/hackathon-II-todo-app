# Data Model: Mark Complete Feature

**Feature**: Mark Complete
**Branch**: 005-mark-complete
**Date**: 2025-12-06

## Overview

The Mark Complete feature does NOT introduce new data entities. It operates exclusively on the existing **Task** entity, modifying two fields: `completed` (toggle) and `updated_at` (timestamp update). This document defines the state transitions, validation rules, and data flow for the completion status toggle operation.

---

## Entities

### Task (Existing - No Schema Changes)

The Task dataclass is defined in `src/models/task.py` and requires **no modifications** for this feature.

**Entity Definition**:

```python
@dataclass
class Task:
    id: int                # Unique identifier (sequential, immutable)
    title: str             # Task title (1-200 chars)
    description: str       # Task description (0-1000 chars)
    completed: bool        # ← MODIFIED BY THIS FEATURE
    created_at: str        # ISO 8601 timestamp (immutable)
    updated_at: str        # ← MODIFIED BY THIS FEATURE
```

**Field Interaction Map**:

| Field | Create | View | Update | Delete | Mark Complete |
|-------|--------|------|--------|--------|---------------|
| `id` | ✅ Set | ✅ Read | ✅ Read | ✅ Read | ✅ Read |
| `title` | ✅ Set | ✅ Read | ✅ Modify | ✅ Read | ✅ Read |
| `description` | ✅ Set | ✅ Read | ✅ Modify | ✅ Read | ✅ Read |
| `completed` | ✅ Set (False) | ✅ Read | - | - | ✅ **Toggle** |
| `created_at` | ✅ Set | ✅ Read | - | - | - |
| `updated_at` | ✅ Set | ✅ Read | ✅ Set | - | ✅ **Set** |

**Key Observations**:
- Mark Complete is the ONLY feature that modifies `completed` field
- Update feature modifies title/description, Mark Complete modifies completed status (orthogonal operations)
- Both Update and Mark Complete set `updated_at` (following same pattern)
- `created_at` is immutable across ALL features (only set on creation)

---

## State Transitions

### Completion Status State Machine

The `completed` field follows a simple binary state machine:

```
┌─────────────┐                             ┌─────────────┐
│  Incomplete │  ────toggle_completion───▶  │  Complete   │
│ (False)     │                             │ (True)      │
└─────────────┘  ◀────toggle_completion───  └─────────────┘
```

**State Definitions**:

| State | Value | Meaning | Visual Indicator |
|-------|-------|---------|------------------|
| Incomplete | `completed=False` | Task not yet finished | `[ ]` (View Tasks) |
| Complete | `completed=True` | Task marked as done | `[X]` (View Tasks) |

**Transition Rules**:

1. **Incomplete → Complete**
   - **Trigger**: User confirms toggle on incomplete task
   - **Actions**:
     - Set `task.completed = True`
     - Set `task.updated_at = Task.generate_timestamp()`
   - **Validation**: Task must exist (ERROR 201 if not found)

2. **Complete → Incomplete**
   - **Trigger**: User confirms toggle on complete task
   - **Actions**:
     - Set `task.completed = False`
     - Set `task.updated_at = Task.generate_timestamp()`
   - **Validation**: Task must exist (ERROR 201 if not found)

**Invariants** (must hold before and after transition):
- `id` remains unchanged
- `title` remains unchanged
- `description` remains unchanged
- `created_at` remains unchanged
- `updated_at` is strictly later than previous value (monotonically increasing)

---

## Data Flow

### Toggle Completion Flow

```
┌────────────┐
│ User Input │  Enter task ID
└──────┬─────┘
       │
       ▼
┌──────────────────┐
│ Validation Layer │  1. Numeric? → ERROR 202 if not
│ (UI Layer)       │  2. Positive? → ERROR 203 if not
└──────┬───────────┘
       │ valid task_id (int)
       ▼
┌──────────────────┐
│ Service Layer    │  3. Exists? → ERROR 201 if not
│ get_task_by_id() │  4. Retrieve Task instance
└──────┬───────────┘
       │ task (Task)
       ▼
┌──────────────────┐
│ UI Confirmation  │  5. Display: "Mark task '{title}' as {action}? (Y/N):"
│ Prompt           │     action = "complete" if task.completed==False else "incomplete"
└──────┬───────────┘
       │
       ├───────────────┐
       │               │
       ▼               ▼
   ┌───────┐     ┌──────────┐
   │ Y/y   │     │ N/n      │
   └───┬───┘     └────┬─────┘
       │              │
       │              ▼
       │         ┌──────────────┐
       │         │ Cancel Flow  │  Print "Operation canceled."
       │         │ Return       │  Return to main menu
       │         └──────────────┘
       │
       ▼
┌──────────────────────────┐
│ Service Layer            │  6. task.completed = not task.completed
│ toggle_task_completion() │  7. task.updated_at = Task.generate_timestamp()
└──────┬───────────────────┘
       │ updated_task (Task)
       ▼
┌──────────────────┐
│ UI Success       │  8. Print "Task marked as {status}."
│ Message          │     status = "complete" if task.completed else "incomplete"
└──────────────────┘
       │
       ▼
┌──────────────┐
│ Main Menu    │
└──────────────┘
```

---

## Validation Rules

### Input Validation

| Field | Validation Rule | Error Code | Error Message | Retry Behavior |
|-------|----------------|------------|---------------|----------------|
| **Task ID (Input)** | Must be numeric | ERROR 202 | "Invalid input. Please enter a numeric task ID." | Re-prompt indefinitely |
| **Task ID (Value)** | Must be positive (> 0) | ERROR 203 | "Task ID must be a positive number." | Re-prompt indefinitely |
| **Task Existence** | Must exist in `_task_storage` | ERROR 201 | "Task with ID {task_id} not found." | Return to main menu (no retry) |
| **Confirmation** | Must be Y/y/N/n | ERROR 205 | "Invalid input. Please enter Y or N." | Re-prompt indefinitely |

### Business Logic Validation

| Rule | Description | Enforcement Point |
|------|-------------|-------------------|
| **Toggle validity** | No restrictions - tasks can be toggled unlimited times | None (always allowed) |
| **Idempotency** | Multiple toggles result in alternating states (not idempotent by design) | Service layer documents behavior |
| **Timestamp monotonicity** | `updated_at` must be strictly increasing | Implicitly enforced by `Task.generate_timestamp()` |

---

## Data Relationships

### Storage Model

```
In-Memory Storage (_task_storage: list[Task])
│
├── Task(id=1, completed=False, updated_at="2025-12-06T10:00:00.000000Z")
├── Task(id=2, completed=True,  updated_at="2025-12-06T11:30:00.000000Z")  ← Can toggle to False
├── Task(id=3, completed=False, updated_at="2025-12-06T09:15:00.000000Z")  ← Can toggle to True
└── Task(id=5, completed=True,  updated_at="2025-12-06T12:45:00.000000Z")
```

**Storage Interactions**:
- **Read**: `get_task_by_id(task_id)` - Retrieves Task instance by ID (validates existence)
- **Write**: In-place modification - `task.completed = not task.completed` (no list operations)
- **No Deletion**: Toggle operation never removes tasks from storage
- **No Creation**: Toggle operation never adds tasks to storage
- **Order Preservation**: List order unchanged by toggle operation

---

## Error Handling Strategy

### Error Propagation Model

```
┌───────────────┐
│ UI Layer      │  Input validation errors (202, 203, 205)
│ (prompts.py)  │  ↓ Handled locally with retry loops
└───────────────┘
       │
       ▼
┌───────────────┐
│ Service Layer │  Business validation error (201)
│ (task_service.py) │  ↓ Raises ValueError with error message
└───────────────┘
       │
       ▼
┌───────────────┐
│ UI Layer      │  Catches ValueError, prints message, returns to main menu
│ (prompts.py)  │
└───────────────┘
```

**Error Handling Matrix**:

| Error Type | Layer | Handling Strategy | User Experience |
|------------|-------|-------------------|-----------------|
| Non-numeric ID | UI | Retry loop | Re-prompt for task ID |
| Zero/negative ID | UI | Retry loop | Re-prompt for task ID |
| Task not found | Service → UI | Catch, print, return | Return to main menu |
| Invalid confirmation | UI | Retry loop | Re-prompt for Y/N |

---

## Timestamp Management

### Timestamp Update Strategy

**Pattern**: Follow existing `update_task()` pattern from Update Task feature.

**Implementation**:

```python
# Before toggle
task.updated_at = "2025-12-06T10:00:00.123456Z"

# During toggle
task.completed = not task.completed
task.updated_at = Task.generate_timestamp()  # ← Generates new timestamp

# After toggle
task.updated_at = "2025-12-06T10:05:32.789012Z"  # ← New value
```

**Timestamp Format**: ISO 8601 with microseconds and UTC timezone
- Format: `YYYY-MM-DDTHH:MM:SS.ffffffZ`
- Example: `2025-12-06T14:23:45.678901Z`
- Timezone: Always UTC (Z suffix)

**Guarantees**:
1. Every toggle updates `updated_at` (even if toggled back immediately)
2. `updated_at` reflects toggle operation time (not task creation time)
3. `created_at` is NEVER modified (immutable audit trail)

---

## Concurrency Considerations

**Current Scope**: Single-threaded CLI application (Phase I)

**Analysis**:
- ✅ No race conditions (single user, single process)
- ✅ No distributed state (in-memory only)
- ✅ No file locking needed (no persistence)
- ✅ Timestamp collisions impossible (microsecond precision, sequential execution)

**Future Considerations** (Phase II+):
- If multi-user support added: Implement optimistic locking with version field
- If persistence added: Consider database transaction isolation levels
- If async added: Use threading locks around `_task_storage` modifications

---

## Data Integrity Constraints

### Pre-Toggle Invariants

Must be true BEFORE `toggle_task_completion()` is called:

```python
assert task.id > 0                        # Valid ID
assert 1 <= len(task.title) <= 200        # Valid title
assert len(task.description) <= 1000      # Valid description
assert isinstance(task.completed, bool)   # Boolean status
assert task.created_at <= task.updated_at # Timestamps ordered
```

### Post-Toggle Invariants

Must be true AFTER `toggle_task_completion()` completes:

```python
assert task.completed == (not original_completed)  # Status toggled
assert task.updated_at > original_updated_at       # Timestamp updated
assert task.created_at == original_created_at      # Created unchanged
assert task.id == original_id                      # ID unchanged
assert task.title == original_title                # Title unchanged
assert task.description == original_description    # Description unchanged
```

---

## Edge Cases

### Data Edge Cases

| Edge Case | Behavior | Rationale |
|-----------|----------|-----------|
| **Empty task list** | ERROR 201 (task not found) | Consistent with other features |
| **Rapid toggle (5x in a row)** | Each toggle updates timestamp, alternates status | Allowed; no throttling |
| **Toggle immediately after creation** | Allowed; timestamp updates normally | No cooldown period |
| **Toggle task ID 0** | ERROR 203 (must be positive) | Validation rejects at UI layer |
| **Toggle task ID -5** | ERROR 203 (must be positive) | Validation rejects at UI layer |
| **Toggle task ID 99999** | ERROR 201 (not found) | Service layer validates existence |
| **Whitespace in confirmation** | Stripped, then validated | " Y " → "Y" (accepted) |

### Timestamp Edge Cases

| Edge Case | Handling |
|-----------|----------|
| System clock reset backwards | Timestamp uses `datetime.now()`, accepts any value (no monotonicity check across app restarts) |
| Microsecond precision overflow | Python `datetime` handles this natively (no overflow risk) |
| Timezone change | Timestamps always UTC (immune to local timezone changes) |

---

## Testing Implications

### Unit Test Requirements

**Service Layer Tests** (`test_task_service.py`):

```python
def test_toggle_incomplete_to_complete():
    """Verify False → True transition."""

def test_toggle_complete_to_incomplete():
    """Verify True → False transition."""

def test_toggle_updates_timestamp():
    """Verify updated_at changes on toggle."""

def test_toggle_preserves_created_at():
    """Verify created_at remains unchanged."""

def test_toggle_preserves_other_fields():
    """Verify id, title, description unchanged."""

def test_toggle_nonexistent_task():
    """Verify ERROR 201 on missing task."""

def test_toggle_invalid_task_id():
    """Verify ERROR 203 on zero/negative ID."""
```

**Integration Test Requirements** (`test_mark_complete_flow.py`):

```python
def test_full_toggle_flow_with_confirmation():
    """End-to-end: ID input → confirmation → toggle → success message."""

def test_full_toggle_flow_with_cancellation():
    """End-to-end: ID input → confirmation → cancel → no changes."""

def test_multiple_consecutive_toggles():
    """Verify toggle alternates status correctly across 5 toggles."""

def test_invalid_id_error_handling():
    """Verify ERROR 202/203 handling and return to menu."""

def test_invalid_confirmation_retry():
    """Verify ERROR 205 re-prompts until valid Y/N."""
```

---

## Summary

**Data Model Characteristics**:
- ✅ **Zero new entities** - Operates on existing Task dataclass
- ✅ **Two field modifications** - `completed` (toggle) + `updated_at` (set)
- ✅ **Simple state machine** - Binary toggle between False ↔ True
- ✅ **Consistent patterns** - Follows Update Task timestamp handling
- ✅ **Strong invariants** - Five fields remain unchanged during toggle
- ✅ **Comprehensive validation** - Four error codes cover all failure modes

**Key Design Principles**:
1. **Immutability**: `id`, `title`, `description`, `created_at` never modified
2. **Auditability**: `updated_at` provides timestamp trail of all toggles
3. **Simplicity**: No complex state (just boolean flip)
4. **Consistency**: Mirrors existing feature patterns (Update, Delete)

**Status**: ✅ Data model complete - Ready for contracts generation (Phase 1 continued)
