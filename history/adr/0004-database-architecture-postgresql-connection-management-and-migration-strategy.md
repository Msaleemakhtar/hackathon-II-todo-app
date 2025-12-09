# ADR-0004: Database Architecture - PostgreSQL Connection Management and Migration Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-09
- **Feature:** Foundational Backend Setup (001-foundational-backend-setup)
- **Context:** Phase II Todo App transitions from ephemeral in-memory storage (Phase I) to persistent PostgreSQL database. The Constitution mandates Neon Serverless PostgreSQL with asyncpg driver and Alembic migrations. We needed to design an integrated database architecture covering connection pooling, async query patterns, migration execution strategy, and test database isolation that balances performance, developer experience, and operational simplicity for Phase II MVP.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Defines data persistence layer and query patterns for entire application
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Connection pooling strategies, sync vs async, migration execution timing, test isolation approaches
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects all data access code, deployment process, testing infrastructure
-->

## Decision

We will implement an integrated PostgreSQL database architecture consisting of:

- **Database Platform**: Neon Serverless PostgreSQL
  - Autoscaling PostgreSQL with built-in connection pooling
  - Branch-based development environments
  - Serverless pricing model (pay for usage)

- **Connection Pooling**: SQLAlchemy async engine with configurable pool
  - **Pool Size**: min=2, max=5 connections for Phase II
  - **Pool Recycle**: 3600 seconds (1 hour) to prevent stale connections
  - **Connection Timeout**: 30 seconds
  - **Pool Pre-ping**: Enabled to verify connections before use
  - Environment variables: `DB_POOL_MIN`, `DB_POOL_MAX`, `DB_POOL_RECYCLE`, `DB_CONNECTION_TIMEOUT`

- **Database Driver**: asyncpg
  - High-performance async PostgreSQL driver (3-5x faster than psycopg2)
  - Non-blocking I/O enables concurrent request handling
  - Native async/await integration with SQLAlchemy 2.0

- **Session Management**: FastAPI dependency injection with async context managers
  - Per-request sessions via `get_db()` dependency
  - Automatic session lifecycle (begin, commit/rollback, close)
  - `async_sessionmaker` with `expire_on_commit=False` for lazy loading

- **Migrations**: Alembic with async support
  - **Execution Strategy**: Manual execution by developers/operators via CLI (`alembic upgrade head`)
  - **Startup Validation**: Application logs warning if migrations pending (does NOT auto-execute)
  - **Auto-generation**: Alembic auto-generates migrations from SQLModel metadata changes
  - **Reversibility**: All migrations MUST include both `upgrade()` and `downgrade()`
  - **Naming Convention**: `YYYYMMDD_HHMMSS_descriptive_name.py`

- **Test Database Isolation**: Separate test database with transactional rollback
  - **Database Name**: `todo_test` (separate from `todo_dev`)
  - **Isolation Strategy**: Each test runs in a transaction, rolled back after test completes
  - **Setup**: pytest fixtures create test database schema once per session
  - **Environment Variable**: `TEST_DATABASE_URL` or auto-derived from `DATABASE_URL` with `_test` suffix

## Consequences

### Positive

- **Performance**: asyncpg non-blocking I/O prevents request queuing; 3-5x faster than psycopg2; connection pooling reuses connections (avoids TCP handshake overhead)
- **Scalability**: Neon autoscaling handles traffic spikes; connection pooling limits database connections (prevents connection exhaustion)
- **Developer Experience**: FastAPI dependency injection makes sessions automatic; Alembic auto-generation from SQLModel reduces boilerplate
- **Safety**: Manual migration execution prevents accidental schema changes; reversible migrations enable rollback on failures; startup validation warns of pending migrations
- **Test Isolation**: Transactional rollback ensures tests don't pollute each other; separate test database prevents accidental dev data corruption
- **Cost Efficiency**: Neon serverless pricing charges for usage; small pool size (max=5) controls costs; pool recycle prevents idle connection charges
- **Constitution Compliance**: Neon PostgreSQL, asyncpg driver, Alembic migrations all mandated by Constitution Section III
- **Monitoring**: Pool pre-ping detects stale connections before use; pool metrics available via SQLAlchemy events

### Negative

