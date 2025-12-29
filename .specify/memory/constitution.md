<!--
SYNC IMPACT REPORT:
Version Change: 2.5.0 -> 3.0.0
Amendment Date: 2025-12-30

MAJOR VERSION BUMP RATIONALE:
This is a MAJOR version increment (3.0.0) due to:
- Three new governance principles added (XVI, XVII, XVIII)
- Expansion to five-phase architecture governance
- New distributed systems requirements (Kafka, Dapr)
- Cloud deployment governance (Oracle Cloud OKE)
- Backward-incompatible governance expansion

Modified Sections:

  - Mission Statement:
    * CHANGED: Updated Phase III status from ACTIVE to COMPLETE
    * CHANGED: Updated Phase IV status from ACTIVE to COMPLETE
    * ADDED: Phase V Advanced Cloud Deployment as NEW, ACTIVE implementation
    * RATIONALE: Phase IV completed; Phase V adds event-driven architecture, Dapr, and cloud deployment

  - Core Principles:
    * ADDED: Principle XVI - Event-Driven Architecture with Kafka (Phase V only)
    * ADDED: Principle XVII - Distributed Application Runtime with Dapr (Phase V only)
    * ADDED: Principle XVIII - Production Cloud Deployment (Phase V only)
    * RATIONALE: Governs Phase V event streaming, distributed runtime, and cloud infrastructure

  - Repository Structure (Principle II):
    * ADDED: /phaseV/ directory structure with kafka/, dapr-components/, kubernetes/ subdirectories
    * ADDED: Phase V-specific directory layout (backend, frontend, kubernetes, dapr-components)
    * RATIONALE: Phase V extends Phase IV with event-driven and cloud-native components

  - Specs Organization:
    * ADDED: `/specs/sphaseV/` directory for Phase V specifications
    * RATIONALE: Maintains spec organization pattern for new phase

  - Feature Scope (Principle X):
    * RENAMED: From "Feature Scope (Phase II - COMPLETED)" to "Feature Scope Evolution"
    * ADDED: Phase V feature progression (14-39 MCP tools)
    * ADDED: Intermediate features (priorities, tags, search, filter, sort)
    * ADDED: Advanced features (due dates, reminders, recurring tasks)
    * RATIONALE: Documents feature evolution across phases

  - Technology Constraints:
    * ADDED: Phase V-specific technology stack (Redpanda/Kafka, Dapr v1.12+, Oracle Cloud OKE)
    * ADDED: Event streaming requirements (aiokafka, Dapr Pub/Sub)
    * ADDED: Cloud deployment stack (cert-manager, GitHub Actions, Prometheus/Grafana)
    * RATIONALE: Enforces mandatory distributed and cloud stack for Phase V hackathon

  - Data Model Specification:
    * ADDED: Phase V enhanced tasks_phaseiii table (priority, due_date, category_id, recurrence_rule, reminder_sent)
    * ADDED: Categories table (id, user_id, name, color, created_at)
    * ADDED: Tags Phase V table (id, user_id, name, color, created_at)
    * ADDED: TaskTags junction table (task_id, tag_id)
    * ADDED: Full-text search with tsvector + GIN indexes
    * RATIONALE: Supports advanced task management features in Phase V

  - Success Criteria:
    * CHANGED: Phase III from ACTIVE to COMPLETED
    * CHANGED: Phase IV from ACTIVE to COMPLETED
    * ADDED: Phase V Part A criteria (advanced features, 17 MCP tools, Kafka events)
    * ADDED: Phase V Part B criteria (Dapr integration, 4 components)
    * ADDED: Phase V Part C criteria (Oracle Cloud OKE, CI/CD, monitoring, security)
    * RATIONALE: Defines completion criteria for Phase V three-part hackathon

  - Requirement-to-Rule Mapping:
    * ADDED: Phase V functional requirements (FR-P5-001 through FR-P5-016)
    * ADDED: Phase V structural requirements (SR-P5-001 through SR-P5-003)
    * ADDED: Phase V technology constraints (TC-P5-001 through TC-P5-006)
    * RATIONALE: Maintains traceability for Phase V governance

Templates Requiring Updates:
  - None - existing templates remain compatible

Follow-up TODOs:
  - Create initial comprehensive specs in /specs/sphaseV/001-advanced-features/, 002-dapr-integration/, 003-cloud-deployment/
  - Setup Redpanda Cloud cluster and Kafka topics
  - Configure Oracle Cloud OKE cluster
  - Create CI/CD pipelines in .github/workflows/
-->

# Todo App - Multi-Phase Constitution

## Mission Statement

This project implements a todo application across five distinct phases, each with complete separation:

**Phase I (COMPLETED)**: Command-line interface (CLI) todo application with in-memory storage and rich terminal UI.

**Phase II (COMPLETED)**: Full-stack web application with persistent storage, multi-user authentication via Better Auth, Next.js frontend, and FastAPI backend.

**Phase III (COMPLETED)**: AI-powered chatbot interface for managing todos through natural language using MCP (Model Context Protocol) server architecture and OpenAI Agents SDK.

**Phase IV (COMPLETED)**: Kubernetes deployment with Helm charts, enabling local orchestration via Minikube with production-grade features (Nginx Ingress, Horizontal Pod Autoscaling, Persistent Volumes).

**Phase V (ACTIVE)**: Advanced cloud deployment with event-driven architecture (Kafka/Redpanda), distributed application runtime (Dapr), production cloud infrastructure (Oracle Cloud OKE), CI/CD pipelines, and comprehensive monitoring.

Each phase is a **completely independent implementation** with no code sharing between phases. The constitution governs all phases while providing phase-specific guidance.

---

## Core Principles

### I. Spec-Driven Development (Mandatory)

**Philosophy**: The specification is the single source of truth; AI is the implementation engine.

**Requirements**:
- ALL frontend and backend code MUST be generated by an AI agent from written specifications in the `/specs` directory.
- Manual coding of features, business logic, UI components, or API endpoints is **strictly forbidden**, with one documented exception.
- **Exception for AI Limitations**: In the rare event that the AI code generator cannot produce a correct implementation for a well-defined specification after reasonable refinement efforts (iterating on prompts, breaking down complexity, adjusting specification clarity), a developer may manually write the minimum necessary code. This action MUST be:
  1. Documented in `DEVIATIONS.md` with full justification including refinement attempts made
  2. Reviewed by the team before merging
  3. Tagged with `[AI-LIMITATION]` in commit message
  4. Accompanied by the specification that was attempted
- Development follows the cycle: **Spec --> AI Generate --> Test --> Refine Spec --> Regenerate**.
- Specifications MUST be managed via GitHub Spec-Kit Plus in the `/specs` directory.
- Spec organization MUST follow the default Specify Plus Kit structure:
  - Phase I: `/specs/sphaseI/NNN-feature-name/`
  - Phase II: `/specs/sphaseII/NNN-feature-name/`
  - Phase III: `/specs/sphaseIII/NNN-feature-name/`
  - Phase IV: `/specs/sphaseIV/NNN-feature-name/`
  - Phase V: `/specs/sphaseV/NNN-feature-name/`
  - Each feature directory contains `spec.md`, `plan.md`, `tasks.md`, and related artifacts.
- **Phase IV Workflow**: Phase IV follows infrastructure-as-code specification approach:
  1. **Specification Phase**: Create comprehensive spec.md covering infrastructure, Helm charts, deployments, production features, and testing
  2. **Generation Phase**: AI generates Helm charts, Kubernetes manifests, scripts, and documentation from spec
  3. **Validation Phase**: Run `helm lint`, `helm template`, and dry-run deployments to validate generated artifacts
  4. **Deployment Phase**: Incremental rollout (Redis --> MCP --> Backend --> Frontend --> Ingress)
  5. **Testing Phase**: Execute helm tests, E2E tests, load tests, resilience tests, persistence tests, ingress tests
- **Phase V Workflow**: Phase V follows event-driven and cloud-native specification approach:
  1. **Specification Phase**: Create specs for advanced features (Part A), Dapr integration (Part B), cloud deployment (Part C)
  2. **Generation Phase**: AI generates enhanced MCP tools, Kafka producers/consumers, Dapr components, cloud manifests
  3. **Validation Phase**: Validate event flow, Dapr component configuration, cloud infrastructure
  4. **Local Deployment Phase**: Deploy to Minikube with Dapr enabled
  5. **Cloud Deployment Phase**: Deploy to Oracle Cloud OKE with CI/CD pipeline
  6. **Testing Phase**: Execute unit tests, integration tests, load tests, resilience tests, E2E tests

**Verification**:
- Commit history shows specification files created/modified before implementation files.
- Pull request descriptions reference the spec file(s) that drive the implementation.
- No implementation PRs without corresponding spec file changes or references.

**Rationale**: AI-driven development ensures consistency, reduces human error, maintains clear traceability from specification to implementation, and demonstrates the viability of AI-first software engineering at scale.

---

### II. Repository Structure

**Philosophy**: Complete phase separation with unified governance.

**Requirements**:
- **Repository Structure**: Monorepo with distinct directories per phase:
  - `/phaseI` - CLI application (Python, Rich UI) - COMPLETED
  - `/phaseII` - Full-stack web application (Next.js + FastAPI) - COMPLETED
  - `/phaseIII` - AI Chatbot (OpenAI ChatKit + FastAPI + MCP) - COMPLETED
  - `/phaseIV` - Kubernetes Deployment (Minikube + Helm + Nginx Ingress) - COMPLETED
  - `/phaseV` - Advanced Cloud Deployment (Kafka + Dapr + Oracle Cloud OKE) - ACTIVE
  - `/specs` - All specifications organized by phase
  - `/.specify` - Spec-Kit Plus configuration and templates

**Phase Separation Requirements**:
- **NO IMPORTS** between phases (e.g., phaseIII MUST NOT import from phaseII)
- **NO SHARED CODE** or modules between phases
- **INDEPENDENT IMPLEMENTATIONS** - each phase reimplements required functionality
- **SEPARATE DATABASE TABLES** - Phase III uses `tasks_phaseiii` table, not Phase II tables

**Phase IV Exception for Container Artifact Reuse**:
Phase IV deploys containerized versions of Phase III services. While source code separation is maintained (Phase IV does not import Phase III source files directly), Phase IV Dockerfiles build from Phase III source directories located in `/phaseIV/frontend/` and `/phaseIV/backend/`.

This is constitutionally acceptable because:
- Docker images are deployment artifacts, not source code
- Helm charts and Kubernetes manifests are Phase IV-specific implementations
- Phase IV demonstrates deployment/orchestration patterns, not new application logic
- Source code remains separated (no cross-phase imports at runtime)

**Phase V Exception for Container Artifact Evolution**:
Phase V builds upon Phase IV container artifacts and extends them with event-driven and cloud-native capabilities. While source code separation is maintained, Phase V:
- Copies Phase IV source directories to `/phaseV/frontend/` and `/phaseV/backend/`
- Enhances backend with Kafka producers, Dapr integration, and new MCP tools
- Adds new Kubernetes deployments (Notification Service, Recurring Task Service)
- Introduces Dapr component configurations

This is constitutionally acceptable because:
- Phase V demonstrates event-driven and distributed runtime patterns
- New services and capabilities are Phase V-specific implementations
- Source code is copied (not imported) and then independently evolved
- No cross-phase imports at runtime

**Phase III Directory Structure**:
```
phaseIII/
├── backend/                    # Python FastAPI backend
│   ├── pyproject.toml         # UV package manager
│   ├── .env.example
│   ├── alembic/               # Database migrations (independent)
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Database connection
│   │   ├── models/            # SQLModel models
│   │   │   ├── __init__.py
│   │   │   ├── task.py        # Task model (independent from Phase II)
│   │   │   ├── conversation.py # Conversation model
│   │   │   └── message.py     # Message model
│   │   ├── services/          # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── task_service.py  # Task CRUD (independent implementation)
│   │   │   └── chat_service.py  # Chat service with OpenAI
│   │   ├── mcp/               # MCP Server
│   │   │   ├── __init__.py
│   │   │   ├── server.py      # MCP server manager
│   │   │   └── tools.py       # MCP tool implementations
│   │   ├── routers/           # API routes
│   │   │   ├── __init__.py
│   │   │   └── chat.py        # Chat endpoint
│   │   └── schemas/           # Pydantic schemas
│   │       ├── __init__.py
│   │       ├── task.py
│   │       └── chat.py
│   └── tests/                 # Pytest tests
│       ├── conftest.py
│       ├── test_mcp_tools.py
│       └── test_chat.py
├── frontend/                   # OpenAI ChatKit UI
│   ├── package.json           # Bun package manager
│   ├── bun.lockb
│   ├── .env.example
│   ├── next.config.js
│   ├── app/
│   │   └── chat/
│   │       └── page.tsx
│   ├── components/
│   │   └── chat/
│   │       ├── ChatInterface.tsx
│   │       └── ChatMessage.tsx
│   └── lib/
│       ├── api/
│       │   └── chat.ts
│       └── auth.ts            # Better Auth integration
└── README.md
```

**Phase II Directory Structure** (Reference - COMPLETED):
```
phaseII/
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/    # Reusable UI components
│   │   ├── lib/           # Utilities, API client, stores
│   │   └── types/         # TypeScript type definitions
│   ├── public/
│   └── package.json
├── backend/
│   ├── src/
│   │   ├── routers/       # APIRouter modules
│   │   ├── models/        # SQLModel entities
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── core/          # Config, dependencies, security
│   ├── tests/
│   ├── alembic/
│   └── pyproject.toml
└── docker-compose.yml
```

