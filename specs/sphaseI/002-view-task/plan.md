# Implementation Plan: View Task

**Branch**: `002-view-task` | **Date**: 2025-12-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-view-task/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a read-only view feature for the todo application with two capabilities: (1) viewing all tasks in a formatted list with completion indicators and pagination every 20 tasks, and (2) viewing detailed information for a single task by ID with comprehensive validation and error handling. This feature provides users visibility into their task data without modifying it, using console-based display with clear formatting and user-friendly error messages.

## Technical Context

**Language/Version**: Python 3.13 (per constitution requirement)
**Primary Dependencies**: pytest for testing only; Python standard library exclusively
**Storage**: In-memory only (Python list of dataclass instances, no persistence)
**Testing**: pytest with 100% coverage requirement on core logic
**Target Platform**: Command-line interface (cross-platform terminal)
**Project Type**: Single project (console application)
**Performance Goals**: <5 seconds for list view, <10 seconds for detail view (per SC-001, SC-003)
**Constraints**: No file I/O, no databases, CLI-only interface, ephemeral state
**Scale/Scope**: 5 core features total (Add, View, Update, Delete, Mark Complete), View is feature #2

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| **I. Spec-Driven Development** | AI-generated code from written spec | ✅ PASS | Complete spec.md exists; implementation will be AI-generated |
| **II. Console-First Interface** | CLI-only, menu-driven | ✅ PASS | Feature adds "View Tasks" and "View Task Details" menu options |
| **III. Ephemeral In-Memory State** | No persistence, in-memory only | ✅ PASS | Read-only feature, accesses existing in-memory task list |
| **IV. Python & UV Ecosystem** | Python 3.13+, pytest only | ✅ PASS | Uses Python 3.13, pytest for testing, standard library only |
| **V. Clean Code Standards** | Type hints, docstrings, PEP 8 | ⏳ PENDING | To be verified during implementation (ruff check/format) |
| **VI. Automated Testing** | pytest with 100% coverage | ⏳ PENDING | Test suite to be generated per spec acceptance scenarios |
| **VII. Core Functionality Scope** | One of 5 core features | ✅ PASS | "View Tasks" is feature #2 of the defined 5-feature set |

**Result**: ✅ PASS - All applicable gates met. Pending items are implementation-phase verification only.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── __init__.py
│   └── task.py              # Task dataclass (existing, reused)
├── services/
│   ├── __init__.py
│   └── task_service.py      # TaskService class (existing, will extend with view methods)
├── ui/
│   ├── __init__.py
│   └── prompts.py           # UI/display functions (existing, will extend with view display)
├── constants.py             # Constants (existing, may add view-related constants)
├── main.py                  # Main entry point (existing, will add view menu options)
└── __init__.py

tests/
├── unit/
│   ├── __init__.py
│   ├── test_task_service.py     # Will add view operation tests
│   ├── test_validation.py       # Will add view validation tests
│   └── test_main.py             # Will add menu integration tests
├── integration/
│   ├── __init__.py
│   └── test_view_task_flow.py   # NEW: End-to-end view scenarios
└── __init__.py
```

**Structure Decision**: Single project structure (Option 1). This feature extends the existing codebase by adding view operations to TaskService, display functions to ui/prompts.py, and new menu options to main.py. No new modules are required since view operations fit naturally into the existing service layer pattern.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected.** All constitutional principles are satisfied by this feature design.

---

## Phase 0: Research Summary

**Status**: ✅ Complete
**Artifact**: `research.md`

**Key Decisions**:
1. **Display Architecture**: Extend existing TaskService with read-only view methods
2. **Error Handling**: Exception-based with specific error codes (101, 102, 103)
3. **Display Formatting**: UI functions in prompts.py for console output
4. **Input Validation**: Try-except with int() conversion, then range validation
5. **Pagination**: Counter-based, pause every 20 tasks with Enter prompt
6. **Empty Description**: Display "(No description)" placeholder
7. **Timestamp Display**: ISO 8601 format as-is (no conversion)

**Unknowns Resolved**: All technical context items were clear from constitution; no additional research needed.

---

## Phase 1: Design & Contracts Summary

**Status**: ✅ Complete

**Artifacts Generated**:

1. **`data-model.md`** - Entity definitions and transformations
   - Documents existing Task entity (no changes required)
   - Defines display transformations for list and detail views
   - Specifies data access patterns and integrity constraints

2. **`contracts/task_service_interface.py`** - Service layer contracts
   - `get_all_tasks() -> list[Task]` - Retrieve all tasks
   - `get_task_by_id(task_id: int) -> Task` - Retrieve single task by ID
   - Includes error specifications, test scenarios, and performance notes

3. **`contracts/ui_display_interface.py`** - UI layer contracts
   - `display_task_list(tasks: list[Task])` - Format and display list view
   - `display_task_details(task: Task)` - Format and display detail view
   - `prompt_for_task_id() -> int` - Validate and collect task ID input
   - Includes format specifications, error handling, and pagination logic

4. **`quickstart.md`** - User guide and documentation
   - How to use both view features
   - Error message explanations with solutions
   - Common workflows and examples
   - Troubleshooting guide

---

## Constitution Re-Check (Post-Design)

| Principle | Status | Verification |
|-----------|--------|--------------|
| **I. Spec-Driven Development** | ✅ PASS | Design contracts ready for AI implementation |
| **II. Console-First Interface** | ✅ PASS | All display uses print/input, no GUI dependencies |
| **III. Ephemeral In-Memory State** | ✅ PASS | Read-only access to existing in-memory task list |
| **IV. Python & UV Ecosystem** | ✅ PASS | Python 3.13, standard library only, pytest for tests |
| **V. Clean Code Standards** | ✅ PASS | Contracts include type hints, docstrings, error handling |
| **VI. Automated Testing** | ✅ PASS | Test scenarios defined in contracts for all methods |
| **VII. Core Functionality Scope** | ✅ PASS | View Tasks is core feature #2 of 5, no scope creep |

**Result**: ✅ PASS - Design maintains constitutional compliance.

---

## Next Steps

### Immediate: Run `/sp.tasks`
Generate the task breakdown file (`tasks.md`) from this plan:
```bash
/sp.tasks
```

### After Tasks: Run `/sp.implement`
Execute the implementation workflow:
```bash
/sp.implement
```

### Implementation Checklist
- [ ] Add `get_all_tasks()` and `get_task_by_id()` to TaskService
- [ ] Add `display_task_list()`, `display_task_details()`, `prompt_for_task_id()` to ui/prompts.py
- [ ] Add "View Tasks" and "View Task Details" menu options to main.py
- [ ] Write unit tests for service methods
- [ ] Write unit tests for UI functions
- [ ] Write integration tests for end-to-end scenarios
- [ ] Run `uv run pytest --cov=src` → verify 100% coverage
- [ ] Run `uv run ruff check .` → verify no linting errors
- [ ] Run `uv run ruff format --check .` → verify formatting
- [ ] Manual testing with various task counts (0, 1, 20, 21, 100)
- [ ] Manual testing of all error scenarios (102, 103, 101)

---

## Architectural Decisions Requiring ADR

No architecturally significant decisions detected in this feature. The feature follows established patterns from the Add Task feature and the constitution:

- **Service layer pattern**: Already established in 001-add-task
- **Error handling strategy**: Already established in 001-add-task
- **UI separation**: Already established in 001-add-task
- **In-memory storage**: Mandated by constitution

**ADR Recommendation**: None required for this feature.

---

**Plan Status**: ✅ COMPLETE - Ready for `/sp.tasks` command
**Branch**: `002-view-task`
**Date Completed**: 2025-12-06
