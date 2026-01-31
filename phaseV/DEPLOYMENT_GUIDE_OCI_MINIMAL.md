# Phase V - Oracle Cloud Infrastructure Deployment Guide (Minimal Resources)

> **Fully functional deployment optimized for Oracle Cloud Free Tier using Redis Pub/Sub**

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture Changes](#architecture-changes)
4. [Resource Requirements](#resource-requirements)
5. [Deployment Steps](#deployment-steps)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## Overview

This deployment guide is optimized for Oracle Cloud Infrastructure (OCI) Free Tier with minimal resource usage while maintaining full application functionality.

**Key Changes from Previous Deployment:**
- ✅ **Redis Pub/Sub** instead of Redpanda Kafka (no external service needed)
- ✅ **Single replicas** for all services (reduced from 2-5)
- ✅ **Reduced CPU/memory** requests and limits
- ✅ **HPA disabled** to save metrics-server overhead
- ✅ **All features functional**: AI chat, email reminders, recurring tasks, full-text search

---

## Prerequisites

### 1. Oracle Cloud Infrastructure Account
- Free tier account: https://cloud.oracle.com/free
- Recommended: **Arm-based Ampere A1 instances** (4 cores, 24GB RAM total - free tier)
- Alternative: 2x AMD instances (1/8 OCPU + 1GB RAM each)

### 2. OCI Kubernetes Cluster (OKE)
```bash
# Create OKE cluster (Basic cluster - free tier)
# Use Oracle Cloud Console or CLI:
oci ce cluster create \
  --compartment-id <compartment-ocid> \
  --name todo-app-cluster \
  --vcn-id <vcn-ocid> \
  --kubernetes-version v1.28.2 \
  --node-shape VM.Standard.A1.Flex \
  --node-shape-config '{"ocpus": 2, "memoryInGBs": 12}' \
  --node-count 2
```

### 3. Local Development Tools
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Install Helm 3
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install OCI CLI (for cluster access)
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
```

### 4. Docker Images
Build and push images to Oracle Cloud Container Registry (OCIR):
```bash
# Login to OCIR (format: <region-key>.ocir.io/<tenancy-namespace>/<repo-name>)
docker login <region>.ocir.io
# Username: <tenancy-namespace>/<username>
# Password: <auth-token>

# Build and push backend image
cd phaseV/backend
docker build -t <region>.ocir.io/<tenancy-namespace>/todo-app-backend:latest .
docker push <region>.ocir.io/<tenancy-namespace>/todo-app-backend:latest

# Build and push frontend image
cd ../frontend
docker build -t <region>.ocir.io/<tenancy-namespace>/todo-frontend:latest .
docker push <region>.ocir.io/<tenancy-namespace>/todo-frontend:latest
```

---

## Architecture Changes

### Before: Kafka-based (Redpanda Cloud)
```
Backend → Dapr Sidecar → Kafka (Redpanda Cloud) → Consumers
                          (External Service, Expired)
```

### After: Redis-based (In-cluster)
```
Backend → Dapr Sidecar → Redis Pub/Sub → Consumers
                         (In-cluster, Free)
```

**Benefits:**
- No external dependencies
- Lower latency (in-cluster communication)
- Zero cost (no cloud service fees)
- Simpler deployment

**Trade-offs:**
- Lower throughput than Kafka (sufficient for most use cases)
- Less durable (Redis Streams vs Kafka log retention)
- Single point of failure (can add Redis cluster if needed)

---

## Resource Requirements

### Total Resource Allocation (values-minimal.yaml)

| Component | Replicas | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-----------|----------|-------------|----------------|-----------|--------------|
| Frontend | 1 | 200m | 256Mi | 500m | 512Mi |
| Backend | 1 | 300m | 384Mi | 600m | 768Mi |
| MCP Server | 1 | 150m | 192Mi | 300m | 384Mi |
| Redis | 1 | 100m | 128Mi | 200m | 256Mi |
| Email Delivery | 1 | 50m | 128Mi | 150m | 256Mi |
| Notification Svc | 1 | 50m | 128Mi | 150m | 256Mi |
| Recurring Task | 1 | 50m | 128Mi | 150m | 256Mi |
| Dapr Sidecars (4x) | 4 | 200m (4x50m) | 256Mi (4x64Mi) | 400m (4x100m) | 512Mi (4x128Mi) |
| **TOTAL** | **10** | **~1.1 cores** | **~1.6 GB** | **~2.5 cores** | **~3.3 GB** |

**Oracle Cloud Free Tier:**
- **Ampere A1**: 4 cores + 24GB RAM (RECOMMENDED) ✅
- **AMD**: 2x instances (0.25 OCPU + 1GB RAM each) ⚠️ (too limited)

**Recommendation:** Use Ampere A1 instances - this deployment fits comfortably with room for system overhead.

---

## Deployment Steps

### Step 1: Configure kubectl for OKE
```bash
# Get kubeconfig from OCI
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file ~/.kube/config \
  --region <region> \
  --token-version 2.0.0

# Verify connection
kubectl get nodes
```

### Step 2: Create Namespace
```bash
kubectl create namespace todo-phasev
kubectl config set-context --current --namespace=todo-phasev
```

### Step 3: Install Dapr Runtime
```bash
# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on Kubernetes
dapr init --kubernetes --wait

# Verify Dapr installation
dapr status -k
```

### Step 4: Create Secrets
```bash
# Copy example values file
cd phaseV/kubernetes/helm/todo-app
cp values.yaml values-local.yaml

# Edit values-local.yaml with your secrets (base64-encoded):
# - DATABASE_URL (Neon PostgreSQL)
# - OPENAI_API_KEY
# - BETTER_AUTH_SECRET
# - Email credentials (if using different SMTP)

# Verify secrets are base64-encoded:
echo -n "your-secret" | base64
```

### Step 5: Update Image Repositories
Edit `values-minimal.yaml` to use your OCIR images:
```yaml
backend:
  image:
    repository: "<region>.ocir.io/<tenancy-namespace>/todo-app-backend"
    tag: "latest"

frontend:
  image:
    repository: "<region>.ocir.io/<tenancy-namespace>/todo-frontend"
    tag: "latest"
```

### Step 6: Install Storage Class (OCI Block Volumes)
```bash
# Create OCI Block Volume storage class
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: oci-bv
provisioner: oracle.com/oci
parameters:
  type: paravirtualized
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
EOF
```

### Step 7: Deploy Dapr Components (Redis Pub/Sub)
```bash
cd phaseV/kubernetes/dapr-components

# Apply Dapr configuration
kubectl apply -f dapr-config.yaml

# Apply Redis pub/sub component (NOT Kafka!)
kubectl apply -f pubsub-redis.yaml

# Apply state store component
kubectl apply -f statestore-postgres.yaml

# Apply secrets component
kubectl apply -f secrets-kubernetes.yaml

# Verify components
kubectl get components -n todo-phasev
```

### Step 8: Deploy Application with Helm
```bash
cd phaseV/kubernetes/helm/todo-app

# Install with minimal resources configuration
helm install todo-app . \
  -f values.yaml \
  -f values-local.yaml \
  -f values-minimal.yaml \
  --namespace todo-phasev \
  --create-namespace

# Or upgrade if already installed
helm upgrade todo-app . \
  -f values.yaml \
  -f values-local.yaml \
  -f values-minimal.yaml \
  --namespace todo-phasev
```

### Step 9: Create NGINX Ingress Controller
```bash
# Install NGINX Ingress Controller (OCI Load Balancer)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/oci-load-balancer-shape"="flexible" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/oci-load-balancer-shape-flex-min"="10" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/oci-load-balancer-shape-flex-max"="10"

# Get Load Balancer IP
kubectl get svc -n ingress-nginx
```

### Step 10: Configure DNS
```bash
# Get external IP from ingress
kubectl get ingress -n todo-phasev

# Add DNS record (or update /etc/hosts for local testing):
# <external-ip> todo-app.local
```

---

## Verification

### 1. Check All Pods are Running
```bash
kubectl get pods -n todo-phasev
# Expected: 10 pods (7 app containers + 3 Dapr sidecars for notification/email/recurring services)

# Check logs for any issues
kubectl logs -n todo-phasev -l app=backend --tail=50
kubectl logs -n todo-phasev -l app=redis --tail=50
```

### 2. Verify Dapr Components
```bash
# Check components are loaded
kubectl get components -n todo-phasev

# Should show:
# - pubsub (type: pubsub.redis)
# - statestore-postgres (type: state.postgresql)
# - secrets-kubernetes (type: secretstores.kubernetes)

# Check Dapr sidecar logs
kubectl logs -n todo-phasev <backend-pod-name> -c daprd
```

### 3. Test Redis Pub/Sub
```bash
# Exec into Redis pod
kubectl exec -it -n todo-phasev redis-0 -- redis-cli

# Inside Redis CLI:
127.0.0.1:6379> PING
# Expected: PONG

127.0.0.1:6379> MONITOR
# Keep this running while you create a task in the UI
# You should see pub/sub messages
```

### 4. Test Application Endpoints
```bash
# Health check
curl -k https://todo-app.local/api/health

# Create a task via API (requires auth token)
curl -k -X POST https://todo-app.local/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Testing deployment"}'
```

### 5. Test Event Flow
1. **Create a task with due date** in ChatKit UI
2. **Check notification service logs**:
   ```bash
   kubectl logs -n todo-phasev -l app=notification-service --tail=50
   ```
3. **Check email delivery service logs**:
   ```bash
   kubectl logs -n todo-phasev -l app=email-delivery --tail=50
   ```
4. **Verify email received** in inbox

---

## Troubleshooting

### Issue: Pods Stuck in Pending
```bash
# Check resource constraints
kubectl describe pod <pod-name> -n todo-phasev

# Check node resources
kubectl top nodes

# Solution: Increase node pool size or reduce resource requests
```

### Issue: Dapr Sidecar Not Injecting
```bash
# Check Dapr operator is running
kubectl get pods -n dapr-system

# Check pod annotations
kubectl describe pod <pod-name> -n todo-phasev | grep dapr.io

# Solution: Ensure dapr.io/enabled: "true" annotation exists
```

### Issue: Redis Connection Failed
```bash
# Check Redis service
kubectl get svc -n todo-phasev redis-service

# Test Redis connectivity from backend pod
kubectl exec -it <backend-pod> -n todo-phasev -- sh
nc -zv redis-service.todo-phasev.svc.cluster.local 6379

# Check Redis logs
kubectl logs -n todo-phasev redis-0
```

### Issue: Events Not Publishing
```bash
# Check Dapr pub/sub component
kubectl describe component pubsub -n todo-phasev

# Check backend Dapr sidecar logs
kubectl logs <backend-pod> -c daprd -n todo-phasev

# Verify USE_DAPR environment variable
kubectl exec <backend-pod> -n todo-phasev -- env | grep USE_DAPR
# Expected: USE_DAPR=true
```

### Issue: OCI Load Balancer Not Provisioning
```bash
# Check ingress events
kubectl describe ingress -n todo-phasev

# Check NGINX ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller

# Solution: Ensure OCI policies allow load balancer creation
```

---

## Monitoring and Scaling

### Monitor Resource Usage
```bash
# Install metrics-server (if not already installed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Check resource usage
kubectl top pods -n todo-phasev
kubectl top nodes
```

### Manual Scaling (if needed)
```bash
# Scale backend replicas
kubectl scale deployment backend -n todo-phasev --replicas=2

# Or update values-minimal.yaml and helm upgrade
```

### Enable HPA (if needed)
Edit `values-minimal.yaml`:
```yaml
backend:
  autoscaling:
    enabled: true
    minReplicas: 1
    maxReplicas: 3
    targetCPUUtilizationPercentage: 70
```

---

## Cost Optimization

**Current Configuration Costs (Oracle Cloud Free Tier):**
- ✅ **Compute**: FREE (Ampere A1 - 4 cores, 24GB RAM)
- ✅ **Block Storage**: FREE (up to 200GB)
- ✅ **Load Balancer**: ~$10/month (flexible shape, 10Mbps min/max)
- ✅ **Outbound Traffic**: First 10TB/month FREE
- ✅ **Neon PostgreSQL**: FREE tier (external)
- ✅ **Redis**: In-cluster (FREE)

**Total Monthly Cost: ~$10 USD** (only Load Balancer)

**Further Cost Reduction:**
- Use NodePort instead of LoadBalancer for testing ($0/month)
- Use OCI Always Free Load Balancer (10Mbps limit)

---

## Next Steps

1. **Setup monitoring**: Deploy Prometheus + Grafana for metrics
2. **Configure backups**: Automate PostgreSQL backups
3. **Add CI/CD**: Setup GitHub Actions for automated deployments
4. **Enable TLS**: Use Let's Encrypt for production certificates
5. **Tune Redis**: Enable AOF persistence for durability

---

## Summary

✅ **Migration Complete**: Kafka → Redis Pub/Sub
✅ **Resource Optimized**: ~1.1 cores, ~1.6GB RAM
✅ **Fully Functional**: All features working
✅ **Free Tier Compatible**: Fits Oracle Cloud Free Tier
✅ **Production Ready**: With monitoring and backups

**Questions?** Check logs, Dapr docs, or Oracle Cloud documentation.
