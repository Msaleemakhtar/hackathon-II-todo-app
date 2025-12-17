# ADR-0013: Phase III Data Architecture: Separate Tables and Database Isolation

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-17
- **Feature:** 002-ai-chat-service-integration
- **Context:** Phase III requires task storage and conversation history. Need to decide whether to reuse Phase II tables or create separate Phase III schema, and how to manage migrations and data isolation.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Affects data integrity, schema evolution, phase separation
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Shared tables vs separate, single vs multiple databases
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all Phase III features, migrations, testing, deployment
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **separate database tables** for Phase III (`tasks_phaseiii`, `conversations`, `messages`) with **independent Alembic migration history** and **strict no-import policy** from Phase II schema.

**Schema Components**:
- **Task Storage**: `tasks_phaseiii` table (NOT Phase II `tasks` table)
- **Conversation Storage**: `conversations` table (new)
- **Message Storage**: `messages` table (new, foreign key to `conversations`)
- **Migration Management**: Independent Alembic environment (`phaseIII/backend/alembic/`)
- **Data Isolation**: No foreign keys or references to Phase II tables
- **Naming Convention**: Phase III tables use `_phaseiii` suffix to prevent accidental queries

**Table Design**:
```sql
-- tasks_phaseiii (Phase III task storage)
CREATE TABLE tasks_phaseiii (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR NOT NULL,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_tasks_phaseiii_user_id ON tasks_phaseiii(user_id);
CREATE INDEX idx_tasks_phaseiii_user_completed ON tasks_phaseiii(user_id, completed);

-- conversations (chat sessions)
CREATE TABLE conversations (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- messages (chat messages)
CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
  user_id VARCHAR NOT NULL,
  role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
```

## Consequences

### Positive

- **Constitutional Compliance**: Principle II mandates complete phase separation (no Phase II imports)
- **Independent Evolution**: Phase III schema can change without affecting Phase II
- **Data Integrity**: No risk of accidental cross-phase data corruption
- **Migration Safety**: Separate Alembic history prevents migration conflicts
- **Testing Isolation**: Phase III tests can reset schema without affecting Phase II
- **Clear Boundaries**: `_phaseiii` naming makes accidental queries obvious
- **Deployment Flexibility**: Can deploy Phase III without Phase II schema presence

### Negative

- **Data Duplication**: Cannot reuse Phase II task data (users must re-create tasks in Phase III)
- **Storage Overhead**: Duplicate task storage for users using both phases
- **Migration Complexity**: Two separate Alembic environments to maintain
- **Query Confusion**: Developers must remember to query `tasks_phaseiii` not `tasks`
- **Cross-Phase Features**: Future features spanning phases require data synchronization logic

## Alternatives Considered

**Alternative 1: Reuse Phase II `tasks` Table**
- **Pros**: Single source of truth for tasks, no data duplication, simpler queries
- **Cons**: Violates Principle II (no Phase II imports), schema coupling, migration conflicts, accidental Phase II queries
- **Rejected Because**: Constitutional mandate for phase separation; coupling risk unacceptable

**Alternative 2: Shared Database with Namespaced Tables (e.g., `phaseii_tasks`, `phaseiii_tasks`)**
- **Pros**: Single database connection, easier backup/restore, less infrastructure
- **Cons**: Still shares migration environment, coupling risk, does not fully isolate phases
- **Rejected Because**: Incomplete isolation; shared migration history creates coupling

**Alternative 3: Completely Separate Databases (Different PostgreSQL Instances)**
- **Pros**: Maximum isolation, no shared infrastructure, can use different database versions
- **Cons**: Increased infrastructure cost, complex data migration for cross-phase features, duplicate connection pools
- **Rejected Because**: Over-isolation; same database with separate tables sufficient for requirements

**Alternative 4: Use Phase II Tables with View Layer (Views Rename to `tasks_phaseiii`)**
- **Pros**: No data duplication, single underlying storage
- **Cons**: Violates no-import policy, view logic complexity, schema coupling remains, migration confusion
- **Rejected Because**: Views do not solve coupling problem; still imports Phase II schema

## References

- Feature Spec: `specs/sphaseIII/002-ai-chat-service-integration/spec.md`
- Data Model: `specs/sphaseIII/002-ai-chat-service-integration/data-model.md`
- Research Document: `specs/sphaseIII/002-ai-chat-service-integration/research.md` (Section 6)
- Constitution: `.specify/memory/constitution.md` (Principle II: Phase Separation)
- Related ADRs: ADR-0011 (MCP Server Architecture), ADR-0009 (Data Isolation)
