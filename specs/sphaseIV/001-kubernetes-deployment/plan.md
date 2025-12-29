# Implementation Plan: Kubernetes Deployment for Phase IV Todo Chatbot

**Branch**: `001-kubernetes-deployment` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-kubernetes-deployment/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deploy Phase III Todo Chatbot (Frontend, Backend, MCP Server, Redis) to local Kubernetes cluster using Minikube with production-grade features including Nginx Ingress for HTTP routing, Horizontal Pod Autoscaling for dynamic replica management, PersistentVolumes for Redis data persistence, and comprehensive health monitoring. The implementation uses Helm charts for templated deployment, incremental rollout scripts, and 6 categories of testing (Helm tests, E2E, load, resilience, persistence, ingress) to validate complete functionality in Kubernetes environment.

## Technical Context

**Language/Version**: YAML (Kubernetes manifests), Helm 3.13+ (templating), Bash (deployment scripts)
**Primary Dependencies**:
- Kubernetes v1.28+ via Minikube
- Docker Desktop (container runtime)
- Nginx Ingress Controller (HTTP routing)
- Metrics Server (HPA functionality)
- Helm v3.13+ (package management)

**Storage**:
- PersistentVolume with standard StorageClass (Minikube hostPath provisioner) for Redis (1Gi)
- External Neon Serverless PostgreSQL (shared with Phase III, connection via DATABASE_URL in Kubernetes Secret)

**Testing**:
- Helm tests (chart-provided health validation)
- E2E tests (Selenium/Playwright for complete user journey)
- Load tests (Apache Bench for HPA validation)
- Resilience tests (pod deletion and recovery)
- Persistence tests (Redis data retention across pod restarts)
- Ingress tests (HTTP routing validation)

**Target Platform**: Minikube local Kubernetes cluster (Linux/macOS/Windows host with 4 CPU + 8GB RAM minimum)

**Project Type**: Kubernetes deployment (infrastructure-as-code) for existing Phase III web application

**Performance Goals**:
- All 4 services (frontend, backend, mcp-server, redis) reach Running state within 5 minutes of helm install
- HPA scales frontend/backend from 2 to 5 replicas within 2 minutes under load (500 req/s)
- HTTP response time maintained at p95 < 200ms for CRUD operations even under load

**Constraints**:
- Namespace isolation (todo-phaseiv) - all resources in single namespace
- Resource limits: Frontend/Backend (500m-1000m CPU, 512Mi-1024Mi RAM), MCP (250m-500m CPU, 256Mi-512Mi RAM), Redis (250m-500m CPU, 128Mi-256Mi RAM)
- Health probe requirements: initialDelaySeconds 10s, periodSeconds 10s, timeoutSeconds 5s, failureThreshold 3
- Secrets management: All sensitive data (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET) in Kubernetes Secrets, never in ConfigMaps or plain YAML
- Helm chart best practices: helm lint passes with 0 warnings, helm test validates deployment

**Scale/Scope**:
- 4 services deployed (Frontend Deployment, Backend Deployment, MCP Server Deployment, Redis StatefulSet)
- 2-5 replicas each for Frontend and Backend (via HPA)
- 20+ YAML templates in Helm chart
- Single Ingress resource with 2 path-based routes
- 5 MCP tools functional in Kubernetes environment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitutional Compliance

✅ **Principle I (Spec-Driven Development)**: Infrastructure-as-code approach followed. Spec.md created before Helm chart generation. All Kubernetes manifests will be AI-generated from specification.

✅ **Principle II (Repository Structure)**: Phase IV directory structure follows constitutional mandate at `/phaseIV/` with `kubernetes/` subdirectory. Container artifact reuse from Phase III explicitly allowed per constitutional exception clause.

✅ **Principle XIV (Containerization & Orchestration)**: Minikube for local Kubernetes cluster, Helm v3.13+ for package management, declarative YAML manifests, namespace isolation (todo-phaseiv) - all requirements met.

✅ **Principle XV (Production-Grade Deployment)**: Nginx Ingress (MANDATORY), HPA (MANDATORY), PersistentVolumes (MANDATORY), Health Probes (MANDATORY), Resource Limits (MANDATORY) - all mandatory features included in spec.

✅ **Technology Constraints (Phase IV)**: Docker Desktop (container runtime), Kubernetes via Minikube, Helm Charts v3.13+, Nginx Ingress, 4 CPU + 8GB RAM minimum, todo-phaseiv namespace, Neon Serverless PostgreSQL - all constitutional technology requirements satisfied.

