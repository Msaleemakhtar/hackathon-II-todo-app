#!/usr/bin/env bash
# Cleanup Script for Todo App Phase IV
# Uninstalls Helm chart and optionally deletes namespace and stops Minikube

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-todo-phaseiv}"
RELEASE_NAME="todo-app"
DELETE_NAMESPACE=false
STOP_MINIKUBE=false
FORCE=false

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

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --delete-namespace)
                DELETE_NAMESPACE=true
                shift
                ;;
            --stop-minikube)
                STOP_MINIKUBE=true
                shift
                ;;
            --force)
                FORCE=true
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
Cleanup Script for Todo App Phase IV

Usage: $0 [OPTIONS]

Options:
  --namespace <name>      Override namespace (default: todo-phaseiv)
  --delete-namespace      Delete namespace after uninstalling Helm chart
  --stop-minikube         Stop Minikube cluster after cleanup
  --force                 Skip confirmation prompts
  --help                  Show this help message

Examples:
  $0                           # Uninstall Helm chart only
  $0 --delete-namespace        # Uninstall and delete namespace
  $0 --stop-minikube           # Uninstall and stop Minikube
  $0 --force                   # Skip confirmation prompts

EOF
}

# Confirm action
confirm_action() {
    local message=$1

    if [ "$FORCE" = true ]; then
        return 0
    fi

    echo -e "${YELLOW}$message${NC}"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Operation cancelled"
        exit 0
    fi
}

# Display current status
display_status() {
    log_info "Current deployment status:"
    echo ""

    # Check if Helm release exists
    if helm list -n "$NAMESPACE" | grep -q "$RELEASE_NAME"; then
        log_info "Helm Release:"
        helm list -n "$NAMESPACE" | grep -E "NAME|$RELEASE_NAME"
        echo ""

        log_info "Pods:"
        kubectl get pods -n "$NAMESPACE" 2>/dev/null || log_warn "Unable to list pods"
        echo ""

        log_info "PVCs:"
        kubectl get pvc -n "$NAMESPACE" 2>/dev/null || log_warn "Unable to list PVCs"
        echo ""
    else
        log_warn "Helm release $RELEASE_NAME not found in namespace $NAMESPACE"
    fi
}

# Uninstall Helm chart
uninstall_helm_chart() {
    log_info "Uninstalling Helm chart: $RELEASE_NAME"

    if helm list -n "$NAMESPACE" | grep -q "$RELEASE_NAME"; then
        confirm_action "This will uninstall the Helm release '$RELEASE_NAME' from namespace '$NAMESPACE'."

        if helm uninstall "$RELEASE_NAME" -n "$NAMESPACE"; then
            log_success "Helm chart uninstalled successfully"

            # Wait for pods to terminate
            log_info "Waiting for pods to terminate..."
            local timeout=60
            local elapsed=0

            while [ $elapsed -lt $timeout ]; do
                local pod_count=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
                if [ "$pod_count" -eq 0 ]; then
                    log_success "All pods terminated"
                    break
                fi

                sleep 5
                elapsed=$((elapsed + 5))
                log_info "[$elapsed/${timeout}s] Waiting for $pod_count pod(s) to terminate..."
            done

            return 0
        else
            log_error "Failed to uninstall Helm chart"
            return 1
        fi
    else
        log_warn "Helm release $RELEASE_NAME not found (may already be uninstalled)"
        return 0
    fi
}

# Delete namespace
delete_namespace() {
    log_info "Deleting namespace: $NAMESPACE"

    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        confirm_action "This will DELETE namespace '$NAMESPACE' and ALL its resources (including PVCs and data)."

        if kubectl delete namespace "$NAMESPACE"; then
            log_success "Namespace deleted successfully"

            # Wait for namespace to be fully deleted
            log_info "Waiting for namespace to be fully deleted..."
            local timeout=120
            local elapsed=0

            while [ $elapsed -lt $timeout ]; do
                if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
                    log_success "Namespace fully deleted"
                    break
                fi

                sleep 5
                elapsed=$((elapsed + 5))
                log_info "[$elapsed/${timeout}s] Waiting for namespace deletion..."
            done

            return 0
        else
            log_error "Failed to delete namespace"
            return 1
        fi
    else
        log_warn "Namespace $NAMESPACE not found (may already be deleted)"
        return 0
    fi
}

