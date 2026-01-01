# Implementation Plan: Event-Driven Architecture

**Branch**: `002-event-driven` | **Date**: 2026-01-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-event-driven/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement event-driven architecture with Kafka/Redpanda integration for task management, including:
- Event streaming infrastructure with 3 Kafka topics (task-events, task-reminders, task-recurrence)
- Notification Service: Kafka consumer that sends reminder notifications for tasks with approaching due dates
- Recurring Task Service: Kafka consumer that automatically regenerates recurring tasks on completion
- Full-text search with PostgreSQL tsvector and GIN indexes
- Enhanced MCP tools that publish events asynchronously after database operations
- At-least-once delivery semantics with idempotent consumers

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.109+, aiokafka 0.11.0, python-dateutil 2.8.2, asyncpg 0.29.0, pydantic 2.5.0
**Storage**: Neon PostgreSQL Serverless (shared database with Phase III/IV, enhanced tasks_phaseiii table with priority, due_date, category_id, recurrence_rule, reminder_sent fields; new tables: categories, tags_phasev, task_tags; tsvector search_vector with GIN index)
**Testing**: pytest with async support, integration tests for Kafka producers/consumers, E2E tests for event flow
**Target Platform**: Linux server (Kubernetes pods in todo-phasev namespace)
**Project Type**: Event-driven microservices (Chat API + Notification Service + Recurring Task Service)
**Performance Goals**: Event publishing <50ms p95, reminder processing <200ms p95, recurring task creation <200ms p95, full-text search <200ms p95, 1000 events/sec throughput
**Constraints**: At-least-once delivery (no exactly-once required), fire-and-forget event publishing (non-blocking), single replica for consumer services (MVP), polling-based reminders (5-second interval), RRULE validation whitelist
**Scale/Scope**: Up to 10,000 tasks per user, <10,000 events/day (MVP), 1-hour reminder window, 7-day event retention (task-events, task-recurrence), 1-day retention (task-reminders)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Functional Requirements Compliance

| Req ID      | Description | Compliance Status |
|-------------|-------------|-------------------|
| FR-P5-001   | Enhanced task fields (priority, due_date, category_id, recurrence_rule, reminder_sent) | ✅ PASS - Spec defines enhanced tasks_phaseiii table |
| FR-P5-005   | Full-text search with PostgreSQL tsvector + GIN index | ✅ PASS - Spec FR-026, FR-027, FR-029 define FTS with search_vector |
| FR-P5-006   | Multi-criteria filtering | ✅ PASS - Spec FR-025, FR-030 define search_tasks MCP tool |
| FR-P5-007   | All 17 MCP tools functional | ✅ PASS - Spec references 5 enhanced + 12 new tools (from Feature 001) |
| FR-P5-008   | Kafka event publishing from MCP tools | ✅ PASS - Spec FR-003, FR-006 through FR-009 define event publishing |
| FR-P5-009   | Notification Service (Kafka consumer) | ✅ PASS - Spec FR-010 through FR-016 define Notification Service |
| FR-P5-010   | Recurring Task Service (Kafka consumer) | ✅ PASS - Spec FR-017 through FR-024 define Recurring Task Service |

**NOTE**: FR-P5-002 (Categories CRUD), FR-P5-003 (Tags CRUD), FR-P5-004 (Task-Tag association), and Dapr requirements (FR-P5-011 through FR-P5-014) are OUT OF SCOPE for this feature (002-event-driven). They belong to Feature 001 (foundation) and future Dapr migration feature.

### Quality Requirements Compliance

| Req ID      | Description | Compliance Status |
|-------------|-------------|-------------------|
| QR-P5-001   | Kafka event latency < 500ms p95 | ✅ PASS - Spec SC-001 defines event publishing <50ms p95 (exceeds requirement) |
| QR-P5-002   | Search response time < 300ms p95 | ✅ PASS - Spec SC-004 defines search <200ms p95 (exceeds requirement) |

### Structural Requirements Compliance

| Req ID      | Description | Compliance Status |
|-------------|-------------|-------------------|
| SR-P5-001   | Phase V directory structure | ✅ PASS - Constitution defines /phaseV/ structure; feature fits within it |
| SR-P5-002   | Container artifact evolution exception | ✅ PASS - This feature extends Phase IV backend with Kafka integration |

### Technology Constraints Compliance

| Req ID      | Description | Compliance Status |
|-------------|-------------|-------------------|
| TC-P5-001   | Redpanda Cloud for Kafka | ✅ PASS - Spec FR-001, FR-002 mandate Redpanda Cloud |
| TC-P5-002   | Dapr v1.12+ | ⚠️  DEFERRED - Dapr migration planned for separate feature after event-driven foundation |

### Event-Driven Architecture Principle (XVI) Compliance

