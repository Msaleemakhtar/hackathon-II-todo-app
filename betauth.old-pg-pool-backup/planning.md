# Better Auth Integration - Implementation Plan

**Project:** Hackathon II Todo App
**Date:** 2025-12-10
**Status:** Approved - Ready for Implementation

---

## Executive Summary

This plan integrates Better Auth authentication with a **hybrid architecture**:
- **Frontend:** Better Auth React hooks for authentication UI/UX
- **Backend:** Enhanced FastAPI JWT system with Better Auth-compatible tokens
- **Routes:** Restructure from `/api/v1/tasks` to `/api/{user_id}/tasks` with validation
- **Security:** Three-layer defense (JWT + path validation + query filtering)

**Key Insight:** We keep the working FastAPI auth and enhance it for Better Auth compatibility, avoiding Node.js sidecar complexity.

---

## Current State

### Backend (FastAPI)
✅ Complete JWT auth with `python-jose`, bcrypt, 15min/7day tokens
✅ Routes: `/api/v1/auth/*` and `/api/v1/tasks/*`
✅ User model with UUID, service layer filters by user_id
✅ 12+ passing auth tests

### Frontend (Next.js 16)
✅ Auth pages scaffolded, useAuth hook mocked
❌ API client missing (`/src/lib/api-client.ts`)
❌ Better Auth not installed
❌ No actual backend integration

---

## Architecture Decision: Hybrid Approach

**Challenge:** Better Auth is TypeScript/Node.js, backend is Python/FastAPI

**Solution:**
- Frontend: Better Auth for session management + React hooks
- Backend: Keep FastAPI JWT, format tokens for Better Auth compatibility
- Integration: Better Auth calls FastAPI endpoints, FastAPI issues JWTs
- Shared: `BETTER_AUTH_SECRET` for JWT signing/verification

**Benefits:** Leverages working FastAPI auth, gains Better Auth UX, no Node.js sidecar

---

## Implementation: 7 Phases

### Phase 1: Auth SDK Package (`packages/auth-sdk/`)

Create shared types and utilities:

```
packages/auth-sdk/
├── package.json
├── src/
│   ├── types.ts           # JWT payload interface, User type
│   └── frontend/
│       └── api-client.ts  # Axios with interceptors
```

**Key type:**
```typescript
interface BetterAuthJWTPayload {
  sub: string;        // User ID
  email: string;
  name?: string;
  exp: number;
  iat: number;
  type: 'access' | 'refresh';
}
```

---

### Phase 2: Backend JWT Enhancement

**Critical files:**

**`/backend/src/core/config.py`:**
- Add `BETTER_AUTH_SECRET` variable (64+ chars)
- Alias to `JWT_SECRET_KEY` for compatibility

**`/backend/src/core/security.py`:**
- Update `create_access_token()` to use Better Auth JWT structure
- Use `BETTER_AUTH_SECRET` for signing
- Include claims: `sub`, `email`, `name`, `exp`, `iat`, `type`

**`/backend/src/core/dependencies.py`:**
- Add `validate_user_access(user_id: str, current_user: User)` function
- Returns 403 if path user_id ≠ JWT user_id
- Used in all protected routes

---

### Phase 3: Route Restructuring

**Change pattern:**
```python
# Before
@router.get("/", response_model=TaskListResponse)
async def list_tasks(current_user: User = Depends(get_current_user), ...):

# After
@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: str,
    current_user: User = Depends(validate_user_access),
    ...
):
```

**Files to update:**
- `/backend/src/routers/tasks.py` - All 8 task endpoints
- `/backend/src/routers/tags.py` - All tag endpoints
- `/backend/src/main.py` - Router prefixes

**New routes:**
```
GET    /api/{user_id}/tasks
POST   /api/{user_id}/tasks
GET    /api/{user_id}/tasks/{task_id}
PUT    /api/{user_id}/tasks/{task_id}
PATCH  /api/{user_id}/tasks/{task_id}
DELETE /api/{user_id}/tasks/{task_id}
```

**Security:** Always use `current_user.id` in service layer, never path `user_id`

---

### Phase 4: Frontend Better Auth Integration

**Install:**
```bash
cd frontend
bun add better-auth@latest @better-auth/react
```

**Create `/frontend/src/lib/auth.ts`:**
```typescript
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  endpoints: {
    signIn: "/api/v1/auth/login",
    signUp: "/api/v1/auth/register",
    getSession: "/api/v1/auth/me",
  },
});
```

**Create `/frontend/src/lib/api-client.ts`:**
```typescript
import axios from 'axios';
import { authClient } from './auth';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  withCredentials: true,
});

// Request interceptor: attach JWT
apiClient.interceptors.request.use(async (config) => {
  const session = await authClient.getSession();
  if (session?.user?.accessToken) {
    config.headers.Authorization = `Bearer ${session.user.accessToken}`;
  }
  return config;
});

// Response interceptor: handle 401/403
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await authClient.refreshToken();
      return apiClient.request(error.config);
    }
    return Promise.reject(error);
  }
);
```

**Update `/frontend/src/hooks/useAuth.ts`:**
```typescript
import { useSession } from '@/lib/auth';

export function useAuth() {
  const { data: session, status } = useSession();
  return {
    user: session?.user || null,
    isLoading: status === 'loading',
  };
}
```

**Update `/frontend/src/hooks/useTasks.ts`:**
- Change all API calls from `/api/v1/tasks` to `/api/${user.id}/tasks`
- Use `apiClient` from `/lib/api-client.ts`

