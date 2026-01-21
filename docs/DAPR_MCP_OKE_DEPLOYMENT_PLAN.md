# Implementation Plan: Dapr Integration Completion + Oracle Cloud Deployment
Plan(~/.claude/plans/shiny-marinating-storm.md)
## Overview

Complete the remaining Phase V implementation:
1. Add Dapr sidecar to MCP Server deployment + verify locally
2. Deploy to Oracle Cloud OKE (both CLI and GitHub Actions)

**Current State**: Dapr working with backend services (backend, notification, email-delivery, recurring)
**Missing**: MCP Server Dapr sidecar, production deployment

**Approach**:
1. First: Add Dapr to MCP server, test locally on Minikube
2. Then: Deploy to OKE using both direct CLI and GitHub Actions

---

## Part 0: OCI CLI Setup (Pre-requisite)

### Install OCI CLI
```bash
# Linux/macOS
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Verify installation
oci --version
```

### Configure OCI CLI
```bash
oci setup config
```

You'll need from OCI Console:
1. **User OCID**: Identity → Users → Your user → OCID
2. **Tenancy OCID**: Administration → Tenancy Details → OCID
3. **Region**: e.g., `us-ashburn-1`, `ap-mumbai-1`
4. **API Key**: Generate during setup or upload existing public key

### Generate API Key (if needed)
```bash
# Keys stored in ~/.oci/
# During setup, choose "Generate a new API key pair"
# Upload the PUBLIC key to OCI Console: Identity → Users → API Keys → Add API Key
```

### Verify Setup
```bash
oci iam region list --output table
```

---

## Part 1: MCP Server Dapr Integration

### Problem
The MCP server at `phaseV/kubernetes/helm/todo-app/templates/mcp-deployment.yaml` is **missing Dapr annotations**. The MCP tools use Dapr for event publishing (`app/dapr/pubsub.py`), so events won't publish without the sidecar.

### Solution
Add Dapr annotations to MCP deployment (copy pattern from backend-deployment.yaml lines 18-27):

**File**: `phaseV/kubernetes/helm/todo-app/templates/mcp-deployment.yaml`

```yaml
# Add after line 17 (labels), before spec:
annotations:
  dapr.io/enabled: "{{ .Values.dapr.enabled }}"
  dapr.io/app-id: "mcp-server"
  dapr.io/app-port: "{{ .Values.mcpServer.service.targetPort }}"
  dapr.io/log-level: "info"
  dapr.io/sidecar-cpu-limit: "{{ .Values.dapr.resources.limits.cpu }}"
  dapr.io/sidecar-memory-limit: "{{ .Values.dapr.resources.limits.memory }}"
  dapr.io/sidecar-cpu-request: "{{ .Values.dapr.resources.requests.cpu }}"
  dapr.io/sidecar-memory-request: "{{ .Values.dapr.resources.requests.memory }}"
```

Also add to spec: `serviceAccountName: todo-app-sa`

**Note**: Frontend does NOT need Dapr - it communicates via HTTP to backend.

### Local Verification (Minikube)

After adding Dapr annotations, test locally:

```bash
# Ensure Minikube is running
minikube status

# Redeploy MCP server
helm upgrade todo-app phaseV/kubernetes/helm/todo-app \
  --namespace todo-phasev \
  -f phaseV/kubernetes/helm/todo-app/values-local.yaml

# Verify MCP pod has Dapr sidecar (should show 2 containers)
kubectl get pods -n todo-phasev -l app=mcp-server

# Check Dapr sidecar logs
kubectl logs -n todo-phasev -l app=mcp-server -c daprd

# Test MCP tool that publishes events (create a task via ChatKit UI)
# Check Kafka topic for events
```

---

## Part 2: Direct OCI CLI Deployment

### Step 2.1: OKE Cluster Setup

**Option A: Via OCI Console (Recommended for first time)**
1. Developer Services → Kubernetes Clusters (OKE)
2. Click "Create Cluster" → "Quick Create"
3. Configuration:
   - Name: `todo-phasev-cluster`
   - K8s Version: v1.28+
   - Node Pool: 2 nodes
   - Shape: VM.Standard.A1.Flex (4 OCPU, 24GB - Always Free eligible)
