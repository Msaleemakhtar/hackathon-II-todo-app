#!/bin/bash
# Quick status checker for OKE deployment
# Run this anytime to see current state and next steps

set +e  # Don't exit on errors - we're checking status

echo "========================================="
echo "OKE Deployment Status Checker"
echo "========================================="
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Source environment if available
if [ -f ~/.oke-env ]; then
  source ~/.oke-env
  echo "✅ Environment loaded from ~/.oke-env"
else
  echo "⚠️  No ~/.oke-env found - some checks may fail"
fi

echo ""
echo "========================================="
echo "1. CLUSTER STATUS"
echo "========================================="

if [ -n "$CLUSTER_ID" ]; then
  echo "Cluster OCID: $CLUSTER_ID"
  echo "Region: $REGION"

  # Check cluster state
  CLUSTER_STATE=$(oci ce cluster get --cluster-id "$CLUSTER_ID" --query 'data."lifecycle-state"' --raw-output 2>/dev/null)

  if [ $? -eq 0 ]; then
    if [ "$CLUSTER_STATE" = "ACTIVE" ]; then
      echo "Status: ✅ ACTIVE"
    else
      echo "Status: ⚠️  $CLUSTER_STATE"
    fi
  else
    echo "Status: ❌ Cannot query cluster (check OCI CLI config)"
  fi
else
  echo "Status: ❌ No CLUSTER_ID found in environment"
fi

echo ""
echo "========================================="
echo "2. KUBECTL CONNECTIVITY"
echo "========================================="

if kubectl cluster-info &>/dev/null; then
  echo "kubectl: ✅ Connected"
  kubectl cluster-info | grep "control plane"
else
  echo "kubectl: ❌ Not connected"
  echo ""
  echo "Fix: Run scripts/configure-kubectl.sh"
fi

echo ""
echo "========================================="
echo "3. NODE POOLS"
echo "========================================="

if [ -n "$CLUSTER_ID" ]; then
  NODE_POOLS=$(oci ce node-pool list \
    --cluster-id "$CLUSTER_ID" \
    --compartment-id "$COMPARTMENT_ID" \
    --query 'data[*].{Name:name,State:"lifecycle-state",Nodes:"node-config-details"."size"}' \
    --output table 2>/dev/null)

  if [ $? -eq 0 ] && [ -n "$NODE_POOLS" ]; then
    echo "$NODE_POOLS"
  else
    echo "Status: ❌ No node pools found or cannot query"
  fi
else
  echo "Status: ❌ Cannot check (no CLUSTER_ID)"
fi

echo ""
echo "========================================="
echo "4. WORKER NODES"
echo "========================================="

NODES=$(kubectl get nodes 2>/dev/null)

if [ $? -eq 0 ]; then
  NODE_COUNT=$(echo "$NODES" | grep -c "Ready\|NotReady" || echo "0")

  if [ "$NODE_COUNT" -gt 0 ]; then
    echo "Nodes found: ✅ $NODE_COUNT"
    echo ""
    kubectl get nodes -o wide
  else
    echo "Nodes found: ⚠️  0 (node pool may be creating)"
    echo ""
    echo "Check node pool status:"
    if [ -n "$CLUSTER_ID" ]; then
      oci ce node-pool list --cluster-id "$CLUSTER_ID" --compartment-id "$COMPARTMENT_ID" 2>/dev/null | grep -E "lifecycle-state|name"
    fi
  fi
else
  echo "Nodes found: ❌ Cannot query (kubectl not connected)"
fi

echo ""
echo "========================================="
echo "5. SYSTEM PODS"
echo "========================================="

if kubectl get pods -n kube-system &>/dev/null; then
  TOTAL_PODS=$(kubectl get pods -n kube-system --no-headers 2>/dev/null | wc -l)
  RUNNING_PODS=$(kubectl get pods -n kube-system --no-headers 2>/dev/null | grep -c "Running" || echo "0")

  if [ "$TOTAL_PODS" -gt 0 ]; then
    echo "System pods: $RUNNING_PODS/$TOTAL_PODS Running"

    if [ "$RUNNING_PODS" -eq "$TOTAL_PODS" ]; then
      echo "Status: ✅ All system pods Running"
    else
      echo "Status: ⚠️  Some pods not ready"
      echo ""
      echo "Pods not Running:"
      kubectl get pods -n kube-system 2>/dev/null | grep -v "Running"
    fi
  else
    echo "Status: ⚠️  No system pods (waiting for nodes)"
  fi
else
  echo "Status: ❌ Cannot query (kubectl not connected)"
fi

echo ""
echo "========================================="
echo "6. BACKGROUND RETRY SCRIPT"
echo "========================================="

