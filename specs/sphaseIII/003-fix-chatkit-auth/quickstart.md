# Quickstart Guide: Fix ChatKit Integration and Better-Auth Backend

**Generated**: 2025-12-20
**Phase**: Phase 1 - Design
**Target Audience**: Developers implementing the fix

---

## Overview

This guide walks through fixing the three critical issues blocking Phase III ChatKit integration:

1. **TypeScript Build Errors** - Missing type definitions for ChatKit and Better Auth
2. **JWT Token Retrieval** - Broken authentication token access
3. **Database Schema** - Missing Better Auth tables

**Estimated Time**: 30-45 minutes

---

## Prerequisites

Before starting, ensure you have:

- ✅ Node.js 20+ installed
- ✅ Python 3.11+ installed
- ✅ Bun package manager installed (`npm install -g bun`)
- ✅ UV package manager installed (`pip install uv`)
- ✅ PostgreSQL database accessible (Neon or local)
- ✅ Git repository cloned and on branch `003-fix-chatkit-auth`

---

## Part 1: Environment Configuration

### Step 1.1: Generate Better Auth Secret

The frontend and backend MUST share the same secret key for JWT validation.

```bash
# Generate a secure 256-bit secret key
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Example output:
# a7f3c8b2e1d9f4a6c3b8e7d2f9a4c1b3e6d8f2a9c4b7e1d3f8a2c6b9e4d7f1a3
```

**Copy this secret** - you'll use it in both frontend and backend .env files.

### Step 1.2: Configure Frontend Environment

Create or update `phaseIII/frontend/.env.local`:

```bash
# Database connection (same as backend)
DATABASE_URL=postgresql://username:password@host:5432/database_name

# Better Auth Configuration
BETTER_AUTH_SECRET=a7f3c8b2e1d9f4a6c3b8e7d2f9a4c1b3e6d8f2a9c4b7e1d3f8a2c6b9e4d7f1a3  # ⚠️ MUST MATCH BACKEND
BETTER_AUTH_URL=http://localhost:3000

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

### Step 1.3: Configure Backend Environment

Create or update `phaseIII/backend/.env`:

```bash
# Database connection (same as frontend)
DATABASE_URL=postgresql://username:password@host:5432/database_name

# Better Auth Configuration
BETTER_AUTH_SECRET=a7f3c8b2e1d9f4a6c3b8e7d2f9a4c1b3e6d8f2a9c4b7e1d3f8a2c6b9e4d7f1a3  # ⚠️ MUST MATCH FRONTEND

# Server Configuration
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:3000"]

# AI Model Configuration (optional - for chat functionality)
AI_MODEL_PROVIDER=gemini  # or "openai"
GEMINI_API_KEY=your-gemini-api-key
# OPENAI_API_KEY=your-openai-api-key  # if using OpenAI

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8001
```

**Critical**: The `BETTER_AUTH_SECRET` value MUST be identical in both files. JWT tokens signed by the frontend will be validated by the backend using this shared secret.

---

## Part 2: Backend Database Migration

### Step 2.1: Navigate to Backend Directory

```bash
cd phaseIII/backend
```

### Step 2.2: Run Database Migration

The migration `003_better_auth_tables.py` creates four Better Auth tables: `user`, `session`, `account`, and `verification`.

```bash
# Run migrations
uv run alembic upgrade head
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, Add Better Auth tables
```

### Step 2.3: Verify Tables Created

```bash
# Connect to your database and verify tables exist
psql $DATABASE_URL -c "\dt"
```

**Expected Tables**:
```
           List of relations
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+---------
 public | account         | table | postgres
 public | conversations   | table | postgres
 public | messages        | table | postgres
 public | session         | table | postgres
 public | tasks_phaseiii  | table | postgres
 public | user            | table | postgres
 public | verification    | table | postgres
