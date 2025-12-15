# UI Function Contracts

**Feature**: 006-rich-ui
**Date**: 2025-12-06
**Module**: `src/ui/prompts.py`

This document defines the function signatures and contracts for UI functions modified or added in this feature.

---

## Modified Functions

### `display_task_list(tasks: list[Task]) -> None`

**Status**: 🔄 **Modified** (existing function, enhanced with rich table)

**Purpose**: Display a formatted list of all tasks using a rich Table.

**Signature**:
```python
def display_task_list(tasks: list[Task]) -> None:
    """Display a formatted list of all tasks using a rich Table.

    Args:
        tasks: List of Task objects to display (may be empty)

    Returns:
        None (outputs to terminal via rich Console)

    Raises:
        No exceptions raised (graceful degradation on rendering errors)

    Side Effects:
        - Prints formatted table to stdout via rich.console.Console
        - Prints empty state message if tasks list is empty
        - Prints warning message if rich rendering fails (fallback to plain text)
    """
```

**Input Contract**:
- **Parameter**: `tasks` - List of Task dataclass instances
- **Preconditions**:
  - `tasks` may be an empty list (valid input, triggers empty state)
  - All items in `tasks` must be valid Task objects with required attributes
  - Task titles may be any length (truncation applied internally)
- **Type Validation**: Assumes caller provides valid `list[Task]` (no runtime type checking)

**Output Contract**:
- **Return Value**: None
- **Side Effects**:
  1. **Happy Path** (non-empty list):
     - Renders rich Table with 5 columns to stdout
     - Table includes header row with styled column names
     - Each task rendered as one table row
  2. **Empty State** (empty list):
     - Prints formatted message: "📋 No tasks found. Add a task to get started!"
     - Uses rich styling (italic cyan)
  3. **Error Fallback** (rich rendering failure):
     - Prints warning: "⚠️ Rich formatting unavailable, using plain text."
     - Falls back to simple text format: `[ID] Title | Status | Created`

**Behavior Specifications**:
1. **Title Truncation**:
   - Titles longer than 50 characters are truncated to 47 characters + "..."
   - Truncation formula: `title[:47] + "..." if len(title) > 50 else title`
   - Example: "This is a very long task title that exceeds fifty characters" → "This is a very long task title that exceeds..."

2. **Status Formatting**:
   - `task.completed == True` → "Completed"
   - `task.completed == False` → "Pending"
   - No boolean values displayed directly

3. **Timestamp Formatting**:
   - Input format: ISO 8601 string (e.g., "2025-12-06T14:30:45.123456Z")
   - Output format: "YYYY-MM-DD HH:MM:SS" (e.g., "2025-12-06 14:30:45")
   - Conversion: Parse ISO string, format via `strftime("%Y-%m-%d %H:%M:%S")`

4. **Table Styling**:
   - Header style: "bold magenta"
   - ID column: "dim" style, fixed width 6 characters
   - Title column: minimum width 20 characters, expandable
   - Status column: center-justified
   - Timestamp columns: right-justified

**Error Handling**:
- **Rich rendering failure**: Caught via try-except, triggers plain text fallback
- **Invalid task attributes**: Not validated (assumes caller provides valid tasks)
- **Terminal width issues**: Handled automatically by rich library (responsive layout)

**Performance**:
- Expected render time: <10ms for 10 tasks, <100ms for 100 tasks, <500ms for 1000 tasks
- No pagination (all tasks rendered in single table)

**Example Usage**:
```python
# Example 1: Display multiple tasks
tasks = [
    Task(1, "Buy groceries", "", False, "2025-12-06T10:00:00Z", "2025-12-06T10:00:00Z"),
    Task(2, "Call dentist", "", True, "2025-12-06T11:00:00Z", "2025-12-06T12:00:00Z"),
]
display_task_list(tasks)
# Outputs rich table with 2 rows

# Example 2: Empty list
display_task_list([])
# Outputs: "📋 No tasks found. Add a task to get started!"
```

---

## Helper Functions (Internal)

### `_truncate_title(title: str, max_length: int = 50) -> str`

**Status**: ➕ **New** (internal helper, may be added for clarity)

**Purpose**: Truncate task title to maximum display length with ellipsis.

**Signature**:
```python
def _truncate_title(title: str, max_length: int = 50) -> str:
    """Truncate title to max_length characters with ellipsis if needed.

    Args:
        title: Task title string to truncate
        max_length: Maximum length before truncation (default: 50)

    Returns:
        Truncated title with "..." appended if exceeds max_length,
        otherwise original title unchanged

    Examples:
        >>> _truncate_title("Short title", 50)
        "Short title"
        >>> _truncate_title("This is a very long task title that exceeds fifty characters", 50)
        "This is a very long task title that exceeds..."
    """
```

**Implementation Note**: This may be implemented inline within `display_task_list()` rather than as a separate function (design decision left to implementation phase).

---

### `_format_timestamp(iso_timestamp: str) -> str`

