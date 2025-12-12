---

description: "Task list for Better Auth Integration feature implementation"
---

# Tasks: Better Auth Integration

**Input**: Design documents from `/specs/[004-better-auth-integration]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no depend
encies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`

<!--
  ============================================================================
  IMPORTANT: The tasks below are based on actual design documents for Better Auth Integration.
  These tasks are organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Install Better Auth dependencies in frontend package.json
- [x] T002 Install python-jose and cryptography dependencies in backend pyproject.toml
- [x] T003 [P] Configure environment variables for BETTER_AUTH_SECRET in both frontend and backend

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [x] T004 Implement JWT validation dependency in backend using python-jose
- [x] T005 [P] Create API client at `@/lib/api-client` with axios interceptors
- [x] T006 [P] Implement path parameter validation middleware to compare path user_id with JWT user_id
- [x] T007 Update User model to use UUID from Better Auth as primary key
- [x] T008 Add user_id foreign key to Task and Tag models with proper indexing
- [x] T009 Configure rate limiting on auth endpoints with slowapi

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration with Better Auth (Priority: P1) 🎯 MVP

**Goal**: Enable users to register using Better Auth to create a secure account with standard authentication

**Independent Test**: Can be fully tested by registering a new user account and verifying the account is created in the system with proper feedback

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

- [ ] T010 [P] [US1] Contract test for /api/v1/auth/register endpoint in backend/tests/contract/test_auth.py
- [ ] T011 [P] [US1] Integration test for registration flow in backend/tests/integration/test_auth.py

### Implementation for User Story 1

- [x] T012 [P] [US1] Create registration endpoint in backend/src/routers/auth.py
- [x] T013 [P] [US1] Integrate Better Auth with JWT plugin in frontend/src/lib/auth.ts
- [x] T014 [US1] Implement registration form UI component in frontend/src/components/auth/RegistrationForm.tsx
- [x] T015 [US1] Add registration functionality to API client in frontend/src/lib/api-client.ts
- [x] T016 [US1] Add validation for duplicate emails and proper error feedback

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - User Login with Better Auth (Priority: P1)

**Goal**: Enable users to login using Better Auth to access their todo lists with proper authentication

**Independent Test**: Can be fully tested by logging in with existing credentials and gaining access to the system

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T017 [P] [US2] Contract test for /api/v1/auth/login endpoint in backend/tests/contract/test_auth.py
- [ ] T018 [P] [US2] Integration test for login flow in backend/tests/integration/test_auth.py

### Implementation for User Story 2

- [x] T019 [P] [US2] Create login endpoint in backend/src/routers/auth.py
- [x] T020 [P] [US2] Implement login functionality in Better Auth integration in frontend/src/lib/auth.ts
- [x] T021 [US2] Implement login form UI component in frontend/src/components/auth/LoginForm.tsx
- [x] T022 [US2] Add login functionality to API client in frontend/src/lib/api-client.ts
- [x] T023 [US2] Implement session management across browser tabs

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - API Security with Better Auth Tokens (Priority: P1)

**Goal**: Secure authenticated user's API calls with Better Auth tokens to keep their data private and secure

**Independent Test**: Can be tested by making API calls with/without valid tokens to verify access control

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T024 [P] [US3] Contract test for protected endpoints requiring Authorization header in backend/tests/contract/test_auth.py
- [ ] T025 [P] [US3] Integration test for unauthorized access attempts in backend/tests/integration/test_auth.py
- [ ] T026 [P] [US3] Unit test for JWT token validation in backend/tests/unit/test_security.py

### Implementation for User Story 3

- [x] T027 [P] [US3] Create authentication middleware to validate JWT tokens in backend/src/core/security.py
- [x] T028 [US3] Update all user-specific endpoints to require Authorization: Bearer <token> header
- [x] T029 [US3] Implement 401 response for unauthenticated requests
- [x] T030 [US3] Add token refresh flow implementation in both frontend and backend
- [x] T031 [US3] Add error handling for expired tokens

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all work independently

---

## Phase 6: User Story 4 - User Data Isolation (Priority: P2)

**Goal**: Ensure authenticated user can only see their own tasks and tags to maintain privacy from other users

**Independent Test**: Can be tested by attempting to access other users' data with various user accounts

### Tests for User Story 4 (OPTIONAL - only if tests requested) ⚠️

- [ ] T032 [P] [US4] Contract test for user-specific endpoints following {user_id}/resources pattern in backend/tests/contract/test_auth.py
- [ ] T033 [P] [US4] Integration test for data isolation (user A cannot access user B's data) in backend/tests/integration/test_isolation.py
- [ ] T034 [P] [US4] Unit test for path parameter validation against JWT user_id in backend/tests/unit/test_security.py

### Implementation for User Story 4

- [x] T035 [P] [US4] Update all task endpoints to follow /api/{user_id}/tasks pattern in backend/src/routers/task.py
- [x] T036 [P] [US4] Update all tag endpoints to follow /api/{user_id}/tags pattern in backend/src/routers/tag.py
- [x] T037 [US4] Implement strict path parameter validation against JWT user_id
- [x] T038 [US4] Ensure all database queries are scoped to JWT user_id, not path parameter
- [x] T039 [US4] Return 403 Forbidden for unauthorized cross-user access attempts

**Checkpoint**: At this point, all user stories should be independently functional

---

## Phase 7: User Story 5 - Frontend-Backend Token Integration (Priority: P2)

**Goal**: Ensure seamless token flow between Better Auth and backend for cohesive and secure authentication

**Independent Test**: Can be tested by verifying token flow during API calls and refresh scenarios

### Tests for User Story 5 (OPTIONAL - only if tests requested) ⚠️

- [ ] T040 [P] [US5] Integration test for token flow with API calls in frontend/tests/integration/test_auth_flow.ts
- [ ] T041 [P] [US5] Unit test for axios interceptors with token attachment in frontend/tests/unit/test_api_client.ts
- [ ] T042 [P] [US5] Integration test for token refresh functionality in frontend/tests/integration/test_token_refresh.ts

### Implementation for User Story 5

- [x] T043 [P] [US5] Update API client to automatically include Better Auth tokens in all requests via interceptors
- [x] T044 [US5] Ensure backend validates tokens with same shared secret
- [x] T045 [US5] Implement seamless token refresh before expiry in frontend
- [x] T046 [US5] Add proper error handling for token refresh failures

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T047 [P] Update API documentation with new auth endpoints in backend/src/main.py
- [x] T048 Migrate existing API endpoints to follow {user_id}/resources pattern
- [x] T049 [P] Add comprehensive error handling for network issues in frontend/src/lib/api-client.ts
- [x] T050 Security hardening and validation of all auth mechanisms
- [x] T051 Run quickstart.md validation to verify complete flow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Builds on US3 for security
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Integrates across all stories

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for /api/v1/auth/register endpoint in backend/tests/contract/test_auth.py"
Task: "Integration test for registration flow in backend/tests/integration/test_auth.py"

# Launch implementation tasks together:
Task: "Create registration endpoint in backend/src/routers/auth.py"
Task: "Integrate Better Auth with JWT plugin in frontend/src/lib/auth.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
   - Developer E: User Story 5
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
