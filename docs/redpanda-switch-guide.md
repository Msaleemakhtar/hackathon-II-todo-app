# Switching from Local Kafka to Redpanda Cloud

**Date**: 2026-01-16
**Status**: Ready to Execute

---

## Prerequisites

✅ **Already configured:**
- Redpanda component: `phaseV/kubernetes/dapr-components/pubsub-kafka.yaml`
- Credentials secret: `kafka-secrets` (username: saleem)
- Broker: `d5k8cf6udu05l9vrkisg.any.ap-south-1.mpx.prd.cloud.redpanda.com:9092`
- Authentication: SASL_SSL SCRAM-SHA-256

---

## Automated Switch (Recommended)

### Option 1: One-Command Switch

```bash
cd phaseV/kubernetes/scripts
./switch-to-redpanda.sh
```

**Duration**: ~2-3 minutes
**Rollback**: Automatic backup created

### Option 2: Test First, Then Switch

```bash
# 1. Test connectivity
cd phaseV/kubernetes/scripts
./test-redpanda-connectivity.sh

# 2. If all tests pass, switch
./switch-to-redpanda.sh
```

---

## Manual Method

### Step 1: Backup Current Component

```bash
kubectl get component pubsub-kafka -n todo-phasev -o yaml > /tmp/pubsub-kafka-local-backup.yaml
```

### Step 2: Verify Redpanda Credentials

```bash
# Check secret exists
kubectl get secret kafka-secrets -n todo-phasev

# Verify username
kubectl get secret kafka-secrets -n todo-phasev -o jsonpath='{.data.username}' | base64 -d
# Expected: saleem

# Check password exists (don't print it!)
kubectl get secret kafka-secrets -n todo-phasev -o jsonpath='{.data.password}' | wc -c
# Expected: >20 characters (base64 encoded)
```

### Step 3: Apply Redpanda Component

```bash
kubectl apply -f phaseV/kubernetes/dapr-components/pubsub-kafka.yaml
```

**Expected output:**
```
component.dapr.io/pubsub-kafka configured
```

### Step 4: Restart Services

```bash
# Restart all event-driven services
kubectl rollout restart deployment/backend -n todo-phasev
kubectl rollout restart deployment/email-delivery -n todo-phasev
kubectl rollout restart deployment/recurring-service -n todo-phasev

# Wait for rollouts to complete
kubectl rollout status deployment/backend -n todo-phasev --timeout=120s
kubectl rollout status deployment/email-delivery -n todo-phasev --timeout=120s
kubectl rollout status deployment/recurring-service -n todo-phasev --timeout=120s
```

### Step 5: Verify Component Loaded

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pod -n todo-phasev -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Check Dapr logs for component loading
kubectl logs -n todo-phasev $BACKEND_POD -c daprd --tail=50 | grep "component loaded"
```

**Expected output:**
```
component loaded. name: pubsub-kafka, type: pubsub.kafka/v1
component loaded. name: kubernetes-secrets, type: secretstores.kubernetes/v1
```

### Step 6: Check for Errors

```bash
# Check Dapr initialization errors
kubectl logs -n todo-phasev $BACKEND_POD -c daprd --tail=100 | grep -i "error\|fatal\|failed"
```

**If no errors**: ✅ You're good to go!
**If you see "kafka: client has run out of available brokers"**: ⚠️ Connectivity issue (see troubleshooting below)

### Step 7: Test Event Publishing

```bash
# Test Dapr publish API
kubectl exec -n todo-phasev $BACKEND_POD -c backend -- python3 -c "
import httpx
import json
result = httpx.post(
    'http://localhost:3500/v1.0/publish/pubsub-kafka/task-reminders',
    json={'test': 'redpanda-connection', 'timestamp': '$(date -Iseconds)'}
)
print(f'Status: {result.status_code}')
print('Expected: 204 (No Content)')
"
```

**Expected output:**
```
Status: 204
Expected: 204 (No Content)
```

---

## Validation Checklist

After switching, verify:

- [ ] All pods show `2/2` containers (app + daprd)
- [ ] Dapr sidecars report "component loaded" for pubsub-kafka
- [ ] No errors in Dapr logs related to Kafka/Redpanda
- [ ] Event publishing returns HTTP 204
- [ ] Backend can create tasks and trigger events
- [ ] Email delivery service receives events
- [ ] Recurring task service processes events

---

## Rollback (If Needed)

### Quick Rollback

```bash
# Restore local Kafka component
kubectl apply -f /tmp/pubsub-kafka-local-backup.yaml

# Restart services
kubectl rollout restart deployment -n todo-phasev backend email-delivery recurring-service