**Status**: ➕ **New** (internal helper, may be added for clarity)

**Purpose**: Convert ISO 8601 timestamp to display format (YYYY-MM-DD HH:MM:SS).

**Signature**:
```python
def _format_timestamp(iso_timestamp: str) -> str:
    """Format ISO 8601 timestamp for table display.

    Args:
        iso_timestamp: Timestamp in ISO 8601 format (e.g., "2025-12-06T14:30:45.123456Z")

    Returns:
        Formatted timestamp string (e.g., "2025-12-06 14:30:45")

    Examples:
        >>> _format_timestamp("2025-12-06T14:30:45.123456Z")
        "2025-12-06 14:30:45"
    """
```

**Implementation Note**: This may be implemented inline or as a separate function (design decision deferred to implementation).

---

## Unchanged Functions

The following functions in `src/ui/prompts.py` remain **unchanged** by this feature:

- `validate_title(title: str) -> tuple[bool, str | None]`
- `validate_description(description: str) -> tuple[bool, str | None]`
- `get_task_title() -> str`
- `get_task_description() -> str`
- `display_task_details(task: Task) -> None`
- `prompt_for_task_id() -> int`
- `display_field_selection_menu() -> None`
- `prompt_for_field_choice() -> int`
- `get_new_task_title(current_title: str) -> str`
- `get_new_task_description(current_description: str) -> str`
- `update_task_prompt() -> None`
- `prompt_for_delete_confirmation(task_title: str) -> bool`
- `delete_task_prompt() -> None`
- `prompt_for_mark_complete_confirmation(task_title: str, current_status: bool) -> bool`
- `mark_complete_prompt() -> None`

---

## External Dependencies (Rich Library)

### Rich Library Imports

**Required Imports**:
```python
from rich.console import Console
from rich.table import Table
```

**Rich API Usage**:

1. **Console Class**:
   ```python
   console = Console()
   console.print(table)  # Render table to stdout
   console.print("message", style="italic cyan")  # Styled text
   ```

2. **Table Class**:
   ```python
   table = Table(
       show_header=True,
       header_style="bold magenta",
       title="Tasks",
       expand=True  # Fill terminal width
   )
   table.add_column("ID", style="dim", width=6)
   table.add_column("Title", min_width=20)
   table.add_column("Status", justify="center")
   table.add_row("1", "Task title", "Pending", "2025-12-06 10:00", "2025-12-06 11:00")
   ```

**Version**: `rich==14.1.0` (specified in `pyproject.toml`)

---

## Backward Compatibility

**Test Compatibility Requirement**: All existing tests in `tests/test_prompts.py` must pass without modification (FR-006).

**Implications**:
- Function signatures cannot change (parameter names, types, return types)
- Side effects (terminal output) may change (tests should not assert on exact output format)
- If tests validate output format, they may need updating (acceptable per spec clarification)

**Risk Mitigation**:
- Review existing tests before implementation
- Ensure tests validate behavior (e.g., "task list is displayed") rather than exact format (e.g., "output contains specific table characters")

---

## Testing Contracts

### Unit Test Requirements

1. **Test: display_task_list with multiple tasks**
   - Given: List of 3 tasks with varying title lengths
   - When: `display_task_list()` is called
   - Then: Function executes without exceptions (output format not strictly validated)

2. **Test: display_task_list with empty list**
   - Given: Empty task list `[]`
   - When: `display_task_list()` is called
   - Then: Function executes without exceptions, empty state message rendered

3. **Test: Title truncation at 50 characters**
   - Given: Task with 51-character title
   - When: `display_task_list()` is called
   - Then: Title is truncated to 47 chars + "..." in rendered output

4. **Test: Title truncation at exactly 50 characters**
   - Given: Task with exactly 50-character title
   - When: `display_task_list()` is called
   - Then: Title is NOT truncated (full title displayed)

5. **Test: Timestamp formatting**
   - Given: Task with ISO 8601 timestamps
   - When: `display_task_list()` is called
   - Then: Timestamps rendered in "YYYY-MM-DD HH:MM:SS" format

6. **Test: Status label mapping**
   - Given: Tasks with `completed=True` and `completed=False`
   - When: `display_task_list()` is called
   - Then: Status column shows "Completed" and "Pending" respectively

7. **Test: Graceful degradation on rich failure**
   - Given: Mock rich Console to raise exception
   - When: `display_task_list()` is called
   - Then: Function prints warning and falls back to plain text (no crash)

---

## Summary

✅ **Primary modification**: `display_task_list()` enhanced with rich table rendering
✅ **Helper functions**: Optional internal helpers for truncation and timestamp formatting
✅ **All other functions**: Unchanged (backward compatible)
✅ **External dependency**: Rich library (already in dependencies)
✅ **Test compatibility**: Maintained (100% existing test pass requirement)

**Readiness**: ✅ Ready to proceed to quickstart.md (Phase 1 continuation)
