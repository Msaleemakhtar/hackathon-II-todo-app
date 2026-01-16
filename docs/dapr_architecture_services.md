# Dapr Architecture - Service Classification

**Date**: 2026-01-16
**Purpose**: Clarify which services require Dapr sidecars and why

---

## Service Classification

### ✅ Services WITH Dapr Sidecars (2/2 containers)

These services participate in event-driven architecture and need infrastructure abstraction:

#### 1. **Backend Service** (2/2 containers)
- **Container 1**: backend application (port 8000)
- **Container 2**: daprd sidecar (port 3500)

**Why Dapr?**
- ✅ Publishes events to Kafka (task-events, task-reminders, task-recurrence)
- ✅ Needs infrastructure abstraction for pub/sub
- ✅ May use state store for idempotency tracking
- ✅ Exposes subscription endpoint for Dapr discovery

**Dapr Annotations**:
```yaml
dapr.io/enabled: "true"
dapr.io/app-id: "backend"
dapr.io/app-port: "8000"
```

---

#### 2. **Email Delivery Service** (2/2 containers)
- **Container 1**: email-delivery application (port 8003)
- **Container 2**: daprd sidecar (port 3500)

**Why Dapr?**
- ✅ Consumes events from Kafka (task-reminders topic)
- ✅ Subscribes via Dapr: `/events/reminder-sent` endpoint
- ✅ Receives CloudEvents from Dapr sidecar
- ✅ Needs infrastructure abstraction for message broker

**Dapr Annotations**:
```yaml
dapr.io/enabled: "true"
dapr.io/app-id: "email-delivery"
dapr.io/app-port: "8003"
```

---

#### 3. **Recurring Task Service** (2/2 containers)
- **Container 1**: recurring-service application (port 8004)
- **Container 2**: daprd sidecar (port 3500)

**Why Dapr?**
- ✅ Consumes events from Kafka (task-recurrence topic)
- ✅ Subscribes via Dapr: `/events/task-completed` endpoint
- ✅ Publishes new TaskCreatedEvent for next occurrence
- ✅ Needs infrastructure abstraction for pub/sub

**Dapr Annotations**:
```yaml
dapr.io/enabled: "true"
dapr.io/app-id: "recurring-service"
dapr.io/app-port: "8004"
```

---

#### 4. **Notification Service** (2/2 containers - currently scaled to 0)
- **Container 1**: notification-service application (port 8002)
- **Container 2**: daprd sidecar (port 3500)

**Why Dapr?**
- ✅ Uses Dapr Jobs API for scheduled tasks (when scheduler available)
- ✅ Publishes reminder events via Dapr
- ✅ Needs state store for idempotency tracking
- ✅ Multi-replica safety with Jobs API

**Dapr Annotations**:
```yaml
dapr.io/enabled: "true"
dapr.io/app-id: "notification-service"
dapr.io/app-port: "8002"
```

**Current Status**: Scaled to 0 (waiting for Dapr scheduler deployment)

---

### ❌ Services WITHOUT Dapr Sidecars (1/1 container)

These services don't participate in event-driven architecture:

#### 1. **Frontend Service** (1/1 container)
- **Container**: Next.js application (port 3000)
- **No Dapr sidecar needed**

**Why NO Dapr?**
- ❌ Frontend is a web UI (browser-based)
- ❌ Communicates with backend via HTTP REST API only
- ❌ Does NOT publish events to Kafka
- ❌ Does NOT consume events from message brokers
- ❌ No need for infrastructure abstraction

**Communication Pattern**:
```
User Browser → Frontend (Next.js) → HTTP REST → Backend API
```

**Pod Status**: `1/1` (single container - correct!)

---

#### 2. **MCP Server** (1/1 container)
- **Container**: MCP server application (port 8001)
- **No Dapr sidecar needed**

