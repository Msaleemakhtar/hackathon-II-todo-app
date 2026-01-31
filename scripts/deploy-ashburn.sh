#!/bin/bash
# Phase V Deployment Script - Oracle Cloud (us-ashburn-1)
# Complete OKE cluster creation and application deployment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
REGION="us-ashburn-1"
CLUSTER_NAME="todo-phasev-oke"
VCN_NAME="todo-phasev-vcn"
NAMESPACE="todo-phasev"
PROJECT_ROOT="/home/salim/Desktop/hackathon-II-todo-app"

# Environment file
ENV_FILE="$HOME/.oke-ashburn-env"

log_info "========================================="
log_info "Phase V Deployment - Oracle Cloud"
log_info "Region: us-ashburn-1"
log_info "========================================="
echo ""

# Step 1: Get OCI information
log_info "Step 1: Gathering OCI account information..."

TENANCY_ID=$(oci iam compartment list --all --compartment-id-in-subtree true --query 'data[0]."compartment-id"' --raw-output 2>/dev/null || echo "")
if [ -z "$TENANCY_ID" ]; then
    log_error "Failed to get tenancy ID. Is OCI CLI configured?"
    log_info "Run: oci setup config"
    exit 1
fi

COMPARTMENT_ID=$(oci iam compartment list --compartment-id "$TENANCY_ID" --query 'data[0].id' --raw-output 2>/dev/null || echo "$TENANCY_ID")

log_success "Tenancy ID: $TENANCY_ID"
log_success "Compartment ID: $COMPARTMENT_ID"
log_success "Region: $REGION"
echo ""

# Save environment variables
cat > "$ENV_FILE" << EOF
# OCI Environment Configuration - us-ashburn-1
export TENANCY_ID="$TENANCY_ID"
export COMPARTMENT_ID="$COMPARTMENT_ID"
export REGION="$REGION"
export CLUSTER_NAME="$CLUSTER_NAME"
export VCN_NAME="$VCN_NAME"
export NAMESPACE="$NAMESPACE"
EOF

log_success "Environment saved to: $ENV_FILE"
source "$ENV_FILE"
echo ""

# Step 2: Check for existing VCN
log_info "Step 2: Checking for existing VCN..."

EXISTING_VCN=$(oci network vcn list --compartment-id "$COMPARTMENT_ID" --query "data[?\"display-name\"=='$VCN_NAME'].id | [0]" --raw-output 2>/dev/null || echo "null")

if [ "$EXISTING_VCN" != "null" ] && [ -n "$EXISTING_VCN" ]; then
    log_warning "VCN '$VCN_NAME' already exists: $EXISTING_VCN"
    VCN_ID="$EXISTING_VCN"
else
    log_info "Creating VCN '$VCN_NAME'..."
    VCN_ID=$(oci network vcn create \
        --compartment-id "$COMPARTMENT_ID" \
        --cidr-block "10.0.0.0/16" \
        --display-name "$VCN_NAME" \
        --dns-label "todophasev" \
        --wait-for-state AVAILABLE \
        --query 'data.id' \
        --raw-output)
    log_success "VCN created: $VCN_ID"
fi

echo "export VCN_ID=\"$VCN_ID\"" >> "$ENV_FILE"
echo ""

# Step 3: Check for existing cluster
log_info "Step 3: Checking for existing OKE cluster..."

EXISTING_CLUSTER=$(oci ce cluster list --compartment-id "$COMPARTMENT_ID" --query "data[?name=='$CLUSTER_NAME'].id | [0]" --raw-output 2>/dev/null || echo "null")

if [ "$EXISTING_CLUSTER" != "null" ] && [ -n "$EXISTING_CLUSTER" ]; then
    log_warning "Cluster '$CLUSTER_NAME' already exists: $EXISTING_CLUSTER"
    CLUSTER_ID="$EXISTING_CLUSTER"

    # Check cluster state
    CLUSTER_STATE=$(oci ce cluster get --cluster-id "$CLUSTER_ID" --query 'data."lifecycle-state"' --raw-output)
    log_info "Cluster state: $CLUSTER_STATE"

    if [ "$CLUSTER_STATE" != "ACTIVE" ]; then
        log_warning "Cluster is not ACTIVE. Waiting..."
        oci ce cluster get --cluster-id "$CLUSTER_ID" --wait-for-state ACTIVE --max-wait-seconds 1800
    fi
