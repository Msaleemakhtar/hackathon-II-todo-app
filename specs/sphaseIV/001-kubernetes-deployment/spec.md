# Feature Specification: Kubernetes Deployment for Phase IV Todo Chatbot

**Feature Branch**: `001-kubernetes-deployment`
**Created**: 2025-12-26
**Status**: Draft
**Phase**: IV (Kubernetes Deployment)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Local Kubernetes Cluster Deployment (Priority: P1)

As a developer or DevOps engineer, I want to deploy the Phase III containerized Todo Chatbot to a local Kubernetes cluster using Minikube so that I can validate the application works in a production-like orchestrated environment before cloud deployment.

**Why this priority**: Core infrastructure deployment is the foundation for all production features. Without this, no other Kubernetes features can be tested or demonstrated.

**Independent Test**: Deploy Helm chart to fresh Minikube cluster, verify all 4 services (frontend, backend, mcp-server, redis) have pods in Running state, and confirm basic connectivity between services via ClusterIP DNS.

**Acceptance Scenarios**:

1. **Given** a fresh Minikube cluster with 4 CPU and 8GB RAM, **When** I run `helm install todo-app ./helm/todo-app -n todo-phaseiv --create-namespace`, **Then** all 4 deployments (frontend, backend, mcp-server, redis) are created successfully within 5 minutes
2. **Given** all pods are running, **When** I execute `kubectl get pods -n todo-phaseiv`, **Then** the output shows 4 pods with status "Running" and 0 restarts
3. **Given** services are deployed, **When** I check `kubectl get svc -n todo-phaseiv`, **Then** I see ClusterIP services for frontend (port 3000), backend (port 8000), mcp-server (port 8001), and redis (port 6379)
4. **Given** services are running, **When** backend pod attempts to connect to redis via internal DNS (redis-service.todo-phaseiv.svc.cluster.local:6379), **Then** connection succeeds and Redis responds to PING command
5. **Given** services are running, **When** backend pod attempts to connect to external Neon PostgreSQL database using DATABASE_URL from Kubernetes Secret, **Then** database connection succeeds and migrations can be applied

---

### User Story 2 - Ingress-Based HTTP Routing (Priority: P2)

As a developer, I want to access the frontend and backend services through a single domain (todo-app.local) with path-based routing so that I can simulate a production-like HTTP routing setup and test the complete user flow from a browser.

**Why this priority**: Ingress provides the critical HTTP entry point for user interaction. Without this, the application cannot be accessed from outside the cluster, making end-to-end testing impossible.

**Independent Test**: Configure /etc/hosts to point todo-app.local to Minikube IP, deploy Nginx Ingress Controller, verify `curl http://todo-app.local/` returns frontend HTML and `curl http://todo-app.local/api/health` returns backend health check JSON.

**Acceptance Scenarios**:

1. **Given** Nginx Ingress Controller is installed in Minikube, **When** I run `kubectl get ingressclass`, **Then** I see "nginx" ingress class in the output
2. **Given** Ingress resource is deployed, **When** I execute `kubectl get ingress -n todo-phaseiv`, **Then** I see todo-app-ingress with host "todo-app.local" and paths configured for "/" and "/api"
3. **Given** /etc/hosts contains entry "192.168.49.2 todo-app.local" (Minikube IP), **When** I browse to http://todo-app.local/, **Then** the browser displays the Phase III frontend chat interface
4. **Given** frontend is accessible, **When** I send HTTP GET to http://todo-app.local/api/health, **Then** I receive HTTP 200 with JSON response `{"status": "healthy"}`
5. **Given** Ingress routing is configured, **When** I send HTTP POST to http://todo-app.local/api/{user_id}/chat with valid JWT token and message, **Then** I receive HTTP 200 with AI-generated response containing tool call information

---

### User Story 3 - Horizontal Pod Autoscaling (Priority: P2)

As a DevOps engineer, I want frontend and backend services to automatically scale from 2 to 5 replicas based on CPU and memory usage so that the application can handle variable traffic loads without manual intervention.

**Why this priority**: Autoscaling is a critical production feature that demonstrates Kubernetes' ability to handle dynamic workloads. This validates the application's readiness for production traffic patterns.

**Independent Test**: Start with 2 frontend replicas, generate load using Apache Bench (500 requests/second), verify HPA scales frontend to 5 replicas within 2 minutes as CPU exceeds 70% threshold.

**Acceptance Scenarios**:

1. **Given** Metrics Server is enabled in Minikube, **When** I run `kubectl top nodes`, **Then** I see CPU and memory usage statistics for Minikube cluster nodes
2. **Given** HPA resources are deployed, **When** I execute `kubectl get hpa -n todo-phaseiv`, **Then** I see HPA for frontend (min: 2, max: 5, target CPU: 70%) and backend (min: 2, max: 5, target CPU: 70%, memory: 80%)
3. **Given** frontend has 2 replicas at idle, **When** I generate load with `ab -n 5000 -c 50 http://todo-app.local/`, **Then** HPA detects CPU usage exceeds 70% and scales frontend to 3+ replicas within 60 seconds
4. **Given** frontend is scaled to 5 replicas under load, **When** load stops and CPU drops below 70% for 5 minutes, **Then** HPA scales down frontend to 2 replicas (down-scale stabilization)
5. **Given** backend experiences high memory usage (>80%), **When** HPA evaluates metrics every 15 seconds, **Then** backend scales from 2 to required replicas based on memory target

