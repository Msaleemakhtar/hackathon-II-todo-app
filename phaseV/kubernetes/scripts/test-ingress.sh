#!/usr/bin/env bash
# Test Ingress HTTP Routing for Todo App Phase IV
# Validates frontend and backend routes through Nginx Ingress

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
TIMEOUT=5

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

    # Check if curl is installed
    if ! command -v curl &> /dev/null; then
        log_error "curl not found. Please install curl"
        exit 1
    fi

    # Check if Minikube is running
    if ! minikube status | grep -q "Running"; then
        log_error "Minikube is not running"
        exit 1
    fi

    # Check if Ingress is deployed
    if ! kubectl get ingress -n "$NAMESPACE" &> /dev/null; then
        log_error "No Ingress found in namespace $NAMESPACE"
        exit 1
    fi

    # Check /etc/hosts configuration
    if ! grep -q "todo-app.local" /etc/hosts 2>/dev/null; then
        log_warn "/etc/hosts does not contain todo-app.local entry"
        log_warn "Add the following line to /etc/hosts:"
        echo "  $(minikube ip) todo-app.local"
    fi

    log_success "Pre-flight checks passed"
}

# Test frontend route
test_frontend_route() {
    log_info "Testing frontend route (GET /)..."

    local http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$BASE_URL/" 2>/dev/null || echo "000")

    if [ "$http_code" = "200" ]; then
        log_success "Frontend route: HTTP $http_code"
        return 0
    elif [ "$http_code" = "000" ]; then
        log_error "Frontend route: Connection timeout or failed"
        log_error "Check if /etc/hosts is configured: $(minikube ip) todo-app.local"
        return 1
    else
        log_error "Frontend route: HTTP $http_code (expected 200)"
        return 1
    fi
}

# Test backend health route
test_backend_health_route() {
    log_info "Testing backend health route (GET /api/health)..."

    local response=$(curl -s --max-time "$TIMEOUT" "$BASE_URL/api/health" 2>/dev/null || echo "")
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$BASE_URL/api/health" 2>/dev/null || echo "000")

    if [ "$http_code" = "200" ]; then
        log_success "Backend health route: HTTP $http_code"

        # Validate JSON response
        if echo "$response" | grep -q "status"; then
            log_success "Backend health response contains 'status' field"
            return 0
        else
            log_warn "Backend health response does not contain expected JSON structure"
            return 0
        fi
    elif [ "$http_code" = "000" ]; then
        log_error "Backend health route: Connection timeout or failed"
        return 1
    else
        log_error "Backend health route: HTTP $http_code (expected 200)"
        return 1
    fi
}

# Test backend API route (additional validation)
test_backend_api_route() {
    log_info "Testing backend API docs route (GET /api/docs)..."

    local http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$BASE_URL/api/docs" 2>/dev/null || echo "000")

    if [ "$http_code" = "200" ]; then
        log_success "Backend API docs route: HTTP $http_code"
        return 0
    elif [ "$http_code" = "000" ]; then
        log_warn "Backend API docs route: Connection timeout (may be expected if docs disabled)"
        return 0
    else
        log_warn "Backend API docs route: HTTP $http_code (may be expected)"
        return 0
    fi
}

# Display Ingress configuration
display_ingress_config() {
    echo ""
    log_info "Ingress Configuration:"
    kubectl get ingress -n "$NAMESPACE" -o wide
    echo ""

    log_info "Ingress Rules:"
    kubectl describe ingress -n "$NAMESPACE" | grep -A 10 "Rules:"
    echo ""
}

# Main execution
main() {
    log_info "Starting Ingress HTTP routing tests..."
    echo ""

    preflight_checks
    echo ""

    local test_failures=0

    # Test frontend route
    if ! test_frontend_route; then
        test_failures=$((test_failures + 1))
    fi
    echo ""

    # Test backend health route
    if ! test_backend_health_route; then
        test_failures=$((test_failures + 1))
    fi
    echo ""

    # Test backend API docs route (optional)
    test_backend_api_route
    echo ""

    # Display configuration
    display_ingress_config

    # Summary
    if [ $test_failures -eq 0 ]; then
        log_success "=== All Ingress tests passed! ==="
        return 0
    else
        log_error "=== $test_failures Ingress test(s) failed ==="
        log_error "Troubleshooting steps:"
        echo "  1. Check /etc/hosts: $(minikube ip) todo-app.local"
        echo "  2. Check pods: kubectl get pods -n $NAMESPACE"
        echo "  3. Check services: kubectl get svc -n $NAMESPACE"
        echo "  4. Check ingress: kubectl describe ingress -n $NAMESPACE"
        echo "  5. Check ingress controller logs:"
        echo "     kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller"
        return 1
    fi
}

# Run main function
main "$@"
