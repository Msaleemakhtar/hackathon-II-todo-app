# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/JavaScript (frontend), Next.js 16 + FastAPI (backend), Better Auth (frontend), SQLModel, PostgreSQL, axios
**Primary Dependencies**:
  - Backend: FastAPI, SQLModel, Pydantic, APScheduler, aiosmtplib, pywebpush, sentry-sdk, redis, aiocache
  - Frontend: Next.js 16 (App Router), TypeScript, shadcn/ui, Tailwind CSS, @tanstack/react-query, @tanstack/react-virtual, @dnd-kit/core, web-vitals, @sentry/nextjs, date-fns, Better Auth
**Storage**: PostgreSQL (Neon Serverless) via SQLModel ORM, Redis for caching, browser IndexedDB for offline storage
**Testing**: pytest (backend), vitest + React Testing Library (frontend)
**Target Platform**: Web application (Next.js), Progressive Web App (PWA) compatible with modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Full-stack monorepo with web application and PWA capabilities
**Performance Goals**:
  - API response time: <100ms p95, <200ms p99
  - Task list with 10,000+ items scrolls smoothly at 60fps
  - Initial page bundle size: <200KB gzipped
  - Lighthouse performance score: >90
  - Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1
**Constraints**:
  - Initial bundle size must not exceed 200KB gzipped
  - Database queries must use appropriate indexes; no full table scans allowed
  - Cache hit rate must exceed 70% for frequently accessed data
  - Must meet WCAG 2.1 Level AA accessibility standards
  - Timezone handling: store all times in UTC server-side and convert to user's current timezone for display and reminders
  - All database queries must be scoped to authenticated user JWT user_id, not path parameter
**Scale/Scope**: Support 1,000 concurrent users during peak hours, typical users have 50-500 tasks, power users up to 10,000+ tasks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### AI-Driven Development Check
✅ **Status**: PASS
- Specification exists in `/specs/005-advanced-features-optimization/spec.md`
- Implementation will be AI-generated as per Constitution I
- Manual coding is forbidden except for documented AI limitations

### Full-Stack Architecture Check
✅ **Status**: PASS
- Backend: Python 3.11, FastAPI, SQLModel (per Constitution II)
- Frontend: Next.js 16 with App Router, TypeScript, shadcn/ui (per Constitution II)
- Repository structure matches `/frontend` and `/backend` directories (per Constitution II)

### Database & Persistence Check
✅ **Status**: PASS
- Using Neon Serverless PostgreSQL (per Constitution III)
- SQLModel ORM for all data access (per Constitution III)
- Async database operations with asyncpg (per Constitution III)
- Alembic for migrations (per Constitution III)
- Data isolation using JWT user_id (per Constitution III & IV)

### Authentication Security Check
✅ **Status**: PASS
- Better Auth with JWT plugin for frontend authentication (per Constitution IV)
- JWT token validation using shared secret (per Constitution IV)
- Path parameter validation against JWT user_id (per Constitution IV & X)
- Data scoping using JWT user_id, not path parameter (per Constitution III & IV)

### Backend Architecture Check
✅ **Status**: PASS
- API endpoints follow `/api/{user_id}/{resources}` pattern (per Constitution X)
- FastAPI with APIRouter organization (per Constitution V)
- Pydantic models for input/output validation (per Constitution V)
- Consistent error response format (per Constitution V)

### Frontend Architecture Check
✅ **Status**: PASS
- Next.js 16 with App Router used (per Constitution VI)
- Better Auth integration for authentication (per Constitution VI)
- API client at `@/lib/api-client` with Better Auth token attachment (per Constitution VI)
- Component organization follows standards (per Constitution VI)
- Accessibility standards (WCAG AA) addressed (per Constitution VI)

### Testing Standards Check
✅ **Status**: PASS
- Backend: pytest with pytest-asyncio (per Constitution VII)
- Frontend: Vitest + React Testing Library (per Constitution VII)
- Coverage requirements (80% backend, 70% frontend) addressed (per Constitution VII)

### Performance & Constraints Check
✅ **Status**: PASS
- Performance goals align with Constitution requirements (per Technical Context)
- Bundle size constraint (<200KB gzipped) noted (per Constitution)
- API response time constraints (<100ms p95) noted (per Constitution)
- WCAG AA compliance requirement addressed (per Constitution)

### Violations: None identified
All requirements from the constitution are satisfied by this implementation plan.

## Project Structure

### Documentation (this feature)

