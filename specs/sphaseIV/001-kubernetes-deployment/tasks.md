# Tasks: Kubernetes Deployment for Phase IV Todo Chatbot

**Input**: Design documents from `/specs/001-kubernetes-deployment/`
**Prerequisites**: plan.md (technical stack), spec.md (user stories), research.md (decisions), data-model.md (entities), contracts/ (deployment contracts), quickstart.md (test scenarios)

**Tests**: Tests are OPTIONAL for this feature. This is an infrastructure deployment feature focused on Kubernetes manifests, deployment scripts, and operational documentation. Testing is primarily validation-based (Helm tests, E2E tests, load tests) rather than unit tests.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a Kubernetes deployment feature following Phase IV structure:
- **Helm charts**: `phaseIV/kubernetes/helm/todo-app/`
- **Deployment scripts**: `phaseIV/kubernetes/scripts/`
- **Documentation**: `phaseIV/kubernetes/docs/`
- **Source code**: `phaseIV/frontend/` and `phaseIV/backend/` (copied from Phase III)

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize Phase IV directory structure and prepare for Kubernetes deployment

- [X] T001 Create phaseIV directory structure (kubernetes/, frontend/, backend/) at repository root
- [X] T002 Copy Phase III frontend source code from root to phaseIV/frontend/ directory
- [X] T003 Copy Phase III backend source code from root to phaseIV/backend/ directory
- [X] T004 [P] Create phaseIV/kubernetes/helm/todo-app/ directory structure per Helm best practices
- [X] T005 [P] Create phaseIV/kubernetes/scripts/ directory for deployment automation
- [X] T006 [P] Create phaseIV/kubernetes/docs/ directory for operational documentation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Helm chart structure and shared configuration that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create Helm Chart.yaml with metadata (name: todo-app, version: 0.1.0, apiVersion: v2) in phaseIV/kubernetes/helm/todo-app/Chart.yaml
- [X] T008 Create Helm values.yaml with default configuration values in phaseIV/kubernetes/helm/todo-app/values.yaml
- [X] T009 Create Helm _helpers.tpl with template helpers (fullname, labels, selectorLabels) in phaseIV/kubernetes/helm/todo-app/templates/_helpers.tpl
- [X] T010 Create namespace.yaml template for todo-phaseiv namespace in phaseIV/kubernetes/helm/todo-app/templates/namespace.yaml
- [X] T011 Create secret.yaml template for Kubernetes Secret (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET) in phaseIV/kubernetes/helm/todo-app/templates/secret.yaml
- [X] T012 Create configmap.yaml template for ConfigMap (REDIS_HOST, REDIS_PORT, MCP_SERVER_URL, NEXT_PUBLIC_API_URL) in phaseIV/kubernetes/helm/todo-app/templates/configmap.yaml
- [X] T013 Create .helmignore file to exclude unnecessary files from Helm package in phaseIV/kubernetes/helm/todo-app/.helmignore

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Local Kubernetes Cluster Deployment (Priority: P1) 🎯 MVP

**Goal**: Deploy all 4 services (frontend, backend, mcp-server, redis) to Minikube cluster and verify basic connectivity

**Independent Test**: Deploy Helm chart to fresh Minikube cluster, verify all 4 services have pods in Running state, confirm basic connectivity via ClusterIP DNS

### Implementation for User Story 1

