# Complete Production-Grade OKE Deployment Plan for Todo App Phase V

## Executive Summary

**Objective**: Deploy Todo App Phase V (event-driven microservices with Dapr) to Oracle Kubernetes Engine (OKE) with production-grade infrastructure, security, observability, and CI/CD automation.

**Current State**: Application running on Minikube with 5 microservices, Dapr integration, external Neon PostgreSQL, and Redpanda Kafka.

**Target State**: Production OKE deployment with multi-AZ HA, SSL/TLS, monitoring, automated CI/CD.

**Timeline**: 4-6 weeks (8 phases)
**Estimated Cost**: $0/month (100% OCI Always Free tier - ARM Ampere A1)

---

## 🎯 FREE TIER HIGHLIGHTS

This plan is **100% free tier compliant** - zero ongoing costs!

### Key Differences from Standard Deployment

| Aspect | Standard (Paid) | This Plan (FREE) |
|--------|-----------------|------------------|
| **Compute** | 4+ x86 nodes (E4.Flex) | 2 ARM nodes (A1.Flex) ✅ |
| **Architecture** | x86_64 (AMD/Intel) | ARM64 (Ampere) ✅ |
| **Node Specs** | 2 OCPU, 8GB per node | 2 OCPU, 12GB per node ✅ |
| **Total Resources** | 8+ OCPU, 32+ GB RAM | 4 OCPU, 24GB RAM (max free tier) ✅ |
| **Load Balancer** | OCI LB ($35-50/month) | NodePort ($0) ✅ |
| **Access URL** | `https://example.com` | `https://<IP>.nip.io:30443` ✅ |
| **Autoscaling** | Yes (2-10 nodes) | No (fixed 2 nodes) ✅ |
| **Monthly Cost** | $300-500+ | **$0** ✅ |

### What You Need to Know

**✅ Advantages**:
- **Zero cost**: All resources within OCI Always Free tier
- **Real Kubernetes**: Production-grade OKE cluster (not a toy environment)
- **High availability**: 2 nodes across 2 Availability Domains
- **Full features**: Dapr, monitoring, CI/CD, security hardening

**⚠️ Limitations**:
- **ARM architecture**: Docker images must be built for ARM64 (covered in Phase 2)
- **NodePort access**: HTTPS on port 30443 instead of standard port 443
- **Fixed capacity**: No autoscaling (2 nodes maximum in free tier)
- **Performance**: ARM A1 slower than x86 for some workloads

**🚀 Upgrade Path**:
- Add OCI Load Balancer (~$35-50/month) for standard HTTPS (port 443)
- Switch to x86 nodes (E4.Flex) for better performance (~$260/month)
- Enable autoscaling for higher traffic (~$20-30/month per additional node)

---

## Architecture Decisions (Pragmatic Choices)

| Component | Decision | Rationale |
|-----------|----------|-----------|
| **Cluster Type** | Enhanced OKE | Required for network policies, pod security |
| **Multi-AZ** | 2 Availability Domains | Balance HA with free tier (2 nodes max) |
| **Node Pools** | Single pool: 2 nodes (ARM) | Free tier limit: 4 OCPU + 24GB RAM total |
| **Node Shape** | VM.Standard.A1.Flex (ARM - 2 OCPU, 12GB) | 100% Always Free tier - Ampere A1 |
| **Load Balancer** | NodePort (no OCI LB) | Free tier - no Load Balancer cost |
| **Ingress** | Nginx Ingress with NodePort | Access via `<NODE_IP>:30443` |
| **SSL/TLS** | cert-manager + Let's Encrypt | Free automated certificates |
| **Domain** | `<NODE_IP>.nip.io` (free dynamic DNS) | Zero cost, instant setup |
| **Secrets** | Sealed Secrets | Simpler than OCI Vault, GitOps-friendly |
| **Monitoring** | Prometheus + Grafana (lightweight) | Skip Loki/Jaeger initially, add later if needed |
| **Storage** | OCI Block Volumes (< 200GB free tier) | Free tier: 2 Block Volumes, 200GB total |
| **CI/CD** | GitHub Actions + OCIR | Leverages existing GitHub repo |

---

## Phase 0: Prerequisites & Planning (Week 1, Days 1-2)

**Objective**: Validate requirements, finalize decisions, prepare credentials.

**Prerequisites**: None (starting point)

**Time**: 4-8 hours | **Cost**: $0

### Tasks

#### 0.1 Verify OCI Account Limits

```bash
export COMPARTMENT_ID="<your-compartment-ocid>"
export REGION="us-ashburn-1"  # Or preferred region

# Check ARM Ampere A1 compute limits (need 4 OCPUs total: 2 nodes × 2 OCPU)
oci limits resource-availability get \
  --compartment-id $COMPARTMENT_ID \
  --service-name compute \
  --limit-name vm-standard-a1-flex-core-count

# Check VCN limits
oci limits resource-availability get \
  --compartment-id $COMPARTMENT_ID \
  --service-name vcn \
  --limit-name vcn-count
```

**Expected Output**: Available OCPUs ≥ 8, VCN count ≥ 1

#### 0.2 Cost Estimation (100% FREE TIER)

| Resource | Configuration | Monthly Cost |
|----------|---------------|--------------|
| Compute (ARM) | 2 × A1.Flex (2 OCPU, 12GB) | **$0** ✅ (Always Free) |
| Networking | NodePort (no Load Balancer) | **$0** ✅ (Always Free) |
| Block Storage | 25GB total (< 200GB limit) | **$0** ✅ (Always Free) |
| Egress Bandwidth | 10TB/month outbound | **$0** ✅ (Always Free) |
| OCIR (Container Registry) | 500GB storage | **$0** ✅ (Always Free) |
| External Services | Neon + Redpanda (existing) | **$0** ✅ (Free tiers) |
| **TOTAL** | | **$0/month** ✅ |

**Note**: No autoscaling available in free tier (4 OCPU max = 2 nodes). Fixed capacity deployment.

#### 0.3 Domain Strategy: nip.io with NodePort (FREE)

**Choice**: Use nip.io with NodePort (no Load Balancer)

**Format**: `<NODE_IP>.nip.io:30443` (e.g., `129.146.50.100.nip.io:30443`)

**How it works**:
1. Get any node's public IP from OKE cluster
2. Nginx Ingress runs as NodePort (30080 for HTTP, 30443 for HTTPS)
3. Access application via `https://<NODE_IP>.nip.io:30443`
4. nip.io automatically resolves to the node IP

**Pros**:
- 100% free (no Load Balancer cost)
- No DNS management needed
- Works with cert-manager (HTTP-01 challenge)
- Instant setup

**Cons**:
- Must include port number (`:30443`)
- If node IP changes, URL changes
- Less professional than standard HTTPS (port 443)

**Migration Path**: Add custom domain + OCI Load Balancer later (adds ~$35-50/month)

#### 0.4 Credentials Checklist

- [x] OCI CLI configured (`~/.oci/config`)
- [x] Neon PostgreSQL URL (`DATABASE_URL`)
- [x] Redpanda Kafka credentials (`KAFKA_BROKER`, `KAFKA_USERNAME`, `KAFKA_PASSWORD`)
- [x] OpenAI API key (`OPENAI_API_KEY`)
- [x] Gmail SMTP credentials (`SMTP_USERNAME`, `SMTP_PASSWORD`)
- [x] Better Auth secret (`BETTER_AUTH_SECRET`)

**Action**: Create `phaseV/kubernetes/secrets/.env.production` (DO NOT COMMIT):

```bash
# Create secrets file (gitignored)
cat > phaseV/kubernetes/secrets/.env.production <<'EOF'
DATABASE_URL=postgresql://user:pass@host.neon.tech/dbname?sslmode=require
KAFKA_BROKER=broker.redpanda.cloud:9093
KAFKA_USERNAME=your-username
KAFKA_PASSWORD=your-password
KAFKA_SASL_MECHANISM=SCRAM-SHA-256
OPENAI_API_KEY=sk-...
BETTER_AUTH_SECRET=your-secret-here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NEXT_PUBLIC_BACKEND_URL=http://backend:8000
EOF
```

### Verification

- [ ] OCI account has ≥8 OCPUs available
- [ ] Cost budget approved ($50-150/month)
- [ ] Domain strategy confirmed (nip.io for MVP)
- [ ] All credentials documented in `.env.production`

### Deliverables

- Infrastructure requirements validated
- Cost estimate documented
- Credentials secured in `.env.production`
- Domain strategy finalized

---

## Phase 1: Core Infrastructure Setup (Week 1, Days 3-5)

**Objective**: Create production-grade OKE cluster with multi-AZ networking.

