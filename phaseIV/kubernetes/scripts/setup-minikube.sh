#!/usr/bin/env bash
# Setup Minikube for Todo App Phase IV
# This script installs required tools and sets up a local Kubernetes cluster

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MINIKUBE_CPU=4
MINIKUBE_MEMORY=8192
KUBERNETES_VERSION="v1.28.0"

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

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Linux*)     OS=linux;;
        Darwin*)    OS=darwin;;
        *)          OS=unknown;;
    esac

    case "$(uname -m)" in
        x86_64*)    ARCH=amd64;;
        arm64*)     ARCH=arm64;;
        aarch64*)   ARCH=arm64;;
        *)          ARCH=unknown;;
    esac

    log_info "Detected OS: $OS, Architecture: $ARCH"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install kubectl
install_kubectl() {
    if command_exists kubectl; then
        log_success "kubectl already installed: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
        return 0
    fi

    log_info "Installing kubectl..."

    if [ "$OS" = "linux" ]; then
        curl -LO "https://dl.k8s.io/release/${KUBERNETES_VERSION}/bin/linux/${ARCH}/kubectl"
        chmod +x kubectl
        sudo mv kubectl /usr/local/bin/
    elif [ "$OS" = "darwin" ]; then
        curl -LO "https://dl.k8s.io/release/${KUBERNETES_VERSION}/bin/darwin/${ARCH}/kubectl"
        chmod +x kubectl
        sudo mv kubectl /usr/local/bin/
    else
        log_error "Unsupported OS: $OS"
        exit 1
    fi

    log_success "kubectl installed successfully"
}

# Install Helm
install_helm() {
    if command_exists helm; then
        log_success "Helm already installed: $(helm version --short)"
        return 0
    fi

    log_info "Installing Helm..."
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    log_success "Helm installed successfully"
}

# Install Minikube
install_minikube() {
    if command_exists minikube; then
        log_success "Minikube already installed: $(minikube version --short)"
        return 0
    fi

    log_info "Installing Minikube..."

    if [ "$OS" = "linux" ]; then
        curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-${ARCH}
        chmod +x minikube-linux-${ARCH}
        sudo mv minikube-linux-${ARCH} /usr/local/bin/minikube
    elif [ "$OS" = "darwin" ]; then
        curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-${ARCH}
        chmod +x minikube-darwin-${ARCH}
        sudo mv minikube-darwin-${ARCH} /usr/local/bin/minikube
    else
        log_error "Unsupported OS: $OS"
        exit 1
    fi

    log_success "Minikube installed successfully"
}

# Start Minikube cluster
start_minikube() {
    log_info "Starting Minikube cluster with ${MINIKUBE_CPU} CPUs and ${MINIKUBE_MEMORY}MB RAM..."

    if minikube status | grep -q "Running"; then
        log_warn "Minikube is already running"
        return 0
    fi

    minikube start \
        --cpus="$MINIKUBE_CPU" \
        --memory="$MINIKUBE_MEMORY" \
        --kubernetes-version="$KUBERNETES_VERSION" \
        --driver=docker

    log_success "Minikube cluster started successfully"
}

# Enable Minikube addons
enable_addons() {
    log_info "Enabling Minikube addons (ingress, metrics-server)..."

    minikube addons enable ingress
    minikube addons enable metrics-server

    log_success "Addons enabled successfully"

    log_info "Waiting for Nginx Ingress Controller to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=120s || log_warn "Ingress controller may not be ready yet"
}

# Display cluster information
display_info() {
    echo ""
    log_success "=== Minikube Setup Complete ==="
    echo ""
    log_info "Cluster Information:"
    kubectl cluster-info
    echo ""
    log_info "Nodes:"
    kubectl get nodes
    echo ""
    log_info "Addons:"
    minikube addons list | grep enabled
    echo ""
    log_info "Minikube IP: $(minikube ip)"
    echo ""
    log_warn "Next steps:"
    echo "  1. Add the following line to /etc/hosts (requires sudo):"
    echo "     $(minikube ip) todo-app.local"
    echo ""
    echo "  2. Build Docker images using Minikube's Docker daemon:"
    echo "     eval \$(minikube docker-env)"
    echo "     docker build -t todo-frontend:latest phaseIV/frontend"
    echo "     docker build -t todo-backend:latest phaseIV/backend"
    echo ""
    echo "  3. Deploy the application:"
    echo "     ./phaseIV/kubernetes/scripts/deploy.sh"
    echo ""
}

# Main execution
main() {
    log_info "Starting Minikube setup for Todo App Phase IV..."
    echo ""

    detect_os
    install_kubectl
    install_helm
    install_minikube
    start_minikube
    enable_addons
    display_info

    log_success "Minikube setup completed successfully!"
}

# Run main function
main "$@"