```text
specs/005-advanced-features-optimization/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/              # SQLModel entities (Reminder, WebVital, etc.)
│   ├── services/            # Business logic (NotificationService, etc.)
│   ├── routers/             # API endpoints (reminders, etc.)
│   ├── workers/             # Background tasks (scheduler for reminders)
│   ├── core/                # Config, database, security, cache
│   ├── schemas/             # Pydantic schemas for API
│   └── lib/                 # Utility functions
├── alembic/
│   └── versions/            # Database migration files
├── requirements.txt         # Python dependencies
└── tests/
    ├── unit/                # Unit tests for business logic
    ├── integration/         # Integration tests for API endpoints
    └── conftest.py          # pytest configuration

frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   ├── components/          # React components (notifications, keyboard shortcuts, etc.)
│   ├── hooks/               # Custom React hooks (useNotifications, etc.)
│   ├── lib/                 # Utilities (api-client, performance tracking, etc.)
│   ├── types/               # TypeScript type definitions
│   └── styles/              # Global styles
├── public/                  # Static assets (PWA icons, service worker, offline page)
├── package.json             # Frontend dependencies and scripts
└── tests/
    ├── unit/                # Unit tests for utilities and hooks
    ├── components/          # Component tests
    └── e2e/                 # End-to-end tests (Playwright)
```

**Structure Decision**: Web application with full-stack monorepo structure selected. This follows the constitution's requirement for distinct `/frontend` and `/backend` directories with clear separation of concerns, enabling atomic changes across frontend and backend while maintaining architectural boundaries.

## Phase 0: Research & Unknowns Resolution

Research will address all technical unknowns and implementation decisions needed for this feature:

### Unknowns to Resolve

1. **Web Push Notification Implementation**
   - How to set up VAPID keys for browser notifications
   - Integration with pywebpush in backend and service worker in frontend
   - Handling browser notification permissions

2. **Background Task Processing**
   - Configuring APScheduler for reminder processing
   - Ensuring reliable execution every minute
   - Handling failures and retries

3. **Redis Caching Strategy**
   - Optimal cache TTL for different data types
   - Cache invalidation patterns for task updates
   - Connection pooling and error handling

4. **Virtual Scrolling Implementation**
   - @tanstack/react-virtual setup with variable height items
   - Performance testing with 10,000+ tasks
   - Integration with existing task list

5. **Service Worker for PWA**
   - Caching strategy for offline functionality
   - Background sync for offline changes
   - Handling updates to service worker

6. **Sentry Error Tracking Setup**
   - Frontend and backend integration
   - Privacy considerations and PII filtering
   - Error grouping and alerting setup

7. **Email Notification Configuration**
   - SMTP setup with Gmail/other provider
   - Handling delivery failures and bounces
   - Rate limiting to prevent spam

### Research Tasks

1. **Web Push Implementation Research**
   - Task: "Research web push notification setup with VAPID keys for FastAPI + Next.js"
   - Expected outcome: VAPID key generation and configuration process documented

2. **Background Processing Research**
   - Task: "Research APScheduler integration and reliable execution patterns"
   - Expected outcome: Background worker setup with error handling patterns

3. **Caching Best Practices Research**
   - Task: "Research Redis caching patterns with aiocache for FastAPI"
   - Expected outcome: Caching strategy with TTL recommendations

4. **Virtual Scrolling Patterns Research**
   - Task: "Research @tanstack/react-virtual implementation for large lists"
   - Expected outcome: Virtual scrolling setup with performance benchmarks

5. **PWA Service Worker Research**
   - Task: "Research service worker implementation for offline functionality"
   - Expected outcome: Service worker code with caching and sync strategies

6. **Error Tracking Research**
   - Task: "Research Sentry integration with Next.js and FastAPI"
   - Expected outcome: Error tracking setup with privacy compliance

7. **Email Delivery Research**
   - Task: "Research email notification implementation with aiosmtplib"
   - Expected outcome: SMTP configuration and delivery handling patterns

### Research Output: research.md
Location: `/specs/005-advanced-features-optimization/research.md`

Each research task will produce:
- Decision: what was chosen
- Rationale: why chosen
- Alternatives considered: what else evaluated
- Implementation approach: how to implement

## Phase 1: Design & Contracts

### Prerequisites
- research.md complete with all unknowns resolved

### 1. Data Model Design
- Extract entities from feature spec → data-model.md
- Entity: Reminder (with fields, relationships, validation rules)
- Entity: WebVital (for performance tracking)
- Entity: AnalyticsEvent (for user event tracking)
- Entity: CacheEntry (for cache management)
- Entity: TaskOrder (for drag-and-drop ordering)

### 2. API Contract Design
- Generate API contracts from functional requirements
- Reminder endpoints: POST /{user_id}/reminders, GET /{user_id}/reminders, POST /{user_id}/reminders/{id}/snooze, DELETE /{user_id}/reminders/{id}
- Performance tracking endpoints: POST /api/analytics/vitals, POST /api/analytics/events
- Task reordering endpoint: POST /{user_id}/tasks/reorder
- Output OpenAPI 3.0 schema to contracts/

### 3. Quickstart Guide
- How to set up the development environment
- How to configure required services (Redis, SMTP, Sentry)
- How to run both frontend and backend
- How to test the new features

### 4. Agent Context Update
- Run `.specify/scripts/bash/update-agent-context.sh qwen`
- Add new technologies: APScheduler, aiosmtplib, pywebpush, sentry-sdk, redis, aiocache, @tanstack/react-virtual, @dnd-kit/core
- Preserve manual additions between markers

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