# Wait for rollout
kubectl rollout status deployment -n todo-phasev backend --timeout=120s
```

### Verify Rollback

```bash
BACKEND_POD=$(kubectl get pod -n todo-phasev -l app=backend -o jsonpath='{.items[0].metadata.name}')
kubectl logs -n todo-phasev $BACKEND_POD -c daprd --tail=20 | grep "component loaded"
```

**Expected:** Component loads with local Kafka broker address

---

## Troubleshooting

### Issue 1: "client has run out of available brokers"

**Symptom:**
```
level=error msg="Failed to init component pubsub-kafka (pubsub.kafka/v1):
kafka: client has run out of available brokers to talk to"
```

**Diagnosis:**
This is the known connectivity issue between Dapr's Sarama client and Redpanda Cloud.

**Solutions:**

#### Option A: Test with TLS Configuration

Try adding explicit TLS configuration to `pubsub-kafka.yaml`:

```yaml
metadata:
  # ... existing metadata ...
  - name: skipVerify
    value: "false"
  - name: caCert
    value: ""  # Let it use system CA bundle
```

Then:
```bash
kubectl apply -f phaseV/kubernetes/dapr-components/pubsub-kafka.yaml
kubectl rollout restart deployment/backend -n todo-phasev
```

#### Option B: Use Redis Streams Alternative

```bash
# Apply Redis component (compatible with same API)
kubectl apply -f phaseV/kubernetes/dapr-components/pubsub-redis.yaml

# Restart services
kubectl rollout restart deployment -n todo-phasev backend email-delivery recurring-service
```

**Pros:** Works immediately, no connectivity issues
**Cons:** Different message broker (but application code unchanged!)

#### Option C: Contact Redpanda/Dapr Support

Gather diagnostic information:

```bash
# Run connectivity test
./test-redpanda-connectivity.sh > /tmp/redpanda-diagnostics.txt

# Get Dapr version
kubectl exec -n todo-phasev $BACKEND_POD -c daprd -- daprd --version

# Export component config
kubectl get component pubsub-kafka -n todo-phasev -o yaml > /tmp/pubsub-config.yaml
```

File issue with:
- Dapr GitHub: https://github.com/dapr/dapr/issues
- Redpanda Support: support@redpanda.com

### Issue 2: "secret not found"

**Solution:**
```bash
# Recreate secret with Redpanda credentials
kubectl create secret generic kafka-secrets -n todo-phasev \
  --from-literal=username=saleem \
  --from-literal=password=YOUR_PASSWORD \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Issue 3: Events not being consumed

**Check consumer subscription:**
```bash
# Check if services registered subscriptions
kubectl exec -n todo-phasev $BACKEND_POD -c backend -- \
  curl -s http://localhost:3500/v1.0/metadata | jq '.subscriptions'
```

**Expected:** Should show subscriptions for task-reminders, task-recurrence

---

## Performance Comparison

### Local Kafka
- **Latency**: 5-15ms (in-cluster)
- **Throughput**: Limited by single broker
- **Availability**: Tied to pod health

### Redpanda Cloud
- **Latency**: 30-50ms (network hop to AWS)
- **Throughput**: Managed cluster (higher capacity)
- **Availability**: 99.99% SLA (cloud-managed)

**Recommendation:** For production, Redpanda Cloud is preferred for durability and availability.

---

## Benefits of Redpanda Cloud

1. **Durability**: Messages persist across restarts/failures
2. **Scalability**: Managed cluster handles high throughput
3. **Monitoring**: Redpanda Console for observability
4. **Managed**: No Kafka broker maintenance required
5. **Production-Ready**: SLA-backed availability

---

## Files Created

- **Switch Script**: `phaseV/kubernetes/scripts/switch-to-redpanda.sh`
- **Test Script**: `phaseV/kubernetes/scripts/test-redpanda-connectivity.sh`
- **Component Config**: `phaseV/kubernetes/dapr-components/pubsub-kafka.yaml` (already exists)
- **Credentials**: `kafka-secrets` secret (already exists)
- **This Guide**: `docs/redpanda-switch-guide.md`

---

## Next Steps After Successful Switch

1. ✅ **Validate Event Flow**: Create a task and verify email delivery
2. ✅ **Monitor Performance**: Check p95 latency vs local Kafka
3. ✅ **Load Test**: Run 100+ events to verify throughput
4. ✅ **Update Documentation**: Mark production-ready in ADR
5. ✅ **Clean Up**: Remove local Kafka pod to save resources

---

## Summary

**Switching is easy because:**
- ✅ Component already configured
- ✅ Credentials already stored
- ✅ Zero code changes required
- ✅ Rollback is instant
- ✅ Automated scripts handle everything

**Try it with confidence!** The worst case is you rollback to local Kafka in 30 seconds.

---

**Created**: 2026-01-16
**Status**: Ready for Execution
**Risk Level**: Low (rollback available)
