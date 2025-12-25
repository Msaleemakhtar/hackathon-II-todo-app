# Phase IV: Local Kubernetes Deployment - Implementation Plan

## Executive Summary

**Current State**: Phase III Todo Chatbot is fully containerized with Docker Compose (4 services: frontend, backend, mcp-server, redis). Complete with multi-stage Dockerfiles, health checks, and 614-line Docker guide.

**Phase IV Goal**: Deploy the containerized application to local Kubernetes (Minikube) using Helm charts, leveraging AI DevOps tools (Docker AI/Gordon, kubectl-ai, kagent).

**Gap Analysis**:
- ✅ Docker containers ready (already built)
- ❌ Helm charts missing
- ❌ Kubernetes manifests missing
- ❌ Minikube deployment configuration missing
- ❌ AI DevOps tools (kubectl-ai, kagent) not yet integrated

---

## Phase IV Requirements (from Hackathon Doc)

### Mandatory Deliverables
1. **Containerization**: ✅ COMPLETE - Docker images exist for frontend, backend, MCP server
2. **Helm Charts**: ❌ TO DO - Create Helm charts for all services
3. **Minikube Deployment**: ❌ TO DO - Deploy and test on local Minikube cluster
4. **AI DevOps Tools**: ❌ TO DO - Use kubectl-ai and/or kagent to generate K8s manifests

### Technology Stack
- **Container Runtime**: Docker Desktop
- **Docker AI**: Gordon (Docker AI Agent) - optional if available
- **Orchestration**: Kubernetes (Minikube)
- **Package Manager**: Helm Charts
- **AI DevOps**: kubectl-ai, kagent

---

## Current Architecture (Phase III in phaseIV directory)

### Services Overview
```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                      │
├─────────────────────────────────────────────────────────────┤
│  1. frontend (Next.js)          - Port 3000                 │
│  2. backend (FastAPI + ChatKit) - Port 8000                 │
│  3. mcp-server (FastMCP)        - Port 8001                 │
│  4. redis (Cache)               - Port 6379                 │
│  External: Neon PostgreSQL (managed database)               │
└─────────────────────────────────────────────────────────────┘
```

### Existing Docker Assets
- **Frontend Dockerfile**: `/phaseIV/frontend/Dockerfile` (3-stage: deps, builder, runner)
- **Backend Dockerfile**: `/phaseIV/backend/Dockerfile` (2-stage: builder, runtime)
- **MCP Dockerfile**: `/phaseIV/backend/Dockerfile.mcp` (2-stage: builder, runtime)
- **Docker Compose**: `/phaseIV/docker-compose.yml` (4 services, networks, volumes)
- **Documentation**: `/phaseIV/DOCKER_GUIDE.md` (comprehensive 614-line guide)

### Resource Limits (from docker-compose.yml)
- Frontend: 1.0 CPU, 1GB RAM
- Backend: 1.0 CPU, 1GB RAM
- MCP Server: 0.5 CPU, 512MB RAM
- Redis: 0.5 CPU, 256MB RAM

---

## Implementation Strategy

### Approach: Helm Charts for Kubernetes

**Why Helm?**
- Package manager for Kubernetes (like npm/apt)
- Templating engine for K8s manifests
- Version management and rollback capability
- Reusable across environments (dev, staging, prod)

**Chart Structure**:
```
phaseIV/helm/
└── todo-chatbot/              # Helm chart root
    ├── Chart.yaml             # Chart metadata
    ├── values.yaml            # Default configuration
    ├── values-dev.yaml        # Dev overrides
    ├── templates/             # K8s manifest templates
    │   ├── _helpers.tpl       # Template helpers
    │   ├── frontend/
    │   │   ├── deployment.yaml
    │   │   ├── service.yaml
    │   │   └── hpa.yaml       # Horizontal Pod Autoscaler (optional)
    │   ├── backend/
    │   │   ├── deployment.yaml
    │   │   ├── service.yaml
    │   │   └── hpa.yaml
    │   ├── mcp-server/
    │   │   ├── deployment.yaml
    │   │   └── service.yaml
    │   ├── redis/
    │   │   ├── deployment.yaml
    │   │   ├── service.yaml
    │   │   └── pvc.yaml       # Persistent Volume Claim
    │   ├── configmap.yaml     # App configuration
    │   ├── secrets.yaml       # Sensitive data (base64)
    │   └── ingress.yaml       # Optional: expose frontend
    └── .helmignore
```

---

## Step-by-Step Execution Plan

### STEP 1: Prerequisites Setup

**1.1 Install Required Tools**
```bash
# Minikube (local Kubernetes cluster)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# kubectl (Kubernetes CLI)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl

# Helm (Kubernetes package manager)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# kubectl-ai (AI-powered kubectl assistant)
curl -LO https://github.com/GoogleCloudPlatform/kubectl-ai/releases/latest/download/kubectl-ai-linux-amd64
chmod +x kubectl-ai-linux-amd64
sudo mv kubectl-ai-linux-amd64 /usr/local/bin/kubectl-ai

# kagent (Kubernetes AI agent)
# Installation method TBD - check https://github.com/kagent-dev/kagent
```