**Prerequisites**: Phase 0 complete

**Time**: 6-10 hours | **Cost**: $0 (Always Free tier - ARM nodes)

### 1.1 Set Environment Variables

```bash
# Save to ~/.oke-env for persistence
cat > ~/.oke-env <<'EOF'
export COMPARTMENT_ID="<your-compartment-ocid>"
export REGION="us-ashburn-1"
export CLUSTER_NAME="todo-phasev-oke"
export VCN_NAME="todo-phasev-vcn"
export NAMESPACE="todo-phasev"

# Network CIDR blocks
export VCN_CIDR="10.0.0.0/16"
export LB_SUBNET_CIDR="10.0.1.0/24"
export NODE_SUBNET_CIDR="10.0.2.0/24"
export SERVICE_SUBNET_CIDR="10.0.3.0/24"
EOF

source ~/.oke-env
```

### 1.2 Create VCN and Networking

```bash
# Create VCN
VCN_ID=$(oci network vcn create \
  --compartment-id $COMPARTMENT_ID \
  --cidr-block $VCN_CIDR \
  --display-name $VCN_NAME \
  --dns-label "todophasev" \
  --wait-for-state AVAILABLE \
  --query 'data.id' \
  --raw-output)

echo "export VCN_ID=$VCN_ID" >> ~/.oke-env
source ~/.oke-env

# Create Internet Gateway
IGW_ID=$(oci network internet-gateway create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --is-enabled true \
  --display-name "${VCN_NAME}-igw" \
  --wait-for-state AVAILABLE \
  --query 'data.id' \
  --raw-output)

echo "export IGW_ID=$IGW_ID" >> ~/.oke-env

# Get default route table and add internet gateway route
RT_ID=$(oci network vcn get --vcn-id $VCN_ID --query 'data."default-route-table-id"' --raw-output)

oci network route-table update \
  --rt-id $RT_ID \
  --route-rules '[{"destination":"0.0.0.0/0","networkEntityId":"'$IGW_ID'"}]' \
  --force

# Create Load Balancer Subnet (public)
LB_SUBNET_ID=$(oci network subnet create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --cidr-block $LB_SUBNET_CIDR \
  --display-name "${VCN_NAME}-lb-subnet" \
  --dns-label "lbsubnet" \
  --prohibit-public-ip-on-vnic false \
  --wait-for-state AVAILABLE \
  --query 'data.id' \
  --raw-output)

echo "export LB_SUBNET_ID=$LB_SUBNET_ID" >> ~/.oke-env

# Create Node Subnet (public for simplicity, private recommended for production)
NODE_SUBNET_ID=$(oci network subnet create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --cidr-block $NODE_SUBNET_CIDR \
  --display-name "${VCN_NAME}-node-subnet" \
  --dns-label "nodesubnet" \
  --prohibit-public-ip-on-vnic false \
  --wait-for-state AVAILABLE \
  --query 'data.id' \
  --raw-output)

echo "export NODE_SUBNET_ID=$NODE_SUBNET_ID" >> ~/.oke-env

# Create Service Subnet (for K8s services)
SVC_SUBNET_ID=$(oci network subnet create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --cidr-block $SERVICE_SUBNET_CIDR \
  --display-name "${VCN_NAME}-service-subnet" \
  --dns-label "svcsubnet" \
  --prohibit-public-ip-on-vnic false \
  --wait-for-state AVAILABLE \
  --query 'data.id' \
  --raw-output)

echo "export SVC_SUBNET_ID=$SVC_SUBNET_ID" >> ~/.oke-env
```

### 1.3 Configure Security Lists

```bash
SECLIST_ID=$(oci network vcn get --vcn-id $VCN_ID --query 'data."default-security-list-id"' --raw-output)

# Update with required ingress/egress rules
oci network security-list update \
  --security-list-id $SECLIST_ID \
  --ingress-security-rules '[
    {"protocol": "6", "source": "0.0.0.0/0", "tcpOptions": {"destinationPortRange": {"min": 80, "max": 80}}, "description": "HTTP"},
    {"protocol": "6", "source": "0.0.0.0/0", "tcpOptions": {"destinationPortRange": {"min": 443, "max": 443}}, "description": "HTTPS"},
    {"protocol": "6", "source": "'$VCN_CIDR'", "tcpOptions": {"destinationPortRange": {"min": 1, "max": 65535}}, "description": "All TCP within VCN"}
  ]' \
  --egress-security-rules '[
    {"protocol": "all", "destination": "0.0.0.0/0", "description": "Allow all egress"}
  ]' \
  --force
```

### 1.4 Create OKE Enhanced Cluster

```bash
# Create cluster (takes ~7 minutes)
CLUSTER_ID=$(oci ce cluster create \
  --compartment-id $COMPARTMENT_ID \
  --name $CLUSTER_NAME \
  --vcn-id $VCN_ID \
  --kubernetes-version "v1.28.2" \
  --service-lb-subnet-ids "[\"$LB_SUBNET_ID\"]" \
  --endpoint-subnet-id $SVC_SUBNET_ID \
  --cluster-pod-network-options '[{"cniType":"FLANNEL_OVERLAY"}]' \
  --wait-for-state ACTIVE \
  --query 'data.id' \
  --raw-output)

echo "export CLUSTER_ID=$CLUSTER_ID" >> ~/.oke-env

# Configure kubectl
oci ce cluster create-kubeconfig \
  --cluster-id $CLUSTER_ID \
  --file ~/.kube/config-oke \
  --region $REGION \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT

# Merge kubeconfigs
export KUBECONFIG=~/.kube/config:~/.kube/config-oke
kubectl config view --flatten > ~/.kube/config-merged
mv ~/.kube/config-merged ~/.kube/config

# Set context
kubectl config use-context $(kubectl config get-contexts -o name | grep $CLUSTER_ID | head -1)
```

### 1.5 Create Node Pools

```bash
# Get availability domains
AD1=$(oci iam availability-domain list --compartment-id $COMPARTMENT_ID --query 'data[0].name' --raw-output)
AD2=$(oci iam availability-domain list --compartment-id $COMPARTMENT_ID --query 'data[1].name' --raw-output)

# Get Oracle Linux 8 ARM image for Kubernetes (Ampere A1)
IMAGE_ID=$(oci compute image list \
  --compartment-id $COMPARTMENT_ID \
  --operating-system "Oracle Linux" \
  --shape "VM.Standard.A1.Flex" \
  --sort-by TIMECREATED \
  --sort-order DESC \
  --limit 1 \
  --query 'data[0].id' \
  --raw-output)

# Create Single Node Pool (2 ARM nodes, A1.Flex 2 OCPU/12GB each)
# Total: 4 OCPU + 24GB RAM = EXACTLY Always Free tier limit
NODE_POOL_ID=$(oci ce node-pool create \
  --cluster-id $CLUSTER_ID \
  --compartment-id $COMPARTMENT_ID \
  --name "free-tier-pool" \
  --kubernetes-version "v1.28.2" \
  --node-shape "VM.Standard.A1.Flex" \
  --node-shape-config '{"ocpus": 2.0, "memoryInGBs": 12.0}' \
  --size 2 \
  --placement-configs "[
    {\"availabilityDomain\":\"$AD1\",\"subnetId\":\"$NODE_SUBNET_ID\"},
    {\"availabilityDomain\":\"$AD2\",\"subnetId\":\"$NODE_SUBNET_ID\"}
  ]" \
  --node-source-details "{
    \"sourceType\": \"IMAGE\",
    \"imageId\": \"$IMAGE_ID\",
    \"bootVolumeSizeInGBs\": 50
  }" \
  --initial-node-labels '[{"key":"pool","value":"free-tier"},{"key":"arch","value":"arm64"}]' \
  --wait-for-state ACTIVE \
  --query 'data.id' \
  --raw-output)

echo "export NODE_POOL_ID=$NODE_POOL_ID" >> ~/.oke-env

# Note: ARM architecture requires ARM64-compatible Docker images
# Frontend and Backend images must be built for ARM64 (multi-arch or native)
```

### 1.6 Configure Storage Class

```bash
# Create OCI Block Volume storage class
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: oci-bv
provisioner: oracle.com/oci
parameters:
  type: paravirtualized
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
reclaimPolicy: Retain
EOF

# Set as default
kubectl patch storageclass oci-bv -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

### Verification

```bash
# Check nodes (should show 2 ARM nodes in Ready state)
kubectl get nodes -o wide

# Check storage class
kubectl get storageclass

# Test cluster access
kubectl cluster-info