---

### User Story 4 - Persistent Storage for Redis (Priority: P2)

As a developer, I want Redis data to persist across pod restarts and deletions so that session data and cache entries are not lost when pods are rescheduled or updated.

**Why this priority**: Data persistence is critical for production readiness. Without this, every pod restart would lose all Redis data, breaking session management and caching functionality.

**Independent Test**: Write test key to Redis, forcefully delete Redis pod with `kubectl delete pod`, verify PVC remains bound and new Redis pod mounts same volume with test key still present.

**Acceptance Scenarios**:

1. **Given** Redis StatefulSet is deployed, **When** I execute `kubectl get pvc -n todo-phaseiv`, **Then** I see redis-data-pvc with status "Bound" and capacity 1Gi
2. **Given** Redis pod is running, **When** I exec into pod and write key `SET test-key "persistence-test"`, **Then** Redis confirms with "+OK"
3. **Given** test key is written, **When** I delete Redis pod with `kubectl delete pod redis-0 -n todo-phaseiv`, **Then** Kubernetes recreates pod automatically within 30 seconds
4. **Given** Redis pod is recreated, **When** I exec into new pod and execute `GET test-key`, **Then** Redis returns "persistence-test" (data persisted)
5. **Given** PVC is bound, **When** I inspect PVC with `kubectl describe pvc redis-data-pvc -n todo-phaseiv`, **Then** I see volume mounted at /data with RWO (ReadWriteOnce) access mode

---

### User Story 5 - Health Monitoring with Probes (Priority: P2)

As a DevOps engineer, I want all services to have liveness and readiness probes configured so that Kubernetes can automatically detect unhealthy pods and restart them, ensuring high availability.

**Why this priority**: Health probes are essential for production reliability. They enable Kubernetes to self-heal and prevent traffic from being routed to unhealthy pods.

**Independent Test**: Configure liveness probe to check /health endpoint every 10 seconds, simulate backend crash by killing FastAPI process, verify Kubernetes detects failure and restarts pod automatically.

**Acceptance Scenarios**:

1. **Given** all deployments are configured with health probes, **When** I run `kubectl describe pod <frontend-pod> -n todo-phaseiv`, **Then** I see liveness probe configured for HTTP GET /health on port 3000 with initialDelaySeconds: 10, periodSeconds: 10
2. **Given** backend pod is running, **When** readiness probe executes HTTP GET to http://localhost:8000/health, **Then** probe succeeds with HTTP 200 and pod is marked Ready in `kubectl get pods` output
3. **Given** frontend pod crashes (simulated by killing Next.js process), **When** liveness probe fails 3 consecutive times (failureThreshold: 3), **Then** Kubernetes restarts the container automatically and pod status shows restarts count incremented
4. **Given** Redis pod is starting, **When** readiness probe executes `redis-cli ping` before Redis is fully initialized, **Then** probe fails and pod remains NotReady, preventing traffic routing until probe succeeds
5. **Given** MCP server pod is healthy, **When** liveness probe checks HTTP GET http://localhost:8001/health every 10 seconds, **Then** probe succeeds continuously and pod maintains Running status without restarts

---

### User Story 6 - Secrets and Configuration Management (Priority: P2)

As a developer, I want sensitive data (database credentials, API keys) stored in Kubernetes Secrets and non-sensitive configuration in ConfigMaps so that I can follow security best practices and easily manage environment-specific settings.

**Why this priority**: Proper secrets management is mandatory for production security. Storing credentials in plain YAML files violates security principles and constitutional requirements.

**Independent Test**: Create Kubernetes Secret with DATABASE_URL and OPENAI_API_KEY, deploy backend referencing these secrets as environment variables, verify backend successfully connects to database and makes OpenAI API calls.

**Acceptance Scenarios**:

1. **Given** secrets are defined in Helm chart, **When** I run `helm install` with values.yaml containing base64-encoded secrets, **Then** Kubernetes creates Secret resource "todo-app-secrets" in todo-phaseiv namespace
2. **Given** Secret exists, **When** I execute `kubectl get secrets -n todo-phaseiv`, **Then** I see todo-app-secrets with keys: DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET, BETTER_AUTH_URL, REDIS_PASSWORD
3. **Given** backend deployment references secrets, **When** I inspect pod environment variables with `kubectl exec <backend-pod> -n todo-phaseiv -- env`, **Then** I see DATABASE_URL populated from secretKeyRef and value is not visible in plain text in deployment YAML
4. **Given** ConfigMap is created with non-sensitive config, **When** I run `kubectl get configmap -n todo-phaseiv`, **Then** I see todo-app-config with keys: REDIS_HOST, REDIS_PORT, MCP_SERVER_URL, NEXT_PUBLIC_API_URL
5. **Given** secrets are rotated (new database password), **When** I update Secret and restart backend pods, **Then** backend successfully connects to database with new credentials without downtime

---

### User Story 7 - Complete End-to-End User Flow (Priority: P1)

As a developer, I want to verify that the complete user journey (signup, login, chat, task creation via MCP tools) works correctly in the Kubernetes environment so that I can confirm all services are properly integrated and functional.