**1.2 Verify Installations**
```bash
minikube version
kubectl version --client
helm version
kubectl-ai --version
kagent --version  # if available
```

**1.3 Docker Desktop Check**
- Ensure Docker Desktop is installed and running
- Enable Kubernetes in Docker Desktop settings (optional alternative to Minikube)
- Check Docker AI (Gordon) availability:
  ```bash
  docker ai "What can you do?"
  ```

---

### STEP 2: Build and Tag Docker Images

**2.1 Build Images Locally**
```bash
cd /home/salim/Desktop/hackathon-II-todo-app/phaseIV

# Build frontend
docker build -t todo-chatbot-frontend:v1.0.0 -f frontend/Dockerfile frontend/

# Build backend
docker build -t todo-chatbot-backend:v1.0.0 -f backend/Dockerfile backend/

# Build MCP server
docker build -t todo-chatbot-mcp:v1.0.0 -f backend/Dockerfile.mcp backend/
```

**2.2 Load Images into Minikube**
```bash
# Start Minikube
minikube start --cpus=4 --memory=8192 --driver=docker

# Load images into Minikube's Docker daemon
minikube image load todo-chatbot-frontend:v1.0.0
minikube image load todo-chatbot-backend:v1.0.0
minikube image load todo-chatbot-mcp:v1.0.0
```

**Alternative: Use Minikube Docker Daemon Directly**
```bash
# Point shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Build images directly in Minikube
docker build -t todo-chatbot-frontend:v1.0.0 -f frontend/Dockerfile frontend/
docker build -t todo-chatbot-backend:v1.0.0 -f backend/Dockerfile backend/
docker build -t todo-chatbot-mcp:v1.0.0 -f backend/Dockerfile.mcp backend/
```

---

### STEP 3: Create Helm Chart Structure

**3.1 Initialize Helm Chart**
```bash
cd /home/salim/Desktop/hackathon-II-todo-app/phaseIV
mkdir -p helm
cd helm

# Create chart scaffold using kubectl-ai or manually
helm create todo-chatbot
```

**3.2 Use kubectl-ai to Generate K8s Manifests** (AI-Assisted Approach)
```bash
# Example prompts for kubectl-ai
kubectl-ai "Create a Kubernetes deployment for a Next.js frontend app on port 3000 with 1GB memory limit"
kubectl-ai "Create a Kubernetes service to expose the frontend deployment"
kubectl-ai "Create a deployment for FastAPI backend with health checks on /health endpoint"
kubectl-ai "Create a Redis statefulset with persistent storage"
```

**3.3 Manual Helm Chart Creation** (Fallback if AI tools unavailable)
- Create Chart.yaml with metadata
- Define values.yaml with all configurable parameters
- Create deployment templates for each service
- Create service templates for internal communication
- Create ConfigMap for environment variables
- Create Secret for sensitive data (API keys, database URLs)

---

### STEP 4: Configure Helm Values

**4.1 Main Configuration (values.yaml)**

**Key Configurations**:
- **Image tags**: Use local images (imagePullPolicy: IfNotPresent or Never)
- **Resource limits**: Match docker-compose.yml specifications
- **Environment variables**: Extract from phaseIV/.env
- **Service ports**: frontend:3000, backend:8000, mcp:8001, redis:6379
- **Health checks**: Replicate from Dockerfiles
- **Persistent volumes**: Redis data storage

**4.2 Secrets Management**

**Critical Secrets** (from .env.example):
- `DATABASE_URL` - Neon PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key
- `GEMINI_API_KEY` - Google Gemini API key (optional)
- `BETTER_AUTH_SECRET` - JWT signing secret
- `REDIS_URL` - Redis connection string (internal)

**Kubernetes Secret Creation**:
```bash
# Create from .env file
kubectl create secret generic todo-chatbot-secrets \
  --from-env-file=.env \
  --dry-run=client -o yaml > helm/todo-chatbot/templates/secrets.yaml
```

---

### STEP 5: Deploy to Minikube

**5.1 Create Kubernetes Namespace**
```bash
kubectl create namespace todo-chatbot
```

**5.2 Deploy with Helm**
```bash
cd /home/salim/Desktop/hackathon-II-todo-app/phaseIV/helm

# Install the chart
helm install todo-chatbot ./todo-chatbot \
  --namespace todo-chatbot \
  --create-namespace \
  --values ./todo-chatbot/values.yaml

# Or use helm upgrade --install for idempotency
helm upgrade --install todo-chatbot ./todo-chatbot \
  --namespace todo-chatbot \
  --create-namespace
```

**5.3 Verify Deployment**
```bash
# Check all resources
kubectl get all -n todo-chatbot

# Check pod status
kubectl get pods -n todo-chatbot

# Check services
kubectl get svc -n todo-chatbot

# View logs
kubectl logs -f deployment/frontend -n todo-chatbot
kubectl logs -f deployment/backend -n todo-chatbot
kubectl logs -f deployment/mcp-server -n todo-chatbot
```

