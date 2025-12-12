# Quickstart Guide: Better Auth Integration

**Feature**: Better Auth Integration
**Date**: 2025-12-10
**Status**: Draft

## Overview

This quickstart guide provides instructions for developers to quickly get up and running with the Better Auth integration feature. It covers setting up the authentication system, running the necessary migrations, and testing the authentication flow.

## Prerequisites

- Node.js 18+ and bun installed
- Python 3.11+ with uv installed
- PostgreSQL server (or Neon Serverless account)
- Docker and docker-compose (optional, for local development)

## Setup Instructions

### 1. Environment Configuration

First, set up your environment variables in both frontend and backend:

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_COOKIE_DOMAIN=localhost
```

**Backend (.env)**:
```bash
BETTER_AUTH_SECRET=your-very-secure-jwt-secret-key-here-min-32-chars
DATABASE_URL=postgresql://user:password@localhost:5432/todoapp
```

**Note**: The `BETTER_AUTH_SECRET` must be the same in both frontend and backend for proper JWT validation.

### 2. Install Dependencies

```bash
# Install backend dependencies with uv
cd backend
uv sync
cd ..

# Install frontend dependencies with bun
cd frontend
bun install
cd ..
```

### 3. Database Setup

Run the database migrations:

```bash
cd backend
uv run alembic upgrade head
```

### 4. Running the Applications

**Option A: Using Docker Compose (Recommended for local development)**:
```bash
docker-compose up
```

**Option B: Running Services Separately**:
```bash
# Terminal 1: Start backend
cd backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
bun run dev
```

## API Client Setup

The API client is implemented at `@/lib/api-client` as required by the constitution:

```typescript
// Example usage in frontend components
import apiClient from '@/lib/api-client';

// All requests will automatically include the Better Auth JWT token
const tasks = await apiClient.get(`/api/${userId}/tasks`);
```

## Testing the Authentication Flow

### 1. Register a New User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securePassword123",
    "name": "Test User"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securePassword123"
  }'
```

### 3. Access Protected Resources
```bash
# Using the JWT token from login response:
curl -X GET http://localhost:8000/api/user_12345/tasks \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json"
```

## Key Architecture Points

1. **JWT Validation**: The backend uses the shared secret to validate JWT tokens issued by Better Auth
2. **Path Parameter Validation**: All endpoints with `{user_id}` in the path validate that the path parameter matches the JWT user_id
3. **Data Isolation**: All database queries are scoped to the JWT user_id, not the path parameter
4. **API Client**: The API client at `@/lib/api-client` handles token attachment automatically

## Troubleshooting

### Common Issues

1. **JWT Validation Fails**
   - Ensure `BETTER_AUTH_SECRET` is identical in frontend and backend
   - Check that tokens are being properly included in requests

2. **Path Parameter Validation Returns 403**
   - Verify the user_id in the path matches the user_id in the JWT token
   - Ensure the authenticated user is accessing their own resources

3. **Database Connection Issues**
   - Check that the DATABASE_URL is properly configured
   - Verify that the database server is running

### Useful Commands

```bash
# Run backend tests
cd backend && uv run pytest

# Run frontend tests
cd frontend && bun test

# Run linters
cd backend && ruff check .
cd frontend && bun run lint

# Run type checker
cd frontend && bun run typecheck
```

## Next Steps

1. Explore the API documentation at `/docs` (Swagger) or `/redoc` (ReDoc)
2. Review the API contracts in `/specs/004-better-auth-integration/contracts/`
3. Look at the data model in `/specs/004-better-auth-integration/data-model.md`
4. Review the tasks in `/specs/004-better-auth-integration/tasks.md` once generated