# Feature Specification: Foundational Backend Setup

**Feature Branch**: `001-foundational-backend-setup`
**Created**: 2025-12-09
**Status**: Draft
**Constitution Version**: 2.2.0
**Input**: User description: "Generate a complete feature specification for the 'Foundational Backend Setup' of the Todo App. This specification covers the initial database schema for all Phase II entities and the complete user authentication and authorization API."

---

## 1. Overview

This specification defines the foundational backend infrastructure for the Todo App Phase II, encompassing:

1. **Database Schema**: Complete SQLModel entity definitions for User, Tag, Task, and TaskTagLink entities with all relationships, constraints, and indexes as mandated by the constitution.

2. **Authentication System**: A complete RESTful authentication API enabling user registration, login, token management, and protected resource access via JWT tokens.

This feature serves as the prerequisite for all subsequent features, establishing the data persistence layer and security infrastructure upon which the entire application is built.

---

## Clarifications

### Session 2025-12-09

- Q: Database Configuration & Environment - The spec defines PostgreSQL as the database and mentions asyncpg driver, but doesn't specify connection pooling behavior or environment configuration details. → A: Configure a small pool (min=2, max=5) appropriate for development/testing with environment variables for customization
- Q: Migration Execution Strategy - The spec defines Alembic migrations but doesn't specify who is responsible for executing them or when they should run. → A: Migrations are executed manually by developers/operators via CLI commands before deployment
- Q: JWT Secret Key Management - The spec requires a minimum 256-bit JWT secret stored in `JWT_SECRET_KEY` environment variable, but doesn't specify generation method or validation requirements. → A: Require a cryptographically secure 256-bit (32-byte) secret generated via secure method (e.g., `openssl rand -hex 32`), validated at startup
- Q: CORS Configuration Specifics - The spec states "Allow localhost origins" for development but doesn't specify which ports or how broad the allowance should be. → A: localhost:8000 fastapi uvicorn server
- Q: Test Database Strategy - The spec includes extensive test acceptance criteria but doesn't specify how test databases should be configured or isolated. → A: Create a separate test database (e.g., `todo_test`) that is created/dropped or reset before each test run

---

## 2. User Scenarios & Testing

### User Story 1 - New User Registration (Priority: P1)

A new user visits the application and creates an account to begin managing their tasks. The system validates their information, securely stores their credentials, and confirms successful registration.

**Why this priority**: Registration is the entry point for all users. Without the ability to create accounts, no other features can be accessed. This is the foundational user journey.

**Independent Test**: Can be fully tested by submitting a registration form with valid credentials and verifying the user record is created in the database with a hashed password.

**Acceptance Scenarios**:

1. **Given** no user exists with the email "newuser@example.com", **When** a user submits registration with email "newuser@example.com", password "SecurePass123!", and name "John Doe", **Then** the system creates the user account and returns the user object (excluding password) with HTTP 201 Created.

2. **Given** a user already exists with the email "existing@example.com", **When** another user attempts to register with email "existing@example.com", **Then** the system returns HTTP 400 Bad Request with error code "EMAIL_ALREADY_EXISTS" and message "A user with this email already exists".

3. **Given** a user submits registration with password "short", **When** the system validates the request, **Then** the system returns HTTP 400 Bad Request with error code "PASSWORD_TOO_SHORT" and message "Password must be at least 8 characters".

---

### User Story 2 - User Login and Token Acquisition (Priority: P1)

A registered user enters their credentials to access the application. The system validates their identity and issues secure tokens for subsequent authenticated requests.

**Why this priority**: Login is essential for accessing any protected functionality. Without authentication, users cannot interact with their data.

**Independent Test**: Can be fully tested by submitting valid credentials and verifying both an access token is returned in the response body and a refresh token is set in an HttpOnly cookie.

**Acceptance Scenarios**:

1. **Given** a registered user with email "user@example.com" and password "SecurePass123!", **When** the user submits login credentials, **Then** the system returns HTTP 200 OK with an access_token, token_type "bearer", and sets the refresh_token in an HttpOnly, Secure, SameSite=Strict cookie.

2. **Given** a registered user with email "user@example.com", **When** the user submits login with an incorrect password "WrongPassword", **Then** the system returns HTTP 401 Unauthorized with error code "INVALID_CREDENTIALS" and message "Invalid email or password".

3. **Given** no user exists with email "nonexistent@example.com", **When** someone attempts to login with that email, **Then** the system returns HTTP 401 Unauthorized with error code "INVALID_CREDENTIALS" and message "Invalid email or password" (same message to prevent user enumeration).

