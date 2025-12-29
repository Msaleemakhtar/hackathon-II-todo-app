#!/usr/bin/env bash
# Test Redis Data Persistence for Todo App Phase IV
# Validates PersistentVolumeClaim data retention across pod restarts

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-todo-phaseiv}"
REDIS_POD="redis-0"
TEST_KEY="persistence-test-key"
TEST_VALUE="persistence-test-value-$(date +%s)"
RESTART_TIMEOUT=60

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Pre-flight checks
preflight_checks() {
    log_info "Running pre-flight checks..."

    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found"
        exit 1
    fi

    # Check if Redis pod exists
    if ! kubectl get pod "$REDIS_POD" -n "$NAMESPACE" &> /dev/null; then
        log_error "Redis pod $REDIS_POD not found in namespace $NAMESPACE"
        exit 1
    fi

    # Check if Redis pod is running
    local pod_status=$(kubectl get pod "$REDIS_POD" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
    if [ "$pod_status" != "Running" ]; then
        log_error "Redis pod is not running (current status: $pod_status)"
        exit 1
    fi

    # Check if PVC exists
    if ! kubectl get pvc -n "$NAMESPACE" | grep -q "redis"; then
        log_error "No Redis PVC found in namespace $NAMESPACE"
        exit 1
    fi

    log_success "Pre-flight checks passed"
}

# Display PVC status
display_pvc_status() {
    echo ""
    log_info "PVC Status:"
    kubectl get pvc -n "$NAMESPACE" | grep -E "NAME|redis"
    echo ""

    log_info "PV Status:"
    local pvc_name=$(kubectl get pvc -n "$NAMESPACE" -l app=redis -o jsonpath='{.items[0].metadata.name}')
    if [ -n "$pvc_name" ]; then
        local pv_name=$(kubectl get pvc "$pvc_name" -n "$NAMESPACE" -o jsonpath='{.spec.volumeName}')
        if [ -n "$pv_name" ]; then
            kubectl get pv "$pv_name"
        fi
    fi
    echo ""
}

# Write test data to Redis
write_test_data() {
    log_info "Writing test data to Redis..."
    log_info "Key: $TEST_KEY"
    log_info "Value: $TEST_VALUE"

    if kubectl exec "$REDIS_POD" -n "$NAMESPACE" -- redis-cli SET "$TEST_KEY" "$TEST_VALUE" &> /dev/null; then
        log_success "Test data written successfully"
        return 0
    else
        log_error "Failed to write test data to Redis"
        return 1
    fi
}

# Read test data from Redis
read_test_data() {
    log_info "Reading test data from Redis..."

    local value=$(kubectl exec "$REDIS_POD" -n "$NAMESPACE" -- redis-cli GET "$TEST_KEY" 2>/dev/null || echo "")

    if [ -z "$value" ]; then
        log_error "No value found for key $TEST_KEY"
        return 1
    elif [ "$value" = "$TEST_VALUE" ]; then
        log_success "Test data read successfully: $value"
        return 0
    else
        log_error "Unexpected value: $value (expected: $TEST_VALUE)"
        return 1
    fi
}

# Delete Redis pod
delete_redis_pod() {
    log_info "Deleting Redis pod to simulate failure..."

    if kubectl delete pod "$REDIS_POD" -n "$NAMESPACE" --grace-period=0 --force &> /dev/null; then
        log_success "Redis pod deleted"
        return 0
    else
        log_error "Failed to delete Redis pod"
        return 1
    fi
}

# Wait for Redis pod to restart
wait_for_redis_restart() {
    log_info "Waiting for Redis pod to restart (timeout: ${RESTART_TIMEOUT}s)..."

    local elapsed=0
    while [ $elapsed -lt $RESTART_TIMEOUT ]; do
        sleep 5
        elapsed=$((elapsed + 5))

        # Check if pod exists
        if kubectl get pod "$REDIS_POD" -n "$NAMESPACE" &> /dev/null; then
            local pod_status=$(kubectl get pod "$REDIS_POD" -n "$NAMESPACE" -o jsonpath='{.status.phase}')

            if [ "$pod_status" = "Running" ]; then
                # Check if pod is ready
                local ready=$(kubectl get pod "$REDIS_POD" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
                if [ "$ready" = "True" ]; then
                    log_success "Redis pod restarted and ready (${elapsed}s)"
                    return 0
                fi
            fi

            log_info "[$elapsed/${RESTART_TIMEOUT}s] Pod status: $pod_status"
        else
            log_info "[$elapsed/${RESTART_TIMEOUT}s] Waiting for pod to be created..."
        fi
    done

    log_error "Timeout waiting for Redis pod to restart"
    return 1
}

# Verify data persistence
verify_persistence() {
    log_info "Verifying data persistence after pod restart..."

    # Give Redis a moment to fully initialize
    log_info "Waiting 5 seconds for Redis to fully initialize..."
    sleep 5

    if read_test_data; then
        log_success "Data persisted successfully across pod restart!"
        return 0
    else
        log_error "Data was NOT persisted across pod restart"
        return 1
    fi
}

# Clean up test data
cleanup_test_data() {
    log_info "Cleaning up test data..."

    if kubectl exec "$REDIS_POD" -n "$NAMESPACE" -- redis-cli DEL "$TEST_KEY" &> /dev/null; then
        log_success "Test data cleaned up"
    else
        log_warn "Failed to clean up test data (may not exist)"
    fi
}

# Display Redis info
display_redis_info() {
    echo ""
    log_info "Redis Information:"
    kubectl exec "$REDIS_POD" -n "$NAMESPACE" -- redis-cli INFO persistence 2>/dev/null | grep -E "rdb_|aof_" | head -5 || log_warn "Unable to get Redis persistence info"
    echo ""
}

# Main execution
main() {
    log_info "Starting Redis persistence test..."
    echo ""

    preflight_checks
    echo ""

    # Display initial PVC status
    display_pvc_status

    local test_failures=0

    # Step 1: Write test data
    if ! write_test_data; then
        test_failures=$((test_failures + 1))
        log_error "=== Persistence test failed at write stage ==="
        exit 1
    fi
    echo ""

    # Step 2: Verify data can be read
    if ! read_test_data; then
        test_failures=$((test_failures + 1))
        log_error "=== Persistence test failed at initial read stage ==="
        cleanup_test_data
        exit 1
    fi
    echo ""

    # Display Redis persistence configuration
    display_redis_info

    # Step 3: Delete Redis pod
    if ! delete_redis_pod; then
        test_failures=$((test_failures + 1))
        log_error "=== Persistence test failed at delete stage ==="
        exit 1
    fi
    echo ""

    # Step 4: Wait for pod to restart
    if ! wait_for_redis_restart; then
        test_failures=$((test_failures + 1))
        log_error "=== Persistence test failed at restart stage ==="
        display_pvc_status
        exit 1
    fi
    echo ""

    # Step 5: Verify data persistence
    if ! verify_persistence; then
        test_failures=$((test_failures + 1))
    fi
    echo ""

    # Display final PVC status
    display_pvc_status

    # Clean up test data
    cleanup_test_data
    echo ""

    # Summary
    if [ $test_failures -eq 0 ]; then
        log_success "=== Persistence test passed! ==="
        log_success "Redis data successfully persisted across pod deletion and restart"
        return 0
    else
        log_error "=== Persistence test failed ==="
        log_error "Troubleshooting steps:"
        echo "  1. Check PVC status: kubectl get pvc -n $NAMESPACE"
        echo "  2. Check PV status: kubectl get pv"
        echo "  3. Check Redis pod logs: kubectl logs $REDIS_POD -n $NAMESPACE"
        echo "  4. Check Redis persistence config: kubectl exec $REDIS_POD -n $NAMESPACE -- redis-cli CONFIG GET save"
        echo "  5. Check volume mount: kubectl describe pod $REDIS_POD -n $NAMESPACE | grep -A 5 Mounts"
        return 1
    fi
}

# Run main function
main "$@"
