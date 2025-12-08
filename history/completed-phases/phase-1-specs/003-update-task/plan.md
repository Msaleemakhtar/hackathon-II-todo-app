# Implementation Plan: Update Task

**Branch**: `003-update-task` | **Date**: 2025-12-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-update-task/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable users to modify existing tasks by updating their title and/or description through a menu-driven CLI interface with selective field update capability. Users choose which field(s) to update (title only, description only, or both) via numbered menu options. The feature extends the existing Task data model by modifying only the title, description, and updated_at fields while preserving id, completed, and created_at immutability.

**Technical Approach**: Extend existing TaskService with update operations, add new UI prompts for field selection and data collection, reuse validation logic from add-task feature, implement read-modify-write pattern for in-memory task list.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: Python standard library only (pytest for testing)
**Storage**: In-memory Python list (ephemeral, no persistence)
**Testing**: pytest with 100% coverage requirement
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: Single project (CLI application)
**Performance Goals**: <30 seconds to complete update operation (per SC-001)
**Constraints**: No file I/O, no database, no external dependencies beyond pytest, must validate all inputs with specific error codes
**Scale/Scope**: Single-user CLI, 5 core features (Add/View/Update/Delete/Mark Complete), ephemeral in-memory storage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Spec-Driven Development
- **Status**: PASS
- **Evidence**: Complete specification exists at `specs/003-update-task/spec.md` with 26 functional requirements, 7 success criteria, and validated checklist
- **AI-Generated Code**: All implementation will be AI-generated from this plan and spec

### ✅ Principle II: Console-First Interface (CLI Only)
- **Status**: PASS
- **Evidence**: Feature uses CLI prompts only - "Enter Task ID", "Select update option (1-3)", "Enter New Task Title", "Enter New Task Description"
- **Menu Integration**: Adds "Update Task" option to main menu (per FR-001)

### ✅ Principle III: Ephemeral In-Memory State
- **Status**: PASS
- **Evidence**: Feature operates on existing in-memory task list, no file I/O or database operations (per constitution Section III)
- **Read-Modify-Write**: Updates task in-place in Python list data structure

### ✅ Principle IV: Python & UV Ecosystem
- **Status**: PASS
- **Evidence**: Python 3.13, pytest for testing, no external dependencies beyond standard library
- **Dependencies**: Reuses existing Task dataclass, no new dependencies required

### ✅ Principle V: Clean Code Standards
- **Status**: PASS (will be enforced during implementation)
- **Requirements**: Type hints, Google-style docstrings, PEP 8 compliance, error codes (001-004, 101-104)
- **Validation**: `ruff check .` and `ruff format --check .` must pass

### ✅ Principle VI: Automated Testing
- **Status**: PASS (test plan to be created in Phase 2)
- **Coverage**: 100% coverage requirement per constitution
- **Test Scenarios**: Defined in spec acceptance scenarios (3 user stories with 8 total scenarios)

### ✅ Principle VII: Core Functionality Scope
- **Status**: PASS
- **Evidence**: Update Task is feature #3 in the fixed 5-feature set defined in constitution Section VII
- **Scope Compliance**: No additional features added, focuses only on updating title/description (completion status update is separate "Mark Complete" feature)

**Overall Constitution Compliance**: ✅ ALL GATES PASS - No violations, no complexity justification needed

## Project Structure

### Documentation (this feature)

```text
specs/003-update-task/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command) - TO BE CREATED
├── data-model.md        # Phase 1 output (/sp.plan command) - TO BE CREATED
├── quickstart.md        # Phase 1 output (/sp.plan command) - TO BE CREATED
├── contracts/           # Phase 1 output (/sp.plan command) - TO BE CREATED
│   ├── task_service_interface.py  # TaskService update methods protocol
│   └── ui_prompts_interface.py    # UI display functions protocol
├── checklists/
│   └── requirements.md  # Specification quality checklist (completed, APPROVED)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   └── task.py          # EXISTING: Task dataclass (no changes needed)
├── services/
│   └── task_service.py  # EXTEND: Add update_task() method
├── ui/
│   └── prompts.py       # EXTEND: Add update_task_prompt(), display_field_selection_menu(), prompt_for_field_choice()
├── constants.py         # EXTEND: Add ERROR_104, possibly FIELD_SELECTION_OPTIONS
└── main.py              # EXTEND: Add menu option 3 for "Update Task"

tests/
├── unit/
│   ├── test_task_service.py      # EXTEND: Add test_update_task_*() methods
│   ├── test_prompts.py            # EXTEND: Add test_update_task_prompt_*() methods
│   └── test_main.py               # EXTEND: Add integration test for update flow
└── [integration tests as needed]
```

**Structure Decision**: Single project structure (Option 1) - matches existing codebase established by features 001-add-task and 002-view-task. No new directories required; all changes extend existing modules.

## Complexity Tracking

**No violations** - Constitution Check shows all gates passing. No complexity justification required.

---

## Phase 0: Research & Decisions

**Status**: To be executed

**Research Tasks**:
1. Review existing TaskService implementation from 001-add-task and 002-view-task
2. Document validation patterns to reuse from add-task (error codes 001-003)
3. Document ID validation patterns to reuse from view-task (error codes 101-103)
4. Research Python in-place list modification best practices
5. Document CLI menu-driven selection patterns from existing features

**Output**: `research.md` with decisions on:
- How to locate and modify task in list (by ID lookup)
- Validation function reuse strategy
- Error handling pattern consistency
- Field selection menu UI pattern

---

## Phase 1: Design & Contracts

**Status**: To be executed after Phase 0

**Deliverables**:
1. **data-model.md**: Document Task entity with focus on update semantics
   - Fields: id (immutable), title (mutable), description (mutable), completed (immutable for this feature), created_at (immutable), updated_at (auto-updated)
   - State transitions: updated_at changes on every update regardless of field selection
   - Validation rules: reuse from add-task

2. **contracts/** directory:
   - `task_service_interface.py`: Protocol defining update_task() signature
   - `ui_prompts_interface.py`: Protocol defining update UI functions

3. **quickstart.md**: Step-by-step guide for implementing update feature

4. **Agent context update**: Run `.specify/scripts/bash/update-agent-context.sh claude` to record new patterns

---

## Phase 2: Task Decomposition

**Status**: Deferred to `/sp.tasks` command

This phase is NOT executed by `/sp.plan`. After completing Phase 1, run `/sp.tasks` to generate the detailed task breakdown with test cases.

---

## Notes

- **Reuse Opportunities**: Validation logic from 001-add-task (title/description), ID validation from 002-view-task
- **New Error Code**: ERROR 104 for invalid field selection (1-3)
- **Design Decision**: Field selection menu (Option B from clarifications) provides clear UX with numbered choices
- **Performance**: 30-second target easily achievable for in-memory operations with simple validation
- **Risk**: None identified - straightforward extension of existing patterns