**Why this priority**: End-to-end validation proves the entire system works as expected in Kubernetes. This is the ultimate success criterion for Phase IV deployment.

**Independent Test**: Access frontend at http://todo-app.local, create new user account, log in, send chat message "Add task to buy groceries", verify MCP tool is invoked and task is created in Neon PostgreSQL database.

**Acceptance Scenarios**:

1. **Given** all services are deployed and healthy, **When** I navigate to http://todo-app.local/auth/register, **Then** I see the signup form and can create a new user account successfully
2. **Given** user account exists, **When** I navigate to http://todo-app.local/auth/login and submit credentials, **Then** I receive JWT token from Better Auth and am redirected to /chat page
3. **Given** user is authenticated, **When** I send chat message "Add task to buy groceries" in the ChatKit interface, **Then** backend receives message, invokes MCP tool add_task, and returns AI response confirming task creation
4. **Given** chat message is sent, **When** I send follow-up message "Show me all my tasks", **Then** MCP tool list_tasks is invoked and AI responds with list containing "Buy groceries" task
5. **Given** task is created, **When** I query Neon PostgreSQL database directly with `SELECT * FROM tasks_phaseiii WHERE user_id = '<test-user-id>'`, **Then** I see task record with title "Buy groceries" and completed = false

---

### User Story 8 - Deployment Automation and Testing (Priority: P3)

As a DevOps engineer, I want automated deployment scripts and comprehensive test suites so that I can quickly deploy to fresh Minikube clusters and validate all production features without manual intervention.

**Why this priority**: Automation improves deployment speed and reliability. While important for operational excellence, the system can function without full automation (manual deployment is acceptable for MVP).

**Independent Test**: Run `./scripts/setup-minikube.sh` on clean machine, then `./scripts/deploy.sh`, then `./scripts/test.sh`, verify all tests pass and application is fully functional without any manual steps.

**Acceptance Scenarios**:

1. **Given** Minikube is not installed, **When** I run `./scripts/setup-minikube.sh`, **Then** script installs Minikube, kubectl, Helm, starts cluster with 4 CPU 8GB RAM, enables ingress and metrics-server addons
2. **Given** Minikube cluster is ready, **When** I run `./scripts/deploy.sh`, **Then** script installs Helm chart in incremental order (Redis → MCP → Backend → Frontend → Ingress) and validates each component before proceeding
3. **Given** deployment is complete, **When** I run `./scripts/test.sh`, **Then** script executes all test suites: helm test, E2E test, load test, resilience test, persistence test, ingress test
4. **Given** load test executes, **When** script generates 500 requests/second for 2 minutes, **Then** HPA scales frontend/backend and script validates scaling occurred correctly
5. **Given** resilience test executes, **When** script deletes random pods (frontend, backend, mcp, redis), **Then** Kubernetes recreates pods automatically and script validates all services recover to healthy state

---

### User Story 9 - Comprehensive Operational Documentation (Priority: P3)

As a new team member or operator, I want detailed documentation (KUBERNETES_GUIDE.md, RUNBOOK.md, Helm README.md) so that I can understand the architecture, perform common operational tasks, and troubleshoot issues without extensive prior knowledge.

**Why this priority**: Documentation is critical for long-term maintainability and knowledge transfer. However, the system can function without perfect documentation (though operational efficiency suffers).

**Independent Test**: Give KUBERNETES_GUIDE.md to developer with no Kubernetes experience, verify they can successfully deploy application to Minikube following step-by-step instructions without external help.

**Acceptance Scenarios**:

1. **Given** KUBERNETES_GUIDE.md exists at phaseIV/kubernetes/docs/, **When** I open the file, **Then** I see comprehensive sections covering: prerequisites, Minikube setup, Helm installation, deployment steps, testing procedures, troubleshooting
2. **Given** RUNBOOK.md exists, **When** I search for "how to scale replicas", **Then** I find clear instructions with exact kubectl command: `kubectl scale deployment frontend -n todo-phaseiv --replicas=3`
3. **Given** Helm README.md exists at helm/todo-app/, **When** I open the file, **Then** I see chart description, requirements, installation instructions, configuration values documentation, and examples
4. **Given** architecture diagram exists in documentation, **When** I view the diagram, **Then** I see visual representation of all 4 services, Ingress, PVC, external database, with arrows showing network flow
5. **Given** troubleshooting section exists in RUNBOOK.md, **When** I search for common issues (pods stuck in Pending, Ingress not routing, HPA not scaling), **Then** I find diagnostic steps and resolution procedures for each issue

---

### Edge Cases

- **What happens when Minikube cluster runs out of resources (CPU/memory exhausted)?**
  - Expected: Pods enter Pending state with "Insufficient cpu" or "Insufficient memory" error in `kubectl describe pod`. HPA cannot scale beyond available resources. Documentation guides operator to either reduce resource requests or increase cluster resources with `minikube config set cpus 8; minikube config set memory 16384`.

- **How does system handle Helm chart upgrade failures (e.g., invalid values.yaml)?**
  - Expected: `helm upgrade` fails with validation error, deployment remains on previous working version. Operator runs `helm rollback todo-app` to restore known-good state. Chart includes pre-upgrade hooks to validate critical configuration before applying changes.

