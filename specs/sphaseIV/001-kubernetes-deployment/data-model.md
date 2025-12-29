# Data Model: Kubernetes Resources for Phase IV Deployment

**Feature**: 001-kubernetes-deployment
**Date**: 2025-12-26
**Phase**: 1 (Design & Contracts)

## Overview

This data model defines the Kubernetes resource entities required for Phase IV deployment. Unlike traditional application data models (database tables), this model describes infrastructure-as-code entities that orchestrate the Phase III Todo Chatbot in Kubernetes.

---

## Entity Catalog

### 1. Namespace

**Kind**: `Namespace`
**Purpose**: Isolate all Phase IV resources in dedicated namespace

| Field | Type | Value | Description |
|-------|------|-------|-------------|
| metadata.name | string | `todo-phaseiv` | Namespace name (constitutional requirement) |
| metadata.labels | map | `phase: iv`, `app: todo-chatbot` | Resource labels for organization |

**State Transitions**: Created once during helm install, deleted on helm uninstall

**Validation Rules**:
- Name MUST be `todo-phaseiv` per constitutional namespace requirement
- Namespace MUST be created before all other resources

---

### 2. Deployment Entities

#### 2.1 Frontend Deployment

**Kind**: `Deployment`
**Purpose**: Manage Frontend (Next.js) pod replicas

| Field | Type | Value/Range | Description |
|-------|------|-------------|-------------|
| metadata.name | string | `frontend` | Deployment name |
| spec.replicas | integer | 2 (initial) | Starting replica count (HPA manages dynamically) |
| spec.selector.matchLabels | map | `app: frontend` | Pod selector |
| spec.template.metadata.labels | map | `app: frontend`, `version: v1` | Pod labels |
| spec.template.spec.containers[0].name | string | `frontend` | Container name |
| spec.template.spec.containers[0].image | string | `todo-frontend:latest` | Docker image (built locally in Minikube) |
| spec.template.spec.containers[0].imagePullPolicy | string | `IfNotPresent` | Avoid pulling if image exists locally |
| spec.template.spec.containers[0].ports[0].containerPort | integer | 3000 | Next.js server port |
| spec.template.spec.containers[0].env | array | ConfigMap + Secret refs | Environment variables |
| spec.template.spec.containers[0].resources.requests.cpu | string | `500m` | Minimum CPU (0.5 cores) |
| spec.template.spec.containers[0].resources.requests.memory | string | `512Mi` | Minimum RAM |
| spec.template.spec.containers[0].resources.limits.cpu | string | `1000m` | Maximum CPU (1.0 cores) |
| spec.template.spec.containers[0].resources.limits.memory | string | `1024Mi` | Maximum RAM (1GB) |
| spec.template.spec.containers[0].livenessProbe | object | HTTP GET /health:3000 | Restart on failure |
| spec.template.spec.containers[0].readinessProbe | object | HTTP GET /health:3000 | Route traffic when ready |

**Relationships**:
- Managed by: `HorizontalPodAutoscaler/frontend-hpa`
- Exposes via: `Service/frontend-service`
- Depends on: `ConfigMap/todo-app-config`, `Secret/todo-app-secrets`

**State Transitions**:
- Created → Scaling Up (HPA detects high CPU) → Scaled (5 replicas)
- Scaled → Scaling Down (HPA detects low CPU after stabilization) → Created (2 replicas)

#### 2.2 Backend Deployment

**Kind**: `Deployment`
**Purpose**: Manage Backend (FastAPI) pod replicas

| Field | Type | Value/Range | Description |
|-------|------|-------------|-------------|
| metadata.name | string | `backend` | Deployment name |
| spec.replicas | integer | 2 (initial) | Starting replica count (HPA manages dynamically) |
| spec.template.spec.containers[0].image | string | `todo-backend:latest` | Docker image (built locally in Minikube) |
| spec.template.spec.containers[0].ports[0].containerPort | integer | 8000 | FastAPI + Uvicorn port |
| spec.template.spec.containers[0].resources.requests.cpu | string | `500m` | Minimum CPU (0.5 cores) |
| spec.template.spec.containers[0].resources.requests.memory | string | `512Mi` | Minimum RAM |
| spec.template.spec.containers[0].resources.limits.cpu | string | `1000m` | Maximum CPU (1.0 cores) |
| spec.template.spec.containers[0].resources.limits.memory | string | `1024Mi` | Maximum RAM (1GB) |
| spec.template.spec.containers[0].livenessProbe | object | HTTP GET /health:8000 | Restart on failure |
| spec.template.spec.containers[0].readinessProbe | object | HTTP GET /health:8000 | Route traffic when ready |

