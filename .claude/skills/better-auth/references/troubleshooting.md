# Troubleshooting Guide

Common issues and solutions for Better Auth integration.

## Installation Issues

### Package Installation Fails

**Error**: `npm ERR! Could not resolve dependency`

**Solutions**:
1. Clear package manager cache:
   ```bash
   # bun
   rm -rf node_modules bun.lockb && bun install

   # npm
   rm -rf node_modules package-lock.json && npm install

   # pnpm
   rm -rf node_modules pnpm-lock.yaml && pnpm install
   ```

2. Check Node.js version (requires 18+):
   ```bash
   node --version
   ```

3. Use exact Better Auth version:
   ```bash
   bun add better-auth@latest
   ```

### TypeScript Errors After Installation

**Error**: `Cannot find module 'better-auth'`

**Solutions**:
1. Restart TypeScript server in your editor
2. Regenerate `tsconfig.json`:
   ```bash
   npx tsc --init
   ```
3. Clear TypeScript cache:
   ```bash
   rm -rf .next node_modules/.cache
   ```

## Database Issues

### Tables Not Created

**Error**: `relation "user" does not exist`

**Solutions**:
1. Generate schema with Better Auth CLI:
   ```bash
   bun x @better-auth/cli generate
   ```

2. Run Drizzle migrations:
   ```bash
   drizzle-kit generate
   drizzle-kit migrate
   ```

3. Verify database connection:
   ```bash
   # Test DATABASE_URL
   psql $DATABASE_URL
   ```

### Migration Fails

**Error**: `Migration failed: duplicate column name`

**Solutions**:
1. Check existing schema:
   ```bash
   drizzle-kit introspect
   ```

2. Drop and recreate (development only):
   ```sql
   DROP TABLE IF EXISTS "user", "account", "session", "verification" CASCADE;
   ```

3. Create manual migration:
   ```bash
   drizzle-kit generate --custom
   ```

### Connection Pool Exhausted

**Error**: `remaining connection slots are reserved`

**Solutions**:
1. Reduce pool size:
   ```ts
   const pool = new Pool({
     connectionString: process.env.DATABASE_URL,
     max: 5, // Reduce from default 10
   });
   ```

2. Close connections properly:
   ```ts
   // Always use connection pooling
   await db.end(); // In app shutdown
   ```

3. Check Neon connection limits (free tier: 10 connections)

## Authentication Issues

### Session Not Persisting

**Error**: User logged in but session lost on refresh

**Solutions**:
1. Verify cookies are set:
   - Check browser DevTools → Application → Cookies
   - Look for `better-auth.session_token`

2. Check `sameSite` configuration:
   ```ts
   advanced: {
     sameSite: "lax", // Not "strict" (prevents navigation)
   }
   ```

3. Ensure HTTPS in production:
   ```ts
   advanced: {
     useSecureCookies: process.env.NODE_ENV === "production",
   }
   ```

4. Verify `trustedOrigins`:
   ```ts
   trustedOrigins: [
     process.env.BETTER_AUTH_URL!,
   ],
   ```

### Sign In Fails Silently

**Error**: No error but user not authenticated

**Solutions**:
1. Check password requirements:
   ```ts
   emailAndPassword: {
     minPasswordLength: 8, // Must match requirements
   }
   ```

2. Verify email/password are correct
3. Check rate limiting:
   ```ts
   rateLimit: {
     enabled: true,
     max: 10, // May be blocking requests
   }
   ```

4. Check console for errors:
   ```ts
   const result = await signIn.email({ email, password });
   console.log('Sign in result:', result);
   ```

### Email Verification Not Working

**Error**: Verification link doesn't work

**Solutions**:
1. Implement `sendVerificationEmail`:
   ```ts
   emailAndPassword: {
     sendVerificationEmail: async ({ user, url }) => {
       await sendEmail({
         to: user.email,
         html: `<a href="${url}">Verify</a>`,
       });
     },
   }
   ```

2. Check verification token expiry:
   ```ts
   emailAndPassword: {
     resetPasswordTokenExpiresIn: 3600, // 1 hour
   }
   ```

3. Verify URL configuration:
   ```env
   BETTER_AUTH_URL=http://localhost:3000 # Must be correct
   ```

## JWT Token Issues

### Token Validation Fails

**Error**: `Invalid token` or `JWT verification failed`

**Solutions**:
1. Verify secret matches:
   ```bash
   # Frontend .env.local
   BETTER_AUTH_SECRET=abc123...

   # Backend .env
   BETTER_AUTH_SECRET=abc123...  # MUST BE IDENTICAL
   ```

2. Check algorithm:
   ```ts
   // Frontend
   jwt.sign(payload, secret, { algorithm: 'HS256' });

   // Backend
   jwt.decode(token, secret, algorithms=["HS256"])
   ```

3. Validate token structure:
   ```ts
   const payload = jwt.decode(token);
   console.log('Payload:', payload);
   // Should have: sub, email, exp, iat
   ```

### Token Expired Immediately

**Error**: Token expires right after generation

**Solutions**:
1. Check expiration calculation:
   ```ts
   const now = Math.floor(Date.now() / 1000); // MUST be in seconds
   const exp = now + (30 * 60); // 30 minutes
   ```

2. Verify server time sync:
   ```bash
   date # Check system time
   ```

3. Check backend validation:
   ```python
   if exp < time.time():  # Current time in seconds
       raise Exception("Expired")
   ```

### Token Not Attached to Requests

**Error**: Backend returns 401, token not in headers

**Solutions**:
1. Verify interceptor runs:
   ```ts
   axios.interceptors.request.use(async (config) => {
     console.log('Interceptor running');
     // ...
   });
   ```