---

### STEP 6: Expose Services Locally

**6.1 Port Forwarding (Quick Access)**
```bash
# Forward frontend to localhost:3000
kubectl port-forward -n todo-chatbot svc/frontend 3000:3000

# Forward backend to localhost:8000
kubectl port-forward -n todo-chatbot svc/backend 8000:8000
```

**6.2 Minikube Service (Persistent Access)**
```bash
# Get Minikube IP
minikube ip

# Access via NodePort
minikube service frontend -n todo-chatbot --url
minikube service backend -n todo-chatbot --url
```

**6.3 Ingress Controller (Production-like)**
```bash
# Enable ingress addon
minikube addons enable ingress

# Create ingress resource (in Helm chart)
# Access via http://todo-chatbot.local (add to /etc/hosts)
```

---

### STEP 7: Testing and Validation

**7.1 Health Checks**
```bash
# Test backend health
curl http://$(minikube ip):$(kubectl get svc backend -n todo-chatbot -o jsonpath='{.spec.ports[0].nodePort}')/health

# Test frontend
curl http://$(minikube ip):$(kubectl get svc frontend -n todo-chatbot -o jsonpath='{.spec.ports[0].nodePort}')
```

**7.2 Functional Testing**
- Open frontend URL in browser
- Test user authentication (Better Auth)
- Test chat functionality
- Verify MCP tools are invoked correctly
- Check database persistence (Neon)
- Test Redis caching

**7.3 Resource Monitoring**
```bash
# Monitor resource usage
kubectl top nodes
kubectl top pods -n todo-chatbot

# Dashboard (optional)
minikube dashboard
```

---

### STEP 8: AI DevOps Integration

**8.1 Use kubectl-ai for Operations**
```bash
# Deploy with AI assistance
kubectl-ai "deploy the todo frontend with 2 replicas"
kubectl-ai "scale the backend to handle more load"
kubectl-ai "check why the pods are failing"

# Troubleshooting
kubectl-ai "show me why the backend pod is crashing"
kubectl-ai "check the logs of the mcp-server pod"
```

**8.2 Use kagent for Advanced Operations** (if available)
```bash
kagent "analyze the cluster health"
kagent "optimize resource allocation for todo-chatbot namespace"
kagent "suggest improvements for deployment stability"
```

**8.3 Use Docker AI (Gordon)** (if available)
```bash
# Docker container insights
docker ai "What can you do?"
docker ai "How can I optimize my Docker images?"
docker ai "Analyze the todo-chatbot-frontend image for security issues"
```

---

## Critical Files to Create/Modify

### New Files (Helm Chart)
1. `/phaseIV/helm/todo-chatbot/Chart.yaml` - Chart metadata
2. `/phaseIV/helm/todo-chatbot/values.yaml` - Default configuration
3. `/phaseIV/helm/todo-chatbot/templates/frontend/deployment.yaml` - Frontend deployment
4. `/phaseIV/helm/todo-chatbot/templates/frontend/service.yaml` - Frontend service
5. `/phaseIV/helm/todo-chatbot/templates/backend/deployment.yaml` - Backend deployment
6. `/phaseIV/helm/todo-chatbot/templates/backend/service.yaml` - Backend service
7. `/phaseIV/helm/todo-chatbot/templates/mcp-server/deployment.yaml` - MCP deployment
8. `/phaseIV/helm/todo-chatbot/templates/mcp-server/service.yaml` - MCP service
9. `/phaseIV/helm/todo-chatbot/templates/redis/deployment.yaml` - Redis deployment
10. `/phaseIV/helm/todo-chatbot/templates/redis/service.yaml` - Redis service
11. `/phaseIV/helm/todo-chatbot/templates/redis/pvc.yaml` - Redis persistent storage
12. `/phaseIV/helm/todo-chatbot/templates/configmap.yaml` - App configuration
13. `/phaseIV/helm/todo-chatbot/templates/secrets.yaml` - Sensitive data
14. `/phaseIV/helm/todo-chatbot/templates/_helpers.tpl` - Template helpers

### Documentation Files
15. `/phaseIV/KUBERNETES_GUIDE.md` - Minikube deployment guide
16. `/phaseIV/README.md` - Update with K8s instructions

---

## Environment Variable Mapping (Docker → Kubernetes)

### Frontend Environment Variables
```yaml
# From docker-compose.yml → ConfigMap/Secret
NEXT_PUBLIC_API_URL: "http://backend:8000"  # Internal K8s service
NEXT_PUBLIC_BETTER_AUTH_URL: "http://frontend:3000"
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY: ""  # From secret
```

