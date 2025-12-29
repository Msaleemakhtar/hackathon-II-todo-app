# Quickstart: Kubernetes Deployment for Phase IV Todo Chatbot

**Feature**: 001-kubernetes-deployment
**Date**: 2025-12-26
**Estimated Time**: 30 minutes (first-time setup)

---

## Prerequisites

Before starting, ensure you have:

- **Docker Desktop**: Running and accessible
- **System Resources**: Minimum 6 CPU cores and 12GB RAM available (4 CPU + 8GB for Minikube, remainder for host OS)
- **Terminal Access**: bash shell with sudo privileges
- **Network Connectivity**: Access to external services (Neon PostgreSQL, OpenAI API)

---

## Step 1: Setup Minikube Cluster (5 minutes)

```bash
# Navigate to Phase IV kubernetes directory
cd phaseIV/kubernetes

# Run Minikube setup script
./scripts/setup-minikube.sh
```

**Expected Output**:
```
Checking Minikube installation...
✓ Minikube v1.32+ installed
Checking kubectl installation...
✓ kubectl v1.28+ installed
Checking Helm installation...
✓ Helm v3.13+ installed

Starting Minikube cluster...
✓ Minikube started (4 CPU, 8GB RAM)

Enabling addons...
✓ Ingress addon enabled
✓ Metrics Server addon enabled

Minikube cluster ready!
Cluster IP: 192.168.49.2
Add to /etc/hosts: 192.168.49.2 todo-app.local
```

**Action Required**: Add the following line to `/etc/hosts`:
```bash
# For macOS/Linux:
sudo sh -c 'echo "192.168.49.2 todo-app.local" >> /etc/hosts'

# For Windows (run PowerShell as Administrator):
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "192.168.49.2 todo-app.local"
```

---

## Step 2: Configure Secrets (3 minutes)

Create a `values-local.yaml` file with your secrets:

```yaml
# phaseIV/kubernetes/values-local.yaml
secrets:
  # Base64-encode your secrets first:
  # echo -n "postgres://..." | base64

  databaseUrl: "<base64-encoded-neon-postgres-url>"
  openaiApiKey: "<base64-encoded-openai-api-key>"
  betterAuthSecret: "<base64-encoded-better-auth-secret>"
  betterAuthUrl: "<base64-encoded-better-auth-url>"
  redisPassword: ""  # Optional, leave empty for no auth
```

**Example (encode secrets)**:
```bash
# Encode DATABASE_URL
echo -n "postgresql://user:pass@host/db" | base64

# Encode OPENAI_API_KEY
echo -n "sk-proj-..." | base64

# Encode BETTER_AUTH_SECRET
echo -n "your-secret-key" | base64

# Encode BETTER_AUTH_URL
echo -n "http://todo-app.local" | base64
```

**⚠️ IMPORTANT**: Do NOT commit `values-local.yaml` to git. Add to `.gitignore`:
```bash
echo "values-local.yaml" >> .gitignore
```

---

## Step 3: Build and Deploy (15 minutes)

```bash
# Navigate to kubernetes directory
cd phaseIV/kubernetes

# Run deployment script with local values
./scripts/deploy.sh --values=values-local.yaml
```

**Expected Output**:
```
[INFO] Setting Minikube Docker environment...
[INFO] Building Docker images...
[INFO] Building frontend image...
✓ Frontend image built: todo-frontend:latest
[INFO] Building backend image...
✓ Backend image built: todo-backend:latest

[INFO] Installing Helm chart...
NAME: todo-app
LAST DEPLOYED: 2025-12-26 10:30:00
NAMESPACE: todo-phaseiv
STATUS: deployed
REVISION: 1

[INFO] Waiting for deployments to be Ready...
[INFO] Redis StatefulSet: Running (1/1)
[INFO] MCP Server Deployment: Running (1/1)
[INFO] Backend Deployment: Running (2/2)
[INFO] Frontend Deployment: Running (2/2)

[INFO] Validating deployment...
✓ All pods Running (6/6)
✓ HPA created (frontend-hpa, backend-hpa)
✓ Ingress created with ADDRESS: 192.168.49.2
✓ PVC bound (redis-data-redis-0)

Deployment complete!
Access: http://todo-app.local/
```

