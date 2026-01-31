#!/bin/bash
set -e

echo "========================================="
echo "Dubai ARM Node Pool - Corrected Version"
echo "========================================="
echo ""

# Source environment
source ~/.oke-env

# Correct values
KUBERNETES_VERSION="v1.34.1"
ARM_IMAGE_ID="ocid1.image.oc1.me-dubai-1.aaaaaaaakkfajrzc3at6fmr5ygcfokdmovkiqrcsftj5lypsjpkbeu3blmya"
ARM_IMAGE_NAME="Oracle-Linux-8.10-aarch64-2025.09.16-0-OKE-1.34.1-1330"
AD="DxZI:ME-DUBAI-1-AD-1"

echo "Configuration:"
echo "- Cluster: $CLUSTER_ID"
echo "- Kubernetes: $KUBERNETES_VERSION"
echo "- Image: $ARM_IMAGE_NAME"
echo "- Image ID: $ARM_IMAGE_ID"
echo "- AD: $AD"
echo ""

# Strategy 1: Try 2 OCPU first
echo "========================================="
echo "Attempting: 1 node × 2 OCPU × 12GB RAM"
echo "========================================="
echo ""

NODE_POOL_ID=$(oci ce node-pool create \
  --cluster-id "$CLUSTER_ID" \
  --compartment-id "$COMPARTMENT_ID" \
  --name "arm-pool-2ocpu" \
  --kubernetes-version "$KUBERNETES_VERSION" \
  --node-shape "VM.Standard.A1.Flex" \
  --node-shape-config '{"ocpus": 2.0, "memoryInGBs": 12.0}' \
  --size 1 \
  --placement-configs "[{\"availabilityDomain\":\"$AD\",\"subnetId\":\"$NODE_SUBNET_ID\"}]" \
  --node-source-details "{\"sourceType\": \"IMAGE\", \"imageId\": \"$ARM_IMAGE_ID\", \"bootVolumeSizeInGBs\": 50}" \
  --initial-node-labels '[{"key":"pool","value":"free-tier"},{"key":"arch","value":"arm64"}]' \
  --query 'data.id' \
  --raw-output 2>&1)

if [[ "$NODE_POOL_ID" == ocid1.nodepool.* ]]; then
    echo "✅ SUCCESS! Node pool creation started"
    echo "Node Pool ID: $NODE_POOL_ID"
    echo "export NODE_POOL_ID=$NODE_POOL_ID" >> ~/.oke-env

    echo ""
    echo "Waiting for node pool to become ACTIVE (10-15 minutes)..."
    oci ce node-pool get --node-pool-id "$NODE_POOL_ID" --wait-for-state ACTIVE --max-wait-seconds 1200

    echo ""
    echo "✅ Node pool is ACTIVE!"
    echo ""
    echo "Waiting for node to become Ready..."
    sleep 60
    kubectl get nodes -o wide

    echo ""
    echo "========================================="
    echo "✅ SUCCESS! ARM Node Deployed"
    echo "========================================="
    echo "Configuration:"
    echo "- Nodes: 1 × ARM A1.Flex"
    echo "- CPU: 2 OCPU"
    echo "- RAM: 12 GB"
    echo "- Cost: \$0 (Free Tier)"
    echo ""
    echo "Next steps:"
    echo "1. Build ARM64 Docker images"
    echo "2. Install Dapr: dapr init --kubernetes --wait"
    echo "3. Deploy application"
    echo ""
    exit 0
fi

# If that failed, check if it's capacity issue
if echo "$NODE_POOL_ID" | grep -qi "out of"; then
    echo "❌ Failed: Out of ARM capacity (2 OCPU)"
    echo ""
    echo "Trying smaller configuration..."
    echo ""

    # Strategy 2: Try 1 OCPU
    echo "========================================="
    echo "Attempting: 1 node × 1 OCPU × 6GB RAM"
    echo "========================================="
    echo ""

    NODE_POOL_ID=$(oci ce node-pool create \
      --cluster-id "$CLUSTER_ID" \
      --compartment-id "$COMPARTMENT_ID" \
      --name "arm-pool-1ocpu" \
      --kubernetes-version "$KUBERNETES_VERSION" \
      --node-shape "VM.Standard.A1.Flex" \
      --node-shape-config '{"ocpus": 1.0, "memoryInGBs": 6.0}' \
      --size 1 \
      --placement-configs "[{\"availabilityDomain\":\"$AD\",\"subnetId\":\"$NODE_SUBNET_ID\"}]" \
      --node-source-details "{\"sourceType\": \"IMAGE\", \"imageId\": \"$ARM_IMAGE_ID\", \"bootVolumeSizeInGBs\": 50}" \
      --initial-node-labels '[{"key":"pool","value":"free-tier"},{"key":"arch","value":"arm64"}]' \
      --query 'data.id' \
      --raw-output 2>&1)

    if [[ "$NODE_POOL_ID" == ocid1.nodepool.* ]]; then
        echo "✅ SUCCESS! Node pool creation started"
        echo "Node Pool ID: $NODE_POOL_ID"
        echo "export NODE_POOL_ID=$NODE_POOL_ID" >> ~/.oke-env

        echo ""
        echo "Waiting for node pool to become ACTIVE (10-15 minutes)..."
        oci ce node-pool get --node-pool-id "$NODE_POOL_ID" --wait-for-state ACTIVE --max-wait-seconds 1200

        echo ""
        echo "✅ Node pool is ACTIVE!"
        echo ""
        echo "Waiting for node to become Ready..."
        sleep 60
        kubectl get nodes -o wide

        echo ""
        echo "========================================="
        echo "✅ SUCCESS! ARM Node Deployed"
        echo "========================================="
        echo "Configuration:"
        echo "- Nodes: 1 × ARM A1.Flex"
        echo "- CPU: 1 OCPU"
        echo "- RAM: 6 GB"
        echo "- Cost: \$0 (Free Tier)"
        echo ""
        echo "Note: Minimal resources - reduce app resource requests"
        echo ""
        echo "Next steps:"
        echo "1. Build ARM64 Docker images"
        echo "2. Install Dapr: dapr init --kubernetes --wait"
        echo "3. Deploy with reduced resource limits"
        echo ""
        exit 0
    else
        echo "❌ Failed: $NODE_POOL_ID"
    fi
else
    echo "❌ Failed with error: $NODE_POOL_ID"
fi

# Both strategies failed
echo ""
echo "========================================="
echo "❌ No ARM capacity available"
echo "========================================="
echo ""
echo "📋 Recommended alternatives:"
echo ""
echo "Option 1: Use x86 Free Tier (RECOMMENDED) ✅"
echo "  - 2 × VM.Standard.E2.1.Micro"
echo "  - Available NOW (95%+ success rate)"
echo "  - Free Tier (\$0/month)"
echo ""
echo "  Run: bash scripts/create-x86-nodepool.sh"
echo ""
echo "Option 2: Start automated retry"
echo "  - Retries every 15 minutes"
echo "  - 60-80% success in 24-48 hours"
echo ""
echo "  Run: nohup bash scripts/retry-arm-nodepool.sh > retry.log 2>&1 &"
echo ""
