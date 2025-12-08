# ADR-0001: Ephemeral Data Architecture with Sequential ID Generation

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-04
- **Feature:** Add Task (001-add-task)
- **Context:** Phase I of the Todo App requires a foundational data architecture for task storage and management. The Constitution mandates ephemeral in-memory state (Principle III) with no file I/O or database operations. The implementation must support sequential ID generation, type-safe data structures, and prepare for future persistence layers in later phases while maintaining simplicity for the current CLI-only scope.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Will be revisited when adding persistence in future phases
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Evaluated dataclass vs dict vs NamedTuple, list vs dict storage, sequential vs UUID IDs
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects models, services, and future migration strategy
-->

## Decision

We will implement an integrated ephemeral data architecture consisting of:

- **Data Model**: Python `dataclass` with type hints for Task entities
  - Fields: `id: int`, `title: str`, `description: str`, `completed: bool`, `created_at: str`, `updated_at: str`
  - Default values: `completed=False`, timestamps auto-generated at creation
  - Validation logic separated into dedicated validation module

- **Storage Structure**: Python `list[Task]` as in-memory storage
  - Module-level list variable: `_task_storage: list[Task] = []` in `task_service.py`
  - No persistence - state lost on application termination
  - Linear search (O(n)) acceptable for ephemeral single-user scope

- **ID Generation**: Sequential integer IDs starting from 1
  - Algorithm: `max(existing_ids) + 1`, or `1` if list empty
  - No UUID or random generation
  - Thread-safety not required (single-threaded CLI)

## Consequences

### Positive

- **Simplicity**: No database setup, no ORM, no migration scripts - reduces Phase I complexity as mandated by Constitution
- **Type Safety**: Dataclass with type hints enables IDE autocomplete, static analysis with mypy, and compile-time error detection
- **Constitution Compliance**: Fully satisfies Principle III (ephemeral state), Principle IV (standard library only), and Principle V (type hints)
- **Testability**: In-memory list enables easy test setup/teardown without database fixtures or mocking
- **Sequential IDs**: Human-readable, predictable, easy to debug in CLI output
- **Future-Ready**: Clear separation allows clean migration path to persistent storage in later phases
- **Zero Dependencies**: No external libraries beyond pytest (Constitution constraint)
- **Fast Development**: Dataclass auto-generates `__init__`, `__repr__`, `__eq__` methods

### Negative

- **Data Loss on Exit**: All tasks lost when application terminates - acceptable for Phase I, blocking for production
- **No Concurrency**: List-based storage with sequential IDs doesn't support concurrent access or distributed systems
- **Performance Ceiling**: O(n) search limits scalability (mitigated by single-user ephemeral scope)
- **Migration Debt**: Future database integration will require:
  - Replacing list with ORM models
  - Migrating ID generation to database auto-increment or UUID
  - Implementing data migration strategy
  - Potential API contract changes
- **No Query Optimization**: Cannot index, filter, or join data efficiently
- **Memory Constraints**: All tasks stored in RAM (practical limit ~10,000 tasks)

## Alternatives Considered

### Alternative A: Dictionary-Based Storage with Dataclass

**Stack**:
- Data Model: Python `dataclass` (same)
- Storage: `dict[int, Task]` with ID as key
- ID Generation: Sequential (same)

**Why Rejected**:
- Adds complexity (key management) without performance benefit for small datasets
- Dictionary ordering not guaranteed in Python < 3.7 (though 3.13 is ordered)
- No advantage for single-user ephemeral scope
- More complex ID generation (need to track max ID separately or scan keys)

### Alternative B: Plain Dictionaries (No Dataclass)

**Stack**:
- Data Model: Plain `dict` with string keys (`{"id": 1, "title": "..."}`)
- Storage: `list[dict]`
- ID Generation: Sequential

**Why Rejected**:
- No type safety - typos in key names cause runtime errors
- No IDE autocomplete or static analysis
- Violates Constitution Principle V (type hints mandatory)
- Harder to maintain and refactor
- No automatic `__repr__` or `__eq__` methods

### Alternative C: NamedTuple

**Stack**:
- Data Model: `collections.namedtuple` or `typing.NamedTuple`
- Storage: `list[Task]`
- ID Generation: Sequential

**Why Rejected**:
- Immutable by default - cannot update `updated_at` timestamp or `completed` status
- Workarounds (creating new instances) are inefficient and confusing
- Doesn't support default values well
- Dataclass is superior for mutable data structures

### Alternative D: UUID-Based ID Generation

**Stack**:
- Data Model: Dataclass (same)
- Storage: List (same)
- ID Generation: `uuid.uuid4()` for globally unique IDs

**Why Rejected**:
- Violates Constitution and spec requirement for "unique integer identifier"
- Spec explicitly requires "starting at 1 for the first task and incrementing by 1"
- Less human-readable in CLI output (e.g., `a3f2-4b1c...` vs `1, 2, 3`)
- Overkill for single-user ephemeral application
- No distributed system requirement in Phase I

### Alternative E: Pydantic Models

**Stack**:
- Data Model: Pydantic `BaseModel` with validation
- Storage: List
- ID Generation: Sequential

**Why Rejected**:
- External dependency violates Constitution Principle IV (standard library only)
- Constitution explicitly states "Dependencies: pytest for testing; otherwise, standard library ONLY"
- Adds unnecessary complexity for simple data structures
- Dataclass sufficient for current needs

## References

- Feature Spec: [specs/001-add-task/spec.md](../../specs/001-add-task/spec.md)
- Implementation Plan: [specs/001-add-task/plan.md](../../specs/001-add-task/plan.md)
- Research Document: [specs/001-add-task/research.md](../../specs/001-add-task/research.md) (Decisions 1, 3, 4)
- Data Model: [specs/001-add-task/data-model.md](../../specs/001-add-task/data-model.md)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (Principles III, IV, V)
- Related ADRs: None (first ADR for this project)
- Evaluator Evidence: [history/prompts/001-add-task/0002-create-add-task-implementation-plan.plan.prompt.md](../../history/prompts/001-add-task/0002-create-add-task-implementation-plan.plan.prompt.md)