```

---

## Part 3: Frontend Type Definitions

### Step 3.1: Create Types Directory

```bash
cd phaseIII/frontend
mkdir -p src/types
```

### Step 3.2: Copy Type Definitions

Copy the type definitions from the contract:

```bash
cp ../../specs/003-fix-chatkit-auth/contracts/auth-types.ts src/types/auth.d.ts
```

Or manually create `src/types/auth.d.ts` with the content from `contracts/auth-types.ts`.

### Step 3.3: Update tsconfig.json (if needed)

Ensure TypeScript includes the types directory:

```json
{
  "compilerOptions": {
    "typeRoots": ["./node_modules/@types", "./src/types"]
  },
  "include": ["src/**/*", "src/types/**/*"]
}
```

---

## Part 4: Fix Better Auth Configuration

### Step 4.1: Update Backend Better Auth Config

No changes needed - backend already validates JWTs correctly via `app/dependencies/auth.py`.

### Step 4.2: Update Frontend Better Auth Server Config

Edit `phaseIII/frontend/src/lib/auth-server.ts`:

```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";  // ✅ Add JWT plugin import
import { Pool } from "pg";

let authInstance: ReturnType<typeof betterAuth> | null = null;

export function getAuth() {
  if (authInstance) {
    return authInstance;
  }

  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
  });

  authInstance = betterAuth({
    database: pool,
    emailAndPassword: {
      enabled: true,
    },
    secret: process.env.BETTER_AUTH_SECRET,
    baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
    plugins: [  // ✅ Add JWT plugin
      jwt({
        expiresIn: "7d",
        algorithm: "HS256",
        issuer: "phaseiii-app",
      }),
    ],
  });

  return authInstance;
}
```

### Step 4.3: Update Frontend Better Auth Client Config

Edit `phaseIII/frontend/src/lib/auth-client.ts`:

```typescript
import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";  // ✅ Add JWT client plugin

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
  plugins: [jwtClient()],  // ✅ Add JWT client plugin
});

export const { useSession, signIn, signOut, signUp } = authClient;
```

---

## Part 5: Create JWT Token Endpoint

### Step 5.1: Create Token API Route

Create `phaseIII/frontend/src/app/api/auth/token/route.ts`:

```typescript
import { getAuth } from "@/lib/auth-server";