- [X] T014 [P] [US1] Create redis-statefulset.yaml template with Redis StatefulSet (1 replica, AOF persistence, exec probes) in phaseIV/kubernetes/helm/todo-app/templates/redis-statefulset.yaml
- [X] T015 [P] [US1] Create redis-service.yaml template with headless ClusterIP Service for Redis in phaseIV/kubernetes/helm/todo-app/templates/redis-service.yaml
- [X] T016 [P] [US1] Create redis-pvc.yaml template with PersistentVolumeClaim (1Gi, RWO, standard StorageClass) in phaseIV/kubernetes/helm/todo-app/templates/redis-pvc.yaml
- [X] T017 [P] [US1] Create mcp-deployment.yaml template with MCP Server Deployment (1 replica, 250m-500m CPU, 256Mi-512Mi RAM) in phaseIV/kubernetes/helm/todo-app/templates/mcp-deployment.yaml
- [X] T018 [P] [US1] Create mcp-service.yaml template with ClusterIP Service for MCP Server in phaseIV/kubernetes/helm/todo-app/templates/mcp-service.yaml
- [X] T019 [P] [US1] Create backend-deployment.yaml template with Backend Deployment (2 replicas, 500m-1000m CPU, 512Mi-1024Mi RAM, HTTP probes) in phaseIV/kubernetes/helm/todo-app/templates/backend-deployment.yaml
- [X] T020 [P] [US1] Create backend-service.yaml template with ClusterIP Service for Backend in phaseIV/kubernetes/helm/todo-app/templates/backend-service.yaml
- [X] T021 [P] [US1] Create frontend-deployment.yaml template with Frontend Deployment (2 replicas, 500m-1000m CPU, 512Mi-1024Mi RAM, HTTP probes) in phaseIV/kubernetes/helm/todo-app/templates/frontend-deployment.yaml
- [X] T022 [P] [US1] Create frontend-service.yaml template with ClusterIP Service for Frontend in phaseIV/kubernetes/helm/todo-app/templates/frontend-service.yaml
- [X] T023 [US1] Create setup-minikube.sh script to install Minikube, kubectl, Helm, start cluster (4 CPU, 8GB RAM), enable ingress and metrics-server addons in phaseIV/kubernetes/scripts/setup-minikube.sh
- [X] T024 [US1] Create deploy.sh script for incremental rollout (Redis → MCP → Backend → Frontend) with health validation gates in phaseIV/kubernetes/scripts/deploy.sh
- [X] T025 [US1] Create Helm test pods for validating service health (test-redis.yaml, test-mcp.yaml, test-backend.yaml, test-frontend.yaml) in phaseIV/kubernetes/helm/todo-app/templates/tests/
- [X] T026 [US1] Update CLAUDE.md to add Phase IV technologies (YAML, Helm 3.13+, Bash) and recent changes (001-kubernetes-deployment) in CLAUDE.md

**Checkpoint**: At this point, User Story 1 should be fully functional - all 4 services deployed and running in Minikube

---

## Phase 4: User Story 2 - Ingress-Based HTTP Routing (Priority: P2)

**Goal**: Enable external HTTP access to frontend and backend services through single domain (todo-app.local) with path-based routing

**Independent Test**: Configure /etc/hosts to point todo-app.local to Minikube IP, deploy Nginx Ingress Controller, verify `curl http://todo-app.local/` returns frontend HTML and `curl http://todo-app.local/api/health` returns backend health JSON

### Implementation for User Story 2

- [ ] T027 [US2] Create ingress.yaml template with Nginx Ingress resource (host: todo-app.local, paths: /api → backend, / → frontend) in phaseIV/kubernetes/helm/todo-app/templates/ingress.yaml
- [ ] T028 [US2] Update deploy.sh script to verify Nginx Ingress Controller is enabled in Minikube and display /etc/hosts configuration instructions in phaseIV/kubernetes/scripts/deploy.sh
- [ ] T029 [US2] Create test-ingress.sh script to validate HTTP routing (frontend route, backend route) in phaseIV/kubernetes/scripts/test-ingress.sh

**Checkpoint**: At this point, User Story 2 should work independently - HTTP access to application via todo-app.local domain

---

## Phase 5: User Story 3 - Horizontal Pod Autoscaling (Priority: P2)

**Goal**: Enable automatic scaling of frontend and backend services from 2 to 5 replicas based on CPU and memory usage

**Independent Test**: Start with 2 frontend replicas, generate load using Apache Bench (500 requests/second), verify HPA scales frontend to 5 replicas within 2 minutes as CPU exceeds 70% threshold

### Implementation for User Story 3

