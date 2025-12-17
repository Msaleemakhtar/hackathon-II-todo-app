# JWT Token Flow - Hybrid Authentication Architecture

Complete guide for implementing JWT tokens with Better Auth for full-stack Next.js + FastAPI applications.

## Why Hybrid Authentication?

Better Auth manages sessions via httpOnly cookies for the Next.js frontend. However, when calling a separate FastAPI backend, we need JWT tokens for stateless authentication.

**Architecture Pattern**:
- **Frontend → Better Auth**: Cookie-based sessions
- **Frontend → Backend API**: JWT token authentication
- **Backend**: Validates JWT tokens, no session state

This hybrid approach provides:
- Secure session management (httpOnly cookies prevent XSS)
- Stateless backend (JWT tokens enable horizontal scaling)
- Shared secret validation (same `BETTER_AUTH_SECRET`)

## Complete Authentication Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js App   │     │   Better Auth   │     │  FastAPI Backend│
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                        │
    1. User Login               │                        │
    ├──────────────────────────►│                        │
         │                  Creates Session              │
         │                  Sets httpOnly Cookie         │
    2. Login Success           │                        │
    ◄──────────────────────────┤                        │
         │                       │                        │
    3. API Request             │                        │
         │    Check Session     │                        │
    ├──────────────────────────►│                        │
    4. Session Valid           │                        │
    ◄──────────────────────────┤                        │
         │                       │                        │
    5. Get JWT Token           │                        │
    ├────────────────────┐      │                        │
    │ /api/auth/token    │      │                        │
    │ Verify Session     │      │                        │
    │ Generate JWT       │      │                        │
    │ Sign with Secret   │      │                        │
    └────────────────────┤      │                        │
    6. JWT Token              │                        │
    ◄──────────────────────────┤                        │
         │                       │                        │
    7. Call Backend API        │                        │
    │ Authorization: Bearer <JWT>                      │
    ├────────────────────────────────────────────────►│
         │                       │        Verify JWT    │
         │                       │        Extract Claims│
         │                       │        Validate Expiry│
    8. API Response            │                        │
    ◄──────────────────────────────────────────────────┤
         │                       │                        │
```

## JWT Token Structure

Better Auth sessions contain user data. We extract this to generate JWTs for the backend:

```json
{
  "sub": "<user_id>",
  "email": "<user_email>",
  "name": "<user_name>",
  "exp": <expiration_timestamp>,
  "iat": <issued_at_timestamp>,
  "type": "access"
}
```

**JWT Claims**:
- `sub` (Subject): User ID from Better Auth session
- `email`: User's email address
- `name`: User's display name
- `exp` (Expiration): Token expiry time (typically 30 minutes)
- `iat` (Issued At): Token creation time
- `type`: Token type identifier

## Implementation

### 1. JWT Token Generation Endpoint

Create `app/api/auth/token/route.ts`:

```ts
import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth-server';
import jwt from 'jsonwebtoken';

export async function GET(request: NextRequest) {
  try {
    // Verify Better Auth session
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session || !session.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Validate environment
    const secret = process.env.BETTER_AUTH_SECRET;
    if (!secret || secret.length < 32) {
      throw new Error('BETTER_AUTH_SECRET must be at least 32 characters');
    }

    // Token expiration (30 minutes)
    const expiresIn = 30 * 60; // seconds
    const now = Math.floor(Date.now() / 1000);
    const exp = now + expiresIn;

    // Create JWT payload
    const payload = {
      sub: session.user.id,
      email: session.user.email,
      name: session.user.name,
      exp,
      iat: now,
      type: 'access',
    };

    // Sign JWT with Better Auth secret
    const token = jwt.sign(payload, secret, {
      algorithm: 'HS256',
    });

    return NextResponse.json({
      token,
      expiresAt: exp * 1000, // Convert to milliseconds
      user: {
        id: session.user.id,
        email: session.user.email,
        name: session.user.name,
      },
    });
  } catch (error) {
    console.error('Token generation error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

**Dependencies**:
```bash
bun add jsonwebtoken
bun add -d @types/jsonwebtoken
```

### 2. Token Caching Strategy

Implement token caching to minimize token generation requests:

```ts
// lib/token-cache.ts
interface CachedToken {
  token: string;
  expiresAt: number;
}

class TokenCache {
  private cache: CachedToken | null = null;
  private fetchPromise: Promise<string> | null = null;

  async getToken(sessionCheck: () => Promise<boolean>): Promise<string | null> {
    // Check if we have a valid cached token
    if (this.cache && this.isTokenValid(this.cache.expiresAt)) {
      return this.cache.token;
    }

    // Prevent duplicate fetches
    if (this.fetchPromise) {
      return this.fetchPromise;
    }

    // Verify session exists
    const hasSession = await sessionCheck();
    if (!hasSession) {
      this.clear();
      return null;
    }

    // Fetch new token
    this.fetchPromise = this.fetchNewToken();

    try {
      const token = await this.fetchPromise;
      return token;
    } finally {
      this.fetchPromise = null;
    }
  }

  private async fetchNewToken(): Promise<string> {
    const response = await fetch('/api/auth/token');

    if (!response.ok) {
      throw new Error('Failed to fetch token');
    }

    const data = await response.json();

    // Cache token with 3-minute buffer before expiry
    this.cache = {
      token: data.token,
      expiresAt: data.expiresAt,
    };

    return data.token;
  }

  private isTokenValid(expiresAt: number): boolean {
    // 3-minute buffer (180000ms)
    return Date.now() + 180000 < expiresAt;
  }

  clear() {
    this.cache = null;
    this.fetchPromise = null;
  }
}

export const tokenCache = new TokenCache();
```

**Caching Benefits**:
- Reduces API calls (token fetched once per 27 minutes)
- Prevents duplicate requests (promise chaining)
- Automatic refresh before expiry (3-minute buffer)
- Memory-only storage (no localStorage for security)

### 3. Token Validation (Backend)

See `fastapi-integration.md` for complete FastAPI validation implementation.

Brief overview:

```python
# FastAPI backend validation
from jose import jwt, JWTError
from fastapi import HTTPException, Header

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

async def verify_token(authorization: str = Header(...)):
    try:
        # Extract token from "Bearer <token>"
        token = authorization.replace("Bearer ", "")

        # Decode and verify JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Validate expiration
        exp = payload.get("exp")
        if exp and exp < time.time():
            raise HTTPException(status_code=401, detail="Token expired")

        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## Token Refresh Flow

When a token expires (401 response), automatically refresh:

```ts
// In axios interceptor (see api-client.md)
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Clear cached token
      tokenCache.clear();

      // Try to get fresh token
      const newToken = await tokenCache.getToken(checkSession);

      if (newToken) {
        // Retry original request with new token
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return axiosInstance(error.config);
      }

      // No session, redirect to login
      signOut();
      window.location.href = '/login?session_expired=true';
    }

    return Promise.reject(error);
  }
);
```

## Security Considerations

### 1. Token Lifetime

**Recommended**: 15-30 minutes

- Too short: Frequent refreshes, poor UX
- Too long: Security risk if token stolen

**Validation** (Backend):
```python
# Ensure token lifetime is reasonable
issued_at = payload.get("iat")
expires_at = payload.get("exp")