export async function GET(request: Request) {
  try {
    const auth = getAuth();
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session) {
      return Response.json({ error: "No active session" }, { status: 401 });
    }

    // JWT token is available via the JWT plugin
    const token = (session as any).jwt;

    if (!token) {
      return Response.json(
        { error: "JWT token not available" },
        { status: 500 }
      );
    }

    return Response.json({ token });
  } catch (error) {
    console.error("Token endpoint error:", error);
    return Response.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
```

---

## Part 6: Fix ChatKit Integration

### Step 6.1: Update Chat Page

Edit `phaseIII/frontend/src/app/chat/page.tsx`:

**Change 1**: Import Better Auth session type

```typescript
import { useSession } from '@/lib/auth';
import type { BetterAuthSession } from '@/types/auth.d';  // ✅ Add type import
```

**Change 2**: Fix token retrieval

Replace the token extraction logic (lines 25-49) with:

```typescript
useEffect(() => {
  if (!isPending && !session) {
    router.push('/login');
    return;
  }

  if (session) {
    // ✅ JWT is now available via the JWT plugin
    if (session.jwt) {
      setAuthToken(session.jwt);
    } else {
      // ✅ Fallback: fetch from token endpoint
      fetch('/api/auth/token')
        .then(res => res.json())
        .then(data => {
          if (data.token) {
            setAuthToken(data.token);
          }
        })
        .catch(err => console.error('Failed to fetch token:', err));
    }
  }
}, [session, isPending, router]);
```

**Change 3**: Fix ChatKit useChatKit usage

Replace the useChatKit call (lines 100-118) with:

```typescript
const control = useChatKit({
  // ✅ Remove 'options' wrapper - pass params directly
  apiUrl: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/chatkit`,
  authToken,  // ✅ authToken is now at top level
  onError: (error) => {
    console.error('ChatKit error:', error);
    alert(`Chat error: ${error.message || 'An error occurred'}`);
  },
  onResponseEnd: (response) => {
    console.log('Response ended:', response);
  },
  onThreadChange: (thread) => {
    console.log('Thread changed:', thread);
  },
});
```

---

## Part 7: Testing the Fix

### Step 7.1: Test Frontend Build

```bash
cd phaseIII/frontend
bun run build
```

**Expected**: Build completes successfully with zero TypeScript errors.

### Step 7.2: Start Development Servers

**Terminal 1** (Backend):
```bash
cd phaseIII/backend
uv run uvicorn app.main:app --reload --port 8000
```

**Terminal 2** (Frontend):
```bash
cd phaseIII/frontend
bun run dev
```

### Step 7.3: Test User Registration

1. Navigate to http://localhost:3000/signup
2. Register a new user (email + password)
3. Verify user row created in `user` table
4. Verify account row created in `account` table

```sql
-- Check user was created
SELECT * FROM "user" ORDER BY "createdAt" DESC LIMIT 1;

-- Check account was created
SELECT * FROM account WHERE "userId" = '<user-id-from-above>';
```

### Step 7.4: Test User Login

1. Navigate to http://localhost:3000/login
2. Login with the registered user
3. Verify session row created in `session` table

```sql
-- Check session was created
SELECT * FROM session WHERE "userId" = '<user-id>' ORDER BY "createdAt" DESC LIMIT 1;
```

### Step 7.5: Test JWT Token Retrieval

1. After logging in, open browser DevTools → Network tab
2. Navigate to http://localhost:3000/chat
3. Look for request to `/api/auth/token`
4. Verify response contains `{ "token": "eyJ..." }`

### Step 7.6: Test ChatKit Integration

1. On the chat page, verify:
   - ✅ No "Authentication Token Missing" error
   - ✅ ChatKit component loads
   - ✅ Can type and send a message
   - ✅ Backend receives authenticated request

2. Check backend logs for:
```
INFO: JWT validation successful for user: <user-id>
```

### Step 7.7: Test Data Isolation

1. Create a task via chat: "Add task to buy milk"
2. Verify task in database:

```sql
-- Check task was created for the correct user
SELECT * FROM tasks_phaseiii WHERE user_id = '<user-id-from-jwt>';
```

3. Register a second user and verify they cannot see the first user's task

---

## Troubleshooting

### Issue: "BETTER_AUTH_SECRET not found"

**Solution**: Verify `.env.local` (frontend) and `.env` (backend) both have `BETTER_AUTH_SECRET` set to the same value.

### Issue: "JWT token not available"

**Solution**: Ensure Better Auth JWT plugin is configured on both server and client:
- Server: `plugins: [jwt(...)]` in `auth-server.ts`
- Client: `plugins: [jwtClient()]` in `auth-client.ts`

### Issue: "Type error: 'options' does not exist"

**Solution**: Update `useChatKit` call to pass params directly (not wrapped in `options`).

### Issue: "Table 'user' does not exist"

**Solution**: Run the database migration:
```bash
cd phaseIII/backend
uv run alembic upgrade head
```

### Issue: "Invalid authentication credentials"

**Solution**: Secrets mismatch. Verify `BETTER_AUTH_SECRET` is identical in frontend and backend .env files.

---

## Success Criteria Checklist

After completing this guide, verify all items:

- ✅ Frontend builds without TypeScript errors (`bun run build` succeeds)
- ✅ Better Auth tables exist in database (user, session, account, verification)
- ✅ JWT plugin configured on both frontend and backend
- ✅ JWT token retrieved successfully via `/api/auth/token`
- ✅ ChatKit component initializes without errors
- ✅ User can register, login, and access chat page
- ✅ Authenticated requests work (JWT validation successful)
- ✅ Data isolation enforced (users see only their own tasks)

---

## Next Steps

With the quickstart complete, proceed to:

1. Run `/sp.tasks` to generate implementation task breakdown
2. Implement fixes according to task list
3. Test against all user stories in spec.md
4. Create pull request for review

---

## References

- Specification: [spec.md](./spec.md)
- Data Model: [data-model.md](./data-model.md)
- Type Definitions: [contracts/auth-types.ts](./contracts/auth-types.ts)
- Research Notes: [research.md](./research.md)
