#!/bin/bash
set -e

# Source environment variables
source ~/.oke-env

echo "Creating ARM A1.Flex Node Pool (FREE TIER)..."
echo "Configuration: 2 nodes × 2 OCPU × 12GB RAM (ARM64)"
echo "Total: 4 OCPU + 24GB RAM = 100% of Always Free tier"
echo ""

# Get availability domains
AD1=$(oci iam availability-domain list --compartment-id "$COMPARTMENT_ID" --query 'data[0].name' --raw-output)
AD2=$(oci iam availability-domain list --compartment-id "$COMPARTMENT_ID" --query 'data[1].name' --raw-output)

echo "Availability Domain 1: $AD1"
echo "Availability Domain 2: $AD2"
echo ""

# Get Oracle Linux 8 ARM image for Kubernetes (Ampere A1)
echo "Finding Oracle Linux ARM64 image for Kubernetes..."
IMAGE_ID=$(oci compute image list \
  --compartment-id "$COMPARTMENT_ID" \
  --operating-system "Oracle Linux" \
  --shape "VM.Standard.A1.Flex" \
  --sort-by TIMECREATED \
  --sort-order DESC \
  --limit 1 \
  --query 'data[0].id' \
  --raw-output 2>&1)

if [ -z "$IMAGE_ID" ]; then
    echo "❌ Failed to find ARM64 image"
    echo "Trying alternative approach..."
    # Use a known working image OCID for me-dubai-1
    IMAGE_ID="ocid1.image.oc1.me-dubai-1.aaaaaaaaw4qe4tdgwjzrsczqncfixaymfmpdmjxlrq5eodxxhh6j3lngr4hq"
fi

echo "Image ID: $IMAGE_ID"
echo ""

# Create Node Pool
echo "Creating node pool (this takes 10-15 minutes)..."
NODE_POOL_ID=$(oci ce node-pool create \
  --cluster-id "$CLUSTER_ID" \
  --compartment-id "$COMPARTMENT_ID" \
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
  --query 'data.id' \
  --raw-output 2>&1)

if [[ "$NODE_POOL_ID" == ocid1.nodepool.* ]]; then
    echo "✅ Node pool creation started!"
    echo "Node Pool ID: $NODE_POOL_ID"
    echo "export NODE_POOL_ID=$NODE_POOL_ID" >> ~/.oke-env

    echo ""
    echo "Waiting for node pool to become ACTIVE (10-15 minutes)..."
    oci ce node-pool get --node-pool-id "$NODE_POOL_ID" --wait-for-state ACTIVE --max-wait-seconds 1200

    echo ""
    echo "✅ Node pool is ACTIVE!"
    echo "Checking nodes..."
    kubectl get nodes -o wide
else
    echo "❌ Failed to create node pool"
    echo "Response: $NODE_POOL_ID"
    exit 1
fi