# Stop Minikube
stop_minikube() {
    log_info "Stopping Minikube cluster"

    if minikube status | grep -q "Running"; then
        confirm_action "This will STOP the Minikube cluster. All deployments across all namespaces will be stopped."

        if minikube stop; then
            log_success "Minikube cluster stopped successfully"
            return 0
        else
            log_error "Failed to stop Minikube cluster"
            return 1
        fi
    else
        log_warn "Minikube is not running"
        return 0
    fi
}

# Delete PVCs (if namespace not deleted)
delete_pvcs() {
    log_info "Checking for remaining PVCs..."

    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        local pvc_count=$(kubectl get pvc -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)

        if [ "$pvc_count" -gt 0 ]; then
            log_warn "Found $pvc_count PVC(s) in namespace $NAMESPACE"
            kubectl get pvc -n "$NAMESPACE"
            echo ""

            if [ "$FORCE" = false ]; then
                read -p "Delete these PVCs? This will delete all data! (y/N) " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    kubectl delete pvc --all -n "$NAMESPACE"
                    log_success "PVCs deleted"
                else
                    log_info "PVCs retained"
                fi
            else
                kubectl delete pvc --all -n "$NAMESPACE"
                log_success "PVCs deleted"
            fi
        else
            log_info "No PVCs found"
        fi
    fi
}

# Main execution
main() {
    log_info "Starting cleanup for Todo App Phase IV..."
    echo ""

    parse_args "$@"

    # Display current status
    display_status
    echo ""

    local cleanup_failures=0

    # Step 1: Uninstall Helm chart
    if ! uninstall_helm_chart; then
        cleanup_failures=$((cleanup_failures + 1))
    fi
    echo ""

    # Step 2: Delete PVCs (if namespace not being deleted)
    if [ "$DELETE_NAMESPACE" = false ]; then
        delete_pvcs
        echo ""
    fi

    # Step 3: Delete namespace (if requested)
    if [ "$DELETE_NAMESPACE" = true ]; then
        if ! delete_namespace; then
            cleanup_failures=$((cleanup_failures + 1))
        fi
        echo ""
    fi

    # Step 4: Stop Minikube (if requested)
    if [ "$STOP_MINIKUBE" = true ]; then
        if ! stop_minikube; then
            cleanup_failures=$((cleanup_failures + 1))
        fi
        echo ""
    fi

    # Summary
    if [ $cleanup_failures -eq 0 ]; then
        log_success "=== Cleanup completed successfully ==="

        if [ "$DELETE_NAMESPACE" = false ] && [ "$STOP_MINIKUBE" = false ]; then
            echo ""
            log_info "Next steps:"
            echo "  - To delete namespace: $0 --delete-namespace"
            echo "  - To stop Minikube: $0 --stop-minikube"
            echo "  - To redeploy: ./phaseIV/kubernetes/scripts/deploy.sh"
        elif [ "$STOP_MINIKUBE" = false ]; then
            echo ""
            log_info "Minikube is still running"
            echo "  - To stop Minikube: $0 --stop-minikube"
            echo "  - To redeploy: ./phaseIV/kubernetes/scripts/deploy.sh"
        else
            echo ""
            log_info "Complete cleanup finished"
            echo "  - To restart: ./phaseIV/kubernetes/scripts/setup-minikube.sh"
        fi

        return 0
    else
        log_error "=== Cleanup completed with $cleanup_failures error(s) ==="
        return 1
    fi
}

# Run main function
main "$@"