# Verify node distribution across ADs
kubectl get nodes -o custom-columns=NAME:.metadata.name,AD:.metadata.labels.topology\\.kubernetes\\.io/zone
```

**Expected Output**:
```
NAME                       READY   STATUS    AD      ARCH
oke-free-tier-pool-node-1  Ready   <none>    AD-1    arm64
oke-free-tier-pool-node-2  Ready   <none>    AD-2    arm64
```

### Rollback

```bash
# Delete node pool
oci ce node-pool delete --node-pool-id $NODE_POOL_ID --force --wait-for-state DELETED

# Delete cluster
oci ce cluster delete --cluster-id $CLUSTER_ID --force --wait-for-state DELETED

# Delete network resources
oci network subnet delete --subnet-id $SVC_SUBNET_ID --force --wait-for-state TERMINATED
oci network subnet delete --subnet-id $NODE_SUBNET_ID --force --wait-for-state TERMINATED
oci network subnet delete --subnet-id $LB_SUBNET_ID --force --wait-for-state TERMINATED
oci network internet-gateway delete --ig-id $IGW_ID --force --wait-for-state TERMINATED
oci network vcn delete --vcn-id $VCN_ID --force --wait-for-state TERMINATED
```

---

## Phase 2: Application Deployment (Week 2, Days 1-3)

**Objective**: Build Docker images, install Dapr, deploy application via Helm.

**Prerequisites**: Phase 1 complete, kubectl configured

**Time**: 8-12 hours | **Cost**: $0 (OCIR free tier: 500GB storage)

### 2.1 Build and Push ARM64 Docker Images to OCIR

**CRITICAL**: OKE uses ARM Ampere A1 nodes, so images MUST be built for ARM64 architecture!

```bash
# Set OCIR variables
export TENANCY_NAMESPACE=$(oci os ns get --query 'data' --raw-output)
export OCIR_REGION="iad"  # us-ashburn-1 = iad
export OCIR_REGISTRY="${OCIR_REGION}.ocir.io"
export IMAGE_PREFIX="${OCIR_REGISTRY}/${TENANCY_NAMESPACE}/todo-phasev"

# Login to OCIR (use auth token as password)
docker login ${OCIR_REGISTRY} -u ${TENANCY_NAMESPACE}/your-oci-username

# Set up Docker buildx for multi-arch builds
docker buildx create --name multiarch --use --platform linux/arm64,linux/amd64
docker buildx inspect --bootstrap

# Build and push backend image for ARM64
cd phaseV/backend
docker buildx build \
  --platform linux/arm64 \
  -t ${IMAGE_PREFIX}/backend:latest \
  -t ${IMAGE_PREFIX}/backend:v1.0.0 \
  --push \
  .

# Build and push frontend image for ARM64
cd ../frontend
docker buildx build \
  --platform linux/arm64 \
  -t ${IMAGE_PREFIX}/frontend:latest \
  -t ${IMAGE_PREFIX}/frontend:v1.0.0 \
  --push \
  .

# Verify images support ARM64
docker manifest inspect ${IMAGE_PREFIX}/backend:latest | grep -A 5 "arm64"
docker manifest inspect ${IMAGE_PREFIX}/frontend:latest | grep -A 5 "arm64"

# Expected: Should show "architecture": "arm64"
```

**Alternative (if buildx not available)**: Build directly on an ARM64 machine or use GitHub Actions ARM64 runners.

### 2.2 Create Image Pull Secret

```bash
# Create namespace
kubectl create namespace $NAMESPACE

# Create OCIR pull secret
kubectl create secret docker-registry ocir-secret \
  --docker-server=${OCIR_REGISTRY} \
  --docker-username="${TENANCY_NAMESPACE}/your-oci-username" \
  --docker-password="<your-auth-token>" \
  --docker-email="your-email@example.com" \
  --namespace=$NAMESPACE
```

### 2.3 Install Dapr on OKE

```bash
# Install Dapr CLI (if not already installed)
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on Kubernetes
dapr init --kubernetes --wait --namespace dapr-system

# Verify Dapr installation
kubectl get pods -n dapr-system

# Expected: dapr-operator, dapr-sidecar-injector, dapr-sentry, dapr-placement
```

### 2.4 Create Application Secrets

**Option A: Using kubectl (for MVP)**

```bash
# Source the production secrets
source phaseV/kubernetes/secrets/.env.production

# Create Kubernetes secret
kubectl create secret generic app-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=kafka-broker="$KAFKA_BROKER" \
  --from-literal=kafka-username="$KAFKA_USERNAME" \
  --from-literal=kafka-password="$KAFKA_PASSWORD" \
  --from-literal=kafka-sasl-mechanism="$KAFKA_SASL_MECHANISM" \
  --from-literal=openai-api-key="$OPENAI_API_KEY" \
  --from-literal=better-auth-secret="$BETTER_AUTH_SECRET" \
  --from-literal=smtp-host="$SMTP_HOST" \
  --from-literal=smtp-port="$SMTP_PORT" \
  --from-literal=smtp-username="$SMTP_USERNAME" \
  --from-literal=smtp-password="$SMTP_PASSWORD" \
  --from-literal=next-public-backend-url="http://backend:8000" \
  --namespace=$NAMESPACE
```

**Option B: Using Sealed Secrets (recommended for GitOps)**

```bash
# Install Sealed Secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Install kubeseal CLI
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/kubeseal-0.24.0-linux-amd64.tar.gz
tar xfz kubeseal-0.24.0-linux-amd64.tar.gz
sudo install -m 755 kubeseal /usr/local/bin/kubeseal

# Create and seal secret
kubectl create secret generic app-secrets \
  --from-env-file=phaseV/kubernetes/secrets/.env.production \
  --namespace=$NAMESPACE \
  --dry-run=client -o yaml | \
  kubeseal -o yaml > phaseV/kubernetes/helm/todo-app/templates/sealed-secret.yaml

# Apply sealed secret (can be committed to Git)
kubectl apply -f phaseV/kubernetes/helm/todo-app/templates/sealed-secret.yaml
```

### 2.5 Deploy Dapr Components

```bash
# Apply Dapr components from existing configs
kubectl apply -f phaseV/kubernetes/dapr-components/ -n $NAMESPACE

# Verify components
kubectl get components -n $NAMESPACE

# Expected: pubsub-kafka, statestore-postgres, secrets-kubernetes, jobs-scheduler
```

### 2.6 Fix MCP Server Dapr Annotations

**Critical Fix**: MCP Server deployment is missing Dapr sidecar annotations.

```bash
# Edit MCP deployment template
vim phaseV/kubernetes/helm/todo-app/templates/mcp-deployment.yaml
```

Add these annotations after line 17 (after labels, before spec):

```yaml
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

Also add service account:

```yaml
spec:
  serviceAccountName: todo-app-sa
  # ... rest of spec
```

### 2.7 Update Helm Values for OKE

Create `phaseV/kubernetes/helm/todo-app/values-oke.yaml`:

```yaml
# OKE Production Values
namespace: "todo-phasev"
environment: "production"

global:
  namespace: "todo-phasev"
  imagePullPolicy: "Always"  # Always pull from OCIR
  imagePullSecrets:
    - name: ocir-secret

# Frontend Configuration
frontend:
  enabled: true
  replicaCount: 2
  image:
    repository: "<OCIR_REGISTRY>/<TENANCY_NAMESPACE>/todo-phasev/frontend"
    tag: "latest"
    pullPolicy: "Always"
  service:
    type: "ClusterIP"
    port: 3000
  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "1000m"
      memory: "1024Mi"
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70

# Backend Configuration (with Dapr)
backend:
  enabled: true
  replicaCount: 2
  image:
    repository: "<OCIR_REGISTRY>/<TENANCY_NAMESPACE>/todo-phasev/backend"
    tag: "latest"
    pullPolicy: "Always"
  service:
    type: "ClusterIP"
    port: 8000
  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "1000m"
      memory: "1024Mi"
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70

# MCP Server (with Dapr - fixed)
mcpServer:
  enabled: true
  replicaCount: 1
  image:
    repository: "<OCIR_REGISTRY>/<TENANCY_NAMESPACE>/todo-phasev/backend"
    tag: "latest"
    pullPolicy: "Always"
  service:
    type: "ClusterIP"
    port: 8001
    targetPort: 8001

# Microservices (with Dapr)
notificationService:
  enabled: true
  replicaCount: 1

emailDeliveryService:
  enabled: true
  replicaCount: 1

recurringTaskService:
  enabled: true
  replicaCount: 1

# Redis Configuration
redis:
  enabled: true
  replicaCount: 1
  persistence:
    enabled: true
    storageClass: "oci-bv"
    size: "10Gi"  # Right-sized (not 50Gi)

# Dapr Configuration
dapr:
  enabled: true
  resources:
    limits:
      cpu: "200m"
      memory: "128Mi"
    requests:
      cpu: "100m"
      memory: "64Mi"
```

