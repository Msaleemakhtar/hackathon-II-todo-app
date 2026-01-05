# ADR-0022: Full-Text Search Strategy (PostgreSQL tsvector with GIN Index)

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2026-01-01
- **Feature:** 002-event-driven
- **Context:** Phase V requires full-text search across task titles and descriptions to support natural language queries (e.g., "find tasks about client meeting"). Need to choose search technology that handles <10,000 tasks/user, provides sub-200ms p95 latency, supports stemming and ranking, and integrates with existing PostgreSQL database without adding operational complexity.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will implement full-text search using PostgreSQL's built-in text search capabilities:

- **Search Technology:** PostgreSQL Full-Text Search (tsvector + tsquery)
- **Indexing Strategy:** GIN (Generalized Inverted Index) on tsvector column
- **Automatic Maintenance:** Database trigger to auto-update search_vector on INSERT/UPDATE
- **Query Function:** plainto_tsquery() for natural language queries
- **Ranking:** ts_rank() with weighted title/description (title matches ranked higher)
- **Language:** English stemming and stop words (pg_catalog.english)
- **Integration:** Direct SQLAlchemy queries via AsyncSession (no separate search service)

**Database Schema:**
```sql
ALTER TABLE tasks_phaseiii ADD COLUMN search_vector tsvector;
CREATE INDEX idx_tasks_search ON tasks_phaseiii USING GIN(search_vector);
CREATE TRIGGER task_search_update BEFORE INSERT OR UPDATE ON tasks_phaseiii
FOR EACH ROW EXECUTE FUNCTION tsvector_update_trigger(search_vector, 'pg_catalog.english', title, description);
```

## Consequences

### Positive

- **Zero external dependencies:** No Elasticsearch, Solr, or Meilisearch to deploy, configure, or maintain
- **Fast for MVP scale:** GIN index provides <200ms p95 latency for <10k tasks/user (meets performance requirement)
- **Integrated with database:** No data synchronization, no eventual consistency issues, single source of truth
- **Automatic stemming:** "running" matches "run", "runs", "runner" automatically via English stemming
- **Stop word filtering:** Ignores "the", "a", "is", "and" to improve relevance
- **Ranking built-in:** ts_rank() provides relevance scoring based on term frequency and document length
- **SQLAlchemy integration:** Direct queries via ORM, no additional client libraries or APIs
- **Trigger-based updates:** search_vector automatically maintained on INSERT/UPDATE (no manual sync)
- **Partial indexing:** Can add WHERE clause to index only non-deleted tasks (performance optimization)
- **Weighting support:** Can boost title matches over description matches with setweight()

### Negative

- **Scalability ceiling:** Performance degrades beyond 10k-100k tasks/user (not suitable for large-scale production)
- **No advanced features:** No fuzzy matching, autocomplete suggestions, or faceted search (would require Elasticsearch)
- **Limited language support:** Only English stemming enabled (adding more languages requires configuration)
- **Index size overhead:** GIN index adds ~50% storage overhead for tsvector column
- **No distributed search:** Single-database bottleneck (can't shard search index across multiple nodes)
- **Query language complexity:** tsquery syntax is less intuitive than Elasticsearch DSL for advanced queries
- **No search analytics:** No built-in query logging, click-through tracking, or A/B testing
- **Maintenance burden:** Database triggers can complicate migrations and rollbacks

## Alternatives Considered

### Alternative A: Elasticsearch (Dedicated Search Engine)
- **Components:** Elasticsearch 8.x + Python client + background sync job to index tasks
- **Why rejected:**
  - **Operational complexity:** Requires deploying, configuring, and monitoring Elasticsearch cluster
  - **Data synchronization:** Eventual consistency between PostgreSQL and Elasticsearch (risk of stale results)
  - **Resource overhead:** Minimum 2GB RAM for single-node Elasticsearch (not viable on minikube)
  - **Cost:** Commercial Elastic Cloud or self-hosted infrastructure (overkill for <10k tasks)
  - **Network latency:** Additional hop to Elasticsearch service adds 10-50ms per query
  - **Overkill for MVP:** Advanced features (geo-search, ML ranking, aggregations) not needed

### Alternative B: Meilisearch (Lightweight Alternative to Elasticsearch)
- **Components:** Meilisearch 1.x + meilisearch-python + sync via webhook or background job
- **Why rejected:**
  - **External service:** Still requires deploying and maintaining separate search server
  - **Data sync complexity:** Need to keep Meilisearch in sync with PostgreSQL (background job or webhook)
  - **Added latency:** Network hop to Meilisearch adds overhead compared to database query
  - **Smaller ecosystem:** Less mature than PostgreSQL FTS or Elasticsearch (fewer resources for debugging)
  - **Not worth complexity:** For <10k tasks, PostgreSQL FTS is sufficient (Meilisearch benefits minimal)

### Alternative C: LIKE/ILIKE Queries (Simple String Matching)
- **Components:** Plain SQL LIKE/ILIKE with wildcards (e.g., `WHERE title ILIKE '%meeting%'`)
- **Why rejected:**
  - **No ranking:** All matches treated equally, no relevance scoring
  - **No stemming:** "running" won't match "run" or "runner" (poor user experience)
  - **Slow for large datasets:** Full table scan without index (O(n) complexity)
  - **No stop word handling:** Matches on "the", "a", "is" create noise in results
  - **Prefix-only indexing:** B-tree index only works for prefix matches (`title LIKE 'abc%'`), not substring

### Alternative D: Typesense (Open-Source Elasticsearch Alternative)
- **Components:** Typesense Cloud or self-hosted + typesense-python client + sync job
- **Why rejected:**
  - **External dependency:** Requires deploying Typesense server (adds operational complexity)
  - **Data synchronization:** Same eventual consistency challenges as Elasticsearch
  - **Resource overhead:** Separate service consumes RAM and CPU (not justified for MVP scale)
  - **Less mature ecosystem:** Smaller community than Elasticsearch or PostgreSQL FTS
  - **Premature optimization:** PostgreSQL FTS is simpler and sufficient for current requirements

## References

- Feature Spec: [specs/002-event-driven/spec.md](../../specs/002-event-driven/spec.md) (FR-025 through FR-029)
- Implementation Plan: [specs/002-event-driven/plan.md](../../specs/002-event-driven/plan.md)
- Research Doc: [specs/002-event-driven/research.md](../../specs/002-event-driven/research.md) (Section 4: PostgreSQL Full-Text Search)
- Data Model: [specs/002-event-driven/data-model.md](../../specs/002-event-driven/data-model.md) (Enhanced Task Model with search_vector)
- Related ADRs: ADR-0004 (Database Architecture - PostgreSQL Connection Management)
- PostgreSQL FTS Docs: https://www.postgresql.org/docs/current/textsearch.html