else
    log_info "Creating OKE cluster via OCI Console is recommended for better control"
    log_info "Please create cluster manually or continue with automated creation"
    echo ""
    read -p "Create cluster automatically? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Creating OKE cluster '$CLUSTER_NAME'..."
        log_info "This will take 10-15 minutes..."

        CLUSTER_ID=$(oci ce cluster create-kubeconfig \
            --compartment-id "$COMPARTMENT_ID" \
            --name "$CLUSTER_NAME" \
            --vcn-id "$VCN_ID" \
            --kubernetes-version "v1.28.2" \
            --wait-for-state ACTIVE \
            --query 'data.id' \
            --raw-output 2>&1 | tee /tmp/cluster-create.log | grep -o 'ocid1.cluster[^"]*' | head -1)

        log_success "Cluster created: $CLUSTER_ID"
    else
        log_info "Please create the cluster manually in OCI Console:"
        log_info "1. Go to: https://cloud.oracle.com/containers/clusters"
        log_info "2. Click 'Create Cluster' → 'Quick Create'"
        log_info "3. Name: $CLUSTER_NAME"
        log_info "4. VCN: $VCN_NAME"
        log_info "5. Shape: VM.Standard.A1.Flex (ARM, 2 OCPU × 12GB × 2 nodes)"
        echo ""
        read -p "Enter Cluster OCID when ready: " CLUSTER_ID
    fi
fi

echo "export CLUSTER_ID=\"$CLUSTER_ID\"" >> "$ENV_FILE"
log_success "Cluster ID: $CLUSTER_ID"
echo ""

# Step 4: Configure kubectl
log_info "Step 4: Configuring kubectl..."

mkdir -p ~/.kube
oci ce cluster create-kubeconfig \
    --cluster-id "$CLUSTER_ID" \
    --file ~/.kube/config \
    --region "$REGION" \
    --token-version 2.0.0 \
    --kube-endpoint PUBLIC_ENDPOINT

log_success "kubectl configured"

# Verify connection
log_info "Verifying cluster connection..."
if kubectl cluster-info &> /dev/null; then
    log_success "kubectl connected to cluster"
    kubectl get nodes
else
    log_error "Failed to connect to cluster"
    exit 1
fi
echo ""

# Step 5: Check nodes
log_info "Step 5: Checking node status..."

NODE_COUNT=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
if [ "$NODE_COUNT" -eq 0 ]; then
    log_warning "No nodes found. You may need to create a node pool."
    log_info "Create node pool in OCI Console or use scripts/create-arm-nodes.sh"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    log_success "Found $NODE_COUNT node(s)"

    # Wait for nodes to be Ready
    log_info "Waiting for nodes to be Ready..."
    kubectl wait --for=condition=Ready nodes --all --timeout=600s || log_warning "Some nodes may not be ready yet"
fi
echo ""

# Step 6: Install Dapr
log_info "Step 6: Installing Dapr..."

if dapr status -k &> /dev/null; then
    log_warning "Dapr already installed"
else
    log_info "Installing Dapr on Kubernetes..."
    dapr init --kubernetes --wait
    log_success "Dapr installed"
fi

dapr status -k
echo ""

# Step 7: Create namespace
log_info "Step 7: Creating namespace '$NAMESPACE'..."

if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    log_warning "Namespace '$NAMESPACE' already exists"
else
    kubectl create namespace "$NAMESPACE"
    log_success "Namespace created"
fi

kubectl config set-context --current --namespace="$NAMESPACE"
echo ""

# Step 8: Create storage class
log_info "Step 8: Creating OCI Block Volume storage class..."

kubectl apply -f - << 'EOF'
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

log_success "Storage class created"
echo ""