**Relationships**:
- Managed by: `HorizontalPodAutoscaler/backend-hpa`
- Exposes via: `Service/backend-service`
- Depends on: `ConfigMap/todo-app-config`, `Secret/todo-app-secrets`, `Service/redis-service`, External Neon PostgreSQL

**State Transitions**: Same as Frontend Deployment

#### 2.3 MCP Server Deployment

**Kind**: `Deployment`
**Purpose**: Manage MCP Server (FastMCP) pod

| Field | Type | Value/Range | Description |
|-------|------|-------------|-------------|
| metadata.name | string | `mcp-server` | Deployment name |
| spec.replicas | integer | 1 (fixed) | Single replica (no autoscaling) |
| spec.template.spec.containers[0].image | string | `todo-backend:latest` | Reuses backend image (different entrypoint) |
| spec.template.spec.containers[0].command | array | Custom MCP server start command | Override entrypoint for MCP server |
| spec.template.spec.containers[0].ports[0].containerPort | integer | 8001 | MCP HTTP server port |
| spec.template.spec.containers[0].resources.requests.cpu | string | `250m` | Minimum CPU (0.25 cores) |
| spec.template.spec.containers[0].resources.requests.memory | string | `256Mi` | Minimum RAM |
| spec.template.spec.containers[0].resources.limits.cpu | string | `500m` | Maximum CPU (0.5 cores) |
| spec.template.spec.containers[0].resources.limits.memory | string | `512Mi` | Maximum RAM |
| spec.template.spec.containers[0].livenessProbe | object | HTTP GET /health:8001 | Restart on failure |
| spec.template.spec.containers[0].readinessProbe | object | HTTP GET /health:8001 | Route traffic when ready |

**Relationships**:
- Exposes via: `Service/mcp-service`
- Depends on: `ConfigMap/todo-app-config`, `Secret/todo-app-secrets`, `Service/redis-service`

**State Transitions**: Single replica (no autoscaling), recreated on pod deletion

---

### 3. StatefulSet Entity

#### 3.1 Redis StatefulSet

**Kind**: `StatefulSet`
**Purpose**: Manage Redis pod with stable network identity and persistent storage

| Field | Type | Value/Range | Description |
|-------|------|-------------|-------------|
| metadata.name | string | `redis` | StatefulSet name |
| spec.serviceName | string | `redis-service` | Headless service for stable DNS |
| spec.replicas | integer | 1 (fixed) | Single replica (no clustering) |
| spec.template.spec.containers[0].name | string | `redis` | Container name |
| spec.template.spec.containers[0].image | string | `redis:7-alpine` | Official Redis 7 Alpine image |
| spec.template.spec.containers[0].command | array | `["redis-server", "--appendonly", "yes"]` | Enable AOF persistence |
| spec.template.spec.containers[0].ports[0].containerPort | integer | 6379 | Redis default port |
| spec.template.spec.containers[0].volumeMounts[0].name | string | `redis-data` | PVC mount name |
| spec.template.spec.containers[0].volumeMounts[0].mountPath | string | `/data` | Redis data directory |
| spec.template.spec.containers[0].resources.requests.cpu | string | `250m` | Minimum CPU (0.25 cores) |
| spec.template.spec.containers[0].resources.requests.memory | string | `128Mi` | Minimum RAM |
| spec.template.spec.containers[0].resources.limits.cpu | string | `500m` | Maximum CPU (0.5 cores) |
| spec.template.spec.containers[0].resources.limits.memory | string | `256Mi` | Maximum RAM |
| spec.template.spec.containers[0].livenessProbe | object | exec: `redis-cli ping` | Restart on failure |
| spec.template.spec.containers[0].readinessProbe | object | exec: `redis-cli ping` | Route traffic when ready |
| spec.volumeClaimTemplates[0].metadata.name | string | `redis-data` | PVC template name |
| spec.volumeClaimTemplates[0].spec.accessModes | array | `["ReadWriteOnce"]` | RWO access mode |
| spec.volumeClaimTemplates[0].spec.storageClassName | string | `standard` | Minikube default StorageClass |
| spec.volumeClaimTemplates[0].spec.resources.requests.storage | string | `1Gi` | 1GB persistent storage |

