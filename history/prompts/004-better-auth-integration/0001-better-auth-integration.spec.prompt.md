---
id: 5
title: better-auth-integration
stage: spec
date: 2025-12-10
surface: agent
model: claude-3-5-sonnet-20250401
feature: better-auth-integration
branch: 004-better-auth-integration
user: salim
command: /sp.specify
labels: [authentication, security, api, user-management]
links:
  spec: /specs/004-better-auth-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - /home/salim/Desktop/hackathon-II-todo-app/specs/004-better-auth-integration/spec.md
 - /home/salim/Desktop/hackathon-II-todo-app/specs/004-better-auth-integration/checklists/requirements.md
tests:
 - null
---

## Prompt

```
Better Auth Integration Specification

## Table of Contents
1. [Overview](#overview)
2. [User Stories](#user-stories)
3. [Acceptance Criteria](#acceptance-criteria)
4. [Technical Requirements](#technical-requirements)
5. [API Specifications](#api-specifications)
6. [Security Requirements](#security-requirements)
7. [Data Model Changes](#data-model-changes)
8. [Implementation Constraints](#implementation-constraints)
9. [Testing Requirements](#testing-requirements)
10. [Performance Requirements](#performance-requirements)

## Overview

### Purpose
This specification documents the integration of Better Auth into the Todo App Phase II, replacing the current custom authentication system with a standardized authentication solution that provides JWT-based security between the Next.js frontend and FastAPI backend.

### Scope
- Replace current custom JWT authentication with Better Auth integration
- Update API endpoints to follow `{user_id}/resources` pattern
- Implement proper user data isolation and security validation
- Create shared auth-sdk package for frontend and backend integration

### Out of Scope
- Team/collaboration features
- OAuth provider integration (beyond Better Auth default providers)
- Mobile native applications

## User Stories

### Story 1: User Registration with Better Auth
**As a** new user
**I want** to register using Better Auth
**So that** I can create a secure account with standard authentication

**Acceptance Criteria:**
- User can register with email and password via Better Auth
- Registration creates a user in the system with a UUID from Better Auth
- User receives proper feedback for successful/failed registration
- Error handling for duplicate emails and validation errors

### Story 2: User Login with Better Auth
**As an** existing user
**I want** to login using Better Auth
**So that** I can access my todo lists with proper authentication

**Acceptance Criteria:**
- User can login with email and password via Better Auth
- Login provides JWT token for API access
- Session is properly maintained after login
- Error handling for invalid credentials

### Story 3: API Security with Better Auth Tokens
**As a** authenticated user
**I want** my API calls to be secured with Better Auth tokens
**So that** my data remains private and secure

**Acceptance Criteria:**
- All API requests include Authorization: Bearer <token> header
- Backend validates Better Auth JWT tokens using shared secret
- Unauthorized requests return 401 status
- Token expiration is properly handled

### Story 4: User Data Isolation
**As a** authenticated user
**I want** to only see my own tasks and tags
**So that** my data remains private from other users

**Acceptance Criteria:**
- All GET requests return only user's own data
- All POST/PUT/DELETE operations affect only user's own data
- Attempts to access other users' data return 403 Forbidden
- User ID path parameter validation prevents URL manipulation

### Story 5: Frontend-Backend Token Integration
**As a** system architect
**I want** seamless token flow between Better Auth and backend
**So that** the authentication system is cohesive and secure

**Acceptance Criteria:**
- Frontend intercepts Better Auth tokens and includes them in API requests
- Backend validates tokens with same secret as frontend
- Token refresh is handled automatically
- User experience is seamless across authentication boundaries

## Acceptance Criteria

### Functional Acceptance Criteria
- [ ] Users can register/login/logout using Better Auth
- [ ] All API endpoints require valid Better Auth JWT token
- [ ] User ID path parameter matches JWT user ID for all user-specific endpoints
- [ ] Users can only access their own tasks and tags
- [ ] API endpoints have been migrated to `{user_id}/resources` pattern
- [ ] Frontend automatically includes Better Auth tokens in all API requests
- [ ] Token refresh works seamlessly without user intervention
- [ ] All existing task and tag functionality works with new authentication

### Security Acceptance Criteria
- [ ] Better Auth JWT tokens are properly validated by backend
- [ ] Path parameter validation prevents cross-user data access
- [ ] 403 Forbidden returned when path user_id != JWT user_id
- [ ] Tokens are stored securely (preferably in memory, not localStorage)
- [ ] Expired tokens trigger proper refresh flow

### Performance Acceptance Criteria
- [ ] API response times remain under 200ms (p95) for authenticated requests
- [ ] Token validation adds minimal latency to API calls
- [ ] Frontend authentication flow doesn't impact user experience

## Technical Requirements

### Frontend Requirements
- **Framework**: Next.js 16 with App Router
- **Better Auth**: Version 1.0.0+ with JWT plugin enabled
- **API Client**: Axios with request/response interceptors
- **Token Management**: Better Auth managed tokens, attached via interceptors
- **User Context**: Updated useAuth hook to use Better Auth session

### Backend Requirements
- **Framework**: FastAPI with Python 3.11+
- **Token Validation**: JWT verification using shared secret with Better Auth
- **Dependency**: Updated get_current_user to validate Better Auth tokens
- **Path Validation**: User ID path parameter matching with JWT validation
- **Data Filtering**: All queries scoped to JWT user_id, not path parameter

### Shared Requirements
- **Auth SDK**: Shared package `@todo-app/auth-sdk` with frontend and backend modules
- **Environment**: Same BETTER_AUTH_SECRET in both frontend and backend
- **Token Format**: Compatible JWT structure between Better Auth and backend validation

## API Specifications

### Updated API Endpoint Structure
```
Authentication Endpoints (remain unchanged):
POST /api/v1/auth/register - User registration
POST /api/v1/auth/login - User login
POST /api/v1/auth/refresh - Token refresh
POST /api/v1/auth/logout - User logout
GET /api/v1/auth/me - Get current user

