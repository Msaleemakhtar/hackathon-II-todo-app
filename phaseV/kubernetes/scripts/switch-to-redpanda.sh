#!/bin/bash
set -e

NAMESPACE="todo-phasev"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Switch from Local Kafka to Redpanda Cloud         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Backup current component
echo "📦 Step 1: Backup current local Kafka component..."
kubectl get component pubsub-kafka -n $NAMESPACE -o yaml > /tmp/pubsub-kafka-local-backup.yaml || echo "No existing component to backup"
echo "   ✅ Backup saved to /tmp/pubsub-kafka-local-backup.yaml"
echo ""

# Step 2: Check Redpanda credentials
echo "🔑 Step 2: Verify Redpanda credentials exist..."
if kubectl get secret kafka-secrets -n $NAMESPACE &>/dev/null; then
    USERNAME=$(kubectl get secret kafka-secrets -n $NAMESPACE -o jsonpath='{.data.username}' | base64 -d)
    echo "   ✅ Credentials found: username=$USERNAME"
else
    echo "   ❌ ERROR: kafka-secrets not found!"
    exit 1
fi
echo ""

# Step 3: Apply Redpanda component
echo "🚀 Step 3: Apply Redpanda component configuration..."
kubectl apply -f $(dirname "$0")/../dapr-components/pubsub-kafka.yaml
echo "   ✅ Redpanda component applied"
echo ""

# Step 4: Wait for component to be processed
echo "⏳ Step 4: Wait for component to propagate (10 seconds)..."
sleep 10
echo "   ✅ Wait complete"
echo ""

# Step 5: Restart services to pick up new component
echo "♻️  Step 5: Restart services to reload Dapr components..."
DEPLOYMENTS=("backend" "email-delivery" "recurring-service")

for deployment in "${DEPLOYMENTS[@]}"; do
    echo "   → Restarting $deployment..."
    kubectl rollout restart deployment/$deployment -n $NAMESPACE
done
echo "   ✅ All deployments restarted"
echo ""

# Step 6: Wait for rollouts to complete
echo "⏳ Step 6: Wait for services to become ready..."
for deployment in "${DEPLOYMENTS[@]}"; do
    echo "   → Waiting for $deployment..."
    kubectl rollout status deployment/$deployment -n $NAMESPACE --timeout=120s
done
echo "   ✅ All services ready"
echo ""

# Step 7: Check Dapr component status
echo "🔍 Step 7: Verify Dapr components loaded..."
BACKEND_POD=$(kubectl get pod -n $NAMESPACE -l app=backend -o jsonpath='{.items[0].metadata.name}')
echo "   → Checking backend pod: $BACKEND_POD"
kubectl logs -n $NAMESPACE $BACKEND_POD -c daprd --tail=50 | grep -i "component loaded" || true
echo ""

# Step 8: Test Dapr health
echo "🏥 Step 8: Test Dapr sidecar health..."
HEALTH=$(kubectl exec -n $NAMESPACE $BACKEND_POD -c backend -- curl -s -o /dev/null -w "%{http_code}" http://localhost:3500/v1.0/healthz || echo "000")
if [ "$HEALTH" = "204" ]; then
    echo "   ✅ Dapr sidecar healthy (HTTP $HEALTH)"
else
    echo "   ⚠️  Dapr health check returned: HTTP $HEALTH"
fi
echo ""

# Step 9: Check for errors
echo "🔍 Step 9: Check for Dapr initialization errors..."
ERROR_LOGS=$(kubectl logs -n $NAMESPACE $BACKEND_POD -c daprd --tail=100 | grep -i "error\|fatal\|failed" || true)
if [ -z "$ERROR_LOGS" ]; then
    echo "   ✅ No errors found in Dapr logs"
else
    echo "   ⚠️  Errors detected:"
    echo "$ERROR_LOGS"
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                      SWITCH COMPLETE                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Current Configuration:"
echo "   Broker: d5k8cf6udu05l9vrkisg.any.ap-south-1.mpx.prd.cloud.redpanda.com:9092"
echo "   Auth: SASL_SSL SCRAM-SHA-256"
echo "   Username: $USERNAME"
echo ""
echo "🧪 Next Steps:"
echo "   1. Test event publishing: kubectl exec -n $NAMESPACE \$BACKEND_POD -c backend -- python3 -c 'import httpx; print(httpx.post(\"http://localhost:3500/v1.0/publish/pubsub-kafka/task-reminders\", json={\"test\": \"event\"}).status_code)'"
echo "   2. Monitor Dapr logs: kubectl logs -n $NAMESPACE $BACKEND_POD -c daprd -f"
echo "   3. Check application logs: kubectl logs -n $NAMESPACE $BACKEND_POD -c backend -f"
echo ""
echo "🔄 To rollback to local Kafka:"
echo "   kubectl apply -f /tmp/pubsub-kafka-local-backup.yaml"
echo "   kubectl rollout restart deployment -n $NAMESPACE backend email-delivery recurring-service"
echo ""