**Phase IV Directory Structure** (COMPLETED):
```
phaseIV/
├── frontend/                    # Next.js frontend (from Phase III)
├── backend/                     # FastAPI backend (from Phase III)
├── kubernetes/                  # Kubernetes-specific artifacts
│   ├── helm/
│   │   └── todo-app/            # Helm chart (20 YAML templates)
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       ├── templates/
│   │       │   ├── frontend-deployment.yaml
│   │       │   ├── backend-deployment.yaml
│   │       │   ├── mcp-deployment.yaml
│   │       │   ├── redis-statefulset.yaml
│   │       │   ├── ingress.yaml
│   │       │   ├── hpa-frontend.yaml
│   │       │   ├── hpa-backend.yaml
│   │       │   └── ...
│   │       └── tests/
│   ├── scripts/                 # Deployment automation
│   │   ├── setup-minikube.sh
│   │   ├── deploy.sh
│   │   └── test.sh
│   └── docs/
│       ├── KUBERNETES_GUIDE.md
│       └── RUNBOOK.md
├── docker-compose.yml           # Local Docker Compose (from Phase III)
└── DOCKER_GUIDE.md              # Docker documentation
```

**Phase V Directory Structure** (ACTIVE):
```
phaseV/
├── frontend/                    # Next.js frontend (enhanced from Phase IV)
│   ├── src/
│   │   ├── app/
│   │   │   └── chat/
│   │   │       └── page.tsx     # Enhanced with priority/date prompts
│   │   └── lib/
├── backend/                     # FastAPI backend (enhanced from Phase IV)
│   ├── app/
│   │   ├── models/
│   │   │   ├── task.py          # Enhanced with priority, due_date, etc.
│   │   │   ├── category.py      # NEW: Category model
│   │   │   ├── tag.py           # NEW: Tag model (tags_phasev)
│   │   │   └── task_tag.py      # NEW: Junction table
│   │   ├── mcp/
│   │   │   └── tools.py         # Enhanced: 17 MCP tools total
│   │   ├── kafka/               # NEW: Kafka integration
│   │   │   ├── producer.py
│   │   │   └── events.py
│   │   ├── services/
│   │   │   ├── notification_service.py  # NEW: Kafka consumer
│   │   │   ├── recurring_task_service.py # NEW: Kafka consumer
│   │   │   └── search_service.py        # NEW: Full-text search
│   │   └── utils/
│   │       └── rrule_parser.py  # NEW: iCal RRULE parsing
│   ├── alembic/
│   │   └── versions/
│   │       └── YYYYMMDD_add_advanced_task_fields.py
│   └── tests/
├── kubernetes/                  # Kubernetes artifacts (extended from Phase IV)
│   ├── helm/
│   │   └── todo-app/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       ├── values-production.yaml   # NEW: Cloud production config
│   │       └── templates/
│   │           ├── notification-deployment.yaml  # NEW
│   │           ├── recurring-deployment.yaml     # NEW
│   │           ├── networkpolicy.yaml            # NEW
│   │           ├── prometheus-servicemonitor.yaml # NEW
│   │           └── ...
│   ├── dapr-components/         # NEW: Dapr configuration
│   │   ├── pubsub-kafka.yaml
│   │   ├── statestore-postgres.yaml
│   │   ├── secrets-kubernetes.yaml
│   │   └── jobs-scheduler.yaml
│   ├── scripts/
│   │   ├── setup-minikube.sh
│   │   ├── setup-dapr.sh        # NEW
│   │   ├── deploy.sh
│   │   ├── deploy-production.sh # NEW
│   │   └── test.sh
│   └── docs/
│       ├── KUBERNETES_GUIDE.md
│       ├── RUNBOOK.md
│       ├── ORACLE_CLOUD_SETUP.md    # NEW
│       ├── DAPR_GUIDE.md            # NEW
│       └── MONITORING_GUIDE.md      # NEW
├── .github/
│   └── workflows/               # NEW: CI/CD pipelines
│       ├── ci-phase-v.yml
│       └── deploy-production.yml
└── README.md
```

**Specs Directory Structure**:
```
specs/
├── sphaseI/               # Phase I specifications (COMPLETED)
│   ├── 001-add-task/
│   ├── 002-view-task/
│   └── ...
├── sphaseII/              # Phase II specifications (COMPLETED)
│   ├── 001-foundational-backend-setup/
│   ├── 002-task-tag-api/
│   └── ...
├── sphaseIII/             # Phase III specifications (COMPLETED)
│   ├── 001-mcp-server-setup/
│   ├── 002-chat-endpoint/
│   └── ...
├── sphaseIV/              # Phase IV specifications (COMPLETED)
│   └── 001-kubernetes-deployment/
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
└── sphaseV/               # Phase V specifications (ACTIVE)
    ├── 001-advanced-features/
    │   ├── spec.md
    │   ├── plan.md
    │   └── tasks.md
    ├── 002-dapr-integration/
    │   ├── spec.md
    │   ├── plan.md
    │   └── tasks.md
    └── 003-cloud-deployment/
        ├── spec.md
        ├── plan.md
        └── tasks.md
```

**Rationale**: Complete phase separation ensures each implementation is independent and can evolve without affecting other phases. This also demonstrates the ability to implement the same functionality using different architectural approaches.

---

### III. Persistent & Relational State

**Philosophy**: Production-grade persistence with cloud-native infrastructure.

**Requirements**:
- **Database**: Neon Serverless PostgreSQL as the single source of truth.
- **ORM**: SQLModel MUST be used for all data access (combines SQLAlchemy and Pydantic).
- **Async Access**: All database operations MUST use asyncpg driver for non-blocking I/O.
- **Migrations**: Schema changes MUST be managed via Alembic migrations:
  - Every schema change requires a migration file
  - Migrations MUST be reversible (include upgrade AND downgrade)
  - Migration naming: `YYYYMMDD_HHMMSS_descriptive_name.py`
- **Connection Pooling**: Production deployments MUST use connection pooling.
- **Data Isolation**: ALL database queries MUST scope to the authenticated user's ID from the JWT token, NOT from the path parameter. The JWT user_id is the authoritative source for determining data access rights.
- **Multi-User Isolation Testing**: All data access functions MUST include tests that verify User A cannot access User B's data, even with valid authentication.
- **Phase Table Separation**: Phase III MUST use separate tables (e.g., `tasks_phaseiii`) to avoid conflicts with Phase II data.
- **Phase V Full-Text Search**: Phase V MUST implement PostgreSQL tsvector with GIN indexes for full-text search on task titles and descriptions.

**Verification**:
- No raw SQL queries outside of migrations
- All queries include user_id filter from JWT token (enforced via FastAPI dependencies)
- Alembic migration history matches production schema
- Database connection uses async context managers
- Multi-user isolation tests pass for all endpoints
- Path parameter user_id validation is enforced at API level
- Full-text search indexes exist and are utilized (Phase V)

**Rationale**: Neon provides serverless PostgreSQL with automatic scaling, SQLModel provides type-safe data access, and Alembic ensures reproducible schema evolution across environments. The JWT user_id as the authoritative source ensures that even if path parameters are manipulated, data access remains secure.

---

### IV. User Authentication & JWT Security (The JWT Challenge)

**Philosophy**: Secure, stateless authentication with defense-in-depth token management.

**Requirements**:

**Authentication Flow**:
1. **Frontend Auth**: Better Auth library handles user signup/login UI on Next.js frontend with JWT plugin enabled. Frontend uses Better Auth client-side session management for user authentication state.
2. **Token Issuance**: Better Auth handles JWT token generation and management on the frontend. The Better Auth JWT plugin issues access tokens that are validated by the backend using a shared secret.
3. **Token Management**: Better Auth automatically manages token refresh and storage. Frontend MUST use Better Auth's built-in session management rather than implementing custom token storage.
4. **Token Attachment**: Frontend axios interceptor retrieves the Better Auth JWT token from the session and attaches it to `Authorization: Bearer <token>` header on all protected requests.
5. **Token Refresh Flow**: Better Auth handles automatic token refresh when needed. The backend only validates tokens according to the shared secret.
6. **Backend Validation**: FastAPI dependency validates Better Auth JWT tokens on all protected endpoints using the shared secret:
   - Verify signature with Better Auth shared secret key
   - Check expiration
   - Extract user_id from payload
   - **Path Parameter Matching**: When user ID appears in the API path (e.g., `/api/{user_id}/tasks`), the backend MUST compare the `user_id` extracted from the validated JWT against the `user_id` path parameter. If they do not match, return 403 Forbidden. This prevents users from accessing other users' resources even with a valid token.
   - **Data Scoping**: User ID from JWT payload MUST scope ALL database queries. All queries MUST be based on the JWT user_id, NOT the path parameter, to ensure data integrity.
7. **Secure Storage**: Better Auth manages token storage using browser storage mechanisms. The JWT plugin ensures secure handling of tokens.

**JWT Token Structure** (issued by Better Auth):
```json
{
  "sub": "<user_id>",
  "email": "<user_email>",
  "exp": "<expiration_timestamp>",
  "iat": "<issued_at_timestamp>",
  "role": "<user_role>"
}
```

**Security Standards**:
- MUST use HS256 algorithm with Better Auth shared secret
- Secret keys MUST be at least 256 bits
- Rate limiting on auth endpoints: 5 attempts per minute per IP
- All API endpoints that accept user_id in path MUST validate that the JWT user_id matches the path user_id

**Future Scope**:
The following security features are explicitly OUT OF SCOPE for current phases and targeted for future implementation:
- **Refresh token rotation**: Rotating refresh tokens on each use
- **Token blacklisting**: Server-side token revocation for logout

**Rationale**: These features add complexity that exceeds current scope. The current implementation provides adequate security for the MVP while clearly identifying enhancement paths.

**Verification**:
- All protected routes return 401 without valid token
- Expired tokens return 401 and trigger refresh flow through Better Auth
- User A cannot access User B's data (data isolation test)
- Path parameter user ID mismatches return 403 Forbidden
- All database queries are scoped to JWT user_id, not path parameter

**Rationale**: Using Better Auth's JWT plugin simplifies frontend authentication while maintaining security through shared secret validation on the backend. The path parameter validation ensures that users can only access resources that belong to them.

---

### V. Backend Architecture Standards

**Philosophy**: Clean, testable, and maintainable API design.

**Requirements**:

**Router Organization**:
- Endpoints organized in `/backend/src/routers/` (Phase II) or `/backend/app/routers/` (Phase III/IV/V) using FastAPI APIRouter
- One router file per resource domain (e.g., `tasks.py`, `auth.py`, `chat.py`)
- Routers registered in `main.py` with version prefix

**API Versioning**:
- ALL routes prefixed with `/api/v1/` or `/api/{user_id}/`
- Version changes require new router files (e.g., `/api/v2/tasks`)
- Breaking changes MUST increment API version

**Configuration**:
- pydantic-settings for environment-based configuration
- `.env` files for local development (NEVER committed)
- Environment variables for production secrets
- `Settings` class validates all config on startup

**Documentation**:
- FastAPI automatic OpenAPI documentation MUST be enabled
- Swagger UI available at `/docs`
- ReDoc available at `/redoc`
- All endpoints MUST have docstrings describing behavior

**Security**:
- CORS policy MUST restrict to deployed frontend domain only
- Local development may allow localhost origins
- All inputs validated via Pydantic models
- SQL injection prevented via SQLModel parameterization
- Rate limiting on sensitive endpoints

**Error Handling**:
- Consistent error response format:
  ```json
  {
    "detail": "Human-readable message",
    "code": "ERROR_CODE",
    "field": "optional_field_name"
  }
  ```
- Standard HTTP status codes (400, 401, 403, 404, 422, 500)
- No stack traces in production responses

**Logging**:
- Structured JSON logging in production
- Request ID tracking across services
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Pre-commit Hooks**:
- `ruff check` - linting MUST pass
- `ruff format` - formatting MUST pass
- `pip-audit` - security vulnerability check

**Rationale**: Consistent API design enables frontend predictability, proper error handling improves debugging, and pre-commit hooks catch issues before they enter the codebase.

---

### VI. Frontend Architecture Standards

**Philosophy**: Fast, accessible, and delightful user experience.

**Phase II Frontend Requirements**:

**Component Structure**:
- Feature-based or type-based organization (choose one, be consistent)
- Feature-based example: `/components/tasks/TaskCard.tsx`
- Type-based example: `/components/ui/Button.tsx`
- shadcn/ui components in `/components/ui/`

**State Management**:
- Zustand for global state (auth state, user preferences)
- React Query or SWR for server state (tasks, tags)
- Local component state for UI-only state

**Authentication Integration**:
- Better Auth library MUST be used for all authentication functionality
- User sessions managed through Better Auth client-side session management
- API client at `@/lib/api-client` MUST be implemented to handle Better Auth token attachment
- Axios interceptor MUST retrieve Better Auth JWT token and attach to `Authorization: Bearer <token>` header
- User ID MUST be extracted from Better Auth session for URL construction with new API pattern

**API Client Implementation**:
- Create API client at `@/lib/api-client` that integrates with Better Auth
- Client MUST construct URLs using the pattern `/api/{user_id}/{resources}` using the user ID from session
- Client MUST handle 403 Forbidden responses by redirecting to appropriate error states
- Client MUST handle 401 Unauthorized responses by allowing Better Auth to manage token refresh

**Phase III Frontend Requirements**:

**OpenAI ChatKit Integration**:
- MUST use OpenAI ChatKit for the chat interface
- Domain allowlist MUST be configured in OpenAI platform settings
- ChatKit domain key MUST be obtained and configured

**Chat Interface Requirements**:
- Message display with user/assistant role differentiation
- Loading states during AI processing
- Tool call visualization (show which MCP tools were invoked)
- Conversation history display
- Error handling with graceful recovery

**Phase V Frontend Enhancements**:

**Enhanced ChatKit Prompts**:
- Suggested prompts MUST include priority-aware commands (e.g., "Add a high priority task...")
- Suggested prompts MUST include date-aware commands (e.g., "Show tasks due this week")
- Suggested prompts MUST include recurring task commands (e.g., "Create a recurring task...")
- Suggested prompts MUST include search commands (e.g., "Search for tasks about...")

**Common Requirements (All Phases)**:

**Environment Variables**:
- `NEXT_PUBLIC_` prefix for browser-exposed variables
- Server-only variables for API keys and secrets
- Type-safe env access via zod validation

**User Experience Standards**:
- **Optimistic UI Updates**: UI updates immediately, reverts on server error
- **Skeleton Loading States**: Show content placeholders during data fetch
- **Toast Notifications**: Non-blocking feedback for actions (success, error)
- **Input Debouncing**: 300ms debounce on search inputs
- **Error Boundaries**: Graceful error handling with recovery options
- **Responsive Design**: Mobile-first, works on all screen sizes

**Accessibility Standards**:
- ARIA labels on interactive elements
- Keyboard navigation support
- Color contrast meets WCAG AA
- Focus management for modals and dialogs

**Performance Standards**:
- First Contentful Paint < 1.5s
- Time to Interactive < 3s
- Bundle size monitoring in CI

**Rationale**: Consistent UX patterns reduce user frustration, optimistic updates feel instant, and accessibility ensures the app works for everyone.

---

### VII. Automated Testing Standards

**Philosophy**: Comprehensive testing enables confident refactoring and continuous deployment.

**Backend Testing Requirements**:
- **Framework**: pytest with pytest-asyncio for async tests
- **Database Isolation**: testcontainers for isolated PostgreSQL per test suite
- **Test Categories**:
  - Unit tests: Business logic in `/services/`
  - Integration tests: API endpoints with database
  - Contract tests: API schema validation
- **Coverage**: Minimum 80% code coverage on core logic
- **Execution**: `cd backend && uv run pytest`

**Frontend Testing Requirements**:
- **Framework**: Vitest (or Jest) with React Testing Library
- **Test Categories**:
  - Unit tests: Utility functions, hooks
  - Component tests: Isolated component behavior
  - Integration tests: User flows with MSW mocking
- **Coverage**: Minimum 70% code coverage on components
- **Execution**: `cd frontend && bun test`

**Phase III Specific Testing**:
- **MCP Tool Tests**: All 5 MCP tools MUST have unit tests
- **Chat Service Tests**: Conversation flow, tool invocation, error handling
- **Integration Tests**: End-to-end chat interactions with mocked OpenAI responses

**Phase V Specific Testing**:
- **MCP Tool Tests**: All 17 MCP tools MUST have unit tests
- **Kafka Event Tests**: Event publishing and consumption tests
- **Search Service Tests**: Full-text search accuracy and ranking tests
- **Dapr Integration Tests**: Pub/Sub, State, Jobs API tests
- **Load Tests**: HPA scaling, Kafka throughput, concurrent users
- **Resilience Tests**: Pod failures, database failures, Kafka broker failures

**End-to-End Testing (Optional)**:
- Playwright for critical user journeys
- Run in CI on staging deployments

**Test Naming Convention**:
- `test_<action>_<condition>_<expected_result>`
- Example: `test_create_task_with_empty_title_returns_400`

**Verification**:
- All tests pass before merge (enforced in CI)
- Coverage reports generated and tracked
- No skipped tests without justification comment

**Rationale**: Comprehensive testing catches regressions, enables refactoring, and provides documentation of expected behavior.

---

### VIII. Containerization & Deployment

**Philosophy**: Environment parity from development to production.

**Requirements**:

**Docker Configuration**:
- `Dockerfile` in each phase's `/frontend` for production build
- `Dockerfile` in each phase's `/backend` for production build
- `docker-compose.yml` at phase root for local development environment
- Multi-stage builds to minimize image size

**Local Development**:
- `docker-compose up` starts all services (frontend, backend, database)
- Hot-reload enabled for both frontend and backend
- Local PostgreSQL or Neon dev branch for database

**Environment Management**:
- Development: Local Docker Compose or direct processes
- Staging: Auto-deploy from main branch
- Production: Deploy from tagged releases

**Health Checks**:
- Backend: `/health` endpoint returns service status
- Frontend: Next.js built-in health checks
- Database: Connection verification on startup

**Rationale**: Docker ensures consistent environments, reduces "works on my machine" issues, and simplifies deployment pipeline.

---

### IX. CI/CD Pipeline

**Philosophy**: Automated quality gates and deployment with practical iteration speed.

**Requirements**:

**GitHub Actions Workflows**:

**PR Checks** (on pull_request) - Fast feedback for developers:
- Lint frontend: `bun run lint`
- Lint backend: `ruff check .`
- Test frontend: `bun test`
- Test backend: `uv run pytest`
- Build frontend: `bun run build`
- Type check frontend: `bun run typecheck`
- **Coverage Gate**: PR MUST NOT decrease overall test coverage percentage (compare against main branch baseline)

**Nightly Pipeline** (scheduled, runs on main branch) - Comprehensive health checks:
- All PR checks
- **Coverage Threshold Check**: Backend coverage >= 80%, Frontend coverage >= 70%
- **Performance Audit**: Lighthouse Performance score >= 90
- **Security Scan**: Dependency vulnerability audit
- **Report Generation**: Publish results to team dashboard/notifications
- **Non-blocking**: Failures generate alerts but do not block development

**Rationale for Pipeline Separation**: Expensive performance audits and strict threshold checks on every PR slow development velocity. Moving these to a nightly pipeline maintains quality standards while enabling faster iteration. PRs focus on not regressing quality; nightly checks ensure absolute thresholds are met.

**Staging Deploy** (on push to main):
- All PR checks pass
- Auto-deploy to staging environment
- Run smoke tests against staging

**Production Deploy** (on release tag):
- All checks pass
- Manual approval (optional)
- Deploy to production environment
- Tag docker images with version

**Phase V CI/CD Additions**:
- **ci-phase-v.yml**: Lint, test, build for Phase V (backend + frontend)
- **deploy-production.yml**: Deploy to Oracle Cloud OKE on release tags
- **Helm Lint**: `helm lint` passes with zero warnings
- **Helm Template Validation**: `helm template --dry-run` validates manifests
- **Smoke Tests**: Health endpoint verification post-deployment
- **Rollback Automation**: Automatic `helm rollback` on failed smoke tests

**Branch Protection**:
- main branch requires PR
- PRs require passing CI checks
- PRs require at least 1 approval (if team > 1)

**Secrets Management**:
- GitHub Secrets for deployment credentials
- Rotate secrets quarterly
- Never commit secrets to repository

**Rationale**: CI/CD automation ensures consistent quality, prevents broken deployments, and enables rapid iteration while nightly checks maintain long-term code health.

---

### X. Feature Scope Evolution

**Philosophy**: Expand core functionality progressively across phases.

**Phase II Features (COMPLETED)**:

**Basic Features (Priority P1 - MVP)**:
1. **Add Task** - Create task with title, description, priority
2. **View Tasks** - Display paginated task list with status indicators
3. **Update Task** - Modify task title, description, priority, due date
4. **Delete Task** - Remove task with confirmation
5. **Mark Complete** - Toggle task completion status

**Intermediate Features (Priority P2)**:
6. **Priorities** - High, Medium, Low priority assignment
7. **Tags/Categories** - Create, assign, and manage task tags
8. **Search** - Full-text search across task titles and descriptions
9. **Filter** - Filter by status (all, pending, completed), priority, tag
10. **Sort** - Sort by due date, priority, creation date, title

**Advanced Features (Priority P3)**:
11. **Due Dates** - Set due dates with visual indicators
12. **Time Reminders** - Browser push notifications for due tasks
13. **Recurring Tasks** - iCal RRULE format for recurring schedules

**Explicitly Out of Scope for Phase II**:
- Team/organization features
- Task sharing or collaboration
- File attachments
- Subtasks or task dependencies
- Integrations with external services (calendar, email)
- Mobile native applications

**Phase III MCP Tools (COMPLETED)**:
- 5 MCP tools: add_task, list_tasks, complete_task, delete_task, update_task

**Phase V MCP Tools (ACTIVE)**:

**Enhanced Existing Tools (5 tools)**:
1. **add_task** - Enhanced with priority, due_date, category_id, tag_ids, recurrence_rule
2. **list_tasks** - Enhanced with priority, category_id, tag_id, due_before, due_after, sort_by filters
3. **complete_task** - Unchanged
4. **delete_task** - Unchanged
5. **update_task** - Enhanced with priority, due_date, category_id, tag_ids, recurrence_rule

**New Tools (12 tools)**:
6. **search_tasks** - Full-text search with PostgreSQL tsvector
7. **add_category** - Create category with name, color
8. **list_categories** - List user's categories
9. **delete_category** - Remove category
10. **add_tag** - Create tag with name, color
11. **list_tags** - List user's tags
12. **delete_tag** - Remove tag
13. **add_tag_to_task** - Associate tag with task
14. **remove_tag_from_task** - Disassociate tag from task
15. **set_reminder** - Schedule reminder for task
16. **get_overdue_tasks** - List tasks past due date
17. **get_upcoming_tasks** - List tasks due within N days

**Total Phase V MCP Tools**: 17

**Rationale**: Prioritized feature scope ensures MVP delivery while planning for valuable enhancements without scope creep. Phase V dramatically expands MCP tool capabilities to support advanced task management.

---

### XI. MCP Server Architecture (Phase III/V)

**Philosophy**: Standardized interface for AI to interact with the application through stateless, database-backed tools.

**Requirements**:

**MCP Server Setup**:
- MUST use the official MCP SDK: https://github.com/modelcontextprotocol/python-sdk
- Phase III: Server MUST expose exactly 5 tools for task operations
- Phase V: Server MUST expose exactly 17 tools (5 enhanced + 12 new)
- All tools MUST be stateless - no in-memory state between requests
- All state MUST be persisted to the database

**Phase III Tool Specifications** (5 tools):

| Tool | Purpose | Required Parameters | Optional Parameters |
|------|---------|---------------------|---------------------|
| `add_task` | Create a new task | `user_id`, `title` | `description` |
| `list_tasks` | Retrieve user's tasks | `user_id` | `status` (all/pending/completed) |
| `complete_task` | Mark task as complete | `user_id`, `task_id` | - |
| `delete_task` | Remove a task | `user_id`, `task_id` | - |
| `update_task` | Modify task | `user_id`, `task_id` | `title`, `description` |

**Phase V Enhanced Tool Specifications** (17 tools):

| Tool | Purpose | Required Parameters | Optional Parameters |
|------|---------|---------------------|---------------------|
| `add_task` | Create task with advanced fields | `user_id`, `title` | `description`, `priority`, `due_date`, `category_id`, `tag_ids`, `recurrence_rule` |
| `list_tasks` | Retrieve with filters | `user_id` | `status`, `priority`, `category_id`, `tag_id`, `due_before`, `due_after`, `sort_by` |
| `complete_task` | Mark task as complete | `user_id`, `task_id` | - |
| `delete_task` | Remove a task | `user_id`, `task_id` | - |
| `update_task` | Modify task with advanced fields | `user_id`, `task_id` | `title`, `description`, `priority`, `due_date`, `category_id`, `tag_ids`, `recurrence_rule` |
| `search_tasks` | Full-text search | `user_id`, `query` | `status`, `limit` |
| `add_category` | Create category | `user_id`, `name` | `color` |
| `list_categories` | List categories | `user_id` | - |
| `delete_category` | Remove category | `user_id`, `category_id` | - |
| `add_tag` | Create tag | `user_id`, `name` | `color` |
| `list_tags` | List tags | `user_id` | - |
| `delete_tag` | Remove tag | `user_id`, `tag_id` | - |
| `add_tag_to_task` | Associate tag | `user_id`, `task_id`, `tag_id` | - |
| `remove_tag_from_task` | Disassociate tag | `user_id`, `task_id`, `tag_id` | - |
| `set_reminder` | Schedule reminder | `user_id`, `task_id`, `remind_before_minutes` | - |
| `get_overdue_tasks` | List overdue | `user_id` | - |
| `get_upcoming_tasks` | List upcoming | `user_id` | `days` |

**Tool Response Format**:
```json
{
  "task_id": <integer>,
  "status": "<created|completed|deleted|updated>",
  "title": "<task_title>"
}
```

**Error Handling**:
- Tool errors MUST return descriptive error messages
- Invalid task_id MUST return "Task not found" error
- All errors MUST be gracefully handled without crashing the server

**Phase V Event Publishing**:
- All MCP tools MUST publish events to Kafka after successful operations
- Event topics: `task-events`, `reminders`, `task-updates`
- Event publishing MUST be asynchronous (non-blocking)

**Rationale**: MCP provides a standardized interface for AI agents to interact with the application, enabling tool composition and clear separation between AI logic and application logic.

---

### XII. OpenAI Agents SDK Integration (Phase III/V)

**Philosophy**: Leverage OpenAI's agent framework for natural language task management.

**Requirements**:

**SDK Integration**:
- MUST use OpenAI Agents SDK: https://github.com/openai/openai-agents-python
- Agent MUST be configured with MCP tools for task operations
- Agent MUST understand natural language intent and invoke appropriate tools

**Agent Behavior Specification** (Phase III):

| User Intent | Agent Action |
|-------------|--------------|
| Adding/creating/remembering something | Invoke `add_task` |
| Viewing/showing/listing tasks | Invoke `list_tasks` with appropriate filter |
| Done/complete/finished with task | Invoke `complete_task` |
| Delete/remove/cancel task | Invoke `delete_task` |
| Change/update/rename task | Invoke `update_task` |

**Agent Behavior Specification** (Phase V Enhanced):

| User Intent | Agent Action |
|-------------|--------------|
| Adding task with priority/date | Invoke `add_task` with priority, due_date |
| Searching for tasks | Invoke `search_tasks` with query |
| Filtering by priority/category/tag | Invoke `list_tasks` with filters |
| Creating recurring task | Invoke `add_task` with recurrence_rule |
| Managing categories | Invoke category tools |
| Managing tags | Invoke tag tools |
| Setting reminders | Invoke `set_reminder` |
| Checking overdue tasks | Invoke `get_overdue_tasks` |
| Checking upcoming tasks | Invoke `get_upcoming_tasks` |

**Conversation Context**:
- Agent MUST receive last 20 messages for context
- Conversation history MUST be loaded from database
- New messages MUST be stored before agent invocation

**Response Requirements**:
- Agent MUST confirm actions with friendly responses
- Agent MUST explain what tools were invoked
- Agent MUST handle errors gracefully with helpful messages

**Rationale**: OpenAI Agents SDK provides robust AI capabilities for natural language understanding and tool invocation, enabling intuitive conversational task management.

---

### XIII. Conversational AI Standards (Phase III/V)

**Philosophy**: Stateless server architecture with database-persisted conversation state.

**Requirements**:

**Stateless Architecture**:
- Server MUST NOT hold conversation state in memory
- Each request MUST be independent and self-contained
- Server MUST be horizontally scalable
- Server restart MUST NOT lose conversation data

**Conversation Flow (Request Cycle)**:
1. Receive user message via API
2. Fetch conversation history from database (if conversation_id provided)
3. Build message array for agent (history + new message)
4. Store user message in database
5. Run agent with MCP tools
6. Agent invokes appropriate MCP tool(s)
7. Store assistant response in database
8. Return response to client
9. Server holds NO state (ready for next request)

**Conversation Persistence**:
- Conversations MUST be stored in `conversations` table
- Messages MUST be stored in `messages` table with conversation_id reference
- Messages MUST include role (user/assistant) and content
- Messages MUST be ordered by created_at timestamp

**Natural Language Commands** (Phase III):
The chatbot MUST understand and respond to:
| User Says | Agent Should |
|-----------|--------------|
| "Add a task to buy groceries" | Call `add_task` with title "Buy groceries" |
| "Show me all my tasks" | Call `list_tasks` with status "all" |
| "What's pending?" | Call `list_tasks` with status "pending" |
| "Mark task 3 as complete" | Call `complete_task` with task_id 3 |
| "Delete the meeting task" | Call `list_tasks` first, then `delete_task` |
| "Change task 1 to 'Call mom tonight'" | Call `update_task` with new title |
| "I need to remember to pay bills" | Call `add_task` with title "Pay bills" |
| "What have I completed?" | Call `list_tasks` with status "completed" |

**Natural Language Commands** (Phase V Enhanced):
| User Says | Agent Should |
|-----------|--------------|
| "Add a high priority task to finish report by Friday" | Call `add_task` with priority="high", due_date, title |
| "Show me all urgent tasks due this week" | Call `list_tasks` with priority="urgent", due_before |
| "Create a recurring task to review emails every Monday" | Call `add_task` with recurrence_rule="FREQ=WEEKLY;BYDAY=MO" |
| "Search for tasks about budget" | Call `search_tasks` with query="budget" |
| "What's overdue?" | Call `get_overdue_tasks` |
| "Show tasks due in the next 7 days" | Call `get_upcoming_tasks` with days=7 |
| "Add a tag 'work' to task 5" | Call `add_tag_to_task` with task_id=5 |
| "Set a reminder for task 3, 30 minutes before" | Call `set_reminder` with remind_before_minutes=30 |

**Rationale**: Stateless architecture enables scalability and resilience while database persistence ensures conversation continuity across requests and server restarts.

---

### XIV. Containerization & Orchestration (Phase IV/V)

**Philosophy**: Infrastructure as Code with declarative Kubernetes configuration.

**Requirements**:

**Container Runtime**:
- Docker Desktop as the container runtime
- Multi-stage Dockerfiles for optimized image sizes
- Docker images as deployment artifacts (not source code)
- Container health checks (liveness and readiness probes)

**Kubernetes Orchestration**:
- Minikube for local Kubernetes cluster (4 CPU, 8GB RAM minimum)
- Phase IV namespace: `todo-phaseiv`
- Phase V namespace: `todo-phasev`
- Service communication via ClusterIP and internal DNS
- Declarative YAML manifests for all resources

**Helm Package Management**:
- Helm v3.13+ for templating and package management
- Chart follows Helm best practices
- Values externalized in values.yaml
- Templating for environment-specific configuration
- helm lint passes with zero warnings
- helm test validates deployment

**Infrastructure as Code Principles**:
- All infrastructure defined in version control
- Reproducible deployments across environments
- No manual kubectl apply of raw YAML
- Git-tracked Helm charts and values

**Service Architecture** (Phase IV):
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

**Service Architecture** (Phase V Enhanced):
```
Kubernetes Cluster (todo-phasev namespace)
├── Frontend Deployment (2-5 replicas, HPA, Dapr sidecar)
├── Backend Deployment (2-5 replicas, HPA, Dapr sidecar)
├── MCP Server Deployment (1 replica, Dapr sidecar)
├── Notification Service Deployment (1 replica, Dapr sidecar)
├── Recurring Task Service Deployment (1 replica, Dapr sidecar)
├── Redis StatefulSet (1 replica, 1Gi PVC)
├── Dapr System (dapr-system namespace)
│   ├── dapr-operator
│   ├── dapr-sidecar-injector
│   ├── dapr-placement
│   └── dapr-sentry
├── Dapr Components
│   ├── pubsub-kafka (Redpanda Cloud)
│   ├── statestore-postgres
│   ├── secrets-kubernetes
│   └── jobs-scheduler
├── Nginx Ingress (HTTPS with cert-manager)
│   ├── / → frontend:3000
│   └── /api → backend:8000
├── Monitoring Stack
│   ├── Prometheus
│   └── Grafana
└── External Services
    ├── Neon PostgreSQL
    └── Redpanda Cloud (Kafka)
```

**Rationale**: Kubernetes provides production-grade orchestration, Helm enables reusable deployment templates, and Infrastructure as Code ensures reproducibility.

---

### XV. Production-Grade Deployment (Phase IV/V)

**Philosophy**: Production-ready features even in local development environments.

**Requirements**:

**Nginx Ingress Controller (MANDATORY)**:
- MUST use Nginx Ingress Controller for HTTP routing
- Single entry point at todo-app.local (Phase IV) or custom domain (Phase V)
- Path-based routing (/ --> frontend, /api --> backend)
- Ingress annotations for CORS, rate limiting (optional)
- TLS termination support (required for Phase V cloud)

**Horizontal Pod Autoscaling (MANDATORY)**:
- Frontend HPA: min 2, max 5 replicas (local) / min 3, max 10 replicas (cloud)
- Backend HPA: min 2, max 5 replicas (local) / min 3, max 10 replicas (cloud)
- CPU target: 70%
- Memory target: 80%
- Metrics Server MUST be enabled in Minikube
- HPA status MUST show scaling activity

**Persistent Volumes (MANDATORY)**:
- Redis StatefulSet with 1Gi PersistentVolumeClaim (local) / 10Gi (cloud)
- Standard StorageClass (Minikube default) / oci-bv (Oracle Cloud)
- Data persists across pod restarts
- PVC bound status verified

**Health Probes (MANDATORY)**:
- Liveness probes for all services (frontend, backend, mcp, redis)
- Readiness probes for all services
- Probes configured with appropriate timeouts and thresholds
- Failed probes trigger pod restarts

**Resource Limits and Requests (MANDATORY)**:
- CPU requests and limits defined for all containers
- Memory requests and limits defined for all containers
- Resource quotas prevent cluster overcommitment
- QoS classes: Guaranteed or Burstable (not BestEffort)

**Observability (RECOMMENDED for Phase IV, MANDATORY for Phase V)**:
- Metrics Server for HPA and resource monitoring
- kubectl top pods/nodes commands functional
- Pod logs accessible via kubectl logs
- Phase V: Prometheus/Grafana integration required

**Testing Requirements**:
- helm test passes
- End-to-end test covers complete user flow
- Load test validates HPA scaling
- Resilience test validates pod restart recovery
- Persistence test validates Redis data retention
- Ingress test validates HTTP routing

**Rationale**: Production-grade features in local development prepare deployments for real-world conditions and demonstrate Kubernetes capabilities.

---

### XVI. Event-Driven Architecture with Kafka (Phase V Only)

**Philosophy**: Decoupled, scalable microservices architecture where services communicate through events.

**Requirements**:

**Kafka/Redpanda Setup**:
- MUST use Redpanda Cloud (serverless free tier) for managed Kafka
- Alternative: Self-hosted Kafka via Strimzi operator on Kubernetes
- Bootstrap server URL and credentials stored in Kubernetes Secrets
- TLS enabled for production connections

**Kafka Topics** (3 required):

| Topic | Producer | Consumers | Purpose |
|-------|----------|-----------|---------|
| `task-events` | All MCP tools | Recurring Task Service, Audit Service | All task CRUD operations |
| `reminders` | Backend (when due_date set) | Notification Service | Scheduled reminder triggers |
| `task-updates` | All MCP tools | WebSocket Service (future) | Real-time client sync |

**Event Schemas**:

**Task Event Schema**:
```json
{
  "event_type": "created|updated|completed|deleted",
  "task_id": "<integer>",
  "task_data": {
    "title": "<string>",
    "description": "<string>",
    "priority": "<low|medium|high|urgent>",
    "due_date": "<ISO 8601 datetime>",
    "completed": "<boolean>"
  },
  "user_id": "<string>",
  "timestamp": "<ISO 8601 datetime>"
}
```

**Reminder Event Schema**:
```json
{
  "task_id": "<integer>",
  "title": "<string>",
  "due_at": "<ISO 8601 datetime>",
  "remind_at": "<ISO 8601 datetime>",
  "user_id": "<string>"
}
```

**Event Producer Integration**:
- MCP tools MUST publish events after successful database operations
- Event publishing MUST be asynchronous (non-blocking)
- Failed event publishing MUST NOT fail the main operation (log and continue)
- Use aiokafka library for async Python Kafka client

**Event Consumer Services**:

**Notification Service**:
- Consumes from `reminders` topic
- Sends browser push notifications at scheduled time
- Marks `reminder_sent=True` in database
- Runs as separate Kubernetes Deployment

**Recurring Task Service**:
- Consumes from `task-events` topic
- Listens for `completed` events on tasks with `recurrence_rule`
- Parses iCal RRULE, calculates next occurrence
- Automatically creates new task instance
- Runs as separate Kubernetes Deployment

**Implementation Pattern**:
```python
# In MCP tool
async def add_task(...):
    # 1. Create task in database
    task = await create_task_in_db(...)

    # 2. Publish event to Kafka (non-blocking)
    await kafka_producer.send(
        topic="task-events",
        value={
            "event_type": "created",
            "task_id": task.id,
            "task_data": task.dict(),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    # 3. If due_date set, publish reminder event
    if task.due_date:
        await publish_reminder_event(task)

    return task
```

**Error Handling**:
- Consumer errors MUST be logged with full context
- Failed event processing MUST NOT crash the consumer
- Dead letter queue for unprocessable events (optional)
- Idempotent consumers to handle duplicate events

**Verification**:
- Events published for all task operations
- Notification Service processes reminder events
- Recurring Task Service creates new task instances
- Kafka consumer lag monitoring configured

**Rationale**: Kafka enables decoupled microservices where the Chat API publishes events and specialized services (Notification, Recurring Task) consume and process them independently, enabling scalability and resilience.

---

### XVII. Distributed Application Runtime with Dapr (Phase V Only)

**Philosophy**: Abstract infrastructure dependencies behind a unified API layer.

**Requirements**:

**Dapr Installation**:
- MUST install Dapr v1.12+ on Kubernetes
- Use Dapr CLI: `dapr init -k --wait`
- Verify components: dapr-operator, dapr-sidecar-injector, dapr-placement, dapr-sentry

**Dapr Components** (4 required):

**1. Pub/Sub Component (Kafka)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-phasev
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "<REDPANDA_URL>:9092"
    - name: authType
      value: "sasl"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
    - name: consumerGroup
      value: "todo-service"
```

**2. State Store Component (PostgreSQL)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-phasev
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: todo-app-secrets
        key: DATABASE_URL
    - name: tableName
      value: "dapr_state"
```

**3. Secrets Store Component**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: todo-phasev
spec:
  type: secretstores.kubernetes
  version: v1
```

**4. Jobs API Component**:
- Used for scheduling exact-time reminders
- Replaces cron-based polling with event-driven scheduling

**Dapr Sidecar Injection**:
All service deployments MUST include Dapr annotations:
```yaml
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "<service-name>"
        dapr.io/app-port: "<port>"
        dapr.io/log-level: "info"