### Backend Environment Variables
```yaml
DATABASE_URL: "postgresql+asyncpg://..."  # From secret
OPENAI_API_KEY: "sk-proj-..."  # From secret
GEMINI_API_KEY: "..."  # From secret
BETTER_AUTH_SECRET: "..."  # From secret
ENVIRONMENT: "production"
LOG_LEVEL: "INFO"
HOST: "0.0.0.0"
PORT: "8000"
CORS_ORIGINS: "http://frontend:3000"  # Internal K8s service
MCP_SERVER_URL: "http://mcp-server:8001/mcp"  # Internal K8s service
REDIS_URL: "redis://redis:6379/0"  # Internal K8s service
```

---

## Service Communication (Kubernetes Internal DNS)

In Kubernetes, services communicate via internal DNS:
- `frontend` → `backend` via `http://backend:8000`
- `backend` → `mcp-server` via `http://mcp-server:8001`
- `backend` → `redis` via `redis://redis:6379`
- External: All services → Neon PostgreSQL via public URL

**Service Naming Convention**: `<service-name>.<namespace>.svc.cluster.local`
- Full: `backend.todo-chatbot.svc.cluster.local:8000`
- Short: `backend:8000` (within same namespace)

---

## Resource Requirements Summary

| Service     | CPU Request | CPU Limit | Memory Request | Memory Limit | Storage      |
|-------------|-------------|-----------|----------------|--------------|--------------|
| Frontend    | 500m        | 1000m     | 512Mi          | 1Gi          | -            |
| Backend     | 500m        | 1000m     | 512Mi          | 1Gi          | -            |
| MCP Server  | 250m        | 500m      | 256Mi          | 512Mi        | -            |
| Redis       | 250m        | 500m      | 128Mi          | 256Mi        | 1Gi (PVC)    |
| **Total**   | **1.5 CPU** | **3 CPU** | **1.4Gi**      | **2.8Gi**    | **1Gi PVC**  |

**Minikube Cluster Requirements**: 4 CPU, 8GB RAM recommended

---

## Troubleshooting Guide

### Common Issues

**Issue 1: Pods in CrashLoopBackOff**
```bash
# Check logs
kubectl logs <pod-name> -n todo-chatbot

# Check events
kubectl describe pod <pod-name> -n todo-chatbot

# Common causes:
# - Missing environment variables (check secrets/configmap)
# - Database connection failure (check DATABASE_URL)
# - Image pull errors (check imagePullPolicy)
```

**Issue 2: Service Not Accessible**
```bash
# Check service endpoints
kubectl get endpoints -n todo-chatbot

# Check if pods are ready
kubectl get pods -n todo-chatbot

# Test internal connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://backend:8000/health
```

**Issue 3: Redis Data Loss**
```bash
# Check PVC status
kubectl get pvc -n todo-chatbot

# Check PV binding
kubectl get pv

# Ensure Redis deployment uses volumeMounts
```

**Issue 4: Environment Variables Not Loading**
```bash
# Verify secret creation
kubectl get secret todo-chatbot-secrets -n todo-chatbot -o yaml

# Check configmap
kubectl get configmap -n todo-chatbot -o yaml

# Verify pod env injection
kubectl describe pod <pod-name> -n todo-chatbot | grep -A 20 "Environment"
```

---

## Validation Checklist

### Pre-Deployment
- [ ] Minikube cluster running
- [ ] Docker images built and loaded
- [ ] Helm chart created
- [ ] Secrets configured (API keys, DB URL)
- [ ] ConfigMap configured (app settings)

### Post-Deployment
- [ ] All pods in Running state
- [ ] All services created and endpoints available
- [ ] Health checks passing
- [ ] Frontend accessible via port-forward or NodePort
- [ ] Backend API responding
- [ ] MCP server responding
- [ ] Redis connected and caching
- [ ] Database connection successful (Neon)
- [ ] User authentication working (Better Auth)
- [ ] Chat functionality working
- [ ] MCP tools invoked correctly

### Documentation
- [ ] KUBERNETES_GUIDE.md created
- [ ] README.md updated with K8s instructions
- [ ] Helm chart documented

---

## Next Steps After Phase IV

**Phase V Preview**: Advanced Cloud Deployment
- Deploy to DigitalOcean Kubernetes (DOKS) or GKE/AKS
- Add Kafka for event-driven architecture
- Integrate Dapr for distributed application runtime
- Set up CI/CD pipeline with GitHub Actions
- Configure monitoring and logging

---

## FINAL IMPLEMENTATION APPROACH

### User Decisions

✅ **Kubernetes Platform**: Minikube (local cluster, 4 CPU, 8GB RAM)
✅ **Development Methodology**: Spec-Driven Development (constitutional requirement)
✅ **AI Tools**: Manual Helm chart creation (kubectl-ai/kagent not available)
✅ **Production Features**: Full professional deployment
  - Nginx Ingress Controller for HTTP routing
  - Persistent Volumes for Redis data
  - Horizontal Pod Autoscaling (HPA) for scalability
  - Complete observability (probes, logs, metrics)

---

## SPECIFICATION-FIRST WORKFLOW

Following the constitutional mandate, implementation will proceed:

**Step 1: Write Specification** → **Step 2: Generate Helm Charts** → **Step 3: Deploy & Test**