| Requirement | Compliance Status |
|-------------|-------------------|
| Kafka/Redpanda Setup | ✅ PASS - Spec FR-001 (Redpanda Cloud with SASL/TLS) |
| 3 Kafka Topics | ✅ PASS - Spec FR-002 (task-events, task-reminders, task-recurrence) |
| Event Schemas | ✅ PASS - Spec FR-006 through FR-009 define 4 event types with Pydantic |
| Event Producers | ✅ PASS - Spec FR-003 (async publishing from MCP tools) |
| Event Consumers | ✅ PASS - Spec FR-010, FR-017 (Notification + Recurring services) |
| At-least-once delivery | ✅ PASS - Spec FR-005 (acks=1, idempotent producers) |
| Consumer idempotency | ✅ PASS - Spec FR-032, FR-033 (idempotent processing, offset commits) |
| aiokafka library | ✅ PASS - Technical Context lists aiokafka 0.11.0 |

### Phase Separation Compliance (Principle II)

| Requirement | Compliance Status |
|-------------|-------------------|
| No cross-phase imports | ✅ PASS - Feature builds on Phase IV container artifacts (constitutional exception) |
| Independent tables | ✅ PASS - Uses tasks_phaseiii (not Phase II tasks), new tables (categories, tags_phasev, task_tags) |
| Separate namespace | ✅ PASS - Kubernetes namespace: todo-phasev (not todo-phaseiv) |

### Data Model Compliance (Principle III)

| Requirement | Compliance Status |
|-------------|-------------------|
| Neon PostgreSQL | ✅ PASS - Spec lists Neon PostgreSQL Serverless |
| SQLModel ORM | ✅ PASS - Implicit from Phase III/IV continuation |
| Async access (asyncpg) | ✅ PASS - Technical Context lists asyncpg 0.29.0 |
| Alembic migrations | ✅ PASS - Spec Dependencies references Feature 001 migration |
| FTS with tsvector + GIN | ✅ PASS - Spec FR-025 through FR-029 |

### MCP Server Architecture Compliance (Principle XI)

| Requirement | Compliance Status |
|-------------|-------------------|
| Stateless tools | ✅ PASS - All MCP tools query database, no in-memory state |
| Event publishing | ✅ PASS - Spec FR-003, FR-006-009 define async event publishing |
| Error handling | ✅ PASS - Spec FR-015, FR-022 define graceful error handling |

### Gate Decision

**STATUS**: ✅ **PASS** - Proceed to Phase 0 Research

**Justifications**:
- All applicable Phase V constitutional requirements are satisfied
- Dapr requirements (TC-P5-002, FR-P5-011 through FR-P5-014) are intentionally deferred to future feature (Dapr Migration), as this feature focuses on direct Kafka integration foundation
- Event-driven architecture (Principle XVI) fully compliant
- This feature represents Part A of Phase V (Advanced Features with Kafka), NOT Part B (Dapr Integration)

## Project Structure

### Documentation (this feature)

```text
specs/002-event-driven/
├── spec.md              # Feature specification (input)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── events.yaml      # Kafka event schemas (Pydantic/OpenAPI)
│   └── mcp-tools.yaml   # MCP tool interfaces
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Structure Decision**: Event-driven microservices architecture (Option 2: Web application) with Kafka integration. This feature extends the Phase IV backend with new services and Kafka integration components.

```text
phaseV/                          # Phase V root (extends Phase IV)
├── backend/                     # FastAPI backend (enhanced from Phase IV)
│   ├── app/
│   │   ├── kafka/              # NEW: Kafka integration
│   │   │   ├── __init__.py
│   │   │   ├── producer.py     # Kafka producer for event publishing
│   │   │   ├── events.py       # Event schema definitions (Pydantic)
│   │   │   └── config.py       # Kafka configuration (broker, topics, credentials)
│   │   ├── services/
│   │   │   ├── notification_service.py    # NEW: Reminder consumer service
│   │   │   ├── recurring_task_service.py  # NEW: Recurring task consumer service
│   │   │   ├── search_service.py          # NEW: Full-text search service
│   │   │   └── task_service.py            # ENHANCED: Event publishing on CRUD
│   │   ├── mcp/
│   │   │   └── tools.py        # ENHANCED: Event publishing, search_tasks tool
│   │   ├── models/
│   │   │   └── task.py         # ENHANCED: priority, due_date, recurrence_rule, reminder_sent
│   │   └── utils/
│   │       └── rrule_parser.py # NEW: iCalendar RRULE parsing
│   ├── alembic/
│   │   └── versions/
│   │       └── YYYYMMDD_add_advanced_task_fields.py  # NEW migration
│   └── tests/
│       ├── test_kafka_events.py           # NEW: Event publishing tests
│       ├── test_notification_service.py   # NEW: Reminder service tests
│       ├── test_recurring_service.py      # NEW: Recurring task tests
│       ├── test_search.py                 # NEW: Full-text search tests
│       └── test_mcp_tools.py              # ENHANCED: Event assertions
├── kubernetes/                  # Kubernetes artifacts (extended from Phase IV)
│   └── helm/
│       └── todo-app/
│           ├── templates/
│           │   ├── notification-deployment.yaml      # NEW: Notification service
│           │   ├── recurring-deployment.yaml         # NEW: Recurring task service
│           │   ├── backend-deployment.yaml           # ENHANCED: Kafka env vars
│           │   └── ...
│           └── values.yaml     # ENHANCED: Kafka config
└── README.md                    # ENHANCED: Event-driven architecture docs
```

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations identified. All gates passed.