Replace `<OCIR_REGISTRY>` and `<TENANCY_NAMESPACE>` with actual values:

```bash
sed -i "s|<OCIR_REGISTRY>|${OCIR_REGISTRY}|g" phaseV/kubernetes/helm/todo-app/values-oke.yaml
sed -i "s|<TENANCY_NAMESPACE>|${TENANCY_NAMESPACE}|g" phaseV/kubernetes/helm/todo-app/values-oke.yaml
```

### 2.8 Deploy Application via Helm

```bash
cd phaseV/kubernetes/helm

# Lint chart
helm lint todo-app -f todo-app/values-oke.yaml

# Dry run to verify
helm install todo-app todo-app \
  --namespace=$NAMESPACE \
  -f todo-app/values-oke.yaml \
  --dry-run --debug

# Deploy
helm install todo-app todo-app \
  --namespace=$NAMESPACE \
  -f todo-app/values-oke.yaml \
  --timeout=10m \
  --wait

# Monitor deployment
kubectl get pods -n $NAMESPACE -w
```

### Verification

```bash
# Check all pods are running
kubectl get pods -n $NAMESPACE

# Expected pods (with Dapr sidecars):
# - frontend-xxx (1 container)
# - backend-xxx (2 containers: app + daprd)
# - mcp-server-xxx (2 containers: app + daprd)
# - notification-service-xxx (2 containers)
# - email-delivery-service-xxx (2 containers)
# - recurring-task-service-xxx (2 containers)
# - redis-0 (1 container)

# Check Dapr sidecars
kubectl get pods -n $NAMESPACE -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'

# Test backend health
kubectl port-forward -n $NAMESPACE svc/backend 8000:8000 &
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# Check Dapr state store connectivity
kubectl logs -n $NAMESPACE -l app=backend -c daprd | grep statestore

# Check Redis persistence
kubectl get pvc -n $NAMESPACE
# Expected: redis-pvc-redis-0 Bound (10Gi)
```

### Rollback

```bash
# Uninstall Helm release
helm uninstall todo-app --namespace=$NAMESPACE

# Delete PVCs (if needed)
kubectl delete pvc -n $NAMESPACE --all

# Delete secrets
kubectl delete secret app-secrets ocir-secret -n $NAMESPACE

# Uninstall Dapr
dapr uninstall --kubernetes --namespace dapr-system
```

---

## Phase 3: Ingress with NodePort (FREE TIER) (Week 2, Days 4-5)

**Objective**: Install Nginx Ingress with NodePort, setup SSL/TLS (NO Load Balancer).

**Prerequisites**: Phase 2 complete, application deployed

**Time**: 3-4 hours | **Cost**: $0 (NodePort is free)

### 3.1 Install Nginx Ingress Controller with NodePort (FREE)

```bash
# Add Nginx Ingress Helm repo
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install Nginx Ingress with NodePort (NO Load Balancer = FREE)
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=NodePort \
  --set controller.service.nodePorts.http=30080 \
  --set controller.service.nodePorts.https=30443 \
  --wait

# Verify Nginx Ingress is running
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx
```

### 3.2 Get Node Public IP and Create Domain

```bash
# Get any node's public IP
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')

# If ExternalIP not available, use InternalIP (and ensure node has public access)
if [ -z "$NODE_IP" ]; then
  NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
fi

echo "Node IP: $NODE_IP"
echo "export NODE_IP=$NODE_IP" >> ~/.oke-env

# Create nip.io domain with NodePort
DOMAIN="${NODE_IP}.nip.io"
echo "Domain: https://${DOMAIN}:30443"
echo "export DOMAIN=$DOMAIN" >> ~/.oke-env

# Note: Access will be via https://<NODE_IP>.nip.io:30443 (port 30443)
```

### 3.3 Install cert-manager for SSL/TLS

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Wait for cert-manager pods
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s

# Create Let's Encrypt ClusterIssuer (HTTP-01 challenge for nip.io)
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 3.4 Create Ingress Resource

```bash
# Create ingress with SSL/TLS
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-app-ingress
  namespace: $NAMESPACE
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - ${DOMAIN}
    secretName: todo-app-tls
  rules:
  - host: ${DOMAIN}
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
EOF
```

### 3.5 Update Frontend Environment Variable

```bash
# Update backend URL in frontend deployment
kubectl set env deployment/frontend -n $NAMESPACE NEXT_PUBLIC_BACKEND_URL=https://${DOMAIN}/api

# Or update via Helm values and upgrade
cat >> phaseV/kubernetes/helm/todo-app/values-oke.yaml <<EOF

# Ingress Configuration
ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: ${DOMAIN}
      paths:
        - path: /api
          pathType: Prefix
          backend:
            service:
              name: backend
              port:
                number: 8000
        - path: /
          pathType: Prefix
          backend:
            service:
              name: frontend
              port:
                number: 3000
  tls:
    - secretName: todo-app-tls
      hosts:
        - ${DOMAIN}

# Frontend environment
frontend:
  env:
    - name: NEXT_PUBLIC_BACKEND_URL
      value: "https://${DOMAIN}/api"
EOF

helm upgrade todo-app todo-app \
  --namespace=$NAMESPACE \
  -f todo-app/values-oke.yaml
```

### Verification

```bash
# Check cert-manager certificate issuance
kubectl get certificate -n $NAMESPACE
# Expected: todo-app-tls Ready=True

kubectl describe certificate todo-app-tls -n $NAMESPACE

# Check ingress
kubectl get ingress -n $NAMESPACE

# Test HTTPS access
curl -I https://${DOMAIN}
# Expected: HTTP/2 200

# Test API endpoint
curl https://${DOMAIN}/api/health
# Expected: {"status": "healthy"}

# Open in browser
echo "Access application at: https://${DOMAIN}"
```

**Expected Output**:
- Certificate issued within 5 minutes
- HTTPS redirects working
- API accessible at `https://<IP>.nip.io/api/*`
- Frontend accessible at `https://<IP>.nip.io/`

### Rollback

```bash
# Delete ingress
kubectl delete ingress todo-app-ingress -n $NAMESPACE

# Delete certificate
kubectl delete certificate todo-app-tls -n $NAMESPACE

# Uninstall cert-manager
kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Uninstall Nginx Ingress
helm uninstall ingress-nginx --namespace ingress-nginx
```

---

## Phase 4: Monitoring & Observability (Week 3, Days 1-3)

**Objective**: Install Prometheus + Grafana for metrics and dashboards.

**Prerequisites**: Phase 3 complete

**Time**: 6-8 hours | **Cost**: $0 (storage within 200GB free tier limit)

### 4.1 Install Prometheus Stack

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack (Prometheus + Grafana + AlertManager)
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.retention=7d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.storageClassName=oci-bv \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=10Gi \
  --set grafana.persistence.enabled=true \
  --set grafana.persistence.storageClassName=oci-bv \
  --set grafana.persistence.size=5Gi \
  --set grafana.adminPassword='<strong-password>' \
  --wait

# Wait for all pods
kubectl wait --for=condition=ready pod -l release=prometheus -n monitoring --timeout=600s
```

### 4.2 Configure Dapr Metrics Scraping

```bash
# Create ServiceMonitor for Dapr sidecars
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: dapr-sidecar
  namespace: monitoring
  labels:
    app: dapr
spec:
  selector:
    matchLabels:
      dapr.io/sidecar: "true"
  namespaceSelector:
    matchNames:
      - $NAMESPACE
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
EOF
```

### 4.3 Expose Grafana via Ingress

```bash
# Create Grafana ingress
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: grafana-ingress
  namespace: monitoring
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - grafana.${DOMAIN}
    secretName: grafana-tls
  rules:
  - host: grafana.${DOMAIN}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: prometheus-grafana
            port:
              number: 80
EOF
```

### 4.4 Import Dapr Dashboards

```bash
# Get Grafana admin password
GRAFANA_PASSWORD=$(kubectl get secret prometheus-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode)

echo "Grafana URL: https://grafana.${DOMAIN}"
echo "Username: admin"
echo "Password: $GRAFANA_PASSWORD"

# Import Dapr dashboard (manual step)
# 1. Login to Grafana
# 2. Go to Dashboards → Import
# 3. Use Dashboard ID: 19490 (Dapr Dashboard for Kubernetes)
# 4. Select Prometheus data source
```

### 4.5 Configure Alerts

```bash
# Create PrometheusRule for critical alerts
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: todo-app-alerts
  namespace: monitoring
  labels:
    prometheus: kube-prometheus