### Specification Structure (1 Comprehensive Spec)

**Single Specification**: `/specs/sphaseIV/001-kubernetes-deployment/`

This comprehensive spec covers all Phase IV requirements:
- **Infrastructure Setup**: Minikube installation, cluster configuration, prerequisites
- **Helm Chart Architecture**: Chart structure, values schema, templating
- **Service Deployments**: All 4 services (frontend, backend, mcp-server, redis)
- **Configuration Management**: Secrets, ConfigMaps, environment variables
- **Production Features**: Nginx Ingress, Persistent Volumes, Horizontal Pod Autoscaling
- **Observability**: Health probes, logging, monitoring, metrics
- **Testing & Validation**: Deployment tests, E2E tests, load tests, rollback procedures

**Required Files**:
- `spec.md` - Comprehensive requirements for entire Kubernetes deployment
- `plan.md` - Implementation strategy and architecture decisions
- `tasks.md` - Sequential tasks broken down by implementation phase

**Rationale for Single Spec**: Phase IV is a cohesive Kubernetes deployment task where all components are tightly integrated. A single comprehensive spec is more practical than 11 granular specs, while still maintaining SDD compliance.

---

## HELM CHART ARCHITECTURE

### Directory Structure

```
phaseIV/kubernetes/
├── helm/
│   └── todo-app/                      # Main Helm chart
│       ├── Chart.yaml                 # Chart metadata (v1.0.0)
│       ├── values.yaml                # Default configuration
│       ├── values-dev.yaml            # Development overrides
│       └── templates/                 # Kubernetes resource templates
│           ├── _helpers.tpl           # Template helpers
│           ├── namespace.yaml         # Namespace definition
│           ├── backend/
│           │   ├── deployment.yaml
│           │   ├── service.yaml
│           │   ├── configmap.yaml
│           │   ├── secret.yaml
│           │   └── hpa.yaml
│           ├── frontend/
│           │   ├── deployment.yaml
│           │   ├── service.yaml
│           │   ├── configmap.yaml
│           │   ├── secret.yaml
│           │   └── hpa.yaml
│           ├── mcp-server/
│           │   ├── deployment.yaml
│           │   ├── service.yaml
│           │   └── configmap.yaml
│           ├── redis/
│           │   ├── statefulset.yaml
│           │   ├── service.yaml
│           │   └── pvc.yaml
│           └── ingress/
│               └── ingress.yaml
├── scripts/
│   ├── setup-cluster.sh               # Initial Minikube setup
│   ├── deploy.sh                      # Helm install/upgrade
│   └── rollback.sh                    # Rollback procedures
└── docs/
    ├── KUBERNETES_GUIDE.md            # Complete deployment guide
    └── RUNBOOK.md                     # Operations handbook
```

---

## IMPLEMENTATION SEQUENCE

### Phase 0: Prerequisites (Spec 001)
1. Install Minikube: `minikube start --cpus=4 --memory=8192 --driver=docker`
2. Install kubectl (v1.28+)
3. Install Helm 3 (v3.13+)
4. Enable addons:
   - `minikube addons enable ingress`
   - `minikube addons enable metrics-server`
5. Create namespace: `kubectl create namespace todo-phaseiv`

### Phase 1: Build Images (Prerequisite)
1. Use Minikube Docker daemon: `eval $(minikube docker-env)`
2. Build images:
   ```bash
   docker build -t phaseiv-backend:1.0.0 -f backend/Dockerfile backend/
   docker build -t phaseiv-frontend:1.0.0 -f frontend/Dockerfile frontend/
   docker build -t phaseiv-mcp-server:1.0.0 -f backend/Dockerfile.mcp backend/
   ```
3. Verify: `docker images | grep phaseiv`

### Phase 2: Helm Chart Foundation (Spec 002)
1. Create chart structure: `helm create kubernetes/helm/todo-app`
2. Define Chart.yaml metadata
3. Design values.yaml with all configuration
4. Create _helpers.tpl with label templates
5. Validate: `helm lint kubernetes/helm/todo-app`

### Phase 3: Secrets & ConfigMaps (Spec 008)
1. Create secrets:
   ```bash
   kubectl create secret generic database-secret --from-literal=url='postgresql+asyncpg://...'
   kubectl create secret generic api-keys-secret --from-literal=openai-key='sk-...'
   kubectl create secret generic auth-secret --from-literal=secret='32-char-secret'
   ```
2. Create ConfigMap templates in Helm chart
3. Document secret schema in spec contracts

### Phase 4: Redis StatefulSet (Spec 006)
1. Create Redis StatefulSet template (1 replica, appendonly mode)
2. Create PVC template (1Gi, standard StorageClass)
3. Create headless Service template
4. Deploy: `helm install todo-app --set redis.enabled=true ...`
5. Verify:
   - `kubectl get statefulset redis`
   - `kubectl get pvc`
   - `kubectl exec -it redis-0 -- redis-cli ping`