- [ ] T030 [P] [US3] Create frontend-hpa.yaml template with HorizontalPodAutoscaler (min: 2, max: 5, CPU target: 70%, scaleDown stabilization: 300s) in phaseIV/kubernetes/helm/todo-app/templates/frontend-hpa.yaml
- [ ] T031 [P] [US3] Create backend-hpa.yaml template with HorizontalPodAutoscaler (min: 2, max: 5, CPU target: 70%, memory target: 80%) in phaseIV/kubernetes/helm/todo-app/templates/backend-hpa.yaml
- [ ] T032 [US3] Update deploy.sh script to verify Metrics Server is enabled in Minikube before installing HPA resources in phaseIV/kubernetes/scripts/deploy.sh
- [ ] T033 [US3] Create test-load.sh script to generate load with Apache Bench and validate HPA scaling behavior in phaseIV/kubernetes/scripts/test-load.sh

**Checkpoint**: At this point, User Story 3 should work independently - HPA scales frontend and backend under load

---

## Phase 6: User Story 4 - Persistent Storage for Redis (Priority: P2)

**Goal**: Ensure Redis data persists across pod restarts and deletions using PersistentVolumeClaim

**Independent Test**: Write test key to Redis, forcefully delete Redis pod, verify PVC remains bound and new Redis pod mounts same volume with test key still present

### Implementation for User Story 4

- [ ] T034 [US4] Update redis-statefulset.yaml to include volumeClaimTemplate for redis-data PVC (already created in T014, verify configuration) in phaseIV/kubernetes/helm/todo-app/templates/redis-statefulset.yaml
- [ ] T035 [US4] Create test-persistence.sh script to write Redis key, delete pod, verify data retention in phaseIV/kubernetes/scripts/test-persistence.sh

**Checkpoint**: At this point, User Story 4 should work independently - Redis data survives pod deletion

---

## Phase 7: User Story 5 - Health Monitoring with Probes (Priority: P2)

**Goal**: Configure liveness and readiness probes for all services to enable Kubernetes self-healing

**Independent Test**: Configure liveness probe to check /health endpoint every 10 seconds, simulate backend crash by killing process, verify Kubernetes detects failure and restarts pod automatically

### Implementation for User Story 5

- [ ] T036 [US5] Update frontend-deployment.yaml to add liveness and readiness probes (HTTP GET /health:3000, initialDelaySeconds: 10, periodSeconds: 10, failureThreshold: 3) in phaseIV/kubernetes/helm/todo-app/templates/frontend-deployment.yaml
- [ ] T037 [US5] Update backend-deployment.yaml to add liveness and readiness probes (HTTP GET /health:8000, initialDelaySeconds: 10, periodSeconds: 10, failureThreshold: 3) in phaseIV/kubernetes/helm/todo-app/templates/backend-deployment.yaml
- [ ] T038 [US5] Update mcp-deployment.yaml to add liveness and readiness probes (HTTP GET /health:8001, initialDelaySeconds: 10, periodSeconds: 10, failureThreshold: 3) in phaseIV/kubernetes/helm/todo-app/templates/mcp-deployment.yaml
- [ ] T039 [US5] Update redis-statefulset.yaml to add liveness and readiness probes (exec: redis-cli ping, initialDelaySeconds: 10, periodSeconds: 10) in phaseIV/kubernetes/helm/todo-app/templates/redis-statefulset.yaml
- [ ] T040 [US5] Create test-resilience.sh script to delete pods and verify automatic restart in phaseIV/kubernetes/scripts/test-resilience.sh

**Checkpoint**: At this point, User Story 5 should work independently - Kubernetes automatically restarts unhealthy pods

---

## Phase 8: User Story 6 - Secrets and Configuration Management (Priority: P2)

**Goal**: Store sensitive data in Kubernetes Secrets and non-sensitive configuration in ConfigMaps following security best practices

**Independent Test**: Create Kubernetes Secret with DATABASE_URL and OPENAI_API_KEY, deploy backend referencing these secrets as environment variables, verify backend successfully connects to database and makes OpenAI API calls