**Relationships**:
- Exposes via: `Service/redis-service`
- Creates: `PersistentVolumeClaim/redis-data-redis-0` (automatically created by StatefulSet)

**State Transitions**:
- Created → Running → Terminated (kubectl delete pod redis-0)
- Terminated → Recreating (Kubernetes auto-restart) → Running (PVC reattached, data retained)

**Validation Rules**:
- Pod name MUST be `redis-0` (stable identity)
- PVC MUST be bound before pod starts
- Data MUST persist across pod deletion/recreation

---

### 4. Service Entities

#### 4.1 Frontend Service

**Kind**: `Service`
**Purpose**: Expose Frontend pods via ClusterIP for internal routing

| Field | Type | Value | Description |
|-------|------|-------|-------------|
| metadata.name | string | `frontend-service` | Service name |
| spec.type | string | `ClusterIP` | Internal cluster IP (not exposed externally) |
| spec.selector | map | `app: frontend` | Pods to route traffic to |
| spec.ports[0].protocol | string | `TCP` | TCP protocol |
| spec.ports[0].port | integer | 3000 | Service port |
| spec.ports[0].targetPort | integer | 3000 | Container port |

**Relationships**:
- Routes to: `Deployment/frontend` pods
- Exposed via: `Ingress/todo-app-ingress` (path: /)

**State Transitions**: Stable (no state changes)

#### 4.2 Backend Service

**Kind**: `Service`
**Purpose**: Expose Backend pods via ClusterIP for internal routing

| Field | Type | Value | Description |
|-------|------|-------|-------------|
| metadata.name | string | `backend-service` | Service name |
| spec.type | string | `ClusterIP` | Internal cluster IP |
| spec.selector | map | `app: backend` | Pods to route traffic to |
| spec.ports[0].port | integer | 8000 | Service port |
| spec.ports[0].targetPort | integer | 8000 | Container port |

**Relationships**:
- Routes to: `Deployment/backend` pods
- Exposed via: `Ingress/todo-app-ingress` (path: /api)

**State Transitions**: Stable (no state changes)

#### 4.3 MCP Service

**Kind**: `Service`
**Purpose**: Expose MCP Server pod via ClusterIP for internal routing

| Field | Type | Value | Description |
|-------|------|-------|-------------|
| metadata.name | string | `mcp-service` | Service name |
| spec.type | string | `ClusterIP` | Internal cluster IP |
| spec.selector | map | `app: mcp-server` | Pods to route traffic to |
| spec.ports[0].port | integer | 8001 | Service port |
| spec.ports[0].targetPort | integer | 8001 | Container port |

**Relationships**:
- Routes to: `Deployment/mcp-server` pod
- Used by: `Deployment/backend` (Backend calls MCP Server for tool invocations)

**State Transitions**: Stable (no state changes)

#### 4.4 Redis Service

**Kind**: `Service`
**Purpose**: Expose Redis StatefulSet via ClusterIP for internal routing

| Field | Type | Value | Description |
|-------|------|-------|-------------|
| metadata.name | string | `redis-service` | Service name |
| spec.type | string | `ClusterIP` | Internal cluster IP |
| spec.clusterIP | string | `None` (headless) | No cluster IP (direct pod DNS) |
| spec.selector | map | `app: redis` | Pods to route traffic to |
| spec.ports[0].port | integer | 6379 | Service port |
| spec.ports[0].targetPort | integer | 6379 | Container port |

**Relationships**:
- Routes to: `StatefulSet/redis` pod
- Used by: `Deployment/backend`, `Deployment/mcp-server`

**State Transitions**: Stable (no state changes)

**Headless Service**: clusterIP: None enables direct pod DNS (`redis-0.redis-service.todo-phaseiv.svc.cluster.local`)

---

### 5. Ingress Entity

#### 5.1 Todo App Ingress

**Kind**: `Ingress`
**Purpose**: Route external HTTP traffic to Frontend and Backend services

