# ADR-0008: API Security and Validation Strategy - JWT Validation and Path Parameter Security

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-10
- **Feature:** 004-better-auth-integration
- **Context:** The Phase II Todo App requires a robust security validation strategy for API endpoints that work with the Better Auth integration. This involves validating JWT tokens issued by Better Auth using a shared secret, implementing path parameter validation to ensure user_id in the URL matches the authenticated user, and ensuring that all API requests are properly authenticated and authorized. This decision cluster encompasses the security validation mechanisms across the entire API surface.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - This affects security validation across all API endpoints
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Different validation approaches, security models
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects all API endpoints and security posture
-->

## Decision

We will implement an integrated API security and validation strategy consisting of:

- **JWT Token Validation**: Using python-jose library to validate Better Auth JWT tokens against shared secret
  - FastAPI dependency injection for token validation on protected endpoints
  - Extract user_id from JWT payload for authentication context
  - Proper error handling for invalid, expired, or malformed tokens

- **Path Parameter Validation**: Strict validation that URL user_id matches JWT user_id
  - Middleware or dependency to validate path parameter against JWT claims
  - Immediate rejection of requests where path user_id doesn't match JWT user_id
  - Prevention of URL manipulation attacks to access other users' data

- **Request Authentication**: All user-specific endpoints require valid JWT tokens
  - Proper Authorization header format: "Bearer <better_auth_jwt_token>"
  - Content-Type requirement: application/json for API requests
  - Standardized error responses for unauthenticated requests

- **Rate Limiting**: Implementation on authentication endpoints
  - 5 attempts per minute per IP on auth endpoints
  - Using slowapi or similar library for rate limiting
  - Protection against brute-force attacks on authentication

## Consequences

### Positive

- **Enhanced Security**: Multiple validation layers ensure only authenticated and authorized requests are processed; prevents unauthorized data access through URL manipulation
- **Consistent Validation**: Centralized validation logic using FastAPI dependencies ensures all endpoints follow the same security pattern
- **Compliance**: Meets security requirements specified in the constitution and feature specifications
- **Performance**: Efficient validation with minimal overhead; JWT validation using optimized libraries
- **Maintainability**: Standardized security patterns make code easier to maintain and audit
- **Attack Prevention**: Rate limiting protects against brute-force attacks; path validation prevents user impersonation attempts
- **Audit Trail**: Security validation can be easily logged for audit and monitoring purposes

### Negative

- **Performance Overhead**: JWT validation adds a small amount of latency to each request; though optimized, it's still additional processing
- **Complexity**: Multiple validation layers increase code complexity and potentially debugging difficulty
- **Dependency Risk**: Using external libraries for JWT validation introduces potential security risks if the libraries have vulnerabilities
- **Token Management**: Need to handle token expiration and refresh correctly, adding complexity to client-side logic
- **Development Overhead**: Developers must remember to apply security validations to new endpoints

## Alternatives Considered

### Alternative A: Minimal Token Validation (Only Token Presence)
- **Components**: Check that Authorization header contains a token without validating its contents or signature
- **Pros**: Simpler implementation, faster processing, fewer dependencies
- **Cons**: Offers no real security; tokens could be forged, manipulated, or invalid; completely vulnerable to attacks
- **Why Rejected**: Would provide no actual security; violates basic security principles and constitution requirements

### Alternative B: Session-Based Validation (Server-Side Sessions)
- **Components**: Store JWT tokens or user sessions on the server, validate against server-side session store
- **Pros**: Allows for server-side token revocation, more control over sessions, ability to track active sessions
- **Cons**: Violates constitution requirement for JWT-based authentication; introduces server-side state; more complex infrastructure; doesn't scale as well as stateless JWTs
- **Why Rejected**: Constitution specifically mandates stateless JWT validation; this approach is explicitly against project requirements

### Alternative C: Alternative Token Validation (Different Algorithm/Library)
- **Components**: Use different JWT validation library, or different cryptographic algorithm (RS256 instead of HS256)
- **Pros**: Potentially different performance characteristics or security model
- **Cons**: python-jose is the standard library for JWT in Python; different algorithm would require more complex key management; unnecessary complexity for single-service architecture
- **Why Rejected**: python-jose with HS256 is established in ADR-0003 and meets our requirements; no compelling advantage to switch

### Alternative D: Path Validation with Additional Checks (Extended Validation)
- **Components**: Token validation plus additional user context validation, database lookup of user status, etc.
- **Pros**: More comprehensive validation, prevents access for suspended or invalid users
- **Cons**: Additional database calls increase latency; more complex implementation; may cause performance issues; potential single points of failure
- **Why Rejected**: Would add unnecessary performance overhead; JWT-based validation with path validation provides adequate security for our use case

## References

- Feature Spec: specs/004-better-auth-integration/spec.md
- Implementation Plan: specs/004-better-auth-integration/plan.md
- Related ADRs: ADR-0003 (Authentication and Security Architecture - JWT Token Strategy)
- Research Findings: specs/004-better-auth-integration/research.md
- Data Model: specs/004-better-auth-integration/data-model.md
- Evaluator Evidence: N/A
