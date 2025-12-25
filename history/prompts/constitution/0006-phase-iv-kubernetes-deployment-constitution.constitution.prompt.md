---
id: 0006
title: Phase IV Kubernetes Deployment Constitution
stage: constitution
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: Msaleemakhtar
command: /sp.constitution
labels: ["constitution", "phase-iv", "kubernetes", "helm", "minikube", "governance", "production-deployment"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None (constitutional document; validation via 4 self-checks)
---

## Prompt

You are updating the Todo App Spec-Driven Development Constitution for Phase IV: Kubernetes Deployment.

## Context from Planning Discussion

**Current State:**
- Constitution v2.4.0 governs Phases I-III (CLI, Full-stack Web, AI Chatbot)
- Phase III Todo Chatbot is fully containerized with Docker Compose (4 services: frontend, backend, mcp-server, redis)
- Phase III is COMPLETED and all files have been copied into `/phaseIV/` directory for Phase IV hackathon
- Phase IV will deploy Phase III containers to Kubernetes (Minikube) using Helm charts

**Phase IV Hackathon Requirements:**
1. ✅ Containerization: COMPLETE (Docker images exist)
2. ❌ Helm Charts: Create Helm charts for all services
3. ❌ Minikube Deployment: Deploy to local Kubernetes cluster
4. ❌ AI DevOps Tools: Integrate kubectl-ai and/or kagent

**Technology Stack for Phase IV:**
- Container Runtime: Docker Desktop
- Orchestration: Kubernetes (Minikube - 4 CPU, 8GB RAM minimum)
- Package Manager: Helm Charts (v3.13+)
- Ingress: Nginx Ingress Controller
- Storage: PersistentVolumes for Redis
- Autoscaling: Horizontal Pod Autoscaler (HPA)
- AI DevOps: kubectl-ai, kagent (optional)

**Architecture:**
```
Minikube Cluster (todo-phaseiv namespace)
├── Frontend Deployment (2-5 replicas, HPA)
├── Backend Deployment (2-5 replicas, HPA)
├── MCP Server Deployment (1 replica)
├── Redis StatefulSet (1 replica, 1Gi PVC)
├── Nginx Ingress (todo-app.local)
│   ├── / → frontend:3000
│   └── /api → backend:8000
└── External: Neon PostgreSQL (shared)
```

## Required Constitutional Updates

### 1. Version Bump
Update from v2.4.0 to v2.5.0 (MINOR bump - new phase added, new principles)

### 2. Mission Statement
Add Phase IV as ACTIVE:
```
**Phase IV (ACTIVE)**: Kubernetes deployment with Helm charts, enabling local
orchestration via Minikube with production-grade features (Nginx Ingress,
Horizontal Pod Autoscaling, Persistent Volumes).
```

### 3. New Core Principles

**Principle XIV: Containerization & Orchestration (Phase IV Only)**
- Docker containers as deployment units
- Kubernetes for orchestration
- Helm charts for package management and templating
- Infrastructure as Code principles
- Declarative configuration management
- Service communication via ClusterIP and internal DNS
- Namespace isolation (todo-phaseiv)

**Principle XV: Production-Grade Deployment (Phase IV Only)**
- Nginx Ingress Controller for HTTP routing (MANDATORY)
- Horizontal Pod Autoscaling (min:2, max:5, CPU:70%, Mem:80%) (MANDATORY)
- Persistent Volumes for Redis (1Gi PVC) (MANDATORY)
- Health probes (liveness/readiness) for all services (MANDATORY)
- Resource limits and requests enforcement (MANDATORY)
- Observability via metrics-server

### 4. Repository Structure Update (Principle II)

Add Phase IV directory structure:
```
/phaseIV/
├── frontend/              # Next.js frontend (from Phase III)
├── backend/               # FastAPI backend (from Phase III)
├── kubernetes/            # NEW: K8s-specific artifacts
│   ├── helm/
│   │   └── todo-app/      # Helm chart (20 YAML templates)
│   ├── scripts/           # Deployment automation
│   └── docs/              # KUBERNETES_GUIDE.md, RUNBOOK.md
├── docker-compose.yml     # Local Docker Compose
└── DOCKER_GUIDE.md        # Docker documentation
```

**CRITICAL: Add Exception Clause for Container Artifact Reuse**

Phase IV uniquely reuses containers from Phase III. Add this clarification:

```markdown
**Phase IV Exception for Container Artifact Reuse:**
Phase IV deploys containerized versions of Phase III services. While source
code separation is maintained (Phase IV does not import Phase III source
files directly), Phase IV Dockerfiles build from Phase III source directories
located in /phaseIV/frontend/ and /phaseIV/backend/.

This is constitutionally acceptable because:
- Docker images are deployment artifacts, not source code
- Helm charts and Kubernetes manifests are Phase IV-specific implementations
- Phase IV demonstrates deployment/orchestration patterns, not new application logic
- Source code remains separated (no cross-phase imports at runtime)
```

### 5. Technology Constraints

Add Phase IV mandatory technologies:
- Container Runtime: Docker Desktop
- Orchestration: Kubernetes via Minikube
- Package Manager: Helm Charts (v3.13+)
- Ingress Controller: Nginx Ingress
- Storage: PersistentVolume with standard StorageClass
- Autoscaling: Horizontal Pod Autoscaler (metrics-server)
- Cluster Requirements: Minikube 4 CPU, 8GB RAM minimum
- Namespace: todo-phaseiv
- Optional AI DevOps: kubectl-ai, kagent, Docker AI (Gordon)

### 6. Success Criteria

Add Phase IV completion checklist with:
- **Functional Requirements:** All 4 services deployed, Ingress routing, Redis persistence, HPA scaling, complete user flow, 5 MCP tools working
- **Technical Requirements:** Comprehensive spec exists, Helm chart best practices, resource limits, health probes, Secrets/ConfigMaps, helm test passes
- **Documentation Requirements:** KUBERNETES_GUIDE.md, Helm README.md, RUNBOOK.md, architecture diagram
- **Testing Requirements:** E2E test, load test, resilience test, persistence test, ingress test

### 7. Requirement-to-Rule Mapping

Add 18 Phase IV requirements:
- FR-P4-001 to FR-P4-010 (Functional Requirements)
- SR-P4-001 to SR-P4-004 (Structural Requirements)
- TC-P4-001 to TC-P4-004 (Technical Constraints)

### 8. Workflow Guidance (Principle I)

Add Phase IV-specific Spec-Driven Development workflow:
1. Specification Phase (comprehensive spec.md covering infrastructure, Helm, deployments, production features, testing)
2. Generation Phase (AI generates Helm charts, scripts, documentation)
3. Validation Phase (helm lint, dry-run, template rendering)
4. Deployment Phase (incremental: Redis → MCP → Backend → Frontend → Ingress)
5. Testing Phase (helm test, E2E, load, resilience, persistence, ingress)

## Your Task

1. Read the current constitution at `.specify/memory/constitution.md`
2. Apply ALL 8 required updates listed above
3. Create Sync Impact Report (HTML comment at top)
4. Validate: no bracket placeholders, version matches, dates ISO format
5. Write updated constitution to `.specify/memory/constitution.md`
6. Create PHR in `history/prompts/constitution/` for this constitution update

**Follow the exact pattern used for Phase III integration in v2.3.0 → v2.4.0**

Use today's date (2025-12-25) for LAST_AMENDED_DATE.

Proceed with the constitution update now.

## Response snapshot

Constitution successfully upgraded from v2.4.0 to v2.5.0 for Phase IV: Kubernetes Deployment.

**Key Updates Applied:**

1. **Version Bump**: Updated to v2.5.0 with amendment date 2025-12-25
2. **Mission Statement**: Added Phase IV as ACTIVE, updated Phase III to COMPLETED
3. **New Core Principles**:
   - Principle XIV: Containerization & Orchestration (Docker, Kubernetes, Helm, Infrastructure as Code)
   - Principle XV: Production-Grade Deployment (Nginx Ingress, HPA, PersistentVolumes, Health Probes, Resource Limits)
4. **Repository Structure**: Added `/phaseIV/` directory structure with `kubernetes/` subdirectory and exception clause for container artifact reuse
5. **Technology Constraints**: Added Phase IV mandatory stack (Docker Desktop, Minikube, Helm v3.13+, Nginx Ingress)
6. **Success Criteria**: Added comprehensive Phase IV completion checklist (10 functional requirements, 10 technical requirements, 5 documentation requirements, 7 testing requirements)
7. **Requirement-to-Rule Mapping**: Added 18 Phase IV requirements (FR-P4-001 to FR-P4-010, SR-P4-001 to SR-P4-004, TC-P4-001 to TC-P4-004)
8. **Workflow Guidance**: Integrated Phase IV Spec-Driven Development workflow (5 phases: Specification → Generation → Validation → Deployment → Testing)

**Constitutional Self-Checks:**
- Alignment Check: ✅ PASS (50+ rules, all mapped to requirements)
- Coverage Check: ✅ PASS (all requirement types covered for all phases)
- Conflict Check: ✅ PASS (no contradictory rules, container reuse exception documented)
- Completeness Check: ✅ PASS (all Phase IV features, principles, workflow guidance complete)

**Sync Impact Report**: Created comprehensive HTML comment documenting all changes from v2.4.0 to v2.5.0

## Outcome

- ✅ Impact: Constitution upgraded from v2.4.0 to v2.5.0 adding Phase IV Kubernetes Deployment governance. Two new core principles added (XIV: Containerization & Orchestration, XV: Production-Grade Deployment). 18 new requirements mapped (10 functional, 4 structural, 4 technology constraints). Phase IV workflow integrated into Principle I. Container artifact reuse exception documented. All 4 constitutional self-checks pass.
- 🧪 Tests: None (constitutional document; validation via 4 self-checks: Alignment ✅ PASS, Coverage ✅ PASS, Conflict-Free ✅ PASS, Completeness ✅ PASS)
- 📁 Files: Modified .specify/memory/constitution.md (1470 lines, comprehensive Phase IV governance)
- 🔁 Next prompts: Create comprehensive specification at /specs/sphaseIV/001-kubernetes-deployment/spec.md covering Helm charts, deployments, Ingress, HPA, PersistentVolumes, health probes, resource limits, and all testing requirements
- 🧠 Reflection: Phase IV represents a unique constitutional challenge - it reuses containers from Phase III while maintaining phase separation principles. The exception clause for container artifact reuse clarifies that Docker images are deployment artifacts (not source code), preserving constitutional integrity while enabling practical hackathon execution. The production-grade requirements (Ingress, HPA, PV, health probes) demonstrate that even local Minikube deployments can follow production best practices.

## Evaluation notes (flywheel)

- Failure modes observed: None. All validations passed. Constitution structure maintained consistency with previous version.
- Graders run and results (PASS/FAIL): Alignment ✅ PASS (50+ rules mapped to requirements), Coverage ✅ PASS (all requirement types covered), Conflict-Free ✅ PASS (container reuse exception documented), Completeness ✅ PASS (principles, workflow, requirements all complete), Placeholder Check ✅ PASS (no unresolved placeholders), Content Check ✅ PASS (1470 lines), File Check ✅ PASS (readable)
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none