spec:
  groups:
  - name: todo-app
    interval: 30s
    rules:
    - alert: PodCrashLooping
      expr: rate(kube_pod_container_status_restarts_total{namespace="$NAMESPACE"}[5m]) > 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Pod {{ \$labels.pod }} is crash looping"
        description: "Pod {{ \$labels.pod }} in namespace {{ \$labels.namespace }} has restarted {{ \$value }} times in the last 5 minutes"

    - alert: HighMemoryUsage
      expr: container_memory_usage_bytes{namespace="$NAMESPACE"} / container_spec_memory_limit_bytes{namespace="$NAMESPACE"} > 0.9
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High memory usage for {{ \$labels.pod }}"
        description: "Pod {{ \$labels.pod }} is using {{ \$value | humanizePercentage }} of its memory limit"

    - alert: DaprSidecarDown
      expr: up{job="dapr-sidecar"} == 0
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "Dapr sidecar is down"
        description: "Dapr sidecar for {{ \$labels.pod }} is not responding"
EOF
```

### Verification

```bash
# Check Prometheus and Grafana pods
kubectl get pods -n monitoring

# Access Grafana
echo "Grafana: https://grafana.${DOMAIN}"
echo "Username: admin"
echo "Password: $GRAFANA_PASSWORD"

# Check Prometheus targets
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090 &
# Open http://localhost:9090/targets

# Verify Dapr metrics
curl http://localhost:9090/api/v1/query?query=dapr_http_server_request_count
```

**Expected**:
- Grafana accessible at `https://grafana.<IP>.nip.io`
- Dapr dashboards showing metrics
- Alerts configured (visible in Grafana → Alerting)
- Prometheus scraping all pods

### Rollback

```bash
# Uninstall Prometheus stack
helm uninstall prometheus --namespace monitoring

# Delete PVCs
kubectl delete pvc -n monitoring --all

# Delete namespace
kubectl delete namespace monitoring
```

---

## Phase 5: CI/CD Automation (Week 3, Days 4-5 & Week 4, Day 1)

**Objective**: Automate deployments via GitHub Actions.

**Prerequisites**: Phase 4 complete

**Time**: 6-10 hours | **Cost**: $0 (GitHub Actions free tier)

### 5.1 Create GitHub Secrets

Go to GitHub repo → Settings → Secrets and variables → Actions → New repository secret:

```
OCI_CLI_USER: <tenancy-namespace>/your-username
OCI_CLI_TENANCY: ocid1.tenancy.oc1..xxxxx
OCI_CLI_FINGERPRINT: xx:xx:xx:...
OCI_CLI_KEY_CONTENT: <paste private key content>
OCI_CLI_REGION: us-ashburn-1
OCI_COMPARTMENT_ID: ocid1.compartment.oc1..xxxxx
OKE_CLUSTER_ID: ocid1.cluster.oc1..xxxxx
OCIR_USERNAME: <tenancy-namespace>/your-username
OCIR_TOKEN: <auth-token>
KUBECONFIG_CONTENT: <paste kubeconfig content>
```

### 5.2 Create GitHub Actions Workflow

Create `.github/workflows/deploy-oke.yml`:

```yaml
name: Deploy to OKE

on:
  push:
    branches:
      - main
    paths:
      - 'phaseV/**'
  workflow_dispatch:

env:
  OCI_CLI_USER: ${{ secrets.OCI_CLI_USER }}
  OCI_CLI_TENANCY: ${{ secrets.OCI_CLI_TENANCY }}
  OCI_CLI_FINGERPRINT: ${{ secrets.OCI_CLI_FINGERPRINT }}
  OCI_CLI_KEY_CONTENT: ${{ secrets.OCI_CLI_KEY_CONTENT }}
  OCI_CLI_REGION: ${{ secrets.OCI_CLI_REGION }}
  OCIR_REGISTRY: iad.ocir.io
  IMAGE_PREFIX: iad.ocir.io/${{ secrets.TENANCY_NAMESPACE }}/todo-phasev

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to OCIR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.OCIR_REGISTRY }}
          username: ${{ secrets.OCIR_USERNAME }}
          password: ${{ secrets.OCIR_TOKEN }}

      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: ./phaseV/backend
          push: true
          tags: |
            ${{ env.IMAGE_PREFIX }}/backend:latest
            ${{ env.IMAGE_PREFIX }}/backend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./phaseV/frontend
          push: true
          tags: |
            ${{ env.IMAGE_PREFIX }}/frontend:latest
            ${{ env.IMAGE_PREFIX }}/frontend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Install OCI CLI
        run: |
          curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh | bash -s -- --accept-all-defaults
          echo "$HOME/bin" >> $GITHUB_PATH

      - name: Configure OCI CLI
        run: |
          mkdir -p ~/.oci
          echo "${{ secrets.OCI_CLI_KEY_CONTENT }}" > ~/.oci/key.pem
          chmod 600 ~/.oci/key.pem
          cat > ~/.oci/config <<EOF
          [DEFAULT]
          user=${{ secrets.OCI_CLI_USER }}
          fingerprint=${{ secrets.OCI_CLI_FINGERPRINT }}
          tenancy=${{ secrets.OCI_CLI_TENANCY }}
          region=${{ secrets.OCI_CLI_REGION }}
          key_file=~/.oci/key.pem
          EOF

      - name: Configure kubectl
        run: |
          mkdir -p ~/.kube
          echo "${{ secrets.KUBECONFIG_CONTENT }}" | base64 -d > ~/.kube/config

      - name: Install Helm
        uses: azure/setup-helm@v3
        with:
          version: '3.13.0'

      - name: Deploy to OKE via Helm
        run: |
          helm upgrade --install todo-app phaseV/kubernetes/helm/todo-app \
            --namespace todo-phasev \
            -f phaseV/kubernetes/helm/todo-app/values-oke.yaml \
            --set backend.image.tag=${{ github.sha }} \
            --set frontend.image.tag=${{ github.sha }} \
            --set mcpServer.image.tag=${{ github.sha }} \
            --timeout=10m \
            --wait

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/backend -n todo-phasev --timeout=5m
          kubectl rollout status deployment/frontend -n todo-phasev --timeout=5m
          kubectl get pods -n todo-phasev

      - name: Run smoke tests
        run: |
          LB_IP=$(kubectl get ingress todo-app-ingress -n todo-phasev -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
          curl -f https://${LB_IP}.nip.io/api/health || exit 1
          curl -f https://${LB_IP}.nip.io/ || exit 1
```

### 5.3 Create Rollback Workflow

Create `.github/workflows/rollback-oke.yml`:

```yaml
name: Rollback OKE Deployment

on:
  workflow_dispatch:
    inputs:
      revision:
        description: 'Helm revision to rollback to (leave empty for previous)'
        required: false
        default: ''

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - name: Configure kubectl
        run: |
          mkdir -p ~/.kube
          echo "${{ secrets.KUBECONFIG_CONTENT }}" | base64 -d > ~/.kube/config

      - name: Install Helm
        uses: azure/setup-helm@v3
        with:
          version: '3.13.0'

      - name: Rollback Helm release
        run: |
          if [ -z "${{ github.event.inputs.revision }}" ]; then
            echo "Rolling back to previous revision"
            helm rollback todo-app --namespace todo-phasev --wait
          else
            echo "Rolling back to revision ${{ github.event.inputs.revision }}"
            helm rollback todo-app ${{ github.event.inputs.revision }} --namespace todo-phasev --wait
          fi

      - name: Verify rollback
        run: |
          kubectl rollout status deployment/backend -n todo-phasev --timeout=5m
          kubectl rollout status deployment/frontend -n todo-phasev --timeout=5m
          kubectl get pods -n todo-phasev
```

### Verification

```bash
# Make a change to trigger workflow
echo "# Test change" >> phaseV/README.md
git add phaseV/README.md
git commit -m "test: trigger CI/CD"
git push origin main

# Watch GitHub Actions
# Go to repo → Actions → Deploy to OKE

# Verify deployment after workflow completes
kubectl get pods -n todo-phasev
helm list -n todo-phasev

# Check deployment history
helm history todo-app -n todo-phasev
```

**Expected**:
- Workflow completes successfully
- New images deployed with git SHA tags
- Rollout successful
- Application accessible

### Rollback

```bash
# Manual rollback if workflow fails
helm rollback todo-app --namespace=$NAMESPACE

# Or via GitHub Actions
# Go to Actions → Rollback OKE Deployment → Run workflow
```

---

