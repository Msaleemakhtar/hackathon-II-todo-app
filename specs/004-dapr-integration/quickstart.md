# Quickstart: Dapr Integration for Event-Driven Architecture

**Feature**: 004-dapr-integration
**Date**: 2026-01-15
**Audience**: Developers implementing the Dapr migration

## Overview

This quickstart guide provides step-by-step instructions for implementing Dapr integration into the existing Kafka-based event-driven architecture. The migration follows a phased approach to minimize risk and enable incremental validation.

---

## Prerequisites

Before starting implementation, ensure you have:

1. **Local Development Environment**:
   - Kubernetes cluster (Minikube or Docker Desktop with Kubernetes enabled)
   - kubectl CLI installed and configured
   - Dapr CLI installed (v1.12+)
   - Python 3.11+ with pip/uv package manager
   - Docker Desktop running

2. **Access to Infrastructure**:
   - Redpanda Cloud Kafka cluster credentials
   - Neon PostgreSQL database connection string
   - Kubernetes namespace `todo-phasev` created

3. **Existing Feature Deployments**:
   - Feature 001 (Advanced Features) deployed
   - Feature 002 (Event-Driven Architecture) deployed with aiokafka
   - Backend, notification service, email delivery service, recurring task service running

4. **Baseline Metrics Captured**:
   - Event publishing latency (current aiokafka baseline)
   - Consumer throughput (messages/batch, consumer lag)
   - End-to-end reminder flow latency (task creation → email delivery)

---

## Phase 0: Dapr Installation and Setup

### Step 1: Install Dapr CLI

```bash
# Install Dapr CLI (Linux/macOS)
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Verify installation
dapr --version
# Expected output: CLI version: 1.12.x, Runtime version: n/a (not installed yet)
```

### Step 2: Initialize Dapr on Kubernetes

```bash
# Initialize Dapr runtime on Kubernetes (Minikube)
dapr init -k --wait --timeout 300

# Verify Dapr system pods are running
kubectl get pods -n dapr-system

# Expected output:
# dapr-operator-xxxxx           1/1     Running
# dapr-sidecar-injector-xxxxx   1/1     Running
# dapr-placement-xxxxx          1/1     Running
# dapr-sentry-xxxxx             1/1     Running
# dapr-scheduler-xxxxx          1/1     Running (required for Jobs API)

# Check Dapr status
dapr status -k
```

### Step 3: Create Kubernetes Secrets

```bash
# Create Kafka credentials secret
kubectl create secret generic kafka-secrets \
  --from-literal=username="${KAFKA_SASL_USERNAME}" \
  --from-literal=password="${KAFKA_SASL_PASSWORD}" \
  -n todo-phasev

# Create PostgreSQL connection string for Dapr State Store
# Extract connection string from existing DATABASE_URL secret
kubectl create secret generic todo-app-secrets \
  --from-literal=POSTGRES_CONNECTION_STRING="${DATABASE_URL}" \
  -n todo-phasev \
  --dry-run=client -o yaml | kubectl apply -f -

# Verify secrets
kubectl get secrets -n todo-phasev
```

---

## Phase 1: Create Dapr Component Configurations

### Step 1: Create Pub/Sub Component (Kafka)

```bash
# Create dapr-components directory
mkdir -p phaseV/kubernetes/dapr-components

# Create pubsub-kafka.yaml
cat > phaseV/kubernetes/dapr-components/pubsub-kafka.yaml <<'EOF'
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
EOF

# Apply component
kubectl apply -f phaseV/kubernetes/dapr-components/pubsub-kafka.yaml

# Verify component loaded
kubectl describe component pubsub-kafka -n todo-phasev
```

### Step 2: Create State Store Component (PostgreSQL)

```bash
cat > phaseV/kubernetes/dapr-components/statestore-postgres.yaml <<'EOF'
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-postgres
  namespace: todo-phasev
spec:
  type: state.postgresql
  version: v2
  metadata:
    - name: connectionString
      secretKeyRef:
        name: todo-app-secrets
        key: POSTGRES_CONNECTION_STRING
    - name: tableName
      value: "dapr_state_store"
    - name: metadataTableName
      value: "dapr_state_metadata"
    - name: cleanupIntervalInSeconds
      value: "3600"
  scopes:
    - backend
    - notification-service
EOF

kubectl apply -f phaseV/kubernetes/dapr-components/statestore-postgres.yaml
```

