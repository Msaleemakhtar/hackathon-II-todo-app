# Research: Better Auth Integration

**Feature**: Better Auth Integration
**Date**: 2025-12-10
**Status**: Completed

## Executive Summary

Research confirms that Better Auth integration is feasible with the existing tech stack. Better Auth provides JWT plugin that allows issuing tokens that can be validated by the FastAPI backend using a shared secret. The implementation approach involves updating the API endpoints to follow the `/api/{user_id}/{resources}` pattern and implementing proper user data isolation.

## Key Findings

### 1. Better Auth JWT Plugin Compatibility
- **Decision**: Use Better Auth with JWT plugin
- **Rationale**: Better Auth provides a JWT plugin that issues tokens compatible with FastAPI backend validation
- **Implementation**: The JWT plugin will issue access tokens that include user_id, email, and expiration time

### 2. JWT Token Validation Strategy
- **Decision**: Implement shared secret validation between frontend and backend
- **Rationale**: Both Better Auth frontend and FastAPI backend can use the same BETTER_AUTH_SECRET to sign and verify JWT tokens
- **Implementation**: FastAPI will use python-jose library to validate the JWT tokens

### 3. Path Parameter Validation Requirements
- **Decision**: Implement strict path parameter validation against JWT user_id
- **Rationale**: Ensures users can only access their own data, preventing URL manipulation attacks
- **Implementation**: Every endpoint with `{user_id}` in the path will validate against the JWT user_id before processing

### 4. API Client Implementation
- **Decision**: Create API client at `@/lib/api-client` as required by constitution
- **Rationale**: Centralizes API calls with proper token management and error handling
- **Implementation**: Axios interceptors will attach the Better Auth JWT token to all requests

### 5. Session Management Across Tabs
- **Decision**: Enable session sharing across browser tabs
- **Rationale**: Provides consistent user experience as specified in clarifications
- **Implementation**: Better Auth's default storage mechanism will handle this

## Technical Architecture

### Frontend Implementation
1. Integrate Better Auth with JWT plugin
2. Implement axios interceptors to attach JWT tokens
3. Create API client at `@/lib/api-client` with proper URL construction
4. Extract user_id from Better Auth session for API calls

### Backend Implementation
1. Create JWT validation dependency using python-jose
2. Implement path parameter validation middleware
3. Update all endpoints to follow `/api/{user_id}/{resources}` pattern
4. Ensure all queries are scoped to JWT user_id, not path parameter

## Dependencies and Integrations

### Frontend Dependencies
- `better-auth`: Main authentication library
- `better-auth-react`: React integration for Next.js
- `axios`: HTTP client for API calls

### Backend Dependencies
- `python-jose`: JWT validation library
- `cryptography`: For JWT decryption

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

## API Contract Changes

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

## Security Considerations

1. **JWT Token Validation**: All tokens must be validated using the shared secret
2. **Path Parameter Validation**: Path user_id must match JWT user_id for all user-specific endpoints
3. **Data Isolation**: All queries must be scoped to JWT user_id, not path parameter
4. **Rate Limiting**: Implement rate limiting at 5 attempts per minute per IP on auth endpoints
5. **Token Expiration**: Handle token refresh automatically before expiry

## Testing Strategy

### Unit Tests
- JWT token validation functions
- Path parameter validation logic
- API client utility functions

### Integration Tests
- Authentication flow (registration, login, logout)
- Token refresh functionality
- Data isolation (user A cannot access user B's data)

### Security Tests
- Path parameter validation (ensure user cannot access other users' data)
- JWT token manipulation attempts
- Rate limiting functionality

## Implementation Risks

1. **Token Refresh Complexity**: Need to ensure seamless token refresh without user interruption
2. **Path Validation Logic**: Critical to implement correctly to prevent data access violations
3. **Backend Token Validation**: Must be implemented securely to prevent authentication bypasses

## Success Criteria Validation

All success criteria from the specification can be validated:
- User registration and login functionality
- JWT token validation and refresh
- Data isolation (0% unauthorized access)
- API performance (<200ms response time)
- Token validation performance (<10ms)