### Implementation for User Story 6

- [ ] T041 [US6] Update secret.yaml template to support base64-encoded values from Helm values (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET, BETTER_AUTH_URL, REDIS_PASSWORD) in phaseIV/kubernetes/helm/todo-app/templates/secret.yaml
- [ ] T042 [US6] Update configmap.yaml template with non-sensitive configuration (REDIS_HOST, REDIS_PORT, MCP_SERVER_URL, NEXT_PUBLIC_API_URL) in phaseIV/kubernetes/helm/todo-app/templates/configmap.yaml
- [ ] T043 [US6] Update all deployment templates to inject secrets and configmap values as environment variables using secretKeyRef and configMapKeyRef in phaseIV/kubernetes/helm/todo-app/templates/*-deployment.yaml
- [ ] T044 [US6] Update values.yaml to include secrets section with placeholder instructions (DO NOT commit actual secrets) in phaseIV/kubernetes/helm/todo-app/values.yaml
- [ ] T045 [US6] Create values-local.yaml.example file with base64 encoding instructions for local development in phaseIV/kubernetes/values-local.yaml.example
- [ ] T046 [US6] Add values-local.yaml to .gitignore to prevent accidental secret commits in phaseIV/kubernetes/.gitignore

**Checkpoint**: At this point, User Story 6 should work independently - Secrets and ConfigMaps properly injected into pods

---

## Phase 9: User Story 7 - Complete End-to-End User Flow (Priority: P1)

**Goal**: Verify complete user journey (signup, login, chat, task creation via MCP tools) works in Kubernetes environment

**Independent Test**: Access frontend at http://todo-app.local, create new user account, log in, send chat message "Add task to buy groceries", verify MCP tool is invoked and task is created in Neon PostgreSQL database

### Implementation for User Story 7

- [ ] T047 [US7] Create test-e2e.sh script to validate complete user flow (signup → login → chat → task creation) using curl or Playwright in phaseIV/kubernetes/scripts/test-e2e.sh
- [ ] T048 [US7] Update deploy.sh script to run E2E test after deployment completes in phaseIV/kubernetes/scripts/deploy.sh

**Checkpoint**: At this point, User Story 7 should work - complete application functionality validated in Kubernetes

---

## Phase 10: User Story 8 - Deployment Automation and Testing (Priority: P3)

**Goal**: Provide automated deployment scripts and comprehensive test suites for quick deployment and validation

**Independent Test**: Run `./scripts/setup-minikube.sh` on clean machine, then `./scripts/deploy.sh`, then `./scripts/test.sh`, verify all tests pass and application is fully functional without manual steps

### Implementation for User Story 8

- [ ] T049 [US8] Create test.sh master test runner script that executes all test suites (Helm test, Ingress test, Load test, Resilience test, Persistence test, E2E test) in phaseIV/kubernetes/scripts/test.sh
- [ ] T050 [US8] Update setup-minikube.sh to add automated installation of Minikube, kubectl, Helm (detect OS, install if missing) in phaseIV/kubernetes/scripts/setup-minikube.sh
- [ ] T051 [US8] Update deploy.sh to add build Docker images step using Minikube Docker environment (eval $(minikube docker-env)) in phaseIV/kubernetes/scripts/deploy.sh
- [ ] T052 [US8] Create cleanup.sh script for uninstalling Helm chart and optionally deleting namespace and stopping Minikube in phaseIV/kubernetes/scripts/cleanup.sh

**Checkpoint**: At this point, User Story 8 should work - fully automated deployment and testing

---

## Phase 11: User Story 9 - Comprehensive Operational Documentation (Priority: P3)

**Goal**: Provide detailed documentation for deployment, operation, and troubleshooting

**Independent Test**: Give KUBERNETES_GUIDE.md to developer with no Kubernetes experience, verify they can successfully deploy application to Minikube following step-by-step instructions without external help

### Implementation for User Story 9

- [ ] T053 [P] [US9] Create KUBERNETES_GUIDE.md with comprehensive deployment guide (prerequisites, Minikube setup, Helm installation, deployment steps, testing, troubleshooting) in phaseIV/kubernetes/docs/KUBERNETES_GUIDE.md
- [ ] T054 [P] [US9] Create RUNBOOK.md with operational procedures (common operations, troubleshooting, backup/restore, upgrade procedures) in phaseIV/kubernetes/docs/RUNBOOK.md
- [ ] T055 [P] [US9] Create Helm chart README.md with chart description, requirements, installation instructions, configuration values documentation in phaseIV/kubernetes/helm/todo-app/README.md
- [ ] T056 [P] [US9] Create architecture diagram (ASCII or image) showing all services, Ingress, PVC, external database in phaseIV/kubernetes/docs/architecture-diagram.md

**Checkpoint**: All user stories complete - comprehensive documentation enables knowledge transfer

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation across all user stories

- [ ] T057 [P] Run helm lint on todo-app chart and fix any warnings in phaseIV/kubernetes/helm/todo-app/
- [ ] T058 [P] Verify all resource names follow Kubernetes naming conventions (lowercase alphanumeric and hyphens only) across all templates
- [ ] T059 [P] Verify all containers have resource requests and limits defined (Burstable QoS class) across all deployment templates
- [ ] T060 [P] Verify all labels follow app.kubernetes.io/* recommended labels across all templates
- [ ] T061 Run complete test suite (./scripts/test.sh) and verify all tests pass
- [ ] T062 Validate quickstart.md by following step-by-step instructions on fresh Minikube cluster
- [ ] T063 Create ADR for significant architectural decisions (Helm chart structure, Nginx Ingress configuration, HPA strategy, StatefulSet for Redis, deployment workflow) in history/adr/ using /sp.adr command

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-11)**: All depend on Foundational phase completion
  - US1 (Cluster Deployment): Can start after Foundational - Foundation for all other stories
  - US2 (Ingress): Depends on US1 (needs services deployed)
  - US3 (HPA): Depends on US1 (needs deployments created) - Independent of US2
  - US4 (Persistence): Depends on US1 (needs Redis StatefulSet) - Independent of US2, US3
  - US5 (Health Probes): Can enhance US1 deployments - Independent of US2, US3, US4
  - US6 (Secrets): Can enhance US1 deployments - Independent of US2, US3, US4, US5
  - US7 (E2E): Depends on US1, US2 (needs full deployment and HTTP access) - Final validation
  - US8 (Automation): Depends on US1-US7 (needs all features implemented)
  - US9 (Documentation): Can be written in parallel with implementation - No technical dependencies
- **Polish (Phase 12)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - FOUNDATION FOR ALL
- **User Story 2 (P2)**: Depends on US1 (needs services deployed first)
- **User Story 3 (P2)**: Depends on US1 (needs deployments created) - Independent of US2
- **User Story 4 (P2)**: Depends on US1 (needs Redis StatefulSet) - Independent of US2, US3
- **User Story 5 (P2)**: Depends on US1 (enhances existing deployments) - Independent of US2, US3, US4
- **User Story 6 (P2)**: Depends on US1 (enhances existing deployments) - Independent of US2, US3, US4, US5
- **User Story 7 (P1)**: Depends on US1 + US2 (needs deployment + HTTP access) - Final validation
- **User Story 8 (P3)**: Depends on US1-US7 (automates all features)
- **User Story 9 (P3)**: Independent (documentation can be written in parallel)

### Within Each User Story

- **US1**: Redis → MCP → Backend → Frontend (sequential deployment order)
- **US2**: Ingress manifest → Deploy → Test
- **US3**: HPA manifests (parallel) → Deploy → Load test
- **US4**: PVC configuration → Persistence test
- **US5**: Probe configurations (parallel) → Deploy → Resilience test
- **US6**: Secret/ConfigMap templates → Update deployments → Verify injection
- **US7**: E2E test script → Run validation
- **US8**: Test scripts (parallel) → Master test runner
- **US9**: Documentation files (parallel)

### Parallel Opportunities

- **Phase 1 Setup**: T002, T003 (copy frontend/backend) and T004, T005, T006 (create directories) can run in parallel
- **Phase 2 Foundational**: T010, T011, T012 (namespace, secret, configmap) can run in parallel
- **US1 Implementation**: T014, T015, T016 (Redis templates), T017, T018 (MCP templates), T019, T020 (Backend templates), T021, T022 (Frontend templates) can all be created in parallel, then deployed sequentially
- **US2 Implementation**: Single-threaded (Ingress manifest → Deploy → Test)
- **US3 Implementation**: T030, T031 (HPA templates) can run in parallel
- **US5 Implementation**: T036, T037, T038, T039 (probe configurations) can run in parallel
- **US9 Implementation**: T053, T054, T055, T056 (all documentation files) can run in parallel
- **Phase 12 Polish**: T057, T058, T059, T060 (validation tasks) can run in parallel

---

## Parallel Example: User Story 1 (Cluster Deployment)

```bash
# Launch all template creation tasks in parallel:
Task: "Create redis-statefulset.yaml template in phaseIV/kubernetes/helm/todo-app/templates/redis-statefulset.yaml"
Task: "Create redis-service.yaml template in phaseIV/kubernetes/helm/todo-app/templates/redis-service.yaml"
Task: "Create redis-pvc.yaml template in phaseIV/kubernetes/helm/todo-app/templates/redis-pvc.yaml"
Task: "Create mcp-deployment.yaml template in phaseIV/kubernetes/helm/todo-app/templates/mcp-deployment.yaml"
Task: "Create mcp-service.yaml template in phaseIV/kubernetes/helm/todo-app/templates/mcp-service.yaml"
Task: "Create backend-deployment.yaml template in phaseIV/kubernetes/helm/todo-app/templates/backend-deployment.yaml"
Task: "Create backend-service.yaml template in phaseIV/kubernetes/helm/todo-app/templates/backend-service.yaml"
Task: "Create frontend-deployment.yaml template in phaseIV/kubernetes/helm/todo-app/templates/frontend-deployment.yaml"
Task: "Create frontend-service.yaml template in phaseIV/kubernetes/helm/todo-app/templates/frontend-service.yaml"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 7 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Core deployment)
4. Complete Phase 9: User Story 7 (E2E validation)
5. **STOP and VALIDATE**: Test complete user flow independently
6. Deploy/demo if ready

**Result**: Functional Kubernetes deployment with basic features (no autoscaling, no persistence, minimal monitoring)

### Incremental Delivery (Recommended)

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP Ready** (basic deployment)
3. Add User Story 2 → Test independently → **HTTP Access Ready** (external routing)
4. Add User Story 3 → Test independently → **Autoscaling Ready** (dynamic scaling)
5. Add User Story 4 → Test independently → **Persistence Ready** (data durability)
6. Add User Story 5 → Test independently → **Self-Healing Ready** (health monitoring)
7. Add User Story 6 → Test independently → **Security Ready** (proper secrets management)
8. Add User Story 7 → Test independently → **Production Validation** (E2E working)
9. Add User Story 8 → Test independently → **Automation Ready** (deployment scripts)
10. Add User Story 9 → Documentation complete → **Knowledge Transfer Ready**

Each story adds production-grade features without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (blocking foundation)
3. Once US1 is complete:
   - Developer A: User Story 2 (Ingress)
   - Developer B: User Story 3 (HPA)
   - Developer C: User Story 4 (Persistence)
   - Developer D: User Story 9 (Documentation)
4. Once US2 complete:
   - Developer A: User Story 7 (E2E tests)
5. Once US1-US7 complete:
   - Any developer: User Story 8 (Automation)
6. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label (US1-US9) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Infrastructure feature: Validation through deployment testing rather than unit tests
- Run `helm lint` frequently during development to catch template errors early
- Test on fresh Minikube cluster to ensure reproducibility
- Keep secrets in values-local.yaml (never commit to git)