User-Specific Endpoints (updated):
GET /api/{user_id}/tasks - Get user's tasks
POST /api/{user_id}/tasks - Create user's task
GET /api/{user_id}/tasks/{id} - Get specific task
PUT /api/{user_id}/tasks/{id} - Update task
PATCH /api/{user_id}/tasks/{id} - Partial update task
DELETE /api/{user_id}/tasks/{id} - Delete task
POST /api/{user_id}/tasks/{task_id}/tags/{tag_id} - Associate tag with task
DELETE /api/{user_id}/tasks/{task_id}/tags/{tag_id} - Remove tag from task
GET /api/{user_id}/tags - Get user's tags
POST /api/{user_id}/tags - Create user's tag
PUT /api/{user_id}/tags/{id} - Update tag
DELETE /api/{user_id}/tags/{id} - Delete tag
```

### Request/Response Format
All requests must include:
```
Authorization: Bearer <better_auth_jwt_token>
Content-Type: application/json
```

### Path Parameter Validation
Every endpoint with `{user_id}` in the path must:
1. Extract user_id from the URL path parameter
2. Extract user_id from the validated JWT token
3. Compare both values - if not equal, return 403 Forbidden
4. Query database using JWT user_id (not path parameter) for data filtering

## Security Requirements

### JWT Token Requirements
- **Algorithm**: HS256 with shared secret
- **Access Token Expiry**: 15 minutes
- **Secret Key**: Minimum 256 bits (BETTER_AUTH_SECRET environment variable)
- **Claims Structure**:
```
{
  "sub": "<user_id_from_better_auth>", // required
  "email": "<user_email>", // required
  "name": "<user_name>", // optional
  "exp": <expiration_timestamp>, // required
  "iat": <issued_at_timestamp>, // required
  "type": "access" // required
}
```

### Authentication Flow Security
- **Frontend**: Better Auth manages tokens via JWT plugin
- **Token Attachment**: Axios interceptor adds Bearer token to all requests
- **Backend Validation**: All endpoints validate JWT with shared secret
- **User ID Validation**: Path parameter must match JWT user ID

### Data Isolation Security
- **Multi-User Isolation**: Users cannot access other users' data
- **Path Parameter Validation**: Prevents URL manipulation attacks
- **Query Scoping**: All database queries filtered by JWT user ID
- **Access Controls**: 403 Forbidden for unauthorized access attempts

## Data Model Changes

### User Model (No Changes Required)
- **id**: str (Primary Key) - UUID from Better Auth
- **email**: str (Unique) - User email address
- **name**: str (Optional) - User display name
- **created_at**: datetime - Account creation timestamp

### Task Model (Add User Relationship)
- **id**: int (Primary Key) - Task ID
- **title**: str - Task title
- **description**: str (Optional) - Task description
- **completed**: bool (Default: False) - Completion status
- **priority**: str (Default: 'medium', Enum: 'low','medium','high') - Priority level
- **due_date**: datetime (Optional) - Due date
- **recurrence_rule**: str (Optional) - RRULE format
- **user_id**: str (Foreign Key) - Links to User.id
- **created_at**: datetime - Creation timestamp
- **updated_at**: datetime - Last update timestamp

### Tag Model (Add User Relationship)
- **id**: int (Primary Key) - Tag ID
- **name**: str - Tag name (max 50 chars)
- **color**: str (Optional) - Tag color (hex format)
- **user_id**: str (Foreign Key) - Links to User.id
- **created_at**: datetime - Creation timestamp

### TaskTagLink Model (No Changes Required)
- **task_id**: int (Foreign Key) - Links to Task.id
- **tag_id**: int (Foreign Key) - Links to Tag.id
- **Composite Primary Key**: (task_id, tag_id)

## Implementation Constraints

### Architecture Constraints
- **Frontend**: Must use Better Auth with JWT plugin for token issuance
- **Backend**: Must validate Better Auth tokens using same shared secret
- **API Structure**: Must use `{user_id}/resources` pattern for all user-specific endpoints
- **Data Filtering**: Must use JWT user_id for database queries, not path parameter
- **Token Storage**: Prefer Better Auth default storage (not localStorage)

### Development Constraints
- **AI Generation**: All code must be AI-generated from specifications
- **Monorepo**: Frontend and backend must work together in single repository
- **Version Compatibility**: Better Auth and FastAPI JWT validation must be compatible
- **Environment Variables**: Same BETTER_AUTH_SECRET across both services

### Security Constraints
- **No Manual Token Creation**: Frontend must use Better Auth tokens only
- **Path Validation**: All user-specific endpoints must validate path vs JWT user ID
- **Data Scoping**: All queries must be scoped to authenticated user
- **Error Handling**: Security errors must not expose internal information

## Testing Requirements

### Unit Tests Required
- **Frontend**: Better Auth integration tests, API client interceptors
- **Backend**: JWT token validation, user ID path parameter validation
- **Auth SDK**: Shared functionality tests for frontend/backend components

### Integration Tests Required
- **Authentication Flow**: Registration, login, logout with Better Auth
- **Token Validation**: JWT validation between frontend and backend
- **Data Isolation**: Multi-user data access prevention
- **Path Validation**: User ID path parameter matching validation

### Security Tests Required
- **Cross-User Access**: Attempt to access other users' data via URL manipulation
- **Invalid Token Handling**: Invalid/expired token validation
- **Token Refresh**: Automatic token refresh functionality
- **Session Management**: Proper session maintenance

### Performance Tests Required
- **API Response Times**: p95 response times under 200ms for authenticated calls
- **Token Validation Latency**: JWT validation overhead measurement
- **Concurrent Users**: Multiple authenticated users performance

## Performance Requirements

### API Response Performance
- **Target**: p95 response time < 200ms for all authenticated endpoints
- **Token Validation**: Overhead < 10ms for JWT validation
- **Database Queries**: Proper indexing for user-specific queries

### User Experience Performance
- **Login Flow**: Authentication flow < 2 seconds
- **API Calls**: No perceptible delay due to token handling
- **Token Refresh**: Seamless refresh without user interruption

### Frontend Performance
- **API Client**: Interceptor overhead < 50ms
- **Token Management**: No performance impact on user interactions
- **Error Handling**: No performance degradation on auth errors

## Dependencies and Integrations

### Frontend Dependencies
- `better-auth`: Main authentication library
- `better-auth-react`: React integration
- `axios`: HTTP client for API calls

### Backend Dependencies
- `jose`: JWT validation
- `fastapi`: Framework
- `python-jose[cryptography]`: JWT support

### Shared Dependencies
- Environment variables: BETTER_AUTH_SECRET

## Deployment Considerations

### Environment Configuration
- **BETTER_AUTH_SECRET**: Same value in both frontend and backend environments
- **CORS Policy**: Allow frontend domain for authentication requests
- **JWT Configuration**: Same algorithm and expiry settings

### Testing Environment
- **Local Development**: Separate Better Auth configuration for local testing
- **Staging**: Staging Better Auth environment with testing users
- **Production**: Production Better Auth environment with proper security
---

```