4. Wait ~10 minutes for cluster to be ACTIVE

**Option B: Via OCI CLI**
```bash
# List compartments to get COMPARTMENT_ID
oci iam compartment list --output table

# Create VCN (if needed)
oci network vcn create \
  --cidr-block "10.0.0.0/16" \
  --compartment-id $COMPARTMENT_ID \
  --display-name "todo-phasev-vcn"

# Create OKE cluster
oci ce cluster create \
  --name "todo-phasev-cluster" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --kubernetes-version "v1.28.2" \
  --wait-for-state ACTIVE
```

### Step 2.2: Configure kubectl

```bash
# Get cluster OCID from OCI Console or CLI
oci ce cluster list --compartment-id $COMPARTMENT_ID --output table

# Generate kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id $CLUSTER_ID \
  --file $HOME/.kube/config \
  --region $REGION \
  --token-version 2.0.0

# Verify connection
kubectl get nodes
```

### Step 2.3: Container Registry (OCIR) Setup

```bash
# Create auth token in OCI Console: Identity → Users → Auth Tokens → Generate Token
# Save the token - it's shown only once!

# Login to OCIR
docker login <region>.ocir.io -u '<tenancy-namespace>/<username>' -p '<auth-token>'

# Example for Mumbai region:
# docker login ap-mumbai-1.ocir.io -u 'mytenancy/oracleidentitycloudservice/user@email.com'
```

### Step 2.4: Build and Push Images

```bash
# Set variables
export REGION=ap-mumbai-1  # Change to your region
export TENANCY=mytenancy   # Change to your tenancy namespace
export TAG=v1.0.0

# Build images
docker build -t $REGION.ocir.io/$TENANCY/todo-app-backend:$TAG phaseV/backend
docker build -t $REGION.ocir.io/$TENANCY/todo-app-frontend:$TAG phaseV/frontend

# Push to OCIR
docker push $REGION.ocir.io/$TENANCY/todo-app-backend:$TAG
docker push $REGION.ocir.io/$TENANCY/todo-app-frontend:$TAG
```

### Step 2.5: Create Production Helm Values

**Create**: `phaseV/kubernetes/helm/todo-app/values-production.yaml`

Key settings:
- `global.imageRegistry: <region>.ocir.io/<tenancy>`
- `imagePullPolicy: Always`
- `ingress.tls.enabled: false` (no domain)
- Production resource limits and replica counts

### Step 2.6: Deploy Infrastructure Components

```bash
# 1. Create namespace
kubectl create namespace todo-phasev

# 2. Create OCIR pull secret
kubectl create secret docker-registry ocir-secret \
  --namespace todo-phasev \
  --docker-server=$REGION.ocir.io \
  --docker-username="$TENANCY/<username>" \
  --docker-password="<auth-token>"

# 3. Install Nginx Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# 4. Install Dapr
dapr init -k --wait
kubectl get pods -n dapr-system  # Verify Dapr is running

# 5. Apply Dapr components
kubectl apply -f phaseV/kubernetes/dapr-components/ -n todo-phasev
```

### Step 2.7: Deploy Application

```bash
# Deploy with Helm
helm install todo-app phaseV/kubernetes/helm/todo-app \
  --namespace todo-phasev \
  -f phaseV/kubernetes/helm/todo-app/values-production.yaml \
  --wait --timeout 10m

# Check deployment status
kubectl get pods -n todo-phasev
kubectl get svc -n todo-phasev
```

### Step 2.8: Get Load Balancer IP

```bash
# Get the external IP (may take 2-3 minutes to provision)
kubectl get svc -n ingress-nginx -w

# Once EXTERNAL-IP is available, access your app:
# http://<EXTERNAL-IP>/
```

---

## Part 3: Deployment Script (Optional)

Create a deployment script to automate the CLI commands:

**File**: `phaseV/kubernetes/scripts/deploy-oke.sh`

