# Research: Rich UI Integration

**Feature**: 006-rich-ui
**Date**: 2025-12-06
**Status**: Complete

## Research Questions Resolved

### 1. Rich Library Table API and Best Practices

**Decision**: Use `rich.table.Table` with explicit column definitions and row-by-row addition.

**Research Findings**:
- The `rich` library provides a `Table` class that handles automatic column width calculation
- Tables support customizable styling through header styles, borders, and column alignment
- The `Console` class is required for rendering tables to terminal output
- Rich automatically handles terminal width detection and responsive layout

**Implementation Pattern**:
```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(show_header=True, header_style="bold magenta", title="Tasks")
table.add_column("ID", style="dim", width=6)
table.add_column("Title", min_width=20)
table.add_column("Status", justify="center")
table.add_column("Creation Time", justify="right")
table.add_column("Last Updated Time", justify="right")

# Add rows
for task in tasks:
    table.add_row(str(task.id), task.title, status, created, updated)

console.print(table)
```

**Rationale**: This approach provides maximum control over column styling, alignment, and width while maintaining simplicity. The explicit column definitions ensure consistent layout across different terminal widths.

**Alternatives Considered**:
- **Alternative 1**: Use `rich.print()` with manual formatting - Rejected because it doesn't provide automatic column alignment and width calculation
- **Alternative 2**: Use third-party table libraries (tabulate, prettytable) - Rejected because `rich` is already in dependencies and provides superior terminal rendering with modern styling

---

### 2. Title Truncation Strategy

**Decision**: Implement client-side truncation at 50 characters with "..." suffix before passing to table.

**Research Findings**:
- Rich tables automatically wrap long content if columns exceed terminal width
- For optimal user experience and table readability, explicit truncation prevents horizontal scrolling
- The truncation threshold of 50 characters balances readability with information density

**Implementation Pattern**:
```python
def truncate_title(title: str, max_length: int = 50) -> str:
    """Truncate title to max_length characters with ellipsis if needed."""
    if len(title) <= max_length:
        return title
    return title[:max_length - 3] + "..."
```

**Rationale**: Explicit truncation provides predictable behavior across different terminal widths and ensures tables remain scannable without horizontal scrolling. The 50-character limit is derived from spec requirement FR-010.

**Alternatives Considered**:
- **Alternative 1**: Let rich handle wrapping automatically - Rejected because it creates multi-line rows that reduce scannability
- **Alternative 2**: Dynamic truncation based on terminal width - Rejected because it adds complexity and produces inconsistent layouts

---

### 3. Graceful Degradation for Unsupported Terminals

**Decision**: Wrap table rendering in try-except block with fallback to plain text format.

**Research Findings**:
- Rich rendering can fail in non-standard terminal environments (e.g., minimal shells, CI environments)
- The `Console` class can detect terminal capabilities but may still encounter edge cases
- Graceful degradation requires catching rendering exceptions and providing readable fallback

**Implementation Pattern**:
```python
def display_task_list(tasks: list[Task]) -> None:
    """Display tasks with rich table, fallback to plain text on error."""
    try:
        console = Console()
        # ... rich table rendering ...
        console.print(table)
    except Exception as e:
        # Fallback to plain text
        print("⚠️ Rich formatting unavailable, using plain text.")
        for task in tasks:
            status = "✓" if task.completed else "✗"
            print(f"[{task.id}] {task.title} | {status} | {task.created_at}")
```

**Rationale**: This ensures the application remains functional in all environments while providing enhanced UX where supported. The warning message informs users about the degradation without blocking functionality.

**Alternatives Considered**:
- **Alternative 1**: Pre-flight terminal capability check - Rejected because it doesn't cover all edge cases and adds complexity
- **Alternative 2**: Require rich-compatible terminals only - Rejected because it violates the graceful degradation requirement (FR-011)

---

### 4. Timestamp Formatting

**Decision**: Use `strftime("%Y-%m-%d %H:%M:%S")` for consistent timestamp display.

**Research Findings**:
- Python's `datetime.strftime()` provides precise control over timestamp formatting
- The ISO-like format (YYYY-MM-DD HH:MM:SS) is human-readable and internationally unambiguous
- This format is explicitly required by spec requirement FR-008