**Progress Timeline**:
- 0-3 min: Docker image builds
- 3-5 min: Redis StatefulSet ready
- 5-7 min: MCP Server ready
- 7-10 min: Backend ready (database migrations)
- 10-12 min: Frontend ready
- 12-15 min: Ingress ready, validation complete

---

## Step 4: Verify Deployment (5 minutes)

### 4.1 Check Pod Status
```bash
kubectl get pods -n todo-phaseiv
```

**Expected Output**:
```
NAME                        READY   STATUS    RESTARTS   AGE
backend-xxxxx-xxxxx         1/1     Running   0          5m
backend-xxxxx-xxxxx         1/1     Running   0          5m
frontend-xxxxx-xxxxx        1/1     Running   0          4m
frontend-xxxxx-xxxxx        1/1     Running   0          4m
mcp-server-xxxxx-xxxxx      1/1     Running   0          6m
redis-0                     1/1     Running   0          7m
```

### 4.2 Check Services
```bash
kubectl get svc -n todo-phaseiv
```

**Expected Output**:
```
NAME               TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
backend-service    ClusterIP   10.96.xxx.xxx    <none>        8000/TCP   5m
frontend-service   ClusterIP   10.96.xxx.xxx    <none>        3000/TCP   4m
mcp-service        ClusterIP   10.96.xxx.xxx    <none>        8001/TCP   6m
redis-service      ClusterIP   None             <none>        6379/TCP   7m
```

### 4.3 Check Ingress
```bash
kubectl get ingress -n todo-phaseiv
```

**Expected Output**:
```
NAME               CLASS   HOSTS             ADDRESS         PORTS   AGE
todo-app-ingress   nginx   todo-app.local    192.168.49.2    80      3m
```

### 4.4 Check HPA
```bash
kubectl get hpa -n todo-phaseiv
```

**Expected Output**:
```
NAME            REFERENCE             TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
backend-hpa     Deployment/backend    15%/70%   2         5         2          5m
frontend-hpa    Deployment/frontend   10%/70%   2         5         2          4m
```

### 4.5 Test HTTP Routes
```bash
# Test frontend
curl -s -o /dev/null -w "%{http_code}\n" http://todo-app.local/

# Test backend
curl http://todo-app.local/api/health
```

**Expected Output**:
```
200
{"status":"healthy"}
```

---

## Step 5: Access the Application (2 minutes)

1. Open browser: http://todo-app.local/
2. Navigate to signup page: http://todo-app.local/auth/register
3. Create a new user account
4. Log in with your credentials
5. Navigate to chat: http://todo-app.local/chat
6. Send message: "Add task to buy groceries"
7. Verify AI response confirms task creation

**Expected Behavior**:
- Frontend loads correctly (Next.js chat interface)
- User registration succeeds
- Login succeeds and JWT token issued
- Chat interface displays conversation
- AI responds with task creation confirmation
- MCP tool `add_task` invoked successfully

---

## Step 6: Run Tests (Optional, 5 minutes)

```bash
# Run all test suites
cd phaseIV/kubernetes
./scripts/test.sh
```

**Expected Output**:
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
✓ Redis data retained after pod restart

Running resilience tests...
✓ Frontend pod recreated automatically

Running load tests...
✓ HPA scaled frontend to 4 replicas

Running E2E tests...
✓ Complete user flow successful

All tests passed!
```

---

## Common Operations

### View Logs
```bash
# Frontend logs
kubectl logs -f deployment/frontend -n todo-phaseiv

# Backend logs
kubectl logs -f deployment/backend -n todo-phaseiv

# MCP Server logs
kubectl logs -f deployment/mcp-server -n todo-phaseiv

# Redis logs
kubectl logs -f redis-0 -n todo-phaseiv
```

### Scale Replicas Manually
```bash
# Scale frontend to 3 replicas
kubectl scale deployment frontend -n todo-phaseiv --replicas=3

# Scale backend to 4 replicas
kubectl scale deployment backend -n todo-phaseiv --replicas=4
```

### Restart Deployment
```bash
# Restart backend deployment
kubectl rollout restart deployment/backend -n todo-phaseiv

# Restart frontend deployment
kubectl rollout restart deployment/frontend -n todo-phaseiv
```

### Access Pod Shell
```bash
# Access backend pod
kubectl exec -it deployment/backend -n todo-phaseiv -- /bin/bash

