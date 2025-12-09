# ADR-0005: Testing Strategy - Async Testing with pytest and Database Isolation

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-09
- **Feature:** Foundational Backend Setup (001-foundational-backend-setup)
- **Context:** Phase II Todo App uses async FastAPI with asyncpg database driver, requiring async-compatible testing infrastructure. The Constitution mandates ≥80% backend test coverage with unit, integration, and contract tests. We needed to design an integrated testing strategy covering async test execution, database isolation, API testing, and test fixtures that ensures high code quality while maintaining fast test execution and developer productivity.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Defines testing patterns and quality assurance for entire backend
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Async vs sync testing, test database strategies, test client choices
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects all backend tests, CI/CD pipeline, development workflow
-->

## Decision

We will implement an integrated async testing strategy consisting of:

- **Test Framework**: pytest with pytest-asyncio
  - `pytest-asyncio` enables async test functions with proper event loop management
  - `asyncio_mode = auto` in pytest.ini for automatic async test detection
  - Compatible with async database operations and FastAPI async endpoints

- **API Testing Client**: httpx AsyncClient
  - Async HTTP client for testing FastAPI async endpoints
  - Compatible with async test functions (native async/await support)
  - Preferred over FastAPI TestClient (synchronous, doesn't support async database fixtures)

- **Database Test Isolation**: Separate test database with transactional rollback
  - **Test Database**: `todo_test` (separate from `todo_dev`)
  - **Isolation Strategy**: Each test runs in a transaction, automatically rolled back after test completes
  - **Schema Setup**: pytest session-scoped fixture creates schema once, reused across all tests
  - **No Cross-Test Pollution**: Rollback ensures tests don't affect each other

- **Test Fixtures**: pytest fixtures for dependency injection override
  - `db_session` fixture: Provides async database session with automatic rollback
  - `client` fixture: Provides httpx AsyncClient with overridden database dependency
  - `app.dependency_overrides` pattern for injecting test database into FastAPI
  - Session-scoped fixtures for expensive setup (database schema creation)

- **Test Organization**:
  - **Unit Tests**: Models, services, utilities (no database/API)
  - **Integration Tests**: API endpoints with database (full request/response cycle)
  - **Contract Tests**: OpenAPI schema validation (future enhancement)
  - Test files: `test_*.py` with descriptive names (`test_auth.py`, `test_models.py`)

- **Coverage Target**: ≥80% line coverage (Constitution requirement)
  - `pytest-cov` for coverage reporting
  - HTML reports for visualization
  - CI pipeline fails if coverage drops below 80%

## Consequences

### Positive

- **Async Compatibility**: pytest-asyncio integrates seamlessly with async FastAPI and asyncpg; no blocking in tests
- **Test Isolation**: Transactional rollback faster than database recreation; enables parallel test execution; prevents test pollution
- **Developer Experience**: httpx AsyncClient API mirrors production usage; pytest fixtures reduce boilerplate; automatic async detection
- **Performance**: Session-scoped schema creation (once per test run); transactional rollback faster than TRUNCATE; tests run in seconds not minutes
- **Type Safety**: Same SQLModel entities in tests as production; type hints work in test code
- **Realistic Testing**: Integration tests use real database (not mocks); catches SQL errors, constraint violations
- **CI/CD Ready**: pytest standard in Python ecosystem; easy GitHub Actions integration; coverage reports in CI
- **Future-Proof**: Contract tests (OpenAPI validation) planned for future; fixture patterns scale to new endpoints

### Negative

- **Learning Curve**: pytest-asyncio requires understanding async fixtures (`@pytest_asyncio.fixture`, `async def`); steeper than sync pytest
- **Setup Complexity**: Database fixtures with dependency overrides more complex than TestClient; requires understanding FastAPI DI
- **Test Database Requirement**: Separate `todo_test` database must exist before running tests; adds setup step for new developers
- **Async Debugging**: Async test failures produce complex stack traces; harder to debug than sync tests
- **Fixture Overhead**: Session/function-scoped fixtures require careful management; scope errors cause flaky tests
- **Parallel Execution Limits**: Transactional rollback works for isolated tests but shared fixtures (e.g., test users) need careful design
- **httpx Learning**: httpx API different from requests library; team must learn new syntax (though similar)

## Alternatives Considered

### Alternative A: FastAPI TestClient (Synchronous)
- **Components**: FastAPI TestClient, pytest (no pytest-asyncio), synchronous tests
- **Pros**: Simpler setup (no async complexity), official FastAPI recommendation for sync apps, easier debugging
- **Cons**:
  - Incompatible with async database fixtures (TestClient runs in separate thread)
  - Cannot test async endpoint behavior accurately
  - Forces synchronous test patterns despite async application
  - Defeats purpose of async architecture
- **Why Rejected**: Incompatible with async database operations; cannot accurately test async FastAPI behavior

### Alternative B: Database Truncation Instead of Rollback
- **Components**: Shared test database, TRUNCATE tables after each test
- **Pros**: Simpler fixture setup (no transactions), easier to inspect test data during debugging
- **Cons**:
  - Slower (TRUNCATE is slower than ROLLBACK, requires CASCADE for foreign keys)
  - Prevents parallel test execution (tests interfere with each other)
  - Foreign key constraints complicate truncation order
  - Test data leakage risk if truncation fails
- **Why Rejected**: Performance penalty unacceptable; rollback faster and safer

### Alternative C: In-Memory SQLite for Tests
- **Components**: SQLite in-memory database instead of PostgreSQL
- **Pros**: Faster setup (no external database), simpler fixture setup, portable
- **Cons**:
  - Different database engine than production (PostgreSQL vs SQLite)
  - SQL dialect differences cause false positives/negatives
  - PostgreSQL-specific features (JSON types, arrays) not testable
  - SQLModel/SQLAlchemy issues hidden in tests, exposed in production
- **Why Rejected**: "Test what you fly, fly what you test" - testing against SQLite doesn't validate PostgreSQL behavior

### Alternative D: Mock Database with unittest.mock
- **Components**: Mock database responses, no real database in tests
- **Pros**: Fastest tests (no I/O), no database setup required, complete control over responses
- **Cons**:
  - Doesn't test actual SQL queries (major blind spot)
  - Misses constraint violations, type errors, SQL syntax issues
  - Brittle tests (mock expectations break on implementation changes)
  - False confidence (tests pass but production fails)
- **Why Rejected**: Unit tests can use mocks, but integration tests MUST use real database

### Alternative E: No Test Database Isolation (Shared Development Database)
- **Components**: Tests run against `todo_dev` database
- **Pros**: Simplest setup (no separate database), easy to inspect test data
- **Cons**:
  - Pollutes development database with test data
  - Concurrent test runs interfere with development work
  - Risk of accidentally deleting development data
  - Tests fail if dev data changes (non-deterministic)
- **Why Rejected**: Dangerous (data corruption risk), non-deterministic tests unacceptable

## References

- Feature Spec: [specs/001-foundational-backend-setup/spec.md](../../specs/001-foundational-backend-setup/spec.md) (Section 10: Testing Acceptance Criteria)
- Implementation Plan: [specs/001-foundational-backend-setup/plan.md](../../specs/001-foundational-backend-setup/plan.md)
- Research Findings: [pytest + FastAPI + Async Database Testing](../../specs/001-foundational-backend-setup/research.md#6-pytest--fastapi--async-database-testing)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (Section VII: Testing Standards)
- Related ADRs: ADR-0002 (Backend Technology Stack), ADR-0004 (Database Architecture)
- pytest-asyncio Documentation: https://pytest-asyncio.readthedocs.io/
- httpx Documentation: https://www.encode.io/httpx/
- FastAPI Testing Guide: https://fastapi.tiangolo.com/advanced/testing-database/