```

**Infrastructure Abstraction**:
- Application code MUST NOT use direct Kafka clients (aiokafka)
- Application code MUST use Dapr HTTP API for Pub/Sub
- Benefit: Kafka can be swapped for Redis, RabbitMQ, etc. without code changes

**Dapr API Usage**:

**Publish Event**:
```python
# Replace direct Kafka with Dapr
await httpx.post(
    "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
    json=event
)
```

**Subscribe to Events**:
```python
@app.post("/dapr/subscribe")
async def subscribe():
    return [
        {"pubsubname": "kafka-pubsub", "topic": "task-events", "route": "/events/task"},
        {"pubsubname": "kafka-pubsub", "topic": "reminders", "route": "/events/reminder"}
    ]

@app.post("/events/task")
async def handle_task_event(request: Request):
    event = await request.json()
    # Process event
    return {"status": "SUCCESS"}
```

**Jobs API for Reminders**:
```python
# Schedule exact-time reminder
await httpx.post(
    f"http://localhost:3500/v1.0-alpha1/jobs/reminder-task-{task_id}",
    json={
        "dueTime": remind_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data": {"task_id": task_id, "user_id": user_id, "type": "reminder"}
    }
)

# Callback endpoint
@app.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    job_data = await request.json()
    # Process scheduled job
    return {"status": "SUCCESS"}
```

**Verification**:
- Dapr system pods running in dapr-system namespace
- All 4 Dapr components configured and loaded
- Services using Dapr HTTP API (not direct infrastructure clients)
- Dapr sidecar logs show successful operation
- Events flowing through Dapr Pub/Sub

**Rationale**: Dapr provides infrastructure abstraction, enabling portable microservices that can run on any cloud or local environment without changing application code.

---

### XVIII. Production Cloud Deployment (Phase V Only)

**Philosophy**: Production-grade cloud infrastructure with security, monitoring, and automation.

**Requirements**:

**Oracle Cloud OKE Setup**:
- MUST use Oracle Cloud OKE (Oracle Kubernetes Engine)
- Always Free tier: 4 OCPUs, 24GB RAM, 200GB storage
- Create OKE cluster with 2 nodes (VM.Standard.A1.Flex shape)
- Kubernetes version: v1.28+
- Namespace: `todo-phasev`

**Container Registry**:
- Use Oracle Container Registry (OCIR) for Docker images
- Image naming: `<region>.ocir.io/<tenancy>/todo-<service>:<tag>`
- Images tagged with git commit SHA and semantic version

**HTTPS with cert-manager**:
- MUST install cert-manager for automatic TLS certificates
- Use Let's Encrypt production issuer
- Configure ClusterIssuer with HTTP-01 challenge
- Ingress annotations: `cert-manager.io/cluster-issuer: letsencrypt-prod`

**Production Helm Values**:
```yaml
# values-production.yaml
environment: production
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: todo.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: todo-tls
      hosts:
        - todo.example.com
frontend:
  replicas: 3
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
backend:
  replicas: 3
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
redis:
  persistence:
    size: 10Gi
    storageClass: oci-bv
```

**CI/CD Pipeline (GitHub Actions)**:

**CI Workflow** (`ci-phase-v.yml`):
- Trigger: On pull_request and push to main for phaseV/** paths
- Jobs: lint-backend, test-backend, lint-frontend, test-frontend, build-images, helm-lint
- Build and push images to OCIR on main branch

**Deploy Workflow** (`deploy-production.yml`):
- Trigger: On release published
- Environment: production (with manual approval)
- Steps: Configure kubectl, helm upgrade, smoke tests, Slack notification on failure

**Monitoring Stack**:

**Prometheus + Grafana**:
- Install kube-prometheus-stack via Helm
- ServiceMonitor for backend metrics (/metrics endpoint)
- Custom Grafana dashboards for HTTP requests, task operations, pod resources

**Backend Metrics Instrumentation**:
```python
from prometheus_client import Counter, Histogram, make_asgi_app

http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
task_operations_total = Counter('task_operations_total', 'Total task operations', ['operation', 'user_id'])

app.mount("/metrics", make_asgi_app())
```

**Security Hardening**:

**Network Policies**:
- Default deny-all ingress/egress
- Allow specific pod-to-pod communication
- Backend only accepts from frontend pods
- Redis only accepts from backend/mcp pods

**RBAC**:
- Service accounts for each service
- Role bindings with least-privilege permissions
- Secrets access limited to required services only

**Pod Security Standards**:
- `runAsNonRoot: true`
- `allowPrivilegeEscalation: false`
- `readOnlyRootFilesystem: true`
- Drop all capabilities

**Resource Quotas**:
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: todo-phasev-quota
  namespace: todo-phasev
spec:
  hard:
    requests.cpu: "8"
    requests.memory: "16Gi"
    limits.cpu: "16"
    limits.memory: "32Gi"
    pods: "50"
```

**Backup Strategy**:
- Install Velero for Kubernetes resource backups
- Schedule daily backups of todo-phasev namespace
- Configure OCI Object Storage as backup destination

**Verification**:
- OKE cluster accessible via kubectl
- Services deployed with HTTPS enabled
- Let's Encrypt certificates valid
- CI/CD pipeline executing on PR and release
- Prometheus collecting metrics
- Grafana dashboards displaying data
- Network policies enforcing traffic rules
- RBAC limiting service permissions

**Rationale**: Production cloud deployment with security hardening, monitoring, and CI/CD automation demonstrates enterprise-grade infrastructure practices.

---

## Data Model Specification

### Phase II Data Models

#### User Entity (SQLModel)

| Field      | Type   | Constraints                          | Description                         |
|------------|--------|--------------------------------------|-------------------------------------|
| id         | str    | PRIMARY KEY                          | User ID from Better Auth            |
| email      | str    | UNIQUE, NOT NULL                     | User's email address                |
| name       | str    | NULLABLE                             | User's display name                 |
| created_at | datetime | NOT NULL, DEFAULT now()            | Account creation timestamp          |

#### Tag Entity (SQLModel)

| Field    | Type   | Constraints                          | Description                         |
|----------|--------|--------------------------------------|-------------------------------------|
| id       | int    | PRIMARY KEY, AUTOINCREMENT           | Unique tag identifier               |
| name     | str    | NOT NULL, max 50 chars               | Tag display name                    |
| color    | str    | NULLABLE, hex format                 | Tag color for UI display            |
| user_id  | str    | FOREIGN KEY -> User.id, NOT NULL     | Owner of the tag                    |

**Constraint**: UNIQUE(name, user_id) - No duplicate tag names per user

#### Task Entity (SQLModel) - Phase II

| Field           | Type         | Constraints                          | Description                         |
|-----------------|--------------|--------------------------------------|-------------------------------------|
| id              | int          | PRIMARY KEY, AUTOINCREMENT           | Unique task identifier              |
| title           | str          | NOT NULL, 1-200 chars                | Task title                          |
| description     | str          | NULLABLE, max 1000 chars             | Detailed description                |
| completed       | bool         | NOT NULL, DEFAULT False              | Completion status                   |
| priority        | str          | NOT NULL, DEFAULT 'medium'           | Enum: 'low', 'medium', 'high'       |
| due_date        | datetime     | NULLABLE                             | Task due date and time              |
| recurrence_rule | str          | NULLABLE                             | iCal RRULE string                   |
| user_id         | str          | FOREIGN KEY -> User.id, NOT NULL     | Task owner                          |
| created_at      | datetime     | NOT NULL, DEFAULT now()              | Creation timestamp                  |
| updated_at      | datetime     | NOT NULL, DEFAULT now(), ON UPDATE   | Last modification timestamp         |
| tags            | List[Tag]    | Many-to-Many via TaskTagLink         | Associated tags                     |

#### TaskTagLink Entity (Junction Table)

| Field   | Type | Constraints                          | Description                         |
|---------|------|--------------------------------------|-------------------------------------|
| task_id | int  | FOREIGN KEY -> Task.id, PRIMARY KEY  | Task reference                      |
| tag_id  | int  | FOREIGN KEY -> Tag.id, PRIMARY KEY   | Tag reference                       |

**Constraint**: Composite PRIMARY KEY(task_id, tag_id)

### Phase III Data Models

**IMPORTANT**: Phase III uses SEPARATE tables from Phase II to maintain complete separation.

#### Task Entity (SQLModel) - Phase III

**Table Name**: `tasks_phaseiii` (NOT the Phase II `tasks` table)

| Field       | Type     | Constraints                          | Description                         |
|-------------|----------|--------------------------------------|-------------------------------------|
| id          | int      | PRIMARY KEY, AUTOINCREMENT           | Unique task identifier              |
| user_id     | str      | INDEX, NOT NULL                      | Owner user ID from Better Auth      |
| title       | str      | NOT NULL, max 200 chars              | Task title                          |
| description | str      | NULLABLE                             | Task description                    |
| completed   | bool     | NOT NULL, DEFAULT False              | Completion status                   |
| created_at  | datetime | NOT NULL, DEFAULT now()              | Creation timestamp                  |
| updated_at  | datetime | NOT NULL, DEFAULT now(), ON UPDATE   | Last modification timestamp         |

#### Conversation Entity (SQLModel)

**Table Name**: `conversations`

| Field      | Type     | Constraints                          | Description                         |
|------------|----------|--------------------------------------|-------------------------------------|
| id         | int      | PRIMARY KEY, AUTOINCREMENT           | Unique conversation identifier      |
| user_id    | str      | INDEX, NOT NULL                      | Owner user ID from Better Auth      |
| created_at | datetime | NOT NULL, DEFAULT now()              | Conversation start timestamp        |
| updated_at | datetime | NOT NULL, DEFAULT now(), ON UPDATE   | Last activity timestamp             |

#### Message Entity (SQLModel)

**Table Name**: `messages`

| Field           | Type     | Constraints                          | Description                         |
|-----------------|----------|--------------------------------------|-------------------------------------|
| id              | int      | PRIMARY KEY, AUTOINCREMENT           | Unique message identifier           |
| conversation_id | int      | FOREIGN KEY -> Conversation.id, INDEX| Parent conversation                 |
| user_id         | str      | INDEX, NOT NULL                      | Owner user ID                       |
| role            | str      | NOT NULL                             | 'user' or 'assistant'               |
| content         | text     | NOT NULL                             | Message content                     |
| created_at      | datetime | NOT NULL, DEFAULT now()              | Message timestamp                   |

### Phase V Data Models

**IMPORTANT**: Phase V enhances the `tasks_phaseiii` table and adds new tables for categories and tags.

#### Task Entity (SQLModel) - Phase V Enhanced

**Table Name**: `tasks_phaseiii` (enhanced with new fields)

| Field           | Type     | Constraints                          | Description                         |
|-----------------|----------|--------------------------------------|-------------------------------------|
| id              | int      | PRIMARY KEY, AUTOINCREMENT           | Unique task identifier              |
| user_id         | str      | INDEX, NOT NULL                      | Owner user ID from Better Auth      |
| title           | str      | NOT NULL, max 200 chars              | Task title                          |
| description     | str      | NULLABLE                             | Task description                    |
| completed       | bool     | NOT NULL, DEFAULT False              | Completion status                   |
| priority        | str      | NOT NULL, DEFAULT 'medium'           | Enum: 'low', 'medium', 'high', 'urgent' |
| due_date        | datetime | NULLABLE, INDEX                      | Task due date and time              |
| category_id     | int      | FOREIGN KEY -> categories.id, NULLABLE | Category reference              |
| recurrence_rule | str      | NULLABLE                             | iCal RRULE string                   |
| reminder_sent   | bool     | NOT NULL, DEFAULT False              | Whether reminder was sent           |
| search_vector   | tsvector | GIN INDEX                            | Full-text search vector             |
| created_at      | datetime | NOT NULL, DEFAULT now()              | Creation timestamp                  |
| updated_at      | datetime | NOT NULL, DEFAULT now(), ON UPDATE   | Last modification timestamp         |

#### Category Entity (SQLModel) - Phase V

**Table Name**: `categories`

| Field      | Type     | Constraints                          | Description                         |
|------------|----------|--------------------------------------|-------------------------------------|
| id         | int      | PRIMARY KEY, AUTOINCREMENT           | Unique category identifier          |
| user_id    | str      | INDEX, NOT NULL                      | Owner user ID from Better Auth      |
| name       | str      | NOT NULL, max 50 chars               | Category display name               |
| color      | str      | NULLABLE, hex format                 | Category color for UI display       |
| created_at | datetime | NOT NULL, DEFAULT now()              | Creation timestamp                  |

**Constraint**: UNIQUE(name, user_id) - No duplicate category names per user

#### Tag Entity (SQLModel) - Phase V

**Table Name**: `tags_phasev` (separate from Phase II tags)

| Field      | Type     | Constraints                          | Description                         |
|------------|----------|--------------------------------------|-------------------------------------|
| id         | int      | PRIMARY KEY, AUTOINCREMENT           | Unique tag identifier               |
| user_id    | str      | INDEX, NOT NULL                      | Owner user ID from Better Auth      |
| name       | str      | NOT NULL, max 30 chars               | Tag display name                    |
| color      | str      | NULLABLE, hex format                 | Tag color for UI display            |
| created_at | datetime | NOT NULL, DEFAULT now()              | Creation timestamp                  |

**Constraint**: UNIQUE(name, user_id) - No duplicate tag names per user

#### TaskTag Junction Entity (SQLModel) - Phase V

