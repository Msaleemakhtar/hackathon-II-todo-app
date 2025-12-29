# Deployment Script Contract

**Feature**: 001-kubernetes-deployment
**Date**: 2025-12-26
**Purpose**: Define the contract for deployment automation scripts

---

## Script: setup-minikube.sh

### Purpose
Install and configure Minikube cluster with required addons for Phase IV deployment.

### Input Parameters
None (uses default configuration)

### Preconditions
- Docker Desktop running and accessible
- User has sudo privileges (for Minikube installation)
- Minimum system resources: 6 CPU cores, 12GB RAM available

### Operations (Sequential)
1. Check if Minikube is installed
   - If not installed: Download and install Minikube v1.32+
2. Check if kubectl is installed
   - If not installed: Download and install kubectl v1.28+
3. Check if Helm is installed
   - If not installed: Download and install Helm v3.13+
4. Start Minikube cluster with configuration:
   - CPUs: 4
   - Memory: 8192MB (8GB)
   - Driver: docker
5. Enable required addons:
   - `minikube addons enable ingress`
   - `minikube addons enable metrics-server`
6. Verify addon status:
   - `minikube addons list | grep ingress` → enabled
   - `minikube addons list | grep metrics-server` → enabled
7. Display Minikube IP for /etc/hosts configuration

### Success Criteria
- Minikube cluster status: Running
- Ingress addon: enabled
- Metrics Server addon: enabled
- kubectl can communicate with cluster (`kubectl cluster-info`)

### Output
```
Minikube cluster ready!
Cluster IP: <minikube-ip>
Add to /etc/hosts: <minikube-ip> todo-app.local
```

### Error Handling
- If Docker Desktop not running: Exit with error "Docker Desktop must be running"
- If insufficient resources: Exit with error "Minimum 6 CPU cores and 12GB RAM required"
- If Minikube start fails: Display error message and cleanup steps

---

## Script: deploy.sh

### Purpose
Build Docker images and deploy Helm chart with incremental rollout validation.

### Input Parameters
- `--namespace <name>` (optional): Override default namespace (default: todo-phaseiv)
- `--wait-timeout <seconds>` (optional): Override default wait timeout (default: 600s)
- `--skip-build` (optional): Skip Docker image building (use existing images)

### Preconditions
- Minikube cluster running (`minikube status`)
- kubectl configured to use Minikube context
- Helm v3.13+ installed
- Source code directories exist: `./frontend`, `./backend`
- Helm chart exists: `./helm/todo-app`

### Operations (Sequential)

#### Phase 1: Environment Setup
1. Set Minikube Docker environment:
   ```bash
   eval $(minikube docker-env)
   ```
2. Verify Minikube Docker daemon accessible

#### Phase 2: Image Building (unless --skip-build)
1. Build frontend image:
   ```bash
   docker build -t todo-frontend:latest ./frontend
   ```
   - Validation: `docker images | grep todo-frontend` → image exists
2. Build backend image:
   ```bash
   docker build -t todo-backend:latest ./backend
   ```
   - Validation: `docker images | grep todo-backend` → image exists

#### Phase 3: Namespace Creation
1. Create namespace (if not exists):
   ```bash
   kubectl create namespace <namespace> --dry-run=client -o yaml | kubectl apply -f -
   ```

#### Phase 4: Helm Chart Installation
1. Install Helm chart with --wait flag:
   ```bash
   helm install todo-app ./helm/todo-app \
     -n <namespace> \
     --create-namespace \
     --wait \
     --timeout <wait-timeout>
   ```
2. Wait for all deployments to be Ready:
   - Redis StatefulSet (1 pod)
   - MCP Server Deployment (1 pod)
   - Backend Deployment (2 pods via HPA)
   - Frontend Deployment (2 pods via HPA)

#### Phase 5: Validation
1. Verify all pods Running:
   ```bash
   kubectl get pods -n <namespace>
   ```
   - Expected: 6 pods (1 redis, 1 mcp, 2 backend, 2 frontend) with STATUS=Running
2. Verify HPA created:
   ```bash
   kubectl get hpa -n <namespace>
   ```
   - Expected: frontend-hpa (2/5 replicas), backend-hpa (2/5 replicas)
3. Verify Ingress created:
   ```bash
   kubectl get ingress -n <namespace>
   ```
   - Expected: todo-app-ingress with ADDRESS assigned
4. Verify PVC bound:
   ```bash
   kubectl get pvc -n <namespace>
   ```
   - Expected: redis-data-redis-0 with STATUS=Bound

#### Phase 6: Access Information
1. Get Minikube IP:
   ```bash
   minikube ip
   ```
2. Display access instructions:
   ```
   Deployment complete!
   Add to /etc/hosts: <minikube-ip> todo-app.local
   Access frontend: http://todo-app.local/
   Access backend: http://todo-app.local/api/health
   ```

### Success Criteria
- Helm install exit code: 0
- All 6 pods in Running state
- HPA resources created (2)
- Ingress ADDRESS assigned
- PVC bound to PersistentVolume

### Output
```
Building Docker images...
Frontend image built successfully
Backend image built successfully

Installing Helm chart...
NAME: todo-app
LAST DEPLOYED: <timestamp>
NAMESPACE: todo-phaseiv
STATUS: deployed
REVISION: 1

Validating deployment...
✓ All pods Running (6/6)
✓ HPA created (2)
✓ Ingress created with ADDRESS
✓ PVC bound

Deployment complete!
Add to /etc/hosts: <minikube-ip> todo-app.local
Access: http://todo-app.local/
```

