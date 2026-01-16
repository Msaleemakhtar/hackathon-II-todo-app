# Research: Dapr Integration for Event-Driven Architecture

**Feature**: 004-dapr-integration
**Date**: 2026-01-15
**Phase**: 0 - Research & Discovery

## Purpose

This document consolidates research findings to resolve all "NEEDS CLARIFICATION" items identified in the Technical Context. The goal is to establish concrete technical decisions before proceeding to design phase.

---

## 1. Dapr Runtime Version and Installation

**Decision**: Use Dapr v1.12.5 (latest stable as of 2026-01)

**Rationale**:
- Dapr v1.12+ provides Jobs API (alpha) required for scheduled notification jobs
- PostgreSQL State Store v2 component supported (required for Neon integration)
- Stable Kafka Pub/Sub component with SASL_SSL authentication
- Well-documented sidecar injection for Kubernetes

**Installation Method**:
```bash
# Install Dapr CLI locally
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on Kubernetes (Minikube)
dapr init -k --wait --timeout 300

# Verify installation
kubectl get pods -n dapr-system
# Expected: dapr-operator, dapr-sidecar-injector, dapr-placement, dapr-sentry, dapr-scheduler
```

**Verification**: Dapr system pods running, `dapr status -k` shows healthy components

**Alternatives Considered**:
- Dapr v1.11: Rejected - lacks Jobs API
- Dapr v1.13 (beta): Rejected - not stable enough for production

---

## 2. Dapr HTTP Client Library for Python

**Decision**: Use `httpx` (async HTTP client) with custom Dapr wrapper

**Rationale**:
- `httpx` is the modern async HTTP client for Python (replaces `requests`)
- No official Dapr Python SDK for async operations (official SDK is sync-only)
- Custom wrapper provides type safety and error handling tailored to this project
- Lightweight dependency (no heavy SDK overhead)

**Implementation Pattern**:
```python
# app/dapr/client.py
import httpx
from typing import Any, Dict

class DaprClient:
    def __init__(self, dapr_http_port: int = 3500):
        self.base_url = f"http://localhost:{dapr_http_port}"
        self.client = httpx.AsyncClient(timeout=10.0)

    async def publish_event(
        self,
        pubsub_name: str,
        topic: str,
        data: Dict[str, Any]
    ) -> None:
        """Publish event to Dapr Pub/Sub"""
        url = f"{self.base_url}/v1.0/publish/{pubsub_name}/{topic}"
        response = await self.client.post(url, json=data)
        response.raise_for_status()

    async def save_state(
        self,
        store_name: str,
        key: str,
        value: Any
    ) -> None:
        """Save state to Dapr State Store"""
        url = f"{self.base_url}/v1.0/state/{store_name}"
        response = await self.client.post(
            url,
            json=[{"key": key, "value": value}]
        )
        response.raise_for_status()

    async def get_state(
        self,
        store_name: str,
        key: str
    ) -> Any:
        """Get state from Dapr State Store"""
        url = f"{self.base_url}/v1.0/state/{store_name}/{key}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()
```

**Dependencies**:
```txt
httpx==0.26.0  # Async HTTP client for Dapr API
```

**Alternatives Considered**:
- `dapr-dev` Python SDK: Rejected - synchronous only, not compatible with FastAPI async patterns
- `aiohttp`: Rejected - `httpx` has better type hints and modern API
- Direct `urllib`: Rejected - too low-level, no async support

---

## 3. Dapr Component Configuration Best Practices

**Decision**: Use Kubernetes Secrets with `secretKeyRef` for all sensitive data

**Rationale**:
- Follows Kubernetes security best practices (12-factor app principle)
- Enables environment-specific configuration (dev, staging, prod)
- Prevents credential leakage in Git
- Supports rotation without redeploying components

**Pattern**:
```yaml
# kubernetes/dapr-components/pubsub-kafka.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: todo-phasev
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "bootstrap.redpanda.cloud:9092"
    - name: authType
      value: "sasl"
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
    - name: enableIdempotence
      value: "true"
    - name: acks
      value: "all"
  scopes:
    - backend
    - notification-service
    - email-delivery-service
    - recurring-task-service
```

**Secret Creation**:
```bash
kubectl create secret generic kafka-secrets \
  --from-literal=username="${KAFKA_SASL_USERNAME}" \
  --from-literal=password="${KAFKA_SASL_PASSWORD}" \
  -n todo-phasev
```

**Alternatives Considered**:
- Inline credentials in YAML: Rejected - security risk
- External secret management (Vault): Rejected - out of scope for Phase V
- ConfigMaps: Rejected - not encrypted at rest

---

## 4. CloudEvents Format Handling

**Decision**: Use CloudEvents 1.0 standard with application-level parser

**Rationale**:
- CloudEvents is industry standard for event metadata (source, type, time)
- Enables future integration with external systems (webhooks, monitoring)
- Dapr wraps events in CloudEvents by default
- Provides built-in event correlation via `id` field