## Response snapshot

# Feature Specification: Better Auth Integration

**Feature Branch**: `004-better-auth-integration`
**Created**: 2025-12-10
**Status**: Draft
**Input**: User description: "Better Auth Integration Specification"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration with Better Auth (Priority: P1)

User can register using Better Auth to create a secure account with standard authentication.

**Why this priority**: This is the foundational functionality that enables users to join the system.

**Independent Test**: Can be fully tested by registering a new user account and verifying the account is created in the system with proper feedback.

**Acceptance Scenarios**:

1. **Given** a user visits the registration page, **When** they enter valid email and password and submit the form, **Then** their account is created with a UUID from Better Auth and they receive positive feedback.
2. **Given** a user attempts to register with an existing email, **When** they submit the form, **Then** they receive appropriate error feedback about duplicate email.
3. **Given** a user enters invalid email format or weak password, **When** they submit the form, **Then** they receive validation error feedback.

---

### User Story 2 - User Login with Better Auth (Priority: P1)

User can login using Better Auth to access their todo lists with proper authentication.

**Why this priority**: Critical for user access to their data after registration.

**Independent Test**: Can be fully tested by logging in with existing credentials and gaining access to the system.

**Acceptance Scenarios**:

1. **Given** an existing user with valid credentials, **When** they enter correct email and password and submit login form, **Then** they successfully authenticate and receive JWT token for API access.
2. **Given** a user attempts to login with invalid credentials, **When** they submit the form, **Then** they receive appropriate error feedback without revealing whether the email or password was incorrect.
3. **Given** a valid user session, **When** they navigate through the application, **Then** their session is properly maintained throughout their usage.