**Table Name**: `task_tags`

| Field   | Type | Constraints                               | Description                         |
|---------|------|-------------------------------------------|-------------------------------------|
| task_id | int  | FOREIGN KEY -> tasks_phaseiii.id, PK      | Task reference                      |
| tag_id  | int  | FOREIGN KEY -> tags_phasev.id, PK         | Tag reference                       |

**Constraint**: Composite PRIMARY KEY(task_id, tag_id)

### Database Indexes

**Phase II Indexes**:
- `idx_tasks_user_id` on tasks(user_id) - User task lookup
- `idx_tasks_user_completed` on tasks(user_id, completed) - Filtered task lists
- `idx_tasks_user_priority` on tasks(user_id, priority) - Priority sorting
- `idx_tasks_user_due_date` on tasks(user_id, due_date) - Due date sorting
- `idx_tags_user_id` on tags(user_id) - User tag lookup
- `idx_task_tag_link_task` on task_tag_link(task_id) - Tag lookup by task
- `idx_task_tag_link_tag` on task_tag_link(tag_id) - Task lookup by tag

**Phase III Indexes**:
- `idx_tasks_phaseiii_user_id` on tasks_phaseiii(user_id) - User task lookup
- `idx_conversations_user_id` on conversations(user_id) - User conversation lookup
- `idx_messages_conversation_id` on messages(conversation_id) - Message lookup by conversation
- `idx_messages_user_id` on messages(user_id) - User message lookup

**Phase V Indexes** (Additional):
- `idx_tasks_phaseiii_priority` on tasks_phaseiii(user_id, priority) - Priority filtering
- `idx_tasks_phaseiii_due_date` on tasks_phaseiii(user_id, due_date) - Due date filtering
- `idx_tasks_phaseiii_category` on tasks_phaseiii(category_id) - Category filtering
- `idx_tasks_search` on tasks_phaseiii USING GIN(search_vector) - Full-text search
- `idx_categories_user` on categories(user_id) - User category lookup
- `idx_tags_phasev_user` on tags_phasev(user_id) - User tag lookup
- `idx_task_tags_task` on task_tags(task_id) - Tag lookup by task
- `idx_task_tags_tag` on task_tags(tag_id) - Task lookup by tag

---

## Validation Rules

### Task Title
- **Required**: Cannot be empty or whitespace-only
- **Length**: 1-200 characters after trimming
- **Error**: `{"detail": "Title is required and must be 1-200 characters", "code": "INVALID_TITLE"}`

### Task Description
- **Optional**: Can be null or empty string
- **Length**: Maximum 1000 characters
- **Error**: `{"detail": "Description cannot exceed 1000 characters", "code": "DESCRIPTION_TOO_LONG"}`

### Task Priority (Phase II/V)
- **Required**: Must be one of: 'low', 'medium', 'high' (Phase II) or 'low', 'medium', 'high', 'urgent' (Phase V)
- **Default**: 'medium'
- **Error**: `{"detail": "Priority must be low, medium, high, or urgent", "code": "INVALID_PRIORITY"}`

### Due Date (Phase II/V)
- **Optional**: Can be null
- **Format**: ISO 8601 datetime string
- **Constraint**: Cannot be in the past when creating (warning only on update)
- **Error**: `{"detail": "Due date must be a valid ISO 8601 datetime", "code": "INVALID_DUE_DATE"}`

### Recurrence Rule (Phase II/V)
- **Optional**: Can be null
- **Format**: Valid iCal RRULE string
- **Error**: `{"detail": "Recurrence rule must be a valid iCal RRULE", "code": "INVALID_RRULE"}`

### Tag Name
- **Required**: Cannot be empty or whitespace-only
- **Length**: 1-50 characters (Phase II) or 1-30 characters (Phase V) after trimming
- **Uniqueness**: No duplicate names per user
- **Error**: `{"detail": "Tag name is required and must be 1-30 characters", "code": "INVALID_TAG_NAME"}`

### Category Name (Phase V)
- **Required**: Cannot be empty or whitespace-only
- **Length**: 1-50 characters after trimming
- **Uniqueness**: No duplicate names per user
- **Error**: `{"detail": "Category name is required and must be 1-50 characters", "code": "INVALID_CATEGORY_NAME"}`

### Task ID (for operations)
- **Required**: Must be a valid integer
- **Existence**: Must correspond to an existing task owned by the user
- **Error**: `{"detail": "Task not found", "code": "TASK_NOT_FOUND"}`

### Chat Message
- **Required**: Cannot be empty or whitespace-only
- **Error**: `{"detail": "Message is required", "code": "INVALID_MESSAGE"}`

### Conversation ID
- **Optional**: Can be null (creates new conversation)
- **Existence**: If provided, must correspond to an existing conversation owned by the user
- **Error**: `{"detail": "Conversation not found", "code": "CONVERSATION_NOT_FOUND"}`

### Search Query (Phase V)
- **Required**: Cannot be empty or whitespace-only
- **Length**: Minimum 2 characters
- **Error**: `{"detail": "Search query must be at least 2 characters", "code": "INVALID_SEARCH_QUERY"}`

---

## API Design Standards

### Phase II Endpoint Patterns

| Operation       | Method | Path                          | Success Code |
|-----------------|--------|-------------------------------|--------------|
| List resources  | GET    | /api/{user_id}/{resources}    | 200          |
| Get resource    | GET    | /api/{user_id}/{resources}/{id}| 200          |
| Create resource | POST   | /api/{user_id}/{resources}    | 201          |
| Update resource | PUT    | /api/{user_id}/{resources}/{id}| 200          |
| Partial update  | PATCH  | /api/{user_id}/{resources}/{id}| 200          |
| Delete resource | DELETE | /api/{user_id}/{resources}/{id}| 204          |

### Authentication Endpoints

| Operation       | Method | Path                          | Success Code |
|-----------------|--------|-------------------------------|--------------|
| Login           | POST   | /api/v1/auth/login            | 200          |
| Register        | POST   | /api/v1/auth/register         | 201          |
| Refresh token   | POST   | /api/v1/auth/refresh          | 200          |
| Logout          | POST   | /api/v1/auth/logout           | 200          |
| Current user    | GET    | /api/v1/auth/me               | 200          |

### Phase III Chat Endpoint

| Operation       | Method | Path                          | Success Code |
|-----------------|--------|-------------------------------|--------------|
| Send message    | POST   | /api/{user_id}/chat           | 200          |

**Request Schema**:
```json
{
  "message": "<string, required>",
  "conversation_id": "<integer, optional>"
}
```

**Response Schema**:
```json
{
  "conversation_id": "<integer>",
  "response": "<string>",
  "tool_calls": [
    {
      "name": "<tool_name>",
      "arguments": {},
      "result": {}
    }
  ]
}
```

### Query Parameters

- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `sort`: Field to sort by (prefix with - for descending)
- `status`: Filter by status (all, pending, completed)
- `priority`: Filter by priority (low, medium, high, urgent)
- `category_id`: Filter by category ID (Phase V)
- `tag_id`: Filter by tag ID (Phase V)
- `due_before`: Filter tasks due before date (Phase V)
- `due_after`: Filter tasks due after date (Phase V)
- `q`: Search query string