## Phase 6: Security Hardening (Week 4, Days 2-3)

**Objective**: Implement network policies, RBAC, pod security standards.

**Prerequisites**: Phase 5 complete

**Time**: 4-6 hours | **Cost**: $0

### 6.1 Create Service Account and RBAC

```bash
# Create service account
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: todo-app-sa
  namespace: $NAMESPACE
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: todo-app-role
  namespace: $NAMESPACE
rules:
- apiGroups: [""]
  resources: ["secrets", "configmaps"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
EOF

# Bind role to service account
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: todo-app-rolebinding
  namespace: $NAMESPACE
subjects:
- kind: ServiceAccount
  name: todo-app-sa
  namespace: $NAMESPACE
roleRef:
  kind: Role
  name: todo-app-role
  apiGroup: rbac.authorization.k8s.io
EOF

# Update deployments to use service account (add to Helm values or patch)
kubectl patch deployment backend -n $NAMESPACE -p '{"spec":{"template":{"spec":{"serviceAccountName":"todo-app-sa"}}}}'
kubectl patch deployment frontend -n $NAMESPACE -p '{"spec":{"template":{"spec":{"serviceAccountName":"todo-app-sa"}}}}'
```

### 6.2 Create Network Policies

```bash
# Deny all ingress by default
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: $NAMESPACE
spec:
  podSelector: {}
  policyTypes:
  - Ingress
EOF

# Allow ingress from Nginx Ingress to Frontend/Backend
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-to-frontend
  namespace: $NAMESPACE
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 3000
EOF

kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-to-backend
  namespace: $NAMESPACE
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8000
EOF

# Allow Dapr sidecar communication
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dapr-sidecar
  namespace: $NAMESPACE
spec:
  podSelector:
    matchLabels:
      dapr.io/enabled: "true"
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: dapr-system
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 3500
    - protocol: TCP
      port: 9090
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: dapr-system
  - to:
    - podSelector: {}
EOF

# Allow egress to external services (Neon, Redpanda)
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-external-egress
  namespace: $NAMESPACE
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector: {}
  - to:
    - podSelector: {}
  - ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 9093
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
EOF
```

### 6.3 Enable Pod Security Standards

```bash
# Label namespace with Pod Security Standard (restricted)
kubectl label namespace $NAMESPACE pod-security.kubernetes.io/enforce=baseline
kubectl label namespace $NAMESPACE pod-security.kubernetes.io/audit=restricted
kubectl label namespace $NAMESPACE pod-security.kubernetes.io/warn=restricted

# Update deployments to comply with restricted PSS
# Add security context to Helm values:
cat >> phaseV/kubernetes/helm/todo-app/values-oke.yaml <<'EOF'

# Security Context (Pod Security Standards)
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault

containerSecurityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: false
EOF

# Upgrade Helm release with security context
helm upgrade todo-app phaseV/kubernetes/helm/todo-app \
  --namespace=$NAMESPACE \
  -f phaseV/kubernetes/helm/todo-app/values-oke.yaml
```

### 6.4 Scan Images for Vulnerabilities

```bash
# Install Trivy (if not already installed)
wget https://github.com/aquasecurity/trivy/releases/download/v0.46.0/trivy_0.46.0_Linux-64bit.tar.gz
tar zxvf trivy_0.46.0_Linux-64bit.tar.gz
sudo mv trivy /usr/local/bin/

# Scan images in OCIR
trivy image ${IMAGE_PREFIX}/backend:latest
trivy image ${IMAGE_PREFIX}/frontend:latest

# Add Trivy to GitHub Actions workflow
# (Add step before deploy in .github/workflows/deploy-oke.yml)
```

### Verification

```bash
# Test network policies
kubectl run -it --rm debug --image=busybox --restart=Never -n $NAMESPACE -- wget -O- http://backend:8000/health

# Should fail (network policy blocks)
kubectl run -it --rm debug --image=busybox --restart=Never -n default -- wget -O- http://backend.todo-phasev:8000/health

# Check pod security
kubectl get pods -n $NAMESPACE -o json | jq '.items[].spec.securityContext'

# Verify RBAC
kubectl auth can-i get secrets --as=system:serviceaccount:$NAMESPACE:todo-app-sa -n $NAMESPACE
# Expected: yes

kubectl auth can-i delete secrets --as=system:serviceaccount:$NAMESPACE:todo-app-sa -n $NAMESPACE
# Expected: no
```

### Rollback

```bash
# Remove network policies
kubectl delete networkpolicy --all -n $NAMESPACE

# Remove Pod Security labels
kubectl label namespace $NAMESPACE pod-security.kubernetes.io/enforce-
kubectl label namespace $NAMESPACE pod-security.kubernetes.io/audit-
kubectl label namespace $NAMESPACE pod-security.kubernetes.io/warn-

# Revert security context changes
helm upgrade todo-app phaseV/kubernetes/helm/todo-app \
  --namespace=$NAMESPACE \
  -f phaseV/kubernetes/helm/todo-app/values-oke.yaml \
  --reset-values
```

---

## Phase 7: Operational Procedures (Week 4, Day 4)

**Objective**: Document operational procedures and disaster recovery.

**Prerequisites**: Phase 6 complete

**Time**: 3-4 hours | **Cost**: $0

### 7.1 Create RUNBOOK.md

Create `phaseV/docs/RUNBOOK.md` with common operational procedures:

```markdown
# Todo App Phase V - Production Runbook

## Common Operations

### Check Application Health
```bash
# Check all pods
kubectl get pods -n todo-phasev

# Check services
kubectl get svc -n todo-phasev

# Check ingress
kubectl get ingress -n todo-phasev

# Test API health
curl https://<LOAD_BALANCER_IP>.nip.io/api/health
```

### View Logs
```bash
# Backend logs
kubectl logs -n todo-phasev -l app=backend -c backend --tail=100 -f

# Dapr sidecar logs
kubectl logs -n todo-phasev -l app=backend -c daprd --tail=100 -f

# All pods logs
kubectl logs -n todo-phasev --all-containers=true --tail=100 -f
```

### Scale Services
```bash
# Scale backend
kubectl scale deployment backend -n todo-phasev --replicas=3

# Scale frontend
kubectl scale deployment frontend -n todo-phasev --replicas=4

# Check HPA status
kubectl get hpa -n todo-phasev
```

### Update Secrets
```bash
# Update database URL
kubectl create secret generic app-secrets \
  --from-literal=database-url="new-value" \
  --namespace=todo-phasev \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new secret
kubectl rollout restart deployment/backend -n todo-phasev
```

### Rollback Deployment
```bash
# View deployment history
helm history todo-app -n todo-phasev

# Rollback to previous version
helm rollback todo-app -n todo-phasev

# Rollback to specific revision
helm rollback todo-app 5 -n todo-phasev
```

### Database Migrations
```bash
# Run Alembic migrations manually
kubectl exec -it deployment/backend -n todo-phasev -c backend -- alembic upgrade head

# Downgrade migration
kubectl exec -it deployment/backend -n todo-phasev -c backend -- alembic downgrade -1
```

### Debug Dapr Issues
```bash
# Check Dapr components
kubectl get components -n todo-phasev

# Check Dapr sidecar status
kubectl get pods -n todo-phasev -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[?(@.name=="daprd")].ready}{"\n"}{end}'

# View Dapr placement tables
kubectl logs -n dapr-system -l app=dapr-placement
```

## Incident Response

### Pod CrashLoopBackOff
1. Check logs: `kubectl logs -n todo-phasev <pod-name> --previous`
2. Describe pod: `kubectl describe pod -n todo-phasev <pod-name>`
3. Check events: `kubectl get events -n todo-phasev --sort-by='.lastTimestamp'`
4. Common causes:
   - Database connection failure → Check DATABASE_URL secret
   - Kafka connection failure → Check Dapr pubsub component
   - OOM → Increase memory limits

### Ingress Not Accessible
1. Check ingress controller: `kubectl get pods -n ingress-nginx`
2. Check load balancer: `kubectl get svc -n ingress-nginx`
3. Check certificate: `kubectl get certificate -n todo-phasev`
4. Check ingress: `kubectl describe ingress todo-app-ingress -n todo-phasev`

### High Memory/CPU Usage
1. Check metrics: `kubectl top pods -n todo-phasev`
2. Check HPA status: `kubectl get hpa -n todo-phasev`
3. Scale manually if needed
4. Review Grafana dashboards for trends

### Dapr Component Failure
1. Check component status: `kubectl describe component <component-name> -n todo-phasev`
2. Check Dapr system logs: `kubectl logs -n dapr-system -l app=dapr-operator`
3. Restart Dapr sidecars: `kubectl rollout restart deployment/<app> -n todo-phasev`

## Disaster Recovery

### Backup Procedures
1. **Database**: Neon provides automatic backups (managed)
2. **Redis**: Backed by OCI Block Volume with retention policy
3. **Kubernetes manifests**: Version controlled in Git
4. **Secrets**: Backup using Sealed Secrets (committed to Git)

### Recovery Procedures
1. **Cluster failure**: Recreate using Phase 1 scripts
2. **Application failure**: Helm rollback
3. **Data loss**: Restore from Neon backup (via Neon console)
4. **Redis data loss**: Restore from OCI Block Volume snapshot

### Backup Redis Data
```bash
# Create snapshot
kubectl exec -n todo-phasev redis-0 -- redis-cli SAVE