2. Check session exists:
   ```ts
   const session = await getSession();
   console.log('Session:', session);
   ```

3. Verify token cache:
   ```ts
   const token = await tokenCache.getToken(() => sessionCache.hasSession());
   console.log('Token:', token);
   ```

4. Check Authorization header:
   ```ts
   config.headers.Authorization = `Bearer ${token}`;
   console.log('Headers:', config.headers);
   ```

## CORS Issues

### Preflight Request Fails

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solutions**:
1. Add frontend to backend CORS:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. Add backend to Better Auth trusted origins:
   ```ts
   trustedOrigins: [
     "http://localhost:3000",
     "http://localhost:8000",
   ],
   ```

3. Include credentials in requests:
   ```ts
   axios.create({
     withCredentials: true,
   });
   ```

### Cookies Not Sent Cross-Origin

**Error**: Session cookie missing in requests

**Solutions**:
1. Use same domain for dev (e.g., localhost:3000 and localhost:8000)
2. Enable credentials:
   ```ts
   axios.create({
     withCredentials: true,
   });
   ```

3. Check `SameSite` setting:
   ```ts
   advanced: {
     sameSite: "lax", // Allows cross-origin GET
   }
   ```

## CLI Issues

### CLI Command Not Found

**Error**: `@better-auth/cli: command not found`

**Solutions**:
1. Use npx/bunx:
   ```bash
   bunx @better-auth/cli generate
   # or
   npx @better-auth/cli@latest generate
   ```

2. Install globally:
   ```bash
   bun add -g @better-auth/cli
   ```

### Generate Command Fails

**Error**: `Failed to generate schema`

**Solutions**:
1. Verify database connection:
   ```env
   DATABASE_URL=postgresql://...
   ```

2. Check Drizzle config exists:
   ```ts
   // drizzle.config.ts
   export default {
     schema: "./lib/db/schema.ts",
     out: "./drizzle",
   };
   ```

3. Run with verbose output:
   ```bash
   bunx @better-auth/cli generate --verbose
   ```

## Performance Issues

### Slow Token Generation

**Symptoms**: `/api/auth/token` takes >1s

**Solutions**:
1. Enable session caching:
   ```ts
   session: {
     cookieCache: {
       enabled: true,
       maxAge: 60 * 60 * 24, // 24 hours
     },
   }
   ```

2. Reduce database queries:
   ```ts
   // Use connection pooling
   const pool = new Pool({ max: 10 });
   ```

3. Cache JWT tokens on frontend (see `api-client.md`)

### High Database Load

**Symptoms**: Many session queries

**Solutions**:
1. Enable cookie cache (reduces DB queries):
   ```ts
   session: {
     cookieCache: { enabled: true },
   }
   ```

2. Increase session `updateAge`:
   ```ts
   session: {
     updateAge: 60 * 60 * 24, // Only update once per day
   }
   ```

3. Use connection pooling:
   ```ts
   const pool = new Pool({
     max: 10,
     idleTimeoutMillis: 30000,
   });
   ```

## Environment Variable Issues

### Secret Too Short

**Error**: `BETTER_AUTH_SECRET must be at least 32 characters`

**Solutions**:
1. Generate proper secret:
   ```bash
   openssl rand -base64 32
   ```

2. Update `.env.local`:
   ```env
   BETTER_AUTH_SECRET=<generated-secret>
   ```

3. Restart dev server:
   ```bash
   bun dev
   ```

### Environment Variables Not Loading

**Error**: `process.env.BETTER_AUTH_SECRET is undefined`

**Solutions**:
1. Check file name (`.env.local` for Next.js)
2. Restart dev server
3. Verify file location (project root)
4. Check variable prefix:
   ```env
   # Client-side (accessible in browser)
   NEXT_PUBLIC_API_URL=...

   # Server-side only
   BETTER_AUTH_SECRET=...
   ```

## Testing Issues

### Tests Fail with Auth

**Error**: `Unauthorized` in test environment

**Solutions**:
1. Mock Better Auth in tests:
   ```ts
   jest.mock('@/lib/auth', () => ({
     getSession: jest.fn().mockResolvedValue({
       user: { id: 'test-user', email: 'test@example.com' },
     }),
   }));
   ```

2. Use test secret:
   ```ts
   // jest.setup.ts
   process.env.BETTER_AUTH_SECRET = 'test-secret-key-min-32-chars-long';
   ```

3. Generate test tokens:
   ```ts
   const testToken = jwt.sign(
     { sub: 'test-user', email: 'test@example.com', exp: ... },
     'test-secret-key-min-32-chars-long'
   );
   ```

## Debugging Tips

### Enable Debug Logging

```ts
// Better Auth server
export const auth = betterAuth({
  // ... config
  logger: {
    disabled: false,
    verboseError: process.env.NODE_ENV === 'development',
  },
});
```

### Check Better Auth Endpoints

Test authentication endpoints directly:

```bash
# Get session
curl http://localhost:3000/api/auth/session \
  -H "Cookie: better-auth.session_token=..."

# Sign in
curl -X POST http://localhost:3000/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Verify JWT Token

Decode JWT to inspect claims:

```bash
# Using jwt.io CLI or online at https://jwt.io
echo "<token>" | jwt decode
```

## Getting Help

1. **Better Auth Discord**: https://discord.gg/better-auth
2. **GitHub Issues**: https://github.com/better-auth/better-auth/issues
3. **Documentation**: https://www.better-auth.com/docs
4. **Stack Overflow**: Tag questions with `better-auth`

## Next Steps

- Review security patterns (see `security-patterns.md`)
- Check JWT token flow (see `jwt-token-flow.md`)
- Verify FastAPI integration (see `fastapi-integration.md`)