# Access Redis pod
kubectl exec -it redis-0 -n todo-phaseiv -- /bin/sh
```

### Update Secrets
```bash
# Update DATABASE_URL secret
kubectl create secret generic todo-app-secrets \
  --from-literal=DATABASE_URL=<new-url> \
  --dry-run=client -o yaml | kubectl apply -n todo-phaseiv -f -

# Restart deployments to pick up new secret
kubectl rollout restart deployment/backend -n todo-phaseiv
```

---

## Troubleshooting

### Issue: Pods stuck in Pending
**Diagnosis**:
```bash
kubectl describe pod <pod-name> -n todo-phaseiv
```
**Common Causes**:
- Insufficient cluster resources (check `kubectl top nodes`)
- PVC not binding (check `kubectl get pvc -n todo-phaseiv`)

**Resolution**:
```bash
# Increase Minikube resources
minikube stop
minikube config set cpus 6
minikube config set memory 12288
minikube start
```

### Issue: Ingress not routing
**Diagnosis**:
```bash
kubectl describe ingress todo-app-ingress -n todo-phaseiv
```
**Common Causes**:
- Ingress Controller not running
- /etc/hosts not configured

**Resolution**:
```bash
# Verify Ingress Controller
kubectl get pods -n ingress-nginx

# Verify /etc/hosts entry
cat /etc/hosts | grep todo-app.local

# Re-enable Ingress addon if needed
minikube addons disable ingress
minikube addons enable ingress
```

### Issue: HPA not scaling
**Diagnosis**:
```bash
kubectl describe hpa frontend-hpa -n todo-phaseiv
kubectl top pods -n todo-phaseiv
```
**Common Causes**:
- Metrics Server not running
- Resource requests not defined

**Resolution**:
```bash
# Verify Metrics Server
kubectl get pods -n kube-system | grep metrics-server

# Re-enable Metrics Server if needed
minikube addons disable metrics-server
minikube addons enable metrics-server
```

### Issue: Backend cannot connect to database
**Diagnosis**:
```bash
kubectl logs deployment/backend -n todo-phaseiv | grep DATABASE
```
**Common Causes**:
- Incorrect DATABASE_URL in Secret
- Network connectivity to Neon PostgreSQL

**Resolution**:
```bash
# Verify Secret exists
kubectl get secret todo-app-secrets -n todo-phaseiv -o yaml

# Test database connectivity from backend pod
kubectl exec -it deployment/backend -n todo-phaseiv -- \
  python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('<database-url>'))"
```

---

## Cleanup (Optional)

### Uninstall Helm Chart
```bash
helm uninstall todo-app -n todo-phaseiv
```

### Delete Namespace
```bash
kubectl delete namespace todo-phaseiv
```

### Stop Minikube
```bash
minikube stop
```

### Delete Minikube Cluster
```bash
minikube delete
```

---

## Next Steps

- **Documentation**: Read KUBERNETES_GUIDE.md for comprehensive deployment guide
- **Operations**: Read RUNBOOK.md for common operational procedures
- **Helm Chart**: Read helm/todo-app/README.md for chart configuration options
- **Testing**: Explore test scripts in `./scripts/test.sh` for validation procedures
- **Monitoring**: Use `kubectl top pods -n todo-phaseiv` to monitor resource usage
- **Scaling**: Experiment with HPA by generating load: `ab -n 10000 -c 50 http://todo-app.local/`

---

## Summary

You have successfully:
- ✅ Setup Minikube cluster with Ingress and Metrics Server
- ✅ Built Docker images for Frontend, Backend, MCP Server
- ✅ Deployed Helm chart with 4 services (Frontend, Backend, MCP, Redis)
- ✅ Configured Nginx Ingress for HTTP routing
- ✅ Enabled Horizontal Pod Autoscaling for Frontend and Backend
- ✅ Configured PersistentVolume for Redis data persistence
- ✅ Verified complete user flow (auth → chat → task creation via MCP tools)

**Access URL**: http://todo-app.local/

**Kubernetes Dashboard** (optional):
```bash
minikube dashboard
```

Congratulations! You've successfully deployed Phase IV Todo Chatbot to Kubernetes. 🎉
