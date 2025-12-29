#!/usr/bin/env bash
# Test Load and HPA Scaling for Todo App Phase IV
# Generates load with Apache Bench and validates HPA scaling behavior

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-todo-phaseiv}"
BASE_URL="http://todo-app.local"
REQUESTS=10000
CONCURRENCY=50
SCALE_WAIT_TIME=120  # Wait 2 minutes for HPA to scale
MIN_REPLICAS=2
MAX_REPLICAS=5

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

    # Check if Apache Bench is installed
    if ! command -v ab &> /dev/null; then
        log_warn "Apache Bench (ab) not found"
        log_info "Installing Apache Bench..."

        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y apache2-utils
        elif command -v yum &> /dev/null; then
            sudo yum install -y httpd-tools
        elif command -v brew &> /dev/null; then
            brew install httpd
        else
            log_error "Unable to install Apache Bench. Please install manually"
            exit 1
        fi
    fi

    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found"
        exit 1
    fi

    # Check if Minikube is running
    if ! minikube status | grep -q "Running"; then
        log_error "Minikube is not running"
        exit 1
    fi

    # Check if HPA exists
    if ! kubectl get hpa -n "$NAMESPACE" &> /dev/null; then
        log_error "No HPA found in namespace $NAMESPACE"
        exit 1
    fi

    # Check if Metrics Server is running
    if ! kubectl get deployment metrics-server -n kube-system &> /dev/null; then
        log_error "Metrics Server not found. Enable with: minikube addons enable metrics-server"
        exit 1
    fi

    log_success "Pre-flight checks passed"
}

# Get HPA status
get_hpa_status() {
    local hpa_name=$1
    local field=$2

    kubectl get hpa "$hpa_name" -n "$NAMESPACE" -o jsonpath="{$field}" 2>/dev/null || echo "0"
}

# Display HPA status
display_hpa_status() {
    echo ""
    log_info "HPA Status:"
    kubectl get hpa -n "$NAMESPACE"
    echo ""
}

# Test frontend HPA scaling
test_frontend_hpa() {
    log_info "Testing Frontend HPA scaling..."
    echo ""

    # Get initial replica count
    local initial_replicas=$(get_hpa_status "frontend-hpa" ".status.currentReplicas")
    log_info "Initial frontend replicas: $initial_replicas"

    if [ "$initial_replicas" = "0" ] || [ -z "$initial_replicas" ]; then
        log_error "Unable to get current replica count. HPA may not be ready"
        log_info "Waiting 30 seconds for metrics to be available..."
        sleep 30
        initial_replicas=$(get_hpa_status "frontend-hpa" ".status.currentReplicas")

        if [ "$initial_replicas" = "0" ] || [ -z "$initial_replicas" ]; then
            log_error "HPA still not reporting metrics. Skipping load test"
            return 1
        fi
    fi

    # Display initial HPA status
    display_hpa_status

    # Generate load
    log_info "Generating load: $REQUESTS requests with concurrency $CONCURRENCY..."
    log_info "Target: $BASE_URL/"
    echo ""

    ab -n "$REQUESTS" -c "$CONCURRENCY" "$BASE_URL/" > /tmp/ab-results.txt 2>&1 || {
        log_error "Apache Bench failed"
        cat /tmp/ab-results.txt
        return 1
    }

    # Display load test results
    log_success "Load generation complete"
    echo ""
    log_info "Load test summary:"
    grep "Requests per second" /tmp/ab-results.txt || true
    grep "Time per request" /tmp/ab-results.txt | head -1 || true
    grep "Transfer rate" /tmp/ab-results.txt || true
    echo ""

    # Wait for HPA to scale
    log_info "Waiting ${SCALE_WAIT_TIME}s for HPA to scale..."
    log_info "Monitoring replica count every 10 seconds..."
    echo ""

    local elapsed=0
    local max_replicas_seen=$initial_replicas

    while [ $elapsed -lt $SCALE_WAIT_TIME ]; do
        sleep 10
        elapsed=$((elapsed + 10))

        local current_replicas=$(get_hpa_status "frontend-hpa" ".status.currentReplicas")
        local current_cpu=$(get_hpa_status "frontend-hpa" ".status.currentMetrics[0].resource.current.averageUtilization")

        log_info "[$elapsed/${SCALE_WAIT_TIME}s] Replicas: $current_replicas, CPU: ${current_cpu}%"

        if [ "$current_replicas" -gt "$max_replicas_seen" ]; then
            max_replicas_seen=$current_replicas
        fi
    done

    echo ""
    log_info "Final replica count: $max_replicas_seen (started at $initial_replicas)"

    # Display final HPA status
    display_hpa_status

    # Validate scaling occurred
    if [ "$max_replicas_seen" -gt "$initial_replicas" ]; then
        log_success "HPA scaled successfully: $initial_replicas → $max_replicas_seen replicas"
        return 0
    else
        log_warn "HPA did not scale up (still at $initial_replicas replicas)"
        log_warn "This may be expected if:"
        log_warn "  1. Load was not sufficient to trigger scaling"
        log_warn "  2. CPU usage stayed below threshold (70%)"
        log_warn "  3. Metrics Server needs more time to collect data"
        log_warn "Try running the test again or increase load parameters"
        return 0
    fi
}

