# Quick Start Guide: Rich UI Integration

**Feature**: 006-rich-ui
**Branch**: `006-rich-ui`
**Prerequisites**: Python 3.13+, UV package manager

---

## Overview

This guide provides a quick reference for implementing the Rich UI Integration feature. It covers setup, implementation checkpoints, testing, and verification steps.

---

## 1. Setup & Prerequisites

### Verify Environment
```bash
# Check Python version (must be 3.13+)
python --version

# Check UV is installed
uv --version

# Verify you're on the correct branch
git branch --show-current
# Expected: 006-rich-ui
```

### Verify Dependencies
```bash
# Check rich is installed
uv pip list | grep rich
# Expected: rich==14.1.0

# If not installed, add it (already should be in pyproject.toml)
uv add rich==14.1.0
```

### Review Key Files
Before starting implementation, review these files:
- **Spec**: `specs/006-rich-ui/spec.md` - Feature requirements
- **Plan**: `specs/006-rich-ui/plan.md` - Architecture decisions
- **Research**: `specs/006-rich-ui/research.md` - Implementation patterns
- **Target File**: `src/ui/prompts.py` - File to modify

---

## 2. Implementation Checklist

### Phase 1: Import and Setup
- [ ] Add rich imports to `src/ui/prompts.py`:
  ```python
  from rich.console import Console
  from rich.table import Table
  ```
- [ ] Verify existing imports are preserved (no removals)

### Phase 2: Modify `display_task_list()` Function
- [ ] Locate existing `display_task_list(tasks: list[Task]) -> None` function
- [ ] Replace plain text implementation with rich table rendering
- [ ] Implement empty state handling with rich formatting
- [ ] Add graceful degradation (try-except for rich failures)

**Implementation Template**:
```python
def display_task_list(tasks: list[Task]) -> None:
    """Display a formatted list of all tasks using a rich Table."""
    console = Console()

    # Empty state
    if not tasks:
        console.print("📋 No tasks found. Add a task to get started!", style="italic cyan")
        return

    try:
        # Create table
        table = Table(
            show_header=True,
            header_style="bold magenta",
            title="Tasks",
            expand=True,
        )

        # Define columns
        table.add_column("ID", style="dim", width=6)
        table.add_column("Title", min_width=20)
        table.add_column("Status", justify="center")
        table.add_column("Creation Time", justify="right")
        table.add_column("Last Updated Time", justify="right")

        # Add rows
        for task in tasks:
            # Title truncation
            title = task.title[:47] + "..." if len(task.title) > 50 else task.title

            # Status mapping
            status = "Completed" if task.completed else "Pending"

            # Timestamp formatting
            created = datetime.fromisoformat(task.created_at.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")
            updated = datetime.fromisoformat(task.updated_at.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")

            table.add_row(str(task.id), title, status, created, updated)

        # Render table
        console.print(table)

    except Exception as e:
        # Graceful degradation
        print("⚠️ Rich formatting unavailable, using plain text.")
        for task in tasks:
            status = "✓" if task.completed else "✗"
            print(f"[{task.id}] {task.title} | {status} | {task.created_at}")
```

### Phase 3: Edge Case Handling
- [ ] Title truncation: Test with 50-char, 51-char, and 200-char titles
- [ ] Unicode handling: Test with emoji and special characters in titles
- [ ] Timestamp parsing: Ensure ISO 8601 format is handled correctly
- [ ] Terminal width: Test on 80-column terminal (minimum width)

### Phase 4: Testing
- [ ] Run existing tests: `uv run pytest tests/test_prompts.py`
- [ ] All tests must pass (100% backward compatibility)
- [ ] Run full test suite: `uv run pytest`
- [ ] Verify no regressions in other features

### Phase 5: Manual Verification
- [ ] Start application: `uv run python src/main.py`
- [ ] Add multiple tasks with varying title lengths
- [ ] Select "View Tasks" option
- [ ] Verify table displays with correct columns
- [ ] Verify status shows "Completed" or "Pending" (not True/False)
- [ ] Verify timestamps in "YYYY-MM-DD HH:MM:SS" format
- [ ] Test empty state (delete all tasks, then view)

---

## 3. Key Implementation Points

### Title Truncation Logic
```python
# Truncate if longer than 50 characters
if len(task.title) > 50:
    display_title = task.title[:47] + "..."
else:
    display_title = task.title
```

**Test Cases**:
- 50 chars: "This title is exactly fifty characters in length!" → No truncation
- 51 chars: "This title is exactly fifty-one characters length." → "This title is exactly fifty-one characters..."

### Timestamp Formatting
```python
from datetime import datetime

# Parse ISO 8601 and format for display
iso_string = "2025-12-06T14:30:45.123456Z"
dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
# Result: "2025-12-06 14:30:45"
```

### Status Mapping
```python
# Map boolean to human-readable label
status = "Completed" if task.completed else "Pending"
```

---

## 4. Common Pitfalls & Solutions

### Pitfall 1: Timestamp Format Mismatch
**Problem**: ISO 8601 string has 'Z' suffix, `fromisoformat()` doesn't recognize it.
**Solution**: Replace 'Z' with '+00:00' before parsing.
```python
dt = datetime.fromisoformat(task.created_at.replace('Z', '+00:00'))
```

### Pitfall 2: Truncation Off-by-One Error
**Problem**: Title truncated at 50 characters includes ellipsis, making total 53 chars.
**Solution**: Truncate at 47 characters, then append "..." (total 50).
```python
title[:47] + "..." if len(title) > 50 else title
```

### Pitfall 3: Rich Rendering Fails in CI Environment
**Problem**: Tests fail in CI due to unsupported terminal.
**Solution**: Implement try-except with plain text fallback.
```python
try:
    console.print(table)
except Exception:
    print("⚠️ Rich formatting unavailable, using plain text.")
    # Fallback logic
```