| Field | Type | Value | Description |
|-------|------|-------|-------------|
| metadata.name | string | `todo-app-ingress` | Ingress name |
| metadata.annotations | map | `nginx.ingress.kubernetes.io/rewrite-target: /` | Nginx Ingress configuration |
| spec.ingressClassName | string | `nginx` | Use Nginx Ingress Controller |
| spec.rules[0].host | string | `todo-app.local` | Hostname for routing |
| spec.rules[0].http.paths[0].path | string | `/api` | API path (MUST come first) |
| spec.rules[0].http.paths[0].pathType | string | `Prefix` | Prefix matching |
| spec.rules[0].http.paths[0].backend.service.name | string | `backend-service` | Route to Backend service |
| spec.rules[0].http.paths[0].backend.service.port.number | integer | 8000 | Backend service port |
| spec.rules[0].http.paths[1].path | string | `/` | Frontend path (MUST come second) |
| spec.rules[0].http.paths[1].pathType | string | `Prefix` | Prefix matching |
| spec.rules[0].http.paths[1].backend.service.name | string | `frontend-service` | Route to Frontend service |
| spec.rules[0].http.paths[1].backend.service.port.number | integer | 3000 | Frontend service port |

**Relationships**:
- Routes to: `Service/backend-service` (path: /api), `Service/frontend-service` (path: /)
- Requires: Nginx Ingress Controller enabled in Minikube

**State Transitions**:
- Created → Pending (waiting for Ingress Controller to allocate IP)
- Pending → Active (IP allocated, routing functional)

**Validation Rules**:
- Path `/api` MUST be listed before `/` to ensure API requests don't route to frontend
- Host `todo-app.local` MUST be added to /etc/hosts pointing to Minikube IP

---

### 6. HorizontalPodAutoscaler Entities

#### 6.1 Frontend HPA

**Kind**: `HorizontalPodAutoscaler`
**Purpose**: Autoscale Frontend deployment based on CPU utilization

| Field | Type | Value | Description |
|-------|------|-------|-------------|
| metadata.name | string | `frontend-hpa` | HPA name |
| spec.scaleTargetRef.kind | string | `Deployment` | Target resource kind |
| spec.scaleTargetRef.name | string | `frontend` | Target deployment |
| spec.minReplicas | integer | 2 | Minimum replicas |
| spec.maxReplicas | integer | 5 | Maximum replicas |
| spec.metrics[0].type | string | `Resource` | Metric type |
| spec.metrics[0].resource.name | string | `cpu` | CPU metric |
| spec.metrics[0].resource.target.type | string | `Utilization` | Percentage-based target |
| spec.metrics[0].resource.target.averageUtilization | integer | 70 | 70% CPU threshold |
| spec.behavior.scaleDown.stabilizationWindowSeconds | integer | 300 | 5 min stabilization before scale-down |
| spec.behavior.scaleUp.stabilizationWindowSeconds | integer | 0 | Immediate scale-up |

**Relationships**:
- Manages: `Deployment/frontend`
- Requires: Metrics Server enabled in Minikube

**State Transitions**:
- Idle (2 replicas) → Scaling Up (CPU > 70%) → Scaled (3-5 replicas)
- Scaled (5 replicas) → Stabilizing (CPU < 70% for 5 min) → Scaling Down → Idle (2 replicas)

#### 6.2 Backend HPA

**Kind**: `HorizontalPodAutoscaler`
**Purpose**: Autoscale Backend deployment based on CPU and memory utilization

| Field | Type | Value | Description |
|-------|------|-------|-------------|
| metadata.name | string | `backend-hpa` | HPA name |
| spec.scaleTargetRef.name | string | `backend` | Target deployment |
| spec.minReplicas | integer | 2 | Minimum replicas |
| spec.maxReplicas | integer | 5 | Maximum replicas |
| spec.metrics[0].resource.name | string | `cpu` | CPU metric |
| spec.metrics[0].resource.target.averageUtilization | integer | 70 | 70% CPU threshold |
| spec.metrics[1].resource.name | string | `memory` | Memory metric |
| spec.metrics[1].resource.target.averageUtilization | integer | 80 | 80% memory threshold |

**Relationships**:
- Manages: `Deployment/backend`
- Requires: Metrics Server enabled in Minikube

**State Transitions**: Same as Frontend HPA (scales when CPU > 70% OR memory > 80%)

---

### 7. ConfigMap Entity

