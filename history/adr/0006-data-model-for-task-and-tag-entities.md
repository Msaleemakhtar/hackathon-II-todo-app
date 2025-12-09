# ADR-0006: Data Model for Task and Tag Entities

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-09
- **Feature:** 002-task-tag-api
- **Context:** The current phase introduces Task and Tag entities to the Todo application. These entities require a robust and scalable data model that supports user-specific data isolation, efficient querying, and many-to-many relationships between Tasks and Tags. The design must integrate with the existing PostgreSQL database and SQLModel ORM, and account for future features like advanced filtering and search.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

The data model for Task and Tag entities will include:
1.  **Tag Entity:** `id` (int, PK), `name` (str, UNIQUE per user), `color` (str, nullable), `user_id` (str, FK to User.id).
2.  **Task Entity:** `id` (int, PK), `title` (str), `description` (str, nullable), `completed` (bool), `priority` (str enum), `due_date` (datetime, nullable), `recurrence_rule` (str, nullable), `user_id` (str, FK to User.id), `created_at` (datetime), `updated_at` (datetime).
3.  **TaskTagLink Entity (Junction Table):** `task_id` (int, PK, FK to Task.id), `tag_id` (int, PK, FK to Tag.id) for many-to-many relationship.
4.  **Database Indexes:** Specific indexes on `tasks(user_id, completed, priority, due_date)`, `tags(user_id)`, `task_tag_link(task_id, tag_id)` to optimize queries based on user ownership and filtering criteria.
These models will be implemented using SQLModel, inheriting from an `SQLModel` base class, and integrated with Alembic for schema migrations.

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

*   Provides clear, type-hinted data structures for Tasks and Tags.
*   Supports efficient querying and data integrity through defined relationships and indexes.
*   Enforces user data isolation at the database level.
*   Facilitates future development of features like advanced search and reporting.
*   Leverages existing database architecture (PostgreSQL, SQLModel, Alembic).

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

*   Adds complexity to the database schema with an additional junction table.
*   Requires careful management of relationships and cascading behaviors during development.

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

*   **No explicit junction table (denormalization):** Store tag IDs as a JSON array or comma-separated string in the Task entity.
    *   **Trade-offs:** Simpler schema, but less efficient for querying tags, difficult to maintain data integrity, and poor performance for many-to-many operations. Rejected due to poor query performance and lack of integrity.
*   **Separate microservices for Tasks and Tags:**
    *   **Trade-offs:** Increased operational complexity, overhead for communication between services, and unnecessary for the current application scope. Rejected for over-engineering.

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

*   Feature Spec: specs/002-task-tag-api/spec.md
*   Implementation Plan: specs/002-task-tag-api/plan.md
*   Related ADRs: history/adr/0004-database-architecture-postgresql-connection-management-and-migration-strategy.md
*   Evaluator Evidence: N/A
