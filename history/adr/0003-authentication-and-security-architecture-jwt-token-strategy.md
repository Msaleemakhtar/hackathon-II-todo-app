# ADR-0003: Authentication and Security Architecture - JWT Token Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-09
- **Feature:** Foundational Backend Setup (001-foundational-backend-setup)
- **Context:** Phase II Todo App requires secure user authentication with stateless token management for API access. The Constitution mandates JWT-based authentication with backend-only token issuance. We needed to design an integrated security architecture covering token creation, storage, validation, refresh mechanism, password hashing, and rate limiting that balances security, user experience, and implementation complexity for Phase II MVP scope.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Defines security model and authentication flow for entire application
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - JWT HS256 vs RS256, session-based auth, token storage strategies, rate limiting approaches
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects all protected endpoints, frontend integration, security posture
-->

## Decision

We will implement an integrated JWT-based authentication and security architecture consisting of:

- **Token Strategy**: JSON Web Tokens (JWT) with dual-token approach
  - **Access Token**: 15-minute expiry, sent in response body, stored in memory by frontend
  - **Refresh Token**: 7-day expiry, sent in HttpOnly cookie, used only for token refresh
  - **Payload Structure**: `{sub: user_id, email, exp, iat, type: "access"|"refresh"}`

- **Token Algorithm**: HS256 (HMAC-SHA256) for Phase II
  - Symmetric key cryptography (same secret for signing and verification)
  - Secret key: 256 bits minimum (64 hex characters)
  - Validated at application startup
  - RS256 (asymmetric) planned for Phase III multi-service architecture

- **Token Issuance**: Backend-only via python-jose
  - Frontend MUST NOT create, sign, or generate JWTs
  - Backend authenticates credentials and issues tokens
  - Token creation in `core/security.py`

- **Token Storage**:
  - **Access Token**: Returned in JSON response body, frontend stores in memory (NOT localStorage)
  - **Refresh Token**: Set in HttpOnly, Secure, SameSite=Strict cookie
  - Cookie path restricted to `/api/v1/auth` to minimize exposure

- **Password Security**: passlib with bcrypt
  - Bcrypt algorithm with 12 rounds (balance of security and performance ~300ms)
  - Async wrapper using `asyncio.to_thread` to prevent event loop blocking
  - No plaintext passwords in database or logs

- **Rate Limiting**: slowapi with in-memory storage
  - 5 requests per minute per IP on authentication endpoints (register, login, refresh)
  - HTTP 429 on rate limit exceeded
  - In-memory storage sufficient for single-instance Phase II (Redis planned for Phase III)

- **Token Validation**: FastAPI dependency injection
  - `get_current_user()` dependency validates access tokens on protected endpoints
  - Extracts user_id from JWT payload for database queries
  - All queries scoped to authenticated user_id

- **Phase II Scope Boundaries** (explicitly OUT OF SCOPE):
  - Refresh token rotation on each use (Phase III)
  - Server-side token blacklisting for logout (Phase III)
  - Password reset functionality
  - Email verification
  - Multi-factor authentication

## Consequences

### Positive

- **Stateless Authentication**: No server-side session storage required; tokens contain all necessary claims; enables horizontal scaling
- **Security**: HttpOnly cookies prevent XSS attacks on refresh tokens; SameSite=Strict prevents CSRF; short-lived access tokens limit exposure from theft
- **User Experience**: Refresh token flow enables seamless token renewal without re-login every 15 minutes; 7-day refresh token balances security and convenience
- **Type Safety**: Token payload structure validated via Pydantic; python-jose integrates cleanly with FastAPI
- **Performance**: bcrypt with async wrapper prevents blocking; rate limiting protects against brute-force attacks without expensive infrastructure
- **Data Isolation**: User ID from JWT scopes all database queries; prevents unauthorized data access even with valid token
- **Constitution Compliance**: Backend-only JWT issuance, dual-token approach, HS256 algorithm, rate limiting all mandated by Constitution Section IV
- **Migration Path**: HS256 → RS256 upgrade path clear for Phase III; token structure supports additional claims (roles, permissions)

### Negative

