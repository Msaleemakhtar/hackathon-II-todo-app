---
id: 0004
title: ADR creation for event-driven architecture
stage: plan
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5
feature: 002-event-driven
branch: 002-event-driven
user: salim
command: /sp.adr
labels: ["adr", "planning", "architecture", "event-driven", "kafka"]
links:
  spec: specs/002-event-driven/spec.md
  ticket: null
  adr: "history/adr/0020-event-driven-architecture-stack-kafka-aiokafka-redpanda-cloud.md, history/adr/0021-recurring-task-implementation-icalendar-rrule-with-python-dateutil.md, history/adr/0022-full-text-search-strategy-postgresql-tsvector-with-gin-index.md, history/adr/0023-event-consumer-service-deployment-architecture-kubernetes-single-replica-strategy.md"
  pr: null
files:
  - history/adr/0020-event-driven-architecture-stack-kafka-aiokafka-redpanda-cloud.md
  - history/adr/0021-recurring-task-implementation-icalendar-rrule-with-python-dateutil.md
  - history/adr/0022-full-text-search-strategy-postgresql-tsvector-with-gin-index.md
  - history/adr/0023-event-consumer-service-deployment-architecture-kubernetes-single-replica-strategy.md
tests:
  - No tests created (documentation task)
---

## Prompt

sp.adr

## Response snapshot

Analyzed planning artifacts (plan.md, research.md, data-model.md) from specs/002-event-driven/ and identified 4 architecturally significant decision clusters requiring ADRs. Created comprehensive Architecture Decision Records documenting:

1. **ADR-0020: Event-Driven Architecture Stack** - Integrated decision covering Redpanda Cloud (message broker), aiokafka 0.11.0 (async Python client), Pydantic v2 (event schemas), at-least-once delivery semantics, and SASL/SCRAM authentication. Rejected alternatives: Self-hosted Kafka (operational burden), AWS MSK (vendor lock-in), Redis Streams (constitutional non-compliance), Confluent Cloud (higher cost).

2. **ADR-0021: Recurring Task Implementation** - Integrated approach using iCalendar RRULE (RFC 5545 standard), python-dateutil 2.8.2 (parsing library), whitelist-based validation, Kafka event-driven trigger, and graceful error handling. Rejected alternatives: Natural language recurrence (ambiguity), custom RRULE parser (reinventing wheel), cron-style expressions (not user-friendly).

3. **ADR-0022: Full-Text Search Strategy** - PostgreSQL built-in FTS using tsvector + GIN index, database trigger for auto-maintenance, plainto_tsquery for queries, ts_rank for relevance scoring, and direct SQLAlchemy integration. Rejected alternatives: Elasticsearch (operational complexity), Meilisearch (data sync burden), LIKE/ILIKE (no ranking), Typesense (premature optimization).

4. **ADR-0023: Event Consumer Service Deployment Architecture** - Kubernetes Deployment with single-replica strategy, burstable QoS (200m CPU, 256Mi RAM), database-level idempotency, graceful shutdown with PreStop hooks, and todo-phasev namespace isolation. Rejected alternatives: Multi-replica deployment (coordination complexity), StatefulSet (unnecessary persistence), DaemonSet (unsuitable pattern), Knative serverless (cold start latency).

All ADRs follow constitutional clustering principle (grouped related decisions), document explicit tradeoffs with positive/negative consequences, list multiple alternatives with rejection rationales, and reference planning artifacts for traceability.

## Outcome

- ✅ Impact: Created 4 comprehensive ADRs documenting all architecturally significant decisions from plan.md, ensuring team alignment before implementation phase
- 🧪 Tests: No tests required (documentation task)
- 📁 Files: 4 ADR files created in history/adr/ (0020-0023)
- 🔁 Next prompts: Run /sp.tasks to generate implementation tasks now that architectural decisions are documented and approved
- 🧠 Reflection: Successfully applied ADR clustering principle - grouped technologies by integration (e.g., Kafka+aiokafka+Pydantic as single stack decision) rather than creating separate ADRs for each library, making decisions easier to understand and review

## Evaluation notes (flywheel)

- Failure modes observed: None - all ADRs passed significance test (impact, alternatives, scope), followed template structure, and documented tradeoffs comprehensively
- Graders run and results (PASS/FAIL): PASS - All ADRs include: (1) clustered decisions not atomic choices, (2) explicit alternatives with rejection rationales, (3) positive and negative consequences, (4) references to planning artifacts
- Prompt variant (if applicable): Default /sp.adr command from constitution
- Next experiment (smallest change to try): None - workflow executed successfully as designed
