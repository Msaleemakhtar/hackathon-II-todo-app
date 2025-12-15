# Research: Add Task Feature

**Feature**: Add Task
**Date**: 2025-12-04
**Phase**: Phase 0 - Outline & Research

## Purpose

Document design decisions, technology choices, and best practices for implementing the Add Task feature according to Phase I Constitution requirements.

## Key Design Decisions

### 1. Data Model Implementation

**Decision**: Use Python `dataclass` with type hints for Task model

**Rationale**:
- Constitution Principle V mandates type hints for all function signatures
- Constitution Task Data Model Specification explicitly requires "Python `dataclass` with type hints"
- Dataclasses provide automatic `__init__`, `__repr__`, and `__eq__` methods
- Type hints enable static analysis with mypy (optional but recommended per constitution)
- Cleaner than manual class implementation or dictionaries

**Alternatives Considered**:
- **Plain dictionaries**: Rejected - no type safety, harder to maintain, no IDE support
- **NamedTuple**: Rejected - immutable by default, doesn't support default values well
- **Pydantic**: Rejected - external dependency violates Principle IV (standard library only)
- **Manual class with `__init__`**: Rejected - more boilerplate, dataclass preferred

**Implementation Notes**:
- Use `@dataclass` decorator from `dataclasses` module (Python 3.13 standard library)
- Field types: `id: int`, `title: str`, `description: str`, `completed: bool`, `created_at: str`, `updated_at: str`
- Default values: `completed=False`, timestamps generated at creation time
- Validation logic separate from model (in validation module)

### 2. Timestamp Format

**Decision**: ISO 8601 format with microseconds - `YYYY-MM-DDTHH:MM:SS.ffffffZ`

**Rationale**:
- Constitution Task Data Model specifies "Timestamp (auto-generated on creation)"
- Feature spec FR-012 explicitly requires "ISO 8601 format (YYYY-MM-DDTHH:MM:SS.ffffffZ)"
- UTC timezone ensures consistency across systems
- Microsecond precision sufficient for task tracking
- Human-readable and machine-parseable

**Alternatives Considered**:
- **Unix epoch**: Rejected - not human-readable, spec requires ISO 8601
- **ISO 8601 without microseconds**: Rejected - spec explicitly includes microseconds
- **Local timezone**: Rejected - spec requires UTC for consistency

**Implementation Notes**:
- Use `datetime.datetime.now(datetime.timezone.utc)` for current UTC time
- Format with `.strftime("%Y-%m-%dT%H:%M:%S.%fZ")`
- Store as string (not datetime object) per spec requirements

### 3. ID Generation Strategy

**Decision**: Sequential integer IDs starting from 1, increment by checking max existing ID

**Rationale**:
- Constitution and spec require "unique integer identifier (auto-generated, starts at 1)"
- FR-010: "starting at 1 for the first task and incrementing by 1 for each subsequent task"
- SC-004: "unique sequential IDs starting from 1 with no gaps or duplicates"
- In-memory ephemeral system doesn't need UUID complexity
- Simple max() + 1 algorithm sufficient

**Alternatives Considered**:
- **UUID**: Rejected - overkill for ephemeral single-user app, spec requires integer
- **Random integers**: Rejected - spec requires sequential starting from 1
- **Database auto-increment**: Rejected - no database per Principle III

**Implementation Notes**:
- Empty list: ID = 1
- Non-empty: ID = max(task.id for task in task_list) + 1
- Thread-safe not required (single-user, single-threaded CLI)

### 4. In-Memory Storage Structure

**Decision**: Python `list` of Task dataclass instances

**Rationale**:
- Constitution Principle III: "Task storage exclusively in Python data structures (list, dict, or similar)"
- List provides ordered collection with O(n) search, acceptable for ephemeral single-user app
- Simpler than dict-based lookup (no need for high-performance queries)
- Easy iteration for View Tasks feature
- Direct access by index for operations

**Alternatives Considered**:
- **Dict with ID as key**: Rejected - adds complexity without performance benefit for small datasets
- **Set**: Rejected - unordered, harder to implement sequential ID generation
- **Deque**: Rejected - no advantage over list for this use case

**Implementation Notes**:
- Module-level list variable in `task_service.py`: `_task_storage: list[Task] = []`
- Service functions operate on this shared list
- No persistence mechanism per constitution

### 5. Input Validation Approach

**Decision**: Separate validation functions with specific error codes and retry logic

**Rationale**:
- Constitution Principle V requires "Graceful handling of invalid inputs with clear error messages and error codes"
- Spec defines three error codes: 001 (empty title), 002 (title too long), 003 (description too long)
- FR-004, FR-005, FR-009 specify exact error messages
- FR-016 requires retry without crash