- **What happens when external Neon PostgreSQL database is unreachable?**
  - Expected: Backend pods fail readiness probes (database health check fails), remain in NotReady state. Ingress stops routing /api traffic to unhealthy pods. Liveness probes continue succeeding (process is running), preventing pod restarts. When database connectivity restores, readiness probes succeed and traffic resumes automatically.

- **How does system handle Redis StatefulSet deletion without deleting PVC?**
  - Expected: `kubectl delete statefulset redis` removes pods but leaves PVC intact. Redeploying StatefulSet (via `helm upgrade` or `kubectl apply`) creates new pods that mount existing PVC, restoring all data. Data loss only occurs if PVC is explicitly deleted.

- **What happens when user sends too many requests and triggers rate limiting?**
  - Expected: (Rate limiting is out of scope for Phase IV - handled at application level, not Kubernetes level). Application returns HTTP 429 Too Many Requests. Multiple replicas distribute load across pods, reducing per-pod request rate.

- **How does system handle pod eviction due to node pressure (disk, memory, PID)?**
  - Expected: Kubernetes evicts pods starting with lowest QoS class (BestEffort first, Burstable second, Guaranteed last). All Phase IV pods have resource requests and limits defined, ensuring Burstable or Guaranteed QoS. Evicted pods are rescheduled automatically on healthy nodes.

- **What happens when Ingress Controller pod is deleted or crashes?**
  - Expected: Kubernetes recreates Ingress Controller pod automatically (it's a deployment with replicas). During brief downtime (typically <30 seconds), http://todo-app.local becomes unreachable with "Connection refused" or timeout errors. Once pod is Running, traffic resumes automatically without manual intervention.

- **How does system handle helm install with conflicting resource names already existing in namespace?**
  - Expected: `helm install` fails with error "already exists" for conflicting resources. Operator must either: (1) delete existing resources manually, (2) use `helm upgrade --install` to update existing resources, or (3) choose different release name to avoid conflicts.

## Requirements *(mandatory)*

### Functional Requirements

#### Core Infrastructure (P1)
- **FR-001**: System MUST deploy Minikube cluster with minimum 4 CPU cores and 8GB RAM
- **FR-002**: System MUST create Kubernetes namespace "todo-phaseiv" for all Phase IV resources
- **FR-003**: System MUST deploy 4 services as Kubernetes resources: Frontend (Deployment), Backend (Deployment), MCP Server (Deployment), Redis (StatefulSet)
- **FR-004**: Frontend deployment MUST use Docker image built from phaseIV/frontend with Next.js runtime
- **FR-005**: Backend deployment MUST use Docker image built from phaseIV/backend with FastAPI + Uvicorn runtime
- **FR-006**: MCP Server deployment MUST use Docker image built from phaseIV/backend/mcp with FastMCP HTTP server
- **FR-007**: Redis StatefulSet MUST use official Redis 7 Alpine image with persistence enabled
- **FR-008**: System MUST create ClusterIP services for all 4 components to enable internal DNS-based service discovery
- **FR-009**: Backend MUST successfully connect to external Neon PostgreSQL database using DATABASE_URL from Kubernetes Secret
- **FR-010**: All 4 services MUST reach "Running" status within 5 minutes of `helm install` command on healthy cluster

#### Networking and Ingress (P2)
- **FR-011**: System MUST install Nginx Ingress Controller in Minikube cluster
- **FR-012**: System MUST create Ingress resource with host "todo-app.local"
- **FR-013**: Ingress MUST route path "/" to frontend service on port 3000
- **FR-014**: Ingress MUST route path "/api" to backend service on port 8000
- **FR-015**: HTTP request to http://todo-app.local/ MUST return frontend HTML with HTTP 200 status
- **FR-016**: HTTP request to http://todo-app.local/api/health MUST return backend health check JSON with HTTP 200 status
- **FR-017**: Ingress MUST preserve path for backend API calls (e.g., /api/{user_id}/chat routes to backend with full path)

#### Autoscaling (P2)
- **FR-018**: System MUST enable Metrics Server addon in Minikube for HPA functionality
- **FR-019**: System MUST create HorizontalPodAutoscaler for frontend deployment with min: 2, max: 5 replicas
- **FR-020**: Frontend HPA MUST scale based on CPU utilization target of 70%
- **FR-021**: System MUST create HorizontalPodAutoscaler for backend deployment with min: 2, max: 5 replicas
- **FR-022**: Backend HPA MUST scale based on CPU utilization target of 70% AND memory utilization target of 80%
- **FR-023**: When frontend CPU exceeds 70% for 30 seconds, HPA MUST scale up by adding 1 replica (up to max 5)
- **FR-024**: When frontend CPU drops below 70% for 5 minutes, HPA MUST scale down by removing 1 replica (down to min 2)

#### Persistent Storage (P2)
- **FR-025**: System MUST create PersistentVolumeClaim named "redis-data-pvc" with 1Gi capacity
- **FR-026**: PVC MUST use standard StorageClass (Minikube default hostPath provisioner)
- **FR-027**: PVC MUST request ReadWriteOnce (RWO) access mode
- **FR-028**: Redis StatefulSet MUST mount PVC at /data directory inside container
- **FR-029**: Redis MUST persist data to mounted volume using AOF (Append-Only File) persistence
- **FR-030**: Data written to Redis MUST survive pod deletion and recreation (PVC remains bound to new pod)

#### Health Monitoring (P2)
- **FR-031**: All deployments MUST configure liveness probes to detect crashed containers
- **FR-032**: All deployments MUST configure readiness probes to control traffic routing
- **FR-033**: Frontend liveness probe MUST check HTTP GET /health on port 3000 every 10 seconds
- **FR-034**: Backend liveness probe MUST check HTTP GET /health on port 8000 every 10 seconds
- **FR-035**: MCP Server liveness probe MUST check HTTP GET /health on port 8001 every 10 seconds
- **FR-036**: Redis liveness probe MUST execute `redis-cli ping` command every 10 seconds
- **FR-037**: Readiness probes MUST use same endpoints/commands as liveness probes
- **FR-038**: Probes MUST have initialDelaySeconds: 10, periodSeconds: 10, timeoutSeconds: 5, failureThreshold: 3
- **FR-039**: When liveness probe fails 3 consecutive times, Kubernetes MUST restart the container automatically
- **FR-040**: When readiness probe fails, Kubernetes MUST remove pod from service endpoints (stop routing traffic)

#### Configuration Management (P2)
- **FR-041**: System MUST create Kubernetes Secret named "todo-app-secrets" containing: DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET, BETTER_AUTH_URL, REDIS_PASSWORD
- **FR-042**: System MUST create ConfigMap named "todo-app-config" containing: REDIS_HOST, REDIS_PORT, MCP_SERVER_URL, NEXT_PUBLIC_API_URL
- **FR-043**: All deployments MUST inject secrets as environment variables using secretKeyRef
- **FR-044**: All deployments MUST inject ConfigMap values as environment variables using configMapKeyRef
- **FR-045**: Secrets MUST NOT be visible in plain text in Helm templates or deployed YAML manifests
- **FR-046**: Helm chart MUST support external secrets management (values.yaml allows base64-encoded secrets input)

#### Resource Management (P2)
- **FR-047**: Frontend deployment MUST specify CPU request: 500m, CPU limit: 1000m (1.0 CPU)
- **FR-048**: Frontend deployment MUST specify memory request: 512Mi, memory limit: 1024Mi (1GB RAM)
- **FR-049**: Backend deployment MUST specify CPU request: 500m, CPU limit: 1000m
- **FR-050**: Backend deployment MUST specify memory request: 512Mi, memory limit: 1024Mi
- **FR-051**: MCP Server deployment MUST specify CPU request: 250m, CPU limit: 500m (0.5 CPU)
- **FR-052**: MCP Server deployment MUST specify memory request: 256Mi, memory limit: 512Mi
- **FR-053**: Redis StatefulSet MUST specify CPU request: 250m, CPU limit: 500m
- **FR-054**: Redis StatefulSet MUST specify memory request: 128Mi, memory limit: 256Mi
- **FR-055**: All pods MUST have QoS class of "Burstable" or "Guaranteed" (never BestEffort)

#### End-to-End Functionality (P1)
- **FR-056**: User MUST be able to access frontend at http://todo-app.local/ and see signup/login pages
- **FR-057**: User MUST be able to create account via Better Auth signup form
- **FR-058**: User MUST be able to log in and receive JWT token for authenticated requests
- **FR-059**: Authenticated user MUST be able to access chat interface at http://todo-app.local/chat
- **FR-060**: User MUST be able to send chat message and receive AI-generated response from backend
- **FR-061**: Chat message "Add task to buy groceries" MUST invoke MCP tool add_task and create task in Neon PostgreSQL database
- **FR-062**: Chat message "Show me all my tasks" MUST invoke MCP tool list_tasks and return user's tasks in AI response
- **FR-063**: All 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task) MUST be functional in Kubernetes environment

