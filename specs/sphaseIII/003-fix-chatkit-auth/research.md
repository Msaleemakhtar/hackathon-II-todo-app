# Research: Fix ChatKit Integration and Better-Auth Backend

**Generated**: 2025-12-20
**Phase**: Phase 0 - Research
**Status**: Complete

## Purpose

Research and resolve all unknowns from the Technical Context to enable Phase 1 design. This document consolidates findings about ChatKit API compatibility, Better Auth JWT plugin configuration, and Better Auth database schema requirements.

---

## Research Task 1: ChatKit useChatKit Hook API

**Unknown**: What is the correct API for @openai/chatkit-react useChatKit hook?

**Current Issue**: Build fails with error:
```
Type error: Object literal may only specify known properties, and 'options' does not exist in type 'UseChatKitOptions'.
```

**Current Code** (phaseIII/frontend/src/app/chat/page.tsx:101-105):
```typescript
const control = useChatKit({
  options: {
    apiUrl: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/chatkit`,
    authToken,
  },
  handlers: { ... }
});
```

### Research Findings

**Source**: @openai/chatkit-react package documentation and type definitions

**Correct API**: The `useChatKit` hook does NOT accept an `options` object. Instead, it accepts parameters directly at the top level.

**Correct Usage**:
```typescript
const control = useChatKit({
  apiUrl: string,           // Backend API endpoint
  authToken?: string,       // Optional JWT token for authentication
  onError?: (error) => void,
  onResponseEnd?: (response) => void,
  onThreadChange?: (thread) => void,
  // ... other handler callbacks
});
```

**Decision**: Remove the `options` wrapper and pass `apiUrl` and `authToken` as top-level properties.

**Alternative Considered**: Creating custom type definitions to match current usage.
**Rejected Because**: This would mask the actual API and cause runtime errors. Better to fix the usage to match the official API.

---

## Research Task 2: Better Auth JWT Plugin Configuration

**Unknown**: How to configure Better Auth to issue and validate JWT tokens for frontend-backend authentication?

**Current Issue**: JWT token not available in frontend session, causing "Authentication Token Missing" error.

### Research Findings

**Source**: Better Auth documentation (https://www.better-auth.com/docs)

**Better Auth JWT Plugin**: Better Auth provides a `jwt` plugin that must be explicitly enabled on both client and server.

**Server Configuration** (auth-server.ts):
```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  database: pool,
  emailAndPassword: {
    enabled: true,
  },
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL,
  plugins: [
    jwt({
      // JWT configuration
      expiresIn: "7d",          // Token expiration
      algorithm: "HS256",       // Signing algorithm
      issuer: "phaseiii-app",   // Token issuer
    })
  ],
});
```

**Client Configuration** (auth-client.ts):
```typescript
import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL,
  plugins: [jwtClient()],
});
```

**Token Retrieval**:
After configuring the JWT plugin, tokens are accessible via:
```typescript
const session = await authClient.getSession();
const token = session?.jwt;  // JWT token is now available
```

Or via API endpoint:
```typescript
// Create /api/auth/token endpoint that calls getSession and returns JWT
const response = await fetch('/api/auth/token');
const { token } = await response.json();
```

**Decision**: Add JWT plugin to both Better Auth server and client configurations. Create `/api/auth/token` endpoint for explicit token retrieval.

---

## Research Task 3: Better Auth Database Schema

**Unknown**: What database tables does Better Auth require for multi-user authentication?

**Current Issue**: Better Auth tables do not exist in the database, preventing proper session management and user storage.

### Research Findings

**Source**: Better Auth database documentation

**Required Tables**:

1. **user** - Stores user account information
   ```sql
   CREATE TABLE user (
     id TEXT PRIMARY KEY,
     email TEXT UNIQUE NOT NULL,
     emailVerified BOOLEAN NOT NULL DEFAULT FALSE,
     name TEXT,
     image TEXT,
     createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
     updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
   );
   ```

2. **session** - Stores active user sessions
   ```sql
   CREATE TABLE session (
     id TEXT PRIMARY KEY,
     userId TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
     expiresAt TIMESTAMP NOT NULL,
     token TEXT UNIQUE NOT NULL,
     ipAddress TEXT,
     userAgent TEXT,
     createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
     updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
   );
   CREATE INDEX idx_session_userId ON session(userId);
   CREATE INDEX idx_session_token ON session(token);
   ```

3. **account** - Stores authentication provider information (email/password)
   ```sql
   CREATE TABLE account (
     id TEXT PRIMARY KEY,
     userId TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
     accountId TEXT NOT NULL,
     providerId TEXT NOT NULL,
     password TEXT,
     accessToken TEXT,
     refreshToken TEXT,
     expiresAt TIMESTAMP,
     createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
     updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
   );
   CREATE INDEX idx_account_userId ON account(userId);
   CREATE UNIQUE INDEX idx_account_provider ON account(providerId, accountId);
   ```

4. **verification** - Stores email verification tokens (optional for MVP but required by Better Auth)
   ```sql
   CREATE TABLE verification (
     id TEXT PRIMARY KEY,
     identifier TEXT NOT NULL,
     value TEXT NOT NULL,
     expiresAt TIMESTAMP NOT NULL,
     createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
     updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
   );
   CREATE INDEX idx_verification_identifier ON verification(identifier);
   ```

**Decision**: Create Alembic migration `003_better_auth_tables.py` to add all four Better Auth tables.

**Alternative Considered**: Using Better Auth's auto-migration feature.
**Rejected Because**: Constitution Principle III requires explicit Alembic migrations for all schema changes. Auto-migration would violate this principle.

**Table Naming Convention**: Better Auth uses lowercase table names (`user`, `session`) not pluralized. This differs from Phase III convention (`tasks_phaseiii`, `conversations`) but is required for Better Auth compatibility.

---

## Research Task 4: TypeScript Type Definitions

**Unknown**: What TypeScript types are needed to resolve compilation errors?

### Research Findings

**Required Type Definitions**:

1. **Better Auth Session Types** (src/types/auth.d.ts):
   ```typescript
   import { Session as BetterAuthSession } from "better-auth/types";

   declare module "better-auth/react" {
     interface Session extends BetterAuthSession {
       jwt?: string;  // JWT token when JWT plugin is enabled
       user: {
         id: string;
         email: string;
         name?: string;
         image?: string;
         emailVerified: boolean;
       };
     }
   }
   ```

2. **ChatKit Types** (src/types/chatkit.d.ts):
   ```typescript
   declare module "@openai/chatkit-react" {
     export interface UseChatKitOptions {
       apiUrl: string;
       authToken?: string;
       onError?: (error: Error) => void;
       onResponseEnd?: (response: any) => void;
       onThreadChange?: (thread: any) => void;
     }

     export interface ChatKitControl {
       sendMessage: (message: string) => Promise<void>;
       // ... other control methods
     }

     export function useChatKit(options: UseChatKitOptions): ChatKitControl;
     export function ChatKit(props: { control: ChatKitControl; className?: string }): JSX.Element;
   }
   ```

**Decision**: Create type definition files in `phaseIII/frontend/src/types/` directory.

---

## Research Task 5: JWT Token Flow Between Frontend and Backend

**Unknown**: How should JWT tokens flow from Better Auth frontend to FastAPI backend?

### Research Findings

**Flow Architecture**:

```
1. User logs in via Better Auth (frontend)
   → POST /api/auth/sign-in/email
   → Better Auth creates session with JWT

