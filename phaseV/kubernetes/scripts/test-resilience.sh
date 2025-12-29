#!/usr/bin/env bash
# Test Pod Resilience for Todo App Phase IV
# Validates Kubernetes self-healing by deleting pods and verifying automatic restart

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-todo-phaseiv}"
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

    # Check if namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_error "Namespace $NAMESPACE not found"
        exit 1
    fi

    # Check if any pods exist
    local pod_count=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    if [ "$pod_count" -eq 0 ]; then
        log_error "No pods found in namespace $NAMESPACE"
        exit 1
    fi

    log_success "Pre-flight checks passed"
}

# Get pod count for a service
get_pod_count() {
    local app_label=$1
    kubectl get pods -n "$NAMESPACE" -l app="$app_label" --field-selector status.phase=Running --no-headers 2>/dev/null | wc -l
}

# Get a random pod for a service
get_random_pod() {
    local app_label=$1
    kubectl get pods -n "$NAMESPACE" -l app="$app_label" --field-selector status.phase=Running -o jsonpath='{.items[0].metadata.name}' 2>/dev/null
}

# Delete a pod
delete_pod() {
    local pod_name=$1

    log_info "Deleting pod: $pod_name"

    if kubectl delete pod "$pod_name" -n "$NAMESPACE" --grace-period=5 &> /dev/null; then
        log_success "Pod deleted: $pod_name"
        return 0
    else
        log_error "Failed to delete pod: $pod_name"
        return 1
    fi
}

# Wait for pod count to be restored
wait_for_pod_recovery() {
    local app_label=$1
    local expected_count=$2

    log_info "Waiting for pod recovery (expected: $expected_count pods, timeout: ${RESTART_TIMEOUT}s)..."

    local elapsed=0
    while [ $elapsed -lt $RESTART_TIMEOUT ]; do
        sleep 5
        elapsed=$((elapsed + 5))

        local current_count=$(get_pod_count "$app_label")
        local ready_count=$(kubectl get pods -n "$NAMESPACE" -l app="$app_label" --field-selector status.phase=Running -o jsonpath='{range .items[*]}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}' 2>/dev/null | grep -c "True" || echo "0")

        log_info "[$elapsed/${RESTART_TIMEOUT}s] Pods: $current_count/$expected_count running, $ready_count ready"

        if [ "$current_count" -eq "$expected_count" ] && [ "$ready_count" -eq "$expected_count" ]; then
            log_success "Pod recovery complete (${elapsed}s)"
            return 0
        fi
    done

    log_error "Timeout waiting for pod recovery"
    return 1
}

# Test frontend resilience
test_frontend_resilience() {
    log_info "Testing Frontend resilience..."
    echo ""

    # Get initial pod count
    local initial_count=$(get_pod_count "frontend")
    log_info "Initial frontend pod count: $initial_count"

    if [ "$initial_count" -eq 0 ]; then
        log_error "No frontend pods running"
        return 1
    fi

    # Get a random frontend pod
    local pod_to_delete=$(get_random_pod "frontend")
    if [ -z "$pod_to_delete" ]; then
        log_error "Unable to find frontend pod to delete"
        return 1
    fi

    log_info "Selected pod for deletion: $pod_to_delete"
    echo ""

    # Delete the pod
    if ! delete_pod "$pod_to_delete"; then
        return 1
    fi
    echo ""

    # Wait for recovery
    if wait_for_pod_recovery "frontend" "$initial_count"; then
        log_success "Frontend resilience test passed"
        return 0
    else
        log_error "Frontend resilience test failed"
        return 1
    fi
}

# Test backend resilience
test_backend_resilience() {
    log_info "Testing Backend resilience..."
    echo ""

    # Get initial pod count
    local initial_count=$(get_pod_count "backend")
    log_info "Initial backend pod count: $initial_count"

    if [ "$initial_count" -eq 0 ]; then
        log_error "No backend pods running"
        return 1
    fi

    # Get a random backend pod
    local pod_to_delete=$(get_random_pod "backend")
    if [ -z "$pod_to_delete" ]; then
        log_error "Unable to find backend pod to delete"
        return 1
    fi

    log_info "Selected pod for deletion: $pod_to_delete"
    echo ""

    # Delete the pod
    if ! delete_pod "$pod_to_delete"; then
        return 1
    fi
    echo ""

    # Wait for recovery
    if wait_for_pod_recovery "backend" "$initial_count"; then
        log_success "Backend resilience test passed"
        return 0
    else
        log_error "Backend resilience test failed"
        return 1
    fi
}