# Copy backup from pod
kubectl cp todo-phasev/redis-0:/data/dump.rdb ./redis-backup.rdb
```

### Restore Redis Data
```bash
# Upload backup to pod
kubectl cp ./redis-backup.rdb todo-phasev/redis-0:/data/dump.rdb

# Restart Redis
kubectl delete pod redis-0 -n todo-phasev
```
```

### 7.2 Create Monitoring Dashboard

Access Grafana and create a custom "Todo App Overview" dashboard:

1. Login to Grafana: `https://grafana.<IP>.nip.io`
2. Create new dashboard
3. Add panels:
   - Pod CPU Usage (query: `sum(rate(container_cpu_usage_seconds_total{namespace="todo-phasev"}[5m])) by (pod)`)
   - Pod Memory Usage (query: `sum(container_memory_usage_bytes{namespace="todo-phasev"}) by (pod)`)
   - HTTP Request Rate (query: `sum(rate(http_requests_total{namespace="todo-phasev"}[5m]))`)
   - Dapr Pub/Sub Success Rate (query: `sum(rate(dapr_component_pubsub_ingress_count{namespace="todo-phasev"}[5m]))`)
   - Pod Restart Count (query: `sum(kube_pod_container_status_restarts_total{namespace="todo-phasev"})`)

### Verification

- [ ] RUNBOOK.md created with all common procedures
- [ ] Grafana dashboard created and saved
- [ ] Team trained on runbook procedures
- [ ] Disaster recovery plan tested (dry run)

---

## Phase 8: Validation & Go-Live (Week 4, Day 5 & Week 5)

**Objective**: Comprehensive testing and production go-live.

**Prerequisites**: All phases 0-7 complete

**Time**: 8-12 hours | **Cost**: $0

### 8.1 End-to-End Testing Checklist

```bash
# Set variables
LB_IP=$(kubectl get ingress todo-app-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
APP_URL="https://${LB_IP}.nip.io"

# 1. Frontend Accessibility
curl -I $APP_URL
# Expected: HTTP/2 200, redirect to HTTPS

# 2. API Health Check
curl ${APP_URL}/api/health
# Expected: {"status": "healthy"}

# 3. Database Connectivity
# (via backend health endpoint - checks DB connection)

# 4. Kafka Connectivity (via Dapr)
# Create task via ChatKit UI → Check Kafka topic for event

# 5. Redis Session Cache
# Login → Verify session persists across backend pod restarts

# 6. SSL/TLS Certificate
openssl s_client -connect ${LB_IP}.nip.io:443 -servername ${LB_IP}.nip.io | grep "Verify return code"
# Expected: Verify return code: 0 (ok)

# 7. MCP Tools via ChatKit
# Open ChatKit UI → Test all 17 MCP tools
# - create_task
# - list_tasks
# - update_task
# - delete_task
# - mark_task_complete
# - search_tasks
# - get_task_by_id
# - create_category
# - list_categories
# - update_category
# - delete_category
# - create_tag
# - list_tags
# - update_tag
# - delete_tag
# - add_tag_to_task
# - remove_tag_from_task

# 8. Dapr State Store
kubectl exec -n $NAMESPACE deployment/backend -c backend -- python -c "import requests; print(requests.get('http://localhost:3500/v1.0/state/statestore').status_code)"
# Expected: 200 or 204

# 9. Notifications (Email via Gmail SMTP)
# Create task with due date → Verify reminder email sent

# 10. Recurring Tasks
# Create recurring task (daily) → Wait 24h → Verify new instance created
```

### 8.2 Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API endpoint (1000 requests, 10 concurrent)
ab -n 1000 -c 10 -H "Authorization: Bearer <token>" ${APP_URL}/api/tasks

# Test frontend (500 requests, 5 concurrent)
ab -n 500 -c 5 ${APP_URL}/

# Monitor during load test
kubectl top pods -n $NAMESPACE
kubectl get hpa -n $NAMESPACE -w

# Expected: HPA scales pods from 2 to 3-5 under load
```

### 8.3 Resilience Testing

```bash
# Test pod recovery
kubectl delete pod -n $NAMESPACE -l app=backend --force
# Watch pods restart
kubectl get pods -n $NAMESPACE -w
# Expected: New pod starts within 30 seconds, traffic continues

# Test Redis persistence
kubectl delete pod redis-0 -n $NAMESPACE
# Wait for pod to restart
sleep 60
# Verify data persists (login session still valid)

# Test Dapr sidecar recovery
kubectl exec -n $NAMESPACE deployment/backend -c daprd -- killall daprd
# Expected: Dapr sidecar restarts automatically
```

### 8.4 Security Validation

```bash
# Test network policies
kubectl run -it --rm debug --image=busybox --restart=Never -n default -- wget -O- http://backend.todo-phasev:8000/health
# Expected: Connection timeout (network policy blocks)

# Test pod security
kubectl auth can-i delete pods --as=system:serviceaccount:$NAMESPACE:todo-app-sa -n $NAMESPACE
# Expected: no

# Scan for vulnerabilities
trivy image ${IMAGE_PREFIX}/backend:latest
# Expected: No HIGH or CRITICAL vulnerabilities

# Test SSL/TLS
testssl ${LB_IP}.nip.io
# Expected: Grade A or B
```

### 8.5 Go-Live Checklist

**Pre-Go-Live (24 hours before)**:
- [ ] All tests passing (E2E, load, resilience, security)
- [ ] Monitoring dashboards configured and tested
- [ ] Alerts configured and tested
- [ ] Runbook reviewed by team
- [ ] Rollback procedure tested
- [ ] Backup procedures verified
- [ ] DNS records ready (if using custom domain)
- [ ] SSL certificates valid and auto-renewing
- [ ] Secrets rotated to production values
- [ ] Database migrations tested on staging
- [ ] Team notified of go-live window

**Go-Live Steps**:
1. [ ] Final smoke test on staging
2. [ ] Run database migrations
   ```bash
   kubectl exec -it deployment/backend -n $NAMESPACE -c backend -- alembic upgrade head
   ```
3. [ ] Deploy latest version
   ```bash
   helm upgrade todo-app phaseV/kubernetes/helm/todo-app \
     --namespace=$NAMESPACE \
     -f phaseV/kubernetes/helm/todo-app/values-oke.yaml
   ```
4. [ ] Verify all pods running
   ```bash
   kubectl get pods -n $NAMESPACE
   ```
5. [ ] Run smoke tests
   ```bash
   curl ${APP_URL}/api/health
   ```
6. [ ] Monitor Grafana for 30 minutes
7. [ ] Test critical user flows (login, create task, etc.)
8. [ ] Announce go-live to users

**Post-Go-Live (first 24 hours)**:
- [ ] Monitor error rates in Grafana
- [ ] Check Prometheus alerts
- [ ] Review application logs
- [ ] Monitor resource usage
- [ ] Verify HPA behavior under real traffic
- [ ] Test rollback procedure (if issues arise)

### 8.6 Success Criteria

**Performance**:
- [ ] p95 latency < 500ms for all API endpoints
- [ ] Frontend loads in < 3 seconds
- [ ] HPA scales within 2 minutes under load
- [ ] Zero downtime during deployments

**Reliability**:
- [ ] 99.9% uptime (measured over 7 days)
- [ ] Zero data loss incidents
- [ ] Automatic recovery from pod failures
- [ ] SSL certificate auto-renewal working

**Security**:
- [ ] All network policies enforced
- [ ] No HIGH/CRITICAL vulnerabilities
- [ ] Pod security standards enforced
- [ ] Secrets stored securely (not in Git)

**Observability**:
- [ ] All metrics flowing to Prometheus
- [ ] Grafana dashboards showing real-time data
- [ ] Alerts firing correctly
- [ ] Logs searchable in kubectl

**Operations**:
- [ ] CI/CD pipeline deploying automatically
- [ ] Rollback working in < 5 minutes
- [ ] Team can execute runbook procedures
- [ ] Backup/restore procedures verified

### Verification

```bash
# Final verification script
cat > verify-production.sh <<'EOF'
#!/bin/bash
set -e