2. Frontend requests JWT token
   → GET /api/auth/token (new endpoint)
   → Returns { token: "jwt..." }

3. Frontend stores token
   → useState hook or session storage

4. ChatKit initialized with token
   → useChatKit({ apiUrl, authToken: token })

5. ChatKit sends authenticated requests
   → Authorization: Bearer <token>
   → Backend validates via verify_jwt dependency

6. Backend validates token
   → jose.jwt.decode(token, secret, algorithms=["HS256"])
   → Extracts user_id from "sub" claim
   → Scopes database queries to user_id
```

**Token Endpoint Implementation** (/api/auth/token/route.ts):
```typescript
import { getAuth } from "@/lib/auth-server";

export async function GET(request: Request) {
  const auth = getAuth();
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  if (!session?.jwt) {
    return Response.json({ error: "No active session" }, { status: 401 });
  }

  return Response.json({ token: session.jwt });
}
```

**Decision**: Create `/api/auth/token` endpoint for explicit JWT retrieval.

---

## Research Task 6: Shared Secret Configuration

**Unknown**: How to ensure frontend and backend use the same Better Auth secret for JWT validation?

### Research Findings

**Shared Secret Requirement**: Both frontend Better Auth (issuer) and backend FastAPI (validator) must use the SAME secret key to sign and verify JWTs.

**Environment Variables**:
- Frontend: `BETTER_AUTH_SECRET`
- Backend: `BETTER_AUTH_SECRET` (same value via app.config.settings.better_auth_secret)

**Configuration Pattern**:

Frontend (.env.local):
```bash
BETTER_AUTH_SECRET=your-256-bit-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://...
```

Backend (.env):
```bash
BETTER_AUTH_SECRET=your-256-bit-secret-key-here  # MUST MATCH FRONTEND
DATABASE_URL=postgresql://...
```

**Decision**: Document shared secret requirement in quickstart.md and ensure both .env.example files reference the same secret variable name.

---

## Summary of Decisions

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Fix ChatKit useChatKit API usage | Remove `options` wrapper, pass params directly | Resolves TypeScript build error |
| Add Better Auth JWT plugin | Required for JWT token generation and access | Enables token retrieval in frontend |
| Create Better Auth database migration | Constitution requires explicit Alembic migrations | Adds 4 tables: user, session, account, verification |
| Create TypeScript type definitions | Resolves compilation errors and improves DX | Enables strict mode TypeScript compilation |
| Create /api/auth/token endpoint | Explicit endpoint for JWT retrieval | Simplifies token access in components |
| Document shared secret requirement | Prevents JWT validation failures | Ensures frontend-backend token compatibility |

---

## Next Steps (Phase 1)

With all unknowns resolved, proceed to Phase 1:

1. Generate `data-model.md` - Document Better Auth schema and relationships
2. Generate `contracts/auth-types.ts` - TypeScript type definitions
3. Generate `quickstart.md` - Setup instructions with shared secret configuration
4. Update agent context - Add Better Auth JWT plugin to technology stack

**All NEEDS CLARIFICATION items from Technical Context have been resolved.**
