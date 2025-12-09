---
description: "Task list for feature implementation: Foundational Backend Setup"
---

# Tasks: Foundational Backend Setup

**Input**: Design documents from `/specs/001-foundational-backend-setup/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/auth-api.yaml

**Tests**: Test tasks are included as specified in `spec.md` and `plan.md`.

**Organization**: Tasks are grouped by phase and user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- All paths are relative to the `backend/` directory.

---

## Phase 1: Project Setup & Configuration

**Purpose**: Initialize the backend project, configure core utilities, and define dependencies.

- [x] T001 Create backend directory structure as defined in `plan.md` (src, tests, alembic).
- [x] T002 Create `backend/pyproject.toml` with dependencies from `plan.md` (fastapi, sqlmodel, etc.).
- [x] T003 Create `backend/.env.example` with all required environment variables from `research.md`.
- [x] T004 [P] Implement settings management using pydantic-settings in `backend/src/core/config.py`.
- [x] T005 [P] Implement structured logging configuration in `backend/src/core/logging_config.py`.
- [x] T006 [P] Implement password hashing (bcrypt) and JWT utilities in `backend/src/core/security.py`.

---

## Phase 2: Foundational Backend & Database

**Purpose**: Establish the core application, database connectivity, and migration framework.

- [x] T007 Implement async database connection pool and session management in `backend/src/core/database.py`.
- [x] T008 Configure Alembic for async migrations in `backend/alembic/env.py` and `alembic.ini`.
- [x] T009 Create the main FastAPI application in `backend/src/main.py` with logging, CORS, and startup validation.
- [x] T010 [US6] Create SQLModel entities for User, Task, Tag, and TaskTagLink in `backend/src/models/`. (user.py, task.py, tag.py, task_tag_link.py)
- [ ] T011 [US6] Generate the initial Alembic migration file in `backend/alembic/versions/` to create all tables and indexes.

---

## Phase 3: Testing Infrastructure

**Purpose**: Set up the testing framework and fixtures for isolated and repeatable tests.

- [x] T012 Configure `pytest.ini` for `pytest-asyncio` and test paths.
- [x] T013 Implement test database fixtures, session management, and an async test client in `backend/tests/conftest.py`.
- [x] T014 [US6] Write unit tests for all data models and their relationships in `backend/tests/test_models.py`.

---

## Phase 4: User Story 1 - New User Registration (Priority: P1)

**Goal**: A new user can create an account.
**Independent Test**: API request to POST /api/v1/auth/register creates a user in the test database.

### Tests for User Story 1
- [x] T015 [P] [US1] Write integration tests for user registration (success, duplicate email, short password) in `backend/tests/test_auth.py`.

### Implementation for User Story 1
- [x] T016 [P] [US1] Create Pydantic schemas for user creation and response in `backend/src/schemas/user.py`.
- [x] T017 [P] [US1] Create Pydantic schemas for registration requests in `backend/src/schemas/auth.py`.
- [x] T018 [US1] Implement user registration logic (hashing password, creating user) in `backend/src/services/auth_service.py`.
- [x] T019 [US1] Create the POST /api/v1/auth/register endpoint in `backend/src/routers/auth.py`.
- [x] T020 [US1] Include the auth router in the main FastAPI app in `backend/src/main.py`.

---

## Phase 5: User Story 2 - User Login (Priority: P1)

**Goal**: A registered user can log in and receive authentication tokens.
**Independent Test**: API request to POST /api/v1/auth/login with valid credentials returns an access token and a refresh token cookie.

### Tests for User Story 2
- [x] T021 [P] [US2] Write integration tests for user login (success, invalid credentials) in `backend/tests/test_auth.py`.

### Implementation for User Story 2
- [x] T022 [P] [US2] Create Pydantic schemas for tokens in `backend/src/schemas/token.py`.
- [x] T023 [US2] Implement user login logic (verifying password, creating tokens) in `backend/src/services/auth_service.py`.
- [x] T024 [US2] Create the POST /api/v1/auth/login endpoint in `backend/src/routers/auth.py`.

---

## Phase 6: User Story 3 - Access Protected Resources (Priority: P1)

**Goal**: An authenticated user can access protected endpoints using their access token.
**Independent Test**: API request to GET /api/v1/auth/me with a valid token returns the user's profile.

### Tests for User Story 3
- [x] T025 [P] [US3] Write integration tests for the /auth/me endpoint (success, expired token, invalid token) in `backend/tests/test_auth.py`.

### Implementation for User Story 3
- [x] T026 [US3] Implement the `get_current_user` FastAPI dependency in `backend/src/core/dependencies.py`.
- [x] T027 [US3] Create the GET /api/v1/auth/me endpoint in `backend/src/routers/auth.py`, using the `get_current_user` dependency.

---

## Phase 7: User Story 4 - Token Refresh (Priority: P1)

**Goal**: An authenticated user can get a new access token using a refresh token.
**Independent Test**: API request to POST /api/v1/auth/refresh with a valid refresh cookie returns a new access token.

### Tests for User Story 4
- [x] T028 [P] [US4] Write integration tests for token refresh (success, expired refresh token) in `backend/tests/test_auth.py`.

### Implementation for User Story 4
- [x] T029 [US4] Implement token refresh logic in `backend/src/services/auth_service.py`.
- [x] T030 [US4] Create the POST /api/v1/auth/refresh endpoint in `backend/src/routers/auth.py`.

---

## Phase 8: User Story 5 - User Logout (Priority: P2)

**Goal**: An authenticated user can log out, clearing their session.
**Independent Test**: API request to POST /api/v1/auth/logout clears the refresh token cookie.

### Tests for User Story 5
- [x] T031 [P] [US5] Write integration tests for user logout in `backend/tests/test_auth.py`.

### Implementation for User Story 5
- [x] T032 [US5] Implement logout logic (clearing cookie) in `backend/src/routers/auth.py`. (Service layer may not be needed).

---

## Phase 9: Polish & Deployment

**Purpose**: Finalize the application, add documentation, and prepare for deployment.

- [x] T033 [P] Implement rate limiting using `slowapi` and apply it to authentication routes in `backend/src/main.py` and `backend/src/routers/auth.py`.
- [x] T034 [P] Write the `backend/Dockerfile` for containerizing the application.
- [x] T035 [P] Write the `backend/README.md` with comprehensive setup and development instructions.
- [x] T036 Final code review, formatting, and linting pass across the entire `backend/` codebase.
- [ ] T037 Validate the completed backend against `quickstart.md`.

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)** must be completed first.
- **Phase 2 (Foundational)** depends on Phase 1.
- **Phase 3 (Testing Infra)** depends on Phase 2.
- **User Story Phases (4-8)** depend on Phase 3. They can be implemented in parallel after Phase 3 is complete.
- **Phase 9 (Polish)** depends on all user stories being complete.

### User Story Dependencies
- **US6 (Database)** is foundational and is handled in Phase 2.
- **US1-US5** are largely independent but follow a logical progression (Register -> Login -> Access -> Refresh/Logout). Implementing them in order is recommended.

### Parallel Opportunities
- Within Phase 1, tasks T004, T005, T006 can be done in parallel.
- Once Phase 3 is complete, dif
arallel.
- Test creation and schema creation within each user story phase can be done in parallel.