**CloudEvents Structure**:
```json
{
  "specversion": "1.0",
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "source": "backend",
  "type": "TaskCreatedEvent",
  "time": "2026-01-15T12:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "user_id": 1,
    "task_id": 123,
    "title": "Complete Dapr migration",
    "priority": "high",
    "due_date": "2026-01-20T17:00:00Z"
  }
}
```

**Consumer Endpoint Pattern**:
```python
# app/routers/events.py
from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/events/task-created")
async def handle_task_created(request: Request):
    """
    Dapr sends CloudEvents to this endpoint.
    Extract data field from CloudEvents envelope.
    """
    cloud_event = await request.json()
    task_data = cloud_event.get("data", {})

    # Process task_data (original event schema)
    task_id = task_data["task_id"]
    user_id = task_data["user_id"]

    # Business logic here
    await process_task_created(task_data)

    return {"status": "SUCCESS"}
```

**Escape Hatch**: If CloudEvents parsing causes issues, use `rawPayload: true` metadata in publish calls to disable CloudEvents wrapping.

**Alternatives Considered**:
- Custom event envelope: Rejected - reinventing the wheel, no interoperability
- `rawPayload: true` by default: Rejected - loses CloudEvents benefits (tracing, correlation)

---

## 5. Jobs API for Notification Service

**Decision**: Replace database polling loop with Dapr Jobs API scheduled execution

**Current Implementation (aiokafka)**:
```python
# app/services/notification_service.py (CURRENT)
async def poll_due_tasks():
    while True:
        await asyncio.sleep(5)  # Poll every 5 seconds
        tasks = await get_tasks_due_soon()
        for task in tasks:
            await publish_reminder_event(task)
```

**Dapr Jobs API Implementation (TARGET)**:
```python
# app/services/notification_service.py (NEW)
from fastapi import APIRouter, Request

router = APIRouter(prefix="/jobs")

@router.post("/check-due-tasks")
async def check_due_tasks_job(request: Request):
    """
    Dapr Scheduler invokes this endpoint every 5 seconds.
    Guaranteed single execution across multiple replicas.
    """
    job_data = await request.json()

    tasks = await get_tasks_due_soon()
    for task in tasks:
        await dapr_client.publish_event(
            pubsub_name="pubsub-kafka",
            topic="task-reminders",
            data={"task_id": task.id, "user_id": task.user_id}
        )

    return {"status": "SUCCESS"}

# Register job at startup
async def register_notification_job():
    await httpx.post(
        "http://localhost:3500/v1.0-alpha1/jobs/check-due-tasks",
        json={
            "schedule": "@every 5s",
            "repeats": -1,  # Infinite repeats
            "dueTime": "0s",  # Start immediately
            "ttl": "3600s"  # Job expires after 1 hour if not renewed
        }
    )
```

**Benefits**:
- Horizontal scaling: Multiple replicas can run without duplicate job execution
- Dapr guarantees at-most-once execution using distributed locks
- Job persistence: Survives scheduler restarts (stored in etcd)
- Simplified code: No manual async loop management

**Verification**: Scale notification service to 3 replicas, verify only one executes job per interval

**Alternatives Considered**:
- Keep database polling: Rejected - cannot scale horizontally (single replica only)
- External cron (Kubernetes CronJob): Rejected - doesn't guarantee single execution
- Redis-based distributed lock: Rejected - Dapr provides this out of the box

---

## 6. Migration Strategy and Rollback Plan

**Decision**: Phased migration with feature flag (environment variable)

**Migration Phases**:

**Phase A: Add Dapr Layer (Non-Breaking)**
1. Install Dapr on Kubernetes
2. Deploy Dapr components (without using them)
3. Add `app/dapr/` module with HTTP client wrappers
4. Deploy with feature flag: `USE_DAPR=false` (default)

**Phase B: Migrate Producers (Low Risk)**
1. Update MCP tools to use Dapr client if `USE_DAPR=true`
2. Test with single replica in staging
3. Enable `USE_DAPR=true` in production
4. Monitor event flow for 24 hours

**Phase C: Migrate Consumers (Medium Risk)**
1. Update notification service to use Dapr subscription
2. Update email delivery service to use Dapr subscription
3. Deploy with Dapr sidecar annotations
4. Verify consumer lag and event processing

**Phase D: Remove aiokafka (Final)**
1. Remove `aiokafka` from requirements.txt
2. Delete `app/kafka/` module
3. Set `USE_DAPR=true` permanently
4. Archive pre-migration Docker images

**Rollback Plan** (30-minute target):
```bash
# 1. Revert Kubernetes deployments (remove Dapr annotations)
kubectl rollout undo deployment/backend -n todo-phasev
kubectl rollout undo deployment/notification-service -n todo-phasev

# 2. Redeploy pre-migration Docker images
helm upgrade todo-app ./helm/todo-app \
  --set image.tag=pre-dapr-migration \
  --namespace todo-phasev

# 3. Remove Dapr components (optional - can leave installed)
kubectl delete component pubsub-kafka -n todo-phasev
kubectl delete component statestore-postgres -n todo-phasev

# 4. Verify aiokafka consumers reconnect
kubectl logs -f deployment/backend -n todo-phasev | grep "aiokafka"
```

