# ADR-0002: Backend Technology Stack - FastAPI, SQLModel, and Python Async Ecosystem

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-09
- **Feature:** Foundational Backend Setup (001-foundational-backend-setup)
- **Context:** Phase II Todo App requires a production-grade backend with persistent storage, JWT authentication, and async request handling. The Constitution mandates FastAPI framework, SQLModel ORM, Neon Serverless PostgreSQL, and uv package manager. We needed to select a cohesive technology stack that balances developer experience, type safety, performance, and maintainability while adhering to constitutional requirements.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Defines entire backend architecture and coding patterns
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Evaluated Django, Flask, different ORMs, sync vs async
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects all backend code: routers, models, services, tests
-->

## Decision

We will implement an integrated Python async backend stack consisting of:

- **Framework**: FastAPI (latest stable)
  - Async-first web framework with automatic OpenAPI documentation
  - Dependency injection system for database sessions and authentication
  - Native Pydantic integration for request/response validation

- **ORM & Validation**: SQLModel
  - Combines SQLAlchemy 2.0 ORM with Pydantic validation
  - Single model definition for database and API schemas
  - Async query support via SQLAlchemy async engine

- **Database Driver**: asyncpg
  - High-performance async PostgreSQL driver
  - Non-blocking I/O for concurrent request handling
  - Connection pooling (min=2, max=5 for Phase II)

- **Database Platform**: Neon Serverless PostgreSQL
  - Serverless autoscaling PostgreSQL
  - Branching for development environments
  - Automatic connection pooling

- **Migrations**: Alembic
  - Database schema versioning and migration
  - Async migration support
  - Auto-generation from SQLModel metadata

- **Language**: Python 3.11+
  - Modern async/await syntax
  - Improved type hints and error messages
  - Performance improvements over 3.10

- **Package Manager**: uv
  - Fast Rust-based Python package installer
  - Lockfile for reproducible builds
  - Faster than pip/poetry

## Consequences

### Positive

- **Type Safety**: SQLModel provides end-to-end type safety from database to API responses, enabling IDE autocomplete and static analysis with mypy
- **Developer Experience**: FastAPI automatic documentation (/docs, /redoc), async patterns, dependency injection reduce boilerplate and improve productivity
- **Performance**: Async architecture enables high concurrency; asyncpg is 3-5x faster than psycopg2; non-blocking I/O prevents request queuing
- **Single Source of Truth**: SQLModel eliminates duplication between ORM models and Pydantic schemas - one class definition serves both purposes
- **Constitution Compliance**: Fully satisfies mandated technology choices (FastAPI, SQLModel, Neon PostgreSQL, uv)
- **Future-Proof**: Async patterns scale naturally to multi-service architecture; SQLModel 0.0.14+ fully supports async operations
- **Ecosystem Maturity**: FastAPI is battle-tested (Uber, Netflix use it); SQLModel created by same author (Sebastián Ramírez) ensuring tight integration
- **Migration Path**: Alembic migrations provide safe schema evolution; reversible migrations enable rollback on failures

### Negative

- **Learning Curve**: Async patterns (async/await, context managers) steeper than synchronous Flask/Django for developers unfamiliar with asyncio
- **Debugging Complexity**: Async stack traces are harder to read; must understand event loop behavior for troubleshooting
- **SQLModel Maturity**: SQLModel is newer (2021) than SQLAlchemy; some edge cases may require dropping to raw SQLAlchemy
- **Connection Pool Tuning**: Requires careful tuning of pool settings (min/max connections) to balance performance and resource usage
- **Testing Complexity**: Async tests require pytest-asyncio; fixtures need async context managers; more setup than sync tests
- **Vendor Lock-in**: Neon is a specific PostgreSQL provider; migration to standard PostgreSQL requires connection string changes (low risk)
- **uv Adoption**: uv is new (2024); fewer Stack Overflow answers compared to pip; team must learn new commands

## Alternatives Considered

### Alternative Stack A: Django + Django ORM + psycopg2 (Synchronous)
- **Components**: Django 5.0, Django ORM, psycopg2, standard PostgreSQL
- **Pros**: Mature ecosystem, built-in admin panel, extensive documentation, synchronous simplicity
- **Cons**:
  - Violates Constitution (mandates FastAPI and SQLModel)
  - Synchronous blocking I/O limits concurrency
  - Heavier framework with unused features (templates, forms)
  - No automatic API documentation
  - Separate serializers required (DRF adds complexity)
- **Why Rejected**: Constitution violation, performance limitations for async workloads

### Alternative Stack B: Flask + SQLAlchemy + psycopg2 (Synchronous)
- **Components**: Flask 3.0, SQLAlchemy 2.0, psycopg2, standard PostgreSQL
- **Pros**: Lightweight, flexible, mature ecosystem, familiar to many developers
- **Cons**:
  - Violates Constitution (mandates FastAPI)
  - Synchronous blocking I/O
  - No automatic API documentation
  - Requires separate Pydantic schemas for validation
  - More boilerplate (manual OpenAPI spec, validation decorators)
- **Why Rejected**: Constitution violation, lacks FastAPI's developer experience benefits

### Alternative Stack C: FastAPI + SQLAlchemy + psycopg2 (Partially Async)
- **Components**: FastAPI, SQLAlchemy 2.0 (without Pydantic integration), psycopg2
- **Pros**: Async framework with familiar ORM
- **Cons**:
  - Violates Constitution (mandates SQLModel)
  - Synchronous database driver (psycopg2) blocks event loop despite async framework
  - Requires separate Pydantic models duplicating SQLAlchemy models
  - Misses SQLModel's schema unification benefits
- **Why Rejected**: Constitution violation, async benefits negated by sync database driver

### Alternative Stack D: FastAPI + Tortoise-ORM + asyncpg
- **Components**: FastAPI, Tortoise-ORM (Django-like async ORM), asyncpg
- **Pros**: Fully async stack, familiar Django ORM patterns
- **Cons**:
  - Violates Constitution (mandates SQLModel)
  - No Pydantic integration (separate schemas required)
  - Smaller community than SQLAlchemy ecosystem
  - Less mature (potential edge case bugs)
- **Why Rejected**: Constitution violation, lacks type-safe schema unification

## References

- Feature Spec: [specs/001-foundational-backend-setup/spec.md](../../specs/001-foundational-backend-setup/spec.md)
- Implementation Plan: [specs/001-foundational-backend-setup/plan.md](../../specs/001-foundational-backend-setup/plan.md)
- Research Findings: [specs/001-foundational-backend-setup/research.md](../../specs/001-foundational-backend-setup/research.md#1-fastapi--sqlmodel--asyncpg-integration-pattern)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (Sections II, III, V)
- Related ADRs: ADR-0001 (superseded - Phase I ephemeral data)
- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- asyncpg Performance: https://magic.io/blog/asyncpg-1m-rows-from-postgres-to-python/