### Pitfall 4: Test Failures Due to Output Format Changes
**Problem**: Existing tests assert on exact output format (plain text).
**Solution**: Update tests to validate behavior, not format (or update assertions to match rich output).

---

## 5. Testing Commands

### Run All Tests
```bash
# Full test suite with coverage
uv run pytest --cov=src --cov-report=term-missing

# Expected: 100% coverage, all tests pass
```

### Run Specific Test File
```bash
# Test prompts module only
uv run pytest tests/test_prompts.py -v

# Expected: All prompt tests pass
```

### Run Code Quality Checks
```bash
# Linting
uv run ruff check .

# Formatting check
uv run ruff format --check .

# Expected: Zero errors, code formatted correctly
```

### Manual Application Test
```bash
# Start the application
uv run python src/main.py

# Test workflow:
# 1. Add 3 tasks (varying title lengths: short, medium, long)
# 2. Mark one task complete
# 3. View tasks (verify table displays)
# 4. Delete all tasks
# 5. View tasks (verify empty state message)
```

---

## 6. Acceptance Criteria Checklist

Before marking this feature complete, verify all acceptance scenarios from the spec:

### User Story 1: View Tasks in Formatted Table (P1)
- [ ] **AC-1.1**: 3 tasks displayed in table with 5 columns (ID, Title, Status, Creation Time, Last Updated Time)
- [ ] **AC-1.2**: Table adjusts column widths for varying title lengths
- [ ] **AC-1.3**: Status clearly shows "Completed" or "Pending"

### User Story 2: Distinguish Task Status Visually (P2)
- [ ] **AC-2.1**: 2 completed + 3 pending tasks show correct status labels
- [ ] **AC-2.2**: Marking task complete updates status in table on next view

### User Story 3: Empty Task List with Clear Messaging (P3)
- [ ] **AC-3.1**: No tasks → formatted empty state message displays
- [ ] **AC-3.2**: Empty state message is clear and friendly

### Functional Requirements (from spec)
- [ ] **FR-001**: Tasks displayed in rich.table.Table format
- [ ] **FR-002**: Table has exactly 5 columns (ID, Title, Status, Creation Time, Last Updated Time)
- [ ] **FR-003**: Status shows "Completed"/"Pending" (not True/False)
- [ ] **FR-006**: All existing tests pass 100%
- [ ] **FR-007**: Empty state uses rich formatting
- [ ] **FR-008**: Timestamps in "YYYY-MM-DD HH:MM:SS" format
- [ ] **FR-010**: Titles >50 chars truncated with "..."
- [ ] **FR-011**: Graceful degradation to plain text if rich fails

### Non-Functional Requirements
- [ ] **NFR-001**: 1000 tasks render in <1 second (optional performance test)

---

## 7. Rollback Plan

If implementation encounters blocking issues:

### Rollback Steps
```bash
# Discard all changes on current branch
git checkout -- src/ui/prompts.py

# Or reset to main branch state
git reset --hard origin/main
```

### Alternative Approach
If rich rendering proves incompatible with existing tests:
1. Investigate test assertions (what exact format do they expect?)
2. Consider refactoring tests to be format-agnostic
3. Document any test changes in implementation notes

---

## 8. Next Steps After Implementation

Once implementation is complete and all acceptance criteria are met:

1. **Run Final Checks**:
   ```bash
   uv run pytest --cov=src
   uv run ruff check .
   uv run ruff format --check .
   ```

2. **Manual Smoke Test**: Run full application workflow (add → view → update → delete → mark complete)

3. **Create Commit**:
   ```bash
   git add src/ui/prompts.py
   git commit -m "feat: integrate rich library for formatted task tables

   - Refactor display_task_list() to use rich.table.Table
   - Add title truncation at 50 characters
   - Format timestamps as YYYY-MM-DD HH:MM:SS
   - Implement graceful degradation for unsupported terminals
   - Maintain 100% backward test compatibility

   🤖 Generated with Claude Code
   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
   ```

4. **Create Pull Request**:
   ```bash
   gh pr create --title "Rich UI Integration (006-rich-ui)" \
     --body "$(cat <<'EOF'
   ## Summary
   - Integrates rich library for formatted task tables
   - Enhances View Tasks feature with 5-column table display
   - Implements title truncation, timestamp formatting, and status labels

   ## Test Plan
   - [x] All existing tests pass (100% compatibility)
   - [x] Manual testing: table displays correctly on 80+ column terminal
   - [x] Edge cases: title truncation, empty state, graceful degradation

   🤖 Generated with Claude Code
   EOF
   )"
   ```

5. **Update Documentation**: Add notes to project README about rich dependency and terminal requirements

---

## 9. Reference Links

- **Rich Library Docs**: https://rich.readthedocs.io/en/stable/tables.html
- **Spec**: `specs/006-rich-ui/spec.md`
- **Plan**: `specs/006-rich-ui/plan.md`
- **Research**: `specs/006-rich-ui/research.md`
- **Contracts**: `specs/006-rich-ui/contracts/ui_functions.md`

---

## Summary

✅ **Implementation Target**: Single file modification (`src/ui/prompts.py`)
✅ **Key Function**: `display_task_list()` enhanced with rich table
✅ **Testing Requirement**: 100% backward compatibility (all existing tests pass)
✅ **Acceptance Criteria**: 3 user stories with 6 acceptance scenarios
✅ **Quality Gates**: pytest, ruff linting, manual verification

**Estimated Implementation Time**: 1-2 hours (simple refactoring of existing display logic)

**Ready to Implement**: ✅ Yes - all design artifacts complete, ready for `/sp.tasks` command