#### 7.1 Todo App ConfigMap

**Kind**: `ConfigMap`
**Purpose**: Store non-sensitive configuration as environment variables

| Field | Type | Value | Description |
|-------|------|-------|-------------|
| metadata.name | string | `todo-app-config` | ConfigMap name |
| data.REDIS_HOST | string | `redis-service.todo-phaseiv.svc.cluster.local` | Redis service DNS |
| data.REDIS_PORT | string | `6379` | Redis port |
| data.MCP_SERVER_URL | string | `http://mcp-service.todo-phaseiv.svc.cluster.local:8001` | MCP Server URL |
| data.NEXT_PUBLIC_API_URL | string | `http://todo-app.local/api` | Frontend API base URL |

**Relationships**:
- Used by: `Deployment/frontend`, `Deployment/backend`, `Deployment/mcp-server`

**State Transitions**: Stable (updated via `helm upgrade` for config changes)

**Validation Rules**:
- MUST NOT contain sensitive data (use Secret for credentials)
- MUST use fully-qualified DNS names for service discovery

---

### 8. Secret Entity

#### 8.1 Todo App Secrets

**Kind**: `Secret`
**Purpose**: Store sensitive configuration (database credentials, API keys)

| Field | Type | Value | Description |
|-------|------|-------|-------------|
| metadata.name | string | `todo-app-secrets` | Secret name |
| type | string | `Opaque` | Generic secret type |
| data.DATABASE_URL | string (base64) | `<base64-encoded-neon-postgres-url>` | Neon PostgreSQL connection string |
| data.OPENAI_API_KEY | string (base64) | `<base64-encoded-api-key>` | OpenAI API key |
| data.BETTER_AUTH_SECRET | string (base64) | `<base64-encoded-secret>` | Better Auth shared secret |
| data.BETTER_AUTH_URL | string (base64) | `<base64-encoded-url>` | Better Auth URL |
| data.REDIS_PASSWORD | string (base64) | `<base64-encoded-password>` | Redis password (optional) |

**Relationships**:
- Used by: `Deployment/frontend`, `Deployment/backend`, `Deployment/mcp-server`

**State Transitions**: Stable (updated via `kubectl create secret` for credential rotation)

**Validation Rules**:
- All values MUST be base64-encoded (Kubernetes API requirement)
- MUST NOT be committed to git (use .gitignore for values.yaml with secrets)
- Production: Use external secret management (deferred to Phase V)

---

## Entity Relationship Diagram (ASCII)

```
┌──────────────────────────────────────────────────────────────────┐
│                        Namespace: todo-phaseiv                   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Ingress (todo-app-ingress)             │   │
│  │               host: todo-app.local                        │   │
│  │         paths: /api → backend-service                     │   │
│  │                / → frontend-service                       │   │
│  └──────────┬───────────────────────────────┬────────────────┘   │
│             │                               │                    │
│             ▼                               ▼                    │
│  ┌──────────────────┐            ┌──────────────────┐           │
│  │ Service          │            │ Service          │           │
│  │ backend-service  │            │ frontend-service │           │
│  │ ClusterIP:8000   │            │ ClusterIP:3000   │           │
│  └────────┬─────────┘            └────────┬─────────┘           │
│           │                               │                     │
│           │                               │                     │
│  ┌────────▼─────────┐            ┌────────▼─────────┐           │
│  │ HPA              │            │ HPA              │           │
│  │ backend-hpa      │            │ frontend-hpa     │           │
│  │ min:2 max:5      │            │ min:2 max:5      │           │
│  │ CPU:70% MEM:80%  │            │ CPU:70%          │           │
│  └────────┬─────────┘            └────────┬─────────┘           │
│           │ manages                       │ manages             │
│           ▼                               ▼                     │
│  ┌────────────────────┐         ┌────────────────────┐          │
│  │ Deployment         │         │ Deployment         │          │
│  │ backend            │         │ frontend           │          │
│  │ replicas: 2-5      │         │ replicas: 2-5      │          │
│  │ image: backend     │         │ image: frontend    │          │
│  │ resources: 500m-1G │         │ resources: 500m-1G │          │
│  └──────┬─────────────┘         └────────────────────┘          │
│         │                                                        │
│         │ depends on                                            │
│         ├──────────┬─────────────┐                              │
│         ▼          ▼             ▼                              │
│  ┌─────────────┐ ┌────────────┐ ┌─────────────────┐            │
│  │ Service     │ │ Service    │ │ ConfigMap       │            │
│  │ mcp-service │ │ redis-svc  │ │ todo-app-config │            │
│  │ ClusterIP   │ │ Headless   │ │ REDIS_HOST      │            │
│  │ :8001       │ │ :6379      │ │ MCP_SERVER_URL  │            │
│  └──────┬──────┘ └──────┬─────┘ └─────────────────┘            │
│         │               │                                       │
│         ▼               ▼                                       │
│  ┌─────────────┐ ┌────────────────┐                            │
│  │ Deployment  │ │ StatefulSet    │                            │
│  │ mcp-server  │ │ redis          │                            │
│  │ replicas: 1 │ │ replicas: 1    │                            │
│  │ resources:  │ │ resources:     │                            │
│  │ 250m-512Mi  │ │ 250m-256Mi     │                            │
│  └─────────────┘ └────────┬───────┘                            │
│                           │ volumeMounts                        │
│                           ▼                                     │
│                  ┌────────────────────┐                         │
│                  │ PersistentVolume   │                         │
│                  │ redis-data-redis-0 │                         │
│                  │ 1Gi, RWO           │                         │
│                  │ standard SC        │                         │
│                  └────────────────────┘                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     Secret (todo-app-secrets)            │  │
│  │  DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET        │  │
│  │  (injected as env vars into all deployments)             │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘

External:
┌─────────────────────────────────────────────────────────────┐
│ Neon PostgreSQL (DATABASE_URL from Secret)                  │
│ Shared with Phase III (tasks_phaseiii, conversations, msgs) │
└─────────────────────────────────────────────────────────────┘
```