---

### User Story 3 - Access Protected Resources (Priority: P1)

An authenticated user accesses their profile information to verify their identity and account status. This validates the token-based authentication flow.

**Why this priority**: Demonstrates that the authentication system works end-to-end. This is the validation proof that tokens are being correctly issued and validated.

**Independent Test**: Can be fully tested by making a request to /auth/me with a valid access token and verifying the current user's information is returned.

**Acceptance Scenarios**:

1. **Given** a user with a valid access token, **When** the user requests GET /api/v1/auth/me, **Then** the system returns HTTP 200 OK with the user object containing id, email, name, and created_at.

2. **Given** a user with an expired access token, **When** the user requests GET /api/v1/auth/me, **Then** the system returns HTTP 401 Unauthorized with error code "TOKEN_EXPIRED" and message "Access token has expired".

3. **Given** a request with no Authorization header, **When** GET /api/v1/auth/me is called, **Then** the system returns HTTP 401 Unauthorized with error code "MISSING_TOKEN" and message "Authentication required".

4. **Given** a request with a malformed or invalid token, **When** GET /api/v1/auth/me is called, **Then** the system returns HTTP 401 Unauthorized with error code "INVALID_TOKEN" and message "Invalid authentication token".

---

### User Story 4 - Token Refresh (Priority: P1)

An authenticated user's access token expires during their session. The system seamlessly issues a new access token using their refresh token, maintaining their authenticated state without requiring re-login.

**Why this priority**: Essential for user experience. Without refresh capability, users would be forced to re-login every 15 minutes, making the application impractical.

**Independent Test**: Can be fully tested by calling the refresh endpoint with a valid refresh token cookie and verifying a new access token is returned.

**Acceptance Scenarios**:

1. **Given** a user with a valid refresh token in their cookie, **When** the user calls POST /api/v1/auth/refresh, **Then** the system returns HTTP 200 OK with a new access_token and token_type "bearer".

2. **Given** a user with an expired refresh token (older than 7 days), **When** the user calls POST /api/v1/auth/refresh, **Then** the system returns HTTP 401 Unauthorized with error code "REFRESH_TOKEN_EXPIRED" and message "Refresh token has expired. Please log in again".

3. **Given** a request with no refresh token cookie, **When** POST /api/v1/auth/refresh is called, **Then** the system returns HTTP 401 Unauthorized with error code "MISSING_REFRESH_TOKEN" and message "Refresh token not found".

---

### User Story 5 - User Logout (Priority: P2)

An authenticated user logs out of the application. The system clears their refresh token cookie, preventing further token refresh operations.

**Why this priority**: Important for security but not blocking for core functionality. Users can close their browser; explicit logout is a security enhancement.

**Independent Test**: Can be fully tested by calling logout and verifying the refresh token cookie is cleared.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a refresh token cookie, **When** the user calls POST /api/v1/auth/logout, **Then** the system returns HTTP 200 OK with message "Successfully logged out" and clears the refresh_token cookie.

2. **Given** a user without a refresh token cookie, **When** POST /api/v1/auth/logout is called, **Then** the system returns HTTP 200 OK with message "Successfully logged out" (idempotent behavior).

---

### User Story 6 - Database Initialization (Priority: P1)

A developer or deployment system initializes a new database with all required tables, constraints, and indexes to support the application's data model.

**Why this priority**: Without the database schema, no data can be persisted. This is a hard prerequisite for all other functionality.

**Independent Test**: Can be fully tested by running migrations against an empty database and verifying all tables, constraints, and indexes are created correctly.

**Acceptance Scenarios**:

1. **Given** an empty PostgreSQL database, **When** Alembic migrations are executed, **Then** the database contains tables for User, Tag, Task, and TaskTagLink with all specified columns, types, and constraints.

2. **Given** a database with migrations applied, **When** Alembic downgrade is executed, **Then** the database schema changes are reversed in order.

---

### Edge Cases

- **Empty State - No Users**: System correctly handles requests when no users exist in the database. Login attempts return appropriate errors without exposing whether email exists.

- **Invalid Input - Malformed Email**: Registration with an invalid email format (e.g., "notanemail") returns HTTP 400 with error code "INVALID_EMAIL" and message "Please provide a valid email address".

- **Invalid Input - SQL Injection Attempt**: Input containing SQL injection attempts (e.g., "'; DROP TABLE users;--") is safely parameterized by SQLModel and causes no data corruption.

