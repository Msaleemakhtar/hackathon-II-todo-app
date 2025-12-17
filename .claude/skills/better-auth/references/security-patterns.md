# Security Patterns & Best Practices

Comprehensive security guide for Better Auth implementation.

## Official Documentation

- **Better Auth Security**: https://www.better-auth.com/docs/concepts/security
- **Session Management**: https://www.better-auth.com/docs/concepts/session

## Session Security

### HttpOnly Cookies

Better Auth uses httpOnly cookies to prevent XSS attacks:

```ts
// Configured automatically by Better Auth
advanced: {
  useSecureCookies: process.env.NODE_ENV === "production",
}
```

**Benefits**:
- JavaScript cannot access session cookies
- Prevents XSS-based session theft
- Automatic CSRF protection

### Secure Cookie Flags

Production configuration:

```ts
advanced: {
  cookiePrefix: "better-auth",
  useSecureCookies: true, // HTTPS only
  sameSite: "lax", // CSRF protection
}
```

**Cookie Attributes**:
- `Secure`: Only transmitted over HTTPS
- `HttpOnly`: Not accessible via JavaScript
- `SameSite=Lax`: Prevents CSRF attacks

## Password Security

### Hashing

Better Auth uses `scrypt` by default:

```ts
// Default configuration (secure)
emailAndPassword: {
  enabled: true,
  // scrypt hashing is automatic
}
```

**Scrypt Benefits**:
- Memory-intensive (prevents GPU attacks)
- Configurable work factor
- Industry standard for password hashing

### Password Requirements

```ts
emailAndPassword: {
  enabled: true,
  minPasswordLength: 8,
  maxPasswordLength: 128,
}
```

**Best Practices**:
- Minimum 8 characters (12+ recommended)
- Maximum 128 characters (prevents DoS)
- No maximum complexity requirements (length is key)

## Rate Limiting

### Built-in Rate Limiting

```ts
rateLimit: {
  enabled: true,
  window: 60, // 1 minute window
  max: 10, // 10 requests per window
}
```

**Protects Against**:
- Brute force attacks
- Password spraying
- Token enumeration
- API abuse

### Custom Rate Limiting

For more granular control:

```ts
rateLimit: {
  enabled: true,
  window: 60,
  max: 10,
  storage: customStorage, // Redis, etc.
}
```

## JWT Security

### Token Configuration

```ts
// Token generation (frontend)
const payload = {
  sub: userId,
  email: userEmail,
  exp: Math.floor(Date.now() / 1000) + (30 * 60), // 30 minutes
  iat: Math.floor(Date.now() / 1000),
};

const token = jwt.sign(payload, SECRET_KEY, {
  algorithm: 'HS256', // Secure symmetric encryption
});
```

**Security Requirements**:
- HS256 algorithm (secure and fast)
- Secret minimum 32 characters
- Token lifetime 15-30 minutes
- Include `exp` and `iat` claims

### Token Storage

**DO**:
- ✅ Store in memory (JavaScript variables)
- ✅ Use with automatic expiry
- ✅ Clear on sign out

**DON'T**:
- ❌ Store in localStorage (XSS risk)
- ❌ Store in sessionStorage (XSS risk)
- ❌ Include in URL parameters (logging risk)
- ❌ Store in cookies without httpOnly

### Secret Management

```env
# Generate secure secret
openssl rand -base64 32

# Environment variables
BETTER_AUTH_SECRET=<generated-secret>
```

**Best Practices**:
- Minimum 32 characters
- High entropy (cryptographically random)
- Same secret across frontend/backend
- Never commit to version control
- Rotate periodically (e.g., quarterly)

## Multi-User Data Isolation

### Three-Layer Security Model

**Layer 1: JWT Authentication**
```python
# Validate token signature and expiration
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

**Layer 2: Path Validation**
```python
# Ensure path user_id matches JWT user_id
if path_user_id != payload["sub"]:
    raise HTTPException(status_code=403)
```

**Layer 3: Query Filtering**
```python
# Scope all queries to authenticated user
tasks = db.query(Task).filter(Task.user_id == payload["sub"])
```

### Never Trust Path Parameters

```python
# ❌ BAD: Using path parameter for queries
@router.get("/{user_id}/tasks")
async def get_tasks(user_id: str):
    tasks = db.query(Task).filter(Task.user_id == user_id)  # VULNERABLE!

# ✅ GOOD: Using JWT user_id
@router.get("/{user_id}/tasks")
async def get_tasks(user_id: str, request: Request):
    payload = await validate_path_user_id(request, user_id)
    jwt_user_id = payload["sub"]  # Authoritative source
    tasks = db.query(Task).filter(Task.user_id == jwt_user_id)