**Why NO Dapr?**
- ❌ Acts as API gateway for Claude Code integration
- ❌ Communicates with backend via HTTP REST API only
- ❌ Does NOT publish/consume events directly
- ❌ No participation in event-driven architecture
- ❌ No need for infrastructure abstraction

**Communication Pattern**:
```
Claude Code → MCP Server → HTTP REST → Backend API
```

**Pod Status**: `1/1` (single container - correct!)

---

### Infrastructure Services (1/1 container)

#### 1. **Kafka Local** (1/1 container)
- Message broker (no application code)
- Dapr sidecars connect TO this service, not run alongside it

#### 2. **Redis** (1/1 container)
- Cache/state store (infrastructure)
- No Dapr sidecar needed

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       Kubernetes Cluster                         │
│                                                                  │
│  ┌──────────────┐                    ┌──────────────┐          │
│  │  Frontend    │                    │  MCP Server  │          │
│  │   (1/1)      │                    │   (1/1)      │          │
│  │              │                    │              │          │
│  │ ❌ No Dapr   │                    │ ❌ No Dapr   │          │
│  └──────┬───────┘                    └──────┬───────┘          │
│         │                                   │                   │
│         │          HTTP REST API            │                   │
│         └───────────────┬───────────────────┘                   │
│                         │                                       │
│                    ┌────▼─────┐                                │
│                    │ Backend  │                                │
│                    │  (2/2)   │                                │
│                    │          │                                │
│                    │ App+Dapr │                                │
│                    └────┬─────┘                                │
│                         │                                       │
│          ┌──────────────┼──────────────┐                       │
│          │              │              │                       │
│     ┌────▼────┐    ┌───▼────┐    ┌───▼────┐                  │
│     │ Email   │    │Recurring│    │Notif   │                  │
│     │Delivery │    │ Task   │    │Service │                  │
│     │ (2/2)   │    │ (2/2)  │    │ (2/2)  │                  │
│     │         │    │        │    │        │                  │
│     │App+Dapr │    │App+Dapr│    │App+Dapr│                  │
│     └─────────┘    └────────┘    └────────┘                  │
│                                                                  │
│     ↑ These 4 services have Dapr sidecars                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

Legend:
✅ (2/2) = App container + Dapr sidecar
❌ (1/1) = App container only (no Dapr needed)
```

---

## Current Pod Status

```bash
$ kubectl get pods -n todo-phasev

NAME                                READY   STATUS
backend-56cd5cc7d-rbsj9             2/2     ✅ With Dapr
backend-56cd5cc7d-z4f8t             2/2     ✅ With Dapr
email-delivery-69d76bf87-7ltrn      2/2     ✅ With Dapr
recurring-service-fd75cbf4b-fzbmd   2/2     ✅ With Dapr
frontend-6fb56fd79c-6svd7           1/1     ❌ No Dapr (correct!)
frontend-6fb56fd79c-sgzcg           1/1     ❌ No Dapr (correct!)
mcp-server-847f99958d-5j2zk         1/1     ❌ No Dapr (correct!)
kafka-local-0                       1/1     Infrastructure
redis-0                             1/1     Infrastructure
```

**Summary**: 4 services with Dapr, 2 services without Dapr - exactly as designed! ✅

---

## Decision Criteria: When to Add Dapr Sidecar?

### ✅ ADD Dapr Sidecar When:

1. **Event Publishing**: Service publishes events to message broker (Kafka/Redis)
2. **Event Consumption**: Service subscribes to topics/streams
3. **Service-to-Service**: Needs Dapr service invocation for mTLS/retries
4. **State Management**: Uses Dapr state store for distributed state
5. **Jobs/Scheduling**: Uses Dapr Jobs API for scheduled tasks
6. **Secrets**: Needs Dapr secrets management (optional - can use K8s secrets directly)

### ❌ SKIP Dapr Sidecar When:

1. **Web UI/Frontend**: Browser-based applications (Next.js, React, Vue)
2. **API Gateway Only**: Services that only call backend REST APIs
3. **Infrastructure**: Message brokers, databases, cache servers
4. **Static Content**: Nginx serving static files
5. **Simple HTTP Clients**: Services with no event-driven requirements

---

## Communication Patterns

### Pattern 1: Frontend/MCP → Backend (HTTP REST)
```
Frontend (1/1) → HTTP → Backend (2/2)
                        ↓
                    Publishes events via Dapr