---

### User Story 3 - API Security with Better Auth Tokens (Priority: P1)

Authenticated user's API calls are secured with Better Auth tokens to keep their data private and secure.

**Why this priority**: Security is fundamental to protecting user data and system integrity.

**Independent Test**: Can be tested by making API calls with/without valid tokens to verify access control.

**Acceptance Scenarios**:

1. **Given** an authenticated user with valid JWT token, **When** their API requests include Authorization: Bearer <token> header, **Then** the requests are processed normally.
2. **Given** a user without valid JWT token, **When** they make API requests without proper authorization, **Then** the API returns 401 status.
3. **Given** an expired JWT token, **When** it's used in API requests, **Then** the system properly handles token expiration and triggers refresh flow.

---

### User Story 4 - User Data Isolation (Priority: P2)

Authenticated user can only see their own tasks and tags to maintain privacy from other users.

**Why this priority**: Critical security requirement that prevents unauthorized data access.

**Independent Test**: Can be tested by attempting to access other users' data with various user accounts.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they request their own tasks and tags via GET requests, **Then** only their own data is returned.
2. **Given** an authenticated user, **When** they perform POST/PUT/DELETE operations on their data, **Then** only their own data is affected.
3. **Given** an authenticated user attempting to access another user's data, **When** they make unauthorized requests, **Then** the system returns 403 Forbidden status.

