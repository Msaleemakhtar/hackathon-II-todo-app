#!/bin/bash
# Dapr Setup Script - Initialize Dapr on Kubernetes cluster

set -e

echo "========================================="
echo "Dapr Cluster Setup"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Dapr CLI is installed
if ! command -v dapr &> /dev/null; then
  echo -e "${RED}❌ Dapr CLI not found${NC}"
  echo "Install with: curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash"
  exit 1
fi

DAPR_VERSION=$(dapr version --client-only 2>/dev/null | grep "CLI version" | awk '{print $NF}')
echo -e "${GREEN}✅ Dapr CLI installed: $DAPR_VERSION${NC}"
echo ""

# Check kubectl access
if ! kubectl cluster-info &> /dev/null; then
  echo -e "${RED}❌ Cannot connect to Kubernetes cluster${NC}"
  echo "Verify kubectl is configured correctly"
  exit 1
fi

echo -e "${GREEN}✅ Kubernetes cluster accessible${NC}"
kubectl cluster-info | head -1
echo ""

# Check if Dapr is already installed
echo "Checking Dapr installation status..."
if kubectl get namespace dapr-system &> /dev/null; then
  echo -e "${YELLOW}⚠️  Dapr already installed${NC}"
  echo ""
  echo "Dapr system pods:"
  kubectl get pods -n dapr-system
  echo ""

  read -p "Reinstall Dapr? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Skipping Dapr installation"
    exit 0
  fi

  echo "Uninstalling existing Dapr..."
  dapr uninstall -k --all
  sleep 5
fi

# Install Dapr on Kubernetes
echo "Installing Dapr on Kubernetes..."
echo "This will create dapr-system namespace and install:"
echo "  - dapr-operator"
echo "  - dapr-sidecar-injector"
echo "  - dapr-placement-server"
echo "  - dapr-scheduler (for Jobs API)"
echo "  - dapr-sentry (mTLS)"
echo ""

dapr init -k --wait --runtime-version 1.12

# Verify installation
echo ""
echo "Verifying Dapr installation..."
sleep 10

# Check dapr-system namespace
if ! kubectl get namespace dapr-system &> /dev/null; then
  echo -e "${RED}❌ dapr-system namespace not created${NC}"
  exit 1
fi

echo -e "${GREEN}✅ dapr-system namespace created${NC}"

# Check Dapr pods
echo ""
echo "Dapr system pods:"
kubectl get pods -n dapr-system

READY_PODS=$(kubectl get pods -n dapr-system --no-headers | grep "Running" | wc -l)
TOTAL_PODS=$(kubectl get pods -n dapr-system --no-headers | wc -l)

if [ "$READY_PODS" != "$TOTAL_PODS" ]; then
  echo -e "${YELLOW}⚠️  Not all Dapr pods are ready ($READY_PODS/$TOTAL_PODS)${NC}"
  echo "Waiting for pods to become ready..."
  kubectl wait --for=condition=Ready pod --all -n dapr-system --timeout=5m
fi

echo -e "${GREEN}✅ All Dapr system pods ready ($READY_PODS/$TOTAL_PODS)${NC}"
echo ""

# Verify Dapr CRDs
echo "Checking Dapr Custom Resource Definitions..."
EXPECTED_CRDS=("components.dapr.io" "configurations.dapr.io" "subscriptions.dapr.io")

for crd in "${EXPECTED_CRDS[@]}"; do
  if kubectl get crd $crd &> /dev/null; then
    echo -e "${GREEN}✅ CRD found: $crd${NC}"
  else
    echo -e "${RED}❌ CRD missing: $crd${NC}"
    exit 1
  fi
done

echo ""

# Display Dapr version
echo "Dapr Installation Details:"
echo "----------------------------------------"
dapr version --client-only
echo ""

# Create application namespace if not exists
NAMESPACE="todo-phasev"
echo "Checking application namespace: $NAMESPACE"

if ! kubectl get namespace $NAMESPACE &> /dev/null; then
  echo "Creating namespace: $NAMESPACE"
  kubectl create namespace $NAMESPACE
  echo -e "${GREEN}✅ Namespace created${NC}"
else
  echo -e "${GREEN}✅ Namespace already exists${NC}"
fi

echo ""

# Summary
cat << EOF

========================================
Dapr Setup Complete!
========================================

✅ Dapr CLI: $DAPR_VERSION
✅ Dapr Runtime: Installed in dapr-system namespace
✅ CRDs: components, configurations, subscriptions
✅ Application Namespace: $NAMESPACE

Next Steps:
-----------
1. Apply Dapr components:
   kubectl apply -f phaseV/kubernetes/dapr-components/ -n $NAMESPACE

2. Verify components:
   kubectl get components -n $NAMESPACE

3. Deploy application with Dapr sidecars:
   helm upgrade todo-app phaseV/kubernetes/helm/todo-app -n $NAMESPACE

4. Verify sidecar injection:
   kubectl get pods -n $NAMESPACE
   (Should show 2/2 containers per pod)

5. Enable Dapr feature flag:
   kubectl patch configmap todo-app-config -n $NAMESPACE \\
     -p '{"data":{"USE_DAPR":"true"}}'

For detailed migration instructions, see:
  phaseV/docs/DAPR_MIGRATION_RUNBOOK.md

EOF