```bash
#!/bin/bash
set -e

# Configuration (set these before running)
export REGION=${REGION:-"ap-mumbai-1"}
export TENANCY=${TENANCY:-"mytenancy"}
export TAG=${TAG:-"v1.0.0"}
export NAMESPACE=${NAMESPACE:-"todo-phasev"}

echo "=== Building and pushing images ==="
docker build -t $REGION.ocir.io/$TENANCY/todo-app-backend:$TAG phaseV/backend
docker build -t $REGION.ocir.io/$TENANCY/todo-app-frontend:$TAG phaseV/frontend
docker push $REGION.ocir.io/$TENANCY/todo-app-backend:$TAG
docker push $REGION.ocir.io/$TENANCY/todo-app-frontend:$TAG

echo "=== Deploying to OKE ==="
helm upgrade --install todo-app phaseV/kubernetes/helm/todo-app \
  --namespace $NAMESPACE \
  --create-namespace \
  -f phaseV/kubernetes/helm/todo-app/values-production.yaml \
  --set backend.image.tag=$TAG \
  --set frontend.image.tag=$TAG \
  --wait --timeout 10m

echo "=== Deployment complete ==="
kubectl get pods -n $NAMESPACE
```

---

## Implementation Order

### Phase A: Local Verification (Minikube)
1. **MCP Dapr Fix** - Add Dapr annotations to mcp-deployment.yaml
2. **Local Deploy** - Redeploy to Minikube with updated MCP
3. **Verify Dapr** - Check MCP server has Dapr sidecar, test event publishing

### Phase B: OKE Direct Deployment (CLI)
4. **OCI CLI Setup** - Install and configure OCI CLI
5. **OKE Cluster** - Create via OCI Console (Quick Create)
6. **values-production.yaml** - Create production Helm values
7. **OCIR Login** - Create auth token, login to registry
8. **Build & Push Images** - Build Docker images, push to OCIR
9. **Deploy Infrastructure** - Nginx Ingress, Dapr, OCIR secret
10. **Deploy App** - Helm install with production values
11. **Verify** - Access app via Load Balancer IP

### Phase C: CI/CD Automation (GitHub Actions)
12. **CI Workflow** - Create ci-phase-v.yml (lint, test, build, push)
13. **Deploy Workflow** - Create deploy-production.yml (deploy to OKE)
14. **GitHub Secrets** - Configure OCI credentials
15. **Test Pipeline** - Trigger deployment via release/manual

**Future Enhancements**:
- Add domain and TLS with cert-manager
- Add monitoring (Prometheus/Grafana)

---

## Verification Checklist

```bash
# All pods running
kubectl get pods -n todo-phasev

# Dapr sidecars present (should see 2 containers per pod)
kubectl get pods -n todo-phasev -o jsonpath='{range .items[*]}{.metadata.name}: {range .spec.containers[*]}{.name} {end}{"\n"}{end}'

# Get Load Balancer IP
kubectl get svc -n ingress-nginx
# Note the EXTERNAL-IP

# Health check (replace <LB_IP> with actual IP)
curl -f http://<LB_IP>/api/health

# Access frontend
curl -f http://<LB_IP>/
```

---

## Files to Modify/Create

### Phase A (Local)
| File | Action |
|------|--------|
| `phaseV/kubernetes/helm/todo-app/templates/mcp-deployment.yaml` | Add Dapr annotations |

### Phase B (OKE CLI)
| File | Action |
|------|--------|
| `phaseV/kubernetes/helm/todo-app/values-production.yaml` | Create new |
| `phaseV/kubernetes/scripts/deploy-oke.sh` | Create deployment script |

### Phase C (CI/CD)
| File | Action |
|------|--------|
| `.github/workflows/ci-phase-v.yml` | CI workflow (lint, test, build, push) |
| `.github/workflows/deploy-production.yml` | Deploy workflow (OKE deployment) |

**Future**:
| `phaseV/kubernetes/helm/todo-app/templates/cluster-issuer.yaml` | TLS with Let's Encrypt |