### Phase 5: MCP Server (Spec 005)
1. Create MCP Deployment template (1 replica)
2. Create Service template (ClusterIP, port 8001)
3. Configure ConfigMap/Secret references
4. Deploy: `helm upgrade todo-app ...`
5. Verify: `kubectl logs -l app=mcp-server`

### Phase 6: Backend (Spec 003)
1. Create Backend Deployment template (2 replicas)
2. Create Service template (ClusterIP, port 8000)
3. Create ConfigMap with env vars (MCP_SERVER_URL, REDIS_URL)
4. Create Secret references (DATABASE_URL, API keys)
5. Configure liveness/readiness probes (/health)
6. Deploy: `helm upgrade todo-app ...`
7. Verify: `curl http://backend:8000/health`

### Phase 7: Frontend (Spec 004)
1. Create Frontend Deployment template (2 replicas)
2. Create Service template (ClusterIP, port 3000)
3. Create ConfigMap (NEXT_PUBLIC_API_URL)
4. Configure liveness/readiness probes (/)
5. Deploy: `helm upgrade todo-app ...`
6. Verify: `kubectl port-forward svc/frontend 3000:3000`

### Phase 8: Ingress (Spec 007)
1. Verify Nginx Ingress Controller: `kubectl get pods -n ingress-nginx`
2. Create Ingress template:
   - Host: `todo-app.local`
   - Path `/` → frontend:3000
   - Path `/api` → backend:8000
3. Deploy: `helm upgrade todo-app --set ingress.enabled=true`
4. Configure hosts: `echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts`
5. Verify:
   - `curl http://todo-app.local`
   - `curl http://todo-app.local/api/health`

### Phase 9: HPA (Spec 009)
1. Verify metrics-server: `kubectl top nodes`
2. Create Backend HPA template (min: 2, max: 5, CPU: 70%, Memory: 80%)
3. Create Frontend HPA template (min: 2, max: 5, CPU: 70%, Memory: 80%)
4. Deploy: `helm upgrade todo-app --set backend.autoscaling.enabled=true ...`
5. Test: Generate load and verify scaling with `watch kubectl get hpa`

### Phase 10: Observability (Spec 010)
1. Verify all liveness/readiness probes configured
2. Enable structured logging in all services
3. Test health checks: `kubectl describe pod <pod-name>`
4. Access dashboard: `minikube dashboard`

### Phase 11: Testing (Spec 011)
1. Run Helm tests: `helm test todo-app`
2. End-to-end test: User flow (signup → login → chat → tasks)
3. Load test: HPA scaling verification
4. Resilience test: Pod deletion and recreation
5. Data persistence test: Redis data survives restart
6. Rollback test: `helm rollback todo-app`

---

## RESOURCE ALLOCATION

| Service    | Replicas | CPU Request | CPU Limit | Memory Request | Memory Limit | Storage |
|------------|----------|-------------|-----------|----------------|--------------|---------|
| Frontend   | 2-5 (HPA)| 500m        | 1000m     | 512Mi          | 1Gi          | -       |
| Backend    | 2-5 (HPA)| 500m        | 1000m     | 512Mi          | 1Gi          | -       |
| MCP Server | 1        | 250m        | 500m      | 256Mi          | 512Mi        | -       |
| Redis      | 1        | 250m        | 500m      | 128Mi          | 256Mi        | 1Gi PVC |
| **Total**  | 6-13     | 2.5 CPUs    | 5 CPUs    | 1.4Gi          | 2.8Gi        | 1Gi     |

**Minikube Requirements**: 4 CPUs, 8GB RAM (sufficient for max scaling)

---

## SERVICE COMMUNICATION

### Kubernetes Internal DNS

Services communicate via ClusterIP and DNS:

- Frontend → Backend: `http://backend:8000`
- Backend → MCP Server: `http://mcp-server:8001/mcp`
- Backend → Redis: `redis://redis:6379/0`
- All Services → Neon PostgreSQL: External URL (via Secret)

Full DNS: `<service>.<namespace>.svc.cluster.local`
Short form (same namespace): `<service>:<port>`

---

## ENVIRONMENT VARIABLES MIGRATION

### From docker-compose.yml to Kubernetes

| Variable                    | Source          | K8s Resource |
|-----------------------------|-----------------|--------------|
| DATABASE_URL                | .env (secret)   | Secret       |
| OPENAI_API_KEY              | .env (secret)   | Secret       |
| GEMINI_API_KEY              | .env (secret)   | Secret       |
| BETTER_AUTH_SECRET          | .env (secret)   | Secret       |
| ENVIRONMENT                 | .env            | ConfigMap    |
| MCP_SERVER_URL              | service DNS     | ConfigMap    |
| REDIS_URL                   | service DNS     | ConfigMap    |
| NEXT_PUBLIC_API_URL         | service DNS     | ConfigMap    |

**Secret Creation**:
```bash
kubectl create secret generic todo-secrets \
  --from-literal=database-url='postgresql+asyncpg://...' \
  --from-literal=openai-key='sk-proj-...' \
  --from-literal=better-auth-secret='...'
```

