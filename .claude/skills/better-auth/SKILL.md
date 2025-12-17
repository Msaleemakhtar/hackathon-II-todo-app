---
name: better-auth
description: Comprehensive Better Auth integration guide for TypeScript/Next.js frontend and FastAPI backend authentication. Use when implementing user authentication in full-stack applications requiring (1) Email/password authentication with Better Auth, (2) JWT token flow between frontend and backend, (3) Session management and caching, (4) Multi-user data isolation with path validation, (5) Database schema setup for Better Auth tables, (6) OAuth provider integration. Covers complete authentication architecture from database setup through frontend session handling to backend token validation.
---

# Better Auth Integration

Expert guidance for implementing Better Auth authentication in full-stack TypeScript applications with Next.js frontend and FastAPI backend.

## Official Documentation

- **Better Auth**: https://www.better-auth.com/docs
- **Installation**: https://www.better-auth.com/docs/installation
- **Drizzle Adapter**: https://www.better-auth.com/docs/adapters/drizzle
- **GitHub**: https://github.com/better-auth/better-auth

## Quick Start Navigation

Choose your entry point:

- **New Project Setup**: Follow "Full Setup Workflow" below
- **Frontend Only**: Read `references/nextjs-setup.md`
- **Backend Only**: Read `references/fastapi-integration.md`
- **JWT Token Flow**: Read `references/jwt-token-flow.md`
- **Database Setup**: Read `references/database-schema.md`
- **Security Best Practices**: Read `references/security-patterns.md`
- **API Client**: Read `references/api-client.md`
- **Troubleshooting**: Read `references/troubleshooting.md`

## Full Setup Workflow

Complete end-to-end integration process for Better Auth with Next.js + FastAPI.

### Phase 1: Database Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   bun add better-auth drizzle-orm pg
   bun add -d drizzle-kit @types/pg
   ```

2. **Configure environment** (`.env.local`):
   ```env
   BETTER_AUTH_SECRET=<openssl-rand-base64-32>
   BETTER_AUTH_URL=http://localhost:3000
   DATABASE_URL=postgresql://user:password@host:5432/database
   ```

3. **Generate schema**:
   ```bash
   bun x @better-auth/cli generate
   drizzle-kit generate
   drizzle-kit migrate
   ```

   **Details**: See `references/database-schema.md`

### Phase 2: Frontend Setup

1. **Create auth server** (`lib/auth-server.ts`):
   - Use template: `assets/auth-server.ts.template`
   - Configure database adapter (Drizzle + PostgreSQL)
   - Enable email/password authentication
   - Set session expiration (7 days)
   - Configure rate limiting (10 req/min)

2. **Create auth client** (`lib/auth.ts`):
   ```ts
   import { createAuthClient } from "better-auth/react";

   export const authClient = createAuthClient({
     baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL,
   });

   export const { signIn, signUp, signOut, useSession } = authClient;
   ```

3. **Create API route** (`app/api/auth/[...all]/route.ts`):
   ```ts
   import { auth } from "@/lib/auth-server";
   import { toNextJsHandler } from "better-auth/next-js";

   export const { GET, POST } = toNextJsHandler(auth);
   ```

   **Details**: See `references/nextjs-setup.md`

### Phase 3: JWT Token Endpoint

1. **Create token generation endpoint** (`app/api/auth/token/route.ts`):
   - Verify Better Auth session
   - Generate JWT with HS256
   - Include claims: `sub`, `email`, `name`, `exp`, `iat`
   - Sign with `BETTER_AUTH_SECRET`
   - Return token + expiration

2. **Install JWT library**:
   ```bash
   bun add jsonwebtoken
   bun add -d @types/jsonwebtoken
   ```

   **Details**: See `references/jwt-token-flow.md`

### Phase 4: API Client Setup

1. **Create API client** (`lib/api-client.ts`):
   - Use template: `assets/api-client.ts.template`
   - Configure axios with base URL
   - Implement token caching (27-minute lifetime)
   - Add request interceptor (attach JWT)
   - Add response interceptor (handle 401)

2. **Install axios**:
   ```bash
   bun add axios
   ```

   **Details**: See `references/api-client.md`

### Phase 5: Backend JWT Validation

1. **Create security module** (`backend/core/security.py`):
   - Use template: `assets/security.py.template`
   - Implement JWT verification
   - Add path validation (user_id matching)
   - Create FastAPI dependencies

2. **Install Python dependencies**:
   ```bash
   cd backend
   uv add "python-jose[cryptography]" python-multipart
   ```

3. **Configure environment** (`backend/.env`):
   ```env
   BETTER_AUTH_SECRET=<same-as-frontend>
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Protect routes**:
   ```python
   from core.security import validate_path_user_id

   @router.get("/{user_id}/tasks")
   async def get_tasks(user_id: str, request: Request):
       payload = await validate_path_user_id(request, user_id)
       jwt_user_id = payload["sub"]
       # Use jwt_user_id for database queries
   ```

   **Details**: See `references/fastapi-integration.md`

