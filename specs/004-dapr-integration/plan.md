# Implementation Plan: Dapr Integration for Event-Driven Architecture

**Branch**: `004-dapr-integration` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-dapr-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature migrates Phase V's existing Kafka-based event-driven architecture from direct aiokafka producers/consumers to Dapr's infrastructure abstraction layer. The primary goal is to decouple application code from Kafka infrastructure, enabling portability across message brokers (Kafka, Redis Streams, RabbitMQ) without code changes. The migration preserves functional equivalence while introducing Dapr's Pub/Sub, State Store, Secrets, and Jobs API for declarative infrastructure management. This is Part B of Phase V's three-part implementation (001-Advanced Features, 002-Dapr Integration, 003-Cloud Deployment).

## Technical Context

**Language/Version**: Python 3.11+ (backend services), YAML (Dapr components)
**Primary Dependencies**: FastAPI 0.109+, httpx (Dapr HTTP client), Dapr v1.12+ runtime, aiokafka 0.11.0 (to be removed)
**Storage**: Neon Serverless PostgreSQL (application data + Dapr State Store v2), Kafka/Redpanda Cloud (message broker backend for Dapr Pub/Sub)
**Testing**: pytest (unit/integration tests), Dapr CLI (`dapr run`), Kubernetes dry-run validation
**Target Platform**: Kubernetes 1.21+ (Minikube local, Oracle Cloud OKE production)
**Project Type**: Distributed microservices (Backend API, Notification Service, Email Delivery Service, Recurring Task Service)
**Performance Goals**: Event publishing latency <100ms p95 (maintain baseline), 1000 concurrent events in 10s, notification service scales to 3 replicas with single job execution guarantee
**Constraints**: Zero functional regression (100% equivalence with aiokafka baseline), zero downtime migration requirement, Dapr sidecar memory overhead <128MB per pod, 30-minute rollback target
**Scale/Scope**: 4 Dapr component configurations, 4 service deployments with sidecar injection, 2 Kafka topics migrated (task-reminders, task-recurrence), 17 MCP tools updated to use Dapr HTTP API

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅
- **Status**: PASS
- **Verification**: Comprehensive spec.md created with detailed requirements before implementation. Migration follows AI-driven generation pattern.
- **Phase V Workflow Compliance**: This feature follows Phase V specification approach (Part B: Dapr Integration) with AI-generated Dapr components, HTTP client wrappers, and deployment manifests.

### Principle II: Repository Structure ✅
- **Status**: PASS
- **Verification**: Feature operates within `/phaseV/` directory structure. No cross-phase imports. Dapr components in `/phaseV/kubernetes/dapr-components/`, service code in `/phaseV/backend/app/`.
- **Phase Separation**: Migration maintains Phase V isolation. Dapr integration is Phase V-specific and does not affect Phase II/III/IV implementations.

