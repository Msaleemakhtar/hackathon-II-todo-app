# Research: Kubernetes Deployment for Phase IV Todo Chatbot

**Feature**: 001-kubernetes-deployment
**Date**: 2025-12-26
**Phase**: 0 (Outline & Research)

## Purpose

This research document resolves all NEEDS CLARIFICATION items from the Technical Context and establishes best practices for deploying Phase III Todo Chatbot to Kubernetes using Minikube, Helm charts, Nginx Ingress, Horizontal Pod Autoscaling, and PersistentVolumes.

---

## Research Areas

### 1. Helm Chart Structure and Best Practices

**Decision**: Use Helm 3 semantic release chart with standard template organization

**Rationale**:
- Helm 3 removes Tiller, simplifying security and reducing cluster footprint
- Standard template structure (`templates/`, `values.yaml`, `Chart.yaml`) ensures maintainability
- Named templates in `_helpers.tpl` promote DRY principles across manifests
- Helm hooks enable pre-install/pre-upgrade validations

**Best Practices Applied**:
- Chart.yaml includes apiVersion: v2, name, version (SemVer), appVersion, description
- values.yaml externalizes all environment-specific configuration
- Templates use `{{ .Values.* }}` placeholders for runtime substitution
- Resource names use `{{ include "todo-app.fullname" . }}` helper for consistency
- Labels follow Kubernetes recommended labels (app.kubernetes.io/*)
- Secrets encoded in values.yaml as base64 strings (not committed to git)

**Alternatives Considered**:
- Kustomize: Rejected - less flexible for multi-environment templating
- Raw kubectl apply: Rejected - no version management or rollback capability
- ArgoCD/FluxCD: Out of scope for Phase IV (deferred to Phase V)

**References**:
- Helm Best Practices: https://helm.sh/docs/chart_best_practices/
- Helm Template Guide: https://helm.sh/docs/chart_template_guide/

---

### 2. Nginx Ingress Controller Configuration

**Decision**: Use official Nginx Ingress Controller with path-based routing

**Rationale**:
- Most widely adopted Ingress controller in Kubernetes ecosystem
- Native support in Minikube via `minikube addons enable ingress`
- Supports path-based routing required for frontend (/) and backend (/api)
- Annotation-based configuration for CORS, rate limiting, timeouts

**Configuration Strategy**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"  # For local dev
spec:
  ingressClassName: nginx
  rules:
  - host: todo-app.local
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 3000
```

**Path Ordering**: /api MUST come before / to ensure API requests don't route to frontend

**DNS Configuration**: /etc/hosts entry `<minikube-ip> todo-app.local` required for local access

**Alternatives Considered**:
- Traefik: Rejected - less documentation for Minikube integration
- HAProxy Ingress: Rejected - smaller community support
- Istio Gateway: Out of scope - service mesh complexity exceeds Phase IV requirements

**References**:
- Nginx Ingress Docs: https://kubernetes.github.io/ingress-nginx/
- Minikube Ingress Addon: https://minikube.sigs.k8s.io/docs/handbook/addons/ingress-dns/

---

### 3. Horizontal Pod Autoscaling (HPA) Configuration

**Decision**: CPU-based HPA for frontend, CPU + Memory HPA for backend

**Rationale**:
- Metrics Server provides CPU/memory metrics without external dependencies
- Frontend (Next.js) CPU-bound during SSR; memory footprint stable
- Backend (FastAPI + Uvicorn) CPU-bound for request processing, memory increases with connection pools
- 70% CPU threshold provides headroom before scaling (industry standard)
- 80% memory threshold prevents OOMKilled events

**HPA Specification**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend
  minReplicas: 2
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 5 minutes before scale-down
      policies:
      - type: Pods
        value: 1
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0  # Immediate scale-up
      policies:
      - type: Pods
        value: 2
        periodSeconds: 60
```

**Metrics Server Requirement**: `minikube addons enable metrics-server` required for HPA functionality

**Alternatives Considered**:
- Custom metrics (request latency, queue depth): Deferred to Phase V - requires Prometheus
- Vertical Pod Autoscaler (VPA): Out of scope - resource sizing manual for MVP
- KEDA (event-driven autoscaling): Out of scope - no event sources in Phase IV

**References**:
- HPA v2 API: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- Metrics Server: https://github.com/kubernetes-sigs/metrics-server

---

### 4. PersistentVolume and StatefulSet for Redis

**Decision**: StatefulSet with PersistentVolumeClaim for Redis data persistence

**Rationale**:
- StatefulSet provides stable network identity (redis-0) and ordered deployment
- PVC ensures data survives pod deletion/recreation
- Minikube default StorageClass (standard) uses hostPath provisioner (suitable for local dev)
- RWO (ReadWriteOnce) access mode sufficient for single Redis replica

**StatefulSet + PVC Pattern**:
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
spec:
  serviceName: redis-service
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command: ["redis-server", "--appendonly", "yes"]
        volumeMounts:
        - name: redis-data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: redis-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: standard
      resources:
        requests:
          storage: 1Gi
```

**AOF Persistence**: `--appendonly yes` enables Append-Only File for durability

**Alternatives Considered**:
- Deployment with PVC: Rejected - no stable pod name, complicates DNS
- Redis Operator: Out of scope - excessive for single-replica local deployment
- EmptyDir volume: Rejected - data lost on pod deletion (violates persistence requirement)

**References**:
- StatefulSet Basics: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
- PersistentVolumes: https://kubernetes.io/docs/concepts/storage/persistent-volumes/

---

### 5. Health Probes (Liveness and Readiness)

**Decision**: HTTP GET probes for frontend/backend/mcp, exec probes for Redis

**Rationale**:
- HTTP GET probes leverage existing /health endpoints in FastAPI and Next.js
- exec probe (`redis-cli ping`) validates Redis process health without HTTP overhead
- Liveness probes detect crashed containers and trigger restarts
- Readiness probes prevent traffic routing to unhealthy pods during startup
- initialDelaySeconds: 10 allows services to initialize before first probe
- failureThreshold: 3 prevents flapping from transient failures

**Probe Configuration**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

**Redis Probe**:
```yaml
livenessProbe:
  exec:
    command:
    - redis-cli
    - ping
  initialDelaySeconds: 10
  periodSeconds: 10
```

**Alternatives Considered**:
- TCP socket probes: Rejected - less informative than HTTP 200 or exec command
- Startup probes: Not needed - services have fast startup times (<10s)
- gRPC probes: Not applicable - no gRPC services in Phase IV

**References**:
- Configure Liveness/Readiness Probes: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

---

### 6. Resource Requests and Limits

**Decision**: Define requests and limits for all containers to ensure Burstable QoS

**Rationale**:
- Requests guarantee minimum resources; limits cap maximum usage
- Burstable QoS class (requests < limits) allows burst capacity while preventing resource hogging
- Values based on Phase III Docker Compose resource constraints for consistency
- HPA uses CPU requests as scaling baseline (70% of request triggers scale-up)

**Resource Specification**:
```yaml
resources:
  requests:
    cpu: 500m      # 0.5 CPU cores
    memory: 512Mi
  limits:
    cpu: 1000m     # 1.0 CPU cores
    memory: 1024Mi
```

**Sizing Rationale**:
- **Frontend**: Next.js SSR requires 512Mi-1Gi RAM; 1 CPU handles typical load
- **Backend**: FastAPI + Uvicorn async I/O requires 512Mi-1Gi RAM; 1 CPU sufficient
- **MCP Server**: Lightweight FastMCP requires 256Mi-512Mi RAM; 0.5 CPU adequate
- **Redis**: In-memory cache requires 128Mi-256Mi RAM; 0.5 CPU sufficient

**QoS Classes**:
- **Guaranteed**: requests == limits (highest priority, least likely to be evicted)
- **Burstable**: requests < limits (medium priority, can burst above requests)
- **BestEffort**: no requests/limits (lowest priority, first to be evicted)

Phase IV uses Burstable for all services to allow burst capacity under load while preventing cluster overcommitment.

**Alternatives Considered**:
- Guaranteed QoS: Rejected - wastes resources when services are idle
- BestEffort QoS: Rejected - violates constitutional resource limits requirement
- VPA (Vertical Pod Autoscaler): Deferred to Phase V - manual sizing acceptable for MVP

**References**:
- Resource Management: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- QoS Classes: https://kubernetes.io/docs/tasks/configure-pod-container/quality-service-pod/

---

### 7. Secrets Management

**Decision**: Kubernetes Secrets with base64 encoding, values provided via Helm values.yaml

**Rationale**:
- Kubernetes Secrets separate sensitive data from container images and manifests
- Base64 encoding required by Kubernetes API (not encryption - just encoding)
- Helm values.yaml allows external secret injection without modifying templates
- secretKeyRef in Deployment manifests injects secrets as environment variables

**Secret Specification**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-app-secrets
type: Opaque
data:
  DATABASE_URL: {{ .Values.secrets.databaseUrl | b64enc | quote }}
  OPENAI_API_KEY: {{ .Values.secrets.openaiApiKey | b64enc | quote }}
  BETTER_AUTH_SECRET: {{ .Values.secrets.betterAuthSecret | b64enc | quote }}
  BETTER_AUTH_URL: {{ .Values.secrets.betterAuthUrl | b64enc | quote }}
  REDIS_PASSWORD: {{ .Values.secrets.redisPassword | b64enc | quote }}
```

**Injection Pattern**:
```yaml
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: todo-app-secrets
      key: DATABASE_URL
```

**Security Considerations**:
- Secrets MUST NOT be committed to git (use .gitignore for values.yaml with secrets)
- Production: Use external secret management (HashiCorp Vault, AWS Secrets Manager) - deferred to Phase V
- Local dev: Secrets stored in values.yaml locally, not pushed to repository

**Alternatives Considered**:
- Sealed Secrets: Deferred to Phase V - requires additional operator
- External Secrets Operator: Deferred to Phase V - cloud integration out of scope
- ConfigMap for secrets: REJECTED - violates constitutional security requirement (Secrets vs ConfigMaps distinction mandatory)

**References**:
- Kubernetes Secrets: https://kubernetes.io/docs/concepts/configuration/secret/
- Secrets Best Practices: https://kubernetes.io/docs/concepts/security/secrets-good-practices/

---

### 8. Incremental Deployment Strategy

**Decision**: Sequential rollout in dependency order with health validation gates

**Rationale**:
- Services have dependencies: Backend requires Redis and PostgreSQL; Frontend requires Backend
- Sequential deployment prevents startup failures from missing dependencies
- Health validation gates ensure each service is Ready before deploying dependent services
- Helm install --wait flag waits for all pods to be Ready before returning success

**Deployment Order**:
1. **Redis StatefulSet + PVC** (no dependencies)
   - Validation: `kubectl wait --for=condition=ready pod -l app=redis -n todo-phaseiv --timeout=60s`
2. **MCP Server Deployment** (depends on Redis for session storage if needed)
   - Validation: `kubectl wait --for=condition=ready pod -l app=mcp-server -n todo-phaseiv --timeout=60s`
3. **Backend Deployment** (depends on Redis and PostgreSQL)
   - Database migrations (via initContainer or pre-install Job)
   - Validation: `kubectl wait --for=condition=ready pod -l app=backend -n todo-phaseiv --timeout=120s`
4. **Frontend Deployment** (depends on Backend API)
   - Validation: `kubectl wait --for=condition=ready pod -l app=frontend -n todo-phaseiv --timeout=60s`
5. **Ingress Resource** (all services must exist before routing)
   - Validation: `kubectl wait --for=jsonpath='{.status.loadBalancer.ingress}' ingress todo-app-ingress -n todo-phaseiv --timeout=60s`

**Script Implementation** (deploy.sh):
```bash
#!/bin/bash
set -e  # Exit on error

# Step 1: Build Docker images in Minikube environment
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# Step 2: Install Helm chart with --wait flag
helm install todo-app ./helm/todo-app \
  -n todo-phaseiv \
  --create-namespace \
  --wait \
  --timeout 10m

# Step 3: Run Helm tests
helm test todo-app -n todo-phaseiv

# Step 4: Display access information
echo "Deployment complete!"
echo "Add to /etc/hosts: $(minikube ip) todo-app.local"
echo "Access: http://todo-app.local"
```

**Alternatives Considered**:
- Parallel deployment: Rejected - causes startup failures from missing dependencies
- Helm hooks for ordering: Considered but --wait flag simpler and sufficient
- Init containers for dependency waiting: Implemented for database migrations only

**References**:
- Helm Install: https://helm.sh/docs/helm/helm_install/
- kubectl wait: https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#wait

---

### 9. Testing Strategy

**Decision**: 6-category testing approach covering functional, performance, and resilience requirements

**Testing Categories**:

#### 9.1 Helm Tests (Chart Validation)
- Purpose: Validate deployment health immediately after helm install
- Implementation: Helm test pods that execute health checks and basic connectivity tests
- Example:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "todo-app.fullname" . }}-test-frontend"
  annotations:
    "helm.sh/hook": test
spec:
  containers:
  - name: wget
    image: busybox
    command: ['wget']
    args: ['--spider', 'http://frontend-service:3000/health']
  restartPolicy: Never
```

#### 9.2 E2E Tests (End-to-End Validation)
- Purpose: Validate complete user journey in Kubernetes environment
- Tools: Playwright or Selenium
- Flow: Navigate to http://todo-app.local → Register → Login → Chat → Create task via MCP → Verify task in database
- Success Criteria: All steps complete without errors

#### 9.3 Load Tests (HPA Validation)
- Purpose: Trigger autoscaling and validate HPA behavior
- Tool: Apache Bench (`ab`)
- Command: `ab -n 10000 -c 50 http://todo-app.local/`
- Success Criteria: Frontend scales from 2 to 5 replicas within 2 minutes

#### 9.4 Resilience Tests (Self-Healing Validation)
- Purpose: Validate Kubernetes automatic pod restart and recovery
- Test: `kubectl delete pod <frontend-pod> -n todo-phaseiv`
- Success Criteria: Kubernetes recreates pod within 30 seconds, service remains available

#### 9.5 Persistence Tests (PVC Validation)
- Purpose: Validate Redis data retention across pod restarts
- Test:
  1. Write key: `kubectl exec redis-0 -n todo-phaseiv -- redis-cli SET test-key "persistence-test"`
  2. Delete pod: `kubectl delete pod redis-0 -n todo-phaseiv`
  3. Read key: `kubectl exec redis-0 -n todo-phaseiv -- redis-cli GET test-key`
- Success Criteria: Key value "persistence-test" retained after pod recreation

#### 9.6 Ingress Tests (HTTP Routing Validation)
- Purpose: Validate path-based routing configuration
- Tests:
  1. `curl http://todo-app.local/` → Returns frontend HTML (HTTP 200)
  2. `curl http://todo-app.local/api/health` → Returns backend health JSON (HTTP 200)
- Success Criteria: Both requests return correct responses

**Test Execution Script** (test.sh):
```bash
#!/bin/bash

echo "Running Helm tests..."
helm test todo-app -n todo-phaseiv

echo "Running E2E tests..."
# Playwright/Selenium test suite

echo "Running load tests..."
ab -n 10000 -c 50 http://todo-app.local/

echo "Running resilience tests..."
# Pod deletion and recovery validation

echo "Running persistence tests..."
# Redis data retention validation

echo "Running ingress tests..."
curl -s -o /dev/null -w "%{http_code}" http://todo-app.local/
curl -s -o /dev/null -w "%{http_code}" http://todo-app.local/api/health

echo "All tests completed!"
```

**Alternatives Considered**:
- Kubernetes conformance tests: Out of scope - cluster validation not required
- Chaos engineering (Chaos Mesh): Deferred to Phase V - advanced resilience testing
- Performance benchmarking (k6, Locust): Deferred to Phase V - load testing with ab sufficient for MVP

**References**:
- Helm Tests: https://helm.sh/docs/topics/chart_tests/
- Apache Bench: https://httpd.apache.org/docs/2.4/programs/ab.html

---

### 10. Documentation Structure

**Decision**: 3-tier documentation approach (KUBERNETES_GUIDE.md, Helm README.md, RUNBOOK.md)

**Documentation Requirements**:

#### 10.1 KUBERNETES_GUIDE.md (Comprehensive Deployment Guide)
- **Audience**: Developers deploying application for first time
- **Sections**:
  1. Prerequisites (Minikube, kubectl, Helm, Docker Desktop)
  2. Minikube Setup (installation, cluster creation, addon enablement)
  3. Helm Installation
  4. Deployment Steps (build images, install chart, verify deployment)
  5. Testing Procedures (run all 6 test categories)
  6. Troubleshooting (common issues and resolutions)
  7. Architecture Diagram (visual representation of services, ingress, PVCs)

#### 10.2 Helm README.md (Chart-Specific Documentation)
- **Audience**: Operators customizing Helm chart
- **Sections**:
  1. Chart Description
  2. Requirements (Kubernetes version, Helm version)
  3. Installation Instructions
  4. Configuration Values (values.yaml documentation)
  5. Examples (common deployment scenarios)

#### 10.3 RUNBOOK.md (Operational Procedures)
- **Audience**: Operators performing routine tasks
- **Sections**:
  1. Common Operations
     - Scale replicas: `kubectl scale deployment frontend -n todo-phaseiv --replicas=3`
     - View logs: `kubectl logs -f <pod> -n todo-phaseiv`
     - Restart pods: `kubectl rollout restart deployment/backend -n todo-phaseiv`
     - Update secrets: `kubectl create secret generic todo-app-secrets --from-literal=...`
  2. Troubleshooting Procedures
     - Pods stuck in Pending: Check resource quotas, PVC binding
     - Ingress not routing: Verify ingress controller, /etc/hosts entry
     - HPA not scaling: Check metrics-server, resource requests defined
  3. Backup and Restore (Redis PVC backup procedures)
  4. Upgrade Procedures (helm upgrade, rollback)

**Architecture Diagram** (ASCII representation for KUBERNETES_GUIDE.md):
```
┌─────────────────────────────────────────────────────────────┐
│                      Minikube Cluster                       │
│                   (Namespace: todo-phaseiv)                 │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Nginx Ingress Controller                │  │
│  │           (todo-app.local → Routing Rules)           │  │
│  └─────────┬────────────────────────────┬───────────────┘  │
│            │                            │                   │
│    Path: / │                    Path: /api                 │
│            ▼                            ▼                   │
│  ┌─────────────────┐          ┌─────────────────┐          │
│  │ Frontend Service│          │ Backend Service │          │
│  │  (ClusterIP)    │          │  (ClusterIP)    │          │
│  └────────┬────────┘          └────────┬────────┘          │
│           │                            │                   │
│           │ HPA (2-5 replicas)         │ HPA (2-5 replicas)│
│           ▼                            ▼                   │
│  ┌─────────────────┐          ┌─────────────────┐          │
│  │Frontend Pods    │          │Backend Pods     │          │
│  │(Next.js:3000)   │          │(FastAPI:8000)   │          │
│  │  Liveness ✓     │          │  Liveness ✓     │          │
│  │  Readiness ✓    │          │  Readiness ✓    │          │
│  └─────────────────┘          └────────┬────────┘          │
│                                        │                   │
│                        ┌───────────────┴────────┐          │
│                        │                        │          │
│              ┌─────────▼─────────┐    ┌─────────▼──────┐  │
│              │ MCP Service       │    │ Redis Service  │  │
│              │ (ClusterIP)       │    │ (ClusterIP)    │  │
│              └─────────┬─────────┘    └─────────┬──────┘  │
│                        │                        │          │
│              ┌─────────▼─────────┐    ┌─────────▼──────┐  │
│              │ MCP Server Pod    │    │ Redis Pod      │  │
│              │ (FastMCP:8001)    │    │ (Redis:6379)   │  │
│              │  Liveness ✓       │    │  Liveness ✓    │  │
│              │  Readiness ✓      │    │  Readiness ✓   │  │
│              └───────────────────┘    └─────────┬──────┘  │
│                                                 │          │
│                                        ┌────────▼───────┐  │
│                                        │ PersistentVolume│  │
│                                        │ (1Gi, RWO)     │  │
│                                        │ (Redis /data)  │  │
│                                        └────────────────┘  │
│                                                             │
│  External:                                                  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Neon PostgreSQL (DATABASE_URL from Secret)          │  │
│  │ Shared with Phase III (tables: tasks_phaseiii,      │  │
│  │ conversations, messages)                             │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Alternatives Considered**:
- Single combined README.md: Rejected - too long, hard to navigate
- Wiki-based documentation: Deferred to Phase V - markdown in repo sufficient for MVP
- Video tutorials: Out of scope - written docs required per constitution

**References**:
- Kubernetes Documentation Style Guide: https://kubernetes.io/docs/contribute/style/style-guide/

---

## Summary of Research Outcomes

All NEEDS CLARIFICATION items from Technical Context have been resolved:

✅ **Helm Chart Structure**: Helm 3 semantic release chart with standard template organization
✅ **Nginx Ingress**: Official controller with path-based routing, Minikube addon enabled
✅ **HPA Configuration**: CPU-based for frontend, CPU+memory for backend, 70%/80% thresholds
✅ **StatefulSet + PVC**: Redis with AOF persistence, standard StorageClass, 1Gi PVC
✅ **Health Probes**: HTTP GET for frontend/backend/mcp, exec for Redis, 10s initial delay
✅ **Resource Limits**: Burstable QoS with requests < limits for all services
✅ **Secrets Management**: Kubernetes Secrets with base64 encoding, Helm values injection
✅ **Deployment Strategy**: Sequential rollout in dependency order with health validation gates
✅ **Testing Strategy**: 6 categories (Helm, E2E, load, resilience, persistence, ingress)
✅ **Documentation Structure**: 3-tier (KUBERNETES_GUIDE.md, Helm README.md, RUNBOOK.md)

**Next Steps**: Proceed to Phase 1 (Design & Contracts) to generate data-model.md, contracts/, and quickstart.md.