### Key Entities

- **Kubernetes Cluster**: Local Minikube cluster with 4 CPU, 8GB RAM, running Kubernetes v1.28+
- **Namespace**: todo-phaseiv namespace isolating all Phase IV resources
- **Helm Chart**: Package named "todo-app" containing 20+ YAML templates for all Kubernetes resources
- **Deployments**: Frontend, Backend, MCP Server (stateless workloads with replica management)
- **StatefulSet**: Redis (stateful workload with stable network identity and persistent storage)
- **Services**: ClusterIP services for internal communication (frontend-service, backend-service, mcp-service, redis-service)
- **Ingress**: Nginx Ingress resource routing HTTP traffic from todo-app.local to appropriate services
- **HorizontalPodAutoscaler**: HPA resources for frontend and backend enabling dynamic replica scaling
- **PersistentVolumeClaim**: redis-data-pvc providing 1Gi persistent storage for Redis data
- **Secret**: todo-app-secrets storing sensitive configuration (database credentials, API keys)
- **ConfigMap**: todo-app-config storing non-sensitive configuration (service URLs, ports)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 4 services (frontend, backend, mcp-server, redis) have pods in Running state within 5 minutes of `helm install todo-app -n todo-phaseiv --create-namespace`
  - Verification: `kubectl get pods -n todo-phaseiv` shows 4 pods with STATUS=Running and READY showing all containers ready (e.g., 1/1, 2/2)

- **SC-002**: HTTP request to http://todo-app.local/ returns frontend page with HTTP 200 status code
  - Verification: `curl -s -o /dev/null -w "%{http_code}" http://todo-app.local/` outputs "200"