- **Connection Pool Tuning**: Requires experimentation to find optimal min/max settings; too few = request queuing, too many = database overload
- **Migration Risk**: Manual execution prone to human error (forgetting to run migrations before deployment); no automatic rollback on failed deploys
- **Startup Warnings**: Applications start even with pending migrations (only logs warning); risk of running code against wrong schema version
- **Test Setup Complexity**: Async test fixtures require pytest-asyncio understanding; transactional rollback adds setup overhead compared to sync tests
- **Neon Dependency**: Vendor lock-in to Neon platform; migration to standard PostgreSQL requires new connection pooling setup (Neon provides built-in pooling)
- **Pool Recycle Overhead**: Recycling connections every hour adds reconnection latency periodically; necessary to prevent stale connections but impacts some requests
- **Async Debugging**: Async stack traces harder to read; connection pool exhaustion errors cryptic (requires understanding asyncio event loop)

## Alternatives Considered

### Alternative A: Synchronous Database Access (psycopg2)
- **Components**: psycopg2 driver, synchronous SQLAlchemy, same Alembic migrations
- **Pros**: Simpler debugging, more mature ecosystem, no async complexity
- **Cons**:
  - Violates Constitution (mandates asyncpg)
  - Blocking I/O limits concurrency (requests wait for database)
  - 3-5x slower than asyncpg
  - Negates FastAPI async benefits (defeats purpose of async framework)
- **Why Rejected**: Constitution violation, performance limitations unacceptable for async architecture

### Alternative B: Auto-Execute Migrations on Startup
- **Components**: Application runs `alembic upgrade head` before accepting requests
- **Pros**: No manual migration step; guarantees schema matches code; prevents schema drift
- **Cons**:
  - Dangerous for production (accidental schema changes on deploy)
  - Race conditions if multiple instances start simultaneously
  - Long migration locks database during startup (downtime)
  - No rollback mechanism if migration fails mid-deploy
- **Why Rejected**: Too risky for production; manual execution with startup validation provides better safety

### Alternative C: No Connection Pooling (Per-Request Connections)
- **Components**: Create new database connection for each request, close after response
- **Pros**: Simpler configuration, no pool tuning required, no stale connection issues
- **Cons**:
  - Huge performance penalty (TCP handshake + authentication per request)
  - Database connection exhaustion under load
  - Latency spike on cold starts (connection setup ~50-100ms)
  - Inefficient use of database resources
- **Why Rejected**: Unacceptable performance tradeoff; connection pooling is standard practice

### Alternative D: Shared Test Database with Truncation
- **Components**: Use same test database for all tests, truncate tables after each test
- **Pros**: Simpler setup (one database), no transaction overhead
- **Cons**:
  - Slower (TRUNCATE is slower than ROLLBACK)
  - Parallel test execution breaks (tests interfere with each other)
  - Foreign key constraints complicate truncation order
  - Risk of test data leaking between tests
- **Why Rejected**: Transactional rollback faster and safer; enables parallel test execution

### Alternative E: Standard PostgreSQL (Self-Hosted)
- **Components**: Self-hosted PostgreSQL on AWS RDS, DigitalOcean, or local server
- **Pros**: No vendor lock-in, full control, predictable pricing
- **Cons**:
  - Violates Constitution (mandates Neon)
  - Requires manual scaling, backups, monitoring
  - No autoscaling (must provision for peak load)
  - Connection pooling (PgBouncer) requires separate infrastructure
- **Why Rejected**: Constitution violation, operational overhead unacceptable for Phase II

## References

- Feature Spec: [specs/001-foundational-backend-setup/spec.md](../../specs/001-foundational-backend-setup/spec.md) (Section 3: Database Schema Requirements)
- Implementation Plan: [specs/001-foundational-backend-setup/plan.md](../../specs/001-foundational-backend-setup/plan.md)
- Research Findings:
  - [FastAPI + SQLModel + asyncpg Integration](../../specs/001-foundational-backend-setup/research.md#1-fastapi--sqlmodel--asyncpg-integration-pattern)
  - [Alembic Async Configuration](../../specs/001-foundational-backend-setup/research.md#4-alembic-async-configuration)
  - [pytest + Async Database Testing](../../specs/001-foundational-backend-setup/research.md#6-pytest--fastapi--async-database-testing)
- Data Model: [specs/001-foundational-backend-setup/data-model.md](../../specs/001-foundational-backend-setup/data-model.md)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (Section III: Persistent & Relational State)
- Related ADRs: ADR-0001 (superseded - Phase I ephemeral data), ADR-0002 (Backend Technology Stack)
- asyncpg Performance: https://magic.io/blog/asyncpg-1m-rows-from-postgres-to-python/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Alembic Documentation: https://alembic.sqlalchemy.org/