- **State Conflict - Concurrent Registration**: Two simultaneous registration attempts with the same email address result in one success and one failure with "EMAIL_ALREADY_EXISTS" due to unique constraint.

- **Token Type Mismatch**: Attempting to use a refresh token as an access token returns HTTP 401 with error code "INVALID_TOKEN_TYPE" and message "Invalid token type for this operation".

- **Rate Limiting Exceeded**: More than 5 authentication attempts per minute from the same IP returns HTTP 429 Too Many Requests with error code "RATE_LIMIT_EXCEEDED" and message "Too many authentication attempts. Please try again later".

---

## 3. Database Schema Requirements

### 3.1 Technology Mandate

The implementation **MUST** use SQLModel as the ORM layer, combining SQLAlchemy and Pydantic for type-safe data access and validation. All database operations **MUST** use the asyncpg driver for non-blocking I/O.

### 3.2 Entity Definitions

#### 3.2.1 User Entity

| Field      | Type     | Constraints                      | Description                    |
| ---------- | -------- | -------------------------------- | ------------------------------ |
| id         | str      | PRIMARY KEY                      | User ID (UUID format)          |
| email      | str      | UNIQUE, NOT NULL                 | User's email address           |
| password_hash | str   | NOT NULL                         | Bcrypt-hashed password         |
| name       | str      | NULLABLE                         | User's display name            |
| created_at | datetime | NOT NULL, DEFAULT now()          | Account creation timestamp     |

**Notes**:
- The `password_hash` field stores the bcrypt hash, never the plaintext password
- The `id` field uses string type to accommodate UUID format from Better Auth integration

#### 3.2.2 Tag Entity

| Field    | Type | Constraints                          | Description               |
| -------- | ---- | ------------------------------------ | ------------------------- |
| id       | int  | PRIMARY KEY, AUTOINCREMENT           | Unique tag identifier     |
| name     | str  | NOT NULL, max 50 chars               | Tag display name          |
| color    | str  | NULLABLE, hex format                 | Tag color for UI display  |
| user_id  | str  | FOREIGN KEY -> User.id, NOT NULL     | Owner of the tag          |

**Constraint**: UNIQUE(name, user_id) - No duplicate tag names per user

#### 3.2.3 Task Entity

| Field           | Type       | Constraints                          | Description                   |
| --------------- | ---------- | ------------------------------------ | ----------------------------- |
| id              | int        | PRIMARY KEY, AUTOINCREMENT           | Unique task identifier        |
| title           | str        | NOT NULL, 1-200 chars                | Task title                    |
| description     | str        | NULLABLE, max 1000 chars             | Detailed description          |
| completed       | bool       | NOT NULL, DEFAULT False              | Completion status             |
| priority        | str        | NOT NULL, DEFAULT 'medium'           | Enum: 'low', 'medium', 'high' |
| due_date        | datetime   | NULLABLE                             | Task due date and time        |
| recurrence_rule | str        | NULLABLE                             | iCal RRULE string             |
| user_id         | str        | FOREIGN KEY -> User.id, NOT NULL     | Task owner                    |
| created_at      | datetime   | NOT NULL, DEFAULT now()              | Creation timestamp            |
| updated_at      | datetime   | NOT NULL, DEFAULT now(), ON UPDATE   | Last modification timestamp   |

#### 3.2.4 TaskTagLink Entity (Junction Table)

| Field   | Type | Constraints                          | Description       |
| ------- | ---- | ------------------------------------ | ----------------- |
| task_id | int  | FOREIGN KEY -> Task.id, PRIMARY KEY  | Task reference    |
| tag_id  | int  | FOREIGN KEY -> Tag.id, PRIMARY KEY   | Tag reference     |

**Constraint**: Composite PRIMARY KEY(task_id, tag_id)

### 3.3 Relationships

- **User to Tasks**: One-to-Many. A user can own multiple tasks; each task belongs to exactly one user.
- **User to Tags**: One-to-Many. A user can own multiple tags; each tag belongs to exactly one user.
- **Task to Tags**: Many-to-Many via TaskTagLink. A task can have multiple tags; a tag can be applied to multiple tasks.

### 3.4 Database Indexes

The following indexes **MUST** be created for query optimization:

| Index Name                  | Table          | Column(s)            | Purpose                    |
| --------------------------- | -------------- | -------------------- | -------------------------- |
| idx_tasks_user_id           | tasks          | user_id              | User task lookup           |
| idx_tasks_user_completed    | tasks          | user_id, completed   | Filtered task lists        |
| idx_tasks_user_priority     | tasks          | user_id, priority    | Priority sorting           |
| idx_tasks_user_due_date     | tasks          | user_id, due_date    | Due date sorting           |
| idx_tags_user_id            | tags           | user_id              | User tag lookup            |
| idx_task_tag_link_task      | task_tag_link  | task_id              | Tag lookup by task         |
| idx_task_tag_link_tag       | task_tag_link  | tag_id               | Task lookup by tag         |

### 3.5 Migration Requirements

- All schema changes **MUST** be managed via Alembic migrations
- Each migration **MUST** be reversible (include upgrade AND downgrade)
- Migration naming convention: `YYYYMMDD_HHMMSS_descriptive_name.py`
- Migrations **MUST** be executed manually by developers/operators via CLI commands (`alembic upgrade head`) before deployment
- The application **SHOULD** verify database schema version at startup and log a warning if migrations are pending (but not auto-execute them)

---

## 4. API Endpoint Requirements: Authentication

### 4.1 Base Configuration

- **API Version Prefix**: All endpoints prefixed with `/api/v1/`
- **Content Type**: `application/json` for request and response bodies
- **Error Format**: Consistent JSON error responses per constitution Section V

### 4.2 Endpoint Definitions

#### 4.2.1 User Registration

| Attribute         | Value                                    |
| ----------------- | ---------------------------------------- |
| **Method**        | POST                                     |
| **Path**          | /api/v1/auth/register                    |
| **Authentication**| None (public endpoint)                   |
| **Rate Limit**    | 5 requests per minute per IP             |

**Request Body**:
```json
{
  "email": "string (required, valid email format)",
  "password": "string (required, minimum 8 characters)",
  "name": "string (optional)"
}
```

**Success Response (201 Created)**:
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-12-09T10:30:00Z"
}
```

**Error Responses**:

| Status Code | Error Code           | Message                                        | Condition                        |
| ----------- | -------------------- | ---------------------------------------------- | -------------------------------- |
| 400         | EMAIL_ALREADY_EXISTS | A user with this email already exists          | Email already registered         |
| 400         | PASSWORD_TOO_SHORT   | Password must be at least 8 characters         | Password < 8 characters          |
| 400         | INVALID_EMAIL        | Please provide a valid email address           | Invalid email format             |
| 422         | VALIDATION_ERROR     | {field-specific validation message}            | Pydantic validation failure      |
| 429         | RATE_LIMIT_EXCEEDED  | Too many authentication attempts. Please try again later | Rate limit exceeded |

#### 4.2.2 User Login

| Attribute         | Value                                    |
| ----------------- | ---------------------------------------- |
| **Method**        | POST                                     |
| **Path**          | /api/v1/auth/login                       |
| **Authentication**| None (public endpoint)                   |
| **Rate Limit**    | 5 requests per minute per IP             |

**Request Body** (OAuth2PasswordRequestForm format):
```
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=SecurePass123!
```

**Success Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Cookie Set**:
```
Set-Cookie: refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...; HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth; Max-Age=604800
```

**Error Responses**:

| Status Code | Error Code          | Message                          | Condition                        |
| ----------- | ------------------- | -------------------------------- | -------------------------------- |
| 401         | INVALID_CREDENTIALS | Invalid email or password        | Wrong email or password          |
| 422         | VALIDATION_ERROR    | {field-specific message}         | Missing required fields          |
| 429         | RATE_LIMIT_EXCEEDED | Too many authentication attempts. Please try again later | Rate limit exceeded |

#### 4.2.3 Token Refresh

| Attribute         | Value                                    |
| ----------------- | ---------------------------------------- |
| **Method**        | POST                                     |
| **Path**          | /api/v1/auth/refresh                     |
| **Authentication**| Refresh token via HttpOnly cookie        |
| **Rate Limit**    | 10 requests per minute per IP            |

**Request**: No body required. The refresh_token is read from the HttpOnly cookie.

**Success Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses**:

| Status Code | Error Code             | Message                                       | Condition                    |
| ----------- | ---------------------- | --------------------------------------------- | ---------------------------- |
| 401         | MISSING_REFRESH_TOKEN  | Refresh token not found                       | No cookie present            |
| 401         | REFRESH_TOKEN_EXPIRED  | Refresh token has expired. Please log in again | Token expired (> 7 days)    |
| 401         | INVALID_TOKEN          | Invalid authentication token                  | Malformed or tampered token  |

#### 4.2.4 Get Current User

| Attribute         | Value                                    |
| ----------------- | ---------------------------------------- |
| **Method**        | GET                                      |
| **Path**          | /api/v1/auth/me                          |
| **Authentication**| Bearer token in Authorization header     |
| **Rate Limit**    | Standard API rate limits                 |

**Request Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK)**:
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-12-09T10:30:00Z"
}
```