- **SC-003**: HTTP request to http://todo-app.local/api/health returns backend health check with HTTP 200 status code and JSON body `{"status": "healthy"}`
  - Verification: `curl http://todo-app.local/api/health` returns HTTP 200 with JSON response

- **SC-004**: Redis pod restart retains data (verified by writing key before restart, reading key after restart)
  - Verification: Execute `kubectl exec redis-0 -n todo-phaseiv -- redis-cli SET test-key "persistence-test"`, then `kubectl delete pod redis-0 -n todo-phaseiv`, wait for pod to restart, execute `kubectl exec redis-0 -n todo-phaseiv -- redis-cli GET test-key` and verify output is "persistence-test"

- **SC-005**: Load test generating 500 requests/second triggers HPA to scale frontend from 2 to 5 replicas within 2 minutes
  - Verification: Baseline with `kubectl get hpa frontend-hpa -n todo-phaseiv` showing 2 current replicas, execute `ab -n 10000 -c 50 http://todo-app.local/` to generate load, after 2 minutes `kubectl get hpa frontend-hpa -n todo-phaseiv` shows 3-5 current replicas

- **SC-006**: Complete user flow (signup → login → chat → create task via MCP) completes successfully in Kubernetes environment
  - Verification: Navigate to http://todo-app.local/auth/register, create account with email "test@example.com", log in, navigate to /chat, send message "Add task to buy groceries", verify AI response confirms task creation, query database `SELECT * FROM tasks_phaseiii WHERE user_id = '<test-user-id>'` and verify task exists

- **SC-007**: `helm test todo-app -n todo-phaseiv` passes all validation tests with 0 failures
  - Verification: Execute `helm test todo-app -n todo-phaseiv` and verify output shows "Phase: Succeeded" for all test pods

- **SC-008**: `helm lint ./helm/todo-app` passes with 0 errors and 0 warnings
  - Verification: Execute `helm lint ./helm/todo-app` from phaseIV/kubernetes directory and verify output shows "0 chart(s) linted, 0 chart(s) failed"

- **SC-009**: All deployments have resource limits defined and QoS class is Burstable or Guaranteed (not BestEffort)
  - Verification: `kubectl describe pod <any-pod> -n todo-phaseiv | grep "QoS Class"` shows "Burstable" or "Guaranteed", never "BestEffort"

- **SC-010**: Comprehensive documentation (KUBERNETES_GUIDE.md, RUNBOOK.md, Helm README.md) exists and enables new developer to deploy application without external assistance
  - Verification: Provide documentation to developer with no Kubernetes experience, measure time to successful deployment (<30 minutes), verify no questions asked during deployment process

## Assumptions *(documented)*

### Infrastructure Assumptions
1. **Minikube Installation**: User has Minikube v1.32+ installed or will install via provided setup script
2. **Docker Desktop**: Docker Desktop is running and accessible to Minikube for image building and container runtime
3. **kubectl Version**: kubectl v1.28+ is installed and configured to communicate with Minikube cluster
4. **Helm Version**: Helm v3.13+ is installed for chart management
5. **System Resources**: Host machine has minimum 6 CPU cores and 12GB RAM available (4 CPU + 8GB allocated to Minikube, remainder for host OS)
6. **Network Connectivity**: Host machine can reach external services (Neon PostgreSQL on neon.tech, OpenAI API on api.openai.com)
7. **DNS Resolution**: User has permissions to modify /etc/hosts file for local DNS entry (todo-app.local → Minikube IP)

### Kubernetes Configuration Assumptions
8. **Ingress Addon**: Minikube ingress addon is enabled via `minikube addons enable ingress`
9. **Metrics Server Addon**: Minikube metrics-server addon is enabled via `minikube addons enable metrics-server`
10. **StorageClass**: Minikube provides standard StorageClass with hostPath provisioner for PersistentVolumes
11. **Default Service Account**: Default service account in todo-phaseiv namespace has sufficient permissions for basic pod operations (no custom RBAC required)
12. **Image Pull Policy**: IfNotPresent is used to avoid pulling images if they exist locally (images built locally with Minikube Docker daemon)

### Application Configuration Assumptions
13. **Neon PostgreSQL**: Database instance from Phase III remains available and accessible (same DATABASE_URL works in Kubernetes environment)
14. **Database Tables**: Phase III database migrations have been applied and tables (tasks_phaseiii, conversations, messages) exist
15. **Better Auth Configuration**: BETTER_AUTH_URL and BETTER_AUTH_SECRET from Phase III work without changes in Kubernetes
16. **OpenAI API Key**: Valid OPENAI_API_KEY is provided in Helm values or Kubernetes Secret
17. **Redis Password**: Redis password (if required) is configured in Secret and matches backend configuration

### Helm Chart Assumptions
18. **Chart Version**: Initial Helm chart version is 0.1.0 following SemVer
19. **Release Name**: Default Helm release name is "todo-app" (user can override with `--name` flag)
20. **Namespace Creation**: Namespace todo-phaseiv will be created automatically via `--create-namespace` flag or must exist before `helm install`
21. **Values Override**: Users can override any chart value via custom values.yaml or `--set` flags during installation

