# Operational Runbook - Todo App Phase IV

> **Complete operational guide for maintaining the AI Task Assistant Kubernetes deployment**
>
> Includes both traditional kubectl commands and kubectl-ai natural language alternatives for naive developers.

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [Health Checks](#health-checks)
3. [Common Operations](#common-operations)
4. [Incident Response](#incident-response)
5. [Monitoring](#monitoring)
6. [Backup and Recovery](#backup-and-recovery)
7. [Performance Tuning](#performance-tuning)
8. [Security Operations](#security-operations)
9. [Using kubectl-ai](#using-kubectl-ai)
10. [Appendix](#appendix)

---

## Service Overview

### Architecture

```
Internet → Nginx Ingress → Frontend/Backend → MCP Server → Redis
                                ↓
                         Neon PostgreSQL (External)
```

### Components

| Component | Type | Replicas | Purpose |
|-----------|------|----------|---------|
| **Frontend** | Deployment | 2-5 (HPA) | Next.js web UI with ChatKit |
| **Backend** | Deployment | 2-5 (HPA) | FastAPI REST API + ChatKit adapter |
| **MCP Server** | Deployment | 1 | AI agent MCP tools |
| **Redis** | StatefulSet | 1 | Session cache (persistent) |
| **Ingress** | Ingress | 1 | HTTPS routing with TLS |

### Key Metrics

- **Target Response Time**: p95 < 200ms
- **Target Availability**: 99.9%
- **HPA Scale Time**: 2 minutes under load
- **Pod Restart Time**: 30 seconds
- **Database**: Neon Serverless PostgreSQL (external)

### Environment

- **Namespace**: `todo-phaseiv`
- **Domain**: `todo-app.local` (HTTPS)
- **Ingress Class**: `nginx`
- **Auto-scaling**: HPA enabled (CPU 70%, Memory 80%)

---

## Health Checks

### Quick Health Check

**Traditional kubectl:**
```bash
# Check all pods are running
kubectl get pods -n todo-phaseiv

# All pods should show:
# STATUS: Running
# READY: 1/1 (or 2/2 for deployments with multiple containers)
# RESTARTS: 0 (or low number)
```

**With kubectl-ai:**
```bash
kubectl-ai "show me all pods in todo-phaseiv namespace"
kubectl-ai "are all my pods healthy in todo-phaseiv"
kubectl-ai "check pod status and show any that are not running"
```

### Detailed Health Checks

#### 1. Frontend Health

**Traditional kubectl:**
```bash
# Check HTTPS endpoint
curl -k https://todo-app.local/chat

# Expected: HTML page loads

# Check pod logs
kubectl logs -l app=frontend -n todo-phaseiv --tail=50

# Check metrics
kubectl top pods -l app=frontend -n todo-phaseiv

# Check specific pod
kubectl describe pod <pod-name> -n todo-phaseiv
```

**With kubectl-ai:**
```bash
kubectl-ai "show me frontend pod logs in todo-phaseiv"
kubectl-ai "show CPU and memory usage for frontend pods"
kubectl-ai "describe the frontend pods and show any errors"
kubectl-ai "are the frontend pods healthy"
```

#### 2. Backend Health

**Traditional kubectl:**
```bash
# Check health endpoint
curl -k https://todo-app.local/api/health

# Expected: {"status":"healthy","service":"phaseiv-backend","adapters":["chatkit"]}

# Check database connectivity
kubectl exec -it deployment/backend -n todo-phaseiv -- \
  python -c "from app.database import engine; engine.connect(); print('DB OK')"

# Check pod logs
kubectl logs -l app=backend -n todo-phaseiv --tail=50

# Check for errors
kubectl logs -l app=backend -n todo-phaseiv | grep -i error
```

**With kubectl-ai:**
```bash
kubectl-ai "show me backend pod logs in todo-phaseiv"
kubectl-ai "find errors in backend pods"
kubectl-ai "show the last 100 lines of backend logs"
kubectl-ai "is the backend deployment healthy"
kubectl-ai "check if backend can connect to database"
```

#### 3. MCP Server Health

**Traditional kubectl:**
```bash
# Check MCP pod
kubectl get pods -l app=mcp-server -n todo-phaseiv

# Test MCP endpoint from backend pod
kubectl exec deployment/backend -n todo-phaseiv -- \
  curl -s http://mcp-service:8001/mcp

# Check MCP logs
kubectl logs -l app=mcp-server -n todo-phaseiv --tail=50

# Check for MCP tool errors
kubectl logs -l app=mcp-server -n todo-phaseiv | grep -i "tool"
```

**With kubectl-ai:**
```bash
kubectl-ai "show mcp-server pod status"
kubectl-ai "show logs from mcp-server"
kubectl-ai "check if mcp-server is responding"
kubectl-ai "find errors in mcp-server logs"
```

#### 4. Redis Health

**Traditional kubectl:**
```bash
# Ping Redis
kubectl exec redis-0 -n todo-phaseiv -- redis-cli PING

# Expected: PONG

# Check Redis info
kubectl exec redis-0 -n todo-phaseiv -- redis-cli INFO

# Check memory usage
kubectl exec redis-0 -n todo-phaseiv -- redis-cli INFO memory

# Check persistence
kubectl exec redis-0 -n todo-phaseiv -- redis-cli INFO persistence

# Check PVC status
kubectl get pvc -n todo-phaseiv

# Check key count
kubectl exec redis-0 -n todo-phaseiv -- redis-cli DBSIZE
```

**With kubectl-ai:**
```bash
kubectl-ai "show redis pod status in todo-phaseiv"
kubectl-ai "check if redis is running"
kubectl-ai "show persistent volume claims in todo-phaseiv"
kubectl-ai "is the redis storage working"
```

#### 5. Ingress Health

**Traditional kubectl:**
```bash
# Check Ingress status
kubectl get ingress -n todo-phaseiv

# Check Ingress controller
kubectl get pods -n ingress-nginx

# Check TLS certificate
kubectl get secret todo-app-tls -n todo-phaseiv

# Check Ingress logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller --tail=100

# Test HTTPS routing
curl -k -I https://todo-app.local/api/health
curl -k -I https://todo-app.local/chat
```

**With kubectl-ai:**
```bash
kubectl-ai "show ingress status in todo-phaseiv"
kubectl-ai "is the ingress controller healthy"
kubectl-ai "show TLS secrets in todo-phaseiv"
kubectl-ai "debug ingress routing issues"
kubectl-ai "check if HTTPS is working"
```

---

## Common Operations

### Restart Services

#### Restart All Services

**Traditional kubectl:**
```bash
# Restart all deployments
kubectl rollout restart deployment -n todo-phaseiv

# Watch progress
kubectl rollout status deployment/frontend -n todo-phaseiv
kubectl rollout status deployment/backend -n todo-phaseiv
kubectl rollout status deployment/mcp-server -n todo-phaseiv
```

**With kubectl-ai:**
```bash
kubectl-ai "restart all deployments in todo-phaseiv"
kubectl-ai "show rollout status for all deployments"
kubectl-ai "are all deployments ready after restart"
```

#### Restart Specific Service

**Traditional kubectl:**
```bash
# Restart frontend
kubectl rollout restart deployment/frontend -n todo-phaseiv

# Restart backend
kubectl rollout restart deployment/backend -n todo-phaseiv

# Restart MCP Server
kubectl rollout restart deployment/mcp-server -n todo-phaseiv

# Restart Redis (StatefulSet)
kubectl delete pod redis-0 -n todo-phaseiv
# StatefulSet automatically recreates with same name and PVC
```

**With kubectl-ai:**
```bash
kubectl-ai "restart the frontend deployment in todo-phaseiv"
kubectl-ai "restart backend deployment"
kubectl-ai "restart mcp-server"
kubectl-ai "restart redis pod in todo-phaseiv"
```

#### Watch Rollout Progress

**Traditional kubectl:**
```bash
kubectl rollout status deployment/frontend -n todo-phaseiv

# Expected output:
# Waiting for deployment "frontend" rollout to finish: 1 of 2 updated replicas are available...
# deployment "frontend" successfully rolled out
```

**With kubectl-ai:**
```bash
kubectl-ai "show rollout status for frontend deployment"
kubectl-ai "is the frontend deployment rollout complete"
kubectl-ai "watch the frontend deployment progress"
```

### Scale Services

#### Manual Scaling

**Traditional kubectl:**
```bash
# Scale frontend to 3 replicas
kubectl scale deployment/frontend --replicas=3 -n todo-phaseiv

# Scale backend to 4 replicas
kubectl scale deployment/backend --replicas=4 -n todo-phaseiv

# Verify scaling
kubectl get pods -l app=frontend -n todo-phaseiv
kubectl get pods -l app=backend -n todo-phaseiv

# Note: HPA will override manual scaling after metrics stabilize
```

**With kubectl-ai:**
```bash
kubectl-ai "scale frontend to 3 replicas in todo-phaseiv"
kubectl-ai "scale backend to 4 replicas"
kubectl-ai "show how many frontend pods are running"
kubectl-ai "is the scaling complete"
```

#### Disable HPA (for manual control)

**Traditional kubectl:**
```bash
# Delete HPA resources
kubectl delete hpa frontend-hpa -n todo-phaseiv
kubectl delete hpa backend-hpa -n todo-phaseiv

# Now manual scaling will persist
kubectl scale deployment/frontend --replicas=3 -n todo-phaseiv
```

**With kubectl-ai:**
```bash
kubectl-ai "delete the hpa for frontend in todo-phaseiv"
kubectl-ai "disable autoscaling for backend"
kubectl-ai "show all hpa resources in todo-phaseiv"
```

#### Re-enable HPA

**Traditional kubectl:**
```bash
# Upgrade Helm release to recreate HPA
helm upgrade todo-app /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app \
  -n todo-phaseiv \
  -f /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app/values-local.yaml \
  -f /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app/values-tls.yaml \
  --reuse-values

# Verify HPA is running
kubectl get hpa -n todo-phaseiv
```

**With kubectl-ai:**
```bash
kubectl-ai "show hpa status in todo-phaseiv"
kubectl-ai "is autoscaling enabled for frontend"
kubectl-ai "what is the current CPU target for backend hpa"
```

### Update Configuration

#### Update Environment Variables

**Traditional kubectl:**
```bash
# Edit ConfigMap
kubectl edit configmap todo-app-config -n todo-phaseiv

# Or update specific value
kubectl patch configmap todo-app-config -n todo-phaseiv \
  --type merge \
  -p '{"data":{"REDIS_PORT":"6380"}}'

# Restart pods to pick up changes
kubectl rollout restart deployment -n todo-phaseiv

# Verify new config
kubectl get configmap todo-app-config -n todo-phaseiv -o yaml
```

**With kubectl-ai:**
```bash
kubectl-ai "show the configmap for todo-app in todo-phaseiv"
kubectl-ai "edit the configmap todo-app-config"
kubectl-ai "restart deployments to pick up new config"
```

#### Update Secrets

**Traditional kubectl:**
```bash
# Create new secret value (base64 encoded)
echo -n 'new-secret-value' | base64
# Output: bmV3LXNlY3JldC12YWx1ZQ==

# Edit secret
kubectl edit secret todo-app-secrets -n todo-phaseiv

# Or patch specific value
kubectl patch secret todo-app-secrets -n todo-phaseiv \
  --type merge \
  -p '{"data":{"BETTER_AUTH_SECRET":"bmV3LXNlY3JldC12YWx1ZQ=="}}'

# Restart pods to pick up changes
kubectl rollout restart deployment -n todo-phaseiv
```

**With kubectl-ai:**
```bash
kubectl-ai "show secrets in todo-phaseiv namespace"
kubectl-ai "edit the secret todo-app-secrets"
kubectl-ai "restart all deployments to use new secrets"
```

#### Update via Helm

**Traditional kubectl:**
```bash
# Edit values-local.yaml with new values
nano /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app/values-local.yaml

# Upgrade release
helm upgrade todo-app /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app \
  -n todo-phaseiv \
  -f /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app/values-local.yaml \
  -f /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app/values-tls.yaml \
  --wait

# Check release status
helm status todo-app -n todo-phaseiv

# View release history
helm history todo-app -n todo-phaseiv
```

**With kubectl-ai:**
```bash
kubectl-ai "show helm releases in todo-phaseiv"
kubectl-ai "show deployment status after helm upgrade"
kubectl-ai "are all pods running after update"
```

### View Logs

#### Stream Logs in Real-Time

**Traditional kubectl:**
```bash
# All backend logs (streaming)
kubectl logs -f -l app=backend -n todo-phaseiv

# All frontend logs
kubectl logs -f -l app=frontend -n todo-phaseiv

# MCP Server logs
kubectl logs -f -l app=mcp-server -n todo-phaseiv

# Redis logs
kubectl logs -f redis-0 -n todo-phaseiv

# All pods with label
kubectl logs -f -l app=backend -n todo-phaseiv --all-containers=true
```

**With kubectl-ai:**
```bash
kubectl-ai "show me live logs from backend pods"
kubectl-ai "tail frontend logs in real-time"
kubectl-ai "stream logs from mcp-server"
kubectl-ai "show redis logs"
```

#### View Historical Logs

**Traditional kubectl:**
```bash
# Last 1 hour
kubectl logs -l app=backend -n todo-phaseiv \
  --since=1h \
  --timestamps

# Last 100 lines
kubectl logs -l app=backend -n todo-phaseiv \
  --tail=100

# From specific time
kubectl logs -l app=backend -n todo-phaseiv \
  --since-time="2025-01-15T10:00:00Z"

# Search for errors
kubectl logs -l app=backend -n todo-phaseiv | grep -i error

# Count errors
kubectl logs -l app=backend -n todo-phaseiv | grep -i error | wc -l
```

**With kubectl-ai:**
```bash
kubectl-ai "show me the last 100 lines of backend logs"
kubectl-ai "find errors in backend pods from the last hour"
kubectl-ai "show logs with timestamps"
kubectl-ai "how many errors are in the backend logs"
```

#### View Previous Container Logs (after crash)

**Traditional kubectl:**
```bash
# View logs from crashed container
kubectl logs <pod-name> -n todo-phaseiv --previous

# With label selector
kubectl logs -l app=backend -n todo-phaseiv --previous --tail=100
```

**With kubectl-ai:**
```bash
kubectl-ai "show logs from the previous backend container"
kubectl-ai "what caused the backend pod to crash"
kubectl-ai "show crash logs for frontend"
```

### Access Pods

**Traditional kubectl:**
```bash
# Shell into backend pod
kubectl exec -it deployment/backend -n todo-phaseiv -- bash

# Shell into frontend pod
kubectl exec -it deployment/frontend -n todo-phaseiv -- sh

# Run single command in pod
kubectl exec deployment/backend -n todo-phaseiv -- python --version
kubectl exec deployment/backend -n todo-phaseiv -- env | grep DATABASE_URL

# Redis CLI
kubectl exec -it redis-0 -n todo-phaseiv -- redis-cli

# Copy files from pod
kubectl cp todo-phaseiv/<pod-name>:/app/logs.txt ./local-logs.txt

# Copy files to pod
kubectl cp ./local-file.txt todo-phaseiv/<pod-name>:/tmp/
```

**With kubectl-ai:**
```bash
kubectl-ai "give me a shell in the backend pod"
kubectl-ai "run python version command in backend"
kubectl-ai "show environment variables in backend pod"
kubectl-ai "connect to redis cli"
```

---

## Incident Response

### High-Level Response Process

1. **Detect**: Monitor alerts, health checks, user reports
2. **Assess**: Determine severity and impact
3. **Mitigate**: Immediate actions to restore service
4. **Resolve**: Root cause fix
5. **Document**: Post-incident review

### Severity Levels

| Severity | Definition | Response Time | Example |
|----------|------------|---------------|---------|
| **P0** | Service down | Immediate | All pods crashing |
| **P1** | Degraded service | 15 minutes | High error rate |
| **P2** | Partial impact | 1 hour | Single pod down |
| **P3** | Minimal impact | Next business day | Slow response times |

### Common Incidents

#### 1. All Pods Crashing (P0)

**Symptoms:**
```bash
kubectl get pods -n todo-phaseiv
# All pods show CrashLoopBackOff or Error
```

**Response:**

**Traditional kubectl:**
```bash
# 1. Check recent changes
kubectl rollout history deployment/backend -n todo-phaseiv
kubectl rollout history deployment/frontend -n todo-phaseiv

# 2. Check pod events
kubectl describe pods -n todo-phaseiv | grep -A 10 Events

# 3. Check logs
kubectl logs -l app=backend -n todo-phaseiv --tail=100
kubectl logs -l app=frontend -n todo-phaseiv --tail=100

# 4. Common causes and fixes:

# Cause: Bad configuration → Rollback Helm release
helm rollback todo-app -n todo-phaseiv

# Cause: Database connection failure → Verify DATABASE_URL secret
kubectl get secret todo-app-secrets -n todo-phaseiv -o yaml
kubectl exec deployment/backend -n todo-phaseiv -- env | grep DATABASE_URL

# Cause: Resource exhaustion → Check node resources
kubectl describe node minikube
kubectl top nodes

# 5. If needed, restart Minikube
minikube stop
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress
```

**With kubectl-ai:**
```bash
kubectl-ai "why are all my pods crashing in todo-phaseiv"
kubectl-ai "show me errors from crashed pods"
kubectl-ai "check if the cluster has enough resources"
kubectl-ai "show recent deployment changes"
kubectl-ai "rollback the last deployment"
```

#### 2. High Error Rate (P1)

**Symptoms:**
```bash
# Logs show many errors
kubectl logs -l app=backend -n todo-phaseiv | grep -i error | wc -l
# High count (>100 in 5 minutes)
```

**Response:**

**Traditional kubectl:**
```bash
# 1. Identify error type
kubectl logs -l app=backend -n todo-phaseiv | grep -i error | tail -50

# 2. Common causes and fixes:

# Cause: Database connection pool exhausted → Scale backend
kubectl scale deployment/backend --replicas=5 -n todo-phaseiv

# Cause: Redis connection issues → Restart Redis
kubectl delete pod redis-0 -n todo-phaseiv
kubectl wait --for=condition=ready pod/redis-0 -n todo-phaseiv --timeout=60s

# Cause: External API failures (OpenAI) → Check API status
curl https://status.openai.com/api/v2/status.json

# 3. Monitor recovery
watch kubectl get pods -n todo-phaseiv
kubectl logs -f -l app=backend -n todo-phaseiv | grep -i error
```

**With kubectl-ai:**
```bash
kubectl-ai "find errors in backend logs"
kubectl-ai "what type of errors are most common"
kubectl-ai "scale backend to 5 replicas to handle load"
kubectl-ai "restart redis to fix connection issues"
kubectl-ai "is the error rate decreasing"
```

#### 3. Pod Not Starting (P2)

**Symptoms:**
```bash
kubectl get pods -n todo-phaseiv
# One pod stuck in Pending, ImagePullBackOff, or CrashLoopBackOff
```

**Response:**

**Traditional kubectl:**
```bash
# 1. Get pod details
kubectl describe pod <pod-name> -n todo-phaseiv

# 2. Check common issues:

# Issue: ImagePullBackOff → Rebuild image in Minikube
eval $(minikube docker-env)
cd /home/salim/Desktop/hackathon-II-todo-app/phaseIV
docker build -t todo-backend:latest backend
docker build -t todo-frontend:latest frontend

# Issue: Pending (insufficient resources) → Check node capacity
kubectl describe node minikube | grep -A 10 "Allocated resources"
# If needed, increase Minikube resources
minikube stop
minikube delete
minikube start --cpus=6 --memory=12288 --driver=docker

# Issue: CrashLoopBackOff → Check logs for startup errors
kubectl logs <pod-name> -n todo-phaseiv
kubectl logs <pod-name> -n todo-phaseiv --previous

# 3. Force recreate pod
kubectl delete pod <pod-name> -n todo-phaseiv
```

**With kubectl-ai:**
```bash
kubectl-ai "why isn't my backend pod starting"
kubectl-ai "describe the pod that's failing"
kubectl-ai "show events for the failing pod"
kubectl-ai "check if there are resource constraints"
kubectl-ai "restart the failing pod"
```

#### 4. Ingress Not Accessible (P1)

**Symptoms:**
```bash
curl -k https://todo-app.local
# Connection refused or timeout
```

**Response:**

**Traditional kubectl:**
```bash
# 1. Check Ingress status
kubectl get ingress -n todo-phaseiv
kubectl describe ingress todo-app-ingress -n todo-phaseiv

# 2. Check Ingress Controller
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller --tail=100

# 3. Restart Ingress Controller if needed
kubectl rollout restart deployment ingress-nginx-controller -n ingress-nginx

# 4. Verify /etc/hosts
cat /etc/hosts | grep todo-app.local
# Expected: <minikube-ip> todo-app.local

# If missing, add it:
echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts

# 5. Check TLS certificate
kubectl get secret todo-app-tls -n todo-phaseiv
kubectl describe secret todo-app-tls -n todo-phaseiv

# 6. Test backend directly (bypass Ingress)
kubectl port-forward svc/backend-service 8000:8000 -n todo-phaseiv &
curl http://localhost:8000/health

# 7. Test frontend directly
kubectl port-forward svc/frontend-service 3000:3000 -n todo-phaseiv &
curl http://localhost:3000
```

**With kubectl-ai:**
```bash
kubectl-ai "why can't I access the ingress"
kubectl-ai "check if ingress controller is running"
kubectl-ai "show ingress configuration"
kubectl-ai "debug ingress routing issues"
kubectl-ai "is TLS configured correctly"
```

#### 5. HPA Not Scaling (P2)

**Symptoms:**
```bash
kubectl get hpa -n todo-phaseiv
# TARGETS show <unknown>/70% or metrics not available
```

**Response:**

**Traditional kubectl:**
```bash
# 1. Check Metrics Server
kubectl get deployment metrics-server -n kube-system
kubectl logs -n kube-system -l k8s-app=metrics-server --tail=50

# 2. Restart Metrics Server
kubectl rollout restart deployment metrics-server -n kube-system

# 3. Wait for metrics to populate (1-2 minutes)
kubectl top pods -n todo-phaseiv
kubectl top nodes

# 4. If still not working, re-enable addon
minikube addons disable metrics-server
minikube addons enable metrics-server

# 5. Verify HPA can read metrics
kubectl describe hpa frontend-hpa -n todo-phaseiv
kubectl describe hpa backend-hpa -n todo-phaseiv

# 6. Manual scaling as workaround
kubectl scale deployment/frontend --replicas=3 -n todo-phaseiv
```

**With kubectl-ai:**
```bash
kubectl-ai "why isn't autoscaling working"
kubectl-ai "show metrics server status"
kubectl-ai "can hpa read pod metrics"
kubectl-ai "show CPU usage for all pods"
kubectl-ai "is autoscaling enabled for frontend"
```

#### 6. ChatKit Not Loading (P1)

**Symptoms:**
- Browser console shows errors
- ChatKit UI blank or not rendering
- "Domain not allowed" errors

**Response:**

**Traditional kubectl:**
```bash
# 1. Check backend logs for ChatKit errors
kubectl logs -l app=backend -n todo-phaseiv | grep -i chatkit

# 2. Verify OPENAI_API_KEY is set
kubectl exec deployment/backend -n todo-phaseiv -- env | grep OPENAI_API_KEY

# 3. Check HTTPS is working (ChatKit requires HTTPS)
curl -k -I https://todo-app.local/chat
# Expected: HTTP/2 200

# 4. Verify TLS certificate
kubectl get secret todo-app-tls -n todo-phaseiv

# 5. Check browser console for errors
# Open: https://todo-app.local/chat
# Browser DevTools → Console tab

# 6. Restart backend to reload ChatKit
kubectl rollout restart deployment/backend -n todo-phaseiv

# 7. Verify ChatKit domain key (if using domain validation)
kubectl get configmap todo-app-config -n todo-phaseiv -o yaml | grep CHATKIT_DOMAIN_KEY
```

**With kubectl-ai:**
```bash
kubectl-ai "find chatkit errors in backend logs"
kubectl-ai "is the openai api key configured"
kubectl-ai "check if https is working"
kubectl-ai "restart backend to fix chatkit"
kubectl-ai "show chatkit configuration"
```

---

## Monitoring

### Resource Usage

**Traditional kubectl:**
```bash
# Pod CPU and memory usage
kubectl top pods -n todo-phaseiv

# Sorted by CPU
kubectl top pods -n todo-phaseiv --sort-by=cpu

# Sorted by memory
kubectl top pods -n todo-phaseiv --sort-by=memory

# Node resource usage
kubectl top nodes

# HPA status (watch mode updates every few seconds)
kubectl get hpa -n todo-phaseiv -w

# Detailed HPA information
kubectl describe hpa frontend-hpa -n todo-phaseiv
kubectl describe hpa backend-hpa -n todo-phaseiv
```

**With kubectl-ai:**
```bash
kubectl-ai "show CPU and memory usage for all pods"
kubectl-ai "which pods are using the most CPU"
kubectl-ai "which pods are using the most memory"
kubectl-ai "show autoscaling status"
kubectl-ai "is the cluster running out of resources"
```

### Event Monitoring

**Traditional kubectl:**
```bash
# Recent events (sorted by time)
kubectl get events -n todo-phaseiv --sort-by='.lastTimestamp'

# Watch events in real-time
kubectl get events -n todo-phaseiv -w

# Filter warning events
kubectl get events -n todo-phaseiv --field-selector type=Warning

# Filter by specific resource
kubectl get events -n todo-phaseiv --field-selector involvedObject.name=backend-<pod-id>

# Last 10 events
kubectl get events -n todo-phaseiv --sort-by='.lastTimestamp' | tail -10
```

**With kubectl-ai:**
```bash
kubectl-ai "show recent events in todo-phaseiv"
kubectl-ai "show warning events"
kubectl-ai "are there any errors in cluster events"
kubectl-ai "what happened to the backend pod"
```

### Continuous Monitoring

**Traditional kubectl:**
```bash
# Watch pod status (updates every 2 seconds)
watch kubectl get pods -n todo-phaseiv

# Watch HPA scaling
watch kubectl get hpa -n todo-phaseiv

# Monitor logs continuously (with error filtering)
kubectl logs -f -l app=backend -n todo-phaseiv | grep -i error

# Monitor multiple resources
watch 'kubectl get pods,svc,ingress -n todo-phaseiv'

# Monitor resource usage
watch kubectl top pods -n todo-phaseiv
```

**With kubectl-ai:**
```bash
kubectl-ai "watch pod status in todo-phaseiv"
kubectl-ai "monitor autoscaling in real-time"
kubectl-ai "stream logs and show errors only"
kubectl-ai "watch resource usage"
```

---

## Backup and Recovery

### Redis Backup

#### Manual Backup

**Traditional kubectl:**
```bash
# Trigger background save
kubectl exec redis-0 -n todo-phaseiv -- redis-cli BGSAVE

# Wait for completion (check every 10 seconds)
kubectl exec redis-0 -n todo-phaseiv -- redis-cli LASTSAVE

# Copy dump to local machine
kubectl cp todo-phaseiv/redis-0:/data/dump.rdb \
  ./backups/redis-$(date +%Y%m%d-%H%M%S).rdb

# Verify backup
ls -lh ./backups/
```

**With kubectl-ai:**
```bash
kubectl-ai "trigger redis backup in todo-phaseiv"
kubectl-ai "check if redis backup is complete"
kubectl-ai "copy redis data to local machine"
```

#### Automated Backup Script

Create file: `backup-redis.sh`
```bash
#!/bin/bash
# Automated Redis backup script

DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="./backups"
NAMESPACE="todo-phaseiv"
POD_NAME="redis-0"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Starting Redis backup at $DATE..."

# Trigger background save
kubectl exec $POD_NAME -n $NAMESPACE -- redis-cli BGSAVE

# Wait for save to complete
echo "Waiting 10 seconds for backup to complete..."
sleep 10

# Copy backup file
echo "Copying backup file..."
kubectl cp $NAMESPACE/$POD_NAME:/data/dump.rdb \
  $BACKUP_DIR/redis-$DATE.rdb

# Verify backup
if [ -f "$BACKUP_DIR/redis-$DATE.rdb" ]; then
  SIZE=$(du -h "$BACKUP_DIR/redis-$DATE.rdb" | cut -f1)
  echo "✅ Backup created: $BACKUP_DIR/redis-$DATE.rdb ($SIZE)"
else
  echo "❌ Backup failed!"
  exit 1
fi

# Keep only last 7 backups
echo "Cleaning old backups (keeping last 7)..."
ls -t $BACKUP_DIR/redis-*.rdb | tail -n +8 | xargs -r rm

echo "Backup complete!"
```

**Usage:**
```bash
chmod +x backup-redis.sh
./backup-redis.sh
```

### Redis Recovery

**Traditional kubectl:**
```bash
# 1. Stop writes to Redis (scale backend to 0)
kubectl scale deployment/backend --replicas=0 -n todo-phaseiv
kubectl scale deployment/mcp-server --replicas=0 -n todo-phaseiv

# Wait for backends to terminate
kubectl wait --for=delete pod -l app=backend -n todo-phaseiv --timeout=60s

# 2. Copy backup to Redis pod
kubectl cp ./backups/redis-20250126-120000.rdb \
  todo-phaseiv/redis-0:/data/dump.rdb

# 3. Restart Redis (StatefulSet will recreate)
kubectl delete pod redis-0 -n todo-phaseiv

# Wait for pod to be ready
kubectl wait --for=condition=ready pod/redis-0 -n todo-phaseiv --timeout=60s

# 4. Verify data restored
kubectl exec redis-0 -n todo-phaseiv -- redis-cli DBSIZE
# Expected: Non-zero number of keys

# 5. Scale backend back up
kubectl scale deployment/backend --replicas=2 -n todo-phaseiv
kubectl scale deployment/mcp-server --replicas=1 -n todo-phaseiv

# Verify services are healthy
kubectl get pods -n todo-phaseiv
```

**With kubectl-ai:**
```bash
kubectl-ai "scale backend to 0 replicas"
kubectl-ai "restart redis pod"
kubectl-ai "check if redis has data"
kubectl-ai "scale backend back to 2 replicas"
```

### PVC Snapshot (Manual)

**Traditional kubectl:**
```bash
# List PVCs
kubectl get pvc -n todo-phaseiv

# Describe PVC to see volume details
kubectl describe pvc redis-data-redis-0 -n todo-phaseiv

# Create manual backup of PV data (Minikube hostPath)
minikube ssh
sudo tar czf /tmp/redis-pv-backup.tar.gz /tmp/hostpath-provisioner/todo-phaseiv/redis-data-redis-0
exit

# Copy from Minikube to local machine
minikube cp /tmp/redis-pv-backup.tar.gz ./backups/redis-pv-$(date +%Y%m%d).tar.gz

# Verify backup
ls -lh ./backups/
```

**With kubectl-ai:**
```bash
kubectl-ai "show persistent volumes in todo-phaseiv"
kubectl-ai "describe the redis pvc"
kubectl-ai "how much storage is the redis pvc using"
```

### Database Backup (Neon PostgreSQL)

**Note**: Neon provides automatic backups via their console.

**Manual Export:**

**Traditional kubectl:**
```bash
# Get database URL (base64 encoded in secret)
kubectl get secret todo-app-secrets -n todo-phaseiv -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Export from backend pod
kubectl exec -it deployment/backend -n todo-phaseiv -- bash

# Inside pod:
pg_dump $DATABASE_URL > /tmp/backup-$(date +%Y%m%d).sql

# Exit pod
exit

# Copy backup from pod
kubectl cp todo-phaseiv/<backend-pod-name>:/tmp/backup-20250126.sql \
  ./backups/postgres-$(date +%Y%m%d).sql

# Verify backup
ls -lh ./backups/postgres-*.sql
```

**With kubectl-ai:**
```bash
kubectl-ai "give me a shell in the backend pod to run database backup"
kubectl-ai "show the database url secret"
```

---

## Performance Tuning

### Resource Optimization

#### Increase Pod Resources

**Edit Helm values:**
```bash
nano /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app/values-local.yaml
```

**Increase backend resources:**
```yaml
backend:
  resources:
    requests:
      cpu: 1000m      # Was 500m
      memory: 1024Mi  # Was 512Mi
    limits:
      cpu: 2000m      # Was 1000m
      memory: 2048Mi  # Was 1024Mi
```

**Upgrade Helm release:**
```bash
helm upgrade todo-app /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app \
  -n todo-phaseiv \
  -f /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app/values-local.yaml \
  -f /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app/values-tls.yaml \
  --wait

# Verify new resources
kubectl describe pod -l app=backend -n todo-phaseiv | grep -A 10 "Limits\|Requests"
```

**With kubectl-ai:**
```bash
kubectl-ai "show resource limits for backend pods"
kubectl-ai "are backend pods cpu constrained"
kubectl-ai "show memory usage compared to limits"
```

#### Adjust HPA Thresholds

**Edit values-local.yaml:**
```yaml
frontend:
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10  # Increased from 5
    targetCPUUtilizationPercentage: 60  # Lowered from 70 (scales faster)
    targetMemoryUtilizationPercentage: 70  # Lowered from 80

backend:
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10  # Increased from 5
    targetCPUUtilizationPercentage: 60
    targetMemoryUtilizationPercentage: 70
```

**Upgrade Helm release:**
```bash
helm upgrade todo-app /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app \
  -n todo-phaseiv \
  -f /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app/values-local.yaml \
  -f /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app/values-tls.yaml

# Verify new HPA settings
kubectl describe hpa frontend-hpa -n todo-phaseiv
kubectl describe hpa backend-hpa -n todo-phaseiv
```

**With kubectl-ai:**
```bash
kubectl-ai "show autoscaling configuration"
kubectl-ai "what are the CPU targets for hpa"
kubectl-ai "is autoscaling working efficiently"
```

### Redis Performance

#### Monitor Redis Performance

**Traditional kubectl:**
```bash
# Get Redis statistics
kubectl exec redis-0 -n todo-phaseiv -- redis-cli INFO stats

# Monitor in real-time (updates every second)
kubectl exec redis-0 -n todo-phaseiv -- redis-cli --stat

# Check memory usage
kubectl exec redis-0 -n todo-phaseiv -- redis-cli INFO memory

# Check connected clients
kubectl exec redis-0 -n todo-phaseiv -- redis-cli CLIENT LIST

# Check slow queries (>10ms)
kubectl exec redis-0 -n todo-phaseiv -- redis-cli SLOWLOG GET 10
```

**With kubectl-ai:**
```bash
kubectl-ai "show redis performance stats"
kubectl-ai "how many clients are connected to redis"
kubectl-ai "show redis memory usage"
```

#### Redis Tuning

**Edit values-local.yaml to increase Redis memory:**
```yaml
redis:
  resources:
    requests:
      cpu: 250m
      memory: 512Mi  # Increased from 256Mi
    limits:
      cpu: 500m
      memory: 1024Mi  # Increased from 512Mi
```

**Configure eviction policy:**
```bash
# Configure Redis to evict least recently used keys when maxmemory is reached
kubectl exec redis-0 -n todo-phaseiv -- \
  redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Set max memory (90% of container limit)
kubectl exec redis-0 -n todo-phaseiv -- \
  redis-cli CONFIG SET maxmemory 461373440  # 440MB (90% of 512MB)

# Verify configuration
kubectl exec redis-0 -n todo-phaseiv -- \
  redis-cli CONFIG GET maxmemory-policy

kubectl exec redis-0 -n todo-phaseiv -- \
  redis-cli CONFIG GET maxmemory

# Make configuration persistent (add to ConfigMap)
kubectl exec redis-0 -n todo-phaseiv -- \
  redis-cli CONFIG REWRITE
```

**With kubectl-ai:**
```bash
kubectl-ai "what is the redis eviction policy"
kubectl-ai "show redis configuration"
kubectl-ai "is redis running out of memory"
```

---

## Security Operations

### Rotate Secrets

**Traditional kubectl:**
```bash
# 1. Generate new secret
NEW_SECRET=$(openssl rand -base64 32)
echo "New secret: $NEW_SECRET"

# Base64 encode for Kubernetes
NEW_SECRET_B64=$(echo -n "$NEW_SECRET" | base64)
echo "Base64: $NEW_SECRET_B64"

# 2. Update secret
kubectl edit secret todo-app-secrets -n todo-phaseiv
# Update the base64 value for BETTER_AUTH_SECRET: <paste NEW_SECRET_B64>

# Or patch directly
kubectl patch secret todo-app-secrets -n todo-phaseiv \
  --type merge \
  -p "{\"data\":{\"BETTER_AUTH_SECRET\":\"$NEW_SECRET_B64\"}}"

# 3. Restart pods to pick up new secret
kubectl rollout restart deployment -n todo-phaseiv

# Wait for rollout
kubectl rollout status deployment/backend -n todo-phaseiv
kubectl rollout status deployment/frontend -n todo-phaseiv

# 4. Verify new secret is loaded
kubectl exec deployment/backend -n todo-phaseiv -- env | grep BETTER_AUTH_SECRET
```

**With kubectl-ai:**
```bash
kubectl-ai "show secrets in todo-phaseiv"
kubectl-ai "restart all deployments to pick up new secrets"
kubectl-ai "are all deployments healthy after secret rotation"
```

### Update Database Credentials

**Traditional kubectl:**
```bash
# 1. Get new DATABASE_URL from Neon
# Go to: https://console.neon.tech
# Reset password and get new connection string

NEW_DB_URL="postgresql://user:newpass@host.neon.tech/dbname?sslmode=require"
NEW_DB_URL_B64=$(echo -n "$NEW_DB_URL" | base64)

# 2. Update secret
kubectl patch secret todo-app-secrets -n todo-phaseiv \
  --type merge \
  -p "{\"data\":{\"DATABASE_URL\":\"$NEW_DB_URL_B64\"}}"

# 3. Restart backend and MCP pods (they use DATABASE_URL)
kubectl rollout restart deployment/backend -n todo-phaseiv
kubectl rollout restart deployment/mcp-server -n todo-phaseiv

# Wait for rollout
kubectl rollout status deployment/backend -n todo-phaseiv
kubectl rollout status deployment/mcp-server -n todo-phaseiv

# 4. Verify database connectivity
kubectl exec deployment/backend -n todo-phaseiv -- \
  python -c "from app.database import engine; engine.connect(); print('DB OK')"
```

**With kubectl-ai:**
```bash
kubectl-ai "restart backend and mcp-server"
kubectl-ai "check if backend can connect to database"
kubectl-ai "show backend logs for database connection"
```

### Rotate TLS Certificates

**Traditional kubectl:**
```bash
# 1. Generate new self-signed certificate (valid 365 days)
cd /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app/certs

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls-new.key \
  -out tls-new.crt \
  -subj "/CN=todo-app.local/O=TodoApp" \
  -addext "subjectAltName=DNS:todo-app.local,DNS:*.todo-app.local"

# 2. Update Kubernetes TLS secret
kubectl create secret tls todo-app-tls \
  --cert=tls-new.crt \
  --key=tls-new.key \
  -n todo-phaseiv \
  --dry-run=client -o yaml | kubectl apply -f -

# 3. Restart Ingress controller to pick up new cert
kubectl rollout restart deployment ingress-nginx-controller -n ingress-nginx

# 4. Verify new certificate
kubectl describe secret todo-app-tls -n todo-phaseiv

# 5. Test HTTPS
curl -k -I https://todo-app.local/api/health

# 6. Move old cert to backup
mv tls.crt tls-old-$(date +%Y%m%d).crt
mv tls.key tls-old-$(date +%Y%m%d).key
mv tls-new.crt tls.crt
mv tls-new.key tls.key
```

**With kubectl-ai:**
```bash
kubectl-ai "show tls secrets in todo-phaseiv"
kubectl-ai "when does the tls certificate expire"
kubectl-ai "restart ingress controller"
kubectl-ai "is https working with new certificate"
```

### Security Audit

**Traditional kubectl:**
```bash
# 1. Check for pods running as root (should be none)
kubectl get pods -n todo-phaseiv -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.securityContext.runAsUser}{"\n"}{end}'

# 2. Check for containers without resource limits (should be none)
kubectl get pods -n todo-phaseiv -o json | \
  jq -r '.items[] | select(.spec.containers[].resources.limits == null) | .metadata.name'

# 3. Review all secrets
kubectl get secrets -n todo-phaseiv

# 4. Check service accounts
kubectl get serviceaccounts -n todo-phaseiv

# 5. Review network policies (if any)
kubectl get networkpolicies -n todo-phaseiv

# 6. Check image pull policies (should be Always or IfNotPresent)
kubectl get pods -n todo-phaseiv -o jsonpath='{range .items[*].spec.containers[*]}{.image}{"\t"}{.imagePullPolicy}{"\n"}{end}'

# 7. Review RBAC (roles and bindings)
kubectl get roles,rolebindings -n todo-phaseiv

# 8. Check for privileged containers (should be none)
kubectl get pods -n todo-phaseiv -o json | \
  jq -r '.items[] | select(.spec.containers[].securityContext.privileged == true) | .metadata.name'
```

**With kubectl-ai:**
```bash
kubectl-ai "show security context for all pods"
kubectl-ai "are any pods running as root"
kubectl-ai "show all secrets in todo-phaseiv"
kubectl-ai "check for security issues in the cluster"
kubectl-ai "are containers properly secured"
```

---

## Using kubectl-ai

### What is kubectl-ai?

kubectl-ai is an AI-powered kubectl assistant that allows you to interact with your Kubernetes cluster using natural language instead of complex kubectl commands.

### Installation

**macOS:**
```bash
brew install kubectl-ai
```

**Linux:**
```bash
# Download latest release
wget https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai-linux-amd64 -O kubectl-ai
sudo install kubectl-ai /usr/local/bin/kubectl-ai
```

**Configuration:**
```bash
# Set OpenAI API key
export OPENAI_API_KEY=your-api-key-here

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export OPENAI_API_KEY=your-api-key-here' >> ~/.bashrc
```

### Basic Usage

**Pattern:**
```bash
kubectl-ai "<natural language description of what you want>"
```

**Examples:**

#### Pod Management
```bash
kubectl-ai "show me all pods in todo-phaseiv"
kubectl-ai "are all my pods healthy"
kubectl-ai "which pods are crash looping"
kubectl-ai "restart the backend deployment"
kubectl-ai "scale frontend to 3 replicas"
```

#### Logs and Debugging
```bash
kubectl-ai "show me the last 50 lines of backend logs"
kubectl-ai "find errors in frontend pods"
kubectl-ai "why is my backend pod not starting"
kubectl-ai "show logs from the crashed container"
```

#### Resource Management
```bash
kubectl-ai "show CPU usage for all pods"
kubectl-ai "which pods are using the most memory"
kubectl-ai "is my cluster running out of resources"
kubectl-ai "show autoscaling status"
```

#### Configuration
```bash
kubectl-ai "show the configmap for todo-app"
kubectl-ai "show all secrets in todo-phaseiv"
kubectl-ai "what environment variables does backend have"
```

#### Troubleshooting
```bash
kubectl-ai "debug why ingress is not routing traffic"
kubectl-ai "why is autoscaling not working"
kubectl-ai "check if backend can connect to database"
kubectl-ai "is TLS configured correctly for ingress"
```

### Advanced Usage

#### Complex Queries
```bash
kubectl-ai "show pods with high cpu usage that are not autoscaling"
kubectl-ai "find all deployments that don't have resource limits"
kubectl-ai "show recent events related to backend deployment"
```

#### Multi-Step Operations
```bash
kubectl-ai "scale backend to 4 replicas and show when it's ready"
kubectl-ai "restart frontend and tail logs to verify it started"
kubectl-ai "show all resources in todo-phaseiv and their health status"
```

### Best Practices

1. **Be Specific**: Include namespace, pod names, or labels
   - ✅ Good: "show logs from backend pods in todo-phaseiv"
   - ❌ Bad: "show logs"

2. **Use Context**: Mention what you're trying to achieve
   - ✅ Good: "why isn't my frontend pod starting"
   - ❌ Bad: "pod status"

3. **Verify Output**: Always review the generated command before execution
   - kubectl-ai shows the command it will run - read it first!

4. **Combine with Traditional Commands**: Use kubectl-ai for exploration, traditional kubectl for automation
   - kubectl-ai: Great for debugging and one-off tasks
   - kubectl: Better for scripts and automated workflows

---

## Appendix

### Useful Aliases

Add these to your `~/.bashrc` or `~/.zshrc`:

```bash
# Kubernetes aliases
alias k='kubectl'
alias kgp='kubectl get pods -n todo-phaseiv'
alias kgs='kubectl get svc -n todo-phaseiv'
alias kgi='kubectl get ingress -n todo-phaseiv'
alias kl='kubectl logs -f -n todo-phaseiv'
alias kd='kubectl describe -n todo-phaseiv'
alias ke='kubectl exec -it -n todo-phaseiv'
alias kdel='kubectl delete -n todo-phaseiv'
alias kroll='kubectl rollout restart deployment -n todo-phaseiv'

# Helm aliases
alias hl='helm list -n todo-phaseiv'
alias hu='helm upgrade todo-app /home/salim/Desktop/hackathon-II-todo-app/phaseIV/kubernetes/helm/todo-app -n todo-phaseiv'
alias hh='helm history todo-app -n todo-phaseiv'

# kubectl-ai aliases
alias kai='kubectl-ai'
alias kaip='kubectl-ai "show me all pods in todo-phaseiv"'
alias kail='kubectl-ai "show backend logs"'
alias kais='kubectl-ai "show resource usage"'

# Minikube aliases
alias mk='minikube'
alias mks='minikube status'
alias mkip='minikube ip'
alias mkd='eval $(minikube docker-env)'
```

**Reload shell:**
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Emergency Contact Information

- **Kubernetes Admin**: [Your contact info]
- **Database Admin (Neon)**: https://console.neon.tech
- **OpenAI Support**: https://help.openai.com
- **On-Call Schedule**: [Link to schedule]

### Quick Reference

**Essential Commands:**
```bash
# Status check
kubectl get all -n todo-phaseiv

# Health check
curl -k https://todo-app.local/api/health

# View logs
kubectl logs -l app=backend -n todo-phaseiv --tail=100

# Restart everything
kubectl rollout restart deployment -n todo-phaseiv

# Emergency rollback
helm rollback todo-app -n todo-phaseiv
```

**Essential kubectl-ai Commands:**
```bash
# Status check
kubectl-ai "show me a summary of todo-app deployment"

# Health check
kubectl-ai "are all my pods healthy in todo-phaseiv"

# View logs
kubectl-ai "show me recent backend logs"

# Restart everything
kubectl-ai "restart all deployments in todo-phaseiv"

# Troubleshoot
kubectl-ai "why is my app not working"
```

### Related Documentation

- **[README.md](../../README.md)** - Project overview and quick start
- **[KUBERNETES_GUIDE.md](./KUBERNETES_GUIDE.md)** - Complete deployment guide for naive developers
- **[Architecture Diagram](./architecture-diagram.md)** - System architecture overview
- **[Helm Chart README](../helm/todo-app/README.md)** - Helm chart documentation

---

## Post-Incident Template

After resolving an incident, document it using this template:

```markdown
# Incident Report: [Title]

**Date**: YYYY-MM-DD
**Severity**: P0/P1/P2/P3
**Duration**: HH:MM
**Affected Components**: [List]

## Summary
[Brief description of what happened]

## Timeline
- HH:MM - Issue detected
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Fix applied
- HH:MM - Service restored
- HH:MM - Incident closed

## Root Cause
[What caused the issue]

## Impact
[What was affected and how]

## Resolution
[What was done to fix it]

## Action Items
1. [ ] [Action item 1]
2. [ ] [Action item 2]

## Lessons Learned
[What we learned and how to prevent in future]
```

---

**Last Updated**: 2025-12-26
**Maintained By**: [Your team name]
**Version**: 2.0 (Phase IV with HTTPS and kubectl-ai support)

---

**🎓 For New Operators**:
1. Start with [KUBERNETES_GUIDE.md](./KUBERNETES_GUIDE.md) to understand the basics
2. Install kubectl-ai for easier interaction
3. Bookmark this runbook for operational tasks
4. Join on-call rotation after shadowing 2 incidents

**📞 Need Help?**
- Stuck? Try kubectl-ai first: `kubectl-ai "help me debug [issue]"`
- Check #kubernetes-help Slack channel
- Escalate to on-call engineer if P0/P1