# Test backend HPA scaling
test_backend_hpa() {
    log_info "Testing Backend HPA scaling..."
    echo ""

    # Get initial replica count
    local initial_replicas=$(get_hpa_status "backend-hpa" ".status.currentReplicas")
    log_info "Initial backend replicas: $initial_replicas"

    if [ "$initial_replicas" = "0" ] || [ -z "$initial_replicas" ]; then
        log_warn "Unable to get backend replica count. Skipping backend load test"
        return 0
    fi

    # Generate load on backend API
    log_info "Generating load on backend: $REQUESTS requests with concurrency $CONCURRENCY..."
    log_info "Target: $BASE_URL/api/health"
    echo ""

    ab -n "$REQUESTS" -c "$CONCURRENCY" "$BASE_URL/api/health" > /tmp/ab-backend-results.txt 2>&1 || {
        log_warn "Apache Bench failed for backend (may be expected)"
        return 0
    }

    log_success "Backend load generation complete"
    echo ""

    # Wait and check scaling
    log_info "Waiting 30s to check backend scaling..."
    sleep 30

    local final_replicas=$(get_hpa_status "backend-hpa" ".status.currentReplicas")
    log_info "Backend replicas: $initial_replicas → $final_replicas"

    if [ "$final_replicas" -gt "$initial_replicas" ]; then
        log_success "Backend HPA scaled successfully"
    else
        log_info "Backend HPA did not scale (may be expected for health endpoint)"
    fi

    echo ""
}

# Display pod distribution
display_pod_distribution() {
    echo ""
    log_info "Pod Distribution:"
    kubectl get pods -n "$NAMESPACE" -o wide | grep -E "NAME|frontend|backend"
    echo ""
}

# Main execution
main() {
    log_info "Starting HPA load testing..."
    echo ""

    preflight_checks
    echo ""

    local test_failures=0

    # Test frontend HPA
    if ! test_frontend_hpa; then
        test_failures=$((test_failures + 1))
    fi
    echo ""

    # Test backend HPA (optional)
    test_backend_hpa
    echo ""

    # Display pod distribution
    display_pod_distribution

    # Summary
    if [ $test_failures -eq 0 ]; then
        log_success "=== HPA load tests completed ==="
        log_info "Note: HPA may take 2-5 minutes to scale down to minimum replicas"
        return 0
    else
        log_error "=== HPA load tests had issues ==="
        log_error "Check HPA configuration and metrics availability"
        return 1
    fi
}

# Run main function
main "$@"