---

### User Story 5 - Frontend-Backend Token Integration (Priority: P2)

System ensures seamless token flow between Better Auth and backend for cohesive and secure authentication.

**Why this priority**: Ensures authentication system works seamlessly across both frontend and backend components.

**Independent Test**: Can be tested by verifying token flow during API calls and refresh scenarios.

**Acceptance Scenarios**:

1. **Given** a user with valid authentication, **When** frontend makes API calls, **Then** Better Auth tokens are automatically included in all requests via interceptors.
2. **Given** a user with valid session, **When** backend receives API requests, **Then** tokens are validated successfully with the same shared secret.
3. **Given** an expiring token, **When** the refresh process occurs, **Then** token refresh happens seamlessly without user intervention.

---

### Edge Cases

- What happens when the Better Auth service is temporarily unavailable during login?
- How does the system handle token refresh failures?
- What occurs if there's a mismatch between frontend and backend token validation?
- How does the system respond when Better Auth provides an unexpected user ID format?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to register via Better Auth with email and password
- **FR-002**: System MUST create user accounts with UUID from Better Auth
- **FR-003**: System MUST authenticate users via Better Auth login with email and password
- **FR-004**: System MUST provide JWT tokens for authenticated API access
- **FR-005**: System MUST validate Better Auth JWT tokens via shared secret on backend
- **FR-006**: System MUST require Authorization: Bearer <token> header for all protected API endpoints
- **FR-007**: System MUST return 401 status for unauthorized requests without valid tokens
- **FR-008**: System MUST return 403 Forbidden when user attempts to access other users' data
- **FR-009**: System MUST validate that path user_id matches JWT user_id for all user-specific endpoints
- **FR-010**: System MUST automatically handle token refresh when tokens expire
- **FR-011**: System MUST scope all data queries to the authenticated user's JWT user_id
- **FR-012**: System MUST migrate existing API endpoints to follow {user_id}/resources pattern

### Key Entities *(include if feature involves data)*

- **User**: Represents a registered user with authentication credentials from Better Auth, including id (UUID from Better Auth), email (unique), name (optional), and creation timestamp
- **Task**: Represents a user's task that is linked to a specific user via user_id foreign key relationship
- **Tag**: Represents a user's tag that is linked to a specific user via user_id foreign key relationship
- **Session**: Represents an authenticated user session managed by Better Auth with JWT token

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of new user registrations are handled successfully through Better Auth with proper user feedback
- **SC-002**: 95% of login attempts result in successful authentication within 2 seconds
- **SC-003**: 100% of protected API endpoints return 401 for unauthenticated requests and 403 for cross-user data access attempts
- **SC-004**: User data isolation is maintained with 0% instances of unauthorized cross-user data access
- **SC-005**: Token refresh flow works seamlessly without user intervention, maintaining session continuity
- **SC-006**: All API endpoints follow the {user_id}/resources pattern with proper path parameter validation
- **SC-007**: 98% of token validations return within 10ms of processing time
- **SC-008**: 99% of users successfully complete the registration and authentication flow on first attempt

## Outcome

- ✅ Impact: Created comprehensive feature specification for Better Auth integration
- 🧪 Tests: Created specification quality checklist
- 📁 Files: specs/004-better-auth-integration/spec.md and checklists/requirements.md
- 🔁 Next prompts: Ready for planning and task breakdown
- 🧠 Reflection: Specification captures all security requirements and user flows for authentication integration

## Evaluation notes (flywheel)

- Failure modes observed: None significant
- Graders run and results (PASS/FAIL): All validation criteria met
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin planning the Better Auth integration