### Step 3: Create Secrets Store Component

```bash
cat > phaseV/kubernetes/dapr-components/secrets-kubernetes.yaml <<'EOF'
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: todo-phasev
spec:
  type: secretstores.kubernetes
  version: v1
EOF

kubectl apply -f phaseV/kubernetes/dapr-components/secrets-kubernetes.yaml
```

### Step 4: Verify All Components Loaded

```bash
# List all Dapr components
kubectl get components -n todo-phasev

# Expected output:
# pubsub-kafka          59s
# statestore-postgres   45s
# kubernetes-secrets    30s

# Check component logs for errors
kubectl logs -n dapr-system -l app=dapr-operator --tail=50
```

---

## Phase 2: Implement Dapr HTTP Client Wrapper

### Step 1: Add httpx Dependency

```bash
cd phaseV/backend

# Add httpx to requirements.txt
echo "httpx==0.26.0  # Dapr HTTP client" >> requirements.txt

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Create Dapr Client Module

```bash
mkdir -p app/dapr
touch app/dapr/__init__.py

# Create dapr/client.py
cat > app/dapr/client.py <<'EOF'
"""
Dapr HTTP client wrapper for pub/sub, state management, and jobs API.
"""
import httpx
from typing import Any, Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DaprClient:
    def __init__(self, dapr_http_port: int = 3500):
        self.base_url = f"http://localhost:{dapr_http_port}"
        self.client = httpx.AsyncClient(timeout=10.0)

    async def publish_event(
        self,
        pubsub_name: str,
        topic: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Publish event to Dapr Pub/Sub.
        Dapr wraps the event in CloudEvents 1.0 format automatically.
        """
        url = f"{self.base_url}/v1.0/publish/{pubsub_name}/{topic}"
        try:
            response = await self.client.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            logger.info(f"Published event to {topic}: {data.get('event_type', 'unknown')}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            raise

    async def save_state(
        self,
        store_name: str,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """Save state to Dapr State Store"""
        url = f"{self.base_url}/v1.0/state/{store_name}"
        state_entry = {"key": key, "value": value}
        if metadata:
            state_entry["metadata"] = metadata

        try:
            response = await self.client.post(url, json=[state_entry])
            response.raise_for_status()
            logger.debug(f"Saved state: {key}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to save state {key}: {e}")
            raise

    async def get_state(
        self,
        store_name: str,
        key: str
    ) -> Optional[Any]:
        """Get state from Dapr State Store"""
        url = f"{self.base_url}/v1.0/state/{store_name}/{key}"
        try:
            response = await self.client.get(url)
            if response.status_code == 204:
                return None  # Key not found
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get state {key}: {e}")
            raise

    async def delete_state(
        self,
        store_name: str,
        key: str
    ) -> None:
        """Delete state from Dapr State Store"""
        url = f"{self.base_url}/v1.0/state/{store_name}/{key}"
        try:
            response = await self.client.delete(url)
            response.raise_for_status()
            logger.debug(f"Deleted state: {key}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to delete state {key}: {e}")
            raise

    async def schedule_job(
        self,
        job_name: str,
        schedule: str,
        repeats: int = -1,
        due_time: str = "0s",
        ttl: str = "3600s",
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Schedule job with Dapr Jobs API (alpha)"""
        url = f"{self.base_url}/v1.0-alpha1/jobs/{job_name}"
        job_definition = {
            "schedule": schedule,
            "repeats": repeats,
            "dueTime": due_time,
            "ttl": ttl,
            "data": data or {}
        }
        try:
            response = await self.client.post(url, json=job_definition)
            response.raise_for_status()
            logger.info(f"Scheduled job: {job_name} ({schedule})")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to schedule job {job_name}: {e}")
            raise

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
EOF
```

### Step 3: Test Dapr Client Locally

```bash
# Run a simple test with Dapr sidecar
cd phaseV/backend

# Start Dapr sidecar in standalone mode
dapr run --app-id test-app --app-port 8000 --dapr-http-port 3500 \
  --components-path ../kubernetes/dapr-components &

# Run Python test script
python -c "
import asyncio
from app.dapr.client import DaprClient

async def test_dapr():
    client = DaprClient()
    # Test publish
    await client.publish_event(
        pubsub_name='pubsub-kafka',
        topic='task-events',
        data={'event_type': 'test', 'task_id': 999}
    )
    # Test state
    await client.save_state(
        store_name='statestore-postgres',
        key='test:key',
        value={'timestamp': '2026-01-15T12:00:00Z'}
    )
    state = await client.get_state('statestore-postgres', 'test:key')
    print(f'State retrieved: {state}')
    await client.close()

asyncio.run(test_dapr())
"

# Stop Dapr sidecar
dapr stop --app-id test-app
```

---

## Phase 3: Migrate Event Publishers (MCP Tools)

### Step 1: Create Feature Flag

```bash
# Add feature flag to backend config
cat >> phaseV/backend/app/config.py <<'EOF'

# Dapr feature flag
USE_DAPR: bool = Field(default=False, env="USE_DAPR")
EOF
```

### Step 2: Update MCP Tools to Use Dapr Client

```python
# app/mcp/tools.py (example for add_task tool)

from app.dapr.client import DaprClient
from app.config import get_settings

settings = get_settings()
dapr_client = DaprClient() if settings.USE_DAPR else None

@tool
async def add_task(title: str, description: str = "", priority: str = "medium", ...):
    """Add a new task"""
    # 1. Create task in database (unchanged)
    task = await create_task_in_db(...)

    # 2. Publish event via Dapr or aiokafka based on feature flag
    if settings.USE_DAPR and dapr_client:
        await dapr_client.publish_event(
            pubsub_name="pubsub-kafka",
            topic="task-events",
            data={
                "event_type": "created",
                "task_id": task.id,
                "task_data": task.dict(),
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    else:
        # Fallback to aiokafka (existing implementation)
        await kafka_producer.send("task-events", value=event_data)

    return task
```

### Step 3: Deploy with Feature Flag Disabled (Safety Check)

```bash
# Update Helm values
cat >> phaseV/kubernetes/helm/todo-app/values.yaml <<'EOF'

backend:
  env:
    USE_DAPR: "false"  # Feature flag disabled by default
EOF

# Deploy backend with Dapr annotations but flag disabled
helm upgrade todo-app ./phaseV/kubernetes/helm/todo-app \
  --namespace todo-phasev \
  --set backend.image.tag=dapr-migration-v1
```

### Step 4: Enable Dapr for Backend Service

```yaml
# Update backend-deployment.yaml
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
        dapr.io/sidecar-memory-limit: "256Mi"
        dapr.io/sidecar-cpu-limit: "200m"
    spec:
      containers:
        - name: backend
          env:
            - name: USE_DAPR
              value: "true"  # Enable feature flag
```

```bash
# Apply deployment
kubectl apply -f phaseV/kubernetes/helm/todo-app/templates/backend-deployment.yaml

# Verify Dapr sidecar injected
kubectl get pod -n todo-phasev -l app=backend
# Expected: 2/2 containers (app + daprd)

# Check Dapr sidecar logs
kubectl logs -n todo-phasev -l app=backend -c daprd
```

---

## Phase 4: Migrate Event Consumers

### Step 1: Update Notification Service with Dapr Subscription

```python
# app/routers/events.py (new file)
from fastapi import APIRouter, Request
from app.services.notification_service import process_reminder

router = APIRouter(prefix="/events")

@router.post("/dapr/subscribe")
async def get_subscriptions():
    """
    Dapr calls this endpoint to discover subscriptions.
    """
    return [
        {
            "pubsubname": "pubsub-kafka",
            "topic": "task-reminders",
            "route": "/events/reminder-sent"
        }
    ]

@router.post("/events/reminder-sent")
async def handle_reminder_event(request: Request):
    """
    Dapr sends CloudEvents to this endpoint.
    """
    cloud_event = await request.json()
    reminder_data = cloud_event.get("data", {})

    task_id = reminder_data["task_id"]
    user_id = reminder_data["user_id"]

    await process_reminder(task_id, user_id)

    return {"status": "SUCCESS"}
```

### Step 2: Update Notification Service Deployment

```yaml
# notification-deployment.yaml
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "notification-service"
        dapr.io/app-port: "8001"
    spec:
      containers:
        - name: notification-service
          env:
            - name: USE_DAPR
              value: "true"
```

```bash
# Apply deployment
kubectl apply -f phaseV/kubernetes/helm/todo-app/templates/notification-deployment.yaml

# Verify subscription registered
kubectl logs -n todo-phasev -l app=notification-service -c daprd | grep "subscription"
# Expected: "subscription registered: task-reminders -> /events/reminder-sent"
```

---

## Phase 5: Testing and Validation

### Step 1: End-to-End Event Flow Test

```bash
# Create a task with due date via ChatKit UI
# Expected: Task created, event published via Dapr, reminder sent

# Verify event published
kubectl logs -n todo-phasev -l app=backend -c daprd | grep "published message to topic task-events"

# Verify event consumed
kubectl logs -n todo-phasev -l app=notification-service -c daprd | grep "received message from topic task-reminders"

# Check application logs
kubectl logs -n todo-phasev -l app=notification-service -c notification-service
```

### Step 2: Performance Baseline Comparison

```bash
# Run performance test (1000 concurrent task creations)
kubectl run loadtest --image=python:3.11 -n todo-phasev --rm -it -- bash
# Inside pod:
pip install httpx
python <<EOF
import asyncio
import httpx
import time

async def create_tasks():
    async with httpx.AsyncClient() as client:
        start = time.time()
        tasks = [
            client.post(
                "http://backend:8000/api/1/tasks",
                json={"title": f"Task {i}"},
                headers={"Authorization": "Bearer <token>"}
            )
            for i in range(1000)
        ]
        await asyncio.gather(*tasks)
        elapsed = time.time() - start
        print(f"Created 1000 tasks in {elapsed:.2f}s")

asyncio.run(create_tasks())
EOF
```

---

## Phase 6: Rollback Plan (If Needed)

```bash
# 1. Disable Dapr feature flag
helm upgrade todo-app ./phaseV/kubernetes/helm/todo-app \
  --namespace todo-phasev \
  --set backend.env.USE_DAPR=false \
  --set notificationService.env.USE_DAPR=false

# 2. Remove Dapr annotations (rollback deployment)
kubectl rollout undo deployment/backend -n todo-phasev
kubectl rollout undo deployment/notification-service -n todo-phasev

# 3. Verify aiokafka reconnected
kubectl logs -n todo-phasev -l app=backend | grep "aiokafka connected"

# 4. (Optional) Remove Dapr components
kubectl delete component pubsub-kafka -n todo-phasev
kubectl delete component statestore-postgres -n todo-phasev
```

---

## Next Steps

After completing this quickstart:

1. **Generate tasks.md**: Run `/sp.tasks` to break down implementation into actionable tasks
2. **Implement Jobs API**: Replace notification service polling loop with Dapr scheduled jobs
3. **Complete Migration**: Migrate email delivery and recurring task services
4. **Remove aiokafka**: Delete `app/kafka/` module and remove dependency from requirements.txt
5. **Update Documentation**: Create DAPR_GUIDE.md with troubleshooting and operational runbook

## Troubleshooting

**Dapr sidecar not injecting**:
```bash
# Check sidecar injector logs
kubectl logs -n dapr-system -l app=dapr-sidecar-injector

# Verify namespace has sidecar injection enabled
kubectl get namespace todo-phasev -o yaml | grep dapr
```

**Kafka authentication failing**:
```bash
# Check Dapr component logs
kubectl describe component pubsub-kafka -n todo-phasev

# Verify secret exists
kubectl get secret kafka-secrets -n todo-phasev -o yaml
```

**CloudEvents parsing errors**:
```bash
# Enable rawPayload mode in publish metadata (escape hatch)
await dapr_client.publish_event(
    pubsub_name="pubsub-kafka",
    topic="task-events",
    data=event_data,
    metadata={"rawPayload": "true"}  # Disable CloudEvents wrapping
)
```

---

## Summary

This quickstart provides:
- Dapr installation and component setup
- HTTP client wrapper implementation
- Phased migration strategy with feature flags
- End-to-end testing procedures
- Rollback plan for safety

Estimated implementation time: 8-12 hours for full migration across all services.