**Implementation Pattern**:
```python
created_str = task.created_at.strftime("%Y-%m-%d %H:%M:%S")
updated_str = task.updated_at.strftime("%Y-%m-%d %H:%M:%S")
```

**Rationale**: Direct string formatting via `strftime()` ensures consistent output regardless of system locale or timezone settings. The format is concise while remaining fully informative.

**Alternatives Considered**:
- **Alternative 1**: Use ISO 8601 format with timezone (`%Y-%m-%dT%H:%M:%S%z`) - Rejected because spec requires space-separated format without timezone (simpler for CLI display)
- **Alternative 2**: Use locale-aware formatting - Rejected because it produces inconsistent output across different systems

---

### 5. Empty State Messaging

**Decision**: Use `rich.console.Console.print()` for formatted empty state message.

**Research Findings**:
- Rich provides styling capabilities for standalone messages via `Console.print()`
- Empty state messaging should be visually distinct from error messages
- The spec requires "formatted message" (FR-007), suggesting styled output is appropriate

**Implementation Pattern**:
```python
from rich.console import Console

console = Console()
if not tasks:
    console.print("📋 No tasks found. Add a task to get started!", style="italic cyan")
    return
```

**Rationale**: Using rich for empty state messaging maintains consistency with the table display while providing a friendly, styled message. The emoji and color enhance visual appeal without adding functional complexity.

**Alternatives Considered**:
- **Alternative 1**: Plain `print()` statement - Rejected because it's inconsistent with the rich-enhanced UI theme
- **Alternative 2**: Display empty table with header only - Rejected because it's less intuitive than a clear message

---

## Technology Stack Validation

**Confirmed Dependencies**:
- `rich==14.1.0` - Already in `pyproject.toml`, constitution pre-amended ✅
- `pytest>=9.0.1` - Testing framework (dev dependency) ✅
- Python 3.13 - Language version confirmed ✅

**No new dependencies required.**

---

## Performance Considerations

**Benchmark Target**: Render 1000 tasks in <1 second (NFR-001)

**Research Findings**:
- Rich table rendering is optimized for terminal output with minimal overhead
- The primary performance factor is the number of rows, not column complexity
- Rich uses lazy rendering and efficient string building internally

**Expected Performance**:
- 10 tasks: <10ms
- 100 tasks: <100ms
- 1000 tasks: <500ms (well under 1s requirement)

**No performance optimizations needed** for the current scope. If performance issues arise with large datasets in future, consider:
- Pagination (out of scope for this feature)
- Virtual scrolling (not applicable to terminal tables)

---

## Testing Strategy

**Test Coverage Required**:
1. **Unit Tests** (src/ui/prompts.py):
   - Table rendering with multiple tasks
   - Empty state messaging
   - Title truncation (exactly 50 chars, 51 chars, 200 chars)
   - Timestamp formatting validation
   - Graceful degradation (mock terminal failure)

2. **Integration Tests**:
   - End-to-end view tasks workflow
   - Backward compatibility with existing test suite (100% pass requirement)

3. **Edge Case Tests**:
   - Unicode characters in task titles
   - Special characters in task titles
   - Tasks with varying title lengths
   - Terminal width edge cases (80 columns minimum)

**Existing Test Compatibility**: All current tests in `tests/test_prompts.py` must pass without modification (FR-006).

---

## Security Considerations

**No security vulnerabilities introduced**:
- Rich library is a trusted, widely-used package (23M+ downloads/month on PyPI)
- No user input is directly passed to rich without validation (titles are pre-validated)
- No terminal injection risks (rich escapes special characters)
- No network or file I/O operations added

---

## Summary

All research questions have been resolved with clear implementation decisions:

1. ✅ **Rich Table API**: Use `Table` class with explicit column definitions
2. ✅ **Title Truncation**: Client-side truncation at 50 chars with "..."
3. ✅ **Graceful Degradation**: Try-except wrapper with plain text fallback
4. ✅ **Timestamp Format**: `strftime("%Y-%m-%d %H:%M:%S")`
5. ✅ **Empty State**: Rich-styled message via `Console.print()`

**Readiness**: ✅ Ready to proceed to Phase 1 (Data Model & Contracts)