### Response Pagination Format

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "limit": 20,
  "pages": 8
}
```

### Path Parameter Validation Requirements

- All endpoints with `{user_id}` in the path MUST validate that the path parameter matches the JWT user_id
- Validation MUST occur before executing the business logic
- Mismatched user_id values MUST return HTTP 403 Forbidden
- All database queries MUST be scoped using the JWT user_id, NOT the path parameter

---

## Success Criteria

### Phase II Completion (COMPLETED)

#### Functional Requirements
- [x] **User Auth**: Better Auth integration works with JWT plugin for user registration, login, logout, and token refresh
- [x] **Task CRUD**: All basic task operations work correctly with new API pattern
- [x] **Data Isolation**: Users only see their own tasks and tags; path parameter validation prevents cross-user access
- [x] **Priorities**: Tasks can be assigned and filtered by priority
- [x] **Tags**: Users can create, edit, delete, and assign tags
- [x] **Search**: Full-text search returns relevant results
- [x] **Filter/Sort**: All filter and sort combinations work
- [x] **Due Dates**: Tasks display due date indicators correctly
- [x] **Notifications**: Browser notifications trigger for due tasks (P3)
- [x] **Recurring Tasks**: RRULE parsing and next occurrence calculation (P3)
- [x] **API Migration**: All user-specific endpoints migrated to `/api/{user_id}/{resources}` pattern with proper validation

#### Technical Requirements
- [x] **AI-Generated Code**: All code generated from specs with exceptions documented
- [x] **Backend Tests**: pytest coverage >= 80% on core logic (verified in nightly pipeline)
- [x] **Frontend Tests**: Component test coverage >= 70% (verified in nightly pipeline)
- [x] **CI Pipeline**: All PR checks pass (lint, test, build) on every PR
- [x] **Docker**: Both services run via `docker-compose up`
- [x] **API Docs**: OpenAPI documentation accurate and complete
- [x] **JWT Security**: Better Auth JWT validation works correctly with shared secret
- [x] **Path Validation**: All endpoints with user_id in path validate against JWT user_id
- [x] **API Client**: API client implemented at `@/lib/api-client` with Better Auth integration
- [x] **Multi-User Isolation**: Tests verify that users can't access other users' resources
- [x] **Performance**: Lighthouse score >= 90 (verified in nightly pipeline)

### Phase III Completion (COMPLETED)

#### Functional Requirements
- [x] **Chat Interface**: OpenAI ChatKit-based UI allows sending messages and receiving AI responses
- [x] **Conversation Persistence**: Conversations and messages are stored in database
- [x] **MCP Tools**: All 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task) work correctly
- [x] **Natural Language**: AI understands natural language commands for task management
- [x] **Tool Invocation**: Agent correctly invokes appropriate MCP tools based on user intent
- [x] **Conversation Resume**: Users can continue previous conversations
- [x] **Stateless Server**: Server holds no in-memory state; all state in database
- [x] **Better Auth Integration**: User authentication works with Phase III frontend

#### Technical Requirements
- [x] **Phase Separation**: Zero imports from Phase II codebase
- [x] **MCP SDK**: Official MCP SDK used correctly
- [x] **OpenAI Agents SDK**: Agent configured with proper system prompt and tools
- [x] **Separate Tables**: Phase III uses `tasks_phaseiii`, `conversations`, `messages` tables
- [x] **Backend Tests**: pytest coverage >= 80% on MCP tools and chat service
- [x] **Frontend Tests**: Component tests for chat interface
- [x] **UV Package Manager**: Backend uses UV for dependency management
- [x] **Bun Package Manager**: Frontend uses Bun for dependency management
- [x] **OpenAI ChatKit**: Frontend built with ChatKit starter template
- [x] **API Docs**: Chat endpoint documented in OpenAPI

### Documentation Requirements (Phase III - COMPLETED)

- [x] Specs exist for all features in `/specs/sphaseIII/NNN-feature-name/spec.md`
- [x] Implementation plans exist in `/specs/sphaseIII/NNN-feature-name/plan.md`
- [x] Task breakdowns exist in `/specs/sphaseIII/NNN-feature-name/tasks.md`
- [x] README.md includes setup, development, and deployment instructions
- [x] DEVIATIONS.md documents any manual code (if any)

---

### Phase IV Completion (COMPLETED)

#### Functional Requirements
- [x] **Four Services Deployed**: Frontend, Backend, MCP Server, Redis all running in Kubernetes
- [x] **Ingress Routing**: Nginx Ingress routes / to frontend and /api to backend at todo-app.local
- [x] **Horizontal Pod Autoscaling**: HPA scales frontend and backend based on CPU/memory metrics
- [x] **Redis Persistence**: Redis data persists across pod restarts via PersistentVolume
- [x] **Complete User Flow**: End-to-end user journey works (auth --> chat --> task operations via MCP tools)
- [x] **All 5 MCP Tools Working**: add_task, list_tasks, complete_task, delete_task, update_task functional in Kubernetes
- [x] **Namespace Isolation**: All resources deployed in todo-phaseiv namespace
- [x] **External Database**: Backend connects to shared Neon PostgreSQL instance
- [x] **Service Discovery**: Services communicate via Kubernetes internal DNS (ClusterIP)
- [x] **Load Balancing**: Multiple frontend/backend replicas load-balanced automatically

#### Technical Requirements
- [x] **Comprehensive Spec**: `/specs/sphaseIV/001-kubernetes-deployment/spec.md` exists and complete
- [x] **Helm Chart Best Practices**: Chart follows Helm conventions, passes helm lint with zero warnings
- [x] **Resource Limits**: CPU/memory requests and limits defined for all containers
- [x] **Health Probes**: Liveness and readiness probes configured for all services
- [x] **Secrets Management**: Database credentials, API keys stored in Kubernetes Secrets
- [x] **ConfigMaps**: Non-sensitive configuration externalized in ConfigMaps
- [x] **helm test Passes**: Helm test suite validates deployment correctness
- [x] **Incremental Rollout**: Deployment script follows Redis --> MCP --> Backend --> Frontend --> Ingress order
- [x] **Rollback Strategy**: helm rollback tested and functional
- [x] **Values Templating**: Environment-specific values templated in values.yaml

#### Documentation Requirements (Phase IV - COMPLETED)
- [x] **KUBERNETES_GUIDE.md**: Comprehensive guide covering Minikube setup, Helm installation, deployment steps, testing procedures
- [x] **Helm README.md**: Chart-specific README in `/phaseIV/kubernetes/helm/todo-app/README.md`
- [x] **RUNBOOK.md**: Operational runbook covering common tasks (scale replicas, view logs, restart pods, troubleshoot Ingress)
- [x] **Architecture Diagram**: Visual diagram of Kubernetes architecture (services, ingress, PVCs)
- [x] **Deployment Scripts**: Automated scripts in `/phaseIV/kubernetes/scripts/` (setup-minikube.sh, deploy.sh, test.sh)

#### Testing Requirements (Phase IV - COMPLETED)
- [x] **E2E Test**: End-to-end test covers full user flow (login --> chat --> task CRUD --> verify persistence)
- [x] **Load Test**: Load test triggers HPA scaling (verify replicas scale from 2 to 5 under load)
- [x] **Resilience Test**: Pod deletion test (kubectl delete pod) validates automatic restart and service continuity
- [x] **Persistence Test**: Redis pod restart test validates data retention via PVC
- [x] **Ingress Test**: HTTP requests to todo-app.local validate correct routing (/ --> frontend, /api --> backend)
- [x] **helm test**: Helm-provided tests validate deployment health
- [x] **Resource Monitoring**: kubectl top pods shows resource usage; metrics-server functional

---

### Phase V Completion (ACTIVE)

#### Part A: Advanced Features

**Functional Requirements**:
- [ ] **Enhanced Task Model**: Tasks support priority (low/medium/high/urgent), due_date, category_id, recurrence_rule, reminder_sent
- [ ] **Categories CRUD**: Users can create, list, delete categories
- [ ] **Tags CRUD**: Users can create, list, delete tags (tags_phasev table)
- [ ] **Task-Tag Association**: Users can add/remove tags from tasks
- [ ] **Full-Text Search**: PostgreSQL tsvector search returns relevant results ranked by relevance
- [ ] **Multi-Criteria Filtering**: list_tasks supports priority, category, tag, due_before, due_after filters
- [ ] **Sorting**: list_tasks supports sort_by (created_at, due_date, priority, title)
- [ ] **Overdue Tasks**: get_overdue_tasks returns tasks past due date
- [ ] **Upcoming Tasks**: get_upcoming_tasks returns tasks due within N days
- [ ] **All 17 MCP Tools Working**: Enhanced and new tools functional in ChatKit
- [ ] **Kafka Event Publishing**: All MCP tools publish events to task-events topic
- [ ] **Notification Service**: Consumes reminders topic, processes reminder events
- [ ] **Recurring Task Service**: Consumes task-events, auto-creates next occurrence on completion

**Technical Requirements**:
- [ ] **Database Migration**: Alembic migration adds new fields to tasks_phaseiii, creates categories, tags_phasev, task_tags tables
- [ ] **Full-Text Search Index**: GIN index on search_vector column functional
- [ ] **Kafka Integration**: aiokafka producer publishes events successfully
- [ ] **Event Consumers**: Notification and Recurring services consume and process events
- [ ] **RRULE Parser**: python-dateutil parses iCal RRULE and calculates next occurrence
- [ ] **Backend Tests**: pytest coverage >= 80% on all 17 MCP tools and services

#### Part B: Dapr Integration

**Functional Requirements**:
- [ ] **Dapr Installed**: Dapr v1.12+ running on Kubernetes (dapr-system namespace)
- [ ] **Pub/Sub Component**: kafka-pubsub component configured for Redpanda Cloud
- [ ] **State Store Component**: statestore component configured for PostgreSQL
- [ ] **Secrets Component**: kubernetes-secrets component configured
- [ ] **Jobs Component**: Jobs API component for scheduled reminders
- [ ] **Dapr Sidecar Injection**: All services have Dapr sidecar with proper annotations
- [ ] **Infrastructure Abstraction**: Application code uses Dapr HTTP API (not direct Kafka clients)

**Technical Requirements**:
- [ ] **Dapr Components Applied**: All 4 YAML files applied to todo-phasev namespace
- [ ] **Service Updates**: Backend, Notification, Recurring services use Dapr Pub/Sub API
- [ ] **Jobs API Integration**: Reminders scheduled via Dapr Jobs API
- [ ] **Helm Chart Updates**: Dapr annotations and configuration in values.yaml
- [ ] **Dapr Logs**: Sidecar logs show successful event publishing/subscription

#### Part C: Production Cloud Deployment

**Functional Requirements**:
- [ ] **OKE Cluster Running**: Oracle Cloud OKE cluster with 2 nodes (4 OCPU, 24GB RAM)
- [ ] **HTTPS Enabled**: Let's Encrypt TLS certificates valid for custom domain
- [ ] **CI/CD Pipeline**: GitHub Actions builds, tests, deploys on release tags
- [ ] **Prometheus Metrics**: Backend /metrics endpoint scraped by Prometheus
- [ ] **Grafana Dashboards**: Custom dashboards showing HTTP requests, task operations, pod resources
- [ ] **Network Policies**: Pod-to-pod communication restricted by NetworkPolicy
- [ ] **RBAC Policies**: Service accounts with least-privilege permissions
- [ ] **Pod Security**: runAsNonRoot, readOnlyRootFilesystem, no privilege escalation
- [ ] **Backup Strategy**: Velero daily backups of todo-phasev namespace configured

**Technical Requirements**:
- [ ] **OCI CLI Configured**: kubectl connects to OKE cluster
- [ ] **OCIR Images**: Docker images pushed to Oracle Container Registry
- [ ] **cert-manager Installed**: ClusterIssuer for Let's Encrypt configured
- [ ] **CI Workflow**: ci-phase-v.yml passes lint, test, build, helm-lint
- [ ] **Deploy Workflow**: deploy-production.yml deploys on release with smoke tests
- [ ] **Resource Quotas**: Namespace limits configured (8 CPU, 16Gi memory requests)
- [ ] **Production Stable**: Application running without issues for 7+ days

#### Documentation Requirements (Phase V)

- [ ] **Specs**: `/specs/sphaseV/001-advanced-features/spec.md` comprehensive
- [ ] **Specs**: `/specs/sphaseV/002-dapr-integration/spec.md` comprehensive
- [ ] **Specs**: `/specs/sphaseV/003-cloud-deployment/spec.md` comprehensive
- [ ] **ORACLE_CLOUD_SETUP.md**: Step-by-step OKE cluster creation guide
- [ ] **DAPR_GUIDE.md**: Dapr installation, components, troubleshooting
- [ ] **MONITORING_GUIDE.md**: Prometheus/Grafana setup and dashboards
- [ ] **DEPLOYMENT_RUNBOOK.md**: Production deployment checklist and rollback procedures
- [ ] **README.md**: Updated with Phase V features, architecture, setup instructions

#### Testing Requirements (Phase V)

- [ ] **Unit Tests**: All 17 MCP tools have unit tests with 80%+ coverage
- [ ] **Kafka Event Tests**: Event publishing and consumption verified
- [ ] **Search Tests**: Full-text search accuracy and ranking validated
- [ ] **Dapr Integration Tests**: Pub/Sub, State, Jobs API tests pass
- [ ] **Load Tests**: HPA scales under load, Kafka handles throughput
- [ ] **Resilience Tests**: Pod failures, database failures, Kafka failures handled
- [ ] **E2E Tests**: Critical user flows (priority task, recurring task, search, reminder) pass
- [ ] **helm test**: Helm tests validate Phase V deployment

---

## Constraints (Hard Limits)

### Development Constraints
- **No Manual Coding**: AI agent generates all implementation (see Principle I for exception)
- **Spec First**: No implementation without corresponding specification
- **Version Control**: All changes via pull requests to main

### Technology Constraints

**Phase II**:
- **Frontend**: Next.js 16 App Router, TypeScript, bun only
- **Backend**: Python 3.11+, FastAPI, uv only
- **Database**: PostgreSQL (Neon Serverless) only
- **ORM**: SQLModel only (no raw SQLAlchemy)
- **Authentication**: Better Auth with JWT plugin for frontend authentication
- **API Endpoint Format**: All user-specific endpoints MUST follow the `/api/{user_id}/{resources}` pattern
- **API Client Location**: MUST be implemented at `@/lib/api-client` with Better Auth integration

**Phase III** (MANDATORY per hackathon requirements):
- **Frontend**: OpenAI ChatKit (https://platform.openai.com/docs/guides/chatkit)
- **Backend**: Python FastAPI
- **AI Framework**: OpenAI Agents SDK (https://github.com/openai/openai-agents-python)
- **MCP Server**: Official MCP SDK (https://github.com/modelcontextprotocol/python-sdk)
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL (same instance, different tables)
- **Authentication**: Better Auth
- **Backend Package Manager**: UV (`uv add <package>`)
- **Frontend Package Manager**: Bun (`bun add <package>`)

**Phase IV** (MANDATORY per hackathon requirements):
- **Container Runtime**: Docker Desktop only
- **Orchestration**: Kubernetes via Minikube only
- **Package Manager**: Helm Charts v3.13+ only
- **Ingress Controller**: Nginx Ingress only
- **Storage**: PersistentVolume with standard StorageClass
- **Autoscaling**: Horizontal Pod Autoscaler with metrics-server
- **Cluster Requirements**: Minikube with 4 CPU, 8GB RAM minimum
- **Namespace**: todo-phaseiv (MUST use this namespace)
- **Database**: Neon Serverless PostgreSQL (shared with Phase III)
- **Optional AI DevOps Tools**: kubectl-ai, kagent, Docker AI (Gordon)

**Phase V** (MANDATORY per hackathon requirements):
- **Event Streaming**: Kafka via Redpanda Cloud (serverless) or self-hosted via Strimzi
- **Kafka Client**: aiokafka for async Python (pre-Dapr) or Dapr Pub/Sub API (post-Dapr)
- **Distributed Runtime**: Dapr v1.12+ with components (Pub/Sub, State, Secrets, Jobs)
- **Cloud Provider**: Oracle Cloud OKE (always free tier: 4 OCPU, 24GB RAM)
- **TLS Certificates**: cert-manager with Let's Encrypt
- **CI/CD**: GitHub Actions (ci-phase-v.yml, deploy-production.yml)
- **Container Registry**: Oracle Container Registry (OCIR)
- **Monitoring**: Prometheus + Grafana (kube-prometheus-stack)
- **Namespace**: todo-phasev (MUST use this namespace)
- **Database**: Neon Serverless PostgreSQL (shared with Phase III/IV)

### Security Constraints
- **No Secrets in Code**: All secrets via environment variables
- **Token Management**: Better Auth handles token storage and refresh
- **Data Access**: All queries scoped to authenticated user JWT user_id (NOT path parameter)
- **Path Parameter Validation**: User ID in path must match JWT user_id; mismatch returns 403 Forbidden
- **Token Validation**: Backend validates Better Auth JWTs using shared secret
- **Data Isolation**: Path parameter user_id is NOT authoritative for data access decisions
- **Kafka Credentials**: SASL authentication for Redpanda Cloud, stored in Kubernetes Secrets
- **Network Policies**: Phase V requires NetworkPolicy to restrict pod communication

### Performance Constraints
- **API Response Time**: p95 < 200ms for CRUD operations
- **Frontend TTI**: Time to Interactive < 3 seconds
- **Database Queries**: No N+1 queries (use eager loading)
- **Chat Response Time**: p95 < 5s for AI responses (includes OpenAI API latency)
- **Kafka Event Latency**: p95 < 500ms for event publishing
- **Search Response Time**: p95 < 300ms for full-text search queries

### Phase Separation Constraints
- **No Imports Between Phases**: Phase V MUST NOT import from phaseIV, phaseIII, phaseII, or phaseI
- **Independent Implementations**: Each phase reimplements required functionality
- **Separate Database Tables**: Phase III/V uses `tasks_phaseiii` table, not Phase II `tasks` table
- **Independent Migrations**: Phase V has its own Alembic migration history
- **Source Code Copy**: Phase V copies (not imports) Phase IV source and evolves independently

---

## Governance & Enforcement

### Authority
This constitution is the **single source of truth** for all phases of development. All decisions, specifications, implementations, and reviews MUST align with these principles.

### Amendment Process
Amendments require:
1. Written justification explaining why the change is necessary
2. Impact analysis on existing specifications and implementations
3. Team review and approval
4. Update to version number and "Last Amended" date
5. Sync Impact Report update in HTML comment

### Deviation Policy
Any deviation from this constitution MUST be:
1. **Documented**: Noted in `DEVIATIONS.md` with full justification
2. **Justified**: Explained as necessary to meet requirements or overcome AI limitations
3. **Minimal**: The smallest possible deviation to achieve the goal
4. **Reviewed**: Approved before merging

### Compliance Verification
- All pull requests MUST be reviewed for constitutional compliance
- CI checks MUST pass before merge
- Code reviews verify adherence to principles
- Spec references required in PR descriptions

---

## Philosophical Foundation

**Spec-Driven Development Principle**:
> "The engineer is no longer a syntax writer but a system architect. The specification is the blueprint; AI is the builder."

**Evolution Mindset**:
> "Each phase builds on lessons learned. We evolve from CLI to web to AI to Kubernetes to cloud-native while maintaining the discipline of specification-first development."

**Security-First Thinking**:
> "Security is not an afterthought. Every feature considers authentication, authorization, and data isolation from the specification phase."

**Quality Over Speed**:
> "Take time to write precise specifications. The better your spec, the better the AI's implementation. Iteration on specs is encouraged; manual coding is forbidden."

**Phase Independence**:
> "Each phase stands alone. Complete separation ensures clean architecture and demonstrates multiple approaches to the same problem domain."

**Event-Driven Architecture**:
> "Services communicate through events, not direct calls. Kafka enables decoupled, scalable microservices where producers and consumers evolve independently."

**Infrastructure Abstraction**:
> "Dapr abstracts infrastructure dependencies. Application code should not know whether it's using Kafka, Redis, or any other specific technology."

---

## Requirement-to-Rule Mapping

### Phase II Requirements

| Req ID | Requirement Description                            | Constitutional Rule(s)                     | Section      |
|--------|---------------------------------------------------|--------------------------------------------|--------------|
| FR-001 | Multi-user authentication                          | JWT token flow, Better Auth integration    | IV           |
| FR-002 | Persistent task storage                            | Neon PostgreSQL, SQLModel                  | III          |
| FR-003 | Task CRUD operations                               | Feature Scope P1                           | X            |
| FR-004 | Priority assignment                                | Data Model - Task.priority                 | Data Model   |
| FR-005 | Tag management                                     | Data Model - Tag entity                    | Data Model   |
| FR-006 | Search and filter                                  | Feature Scope P2                           | X            |
| FR-007 | Due dates and reminders                            | Feature Scope P3                           | X            |
| FR-008 | Recurring tasks                                    | Data Model - Task.recurrence_rule          | Data Model   |
| QR-001 | API response time < 200ms p95                      | Performance Constraints                    | Constraints  |
| QR-002 | Frontend TTI < 3s                                  | Performance Constraints                    | Constraints  |
| QR-003 | Lighthouse score >= 90                             | Nightly Pipeline Performance Audit         | IX           |
| SR-001 | Monorepo structure                                 | Full-Stack Monorepo Architecture           | II           |
| SR-002 | API versioning                                     | Backend Architecture Standards             | V            |
| SR-003 | Component organization                             | Frontend Architecture Standards            | VI           |
| IR-001 | REST API design                                    | API Design Standards                       | API Design   |
| IR-002 | JWT token format                                   | JWT Security principle                     | IV           |
| PR-001 | Spec-driven workflow                               | Spec-Driven Development                    | I            |
| PR-002 | CI/CD pipeline                                     | CI/CD Pipeline                             | IX           |
| PR-003 | Docker deployment                                  | Containerization & Deployment              | VIII         |
| SEC-001| Secure token storage                               | JWT Security - Storage requirements        | IV           |
| SEC-002| Data isolation                                     | JWT Security - Data scoping                | IV           |
| SEC-003| CORS policy                                        | Backend Architecture Standards             | V            |
| SEC-004| Path parameter user ID validation                  | JWT Security - Path Parameter Matching     | IV           |

### Phase III Requirements

| Req ID      | Requirement Description                       | Constitutional Rule(s)                     | Section      |
|-------------|----------------------------------------------|--------------------------------------------|--------------|
| FR-P3-001   | Conversational chat interface                 | OpenAI ChatKit Integration                 | VI           |
| FR-P3-002   | Natural language task management              | Agent Behavior Specification               | XII          |
| FR-P3-003   | MCP tools for task operations                 | MCP Server Architecture                    | XI           |
| FR-P3-004   | Stateless chat endpoint                       | Conversational AI Standards                | XIII         |
| FR-P3-005   | Conversation persistence                      | Data Model - Conversation, Message         | Data Model   |
| FR-P3-006   | Tool invocation by AI agent                   | OpenAI Agents SDK Integration              | XII          |
| FR-P3-007   | Chat history context                          | Conversation Flow specification            | XIII         |
| FR-P3-008   | Error handling in conversations               | Agent Behavior - Error Handling            | XII          |
| QR-P3-001   | Chat response time < 5s p95                   | Performance Constraints                    | Constraints  |
| SR-P3-001   | Phase III directory structure                 | Repository Structure                       | II           |
| SR-P3-002   | Complete phase separation                     | Phase Separation Constraints               | Constraints  |
| IR-P3-001   | Chat API endpoint                             | API Design Standards - Phase III           | API Design   |
| IR-P3-002   | MCP tool interface                            | MCP Tools Specification                    | XI           |
| TC-P3-001   | OpenAI ChatKit frontend                       | Technology Constraints - Phase III         | Constraints  |
| TC-P3-002   | OpenAI Agents SDK                             | Technology Constraints - Phase III         | Constraints  |
| TC-P3-003   | Official MCP SDK                              | Technology Constraints - Phase III         | Constraints  |
| TC-P3-004   | UV package manager for backend                | Technology Constraints - Phase III         | Constraints  |
| TC-P3-005   | Bun package manager for frontend              | Technology Constraints - Phase III         | Constraints  |

### Phase IV Requirements

| Req ID      | Requirement Description                       | Constitutional Rule(s)                     | Section      |
|-------------|----------------------------------------------|--------------------------------------------|--------------|
| FR-P4-001   | Four services deployed in Kubernetes          | Containerization & Orchestration           | XIV          |
| FR-P4-002   | Nginx Ingress routing                         | Production-Grade Deployment - Ingress      | XV           |
| FR-P4-003   | Horizontal Pod Autoscaling                    | Production-Grade Deployment - HPA          | XV           |
| FR-P4-004   | Redis persistence via PersistentVolume        | Production-Grade Deployment - PV           | XV           |
| FR-P4-005   | Complete user flow in Kubernetes              | Success Criteria - Functional              | Success      |
| FR-P4-006   | All 5 MCP tools functional                    | Success Criteria - Functional              | Success      |
| FR-P4-007   | Namespace isolation (todo-phaseiv)            | Containerization & Orchestration           | XIV          |
| FR-P4-008   | External Neon PostgreSQL connection           | Success Criteria - Functional              | Success      |
| FR-P4-009   | Service discovery via ClusterIP               | Containerization & Orchestration           | XIV          |
| FR-P4-010   | Load balancing across replicas                | Success Criteria - Functional              | Success      |
| SR-P4-001   | Phase IV directory structure                  | Repository Structure                       | II           |
| SR-P4-002   | Helm chart best practices                     | Containerization & Orchestration           | XIV          |
| SR-P4-003   | Infrastructure as Code principles             | Containerization & Orchestration           | XIV          |
| SR-P4-004   | Container artifact reuse exception            | Phase IV Exception for Container Reuse     | II           |
| TC-P4-001   | Docker Desktop container runtime              | Technology Constraints - Phase IV          | Constraints  |
| TC-P4-002   | Kubernetes via Minikube                       | Technology Constraints - Phase IV          | Constraints  |
| TC-P4-003   | Helm Charts v3.13+                            | Technology Constraints - Phase IV          | Constraints  |
| TC-P4-004   | Nginx Ingress Controller                      | Technology Constraints - Phase IV          | Constraints  |

### Phase V Requirements

| Req ID      | Requirement Description                       | Constitutional Rule(s)                     | Section      |
|-------------|----------------------------------------------|--------------------------------------------|--------------|
| FR-P5-001   | Enhanced task fields (priority, due_date, etc.) | Phase V Data Models                      | Data Model   |
| FR-P5-002   | Categories CRUD operations                    | MCP Server Architecture - Phase V          | XI           |
| FR-P5-003   | Tags CRUD operations (tags_phasev)            | MCP Server Architecture - Phase V          | XI           |
| FR-P5-004   | Task-Tag association                          | Data Model - TaskTag junction              | Data Model   |
| FR-P5-005   | Full-text search with PostgreSQL tsvector     | Persistent State - FTS, Feature Scope      | III, X       |
| FR-P5-006   | Multi-criteria filtering                      | MCP Server Architecture - list_tasks       | XI           |
| FR-P5-007   | All 17 MCP tools functional                   | MCP Server Architecture - Phase V          | XI           |
| FR-P5-008   | Kafka event publishing from MCP tools         | Event-Driven Architecture                  | XVI          |
| FR-P5-009   | Notification Service (Kafka consumer)         | Event-Driven Architecture                  | XVI          |
| FR-P5-010   | Recurring Task Service (Kafka consumer)       | Event-Driven Architecture                  | XVI          |
| FR-P5-011   | Dapr Pub/Sub component                        | Distributed Application Runtime            | XVII         |
| FR-P5-012   | Dapr State Store component                    | Distributed Application Runtime            | XVII         |
| FR-P5-013   | Dapr Secrets component                        | Distributed Application Runtime            | XVII         |
| FR-P5-014   | Dapr Jobs API for reminders                   | Distributed Application Runtime            | XVII         |
| FR-P5-015   | Oracle Cloud OKE deployment                   | Production Cloud Deployment                | XVIII        |
| FR-P5-016   | HTTPS with cert-manager/Let's Encrypt         | Production Cloud Deployment                | XVIII        |
| FR-P5-017   | CI/CD pipeline with GitHub Actions            | Production Cloud Deployment, CI/CD         | XVIII, IX    |
| FR-P5-018   | Prometheus metrics collection                 | Production Cloud Deployment                | XVIII        |
| FR-P5-019   | Grafana dashboards                            | Production Cloud Deployment                | XVIII        |
| FR-P5-020   | Network Policies                              | Production Cloud Deployment - Security     | XVIII        |
| FR-P5-021   | RBAC Policies                                 | Production Cloud Deployment - Security     | XVIII        |
| FR-P5-022   | Pod Security Standards                        | Production Cloud Deployment - Security     | XVIII        |
| FR-P5-023   | Velero backup strategy                        | Production Cloud Deployment - Backup       | XVIII        |
| QR-P5-001   | Kafka event latency < 500ms p95               | Performance Constraints                    | Constraints  |
| QR-P5-002   | Search response time < 300ms p95              | Performance Constraints                    | Constraints  |
| SR-P5-001   | Phase V directory structure                   | Repository Structure                       | II           |
| SR-P5-002   | Container artifact evolution exception        | Phase V Exception for Container Evolution  | II           |
| SR-P5-003   | Dapr component YAML files                     | Distributed Application Runtime            | XVII         |
| TC-P5-001   | Redpanda Cloud for Kafka                      | Technology Constraints - Phase V           | Constraints  |
| TC-P5-002   | Dapr v1.12+                                   | Technology Constraints - Phase V           | Constraints  |
| TC-P5-003   | Oracle Cloud OKE                              | Technology Constraints - Phase V           | Constraints  |
| TC-P5-004   | cert-manager with Let's Encrypt               | Technology Constraints - Phase V           | Constraints  |
| TC-P5-005   | GitHub Actions CI/CD                          | Technology Constraints - Phase V           | Constraints  |
| TC-P5-006   | Prometheus + Grafana monitoring               | Technology Constraints - Phase V           | Constraints  |

---

## Constitutional Self-Checks

### 1. Alignment Check
**Status**: PASS
- All 80+ rules map to documented requirements
- No orphan rules without requirement backing
- Requirement-to-Rule mapping table complete for Phase II, Phase III, Phase IV, and Phase V
- New Phase V requirements added (FR-P5-001 through FR-P5-023, QR-P5-001 through QR-P5-002, SR-P5-001 through SR-P5-003, TC-P5-001 through TC-P5-006)

### 2. Coverage Check
**Status**: PASS
- Functional Requirements: Covered (FR-001 through FR-008, FR-P3-001 through FR-P3-008, FR-P4-001 through FR-P4-010, FR-P5-001 through FR-P5-023)
- Quality Requirements: Covered (QR-001 through QR-003, QR-P3-001, QR-P5-001 through QR-P5-002)
- Structural Requirements: Covered (SR-001 through SR-003, SR-P3-001, SR-P3-002, SR-P4-001 through SR-P4-004, SR-P5-001 through SR-P5-003)
- Interface Requirements: Covered (IR-001, IR-002, IR-P3-001, IR-P3-002)
- Process Requirements: Covered (PR-001 through PR-003)
- Security Requirements: Covered (SEC-001 through SEC-004)
- Technology Constraints: Covered (TC-P3-001 through TC-P3-005, TC-P4-001 through TC-P4-004, TC-P5-001 through TC-P5-006)

### 3. Conflict Check
**Status**: PASS
- No contradictory rules identified
- Phase II, Phase III, Phase IV, and Phase V rules are complementary, not conflicting
- Phase separation rules prevent cross-phase conflicts
- Phase IV container artifact reuse exception explicitly documented and justified
- Phase V container artifact evolution exception explicitly documented and justified
- Technology stack consistent within each phase
- Event-driven architecture (XVI) and Dapr integration (XVII) are complementary (Dapr can abstract Kafka)
- Cloud deployment (XVIII) builds on orchestration principles (XIV, XV)

### 4. Completeness Check
**Status**: PASS
- All Phase II features have governance rules (COMPLETED)
- All Phase III features have governance rules (COMPLETED)
- All Phase IV features have governance rules (COMPLETED)
- All Phase V features have governance rules (ACTIVE)
- Event-Driven Architecture principles fully specified (Principle XVI)
- Distributed Application Runtime principles fully specified (Principle XVII)
- Production Cloud Deployment principles fully specified (Principle XVIII)
- Phase V workflow guidance integrated into Principle I
- Three-part structure (Part A, Part B, Part C) mapped to success criteria
- 17 MCP tools documented with parameters and behaviors
- Kafka topics, event schemas, and consumer services defined
- Dapr components and configuration specified
- Oracle Cloud OKE, CI/CD, monitoring, security all covered
- Testing requirements comprehensive (unit, Kafka, search, Dapr, load, resilience, E2E)
- Documentation requirements specified (specs, guides, runbook)

---

**Version**: 3.0.0 | **Ratified**: 2025-12-04 | **Last Amended**: 2025-12-30