### Phase 6: Validation

1. **Validate environment variables**:
   ```bash
   python scripts/validate_env.py
   ```

2. **Test authentication flow**:
   - Sign up → verify session created
   - Sign in → verify session persists
   - API call → verify JWT attached
   - Backend → verify token validated
   - Sign out → verify session cleared

3. **Test security**:
   - User A cannot access User B's data
   - Invalid tokens return 401
   - Path mismatches return 403

## Key Architecture Patterns

### Pattern 1: Hybrid Authentication

**Better Auth for Frontend, JWT for Backend**

```
Frontend (Next.js)          Backend (FastAPI)
─────────────────           ─────────────────
Better Auth Session    →    JWT Token
(httpOnly cookies)          (Bearer header)

Session Management     →    Stateless Validation
Secure, State-Based         Scalable, Horizontal
```

**Why**:
- Better Auth handles session complexity
- JWT enables stateless backend
- Shared secret ensures security
- Horizontal scaling supported

### Pattern 2: Three-Layer Security

```
Layer 1: JWT Authentication
└─> Verify token signature and expiration

Layer 2: Path Validation
└─> Ensure path user_id matches JWT user_id

Layer 3: Query Filtering
└─> Scope database queries to JWT user_id
```

**Implementation**:
```python
# Layer 1 & 2: validate_path_user_id()
payload = await validate_path_user_id(request, path_user_id)

# Layer 3: Use JWT user_id for queries
jwt_user_id = payload["sub"]
tasks = db.query(Task).filter(Task.user_id == jwt_user_id)
```

### Pattern 3: Token Caching

**Minimize token generation requests with intelligent caching**

```
Cache Strategy:
├─> Token lifetime: 30 minutes
├─> Cache refresh: 27 minutes (3-minute buffer)
├─> Prevents duplicate fetches
└─> Memory-only storage (no localStorage)
```

**Benefits**:
- Reduces API calls (1 token per 27 min)
- No localStorage security risks
- Automatic refresh before expiry
- Promise chaining prevents duplicates

## Environment Variables

### Frontend (`.env.local`)

```env
# Better Auth Configuration
BETTER_AUTH_SECRET=<min-32-chars-openssl-rand-base64-32>
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:password@host:5432/database

# API Configuration
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

### Backend (`.env`)

```env
# Must match frontend
BETTER_AUTH_SECRET=<same-as-frontend>

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Token Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Validation**:
```bash
python scripts/validate_env.py
```

## Reference Guides

### Frontend Integration
- **Next.js Setup**: `references/nextjs-setup.md`
  - Installation and configuration
  - Email/password authentication
  - Session management
  - Protected routes
  - Sign up/in/out flows

### Backend Integration
- **FastAPI Integration**: `references/fastapi-integration.md`
  - JWT validation with python-jose
  - Security module implementation
  - Path validation patterns
  - Router protection
  - Multi-layer security

### Architecture & Flow
- **JWT Token Flow**: `references/jwt-token-flow.md`
  - Hybrid authentication architecture
  - Token generation and validation
  - Caching strategies
  - Refresh flows
  - Security considerations