- **Token Revocation Limitation**: No server-side blacklist means compromised tokens remain valid until expiry (15 min max for access, 7 days for refresh)
- **Logout Gaps**: Clearing refresh cookie doesn't invalidate access tokens; user could remain "logged in" for up to 15 minutes post-logout
- **Algorithm Tradeoff**: HS256 requires shared secret; multi-service architecture in Phase III will need RS256 migration
- **Rate Limiting Scope**: Per-IP limiting vulnerable to distributed attacks or shared IP scenarios (NAT, VPN); per-user limiting deferred to Phase III
- **Bcrypt Performance**: 12 rounds take ~300ms; intentionally slow to prevent brute-force but impacts login latency (acceptable for Phase II)
- **In-Memory Rate Limiter**: Lost on application restart; no distributed rate limiting across multiple instances (single-instance assumption for Phase II)
- **No MFA**: Single-factor authentication less secure than MFA; acceptable for Phase II MVP, critical for production

## Alternatives Considered

### Alternative A: Session-Based Authentication
- **Components**: Server-side sessions with Redis/database storage, session cookies
- **Pros**: Easy revocation (delete session), mature pattern, simpler frontend
- **Cons**:
  - Violates Constitution (mandates JWT)
  - Requires Redis or database for session storage (additional infrastructure)
  - Server-side state complicates horizontal scaling
  - No built-in expiry mechanism (manual cleanup required)
- **Why Rejected**: Constitution violation, stateful architecture conflicts with scalability goals

### Alternative B: JWT with RS256 (Asymmetric) from Phase II
- **Components**: RS256 algorithm, public/private key pair, same token strategy
- **Pros**: Public key can be shared with multiple services; private key remains secret; better for microservices
- **Cons**:
  - Overkill for single backend service in Phase II
  - Adds complexity of key pair management (storage, rotation)
  - Slower token verification than HS256 (asymmetric crypto overhead)
  - Premature optimization for future multi-service architecture
- **Why Rejected**: Unnecessary complexity for Phase II single-service scope; planned for Phase III

### Alternative C: Single Long-Lived Token (No Refresh)
- **Components**: JWT with 7-day expiry, no refresh mechanism, same HS256 algorithm
- **Pros**: Simpler implementation (one token type), less network requests
- **Cons**:
  - Violates Constitution (mandates dual-token approach)
  - Security risk: compromised token valid for 7 days
  - Forces re-login every 7 days even for active users (poor UX)
  - No granular control over access token expiry
- **Why Rejected**: Constitution violation, poor security/UX tradeoff

### Alternative D: OAuth 2.0 + Better Auth Integration
- **Components**: Better Auth library, OAuth 2.0 flows, third-party provider integration
- **Pros**: Social login (Google, GitHub), email verification, MFA built-in
- **Cons**:
  - Violates Constitution (Phase II scope: backend implements JWT auth)
  - Adds dependency on third-party services
  - More complex implementation (OAuth flows, provider setup)
  - Frontend Better Auth library does NOT issue JWTs (Constitution violation if frontend creates tokens)
- **Why Rejected**: Constitution mandates backend-only JWT issuance; Better Auth frontend usage would violate this; deferred to future phase

### Alternative E: Custom Rate Limiting Middleware
- **Components**: FastAPI middleware with in-memory counter, IP-based limiting
- **Pros**: Full control over implementation, no external dependency
- **Cons**:
  - Reinventing the wheel (slowapi is battle-tested)
  - More code to maintain and test
  - Likely to miss edge cases (slowapi handles concurrent requests, cleanup, etc.)
- **Why Rejected**: slowapi provides proven solution; custom implementation offers no benefits for Phase II

## References

- Feature Spec: [specs/001-foundational-backend-setup/spec.md](../../specs/001-foundational-backend-setup/spec.md) (Section 4: API Endpoint Requirements, Section 5: Non-Functional & Security Requirements)
- Implementation Plan: [specs/001-foundational-backend-setup/plan.md](../../specs/001-foundational-backend-setup/plan.md)
- Research Findings:
  - [JWT Implementation](../../specs/001-foundational-backend-setup/research.md#2-jwt-implementation-with-python-jose)
  - [Password Hashing](../../specs/001-foundational-backend-setup/research.md#3-password-hashing-with-passlibrbcrypt)
  - [Rate Limiting](../../specs/001-foundational-backend-setup/research.md#5-fastapi-rate-limiting)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (Section IV: User Authentication & JWT Security)
- Related ADRs: ADR-0002 (Backend Technology Stack)
- JWT Best Practices: https://tools.ietf.org/html/rfc8725
- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
