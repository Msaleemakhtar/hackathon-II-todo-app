# Tasks: Fix ChatKit Integration and Better-Auth Backend

**Input**: Design documents from `/specs/003-fix-chatkit-auth/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT requested in the feature specification - this is a bug fix with manual verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a full-stack web application:
- Frontend: `phaseIII/frontend/src/`
- Backend: `phaseIII/backend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [X] T001 Generate Better Auth secret key for JWT token signing using Node.js crypto
- [X] T002 [P] Configure frontend environment variables in phaseIII/frontend/.env.local (DATABASE_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL, NEXT_PUBLIC_API_URL)
- [X] T003 [P] Configure backend environment variables in phaseIII/backend/.env (DATABASE_URL, BETTER_AUTH_SECRET)
- [X] T004 Verify both frontend and backend use identical BETTER_AUTH_SECRET value

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create Better Auth database migration file phaseIII/backend/alembic/versions/003_better_auth_tables.py
- [X] T006 Add user table creation with columns (id, email, emailVerified, name, image, createdAt, updatedAt) and indexes
- [X] T007 Add session table creation with foreign key to user, columns (id, userId, expiresAt, token, ipAddress, userAgent, createdAt, updatedAt) and indexes
- [X] T008 Add account table creation with foreign key to user, columns (id, userId, accountId, providerId, password, accessToken, refreshToken, expiresAt, createdAt, updatedAt) and indexes
- [X] T009 Add verification table creation with columns (id, identifier, value, expiresAt, createdAt, updatedAt) and indexes
- [X] T010 Add migration downgrade functions for all four tables to enable rollback
- [X] T011 Run database migration using uv run alembic upgrade head from phaseIII/backend directory
- [X] T012 Verify all four Better Auth tables exist in database (user, session, account, verification)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Developer Can Build Frontend Without Errors (Priority: P1) 🎯 MVP

**Goal**: Fix TypeScript compilation errors by adding missing type definitions for ChatKit and Better Auth

**Independent Test**: Run `bun run build` in phaseIII/frontend and verify zero TypeScript errors

### Implementation for User Story 1

- [X] T013 [P] [US1] Create types directory at phaseIII/frontend/src/types/
- [X] T014 [P] [US1] Copy type definitions from specs/003-fix-chatkit-auth/contracts/auth-types.ts to phaseIII/frontend/src/types/auth.d.ts
- [X] T015 [US1] Update phaseIII/frontend/tsconfig.json to include types directory in typeRoots and include paths
- [X] T016 [US1] Test frontend build by running bun run build in phaseIII/frontend directory
- [X] T017 [US1] Verify zero TypeScript compilation errors in build output

**Checkpoint**: At this point, frontend should build successfully without type errors

---

## Phase 4: User Story 2 - User Can Access Chat Interface with Valid Authentication (Priority: P1)

**Goal**: Fix JWT token retrieval and Better Auth configuration to enable authenticated chat access

**Independent Test**: User can sign up, log in, navigate to chat page, and see chat interface without "Authentication Token Missing" errors

### Implementation for User Story 2

- [X] T018 [P] [US2] Add Better Auth JWT plugin import to phaseIII/frontend/src/lib/auth-server.ts
- [X] T019 [US2] Configure Better Auth server with JWT plugin (expiresIn: 7d, algorithm: HS256, issuer: phaseiii-app) in phaseIII/frontend/src/lib/auth-server.ts
- [X] T020 [P] [US2] Add Better Auth JWT client plugin import to phaseIII/frontend/src/lib/auth-client.ts
- [X] T021 [US2] Configure Better Auth client with jwtClient plugin in phaseIII/frontend/src/lib/auth-client.ts
- [X] T022 [US2] Create JWT token endpoint directory at phaseIII/frontend/src/app/api/auth/token/
- [X] T023 [US2] Implement JWT token endpoint in phaseIII/frontend/src/app/api/auth/token/route.ts using getAuth and getSession
- [X] T024 [US2] Add error handling for missing session and missing JWT in token endpoint
- [X] T025 [US2] Update phaseIII/frontend/src/app/chat/page.tsx to import BetterAuthSession type from @/types/auth.d
- [X] T026 [US2] Fix JWT token retrieval in chat page useEffect to check session.jwt first, fallback to /api/auth/token endpoint
- [X] T027 [US2] Remove options wrapper from useChatKit call in phaseIII/frontend/src/app/chat/page.tsx
- [X] T028 [US2] Pass apiUrl and authToken as top-level properties to useChatKit hook
- [X] T029 [US2] Move handler callbacks (onError, onResponseEnd, onThreadChange) to top level in useChatKit call
- [ ] T030 [US2] Test user registration flow by creating new account and verifying user and account rows in database
- [ ] T031 [US2] Test user login flow by authenticating and verifying session row created in database
- [ ] T032 [US2] Test JWT token retrieval by accessing /api/auth/token endpoint and verifying response contains token field
- [ ] T033 [US2] Test chat page access by navigating to /chat after login and verifying no authentication errors