if expires_at - issued_at > 1800:  # 30 minutes
    raise HTTPException(status_code=401, detail="Invalid token lifetime")

if expires_at - issued_at < 900:  # 15 minutes
    raise HTTPException(status_code=401, detail="Invalid token lifetime")
```

### 2. Shared Secret

**Requirements**:
- Same `BETTER_AUTH_SECRET` in frontend and backend
- Minimum 32 characters
- High entropy (use `openssl rand -base64 32`)
- Never commit to version control

**Validation**:
```ts
if (!process.env.BETTER_AUTH_SECRET || process.env.BETTER_AUTH_SECRET.length < 32) {
  throw new Error('BETTER_AUTH_SECRET must be at least 32 characters');
}
```

### 3. Token Storage

**DO**:
- Store tokens in memory only (JavaScript variables)
- Cache with automatic expiry
- Clear on sign out

**DON'T**:
- Store in localStorage (XSS vulnerability)
- Store in sessionStorage (XSS vulnerability)
- Include tokens in URL parameters

### 4. HTTPS Only

In production, enforce HTTPS for all token transmission:

```ts
if (process.env.NODE_ENV === 'production' && !request.url.startsWith('https://')) {
  throw new Error('Tokens must be transmitted over HTTPS');
}
```

## Best Practices

1. **Validate Session Before Token Generation**
   - Always verify Better Auth session exists
   - Check session hasn't expired
   - Validate user still exists in database

2. **Cache Tokens Appropriately**
   - Use 3-minute buffer before expiry
   - Clear cache on sign out
   - Prevent duplicate fetch requests

3. **Handle Errors Gracefully**
   - 401: Clear cache, try refresh, redirect to login
   - 500: Show error, don't retry automatically
   - Network errors: Retry with exponential backoff

4. **Monitor Token Usage**
   - Log token generation (not token value)
   - Track token expiry and refresh rates
   - Alert on unusual patterns

5. **Synchronize Secrets**
   - Same `BETTER_AUTH_SECRET` across environments
   - Rotate secrets periodically
   - Update in all services simultaneously

## Troubleshooting

### Token Validation Fails

**Symptoms**: Backend returns 401 even with valid session

**Solutions**:
1. Verify `BETTER_AUTH_SECRET` matches frontend and backend
2. Check token hasn't expired (`exp` claim)
3. Ensure algorithm is HS256
4. Validate token structure (all required claims present)

### Token Refresh Loop

**Symptoms**: Continuous token generation requests

**Solutions**:
1. Check token caching logic
2. Verify expiry buffer calculation (should be < expiry time)
3. Ensure `fetchPromise` is cleared after fetch
4. Check session validation isn't failing repeatedly

### CORS Issues

**Symptoms**: Token endpoint returns CORS errors

**Solutions**:
1. Add frontend origin to `trustedOrigins` in Better Auth config
2. Configure CORS headers in Next.js API route
3. Ensure credentials are included in fetch requests

## Next Steps

- Implement API client with interceptors (see `api-client.md`)
- Set up FastAPI JWT validation (see `fastapi-integration.md`)
- Review security best practices (see `security-patterns.md`)