### Database & Schema
- **Database Schema**: `references/database-schema.md`
  - Required tables (user, account, session, verification)
  - Drizzle adapter setup
  - Migration workflows
  - PostgreSQL configuration
  - Schema customization

### Security & Best Practices
- **Security Patterns**: `references/security-patterns.md`
  - Session security (httpOnly cookies)
  - JWT best practices
  - Rate limiting
  - Multi-user data isolation
  - CORS configuration
  - Security checklist

### Client Implementation
- **API Client**: `references/api-client.md`
  - Axios configuration
  - Request/response interceptors
  - Token caching implementation
  - Session caching
  - Error handling
  - React hook integration

### Problem Solving
- **Troubleshooting**: `references/troubleshooting.md`
  - Common issues and solutions
  - Installation problems
  - Database errors
  - Authentication failures
  - JWT validation issues
  - CORS problems
  - Performance optimization

## Template Assets

Ready-to-use templates in `assets/` directory:

1. **auth-server.ts.template**: Better Auth server configuration
   - Database adapter setup
   - Email/password config
   - Session settings
   - Rate limiting
   - Security options

2. **api-client.ts.template**: Frontend API client
   - Token caching
   - Session caching
   - Axios interceptors
   - Error handling

3. **security.py.template**: FastAPI JWT validation
   - JWT verification
   - Path validation
   - FastAPI dependencies
   - Error handling

4. **schema.ts.template**: Drizzle schema
   - User, account, session, verification tables
   - Field definitions
   - Indexes
   - Type exports

## Scripts

### Environment Validation

Validate all required environment variables before starting:

```bash
python scripts/validate_env.py

# Frontend only
python scripts/validate_env.py --frontend

# Backend only
python scripts/validate_env.py --backend
```

**Checks**:
- `BETTER_AUTH_SECRET` length (32+ chars)
- Database URL format
- Required NEXT_PUBLIC_ variables
- URL format validation

## Common Usage Examples

### Sign Up Flow

```tsx
import { signUp } from '@/lib/auth';

const result = await signUp.email({
  email: "user@example.com",
  password: "secure-password",
  name: "User Name",
});

if (result.error) {
  console.error(result.error.message);
} else {
  // User auto-signed in
  router.push('/dashboard');
}
```

### Protected API Call

```tsx
import apiClient from '@/lib/api-client';
import { useAuthContext } from '@/contexts/AuthContext';

const { user } = useAuthContext();

// Token automatically attached by interceptor
const response = await apiClient.get(`/v1/${user.id}/tasks`);
const tasks = response.data.tasks;
```

### Backend Route Protection

```python
from core.security import validate_path_user_id

@router.get("/{user_id}/tasks")
async def get_tasks(user_id: str, request: Request):
    # Validates JWT and path user_id
    payload = await validate_path_user_id(request, user_id)
    jwt_user_id = payload["sub"]

    # Query with JWT user_id
    tasks = await get_user_tasks(jwt_user_id)
    return {"tasks": tasks}
```

## Security Checklist

Before deploying:

- [ ] `BETTER_AUTH_SECRET` is 32+ characters
- [ ] Same secret in frontend and backend
- [ ] Secrets not committed to version control
- [ ] HTTPS enforced in production
- [ ] Email verification enabled (if required)
- [ ] Rate limiting configured (10 req/min)
- [ ] HttpOnly cookies enabled
- [ ] JWT tokens expire in 15-30 minutes
- [ ] Path user_id validated against JWT
- [ ] All queries scoped to JWT user_id
- [ ] Multi-user isolation tests pass
- [ ] CORS properly configured
- [ ] Environment validation passes

## Need Help?

1. Check `references/troubleshooting.md` for common issues
2. Verify environment with `scripts/validate_env.py`
3. Review security patterns in `references/security-patterns.md`
4. Visit Better Auth docs: https://www.better-auth.com/docs
5. GitHub issues: https://github.com/better-auth/better-auth/issues