**Checkpoint**: At this point, users should be able to log in and access the chat interface without authentication errors

---

## Phase 5: User Story 3 - User Can Send Messages and Receive AI Responses (Priority: P1)

**Goal**: Verify authenticated chat message flow works end-to-end with AI responses

**Independent Test**: Authenticated user can send a message and receive an AI-generated response within 5 seconds

### Implementation for User Story 3

- [ ] T034 [US3] Verify backend JWT validation in phaseIII/backend/app/dependencies/auth.py uses BETTER_AUTH_SECRET from environment
- [ ] T035 [US3] Test sending chat message from frontend and verify Authorization header contains Bearer token
- [ ] T036 [US3] Test backend receives and validates JWT token successfully
- [ ] T037 [US3] Test backend extracts user_id from JWT sub claim
- [ ] T038 [US3] Test AI response generation and verify response returned within 5 seconds
- [ ] T039 [US3] Test conversation history persistence in messages table with correct user_id
- [ ] T040 [US3] Test multi-turn conversation maintains context from previous messages

**Checkpoint**: Core chat functionality should work end-to-end with authentication

---

## Phase 6: User Story 4 - System Enforces Multi-User Data Isolation (Priority: P2)

**Goal**: Verify multi-user data isolation - each user sees only their own tasks and conversations

**Independent Test**: Two different users can register, log in, create tasks, and verify each user only sees their own data

### Implementation for User Story 4

- [ ] T041 [US4] Verify tasks_phaseiii queries filter by user_id from JWT in phaseIII/backend/app/services/task_service.py
- [ ] T042 [US4] Verify conversations queries filter by user_id from JWT in phaseIII/backend/app/services/conversation_service.py
- [ ] T043 [US4] Verify messages queries filter by user_id from JWT in phaseIII/backend/app/services/message_service.py
- [ ] T044 [US4] Test creating two different user accounts and logging in as each
- [ ] T045 [US4] Test User A creates tasks and conversations
- [ ] T046 [US4] Test User B cannot see User A tasks by querying database and verifying user_id isolation
- [ ] T047 [US4] Test User B cannot see User A conversations by querying database and verifying user_id isolation
- [ ] T048 [US4] Test cross-user data access attempts are denied with appropriate errors

**Checkpoint**: Multi-user data isolation should be fully enforced

---

## Phase 7: User Story 5 - Developers Can Manage User Accounts (Priority: P2)

**Goal**: Enable developers to query and manage user accounts through database

**Independent Test**: Developers can query user accounts, sessions, and verify authentication state through database queries

### Implementation for User Story 5

- [ ] T049 [US5] Document SQL query for viewing all users (SELECT from user table) in quickstart.md
- [ ] T050 [US5] Document SQL query for viewing user sessions (SELECT from session table with userId join) in quickstart.md
- [ ] T051 [US5] Document SQL query for viewing user authentication accounts (SELECT from account table) in quickstart.md
- [ ] T052 [US5] Test querying user table to view registered users
- [ ] T053 [US5] Test querying session table to view active sessions with expiration times
- [ ] T054 [US5] Test querying account table to verify authentication provider information
- [ ] T055 [US5] Test updating user record and verify changes persist with integrity maintained

**Checkpoint**: Developer tooling for user account management should be documented and tested

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [ ] T056 [P] Update CLAUDE.md to document Neon Serverless PostgreSQL as active technology
- [ ] T057 [P] Run frontend build validation using bun run build and verify zero errors
- [ ] T058 [P] Run backend startup validation using uv run uvicorn app.main:app and verify no startup errors
- [ ] T059 Test complete user registration and login flow end-to-end
- [ ] T060 Test complete chat message flow with AI responses end-to-end
- [ ] T061 Test session persistence across page refreshes
- [ ] T062 Verify all success criteria from spec.md are met
- [ ] T063 Run quickstart.md validation by following all setup steps
- [ ] T064 Document any environment variable changes in .env.example files
- [ ] T065 Create pull request with summary of fixes and testing results

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational
  - User Story 2 (P1): Can start after Foundational (depends on US1 types being created)
  - User Story 3 (P1): Can start after US2 (requires authentication working)
  - User Story 4 (P2): Can start after US3 (requires chat working)
  - User Story 5 (P2): Can start after Foundational (independent of other stories)
