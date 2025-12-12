---
id: 4
title: update-better-auth-integration
stage: constitution
date: 2025-12-10
surface: agent
model: claude-3-5-sonnet-20250401
feature: none
branch: main
user: salim
command: /sp.constitution
labels: [constitution, authentication, api-design, security]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - /home/salim/Desktop/hackathon-II-todo-app/.specify/memory/constitution.md
tests:
 - null
---

## Prompt

```
Update Constitution for Better Auth Integration

## Context
I need to update the Todo App Phase II Constitution to properly reflect the Better Auth integration requirements. The current constitution has Better Auth mentioned but doesn't fully align with the specific implementation approach where Better Auth handles authentication and issues JWTs that are validated by the FastAPI backend.

## Current State Analysis
- Backend currently uses `/api/v1/tasks` and `/api/v1/tags` patterns
- Frontend expects API client at `@/lib/api-client` but this file doesn't exist
- Constitution mentions Better Auth but not the specific JWT plugin integration approach
- Missing the `{user_id}/resources` API pattern requirement from specifications
- Missing user ID path parameter validation requirements

## Required Constitution Updates

### 1. Update Section IV (User Authentication & JWT Security)
- Clarify that Better Auth handles authentication on frontend with JWT plugin
- Better Auth issues tokens validated by FastAPI backend with shared secret
- Add requirement for path parameter validation: `{user_id}` in URL must match JWT user ID
- Update security standards for Better Auth token compatibility

### 2. Update API Design Standards Section  
- Replace current `/api/v1/{resources}` pattern with `/api/{user_id}/{resources}` pattern
- Document that all user-specific endpoints must follow this pattern
- Specify that authentication endpoints remain `/api/v1/auth/*`
- Add security validation requirements for path parameter matching

### 3. Update Section III (Persistent & Relational State)
- Enhance data isolation requirements to include path parameter validation
- Add requirement for multi-user isolation testing
- Specify that all queries must be scoped to JWT user ID, not path parameter

### 4. Update Frontend Architecture Standards
- Add requirements for Better Auth integration in frontend
- Specify axios interceptor implementation for token attachment
- Add requirements for user ID extraction and URL construction
- Define how frontend handles 403 forbidden responses

### 5. Update Success Criteria
- Add functional requirements for endpoint migration
- Add requirements for path parameter validation
- Include frontend integration requirements
- Add multi-user isolation testing requirements

### 6. Update Security and Technology Constraints
- Add Better Auth specific constraints
- Update token storage requirements to reflect Better Auth management
- Update API endpoint format constraints
- Add endpoint migration requirements

## Implementation Requirements

### Backend Changes Required:
- Change `/api/v1/tasks/*` to `/api/{user_id}/tasks/*`
- Change `/api/v1/tags/*` to `/api/{user_id}/tags/*`
- Add user_id path validation in all endpoints
- Validate that path user_id matches JWT user_id
- Scope all queries to JWT user_id (not path parameter)

### Frontend Changes Required:
- Create API client at `@/lib/api-client` that uses Better Auth tokens
- Extract user_id from Better Auth session for URL construction
- Update all API calls to use new path patterns
- Implement 403/401 error handling

## Security Critical Requirements

1. **Path Parameter Validation**: Every endpoint with user_id in path must validate that path parameter matches JWT user_id
2. **Data Scoping**: All database queries must use JWT user_id, not path parameter
3. **Access Control**: Mismatched user_id in path vs JWT must return 403 Forbidden
4. **Token Management**: Better Auth tokens must be properly validated by backend

## Migration Strategy

The constitution update should clearly specify:
1. How existing endpoints need to be migrated
2. What validation requirements are critical for security
3. How frontend and backend need to work together
4. What tests are required to validate the implementation

## Version Update
- Update to next version (e.g., 2.3.0) 
- Include sync impact report with changes
- Document the reason for each change
- Ensure requirement-to-rule mapping is updated

Please update the constitution with these changes, maintaining the same format and structure as the original document while incorporating all the Better Auth integration requirements and the `{user_id}/resources` API pattern.
```

## Response snapshot

The constitution has been successfully updated to reflect the Better Auth integration requirements. Here's a summary of the changes made:

## Summary of Changes Made

1. **Section IV (User Authentication & JWT Security)**: Completely updated to reflect Better Auth JWT plugin integration, clarifying that Better Auth handles token issuance and validation against a shared secret, with enhanced security requirements.

2. **API Design Standards**: Updated API patterns from `/api/v1/{resources}` to `/api/{user_id}/{resources}`, with added requirements for path parameter validation.

3. **Section III (Persistent & Relational State)**: Enhanced data isolation requirements to specify JWT user_id as the authoritative source and added multi-user isolation testing requirements.

4. **Frontend Architecture Standards**: Added sections for Better Auth integration and API client implementation requirements.

5. **Success Criteria**: Updated functional and technical requirements to include Better Auth integration, API migration, and path validation requirements.

6. **Security and Technology Constraints**: Added new constraints for Better Auth, API endpoint format, and migration requirements.

7. **Version Update**: Updated version from 2.2.0 to 2.3.0 with a comprehensive sync impact report.

The updated constitution now properly reflects all the Better Auth integration requirements and the `{user_id}/resources` API pattern, with clear guidelines for frontend and backend implementation.

## Outcome

- ✅ Impact: Constitution updated to reflect Better Auth integration requirements and new API patterns
- 🧪 Tests: null
- 📁 Files: .specify/memory/constitution.md updated with version 2.3.0
- 🔁 Next prompts: Implementation of Better Auth integration according to updated constitution
- 🧠 Reflection: The constitution now properly specifies the security-critical requirements for path parameter validation and JWT user_id scoping

## Evaluation notes (flywheel)

- Failure modes observed: null
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Begin implementation of Better Auth integration based on updated constitution