### Principle III: Persistent & Relational State ✅
- **Status**: PASS
- **Verification**: Dapr State Store uses separate tables (`dapr_state_store`, `dapr_state_metadata`) to avoid conflicts with application schema. Application database access remains via SQLModel/asyncpg (no changes to data access layer).
- **Data Isolation**: Dapr state operations maintain user_id scoping through application logic (not Dapr's responsibility).

### Principle XVI: Event-Driven Architecture with Kafka ⚠️
- **Status**: PASS with Transformation
- **Verification**: Migration replaces direct aiokafka usage with Dapr Pub/Sub HTTP API. Kafka remains the message broker backend but is abstracted behind Dapr components.
- **Compliance**: Maintains all Kafka topic requirements (task-events, reminders, task-updates), event schemas, and consumer patterns. Dapr acts as abstraction layer without changing event-driven architecture principles.
- **Transformation Note**: Application code no longer uses `aiokafka` library directly; all pub/sub operations via Dapr HTTP API at `http://localhost:3500`.

### Principle XVII: Distributed Application Runtime with Dapr ✅
- **Status**: PASS
- **Verification**: This feature implements Dapr integration as mandated by Principle XVII. All 4 required Dapr components (Pub/Sub, State Store, Secrets, Jobs API) are configured.
- **Sidecar Injection**: All service deployments include Dapr annotations (`dapr.io/enabled: true`, `dapr.io/app-id`, `dapr.io/app-port`).
- **Infrastructure Abstraction**: Migration removes direct infrastructure clients (aiokafka) and replaces with Dapr HTTP API, enabling portability.

### Principle XVIII: Production Cloud Deployment ⚠️
- **Status**: DEFERRED to Feature 003-Cloud-Deployment
- **Verification**: This feature (004-Dapr-Integration) focuses on infrastructure abstraction layer. Oracle Cloud OKE deployment is out of scope for this feature but will be covered in the next feature (003-Cloud-Deployment).
- **Local Testing**: Dapr migration will be validated on Minikube before cloud deployment.

### Feature Scope (Principle X) ✅
- **Status**: PASS
- **Verification**: Feature scope is clearly bounded: migrate Kafka integration from aiokafka to Dapr. No new business features. No changes to task management logic. Purely infrastructure migration.
- **Backward Compatibility**: 100% functional equivalence maintained with current aiokafka implementation.

### Summary
**Overall Gate Status**: ✅ PASS - All constitutional requirements satisfied. No complexity violations. Feature aligns with Phase V Dapr integration mandate (Principle XVII).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
phaseV/
├── backend/                     # FastAPI backend (enhanced from Phase IV)
│   ├── app/
│   │   ├── kafka/               # Kafka integration (TO BE REPLACED with Dapr)
│   │   │   ├── producer.py      # aiokafka producer (REMOVE after migration)
│   │   │   ├── consumer.py      # aiokafka consumer (REMOVE after migration)
│   │   │   └── events.py        # Event schemas (KEEP - reuse with Dapr)
│   │   ├── dapr/                # NEW: Dapr integration layer
│   │   │   ├── __init__.py
│   │   │   ├── client.py        # Dapr HTTP client wrapper
│   │   │   ├── pubsub.py        # Pub/Sub operations
│   │   │   ├── state.py         # State Store operations
│   │   │   └── jobs.py          # Jobs API operations
│   │   ├── services/
│   │   │   ├── notification_service.py  # MIGRATE: Replace aiokafka consumer with Dapr subscription
│   │   │   ├── email_delivery_service.py # MIGRATE: Replace aiokafka consumer with Dapr subscription
│   │   │   └── recurring_task_service.py # MIGRATE: Replace aiokafka consumer with Dapr subscription
│   │   ├── mcp/
│   │   │   └── tools.py         # MIGRATE: 17 MCP tools to use Dapr client instead of kafka producer
│   │   └── routers/
│   │       └── jobs.py          # NEW: Dapr Jobs API callback endpoint
│   └── requirements.txt         # UPDATE: Remove aiokafka, add httpx
├── kubernetes/
│   ├── dapr-components/         # NEW: Dapr component configurations
│   │   ├── pubsub-kafka.yaml
│   │   ├── statestore-postgres.yaml
│   │   ├── secrets-kubernetes.yaml
│   │   └── jobs-scheduler.yaml
│   ├── helm/
│   │   └── todo-app/
│   │       ├── values.yaml      # UPDATE: Add Dapr sidecar annotations
│   │       └── templates/
│   │           ├── backend-deployment.yaml       # UPDATE: Add Dapr annotations
│   │           ├── notification-deployment.yaml  # UPDATE: Add Dapr annotations
│   │           ├── email-deployment.yaml         # UPDATE: Add Dapr annotations
│   │           ├── recurring-deployment.yaml     # UPDATE: Add Dapr annotations
│   │           └── dapr-components.yaml          # NEW: Deploy Dapr components
│   └── scripts/
│       ├── setup-dapr.sh        # NEW: Initialize Dapr on Kubernetes
│       └── deploy.sh            # UPDATE: Apply Dapr components before deployments
└── docs/
    └── DAPR_GUIDE.md            # NEW: Dapr component configuration and troubleshooting

specs/004-dapr-integration/
├── spec.md                      # Feature specification (COMPLETED)
├── plan.md                      # This file (IN PROGRESS)
├── research.md                  # Phase 0 output (TO BE GENERATED)
├── data-model.md                # Phase 1 output (TO BE GENERATED)
├── quickstart.md                # Phase 1 output (TO BE GENERATED)
└── contracts/                   # Phase 1 output (TO BE GENERATED)
    ├── dapr-pubsub-api.yaml     # Dapr Pub/Sub HTTP API contract
    └── dapr-jobs-api.yaml       # Dapr Jobs HTTP API contract
```

**Structure Decision**: This feature uses the Phase V microservices architecture established in Feature 001 (Advanced Features) and Feature 002 (Event-Driven). The migration strategy is additive-then-replace: (1) Add new `/phaseV/backend/app/dapr/` module for Dapr client wrappers, (2) Migrate MCP tools and consumer services to use Dapr client, (3) Remove `/phaseV/backend/app/kafka/` module after successful migration. All Dapr component YAMLs are centralized in `/phaseV/kubernetes/dapr-components/` for declarative infrastructure management.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No complexity violations. Feature is purely infrastructure migration with no architectural complexity added.