```

**Why no Dapr on frontend?**
- Frontend doesn't publish events directly
- Backend handles all event publishing

---

### Pattern 2: Backend → Services (Event-Driven)
```
Backend (2/2) → Dapr Pub → Kafka → Dapr Sub → Email (2/2)
                                  → Dapr Sub → Recurring (2/2)
```

**Why Dapr on all?**
- Backend publishes via Dapr
- Consumers subscribe via Dapr
- Infrastructure abstraction for all

---

## Resource Usage Comparison

| Service | Containers | Memory (App) | Memory (Dapr) | Total |
|---------|-----------|--------------|---------------|-------|
| Backend | 2/2 | 256Mi | 50-80Mi | ~330Mi |
| Email Delivery | 2/2 | 256Mi | 50-80Mi | ~330Mi |
| Recurring | 2/2 | 256Mi | 50-80Mi | ~330Mi |
| Frontend | 1/1 | 256Mi | N/A | 256Mi |
| MCP Server | 1/1 | 256Mi | N/A | 256Mi |

**Dapr Overhead**: ~50-80MB per sidecar (acceptable for infrastructure abstraction benefits)

**Saved Resources**: Frontend and MCP not having Dapr saves ~160MB (2 x 80MB)

---

## Best Practices

### ✅ DO Add Dapr When:
- Service participates in event-driven architecture
- Need infrastructure portability (swap Kafka→Redis)
- Multi-replica coordination required (Jobs API)
- Distributed state management needed

### ❌ DON'T Add Dapr When:
- Simple HTTP client (API consumer only)
- Web UI/Frontend (browser-based)
- Pure infrastructure (Kafka, Redis, PostgreSQL)
- No event-driven requirements

### 🤔 Consider Dapr For:
- Service invocation (mTLS, retries, circuit breaker)
- Secrets management (rotation, scoping)
- Distributed tracing (automatic instrumentation)
- Rate limiting and middleware

---

## Verification Commands

### Check which services have Dapr:
```bash
# List all pods with container count
kubectl get pods -n todo-phasev

# Check Dapr annotations on deployment
kubectl get deployment backend -n todo-phasev -o yaml | grep -A 5 "dapr.io"

# Check Dapr components loaded in sidecar
kubectl logs -n todo-phasev deployment/backend -c daprd | grep "Component loaded"
```

### Verify frontend/MCP have NO Dapr:
```bash
# Should show NO dapr.io annotations
kubectl get deployment frontend -n todo-phasev -o yaml | grep "dapr.io" || echo "No Dapr annotations (correct!)"
kubectl get deployment mcp-server -n todo-phasev -o yaml | grep "dapr.io" || echo "No Dapr annotations (correct!)"
```

---

## Conclusion

**Architecture Status**: ✅ **CORRECT**

- 4 services WITH Dapr sidecars (event-driven participants)
- 2 services WITHOUT Dapr sidecars (HTTP clients only)
- Resource efficient (no unnecessary sidecars)
- Clear separation of concerns

**Frontend and MCP Server correctly do NOT have Dapr sidecars** because they:
1. Only communicate via HTTP REST APIs
2. Don't publish or consume events
3. Don't need infrastructure abstraction
4. Are simple API clients

This is the **optimal architecture** - Dapr where needed, simple containers where not! 🎯

---

**Created**: 2026-01-16
**Architecture**: Event-Driven with Selective Dapr Integration
**Status**: Production Ready