```

## CORS Configuration

### Development

```ts
trustedOrigins: [
  "http://localhost:3000",
  "http://localhost:8000",
]
```

### Production

```ts
trustedOrigins: [
  process.env.FRONTEND_URL,
  process.env.API_URL,
]
```

**FastAPI CORS**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL"),
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Email Verification

### Enable Email Verification

```ts
emailAndPassword: {
  enabled: true,
  requireEmailVerification: true,
  sendVerificationEmail: async ({ user, url }) => {
    // Send email with verification link
    await sendEmail({
      to: user.email,
      subject: "Verify your email",
      html: `Click <a href="${url}">here</a> to verify`,
    });
  },
}
```

**Security Benefits**:
- Confirms email ownership
- Prevents fake registrations
- Enables password recovery

## SQL Injection Prevention

### Use ORM Parameterization

```python
# ✅ GOOD: SQLModel/SQLAlchemy parameterization
from sqlmodel import select

result = await session.execute(
    select(Task).where(Task.user_id == user_id)
)
```

```python
# ❌ BAD: String concatenation
query = f"SELECT * FROM tasks WHERE user_id = '{user_id}'"  # VULNERABLE!
```

**Better Auth Protection**:
- Uses parameterized queries
- ORM adapter handles escaping
- No raw SQL in core operations

## XSS Prevention

### Frontend

```tsx
// ✅ React automatically escapes
<div>{user.name}</div>

// ❌ Dangerous: dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: userInput }} />
```

### Backend

```python
# Pydantic models validate and sanitize
class TaskCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str | None = Field(None, max_length=1000)
```

## CSRF Protection

Better Auth includes automatic CSRF protection:

```ts
// SameSite cookie attribute
advanced: {
  sameSite: "lax",
}
```

**How it Works**:
- Session cookies have `SameSite=Lax`
- Cross-site requests don't include cookies
- Only same-site requests authenticated

## Session Management

### Session Expiration

```ts
session: {
  expiresIn: 60 * 60 * 24 * 7, // 7 days
  updateAge: 60 * 60 * 24, // Refresh every 24 hours
}
```

**Behavior**:
- Sessions expire after 7 days of inactivity
- Active sessions refresh timestamp every 24 hours
- No sliding expiration after 7 days

### Session Revocation

```ts
// Sign out (revokes session)
await signOut();
```

**Cleanup**:
- Deletes session from database
- Clears session cookie
- Token cache cleared on frontend

## Monitoring & Logging

### Security Events to Log

```python
# Login attempts
logger.info(f"Login attempt: {email}")

# Failed authentication
logger.warning(f"Failed auth: {email} - {reason}")

# Token validation failures
logger.warning(f"Invalid token: {error}")

# User ID mismatches
logger.error(f"Path validation failed: {path_id} != {jwt_id}")
```

### Alerts

Set up alerts for:
- Multiple failed login attempts
- Token validation failures spike
- Unusual geographic access
- After-hours API access

## Security Checklist

**Environment**:
- [ ] `BETTER_AUTH_SECRET` is 32+ characters
- [ ] Same secret in frontend and backend
- [ ] Secrets not committed to version control
- [ ] HTTPS enforced in production

**Authentication**:
- [ ] Password minimum length: 8+ characters
- [ ] Email verification enabled
- [ ] Rate limiting configured (10 req/min)
- [ ] HttpOnly cookies enabled

**JWT Tokens**:
- [ ] HS256 algorithm
- [ ] 15-30 minute expiration
- [ ] Tokens stored in memory only
- [ ] Token validation on backend

**Authorization**:
- [ ] Path user_id validated against JWT
- [ ] All queries scoped to JWT user_id
- [ ] Multi-user isolation tests pass
- [ ] 403 returned for user_id mismatch

**Data Protection**:
- [ ] ORM parameterization (no raw SQL)
- [ ] Input validation with Pydantic
- [ ] Output encoding in React
- [ ] CORS properly configured

**Monitoring**:
- [ ] Security events logged
- [ ] Failed auth alerts configured
- [ ] Token failures monitored
- [ ] Unusual patterns detected

## Common Vulnerabilities to Avoid

### 1. Path Parameter Trust

```python
# ❌ VULNERABLE
@router.get("/{user_id}/tasks")
async def get_tasks(user_id: str):
    # User can access any user_id!
    return get_user_tasks(user_id)

# ✅ SECURE
@router.get("/{user_id}/tasks")
async def get_tasks(user_id: str, request: Request):
    payload = await validate_path_user_id(request, user_id)
    return get_user_tasks(payload["sub"])
```

### 2. Token in localStorage

```ts
// ❌ VULNERABLE to XSS
localStorage.setItem('token', jwtToken);

// ✅ SECURE: Memory only
let cachedToken: string | null = null;
```

### 3. Missing Rate Limiting

```ts
// ❌ VULNERABLE to brute force
rateLimit: {
  enabled: false,
}

// ✅ SECURE
rateLimit: {
  enabled: true,
  window: 60,
  max: 10,
}
```

### 4. Weak Secrets

```env
# ❌ WEAK
BETTER_AUTH_SECRET=secret123

# ✅ STRONG (32+ chars, high entropy)
BETTER_AUTH_SECRET=<openssl-rand-base64-32-output>
```

## Security Resources

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **JWT Best Practices**: https://tools.ietf.org/html/rfc8725
- **Better Auth Security**: https://www.better-auth.com/docs/concepts/security

## Next Steps

- Review JWT token flow (see `jwt-token-flow.md`)
- Implement FastAPI validation (see `fastapi-integration.md`)
- Set up monitoring and alerts