---

## PRODUCTION FEATURES DETAILS

### 1. Nginx Ingress Controller

**Purpose**: Single HTTP entry point with path-based routing

**Configuration**:
```yaml
spec:
  ingressClassName: nginx
  rules:
    - host: todo-app.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port: 3000
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend
                port: 8000
```

**Access**: `http://todo-app.local` (requires /etc/hosts entry)

### 2. Persistent Volumes for Redis

**Purpose**: Data survives pod restarts

**Implementation**:
- StorageClass: `standard` (Minikube default)
- PersistentVolumeClaim: 1Gi, ReadWriteOnce
- StatefulSet volumeClaimTemplate
- Mount path: `/data`
- Redis AOF: `redis-server --appendonly yes`

**Verification**:
```bash
# Write data
kubectl exec -it redis-0 -- redis-cli SET test-key test-value

# Delete pod
kubectl delete pod redis-0

# Verify data persists
kubectl exec -it redis-0 -- redis-cli GET test-key
```

### 3. Horizontal Pod Autoscaling

**Purpose**: Auto-scale frontend/backend based on resource usage

**Configuration**:
- Min replicas: 2
- Max replicas: 5
- Target CPU: 70%
- Target Memory: 80%
- Scale-up: Fast (30s window)
- Scale-down: Slow (300s window, prevents flapping)

**Testing**:
```bash
# Generate load
kubectl run load-generator --rm -it --image=busybox --restart=Never -- \
  /bin/sh -c "while true; do wget -q -O- http://backend:8000/health; done"

# Monitor scaling
watch kubectl get hpa
```

### 4. Health Checks

**Liveness Probes** (restart unhealthy pods):
- Backend: `GET /health` every 10s
- Frontend: `GET /` every 10s
- MCP Server: `TCP :8001` every 10s
- Redis: `redis-cli ping` every 10s

**Readiness Probes** (remove from load balancing):
- Same as liveness, but every 5s
- Faster detection for traffic routing

---

## TESTING STRATEGY

### 1. Pre-Deployment Tests
```bash
# Validate Helm chart
helm lint kubernetes/helm/todo-app

# Dry-run deployment
helm install todo-app ./helm/todo-app --dry-run --debug

# Template validation
helm template todo-app ./helm/todo-app
```

### 2. Deployment Verification
```bash
# Check all resources
kubectl get all -n todo-phaseiv

# Verify pod status
kubectl get pods

# Check services
kubectl get svc

# Verify ingress
kubectl get ingress
```

### 3. End-to-End Tests

**Test Scenarios**:
1. Access frontend: `http://todo-app.local`
2. User signup via Better Auth
3. User login
4. Send chat message: "Add a task to buy groceries"
5. Verify MCP tool invocation
6. List tasks: "Show me all my tasks"
7. Complete task: "Mark the first task as complete"
8. Delete task: "Delete the last task"

### 4. Load & Resilience Tests

**HPA Scaling**:
```bash
# Load test
ab -n 10000 -c 100 http://todo-app.local/api/health

# Verify HPA triggered
kubectl get hpa
kubectl get pods
```

**Pod Resilience**:
```bash
# Delete backend pod
kubectl delete pod -l app=backend --force

# Verify automatic recreation
kubectl get pods -w

# Verify service available
curl http://todo-app.local/api/health
```

**Data Persistence**:
```bash
# Write to Redis
kubectl exec -it redis-0 -- redis-cli SET persist-test value123

# Delete Redis pod
kubectl delete pod redis-0

# Wait for recreation
kubectl wait --for=condition=ready pod/redis-0 --timeout=60s

# Verify data persists
kubectl exec -it redis-0 -- redis-cli GET persist-test
# Expected: "value123"
```

---

## DOCUMENTATION DELIVERABLES

### 1. KUBERNETES_GUIDE.md
- Prerequisites and installation
- Quick start (one-command deployment)
- Architecture overview with diagram
- Service descriptions
- Deployment step-by-step
- Accessing the application
- Scaling instructions
- Monitoring and logs
- Troubleshooting guide
- Rollback procedures
- Cleanup instructions

### 2. Helm Chart README.md
- Chart description
- Installing/uninstalling
- Configuration parameters
- Examples (dev vs prod)
- Upgrading
- Testing

### 3. RUNBOOK.md
- Deployment checklist
- Pre/post-deployment verification
- Monitoring guidelines
- Common operational tasks
- Incident response
- Disaster recovery

---

## CRITICAL FILES TO CREATE/MODIFY

### Specifications (AI-Generated from User Stories)
```
/specs/sphaseIV/001-kubernetes-deployment/spec.md      # Comprehensive Kubernetes deployment requirements
/specs/sphaseIV/001-kubernetes-deployment/plan.md     # Implementation strategy and architecture
/specs/sphaseIV/001-kubernetes-deployment/tasks.md    # Sequential implementation tasks
```