### Operational Assumptions
22. **Deployment Order**: Services must be deployed in specific order to satisfy dependencies: Redis → MCP Server → Backend → Frontend → Ingress
23. **Startup Time**: Backend requires database connectivity before becoming Ready; maximum 60 seconds allowed for initial startup
24. **Health Check Endpoints**: All services implement /health endpoint returning HTTP 200 when healthy
25. **Log Access**: Operators use `kubectl logs` for troubleshooting (no centralized logging aggregation in Phase IV)
26. **Backup Strategy**: PersistentVolume provides basic data persistence; full backup/restore procedures are out of scope for Phase IV

### Testing Assumptions
27. **Test Environment**: All tests run on same Minikube cluster (no separate staging environment)
28. **Test Data**: Test suite creates and cleans up test data; no persistent test data between test runs
29. **Load Testing Tool**: Apache Bench (ab) is used for load testing and is installed on host machine
30. **Test Isolation**: Tests can run concurrently without interfering with each other (use separate user accounts for isolation)

## Out of Scope *(explicitly excluded)*

### Deferred to Phase V (Future Cloud Deployment)
1. **Cloud Kubernetes Providers**: DigitalOcean Kubernetes (DOKS), Google Kubernetes Engine (GKE), Azure Kubernetes Service (AKS), Amazon EKS
2. **CI/CD Pipelines**: Automated deployment pipelines, GitOps workflows (ArgoCD, FluxCD), GitHub Actions workflows for Kubernetes
3. **TLS/SSL Certificates**: HTTPS configuration, cert-manager, Let's Encrypt integration, certificate rotation
4. **External DNS**: Automatic DNS record creation, external-dns controller, DNS-based service discovery
5. **Prometheus/Grafana Monitoring**: Full observability stack, custom metrics, dashboards, alerting rules
6. **Centralized Logging**: ELK stack (Elasticsearch, Logstash, Kibana), Loki, log aggregation, log retention policies

### Production Features Beyond MVP
7. **Network Policies**: Pod-to-pod traffic restrictions, namespace isolation, egress/ingress rules
8. **RBAC Customization**: Custom ServiceAccounts, Roles, RoleBindings, ClusterRoles for fine-grained permissions
9. **Pod Security Policies/Standards**: Pod security admission, security contexts enforcement, privileged container restrictions
10. **Multi-Environment Deployments**: Separate dev/staging/production environments, environment promotion workflows
11. **Blue-Green Deployments**: Zero-downtime deployment strategies, traffic splitting, canary releases
12. **Service Mesh**: Istio, Linkerd, service-to-service encryption, advanced traffic management

### Advanced Kubernetes Features
13. **Custom Resource Definitions (CRDs)**: Operators, custom controllers, domain-specific resource types
14. **DaemonSets**: Node-level services (logging agents, monitoring agents, network plugins)
15. **Jobs and CronJobs**: Batch processing, scheduled tasks, database backup jobs
16. **Init Containers**: Pre-startup initialization, dependency waiting, configuration setup
17. **Multi-Zone/Multi-Region**: High availability across zones/regions, zone-aware scheduling, regional failover

### Integration and Messaging
18. **Kafka Integration**: Event streaming, message queues, event-driven architecture
19. **Dapr Integration**: Microservices building blocks, state management, pub/sub, service invocation
20. **External Service Discovery**: Consul, Eureka integration for hybrid cloud/on-prem service discovery

### Backup and Disaster Recovery
21. **Velero Backups**: Cluster-wide backup/restore, disaster recovery procedures, backup automation
22. **Database Backups**: Automated PostgreSQL backups, point-in-time recovery, backup verification
23. **Redis Clustering**: Redis Cluster mode, master-replica replication, automatic failover

### Advanced Autoscaling
24. **Vertical Pod Autoscaling (VPA)**: Automatic resource request/limit adjustment based on usage
25. **Cluster Autoscaling**: Automatic node scaling based on pod resource requirements (only relevant in cloud environments)
26. **Custom Metrics Autoscaling**: HPA based on application-specific metrics (e.g., queue length, request latency)

### Security Enhancements
27. **Secrets Encryption at Rest**: etcd encryption, KMS integration, external secret stores (HashiCorp Vault, AWS Secrets Manager)
28. **Image Scanning**: Container image vulnerability scanning, admission controllers blocking vulnerable images
29. **Runtime Security**: Falco, intrusion detection, runtime anomaly detection

### Cost Optimization
30. **Resource Quotas**: Namespace-level resource limits, LimitRanges, cost allocation tracking
31. **Pod Disruption Budgets**: Controlled voluntary disruptions, maintenance window management
32. **Spot/Preemptible Instances**: Cost optimization with interruptible compute (cloud-only feature)

## Technical Notes