**Error Responses**:

| Status Code | Error Code     | Message                         | Condition                    |
| ----------- | -------------- | ------------------------------- | ---------------------------- |
| 401         | MISSING_TOKEN  | Authentication required         | No Authorization header      |
| 401         | TOKEN_EXPIRED  | Access token has expired        | Token expired (> 15 min)     |
| 401         | INVALID_TOKEN  | Invalid authentication token    | Malformed or tampered token  |

#### 4.2.5 User Logout

| Attribute         | Value                                    |
| ----------------- | ---------------------------------------- |
| **Method**        | POST                                     |
| **Path**          | /api/v1/auth/logout                      |
| **Authentication**| None required (idempotent)               |
| **Rate Limit**    | Standard API rate limits                 |

**Request**: No body required.

**Success Response (200 OK)**:
```json
{
  "message": "Successfully logged out"
}
```

**Cookie Cleared**:
```
Set-Cookie: refresh_token=; HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth; Max-Age=0
```

---

## 5. Non-Functional & Security Requirements

### 5.1 Password Security

- Passwords **MUST** be hashed using `passlib[bcrypt]`
- Plaintext passwords **MUST NEVER** be stored in the database
- Plaintext passwords **MUST NEVER** appear in logs
- Minimum password length: 8 characters

### 5.2 JWT Token Specification

Per constitution Section IV, tokens **MUST** follow this structure:

**JWT Payload Structure**:
```json
{
  "sub": "<user_id>",
  "email": "<user_email>",
  "exp": "<expiration_timestamp>",
  "iat": "<issued_at_timestamp>",
  "type": "access|refresh"
}
```

**Token Expiration**:
- Access Token: 15 minutes (900 seconds)
- Refresh Token: 7 days (604800 seconds)

**Algorithm**: HS256 (HMAC-SHA256) for Phase II. RS256 preferred for production (future enhancement).

**Secret Key Requirements**:
- **Storage**: Environment variable `JWT_SECRET_KEY`
- **Minimum Length**: 256 bits (32 bytes when hex-encoded = 64 characters)
- **Generation Method**: MUST be generated using a cryptographically secure random generator (e.g., `openssl rand -hex 32`, `python -c "import secrets; print(secrets.token_hex(32))"`)
- **Validation**: Application MUST validate secret key length at startup and refuse to start if the key is shorter than 64 hex characters
- **Documentation**: Setup instructions MUST include the command for generating a secure secret

### 5.3 Token Storage

- **Access Tokens**: Returned in response body; frontend stores in memory only (NOT localStorage)
- **Refresh Tokens**: Set via HttpOnly, Secure, SameSite=Strict cookie

### 5.4 Rate Limiting

- Authentication endpoints (login, register, refresh): 5 attempts per minute per IP
- Rate limit exceeded returns HTTP 429 with error code "RATE_LIMIT_EXCEEDED"

### 5.5 CORS Policy

**Development Environment**:
- Backend runs on: `http://localhost:8000` (FastAPI with Uvicorn)
- Allowed CORS origins (configurable via `CORS_ORIGINS` environment variable):
  - `http://localhost:3000` (React/Next.js default)
  - `http://localhost:5173` (Vite default)
  - `http://localhost:8080` (Vue CLI default)
  - `http://localhost:8000` (same-origin for API testing tools)
- Allow credentials: True (required for HttpOnly cookies)
- Allowed methods: GET, POST, PUT, DELETE, OPTIONS
- Allowed headers: Content-Type, Authorization

**Production Environment**:
- Restrict to deployed frontend domain only (configured via `CORS_ORIGINS` environment variable)
- MUST NOT use wildcard (*) in production

### 5.6 Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLModel
- **JWT Library**: `python-jose` or `PyJWT`
- **Password Hashing**: `passlib[bcrypt]`
- **Database Driver**: asyncpg
- **Migrations**: Alembic

### 5.7 Database Connection Configuration

The database connection pool **MUST** be configured with the following settings appropriate for development and testing environments:

- **Minimum Pool Size**: 2 connections
- **Maximum Pool Size**: 5 connections
- **Pool Recycle Time**: 3600 seconds (1 hour)
- **Connection Timeout**: 30 seconds

These settings **MUST** be configurable via environment variables:
- `DB_POOL_MIN` (default: 2)
- `DB_POOL_MAX` (default: 5)
- `DB_POOL_RECYCLE` (default: 3600)
- `DB_CONNECTION_TIMEOUT` (default: 30)

### 5.8 Phase II Scope Boundaries

The following security features are explicitly **OUT OF SCOPE** for Phase II:
- Refresh token rotation on each use
- Server-side token blacklisting for logout
- Password reset functionality
- Email verification
- Multi-factor authentication

---

## 6. Requirements Summary

### Functional Requirements

- **FR-001**: System MUST allow new users to create accounts with email, password, and optional name.
- **FR-002**: System MUST validate email format and reject invalid addresses with error code "INVALID_EMAIL".
- **FR-003**: System MUST validate password length (minimum 8 characters) and reject short passwords with error code "PASSWORD_TOO_SHORT".
- **FR-004**: System MUST prevent duplicate email registration with error code "EMAIL_ALREADY_EXISTS".
- **FR-005**: System MUST hash all passwords using bcrypt before storage.
- **FR-006**: System MUST authenticate users via email/password and issue JWT tokens upon successful login.
- **FR-007**: System MUST return access token in response body and set refresh token in HttpOnly cookie upon login.
- **FR-008**: System MUST validate access tokens on all protected endpoints and return user context.
- **FR-009**: System MUST issue new access tokens via refresh endpoint using valid refresh token from cookie.
- **FR-010**: System MUST clear refresh token cookie upon logout.
- **FR-011**: System MUST reject expired tokens with appropriate error codes ("TOKEN_EXPIRED" or "REFRESH_TOKEN_EXPIRED").
- **FR-012**: System MUST reject invalid or malformed tokens with error code "INVALID_TOKEN".
- **FR-013**: System MUST reject requests to protected endpoints without tokens with error code "MISSING_TOKEN".
- **FR-014**: System MUST create database schema via Alembic migrations with all specified entities, constraints, and indexes.
- **FR-015**: System MUST support migration rollback (downgrade) for all schema changes.
- **FR-016**: System MUST rate limit authentication endpoints to 5 requests per minute per IP.

### Key Entities

- **User**: Represents a registered application user. Key attributes: unique email, hashed password, optional display name, creation timestamp. Owns tasks and tags.
- **Task**: Represents a todo item. Key attributes: title (required), description, completion status, priority level, optional due date, optional recurrence rule. Belongs to exactly one user.
- **Tag**: Represents a category label for tasks. Key attributes: name (unique per user), optional color. Belongs to exactly one user.
- **TaskTagLink**: Junction entity enabling many-to-many relationship between tasks and tags.

---

## 7. Success Criteria

### Measurable Outcomes

- **SC-001**: A new, empty PostgreSQL database can be fully initialized by running `alembic upgrade head`, resulting in all four tables (users, tasks, tags, task_tag_link) with correct columns, constraints, and indexes.
- **SC-002**: A user can successfully complete the registration flow in under 5 seconds, receiving HTTP 201 with their user object (excluding password).
- **SC-003**: A registered user can successfully complete the login flow in under 3 seconds, receiving an access token and refresh token cookie.
- **SC-004**: A user with a valid access token can access GET /api/v1/auth/me and receive their user profile within 200ms (p95).
- **SC-005**: An attempt to access a protected endpoint with an expired access token results in HTTP 401 with error code "TOKEN_EXPIRED" within 100ms.
- **SC-006**: An attempt to access a protected endpoint with an invalid token results in HTTP 401 with error code "INVALID_TOKEN" within 100ms.
- **SC-007**: A user with a valid refresh token can obtain a new access token via /api/v1/auth/refresh within 200ms.
- **SC-008**: After logout, the refresh token cookie is cleared (Max-Age=0) and subsequent refresh attempts fail with "MISSING_REFRESH_TOKEN".
- **SC-009**: All API error responses match the format: `{"detail": "message", "code": "ERROR_CODE"}`.
- **SC-010**: 100% of authentication tests pass in the CI pipeline before merge.
- **SC-011**: Backend test coverage for authentication module is >= 80%.

---

## 8. Assumptions

The following assumptions have been applied based on the constitution and industry standards:

1. **User ID Format**: User IDs are UUID strings to accommodate Better Auth integration (Constitution Section IV).

2. **Password Minimum Length**: 8 characters is the minimum acceptable password length (industry standard NIST guidelines).

3. **Rate Limiting Scope**: Rate limiting is per-IP for authentication endpoints. More sophisticated rate limiting (per-user, distributed) is deferred to future phases.

4. **Same Error Message for Invalid Credentials**: Both "wrong password" and "user not found" return the same "Invalid email or password" message to prevent user enumeration attacks.

5. **Logout is Idempotent**: Calling logout without an existing session still returns 200 OK to provide consistent client behavior.

6. **Refresh Token Cookie Path**: Cookie path is restricted to `/api/v1/auth` to prevent sending the token to other API endpoints unnecessarily.

7. **Algorithm Selection**: HS256 is acceptable for Phase II with the understanding that RS256 is preferred for production environments with multiple services.

---

## 9. Out of Scope

The following items are explicitly excluded from this specification:

1. **Refresh Token Rotation**: Rotating refresh tokens on each use (targeted for Phase III per constitution).
2. **Token Blacklisting**: Server-side token revocation mechanism (targeted for Phase III per constitution).
3. **Password Reset**: Email-based password reset functionality.
4. **Email Verification**: Confirming user email ownership.
5. **Multi-Factor Authentication**: 2FA/MFA support.
6. **Social Login**: OAuth integration with Google, GitHub, etc.
7. **Account Deletion**: User self-service account deletion.
8. **Admin Endpoints**: Administrative user management endpoints.
9. **Frontend Implementation**: This specification covers backend only; frontend integration is a separate feature.

---

## 10. Testing Acceptance Criteria

### 10.0 Test Environment Configuration

**Test Database Setup**:
- **Database Name**: `todo_test` (separate from development database `todo_dev`)
- **Isolation Strategy**: Each test run operates on a clean database state
- **Setup Process**:
  - Before test suite: Create test database if it doesn't exist, run migrations (`alembic upgrade head`)
  - Before each test: Begin a transaction or truncate all tables to ensure clean state
  - After each test: Rollback transaction or clean up test data
  - After test suite: Optionally drop test database (or leave for debugging)
- **Configuration**: Test database connection string provided via `TEST_DATABASE_URL` environment variable or derived from `DATABASE_URL` with `_test` suffix
- **Fixtures**: Provide reusable test fixtures for common entities (test users, test tasks) via pytest fixtures or similar framework

**Test Execution Requirements**:
- Tests MUST be runnable via a single command (e.g., `pytest` or `python -m pytest`)
- Tests MUST be idempotent and not depend on execution order
- Tests MUST clean up after themselves to allow repeated execution
- Tests MUST NOT affect the development or production databases

### 10.1 Database Schema Tests

| Test ID | Description                                              | Expected Result                              |
| ------- | -------------------------------------------------------- | -------------------------------------------- |
| DB-001  | Run migrations on empty database                         | All tables created with correct schema       |
| DB-002  | Verify User table constraints                            | UNIQUE on email enforced                     |
| DB-003  | Verify Tag table constraints                             | UNIQUE(name, user_id) enforced               |
| DB-004  | Verify Task table constraints                            | Foreign key to User enforced                 |
| DB-005  | Verify TaskTagLink constraints                           | Composite primary key enforced               |
| DB-006  | Verify all indexes exist                                 | 7 indexes created as specified               |
| DB-007  | Run migration downgrade                                  | Schema changes reversed                      |

### 10.2 Registration Tests

| Test ID  | Description                                              | Expected Result                              |
| -------- | -------------------------------------------------------- | -------------------------------------------- |
| REG-001  | Register with valid email, password, name                | 201 Created, user object returned            |
| REG-002  | Register with valid email, password, no name             | 201 Created, name is null                    |
| REG-003  | Register with existing email                             | 400, EMAIL_ALREADY_EXISTS                    |
| REG-004  | Register with password < 8 characters                    | 400, PASSWORD_TOO_SHORT                      |
| REG-005  | Register with invalid email format                       | 400, INVALID_EMAIL                           |
| REG-006  | Register with missing email                              | 422, VALIDATION_ERROR                        |
| REG-007  | Register with missing password                           | 422, VALIDATION_ERROR                        |
| REG-008  | Verify password is hashed in database                    | password_hash != original password           |

### 10.3 Login Tests

