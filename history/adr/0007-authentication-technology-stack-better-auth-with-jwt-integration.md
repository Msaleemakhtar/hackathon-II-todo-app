# ADR-0007: Authentication Technology Stack - Better Auth with JWT Integration

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-10
- **Feature:** 004-better-auth-integration
- **Context:** The Phase II Todo App requires a standardized authentication solution that replaces the existing custom authentication system. We need to integrate Better Auth to provide consistent JWT-based authentication between the Next.js frontend and FastAPI backend. This decision cluster encompasses the technology choices for authentication, including the Better Auth library, JWT token strategy, and API client implementation for secure communication.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - This affects the entire authentication system and security model
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Better Auth vs custom auth vs other auth libraries
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects all protected endpoints, frontend integration, and overall security posture
-->

## Decision

We will implement an integrated authentication technology stack consisting of:

- **Frontend Authentication**: Better Auth library for Next.js integration
  - `better-auth` for core authentication functionality
  - `better-auth-react` for React-specific components
  - JWT plugin for issuing compatible tokens that the backend can validate
  - Session management with cross-tab support enabled

- **JWT Token Strategy**: Better Auth JWT tokens with shared secret validation
  - Access tokens issued by Better Auth JWT plugin
  - Shared BETTER_AUTH_SECRET between frontend and backend
  - Token validation using python-jose library in FastAPI backend
  - User_id, email, and expiration time in token payload

- **API Client Integration**: Centralized API client at `@/lib/api-client`
  - Axios for HTTP requests with interceptors to attach Better Auth JWT tokens
  - Automatic token management and error handling
  - Proper URL construction for user-specific endpoints

- **Frontend Components**: Integration with Next.js App Router
  - Client-side session state management
  - Redirects and authentication flow handling
  - Secure token storage and retrieval

## Consequences

### Positive

- **Standardized Implementation**: Better Auth provides a well-maintained, battle-tested authentication solution with consistent behavior across different deployment environments
- **Reduced Development Time**: Less custom code to implement and maintain; focus shifts to business logic rather than authentication infrastructure
- **Security**: Better Auth follows security best practices and is regularly updated for security vulnerabilities
- **Cross-Tab Session Sharing**: Better Auth handles session sharing across browser tabs, providing consistent user experience
- **JWT Compatibility**: Better Auth's JWT plugin allows seamless integration with the existing FastAPI backend using shared secret validation
- **Type Safety**: Better Auth provides TypeScript definitions, improving development experience and catching errors at compile time
- **Community Support**: Better Auth has active community and documentation, making debugging and troubleshooting easier

### Negative

- **External Dependency**: Introducing another external dependency increases the attack surface and creates dependency on a third-party library
- **Vendor Lock-in Potential**: Tightly coupling to Better Auth may make future authentication provider changes more difficult
- **Limited Customization**: Some specific authentication flows may be harder to customize compared to a fully custom solution
- **Additional Abstraction Layer**: Extra layer between application and authentication logic, potentially making debugging more complex
- **Learning Curve**: Team needs to learn Better Auth's specific APIs and patterns

## Alternatives Considered

### Alternative A: Continue with Custom Authentication Implementation
- **Components**: Maintain existing custom JWT implementation, implement token validation without Better Auth
- **Pros**: Complete control over authentication flow, no external dependencies, custom implementation tailored to exact needs
- **Cons**: More development work, security maintenance burden, potential for security vulnerabilities, no built-in cross-tab session sharing
- **Why Rejected**: Constitution and feature requirements specifically call for Better Auth integration; custom solution doesn't meet current project requirements

### Alternative B: Use Alternative Authentication Library (e.g., Next-Auth)
- **Components**: NextAuth.js for Next.js authentication, different JWT strategy
- **Pros**: Popular, well-documented, good Next.js integration
- **Cons**: Would require different JWT validation approach on the backend, potential inconsistencies with Better Auth's approach, different API patterns to learn
- **Why Rejected**: Feature requirements specifically mandate Better Auth usage; Better Auth was selected as it provides better integration with the existing tech stack

### Alternative C: Use External Authentication Provider (e.g., Auth0, Firebase Auth)
- **Components**: Cloud authentication service, API-based authentication
- **Pros**: Minimal code to implement, handles edge cases, provides additional features like social logins
- **Cons**: Vendor lock-in, potential additional costs, less control over user data, requires external API calls
- **Why Rejected**: Constitution mandates backend-based authentication with JWT tokens; external providers conflict with data ownership requirements

### Alternative D: Hybrid Approach (Custom Frontend + Better Auth Backend)
- **Components**: Custom Next.js authentication components with direct API calls, Better Auth backend services
- **Pros**: More control over UI/UX, potentially better performance with fewer dependencies
- **Cons**: Loses the benefit of Better Auth's frontend ecosystem, still requires backend integration work
- **Why Rejected**: Would lose the benefits of Better Auth's integrated approach and create an inconsistent architecture

## References

- Feature Spec: specs/004-better-auth-integration/spec.md
- Implementation Plan: specs/004-better-auth-integration/plan.md
- Related ADRs: ADR-0003 (Authentication and Security Architecture - JWT Token Strategy)
- Research Findings: specs/004-better-auth-integration/research.md
- Data Model: specs/004-better-auth-integration/data-model.md
- Evaluator Evidence: N/A