---

### Phase 5: Environment Configuration

**Backend `.env`:**
```bash
BETTER_AUTH_SECRET=<64+ hex chars>
JWT_SECRET_KEY=${BETTER_AUTH_SECRET}
DATABASE_URL=postgresql+asyncpg://...
CORS_ORIGINS='["http://localhost:3000"]'
```

**Frontend `.env.local`:**
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
BETTER_AUTH_SECRET=<same as backend>
```

**Generate secret:**
```bash
openssl rand -hex 64
```

---

### Phase 6: Testing

**Backend tests:**
- JWT structure validates Better Auth format
- Path validation: 403 when user_id mismatch
- Data isolation: service layer uses JWT user_id

**Manual security checklist:**
- [ ] User can register/login/logout
- [ ] User can access own tasks
- [ ] User cannot access other user tasks (403)
- [ ] URL manipulation blocked: `/api/OTHER_USER_ID/tasks` → 403
- [ ] Token refresh works on 401

---

### Phase 7: Constitution Update

**File:** `/.specify/memory/constitution.md`

**Update Section IV (Authentication):**
- Document hybrid Better Auth + FastAPI architecture
- Describe JWT structure (sub, email, name, exp, iat, type)
- Explain three-layer security model

**Update Section V (API Design):**
- Document route pattern: `/api/{user_id}/resources`
- Explain path validation rules

---

## Critical Files

**Backend (5 files):**
1. `/backend/src/core/security.py` - JWT with BETTER_AUTH_SECRET
2. `/backend/src/core/dependencies.py` - Add validate_user_access()
3. `/backend/src/routers/tasks.py` - Add {user_id} path param
4. `/backend/src/routers/tags.py` - Add {user_id} path param
5. `/backend/src/main.py` - Update router prefixes

**Frontend (4 files):**
1. `/frontend/src/lib/auth.ts` - Better Auth config (NEW)
2. `/frontend/src/lib/api-client.ts` - Axios interceptors (NEW)
3. `/frontend/src/hooks/useAuth.ts` - Use Better Auth session
4. `/frontend/src/hooks/useTasks.ts` - Update API URLs

**Configuration:**
- `/backend/.env` - Add BETTER_AUTH_SECRET
- `/frontend/.env.local` - Add API URL and secret

---

## Security: Three-Layer Defense

**Layer 1: JWT Authentication**
- Valid signed token required
- No token → 401 Unauthorized

**Layer 2: Path Validation**
- JWT user_id must match path user_id
- Mismatch → 403 Forbidden
- Implemented in `validate_user_access()` dependency

**Layer 3: Query Filtering (Defense in Depth)**
- Service layer always uses `current_user.id` from JWT
- Never uses path parameter for queries
- Ensures isolation even if layers 1-2 bypassed

**Example Attack Prevention:**
```
User A tries: GET /api/USER_B_ID/tasks
→ Layer 1: JWT valid ✓
→ Layer 2: user_id mismatch ✗ → 403 Forbidden
→ Layer 3: Not reached (blocked at Layer 2)
```

---

## Implementation Order (Critical)

**Stage 1: Backend Prep (No breaking changes)**
1. Add BETTER_AUTH_SECRET to config
2. Update JWT payload structure
3. Add validate_user_access() function
4. Write tests

**Stage 2: Backend Routes (Breaking change)**
5. Update all routes with {user_id} path
6. Update router prefixes
7. Update backend tests

**Stage 3: Frontend Foundation**
8. Create auth-sdk package
9. Install Better Auth
10. Create auth.ts and api-client.ts

**Stage 4: Frontend Integration (Breaking change)**
11. Update useAuth hook
12. Update all API calls with new URLs
13. Update login/signup pages

**Stage 5: Testing**
14. Run all tests
15. Manual security checklist

**Stage 6: Documentation**
16. Update constitution

---

## Risk Mitigation

**High Risk:** Better Auth config complexity
**Mitigation:** Minimal config, can fallback to custom hooks

**Medium Risk:** JWT format mismatch
**Mitigation:** Unit tests, manual token verification

**Medium Risk:** Route changes break frontend
**Mitigation:** Update all at once, comprehensive testing

**Low Risk:** Env var misconfiguration
**Mitigation:** Startup validation, clear examples

---

## Success Criteria

**Functional:**
- ✅ Users can register, login, logout
- ✅ Users can CRUD their own tasks
- ✅ Users get 403 accessing other user tasks
- ✅ JWT auto-attached to requests
- ✅ Token refresh automatic

**Security:**
- ✅ Path user_id validated against JWT
- ✅ Queries filtered by JWT user_id (not path)
- ✅ No data leakage in errors
- ✅ 15-min access tokens, 7-day refresh

**Code Quality:**
- ✅ All tests passing
- ✅ No hardcoded secrets
- ✅ Constitution updated

---

## Questions Resolved

✅ Route pattern? → `/api/{user_id}/tasks` with validation
✅ Auth integration? → Hybrid (Better Auth frontend + FastAPI backend)
✅ SDK location? → `packages/auth-sdk/`

## Open Questions

- Better Auth exact configuration for custom backend?
- Error message standardization?
- Migration for existing test users?

---

**Status:** ✅ Approved - Ready for Phase 1 implementation
**Next Step:** Begin Phase 1 - Auth SDK Package setup