if [ -f retry-nodepool.pid ]; then
  PID=$(cat retry-nodepool.pid)

  if ps -p "$PID" &>/dev/null; then
    echo "Status: ✅ Running (PID: $PID)"

    if [ -f retry-nodepool.log ]; then
      echo ""
      echo "Last 5 log lines:"
      tail -5 retry-nodepool.log
    fi
  else
    echo "Status: ⚠️  Not running (PID file exists but process dead)"
  fi
else
  echo "Status: ⚠️  Not started"
  echo ""
  echo "To start: nohup bash scripts/retry-arm-nodepool.sh > retry-nodepool.log 2>&1 &"
fi

echo ""
echo "========================================="
echo "7. STORAGE"
echo "========================================="

if kubectl get storageclass &>/dev/null; then
  DEFAULT_SC=$(kubectl get storageclass 2>/dev/null | grep "(default)" | awk '{print $1}')

  if [ -n "$DEFAULT_SC" ]; then
    echo "Default StorageClass: ✅ $DEFAULT_SC"
  else
    echo "Default StorageClass: ⚠️  Not set"
  fi

  kubectl get storageclass 2>/dev/null
else
  echo "Status: ❌ Cannot query (kubectl not connected)"
fi

echo ""
echo "========================================="
echo "8. APPLICATION DEPLOYMENT"
echo "========================================="

if kubectl get namespace todo-phasev &>/dev/null; then
  echo "Namespace: ✅ todo-phasev exists"

  APP_PODS=$(kubectl get pods -n todo-phasev --no-headers 2>/dev/null | wc -l)

  if [ "$APP_PODS" -gt 0 ]; then
    echo "Application pods: ✅ $APP_PODS found"
    echo ""
    kubectl get pods -n todo-phasev 2>/dev/null
  else
    echo "Application pods: ⚠️  0 (not deployed yet)"
  fi
else
  echo "Namespace: ⚠️  todo-phasev not created"
  echo "Application: ⚠️  Not deployed"
fi

echo ""
echo "========================================="
echo "SUMMARY & NEXT STEPS"
echo "========================================="

# Determine current phase
if [ "$NODE_COUNT" -gt 0 ] && [ "$RUNNING_PODS" -gt 0 ]; then
  echo ""
  echo "📊 Current Phase: Infrastructure Ready ✅"
  echo ""
  echo "Next steps:"
  echo "1. Build ARM64 Docker images (if nodes are ARM)"
  echo "2. Push images to Oracle Container Registry (OCIR)"
  echo "3. Install Dapr: dapr init --kubernetes"
  echo "4. Deploy application via Helm"
  echo ""
  echo "See: docs/OKE_DEPLOYMENT_PLAN_FREE_TIER.md - Phase 2"

elif [ "$NODE_COUNT" -gt 0 ]; then
  echo ""
  echo "📊 Current Phase: Nodes joining ⏳"
  echo ""
  echo "Next steps:"
  echo "1. Wait for system pods to be Running (2-3 minutes)"
  echo "2. Run this script again to verify"
  echo ""
  echo "Monitor: kubectl get pods -n kube-system -w"

elif [ "$CLUSTER_STATE" = "ACTIVE" ]; then
  echo ""
  echo "📊 Current Phase: Waiting for nodes ⏳"
  echo ""
  echo "Issue: Node pool creation blocked (ARM capacity shortage)"
  echo ""
  echo "Options:"
  echo "1. Wait for background retry (if running)"
  echo "2. Try single node in different ADs:"
  echo "   bash scripts/try-single-node-all-ads.sh"
  echo "3. Deploy to different region (us-phoenix-1)"
  echo "4. Use x86 free tier or paid instances"
  echo ""
  echo "See: docs/QUICK_ACTION_GUIDE.md"

else
  echo ""
  echo "📊 Current Phase: Initial setup ⚠️"
  echo ""
  echo "Issue: Cluster not ready or not configured"
  echo ""
  echo "Next steps:"
  echo "1. Create OKE cluster via OCI Console"
  echo "2. Run: scripts/configure-kubectl.sh"
  echo ""
  echo "See: docs/OKE_MANUAL_SETUP_GUIDE.md"
fi

echo ""
echo "========================================="
echo "Quick Commands:"
echo "========================================="
echo "Check nodes:         kubectl get nodes"
echo "Check system pods:   kubectl get pods -n kube-system"
echo "Check app pods:      kubectl get pods -n todo-phasev"
echo "View retry log:      tail -f retry-nodepool.log"
echo "Run this again:      bash scripts/check-deployment-status.sh"
echo ""
echo "Full docs:           docs/QUICK_ACTION_GUIDE.md"
echo "========================================="
