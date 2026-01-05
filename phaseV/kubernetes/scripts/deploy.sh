#!/usr/bin/env bash
# Deploy Todo App Phase V to Kubernetes via Helm
# Implements incremental rollout: Redis → MCP → Backend → Frontend → Ingress

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RELEASE_NAME="todo-app"
NAMESPACE="todo-phasev"
CHART_PATH="./phaseV/kubernetes/helm/todo-app"
VALUES_FILE="${VALUES_FILE:-values-local.yaml}"
TIMEOUT="10m"

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

    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please run ./scripts/setup-minikube.sh first"
        exit 1
    fi

    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        log_error "helm not found. Please run ./scripts/setup-minikube.sh first"
        exit 1
    fi

    # Check if Minikube is running
    if ! minikube status | grep -q "Running"; then
        log_error "Minikube is not running. Please run ./scripts/setup-minikube.sh first"
        exit 1
    fi

    # Check if Nginx Ingress is enabled
    if ! minikube addons list | grep ingress | grep -q enabled; then
        log_warn "Nginx Ingress addon not enabled. Enabling now..."
        minikube addons enable ingress
    fi

    # Check if Metrics Server is enabled
    if ! minikube addons list | grep metrics-server | grep -q enabled; then
        log_warn "Metrics Server addon not enabled. Enabling now..."
        minikube addons enable metrics-server
    fi

    # Check if chart exists
    if [ ! -f "$CHART_PATH/Chart.yaml" ]; then
        log_error "Helm chart not found at $CHART_PATH"
        exit 1
    fi

    log_success "Pre-flight checks passed"
}

# Build Docker images using Minikube's Docker daemon
build_images() {
    log_info "Building Docker images using Minikube's Docker daemon..."

    # Set Docker environment to use Minikube
    eval $(minikube docker-env)

    # Build frontend image
    log_info "Building frontend image..."
    docker build -t todo-frontend:latest phaseV/frontend

    # Build backend image
    log_info "Building backend image..."
    docker build -t todo-backend:latest phaseV/backend

    log_success "Docker images built successfully"
}

# Lint Helm chart
lint_chart() {
    log_info "Linting Helm chart..."
    helm lint "$CHART_PATH"
    log_success "Helm chart lint passed"
}

# Deploy with Helm
deploy_helm() {
    log_info "Deploying Helm chart..."

    local values_arg=""
    if [ -f "$CHART_PATH/$VALUES_FILE" ]; then
        log_info "Using values file: $VALUES_FILE"
        values_arg="-f $CHART_PATH/$VALUES_FILE"
    elif [ -f "$VALUES_FILE" ]; then
        log_info "Using values file: $VALUES_FILE"
        values_arg="-f $VALUES_FILE"
    else
        log_warn "Values file $VALUES_FILE not found, using default values.yaml"
    fi

    # Check if release already exists
    if helm list -n "$NAMESPACE" | grep -q "$RELEASE_NAME"; then
        log_info "Existing release found, upgrading..."
        helm upgrade "$RELEASE_NAME" "$CHART_PATH" \
            --namespace "$NAMESPACE" \
            --timeout "$TIMEOUT" \
            --wait \
            $values_arg
    else
        log_info "Installing new release..."
        helm install "$RELEASE_NAME" "$CHART_PATH" \
            --namespace "$NAMESPACE" \
            --create-namespace \
            --timeout "$TIMEOUT" \
            --wait \
            $values_arg
    fi

    log_success "Helm deployment complete"
}

# Wait for service to be ready
wait_for_service() {
    local service_name=$1
    local timeout=${2:-300}

    log_info "Waiting for $service_name to be ready (timeout: ${timeout}s)..."

    kubectl wait --namespace "$NAMESPACE" \
        --for=condition=ready pod \
        --selector=app="$service_name" \
        --timeout="${timeout}s" || {
            log_error "Timeout waiting for $service_name"
            return 1
        }

    log_success "$service_name is ready"
}

# Health validation gates (incremental rollout)
validate_rollout() {
    log_info "=== Starting incremental rollout validation ==="
    echo ""

    # Stage 1: Redis
    log_info "[Stage 1/4] Validating Redis..."
    wait_for_service "redis" 120
    echo ""

    # Stage 2: MCP Server
    log_info "[Stage 2/4] Validating MCP Server..."
    wait_for_service "mcp-server" 120
    echo ""

    # Stage 3: Backend
    log_info "[Stage 3/4] Validating Backend..."
    wait_for_service "backend" 180
    echo ""

    # Stage 4: Frontend
    log_info "[Stage 4/4] Validating Frontend..."
    wait_for_service "frontend" 180
    echo ""

    log_success "All services are ready!"
}

# Display deployment status
display_status() {
    echo ""
    log_success "=== Deployment Complete ==="
    echo ""

    log_info "Pods:"
    kubectl get pods -n "$NAMESPACE"
    echo ""

    log_info "Services:"
    kubectl get services -n "$NAMESPACE"
    echo ""

    log_info "Ingress:"
    kubectl get ingress -n "$NAMESPACE"
    echo ""

    log_info "HPA:"
    kubectl get hpa -n "$NAMESPACE"
    echo ""

    local minikube_ip=$(minikube ip)
    log_warn "Access the application:"
    echo "  1. Ensure /etc/hosts has: $minikube_ip todo-app.local"
    echo "  2. Frontend: http://todo-app.local"
    echo "  3. Backend API: http://todo-app.local/api/health"
    echo ""

    log_warn "Run tests:"
    echo "  helm test $RELEASE_NAME -n $NAMESPACE"
    echo ""
}

# Main execution
main() {
    log_info "Starting deployment of Todo App Phase V..."
    echo ""

    preflight_checks
    build_images
    lint_chart
    deploy_helm
    validate_rollout
    display_status

    log_success "Deployment completed successfully!"
}

# Run main function
main "$@"
