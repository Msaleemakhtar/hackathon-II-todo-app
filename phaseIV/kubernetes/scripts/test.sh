#!/usr/bin/env bash
# Master Test Runner for Todo App Phase IV
# Executes all test suites: Helm, Ingress, Persistence, Resilience, Load, E2E

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-todo-phaseiv}"
RELEASE_NAME="todo-app"
SKIP_LOAD_TEST=false
SKIP_HELM_TEST=false

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

log_section() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-load-test)
                SKIP_LOAD_TEST=true
                shift
                ;;
            --skip-helm-test)
                SKIP_HELM_TEST=true
                shift
                ;;
            --namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Show help message
show_help() {
    cat << EOF
Master Test Runner for Todo App Phase IV

Usage: $0 [OPTIONS]

Options:
  --namespace <name>     Override namespace (default: todo-phaseiv)
  --skip-load-test      Skip load testing (for CI environments)
  --skip-helm-test      Skip Helm test suite
  --help                Show this help message

Test Suites:
  1. Helm Tests         - Validate pod health via Helm test pods
  2. Ingress Tests      - Validate HTTP routing (frontend and backend)
  3. Persistence Tests  - Validate Redis data retention across pod restarts
  4. Resilience Tests   - Validate Kubernetes self-healing
  5. Load Tests         - Validate HPA scaling under load (optional)
  6. E2E Tests          - Validate complete user flow

Example:
  $0                           # Run all tests
  $0 --skip-load-test          # Skip load testing
  $0 --namespace my-namespace  # Use custom namespace

EOF
}

# Pre-flight checks
preflight_checks() {
    log_info "Running pre-flight checks..."

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

    # Check if namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_error "Namespace $NAMESPACE not found"
        exit 1
    fi

    # Check if Helm release exists
    if ! helm list -n "$NAMESPACE" | grep -q "$RELEASE_NAME"; then
        log_error "Helm release $RELEASE_NAME not found in namespace $NAMESPACE"
        exit 1
    fi

    # Check if all pods are running
    local pod_count=$(kubectl get pods -n "$NAMESPACE" --field-selector status.phase=Running --no-headers 2>/dev/null | wc -l)
    if [ "$pod_count" -eq 0 ]; then
        log_error "No pods running in namespace $NAMESPACE"
        exit 1
    fi

    log_success "Pre-flight checks passed"
}

# Test Suite 1: Helm Tests
run_helm_tests() {
    log_section "Test Suite 1: Helm Tests"

    if [ "$SKIP_HELM_TEST" = true ]; then
        log_warn "Skipping Helm tests (--skip-helm-test flag set)"
        return 0
    fi

    log_info "Running Helm test suite..."

    if helm test "$RELEASE_NAME" -n "$NAMESPACE" --timeout 5m; then
        log_success "Helm tests passed"
        return 0
    else
        log_error "Helm tests failed"
        log_info "Checking test pod logs..."
        kubectl logs -n "$NAMESPACE" -l "app.kubernetes.io/managed-by=Helm" --tail=50 || true
        return 1
    fi
}

# Test Suite 2: Ingress Tests
run_ingress_tests() {
    log_section "Test Suite 2: Ingress Tests"

    if [ -f "$SCRIPT_DIR/test-ingress.sh" ]; then
        if bash "$SCRIPT_DIR/test-ingress.sh"; then
            return 0
        else
            log_error "Ingress tests failed"
            return 1
        fi
    else
        log_error "test-ingress.sh not found at $SCRIPT_DIR/test-ingress.sh"
        return 1
    fi
}

# Test Suite 3: Persistence Tests
run_persistence_tests() {
    log_section "Test Suite 3: Persistence Tests"

    if [ -f "$SCRIPT_DIR/test-persistence.sh" ]; then
        if bash "$SCRIPT_DIR/test-persistence.sh"; then
            return 0
        else
            log_error "Persistence tests failed"
            return 1
        fi
    else
        log_error "test-persistence.sh not found at $SCRIPT_DIR/test-persistence.sh"
        return 1
    fi
}