# Test MCP Server resilience
test_mcp_resilience() {
    log_info "Testing MCP Server resilience..."
    echo ""

    # Get initial pod count
    local initial_count=$(get_pod_count "mcp-server")
    log_info "Initial MCP Server pod count: $initial_count"

    if [ "$initial_count" -eq 0 ]; then
        log_error "No MCP Server pods running"
        return 1
    fi

    # Get the MCP Server pod
    local pod_to_delete=$(get_random_pod "mcp-server")
    if [ -z "$pod_to_delete" ]; then
        log_error "Unable to find MCP Server pod to delete"
        return 1
    fi

    log_info "Selected pod for deletion: $pod_to_delete"
    echo ""

    # Delete the pod
    if ! delete_pod "$pod_to_delete"; then
        return 1
    fi
    echo ""

    # Wait for recovery
    if wait_for_pod_recovery "mcp-server" "$initial_count"; then
        log_success "MCP Server resilience test passed"
        return 0
    else
        log_error "MCP Server resilience test failed"
        return 1
    fi
}

# Test Redis resilience (StatefulSet)
test_redis_resilience() {
    log_info "Testing Redis resilience (StatefulSet)..."
    echo ""

    # Redis uses StatefulSet, so we check specifically for redis-0
    local redis_pod="redis-0"

    if ! kubectl get pod "$redis_pod" -n "$NAMESPACE" &> /dev/null; then
        log_error "Redis pod $redis_pod not found"
        return 1
    fi

    log_info "Selected pod for deletion: $redis_pod"
    echo ""

    # Delete the pod
    if ! delete_pod "$redis_pod"; then
        return 1
    fi
    echo ""

    # Wait for recovery (StatefulSet should recreate with same name)
    log_info "Waiting for Redis pod to be recreated (timeout: ${RESTART_TIMEOUT}s)..."

    local elapsed=0
    while [ $elapsed -lt $RESTART_TIMEOUT ]; do
        sleep 5
        elapsed=$((elapsed + 5))

        if kubectl get pod "$redis_pod" -n "$NAMESPACE" &> /dev/null; then
            local pod_status=$(kubectl get pod "$redis_pod" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
            local ready=$(kubectl get pod "$redis_pod" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "False")

            log_info "[$elapsed/${RESTART_TIMEOUT}s] Pod status: $pod_status, Ready: $ready"

            if [ "$pod_status" = "Running" ] && [ "$ready" = "True" ]; then
                log_success "Redis pod recovery complete (${elapsed}s)"
                log_success "Redis resilience test passed"
                return 0
            fi
        else
            log_info "[$elapsed/${RESTART_TIMEOUT}s] Waiting for pod to be created..."
        fi
    done

    log_error "Timeout waiting for Redis pod recovery"
    return 1
}

# Display pod status
display_pod_status() {
    echo ""
    log_info "Current Pod Status:"
    kubectl get pods -n "$NAMESPACE" -o wide
    echo ""

    log_info "Pod Events (last 5 minutes):"
    kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -10
    echo ""
}

# Main execution
main() {
    log_info "Starting pod resilience tests..."
    echo ""

    preflight_checks
    echo ""

    local test_failures=0

    # Test Frontend resilience
    if ! test_frontend_resilience; then
        test_failures=$((test_failures + 1))
    fi
    echo ""

    # Test Backend resilience
    if ! test_backend_resilience; then
        test_failures=$((test_failures + 1))
    fi
    echo ""

    # Test MCP Server resilience
    if ! test_mcp_resilience; then
        test_failures=$((test_failures + 1))
    fi
    echo ""

    # Test Redis resilience
    if ! test_redis_resilience; then
        test_failures=$((test_failures + 1))
    fi
    echo ""

    # Display final pod status
    display_pod_status

    # Summary
    if [ $test_failures -eq 0 ]; then
        log_success "=== All resilience tests passed! ==="
        log_success "Kubernetes successfully recreated all deleted pods"
        return 0
    else
        log_error "=== $test_failures resilience test(s) failed ==="
        log_error "Troubleshooting steps:"
        echo "  1. Check pod events: kubectl describe pod <pod-name> -n $NAMESPACE"
        echo "  2. Check deployment status: kubectl get deployments -n $NAMESPACE"
        echo "  3. Check ReplicaSet status: kubectl get rs -n $NAMESPACE"
        echo "  4. Check StatefulSet status: kubectl get statefulset -n $NAMESPACE"
        echo "  5. Check resource limits: kubectl top pods -n $NAMESPACE"
        return 1
    fi
}

# Run main function
main "$@"