---

## Validation and Constraints

### Resource Naming Constraints
- All resource names MUST use lowercase alphanumeric characters and hyphens only
- Namespace MUST be `todo-phaseiv` (constitutional requirement)
- Labels MUST follow `app.kubernetes.io/*` recommended labels

### Resource Limits Constraints
- All containers MUST define CPU requests and limits
- All containers MUST define memory requests and limits
- QoS class MUST be Burstable or Guaranteed (not BestEffort)

### Security Constraints
- Secrets MUST use base64 encoding (Kubernetes API requirement)
- Secrets MUST NOT be committed to git
- ConfigMaps MUST NOT contain sensitive data

### Dependency Constraints
- Backend Deployment MUST start after Redis StatefulSet is Ready
- Frontend Deployment MUST start after Backend Deployment is Ready
- Ingress MUST be created after all Services exist

### Storage Constraints
- Redis PVC MUST use RWO (ReadWriteOnce) access mode
- Redis PVC MUST use standard StorageClass (Minikube default)
- Redis PVC MUST request 1Gi capacity

---

## Data Integrity and State Management

### Pod Lifecycle
- **Deployments**: Kubernetes recreates pods on failure (self-healing)
- **StatefulSets**: Kubernetes recreates pods with same network identity and PVC reattachment
- **HPA**: Dynamically adjusts replica count based on metrics

### Data Persistence
- **Redis**: Data persists in PVC across pod deletion/recreation
- **Application State**: Stored in external Neon PostgreSQL (not affected by Kubernetes pod lifecycle)
- **Configuration**: Stored in ConfigMap and Secret (updated via `helm upgrade`)

### Scaling Behavior
- **Frontend/Backend**: HPA scales based on CPU/memory metrics (2-5 replicas)
- **MCP Server**: Fixed 1 replica (no autoscaling)
- **Redis**: Fixed 1 replica (no autoscaling, no clustering)

---

## Summary

This data model defines 14 Kubernetes resource entities across 8 categories:
1. Namespace (1): Isolation boundary
2. Deployments (3): Frontend, Backend, MCP Server
3. StatefulSet (1): Redis with persistent storage
4. Services (4): ClusterIP routing for all services
5. Ingress (1): HTTP routing to Frontend and Backend
6. HorizontalPodAutoscalers (2): CPU/memory-based autoscaling
7. ConfigMap (1): Non-sensitive configuration
8. Secret (1): Sensitive credentials

All entities follow Kubernetes best practices, constitutional requirements, and research outcomes from Phase 0.