# Step 9: Deploy Dapr components
log_info "Step 9: Deploying Dapr components..."

cd "$PROJECT_ROOT/phaseV/kubernetes/dapr-components"

kubectl apply -f dapr-config.yaml
kubectl apply -f pubsub-redis.yaml
kubectl apply -f statestore-postgres.yaml
kubectl apply -f secrets-kubernetes.yaml

log_success "Dapr components deployed"
kubectl get components -n "$NAMESPACE"
echo ""

# Step 10: Prepare secrets
log_info "Step 10: Preparing application secrets..."

log_warning "Please ensure secrets are configured in:"
log_warning "  phaseV/kubernetes/helm/todo-app/values-local.yaml"
echo ""
read -p "Are secrets configured? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Please configure secrets and run the deployment manually:"
    log_info "  cd $PROJECT_ROOT/phaseV/kubernetes/helm/todo-app"
    log_info "  helm install todo-app . -f values.yaml -f values-local.yaml -f values-minimal.yaml --namespace $NAMESPACE"
    exit 0
fi
echo ""

# Step 11: Deploy application
log_info "Step 11: Deploying application via Helm..."

cd "$PROJECT_ROOT/phaseV/kubernetes/helm/todo-app"

if helm list -n "$NAMESPACE" | grep -q "todo-app"; then
    log_warning "Application already deployed. Upgrading..."
    helm upgrade todo-app . \
        -f values.yaml \
        -f values-local.yaml \
        -f values-minimal.yaml \
        --namespace "$NAMESPACE"
else
    helm install todo-app . \
        -f values.yaml \
        -f values-local.yaml \
        -f values-minimal.yaml \
        --namespace "$NAMESPACE" \
        --create-namespace
fi

log_success "Application deployed"
echo ""

# Step 12: Install NGINX Ingress
log_info "Step 12: Installing NGINX Ingress Controller..."

if helm list -n ingress-nginx | grep -q "ingress-nginx"; then
    log_warning "NGINX Ingress already installed"
else
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update

    helm install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer

    log_success "NGINX Ingress installed"
fi
echo ""

# Step 13: Wait for pods
log_info "Step 13: Waiting for pods to be ready..."

kubectl get pods -n "$NAMESPACE"
echo ""

log_info "Waiting for all pods to be Running (this may take 2-3 minutes)..."
kubectl wait --for=condition=Ready pod --all -n "$NAMESPACE" --timeout=600s || log_warning "Some pods may not be ready yet"
echo ""

# Step 14: Get ingress IP
log_info "Step 14: Getting Load Balancer IP..."

log_info "Waiting for Load Balancer to provision (this may take 2-3 minutes)..."
sleep 30

EXTERNAL_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")

if [ -z "$EXTERNAL_IP" ]; then
    log_warning "Load Balancer IP not yet available. Check with:"
    log_info "  kubectl get svc -n ingress-nginx ingress-nginx-controller"
else
    log_success "Load Balancer IP: $EXTERNAL_IP"
    echo "export EXTERNAL_IP=\"$EXTERNAL_IP\"" >> "$ENV_FILE"

    log_info "Add to /etc/hosts or configure DNS:"
    log_info "  $EXTERNAL_IP todo-app.local"
fi
echo ""

# Summary
log_success "========================================="
log_success "DEPLOYMENT COMPLETE!"
log_success "========================================="
echo ""
log_info "Summary:"
log_info "  Region: $REGION"
log_info "  Cluster: $CLUSTER_NAME ($CLUSTER_ID)"
log_info "  Namespace: $NAMESPACE"
log_info "  Environment: $ENV_FILE"
echo ""
log_info "Next steps:"
log_info "  1. Configure DNS: $EXTERNAL_IP → todo-app.local"
log_info "  2. Test: curl -k https://todo-app.local/api/health"
log_info "  3. Monitor: kubectl get pods -n $NAMESPACE"
log_info "  4. Logs: kubectl logs -l app=backend -n $NAMESPACE --tail=50"
echo ""
log_success "Access your app at: https://todo-app.local"