- **Polish (Phase 8)**: Depends on all P1 user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1 (needs type definitions) - Sequential
- **User Story 3 (P1)**: Depends on US2 (needs authentication working) - Sequential
- **User Story 4 (P2)**: Depends on US3 (needs chat working) - Sequential
- **User Story 5 (P2)**: Depends on Foundational (Phase 2) - Can run in parallel with US1-4

### Within Each User Story

- Setup tasks can run in parallel where marked [P]
- Type definition creation before frontend build validation
- Backend configuration before JWT token endpoint creation
- JWT token retrieval fix before chat interface fix
- Individual verification tasks sequential after implementation

### Parallel Opportunities

- Phase 1: T002 and T003 (frontend and backend .env configuration) can run in parallel
- Phase 2: T006-T009 (migration file table additions) can be written in parallel
- US1: T013 and T014 (create directory and copy types) can run in parallel
- US2: T018/T019 (server config) and T020/T021 (client config) can run in parallel if different developers
- US5 can run in parallel with US1-4 (only depends on Foundational phase)
- Phase 8: T056, T057, T058 (documentation and build validation) can run in parallel

---

## Parallel Example: User Story 2

```bash
# These tasks can run in parallel (different files):
Task T018: "Add Better Auth JWT plugin import to auth-server.ts"
Task T020: "Add Better Auth JWT client plugin import to auth-client.ts"

# But these must run sequentially:
Task T022-T024: Create token endpoint (must complete before testing)
Task T025-T029: Fix chat page (depends on types from US1)
Task T030-T033: Testing (depends on implementation being complete)
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 Only)

1. Complete Phase 1: Setup (environment configuration)
2. Complete Phase 2: Foundational (database migration) - CRITICAL
3. Complete Phase 3: User Story 1 (type definitions)
4. Complete Phase 4: User Story 2 (authentication and token retrieval)
5. Complete Phase 5: User Story 3 (chat message flow)
6. **STOP and VALIDATE**: Test end-to-end chat with authentication
7. Demo/validate before proceeding to P2 stories

### Incremental Delivery

1. Setup + Foundational → Database ready
2. Add User Story 1 → Frontend builds successfully
3. Add User Story 2 → Users can authenticate and access chat
4. Add User Story 3 → Chat messages work end-to-end (MVP COMPLETE!)
5. Add User Story 4 → Multi-user isolation verified
6. Add User Story 5 → Developer tooling documented
7. Polish → Production ready

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T012)
2. Developer A: User Story 1 (T013-T017) - Type definitions
3. Wait for US1, then Developer B: User Story 2 (T018-T033) - Authentication
4. Wait for US2, then Developer C: User Story 3 (T034-T040) - Chat flow
5. Developer D (parallel): User Story 5 (T049-T055) - Developer tooling
6. All together: User Story 4 testing (T041-T048) and Polish (T056-T065)

---

## Task Summary

**Total Tasks**: 65 tasks

**Tasks by User Story**:
- Setup (Phase 1): 4 tasks
- Foundational (Phase 2): 8 tasks
- User Story 1 (P1): 5 tasks
- User Story 2 (P1): 16 tasks
- User Story 3 (P1): 7 tasks
- User Story 4 (P2): 8 tasks
- User Story 5 (P2): 7 tasks
- Polish (Phase 8): 10 tasks

**Parallel Opportunities**: 14 tasks marked [P] can run in parallel

**Independent Test Criteria**:
- US1: Frontend builds with zero TypeScript errors
- US2: Users can authenticate and access chat without errors
- US3: Chat messages work with AI responses in <5s
- US4: Multi-user data isolation enforced (no cross-user access)
- US5: Developers can query and manage user accounts

**MVP Scope**: User Stories 1, 2, 3 (35 tasks including Setup and Foundational)

---

## Format Validation

✅ All tasks follow checklist format: `- [ ] [ID] [P?] [Story] Description with file path`
✅ All task IDs sequential (T001-T065)
✅ All user story tasks labeled with [US1]-[US5]
✅ All tasks include specific file paths where applicable
✅ Parallel tasks marked with [P] where appropriate
✅ Tasks organized by user story for independent implementation

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No tests included (manual verification only per spec requirements)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Frontend type fixes enable build, authentication fixes enable chat access, chat flow fixes enable end-to-end functionality
- Multi-user isolation and developer tooling are P2 (important but not blocking for MVP demonstration)
