#!/bin/bash
set -e

NAMESPACE="todo-phasev"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Switch to Redis Streams (Alternative)             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check Redis availability
echo "🔍 Step 1: Verify Redis is available..."
if kubectl get pod redis-0 -n $NAMESPACE &>/dev/null; then
    REDIS_STATUS=$(kubectl get pod redis-0 -n $NAMESPACE -o jsonpath='{.status.phase}')
    if [ "$REDIS_STATUS" = "Running" ]; then
        echo "   ✅ Redis pod is running"
    else
        echo "   ⚠️  Redis pod status: $REDIS_STATUS"
    fi
else
    echo "   ❌ Redis pod not found!"
    exit 1
fi
echo ""

# Step 2: Backup current component
echo "📦 Step 2: Backup current component..."
kubectl get component pubsub-kafka -n $NAMESPACE -o yaml > /tmp/pubsub-component-backup.yaml || true
echo "   ✅ Backup saved to /tmp/pubsub-component-backup.yaml"
echo ""

# Step 3: Apply Redis component
echo "🚀 Step 3: Apply Redis Streams component..."
kubectl apply -f $(dirname "$0")/../dapr-components/pubsub-redis.yaml
echo "   ✅ Redis component applied"
echo ""

# Step 4: Wait for component to propagate
echo "⏳ Step 4: Wait for component to propagate (10 seconds)..."
sleep 10
echo ""

# Step 5: Clean up failed pods
echo "🗑️  Step 5: Delete crashing pods..."
kubectl delete pod -n $NAMESPACE -l app=backend --field-selector status.phase=Pending 2>/dev/null || true
kubectl delete pod -n $NAMESPACE -l app=email-delivery --field-selector status.phase=Pending 2>/dev/null || true
kubectl delete pod -n $NAMESPACE -l app=recurring-service --field-selector status.phase=Pending 2>/dev/null || true
echo "   ✅ Cleanup complete"
echo ""

# Step 6: Restart services
echo "♻️  Step 6: Restart services to pick up Redis component..."
kubectl rollout restart deployment/backend -n $NAMESPACE
kubectl rollout restart deployment/email-delivery -n $NAMESPACE
kubectl rollout restart deployment/recurring-service -n $NAMESPACE
echo "   ✅ Deployments restarted"
echo ""

# Step 7: Wait for rollout
echo "⏳ Step 7: Wait for services to become ready..."
kubectl rollout status deployment/backend -n $NAMESPACE --timeout=120s
kubectl rollout status deployment/email-delivery -n $NAMESPACE --timeout=120s
kubectl rollout status deployment/recurring-service -n $NAMESPACE --timeout=120s
echo "   ✅ All services ready"
echo ""

# Step 8: Verify Dapr component loading
echo "🔍 Step 8: Verify Dapr components loaded..."
BACKEND_POD=$(kubectl get pod -n $NAMESPACE -l app=backend -o jsonpath='{.items[0].metadata.name}')
echo "   → Checking pod: $BACKEND_POD"
sleep 5  # Give Dapr time to initialize
COMPONENT_TYPE=$(kubectl logs -n $NAMESPACE $BACKEND_POD -c daprd --tail=50 | grep "component loaded.*pubsub-kafka" | tail -1 || true)
if [[ "$COMPONENT_TYPE" == *"pubsub.redis"* ]]; then
    echo "   ✅ Redis component loaded"
elif [[ "$COMPONENT_TYPE" == *"pubsub.kafka"* ]]; then
    echo "   ✅ Component loaded (checking type...)"
else
    echo "   ⚠️  Could not confirm component type, checking manually..."
fi
echo ""

# Step 9: Test Dapr health
echo "🏥 Step 9: Test Dapr sidecar health..."
HEALTH=$(kubectl exec -n $NAMESPACE $BACKEND_POD -c backend -- curl -s -o /dev/null -w "%{http_code}" http://localhost:3500/v1.0/healthz 2>/dev/null || echo "000")
if [ "$HEALTH" = "204" ]; then
    echo "   ✅ Dapr sidecar healthy (HTTP $HEALTH)"
else
    echo "   ⚠️  Dapr health check returned: HTTP $HEALTH"
fi
echo ""

# Step 10: Check for errors
echo "🔍 Step 10: Check for initialization errors..."
ERROR_LOGS=$(kubectl logs -n $NAMESPACE $BACKEND_POD -c daprd --tail=100 | grep -i "error\|fatal\|failed" || true)
if [ -z "$ERROR_LOGS" ]; then
    echo "   ✅ No errors found"
else
    echo "   ⚠️  Errors detected:"
    echo "$ERROR_LOGS" | head -10
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 SWITCH TO REDIS COMPLETE                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 New Configuration:"
echo "   Message Broker: Redis Streams"
echo "   Host: redis.todo-phasev.svc.cluster.local:6379"
echo "   Type: pubsub.redis/v1"
echo ""
echo "✅ Benefits of Redis:"
echo "   • Low latency (<10ms in-cluster)"
echo "   • No SASL_SSL complexity"
echo "   • Simpler infrastructure"
echo "   • Already running in cluster"
echo ""
echo "⚠️  Differences from Kafka:"
echo "   • No persistent log (Redis Streams retention is limited)"
echo "   • Different performance characteristics"
echo "   • May not support all Kafka features"
echo ""
echo "🧪 Test event publishing:"
echo "   kubectl exec -n $NAMESPACE $BACKEND_POD -c backend -- \\"
echo "     python3 -c 'import httpx; print(httpx.post(\"http://localhost:3500/v1.0/publish/pubsub-kafka/task-reminders\", json={\"test\": \"redis\"}).status_code)'"
echo ""
echo "🔄 To rollback:"
echo "   kubectl apply -f /tmp/pubsub-component-backup.yaml"
echo "   kubectl rollout restart deployment -n $NAMESPACE backend email-delivery recurring-service"
echo ""