### Helm Chart Templates (Generated from Specs)
```
/phaseIV/kubernetes/helm/todo-app/Chart.yaml
/phaseIV/kubernetes/helm/todo-app/values.yaml
/phaseIV/kubernetes/helm/todo-app/values-dev.yaml
/phaseIV/kubernetes/helm/todo-app/templates/_helpers.tpl
/phaseIV/kubernetes/helm/todo-app/templates/namespace.yaml
/phaseIV/kubernetes/helm/todo-app/templates/backend/deployment.yaml
/phaseIV/kubernetes/helm/todo-app/templates/backend/service.yaml
/phaseIV/kubernetes/helm/todo-app/templates/backend/hpa.yaml
/phaseIV/kubernetes/helm/todo-app/templates/frontend/deployment.yaml
/phaseIV/kubernetes/helm/todo-app/templates/frontend/service.yaml
/phaseIV/kubernetes/helm/todo-app/templates/frontend/hpa.yaml
/phaseIV/kubernetes/helm/todo-app/templates/mcp-server/deployment.yaml
/phaseIV/kubernetes/helm/todo-app/templates/mcp-server/service.yaml
/phaseIV/kubernetes/helm/todo-app/templates/redis/statefulset.yaml
/phaseIV/kubernetes/helm/todo-app/templates/redis/service.yaml
/phaseIV/kubernetes/helm/todo-app/templates/redis/pvc.yaml
/phaseIV/kubernetes/helm/todo-app/templates/ingress/ingress.yaml
```

### Documentation (To Be Created)
```
/phaseIV/KUBERNETES_GUIDE.md
/phaseIV/kubernetes/RUNBOOK.md
/phaseIV/kubernetes/helm/todo-app/README.md
```

### Scripts (To Be Created)
```
/phaseIV/kubernetes/scripts/setup-cluster.sh
/phaseIV/kubernetes/scripts/deploy.sh
/phaseIV/kubernetes/scripts/rollback.sh
/phaseIV/kubernetes/scripts/cleanup.sh
```

---

## SUCCESS CRITERIA

Phase IV deployment is **COMPLETE** when:

### Functional Requirements
- ✅ All 4 services deployed to Minikube (frontend, backend, mcp-server, redis)
- ✅ Ingress routes traffic correctly (/ → frontend, /api → backend)
- ✅ Frontend accessible at `http://todo-app.local`
- ✅ Backend API accessible at `http://todo-app.local/api/health`
- ✅ Redis data persists across pod restarts
- ✅ HPA scales frontend/backend under load
- ✅ User can signup, login, and chat with AI
- ✅ MCP tools work (add, list, complete, delete, update tasks)

### Technical Requirements
- ✅ Comprehensive spec exists with spec.md, plan.md, tasks.md in `/specs/sphaseIV/001-kubernetes-deployment/`
- ✅ Helm chart follows best practices
- ✅ All pods have resource limits and requests
- ✅ All services have liveness/readiness probes
- ✅ Secrets managed via Kubernetes Secrets
- ✅ ConfigMaps used for non-sensitive config
- ✅ Namespace `todo-phaseiv` isolates resources
- ✅ `helm test` passes
- ✅ All pods in Running state with 0 restarts

### Documentation Requirements
- ✅ KUBERNETES_GUIDE.md with deployment instructions
- ✅ Helm chart README.md with configuration guide
- ✅ RUNBOOK.md with operations procedures
- ✅ Architecture diagram included
- ✅ Troubleshooting section complete

### Testing Requirements
- ✅ End-to-end test: Complete user flow works
- ✅ Load test: HPA scales correctly
- ✅ Resilience test: Pod deletion handled gracefully
- ✅ Data persistence test: Redis survives restarts
- ✅ Ingress test: HTTP routing correct

---

## ESTIMATED TIMELINE

| Phase | Tasks | Duration |
|-------|-------|----------|
| **Spec** (001) | Write comprehensive specification | 1 day |
| **Helm Chart** | Create chart structure, templates | 2-3 days |
| **Deployment** | Deploy services incrementally | 2-3 days |
| **Testing** | Validate all functionality | 1-2 days |
| **Documentation** | Complete all docs | 1 day |
| **Total** | | **7-10 days** |

**Parallelization Opportunities**:
- Helm templates can be created concurrently after chart structure
- Testing runs continuously throughout deployment
- Documentation can be written alongside implementation

---

**Plan Status**: ✅ FINAL - Ready for execution following Spec-Driven Development workflow

---

## NEXT STEPS

**User Request**: Save this comprehensive plan to `/docs/phase-iv-implementation-plan.md` for documentation.

**When Ready to Execute**:
1. Exit plan mode
2. Create comprehensive specification at `/specs/sphaseIV/001-kubernetes-deployment/`
   - Write `spec.md` covering all requirements (infrastructure, Helm, deployments, production features, testing)
   - Write `plan.md` with implementation strategy
   - Write `tasks.md` with sequential implementation tasks
3. Generate Helm charts based on specification
4. Deploy to Minikube following implementation sequence (Prerequisites → Build Images → Helm Chart → Services → Production Features → Testing)
