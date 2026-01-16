#!/bin/bash
set -e

NAMESPACE="todo-phasev"
BROKER="d5k8cf6udu05l9vrkisg.any.ap-south-1.mpx.prd.cloud.redpanda.com:9092"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Redpanda Cloud Connectivity Test                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get backend pod
BACKEND_POD=$(kubectl get pod -n $NAMESPACE -l app=backend -o jsonpath='{.items[0].metadata.name}')
echo "📦 Using pod: $BACKEND_POD"
echo ""

# Test 1: DNS Resolution
echo "🔍 Test 1: DNS Resolution"
DNS_IP=$(kubectl exec -n $NAMESPACE $BACKEND_POD -c backend -- nslookup d5k8cf6udu05l9vrkisg.any.ap-south-1.mpx.prd.cloud.redpanda.com 2>/dev/null | grep -A 1 "Name:" | grep "Address:" | awk '{print $2}' || echo "FAILED")
if [ "$DNS_IP" != "FAILED" ]; then
    echo "   ✅ DNS resolves to: $DNS_IP"
else
    echo "   ❌ DNS resolution failed"
    exit 1
fi
echo ""

# Test 2: Network Connectivity (TCP)
echo "🌐 Test 2: TCP Connectivity to port 9092"
TCP_TEST=$(kubectl exec -n $NAMESPACE $BACKEND_POD -c backend -- timeout 5 bash -c "cat < /dev/null > /dev/tcp/d5k8cf6udu05l9vrkisg.any.ap-south-1.mpx.prd.cloud.redpanda.com/9092" 2>&1 && echo "SUCCESS" || echo "FAILED")
if [ "$TCP_TEST" = "SUCCESS" ]; then
    echo "   ✅ TCP connection to port 9092 successful"
else
    echo "   ❌ TCP connection failed"
    echo "   Error: $TCP_TEST"
fi
echo ""

# Test 3: Check Redpanda credentials
echo "🔑 Test 3: Verify Credentials"
if kubectl get secret kafka-secrets -n $NAMESPACE &>/dev/null; then
    USERNAME=$(kubectl get secret kafka-secrets -n $NAMESPACE -o jsonpath='{.data.username}' | base64 -d)
    PASSWORD=$(kubectl get secret kafka-secrets -n $NAMESPACE -o jsonpath='{.data.password}' | base64 -d)
    echo "   ✅ Username: $USERNAME"
    echo "   ✅ Password: ${PASSWORD:0:5}...${PASSWORD: -5} (masked)"
else
    echo "   ❌ kafka-secrets not found"
    exit 1
fi
echo ""

# Test 4: Application-level connection test (aiokafka)
echo "🐍 Test 4: Application Connection (aiokafka)"
cat <<'EOF' > /tmp/test_kafka_connection.py
import asyncio
from aiokafka import AIOKafkaProducer
import sys

async def test_connection():
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers='d5k8cf6udu05l9vrkisg.any.ap-south-1.mpx.prd.cloud.redpanda.com:9092',
            security_protocol='SASL_SSL',
            sasl_mechanism='SCRAM-SHA-256',
            sasl_plain_username='USERNAME_PLACEHOLDER',
            sasl_plain_password='PASSWORD_PLACEHOLDER'
        )
        await producer.start()
        print("✅ aiokafka connection successful")
        await producer.stop()
        return 0
    except Exception as e:
        print(f"❌ aiokafka connection failed: {e}")
        return 1

sys.exit(asyncio.run(test_connection()))
EOF

# Replace placeholders
sed -i "s/USERNAME_PLACEHOLDER/$USERNAME/g" /tmp/test_kafka_connection.py
sed -i "s/PASSWORD_PLACEHOLDER/$PASSWORD/g" /tmp/test_kafka_connection.py

kubectl cp /tmp/test_kafka_connection.py $NAMESPACE/$BACKEND_POD:/tmp/test_kafka_connection.py -c backend
AIOKAFKA_RESULT=$(kubectl exec -n $NAMESPACE $BACKEND_POD -c backend -- python3 /tmp/test_kafka_connection.py 2>&1)
echo "   $AIOKAFKA_RESULT"
echo ""

# Test 5: Check Dapr component status
echo "🚀 Test 5: Dapr Component Status"
COMPONENT_STATUS=$(kubectl get component pubsub-kafka -n $NAMESPACE -o jsonpath='{.spec.type}' 2>/dev/null || echo "NOT_FOUND")
if [ "$COMPONENT_STATUS" = "pubsub.kafka" ]; then
    echo "   ✅ pubsub-kafka component exists"
    BROKER_CONFIG=$(kubectl get component pubsub-kafka -n $NAMESPACE -o jsonpath='{.spec.metadata[?(@.name=="brokers")].value}')
    echo "   📡 Configured broker: $BROKER_CONFIG"
else
    echo "   ⚠️  pubsub-kafka component not found"
fi
echo ""

# Test 6: Check Dapr logs for component initialization
echo "📋 Test 6: Dapr Component Initialization Logs"
COMPONENT_LOGS=$(kubectl logs -n $NAMESPACE $BACKEND_POD -c daprd --tail=200 | grep -i "pubsub-kafka\|component loaded\|kafka" | tail -10 || echo "No logs found")
echo "$COMPONENT_LOGS"
echo ""

# Test 7: Check for Dapr errors
echo "❌ Test 7: Check for Dapr Errors"
ERROR_LOGS=$(kubectl logs -n $NAMESPACE $BACKEND_POD -c daprd --tail=100 | grep -i "error\|fatal\|failed" || echo "No errors found")
if [ "$ERROR_LOGS" = "No errors found" ]; then
    echo "   ✅ No errors in Dapr logs"
else
    echo "   ⚠️  Errors detected:"
    echo "$ERROR_LOGS" | head -20
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    TEST SUMMARY                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Broker: $BROKER"
echo "Username: $USERNAME"
echo ""
echo "If all tests pass but Dapr still fails, try:"
echo "  1. Check Dapr version: kubectl exec -n $NAMESPACE $BACKEND_POD -c daprd -- daprd --version"
echo "  2. Check Sarama client logs (Dapr's Kafka client library)"
echo "  3. Compare with working aiokafka configuration"
echo "  4. Contact Dapr support with logs"
echo ""