### Helm Chart Structure
The Helm chart follows best practices with the following structure:
```
phaseIV/kubernetes/helm/todo-app/
├── Chart.yaml                      # Chart metadata (name, version, description)
├── values.yaml                     # Default configuration values
├── README.md                       # Chart documentation
├── templates/
│   ├── _helpers.tpl               # Template helpers and functions
│   ├── frontend-deployment.yaml   # Frontend Deployment
│   ├── frontend-service.yaml      # Frontend ClusterIP Service
│   ├── frontend-hpa.yaml          # Frontend HorizontalPodAutoscaler
│   ├── backend-deployment.yaml    # Backend Deployment
│   ├── backend-service.yaml       # Backend ClusterIP Service
│   ├── backend-hpa.yaml           # Backend HorizontalPodAutoscaler
│   ├── mcp-deployment.yaml        # MCP Server Deployment
│   ├── mcp-service.yaml           # MCP Server ClusterIP Service
│   ├── redis-statefulset.yaml     # Redis StatefulSet
│   ├── redis-service.yaml         # Redis ClusterIP Service
│   ├── redis-pvc.yaml             # Redis PersistentVolumeClaim
│   ├── ingress.yaml               # Nginx Ingress resource
│   ├── secret.yaml                # Kubernetes Secret (sensitive data)
│   ├── configmap.yaml             # ConfigMap (non-sensitive config)
│   └── tests/
│       ├── test-frontend.yaml     # Helm test for frontend health
│       ├── test-backend.yaml      # Helm test for backend health
│       ├── test-mcp.yaml          # Helm test for MCP server health
│       └── test-redis.yaml        # Helm test for Redis connectivity
└── .helmignore                     # Files to exclude from chart package
```

### Deployment Script Flow
The automated deployment script (`./scripts/deploy.sh`) follows this incremental rollout order:
1. **Validate Prerequisites**: Check Minikube is running, kubectl configured, Helm installed
2. **Build Docker Images**: Build frontend, backend, mcp-server images in Minikube Docker environment
3. **Install Redis**: Deploy Redis StatefulSet and PVC first (no dependencies)
4. **Verify Redis**: Wait for Redis pod to be Running and Ready (health probe succeeds)
5. **Install MCP Server**: Deploy MCP Server Deployment (depends on Redis for session storage if needed)
6. **Verify MCP**: Wait for MCP pod to be Running and Ready
7. **Install Backend**: Deploy Backend Deployment (depends on Redis and external PostgreSQL)
8. **Run Migrations**: Execute Alembic migrations via Kubernetes Job or backend init container
9. **Verify Backend**: Wait for Backend pods (2 replicas via HPA) to be Running and Ready
10. **Install Frontend**: Deploy Frontend Deployment (depends on Backend API availability)
11. **Verify Frontend**: Wait for Frontend pods (2 replicas via HPA) to be Running and Ready
12. **Install Ingress**: Deploy Nginx Ingress resource last (all backend services must exist before routing)
13. **Verify Ingress**: Wait for Ingress to receive IP address from Minikube Ingress Controller
14. **Run Helm Tests**: Execute `helm test` to validate all services are functional
15. **Display Access Information**: Print URL (http://todo-app.local) and /etc/hosts configuration instructions

### Resource Sizing Rationale
Resource requests and limits match Phase III Docker Compose configuration to ensure consistency across environments:
- **Frontend**: Next.js requires 512Mi-1Gi RAM for SSR and client-side hydration; 1 CPU handles typical load
- **Backend**: FastAPI + Uvicorn workers require 512Mi-1Gi RAM; 1 CPU sufficient for async I/O workloads
- **MCP Server**: Lightweight FastMCP server requires minimal resources; 256Mi-512Mi RAM, 0.5 CPU
- **Redis**: In-memory cache requires 128Mi-256Mi RAM for session storage; 0.5 CPU handles typical throughput
- **HPA Targets**: 70% CPU / 80% Memory thresholds provide headroom for traffic spikes before scaling

### Testing Strategy
Phase IV testing covers 6 categories:
1. **Helm Tests**: Built-in chart tests validating service health endpoints
2. **E2E Tests**: Selenium/Playwright tests covering complete user journey (signup → chat → task CRUD)
3. **Load Tests**: Apache Bench generating sustained load to validate HPA scaling behavior
4. **Resilience Tests**: Pod deletion tests validating Kubernetes self-healing and automatic restart
5. **Persistence Tests**: Redis data retention tests validating PVC functionality across pod lifecycle
6. **Ingress Tests**: HTTP routing tests validating path-based routing and host configuration

### Observability Approach
Phase IV uses basic Kubernetes-native observability:
- **Logs**: `kubectl logs <pod> -n todo-phaseiv -f` for real-time log streaming
- **Metrics**: `kubectl top pods -n todo-phaseiv` for CPU/memory usage (requires Metrics Server)
- **Events**: `kubectl get events -n todo-phaseiv --sort-by='.lastTimestamp'` for cluster events
- **Describe**: `kubectl describe pod <pod> -n todo-phaseiv` for detailed pod state and probe results
Advanced observability (Prometheus, Grafana, distributed tracing) is deferred to Phase V.

### Security Considerations
Phase IV follows constitutional security principles:
- **Secrets Management**: All sensitive data (DATABASE_URL, API keys) stored in Kubernetes Secrets, never in ConfigMaps or plain YAML
- **Non-Root Users**: All container images run as non-root users (nextjs:nodejs, appuser, mcpuser)
- **Resource Limits**: CPU/memory limits prevent resource exhaustion attacks and ensure fair resource allocation
- **Network Isolation**: Services use ClusterIP (internal only), only Ingress exposes HTTP externally
- **Image Provenance**: All images built locally from trusted source code, no third-party images except official Redis
Advanced security (NetworkPolicies, Pod Security Standards, image scanning) is deferred to Phase V.
