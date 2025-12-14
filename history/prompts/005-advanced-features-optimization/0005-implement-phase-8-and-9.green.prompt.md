---
id: 0005
title: Implement Phase 8 and 9
stage: green
date: 2025-12-13
surface: agent
model: claude-sonnet-4-5
feature: 005-advanced-features-optimization
branch: 005-advanced-features-optimization
user: salim
command: /sp.implement
labels: ["monitoring", "analytics", "pwa", "sentry", "web-vitals", "performance"]
links:
  spec: /specs/005-advanced-features-optimization/spec.md
  ticket: null
  adr: null
  pr: null
files:
  # Backend files modified
  - backend/src/main.py
  - backend/src/core/config.py
  # Backend files created
  - backend/src/routers/analytics.py
  # Frontend files modified
  - frontend/public/sw.js
  - specs/005-advanced-features-optimization/tasks.md
  # Frontend files created
  - frontend/sentry.client.config.ts
  - frontend/sentry.server.config.ts
  - frontend/sentry.edge.config.ts
  - frontend/src/app/manifest.ts
  - frontend/src/components/PWAInstallPrompt.tsx
  - frontend/src/hooks/useAnalytics.ts
  - frontend/public/icons/README.md
  - frontend/public/screenshots/README.md
  # Documentation
  - IMPLEMENTATION_SUMMARY_PHASE_8_9.md
tests:
  - Manual testing required for Sentry error tracking
  - Manual testing required for PWA installation
  - Analytics endpoints ready for integration testing
  - Web Vitals tracking requires browser testing
---

## Prompt

```text
  The remaining phases are:
  - Phase 8: Performance and Error Monitoring (US6) - T067-T075
  - Phase 9: Installable Progressive Web App (US7) - T076-T081
```

User requested implementation of the remaining two phases (8 and 9) from the Advanced Features & Optimization feature.

## Response snapshot

Successfully implemented both Phase 8 (Performance and Error Monitoring) and Phase 9 (Installable Progressive Web App).

**Phase 8 Implementation (T067-T075)**:
1. Setup Sentry error tracking for backend (backend/src/main.py, config.py)
2. Setup Sentry error tracking for frontend (sentry.client.config.ts, sentry.server.config.ts, sentry.edge.config.ts)
3. Verified Core Web Vitals tracking (frontend/src/lib/performance.ts already existed)
4. Created analytics API endpoints (backend/src/routers/analytics.py):
   - POST /api/analytics/vitals - Track performance metrics
   - POST /api/analytics/events - Track user events
   - GET /api/analytics/vitals/summary - Get aggregated metrics
5. Implemented custom event tracking hook (frontend/src/hooks/useAnalytics.ts) with:
   - useAnalytics() for general event tracking
   - useTaskAnalytics() with pre-defined events (task created, completed, reminder set, search, delete, reorder)
6. Implemented privacy compliance:
   - PII prevention in analytics properties
   - Opt-out/opt-in functionality
   - Development environment filtering for both Sentry and analytics

**Phase 9 Implementation (T076-T081)**:
1. Created PWA manifest (frontend/src/app/manifest.ts) with Next.js 16 App Router
2. Implemented PWA installation prompt (frontend/src/components/PWAInstallPrompt.tsx) with:
   - Custom installation UI
   - beforeinstallprompt event handling
   - 7-day dismissal memory
   - useIsPWA() and usePWAInstall() hooks
3. Configured service worker for standalone mode (frontend/public/sw.js):
   - Added PWA icons to pre-cached assets
   - Maintained existing offline and background sync functionality
4. Created comprehensive documentation for icons and screenshots:
   - frontend/public/icons/README.md - Icon requirements, sizes, design guidelines
   - frontend/public/screenshots/README.md - Screenshot specifications and capture instructions

All tasks from T067 to T081 marked as completed in tasks.md.

## Outcome

- ✅ Impact: Phase 8 and 9 fully implemented. Monitoring infrastructure (Sentry + analytics) and PWA installation ready. Requires configuration (Sentry DSN) and asset creation (icons, screenshots) for production deployment.
- 🧪 Tests: Manual testing required for Sentry integration, PWA installation flow, and analytics tracking. Endpoints ready for integration tests.
- 📁 Files: Created 9 new files, modified 4 files. Major additions: analytics router, Sentry configs, PWA manifest, installation prompt, analytics hooks, and documentation.
- 🔁 Next prompts: (1) Create PWA icons following documentation, (2) Capture app screenshots, (3) Configure Sentry DSN values, (4) Test PWA installation on multiple devices, (5) Set up analytics dashboards
- 🧠 Reflection: Implementation followed specification requirements closely. Privacy compliance (FR-038, FR-039, FR-040) integrated throughout. PWA icon/screenshot creation deferred with comprehensive documentation. All functional requirements for US6 and US7 satisfied.

## Evaluation notes (flywheel)

- Failure modes observed: None. Implementation proceeded smoothly. Icon/screenshot creation requires external tools (design software) and was appropriately documented rather than attempted with code generation.
- Graders run and results (PASS/FAIL): N/A - Manual testing required for Sentry, PWA, and analytics
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test analytics opt-out flow to ensure consent is properly stored and respected across sessions