**Alternatives Considered**:
- **Exception-based validation**: Rejected - harder to control exact error message format
- **Inline validation**: Rejected - reduces code reusability and testability
- **Schema validation library**: Rejected - external dependency violates constitution

**Implementation Notes**:
- Validation functions return tuple: `(is_valid: bool, error_message: str | None)`
- Input loop continues until valid input or user exits to menu
- Whitespace stripping applied before validation per FR-002, FR-007

### 6. Code Organization Pattern

**Decision**: Layered architecture with models, services, and UI separation

**Rationale**:
- Constitution Principle V: "Code Organization: Logical separation of concerns (models, storage, operations, UI, main)"
- Enables independent testing of each layer
- Clear boundaries match constitution requirements
- Supports future feature additions (View, Update, Delete, Mark Complete)

**Alternatives Considered**:
- **Single file monolith**: Rejected - violates separation of concerns principle
- **MVC pattern**: Rejected - overkill for CLI, no "view" rendering beyond print statements
- **Hexagonal architecture**: Rejected - excessive for Phase I scope

**Implementation Notes**:
- `models/task.py` - Task dataclass (no business logic)
- `services/task_service.py` - Business operations (create, store, ID generation)
- `ui/prompts.py` - Input collection and validation
- `ui/messages.py` - Message constants (error codes, success messages)
- `constants.py` - Configuration (MAX_TITLE_LENGTH, MAX_DESCRIPTION_LENGTH)

### 7. Testing Strategy

**Decision**: Pytest with unit tests and integration tests, 100% coverage target

**Rationale**:
- Constitution Principle VI: "pytest for all tests", "100% coverage of all core logic"
- Success criteria SC-002 through SC-007 require comprehensive validation
- Unit tests for isolated components (validation, ID generation, Task model)
- Integration test for end-to-end user flow

**Alternatives Considered**:
- **unittest**: Rejected - pytest preferred per constitution
- **Coverage < 100%**: Rejected - constitution mandates 100% core logic coverage
- **Manual testing only**: Rejected - automated testing mandatory

**Implementation Notes**:
- Unit tests: `test_task_model.py`, `test_task_service.py`, `test_prompts.py`, `test_validation.py`
- Integration test: `test_add_task_flow.py` (simulate full user interaction)
- Use `pytest-cov` for coverage reporting (already part of pytest ecosystem)
- Run with: `uv run pytest --cov=src --cov-report=term-missing`

### 8. Error Code Design

**Decision**: Three-digit error codes (001-003) with descriptive messages

**Rationale**:
- Spec assumption: "Error codes (001, 002, 003) are sequential and unique across validation rules for this feature"
- FR-004, FR-005, FR-009 define exact error messages with codes
- Future features will use ranges: Add Task (001-003), View Tasks (101-103), etc.

**Implementation Notes**:
- ERROR 001: "Title is required and must be 1-200 characters." (empty/whitespace-only)
- ERROR 002: "Title is required and must be 1-200 characters." (> 200 chars)
- ERROR 003: "Description cannot exceed 1000 characters."
- Constants defined in `constants.py` or `ui/messages.py`

### 9. Project Initialization

**Decision**: UV for environment and dependency management, pyproject.toml for configuration

**Rationale**:
- Constitution Principle IV: "UV exclusively for dependency and environment management"
- Constitution: "pyproject.toml MUST exist and define project metadata"
- Modern Python standard (PEP 518, PEP 621)

**Implementation Notes**:
- Initialize with: `uv init` or manual `pyproject.toml` creation
- Dependencies: `pytest`, `pytest-cov`, `ruff` (dev dependencies)
- Project metadata: name, version, description, Python version requirement (>=3.13)

### 10. Code Quality Tooling

**Decision**: Ruff for linting and formatting, optional mypy for type checking

**Rationale**:
- Constitution Principle V: "`ruff check .` MUST pass with zero errors", "`ruff format --check .`"
- Constitution: "mypy src/ SHOULD pass" (optional but recommended)
- Ruff is fast, modern, and covers multiple tools (flake8, black, isort)

**Implementation Notes**:
- Configure ruff in `pyproject.toml`: line length, target Python version
- Run before commits: `ruff check .` and `ruff format .`
- Optional: `mypy src/ --strict` for additional type safety

## Open Questions

None. All design decisions are fully constrained by the Constitution and feature specification.

## Next Steps

1. **Phase 1**: Create data-model.md with detailed Task entity specification
2. **Phase 1**: Generate quickstart.md for developer onboarding
3. **Phase 2** (via `/sp.tasks`): Break down implementation into concrete tasks
4. **Red Phase**: Write failing tests based on spec acceptance criteria
5. **Green Phase**: Implement code to pass tests
6. **Refactor Phase**: Clean up code while maintaining test passage

## References

- [Constitution](../../.specify/memory/constitution.md)
- [Feature Specification](./spec.md)
- [Implementation Plan](./plan.md)
