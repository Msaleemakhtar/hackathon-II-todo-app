# Implementation Plan: Mark Complete

**Branch**: `005-mark-complete` | **Date**: 2025-12-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-mark-complete/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a toggle-based task completion status feature that allows users to mark tasks as complete or incomplete through an interactive CLI menu option. Users enter a task ID, receive a status-appropriate confirmation prompt showing the task title, and upon confirmation the system toggles the `completed` field (False↔True) and updates the `updated_at` timestamp. The feature includes comprehensive input validation, error handling, and follows the existing application patterns for ID validation and confirmation flows.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: Python standard library only (pytest for testing)
**Storage**: In-memory only (Python list of Task dataclass instances, ephemeral)
**Testing**: pytest with comprehensive unit and integration tests
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: Single CLI application
**Performance Goals**: Interactive response time <100ms for status toggle operations
**Constraints**:
- No external dependencies beyond pytest
- No file I/O or database operations
- All code must be AI-generated per constitution
- Maintain 100% test coverage on core logic

**Scale/Scope**:
- Single user, single session
- ~5 core features (CRUD + toggle complete)
- Menu-driven text interface
- Input validation with specific error codes (201-205 range for this feature)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Evidence/Notes |
|-----------|-------------|--------|----------------|
| **I. Spec-Driven Development** | All code AI-generated from specs | ✅ PASS | Feature spec complete in `spec.md`; all implementation will be AI-generated |
| **II. Console-First Interface** | Pure CLI with menu-driven navigation | ✅ PASS | Adds menu option "6. Mark Complete" to existing CLI main menu |
| **III. Ephemeral In-Memory State** | No file I/O, no database, no persistence | ✅ PASS | Uses existing in-memory `_task_storage` list; no new persistence introduced |
| **IV. Python & UV Ecosystem** | Python 3.13+, UV package manager, pytest only | ✅ PASS | Uses Python 3.13, pytest (existing); no new dependencies |
| **V. Clean Code Standards** | Type hints, docstrings, PEP 8, error handling | ✅ PASS | All new code will follow existing patterns with type hints, docstrings, error codes |
| **VI. Automated Testing** | pytest unit tests, 100% coverage | ✅ PASS | Test plan includes comprehensive unit and integration tests |
| **VII. Core Functionality Scope** | 5 features max (this is #5) | ✅ PASS | Mark Complete is the 5th and final feature in Phase I scope |

**Overall Gate Status**: ✅ **APPROVED - All principles satisfied**

**Notes**:
- No violations requiring justification
- Feature aligns perfectly with constitution constraints
- This is the final feature in Phase I feature freeze
- Follows existing architectural patterns (task_service operations, UI prompts, error code sequences)

## Project Structure

### Documentation (this feature)

```text
specs/005-mark-complete/
├── spec.md              # Feature specification (input)
├── plan.md              # This file (/sp.plan output)
├── research.md          # Phase 0: Research findings
├── data-model.md        # Phase 1: Data model design
├── quickstart.md        # Phase 1: Implementation guide
├── contracts/           # Phase 1: API contracts (if applicable)
└── tasks.md             # Phase 2: /sp.tasks output (NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── __init__.py
│   └── task.py              # Task dataclass (EXISTING - no changes needed)
├── services/
│   ├── __init__.py
│   └── task_service.py      # NEW: toggle_task_completion() function
├── ui/
│   ├── __init__.py
│   └── prompts.py           # NEW: mark_complete_prompt() function
├── constants.py             # NEW: Mark Complete error codes (201-205)
└── main.py                  # MODIFIED: Add handle_mark_complete(), menu option 6

tests/
├── unit/
│   ├── __init__.py
│   ├── test_task_service.py      # NEW: test_toggle_task_completion()
│   ├── test_prompts.py           # NEW: test_mark_complete_prompt()
│   └── test_validation.py        # MODIFIED: Add toggle validation tests
└── integration/
    ├── __init__.py
    └── test_mark_complete_flow.py  # NEW: End-to-end toggle flow tests
```

**Structure Decision**: Single CLI project (Option 1) - existing structure maintained.

**Files to Create**:
- `tests/integration/test_mark_complete_flow.py` - Integration tests for complete user flow

**Files to Modify**:
- `src/services/task_service.py` - Add `toggle_task_completion(task_id)` function
- `src/ui/prompts.py` - Add `mark_complete_prompt()` function
- `src/constants.py` - Add error codes 201-205 and Mark Complete messages
- `src/main.py` - Add `handle_mark_complete()` handler and menu integration
- `tests/unit/test_task_service.py` - Add toggle function tests
- `tests/unit/test_prompts.py` - Add prompt function tests

**Files Unchanged**:
- `src/models/task.py` - Task dataclass already has all required fields (`completed`, `updated_at`)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected** - All constitution principles are satisfied without any complexity exceptions required.

---

## Phase 0: Research & Discovery

### Research Questions

Based on the Technical Context analysis, the following questions require investigation before design:

1. **Input Validation Pattern Consistency**
   - Question: What is the exact validation sequence pattern used in existing features (Delete, Update) for task ID input and confirmation?
   - Need: Ensure Mark Complete follows identical error codes, retry logic, and user experience patterns

2. **Confirmation Prompt Architecture**
   - Question: How does the Delete feature implement confirmation prompts with Y/N validation?
   - Need: Reuse or mirror existing confirmation logic for consistency

3. **Error Code Allocation Strategy**
   - Question: What is the error code numbering convention? (101-105 for Delete, 151-155 for Update)
   - Need: Confirm 201-205 range is appropriate for Mark Complete feature

4. **Toggle vs. Separate Actions Design Pattern**
   - Question: Should single "Mark Complete" option intelligently toggle, or provide separate "Mark Complete" and "Mark Incomplete" menu options?
   - Need: Spec indicates toggle behavior; validate this is optimal UX

5. **Timestamp Update Mechanism**
   - Question: How is `updated_at` currently managed in update_task()? Is Task.generate_timestamp() the standard approach?
   - Need: Ensure timestamp update follows existing pattern

### Research Outcomes

All research questions have been answered. See `research.md` for detailed findings and decisions.

**Key Decisions**:
1. ✅ Reuse `prompt_for_task_id()` for input validation (consistency)
2. ✅ Create parallel confirmation function mirroring Delete feature pattern
3. ✅ Use error codes 201-205 (feature-specific isolation)
4. ✅ Single "Mark Complete" menu option with smart toggle (spec-aligned)
5. ✅ Use `Task.generate_timestamp()` for timestamp updates (existing pattern)

---

## Phase 1: Design & Contracts

### Data Model Design

See `data-model.md` for complete data model specification.

**Summary**:
- **Zero new entities** - Operates on existing Task dataclass
- **Two field modifications**: `completed` (toggle), `updated_at` (timestamp)
- **Simple state machine**: Binary toggle False ↔ True
- **Strong invariants**: Five fields remain unchanged (id, title, description, created_at)
- **Comprehensive validation**: Four error codes (201-205) cover all failure modes

### API Contracts

**N/A for this feature** - Internal CLI feature with no external API exposure.

This is a single-application, in-memory CLI tool. All contracts are internal function signatures:

**Service Layer Contract**:
```python
def toggle_task_completion(task_id: int) -> Task:
    """Toggle task completion status.

    Args:
        task_id: Unique identifier of task to toggle

    Returns:
        Updated Task instance with toggled completed field

    Raises:
        ValueError: If task_id invalid or task not found
    """
```

**UI Layer Contract**:
```python
def mark_complete_prompt() -> None:
    """Orchestrate mark complete workflow (ID input → confirmation → toggle)."""

def prompt_for_mark_complete_confirmation(task_title: str, current_status: bool) -> bool:
    """Prompt for Y/N confirmation with dynamic action text.

    Args:
        task_title: Title to display in confirmation prompt
        current_status: Current completed status (determines prompt text)

    Returns:
        True if user confirms (Y/y), False if cancels (N/n)
    """
```

No contracts directory needed - all interfaces are Python function signatures with type hints.

### Implementation Guide

See `quickstart.md` for step-by-step implementation instructions.

**Implementation Steps**:
1. Add constants (error codes, messages, prompts)
2. Add service layer function (`toggle_task_completion`)
3. Add UI layer functions (confirmation + orchestration)
4. Wire into main menu (handler + enable option 6)
5. Write unit tests (service + UI layers)
6. Write integration tests (end-to-end flows)
7. Run full test suite (pytest, ruff, manual smoke test)

**Estimated Effort**: ~440 lines of code (implementation + tests)

---

## Phase 2: Task Generation

**Note**: Phase 2 (task generation) is handled by the `/sp.tasks` command, NOT by `/sp.plan`.

The `/sp.plan` command ends here. Next steps:

1. ✅ **Planning Complete** - This file documents all design decisions
2. ⏭️ **Run `/sp.tasks`** - Generate `tasks.md` with dependency-ordered implementation tasks
3. ⏭️ **Run `/sp.implement`** - Execute tasks and generate code

---

## Constitution Re-Check (Post-Design)

Re-evaluating constitution compliance after Phase 1 design:

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Spec-Driven Development** | ✅ PASS | All design artifacts created from spec; ready for AI code generation |
| **II. Console-First Interface** | ✅ PASS | Menu-driven CLI with numbered option 6 |
| **III. Ephemeral In-Memory State** | ✅ PASS | No new persistence introduced; uses existing `_task_storage` |
| **IV. Python & UV Ecosystem** | ✅ PASS | Python 3.13, pytest only, no new dependencies |
| **V. Clean Code Standards** | ✅ PASS | Quickstart mandates type hints, docstrings, PEP 8 compliance |
| **VI. Automated Testing** | ✅ PASS | 27 tests planned (7 unit service + 10 unit UI + 10 integration) |
| **VII. Core Functionality Scope** | ✅ PASS | Feature #5 of 5 (final feature in Phase I) |

**Final Gate Status**: ✅ **APPROVED - All principles satisfied post-design**

---

## Summary

### Planning Artifacts Generated

✅ **Phase 0 - Research**:
- `research.md` - 5 research questions answered, all design decisions documented

✅ **Phase 1 - Design**:
- `data-model.md` - State transitions, validation rules, data flow diagrams
- `quickstart.md` - Step-by-step implementation guide with 7 implementation steps
- `plan.md` (this file) - Technical context, constitution checks, project structure

### Key Architectural Decisions

1. **Smart Toggle Pattern**: Single menu option with dynamic confirmation prompts (vs. separate complete/incomplete options)
2. **Error Code Isolation**: Feature-specific 201-205 range (vs. reusing shared 101-105)
3. **Pattern Reuse**: Mirrors Delete feature confirmation flow for consistency
4. **Timestamp Management**: Follows Update feature pattern (`Task.generate_timestamp()`)
5. **Validation Strategy**: Reuses `prompt_for_task_id()` to avoid duplication

### Technical Specifications

- **Files Modified**: 4 (constants, service, UI, main)
- **Files Created**: 1 (integration tests)
- **Lines of Code**: ~440 (including tests)
- **Test Coverage**: 27 tests (100% coverage target)
- **Error Codes**: 5 (201-205)
- **User Flows**: 4 user stories, 11 acceptance scenarios

### Success Criteria

Feature is complete when:
1. All 24 functional requirements (FR-001 to FR-024) implemented
2. All 11 acceptance scenarios pass
3. All 27 tests pass with 100% coverage
4. Ruff linter and formatter pass
5. Manual smoke test confirms expected behavior
6. No constitution violations

### Next Steps

1. **Run `/sp.tasks`** to generate dependency-ordered implementation tasks
2. Review `tasks.md` for task breakdown and sequencing
3. **Run `/sp.implement`** to execute tasks and generate code
4. Verify all tests pass and code quality checks succeed
5. Create git commit and pull request

---

**Planning Status**: ✅ **COMPLETE** - Ready for task generation (`/sp.tasks`)

**Branch**: `005-mark-complete`
**Feature Spec**: [specs/005-mark-complete/spec.md](./spec.md)
**Implementation Plan**: This file
**Date Completed**: 2025-12-06