**Rollback Triggers**:
- Event publishing latency >200ms p95 for 5 minutes
- Consumer lag >1000 messages for 10 minutes
- Application error rate >1% for 5 minutes
- Dapr sidecar memory >256MB per pod

**Alternatives Considered**:
- Big-bang migration: Rejected - too risky, no incremental validation
- Blue-green deployment: Rejected - requires duplicate infrastructure
- Canary deployment: Accepted as optional enhancement

---

## 7. Performance Testing Methodology

**Decision**: Baseline → Migrate → Compare approach

**Baseline Metrics (aiokafka - to be captured before migration)**:
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Event publish latency | <100ms p95 | Application logs with timestamps |
| Consumer throughput | 10 msg/batch | Consumer lag monitoring |
| End-to-end reminder flow | <10s | Create task → receive email |
| Resource usage | <128MB per pod | Kubernetes metrics |

**Migration Metrics (Dapr - to be validated after migration)**:
| Metric | Target | Acceptance |
|--------|--------|-----------|
| Event publish latency | <100ms p95 | Must not regress >10% |
| Consumer throughput | 10 msg/batch | Must match baseline |
| End-to-end reminder flow | <10s | Must not regress >20% |
| Dapr sidecar overhead | <128MB per pod | Hard limit |

**Testing Tools**:
```python
# tests/performance/test_event_latency.py
import asyncio
import time
from app.dapr.client import DaprClient

async def test_publish_latency():
    client = DaprClient()
    latencies = []

    for i in range(1000):
        start = time.time()
        await client.publish_event(
            pubsub_name="pubsub-kafka",
            topic="task-events",
            data={"task_id": i, "user_id": 1}
        )
        latencies.append(time.time() - start)

    p95 = sorted(latencies)[int(len(latencies) * 0.95)]
    assert p95 < 0.1, f"p95 latency {p95}s exceeds 100ms"
```

**Load Test Scenario**:
```bash
# Create 1000 tasks concurrently
kubectl run loadtest --image=python:3.11 -n todo-phasev -- \
  python -c "
import asyncio
import httpx

async def create_tasks():
    tasks = []
    async with httpx.AsyncClient() as client:
        for i in range(1000):
            tasks.append(client.post(
                'http://backend/api/1/tasks',
                json={'title': f'Task {i}'}
            ))
        await asyncio.gather(*tasks)

asyncio.run(create_tasks())
"
```

**Alternatives Considered**:
- Manual testing only: Rejected - not repeatable
- External load testing tools (Locust, k6): Accepted as optional enhancement

---

## 8. Dapr State Store Schema Design

**Decision**: Use separate `dapr_state_store` table with TTL support

**Schema**:
```sql
-- Created automatically by Dapr PostgreSQL State Store v2
CREATE TABLE dapr_state_store (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    etag VARCHAR(50) NOT NULL,
    update_time TIMESTAMPTZ DEFAULT NOW(),
    expiration_time TIMESTAMPTZ
);

CREATE INDEX idx_dapr_state_expiration ON dapr_state_store(expiration_time)
WHERE expiration_time IS NOT NULL;

-- Metadata table for internal Dapr use
CREATE TABLE dapr_state_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

**Usage Pattern**:
```python
# Store notification service last poll timestamp
await dapr_client.save_state(
    store_name="statestore-postgres",
    key="notification:last_poll",
    value={"timestamp": "2026-01-15T12:00:00Z"},
    metadata={"ttl": "3600"}  # Auto-delete after 1 hour
)

# Retrieve last poll timestamp
state = await dapr_client.get_state(
    store_name="statestore-postgres",
    key="notification:last_poll"
)
```

**Separation from Application Schema**:
- Dapr State Store uses separate tables (`dapr_state_store`, `dapr_state_metadata`)
- Application continues using `tasks_phaseiii`, `categories`, etc. via SQLModel
- No schema conflicts

**Alternatives Considered**:
- Reuse application tables for Dapr state: Rejected - tight coupling, schema conflicts
- Redis State Store: Rejected - adds new infrastructure dependency
- In-memory state (no persistence): Rejected - loses state on pod restart

---

## Summary

All technical clarifications have been resolved:

| Area | Decision | Risk Level |
|------|----------|-----------|
| Dapr Version | v1.12.5 | Low |
| HTTP Client | `httpx` with custom wrapper | Low |
| Component Config | Kubernetes Secrets with `secretKeyRef` | Low |
| CloudEvents | Use standard with parser | Medium |
| Jobs API | Replace polling loop | Medium |
| Migration Strategy | Phased with feature flag | Low |
| Performance Testing | Baseline → Compare | Low |
| State Store | Separate PostgreSQL tables | Low |

**Next Steps**: Proceed to Phase 1 (Design) to generate data models, API contracts, and implementation artifacts.