### Error Handling
- If Minikube not running: Exit with error "Minikube cluster not running. Run setup-minikube.sh first"
- If Docker build fails: Exit with error "Docker build failed for <service>"
- If Helm install fails: Display `helm status todo-app -n <namespace>` and rollback
- If pods fail to start: Display `kubectl describe pod <pod> -n <namespace>` for debugging
- If timeout exceeded: Exit with error "Deployment timeout exceeded. Check pod status"

---

## Script: test.sh

### Purpose
Execute all 6 test suites to validate deployment correctness.

### Input Parameters
- `--namespace <name>` (optional): Override default namespace (default: todo-phaseiv)
- `--skip-load-test` (optional): Skip load testing (for CI environments)

### Preconditions
- Helm chart deployed (`helm status todo-app -n <namespace>`)
- All pods Running
- /etc/hosts configured with `<minikube-ip> todo-app.local`

### Operations (Sequential)

#### Test Suite 1: Helm Tests
1. Run Helm test suite:
   ```bash
   helm test todo-app -n <namespace>
   ```
2. Verify all test pods succeed

#### Test Suite 2: Ingress Tests
1. Test frontend route:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://todo-app.local/
   ```
   - Expected: HTTP 200
2. Test backend route:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://todo-app.local/api/health
   ```
   - Expected: HTTP 200 with JSON body `{"status": "healthy"}`

#### Test Suite 3: Persistence Tests
1. Write key to Redis:
   ```bash
   kubectl exec redis-0 -n <namespace> -- redis-cli SET test-key "persistence-test"
   ```
2. Delete Redis pod:
   ```bash
   kubectl delete pod redis-0 -n <namespace>
   ```
3. Wait for pod to restart (30s timeout)
4. Read key from Redis:
   ```bash
   kubectl exec redis-0 -n <namespace> -- redis-cli GET test-key
   ```
   - Expected: "persistence-test" (data retained)

#### Test Suite 4: Resilience Tests
1. Get initial frontend pod count:
   ```bash
   kubectl get pods -n <namespace> -l app=frontend --no-headers | wc -l
   ```
2. Delete random frontend pod:
   ```bash
   kubectl delete pod <random-frontend-pod> -n <namespace>
   ```
3. Wait for pod to restart (30s timeout)
4. Verify frontend pod count restored

#### Test Suite 5: Load Tests (unless --skip-load-test)
1. Get initial frontend replica count:
   ```bash
   kubectl get hpa frontend-hpa -n <namespace> -o jsonpath='{.status.currentReplicas}'
   ```
   - Expected: 2 (min replicas)
2. Generate load with Apache Bench:
   ```bash
   ab -n 10000 -c 50 http://todo-app.local/
   ```
3. Wait 2 minutes for HPA to scale
4. Get current frontend replica count:
   ```bash
   kubectl get hpa frontend-hpa -n <namespace> -o jsonpath='{.status.currentReplicas}'
   ```
   - Expected: 3-5 (scaled up)

#### Test Suite 6: E2E Tests
1. Navigate to http://todo-app.local/auth/register
2. Create test user account
3. Log in with test credentials
4. Navigate to /chat
5. Send message "Add task to buy groceries"
6. Verify AI response confirms task creation
7. Query database for task:
   ```bash
   kubectl exec <backend-pod> -n <namespace> -- \
     python -c "from app.database import SessionLocal; from app.models.task import Task; \
     db = SessionLocal(); tasks = db.query(Task).filter(Task.user_id=='<test-user-id>').all(); \
     print([t.title for t in tasks])"
   ```
   - Expected: "Buy groceries" in task list

### Success Criteria
- All Helm tests pass (Phase: Succeeded)
- Ingress routes return HTTP 200
- Redis data persists across pod restart
- Kubernetes recreates deleted pods within 30s
- HPA scales frontend to 3-5 replicas under load
- E2E user flow completes without errors

### Output
```
Running Helm tests...
✓ test-frontend: Succeeded
✓ test-backend: Succeeded
✓ test-mcp: Succeeded
✓ test-redis: Succeeded

Running Ingress tests...
✓ Frontend route: HTTP 200
✓ Backend route: HTTP 200

Running persistence tests...
✓ Redis key written
✓ Redis pod deleted
✓ Redis pod restarted
✓ Redis data retained

Running resilience tests...
✓ Frontend pod deleted
✓ Frontend pod recreated (12s)

Running load tests...
✓ Initial replicas: 2
✓ Load generated (10000 requests)
✓ Current replicas: 4 (scaled up)

Running E2E tests...
✓ User registration successful
✓ User login successful
✓ Chat message sent
✓ Task created in database

All tests passed!
```

### Error Handling
- If Helm test fails: Display test pod logs and exit
- If Ingress test fails: Display Ingress configuration and exit
- If persistence test fails: Display PVC/PV status and exit
- If resilience test fails: Display pod events and exit
- If load test fails: Display HPA status and metrics
- If E2E test fails: Display frontend/backend logs and exit

---

## Contract Validation

All scripts MUST adhere to the following contracts:

### Exit Codes
- 0: Success
- 1: Precondition failure (e.g., Minikube not running)
- 2: Validation failure (e.g., pods not Ready)
- 3: Test failure (e.g., Helm test failed)

### Logging
- All scripts MUST log operations to stdout
- Errors MUST be logged to stderr
- Use prefixes: `[INFO]`, `[WARN]`, `[ERROR]` for log levels

### Idempotency
- All scripts MUST be idempotent (safe to run multiple times)
- `setup-minikube.sh`: Reuse existing cluster if already running
- `deploy.sh`: Use `helm upgrade --install` pattern
- `test.sh`: Clean up test data after execution

### Cleanup
- `deploy.sh` MUST provide uninstall instructions on failure
- `test.sh` MUST delete test pods after execution
- Scripts MUST NOT leave orphan resources on failure