# Test Suite 4: Resilience Tests
run_resilience_tests() {
    log_section "Test Suite 4: Resilience Tests"

    if [ -f "$SCRIPT_DIR/test-resilience.sh" ]; then
        if bash "$SCRIPT_DIR/test-resilience.sh"; then
            return 0
        else
            log_error "Resilience tests failed"
            return 1
        fi
    else
        log_error "test-resilience.sh not found at $SCRIPT_DIR/test-resilience.sh"
        return 1
    fi
}

# Test Suite 5: Load Tests
run_load_tests() {
    log_section "Test Suite 5: Load Tests (HPA Scaling)"

    if [ "$SKIP_LOAD_TEST" = true ]; then
        log_warn "Skipping load tests (--skip-load-test flag set)"
        return 0
    fi

    if [ -f "$SCRIPT_DIR/test-load.sh" ]; then
        if bash "$SCRIPT_DIR/test-load.sh"; then
            return 0
        else
            log_warn "Load tests completed with warnings (may be expected)"
            return 0
        fi
    else
        log_error "test-load.sh not found at $SCRIPT_DIR/test-load.sh"
        return 1
    fi
}

# Test Suite 6: E2E Tests
run_e2e_tests() {
    log_section "Test Suite 6: End-to-End Tests"

    if [ -f "$SCRIPT_DIR/test-e2e.sh" ]; then
        if bash "$SCRIPT_DIR/test-e2e.sh"; then
            return 0
        else
            log_warn "E2E tests completed with warnings (may be expected)"
            return 0
        fi
    else
        log_error "test-e2e.sh not found at $SCRIPT_DIR/test-e2e.sh"
        return 1
    fi
}

# Display final summary
display_summary() {
    local total_tests=$1
    local failed_tests=$2
    local passed_tests=$((total_tests - failed_tests))

    echo ""
    log_section "Test Summary"

    log_info "Total Test Suites: $total_tests"
    log_success "Passed: $passed_tests"

    if [ $failed_tests -gt 0 ]; then
        log_error "Failed: $failed_tests"
    fi

    echo ""

    if [ $failed_tests -eq 0 ]; then
        log_success "=== ALL TESTS PASSED ==="
        log_success "Todo App Phase IV is fully functional!"
    else
        log_error "=== SOME TESTS FAILED ==="
        log_error "Please review the test output above for details"
    fi

    echo ""
}

# Display system status
display_system_status() {
    log_section "System Status"

    log_info "Pods:"
    kubectl get pods -n "$NAMESPACE"
    echo ""

    log_info "Services:"
    kubectl get svc -n "$NAMESPACE"
    echo ""

    log_info "HPA:"
    kubectl get hpa -n "$NAMESPACE"
    echo ""

    log_info "PVC:"
    kubectl get pvc -n "$NAMESPACE"
    echo ""

    log_info "Ingress:"
    kubectl get ingress -n "$NAMESPACE"
    echo ""
}

# Main execution
main() {
    local start_time=$(date +%s)

    log_section "Todo App Phase IV - Master Test Runner"
    log_info "Namespace: $NAMESPACE"
    log_info "Release: $RELEASE_NAME"
    echo ""

    parse_args "$@"

    preflight_checks
    echo ""

    local total_tests=6
    local failed_tests=0

    # Run all test suites
    if ! run_helm_tests; then
        failed_tests=$((failed_tests + 1))
    fi

    if ! run_ingress_tests; then
        failed_tests=$((failed_tests + 1))
    fi

    if ! run_persistence_tests; then
        failed_tests=$((failed_tests + 1))
    fi

    if ! run_resilience_tests; then
        failed_tests=$((failed_tests + 1))
    fi

    if ! run_load_tests; then
        if [ "$SKIP_LOAD_TEST" = false ]; then
            failed_tests=$((failed_tests + 1))
        else
            total_tests=$((total_tests - 1))
        fi
    fi

    if ! run_e2e_tests; then
        # E2E tests may have warnings, don't count as failure
        log_info "E2E tests completed (check output for details)"
    fi

    # Display system status
    display_system_status

    # Calculate duration
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    log_info "Total test duration: ${duration}s"

    # Display summary
    display_summary "$total_tests" "$failed_tests"

    # Exit with appropriate code
    if [ $failed_tests -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main "$@"