echo "=== Production Verification ==="

# 1. Check all pods running
echo "[1/10] Checking pods..."
kubectl get pods -n todo-phasev | grep -v "Running" | grep -v "NAME" && echo "FAIL: Not all pods running" || echo "PASS"

# 2. Check ingress
echo "[2/10] Checking ingress..."
LB_IP=$(kubectl get ingress todo-app-ingress -n todo-phasev -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -sf https://${LB_IP}.nip.io/api/health > /dev/null && echo "PASS" || echo "FAIL"

# 3. Check certificate
echo "[3/10] Checking SSL certificate..."
kubectl get certificate -n todo-phasev -o jsonpath='{.items[0].status.conditions[?(@.type=="Ready")].status}' | grep -q "True" && echo "PASS" || echo "FAIL"

# 4. Check Dapr components
echo "[4/10] Checking Dapr components..."
[ $(kubectl get components -n todo-phasev -o json | jq '.items | length') -eq 4 ] && echo "PASS" || echo "FAIL"

# 5. Check HPA
echo "[5/10] Checking HPA..."
kubectl get hpa -n todo-phasev | grep -q "backend" && echo "PASS" || echo "FAIL"

# 6. Check monitoring
echo "[6/10] Checking monitoring..."
kubectl get pods -n monitoring | grep prometheus | grep -q "Running" && echo "PASS" || echo "FAIL"

# 7. Check storage
echo "[7/10] Checking storage..."
kubectl get pvc -n todo-phasev | grep redis | grep -q "Bound" && echo "PASS" || echo "FAIL"

# 8. Check network policies
echo "[8/10] Checking network policies..."
[ $(kubectl get networkpolicy -n todo-phasev -o json | jq '.items | length') -ge 4 ] && echo "PASS" || echo "FAIL"

# 9. Check RBAC
echo "[9/10] Checking RBAC..."
kubectl get serviceaccount todo-app-sa -n todo-phasev > /dev/null 2>&1 && echo "PASS" || echo "FAIL"

# 10. Check GitHub Actions
echo "[10/10] Checking GitHub Actions..."
[ -f .github/workflows/deploy-oke.yml ] && echo "PASS" || echo "FAIL"

echo "=== Verification Complete ==="
EOF

chmod +x verify-production.sh
./verify-production.sh
```

**Expected Output**: All checks show "PASS"

---

## Cost Summary (100% FREE TIER)

| Component | Configuration | Monthly Cost |
|-----------|---------------|--------------|
| **Compute (ARM)** | | |
| - Free Tier Node Pool | 2 × A1.Flex (2 OCPU, 12GB ARM) | **$0** ✅ (Always Free) |
| **Networking** | | |
| - NodePort (No Load Balancer) | Ports 30080, 30443 | **$0** ✅ (Always Free) |
| - Egress Bandwidth | 10TB/month outbound | **$0** ✅ (Always Free) |
| **Storage** | | |
| - Redis (Block Volume) | 10Gi | **$0** ✅ (< 200GB Always Free limit) |
| - Prometheus (metrics) | 10Gi | **$0** ✅ (< 200GB Always Free limit) |
| - Grafana (dashboards) | 5Gi | **$0** ✅ (< 200GB Always Free limit) |
| - Total Storage Used | 25Gi of 200Gi free tier | **$0** ✅ (Within limit) |
| **Container Registry** | | |
| - OCIR (Oracle Cloud Infrastructure Registry) | 500GB storage | **$0** ✅ (Always Free) |
| **External Services** | | |
| - Neon PostgreSQL | Serverless (existing) | **$0** ✅ (Free tier) |
| - Redpanda Kafka | Managed (existing) | **$0** ✅ (Free tier) |
| **TOTAL (All Costs)** | | **$0/month** ✅ |

**Notes**:
- ✅ 100% free tier deployment - zero ongoing costs
- ⚠️ No autoscaling available (free tier limits: 4 OCPU + 24GB RAM total)
- ⚠️ ARM architecture requires ARM64-compatible Docker images
- ⚠️ Access via NodePort (`:30443`) instead of standard HTTPS (`:443`)
- 🎯 Perfect for dev/test/demo environments
- 📈 To upgrade: Add OCI Load Balancer (~$35-50/month) + scale to x86 nodes

---

## Rollback Plan (Emergency)

If critical issues arise in production:

### Immediate Rollback (< 5 minutes)

```bash
# 1. Rollback to previous Helm release
helm rollback todo-app --namespace=todo-phasev --wait

# 2. Verify rollback
kubectl rollout status deployment/backend -n todo-phasev
kubectl rollout status deployment/frontend -n todo-phasev

# 3. Check application health
LB_IP=$(kubectl get ingress todo-app-ingress -n todo-phasev -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl https://${LB_IP}.nip.io/api/health
```

### Database Rollback (if migrations fail)

```bash
# Downgrade Alembic migrations
kubectl exec -it deployment/backend -n todo-phasev -c backend -- alembic downgrade -1

# Or restore from Neon backup (via Neon console)
```

### Complete Infrastructure Rollback

```bash
# If infrastructure changes cause issues:
# 1. Delete current deployment
helm uninstall todo-app --namespace=todo-phasev

# 2. Revert infrastructure changes (e.g., network policies)
kubectl delete networkpolicy --all -n todo-phasev

# 3. Redeploy previous stable version
helm install todo-app phaseV/kubernetes/helm/todo-app \
  --namespace=todo-phasev \
  -f phaseV/kubernetes/helm/todo-app/values-oke.yaml \
  --version <previous-stable-version>
```

---

## Post-Deployment Optimization (Optional Phase 9)

After 1-2 weeks of production operation, consider these optimizations:

### 1. Cost Optimization
- Analyze actual resource usage via Grafana
- Right-size CPU/memory requests and limits
- Enable cluster autoscaler for node pool
- Consider Reserved Compute for predictable workloads

### 2. Performance Optimization
- Enable Redis persistence AOF for durability
- Add read replicas for PostgreSQL (if needed)
- Implement CDN for frontend static assets
- Optimize Docker image sizes

### 3. Observability Enhancement
- Add Loki for centralized log aggregation
- Add Jaeger for distributed tracing
- Create SLI/SLO dashboards
- Configure on-call rotation and PagerDuty integration

### 4. Security Enhancement
- Migrate from Sealed Secrets to OCI Vault
- Implement private node pools (NAT Gateway)
- Add Web Application Firewall (WAF) rules
- Enable OCI Security Advisor

### 5. Operational Excellence
- Implement GitOps with ArgoCD or Flux
- Add automated backups for Redis
- Implement canary deployments
- Add chaos engineering tests (Chaos Mesh)

---

## Support and Troubleshooting

### Getting Help

1. **Kubernetes Issues**: Check kubectl logs and describe resources
2. **Dapr Issues**: Check Dapr documentation at https://docs.dapr.io
3. **OCI Issues**: Check OCI documentation at https://docs.oracle.com/iaas
4. **Application Issues**: Review application logs and Grafana metrics

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Pods stuck in Pending | Check node resources: `kubectl describe node` |
| ImagePullBackOff | Verify OCIR credentials: `kubectl describe pod <pod-name>` |
| CrashLoopBackOff | Check logs: `kubectl logs <pod-name> --previous` |
| Ingress not working | Check ingress controller: `kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller` |
| Certificate not issuing | Check cert-manager: `kubectl logs -n cert-manager -l app=cert-manager` |
| Dapr sidecar issues | Check Dapr logs: `kubectl logs <pod-name> -c daprd` |
| High costs | Review OCI Cost Analysis dashboard, consider downsizing |

---

## Conclusion

This plan provides a complete, production-grade deployment strategy for Todo App Phase V on Oracle Kubernetes Engine. By following these 8 phases, you'll deploy a secure, scalable, observable, and cost-optimized application with:

- **High Availability**: Multi-AZ deployment across 2 Availability Domains
- **Security**: Network policies, RBAC, pod security standards, SSL/TLS
- **Observability**: Prometheus + Grafana monitoring with custom dashboards
- **Automation**: GitHub Actions CI/CD pipeline
- **Cost Efficiency**: $50-150/month leveraging OCI Always Free tier
- **Operational Excellence**: Comprehensive runbook and disaster recovery procedures

**Timeline**: 4-6 weeks from start to production go-live.

**Next Steps**: Begin with Phase 0 (Prerequisites) and proceed sequentially through all phases.