| Test ID  | Description                                              | Expected Result                              |
| -------- | -------------------------------------------------------- | -------------------------------------------- |
| LOG-001  | Login with valid credentials                             | 200, access_token returned, cookie set       |
| LOG-002  | Login with wrong password                                | 401, INVALID_CREDENTIALS                     |
| LOG-003  | Login with non-existent email                            | 401, INVALID_CREDENTIALS                     |
| LOG-004  | Login with missing username                              | 422, VALIDATION_ERROR                        |
| LOG-005  | Login with missing password                              | 422, VALIDATION_ERROR                        |
| LOG-006  | Verify refresh token cookie attributes                   | HttpOnly, Secure, SameSite=Strict            |

### 10.4 Token Validation Tests

| Test ID  | Description                                              | Expected Result                              |
| -------- | -------------------------------------------------------- | -------------------------------------------- |
| TOK-001  | Access /auth/me with valid token                         | 200, user object returned                    |
| TOK-002  | Access /auth/me with expired token                       | 401, TOKEN_EXPIRED                           |
| TOK-003  | Access /auth/me with malformed token                     | 401, INVALID_TOKEN                           |
| TOK-004  | Access /auth/me without Authorization header             | 401, MISSING_TOKEN                           |
| TOK-005  | Access /auth/me with refresh token (wrong type)          | 401, INVALID_TOKEN_TYPE                      |
| TOK-006  | Verify token contains correct claims (sub, email, exp, iat, type) | All claims present and valid      |

### 10.5 Token Refresh Tests

| Test ID  | Description                                              | Expected Result                              |
| -------- | -------------------------------------------------------- | -------------------------------------------- |
| REF-001  | Refresh with valid refresh token                         | 200, new access_token returned               |
| REF-002  | Refresh with expired refresh token                       | 401, REFRESH_TOKEN_EXPIRED                   |
| REF-003  | Refresh without cookie                                   | 401, MISSING_REFRESH_TOKEN                   |
| REF-004  | Refresh with invalid token                               | 401, INVALID_TOKEN                           |
| REF-005  | Verify new access token is valid                         | Can use new token for /auth/me               |

### 10.6 Logout Tests

| Test ID  | Description                                              | Expected Result                              |
| -------- | -------------------------------------------------------- | -------------------------------------------- |
| OUT-001  | Logout with existing session                             | 200, cookie cleared                          |
| OUT-002  | Logout without existing session                          | 200, idempotent behavior                     |
| OUT-003  | Refresh after logout                                     | 401, MISSING_REFRESH_TOKEN                   |

### 10.7 Rate Limiting Tests

| Test ID  | Description                                              | Expected Result                              |
| -------- | -------------------------------------------------------- | -------------------------------------------- |
| RTE-001  | 5 login attempts within 1 minute                         | All succeed                                  |
| RTE-002  | 6th login attempt within 1 minute                        | 429, RATE_LIMIT_EXCEEDED                     |
| RTE-003  | Login attempt after rate limit window expires            | Request succeeds                             |

---

## 11. Glossary

| Term           | Definition                                                                 |
| -------------- | -------------------------------------------------------------------------- |
| Access Token   | Short-lived JWT (15 min) used to authenticate API requests                 |
| Refresh Token  | Long-lived JWT (7 days) used to obtain new access tokens                   |
| JWT            | JSON Web Token - a compact, URL-safe means of representing claims          |
| HttpOnly       | Cookie attribute preventing JavaScript access (XSS protection)             |
| Secure         | Cookie attribute requiring HTTPS transmission                              |
| SameSite       | Cookie attribute controlling cross-site request behavior (CSRF protection) |
| Bcrypt         | Password hashing algorithm with built-in salt                              |
| SQLModel       | Python library combining SQLAlchemy ORM with Pydantic validation           |
| Alembic        | Database migration tool for SQLAlchemy                                     |
| Rate Limiting  | Restricting the number of requests from a source within a time window      |

---

## 12. References

- Constitution: `.specify/memory/constitution.md` (Version 2.2.0)
- Section II: Full-Stack Monorepo Architecture
- Section III: Persistent & Relational State
- Section IV: User Authentication & JWT Security
- Section V: Backend Architecture Standards
- Data Model Specification (Constitution)
- Validation Rules (Constitution)
- API Design Standards (Constitution)

---

**Specification Status**: Complete
**Clarifications Required**: 0
**Validation Iterations**: 1
**Next Step**: Proceed to `/sp.plan` for implementation planning