✅ **Phase Separation**: Phase IV deploys Phase III containers as deployment artifacts (constitutionally allowed exception). No source code imports between phases. Docker images built from Phase III source in `/phaseIV/frontend/` and `/phaseIV/backend/`.

✅ **Testing Requirements**: All 6 testing categories specified (Helm tests, E2E, load, resilience, persistence, ingress) per constitutional Phase IV testing mandate.

✅ **Documentation Requirements**: KUBERNETES_GUIDE.md, RUNBOOK.md, Helm README.md all specified per constitutional Phase IV documentation mandate.

### No Violations Detected

All constitutional requirements satisfied. No complexity justification needed.

---

## Post-Design Re-Evaluation (Phase 1 Complete)

**Re-evaluation Date**: 2025-12-26

✅ **Helm Chart Structure**: 20+ YAML templates organized per Helm best practices (Chart.yaml, values.yaml, templates/, tests/)
✅ **Kubernetes Resources**: 14 resource entities defined in data-model.md (Deployments, StatefulSet, Services, Ingress, HPA, ConfigMap, Secret, Namespace)
✅ **Contracts Specified**: Helm values schema and deployment script contracts documented in contracts/
✅ **Deployment Workflow**: Incremental rollout strategy defined (Redis → MCP → Backend → Frontend → Ingress)
✅ **Testing Strategy**: All 6 testing categories specified (Helm, Ingress, Persistence, Resilience, Load, E2E)
✅ **Documentation**: Quickstart.md provides 30-minute deployment guide
✅ **Agent Context Updated**: Phase IV technologies added to CLAUDE.md

**Constitutional Compliance Post-Design**: All requirements satisfied. Design artifacts complete. Ready for Phase 2 (Task Generation via `/sp.tasks` command).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
phaseIV/
├── frontend/                    # Next.js frontend (copied from Phase III)
│   ├── app/
│   │   └── chat/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── Dockerfile               # Multi-stage production build
│   ├── package.json
│   └── bun.lockb
│
├── backend/                     # FastAPI backend (copied from Phase III)
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── services/
│   │   ├── routers/
│   │   └── mcp/                 # MCP Server
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile               # Multi-stage production build
│   ├── pyproject.toml
│   └── uv.lock
│
├── kubernetes/                  # NEW: Kubernetes-specific artifacts
│   ├── helm/
│   │   └── todo-app/            # Helm chart (20+ YAML templates)
│   │       ├── Chart.yaml       # Chart metadata
│   │       ├── values.yaml      # Default configuration values
│   │       ├── README.md        # Chart documentation
│   │       ├── templates/
│   │       │   ├── _helpers.tpl
│   │       │   ├── frontend-deployment.yaml
│   │       │   ├── frontend-service.yaml
│   │       │   ├── frontend-hpa.yaml
│   │       │   ├── backend-deployment.yaml
│   │       │   ├── backend-service.yaml
│   │       │   ├── backend-hpa.yaml
│   │       │   ├── mcp-deployment.yaml
│   │       │   ├── mcp-service.yaml
│   │       │   ├── redis-statefulset.yaml
│   │       │   ├── redis-service.yaml
│   │       │   ├── redis-pvc.yaml
│   │       │   ├── ingress.yaml
│   │       │   ├── secret.yaml
│   │       │   ├── configmap.yaml
│   │       │   └── tests/
│   │       │       ├── test-frontend.yaml
│   │       │       ├── test-backend.yaml
│   │       │       ├── test-mcp.yaml
│   │       │       └── test-redis.yaml
│   │       └── .helmignore
│   │
│   ├── scripts/                 # Deployment automation
│   │   ├── setup-minikube.sh   # Minikube installation and cluster setup
│   │   ├── deploy.sh            # Incremental rollout (Redis → MCP → Backend → Frontend → Ingress)
│   │   └── test.sh              # Run all 6 test suites
│   │
│   └── docs/
│       ├── KUBERNETES_GUIDE.md  # Comprehensive deployment guide
│       └── RUNBOOK.md           # Operational procedures
│
├── docker-compose.yml           # Local Docker Compose (from Phase III)
└── DOCKER_GUIDE.md              # Docker documentation
```

**Structure Decision**: Phase IV uses Kubernetes deployment structure (Option 2 variant with infrastructure-as-code). Source code (frontend, backend) is copied from Phase III to maintain phase separation while allowing Docker image builds from Phase IV directory. All Kubernetes-specific artifacts (Helm charts, scripts, docs) are new in `/phaseIV/kubernetes/` subdirectory per constitutional requirement.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
