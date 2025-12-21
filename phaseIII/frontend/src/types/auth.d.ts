/**
 * Type Definitions for Better Auth and ChatKit Integration
 *
 * This file provides TypeScript type definitions to resolve compilation errors
 * in the Phase III frontend. These types are based on research findings from
 * Better Auth and @openai/chatkit-react package documentation.
 *
 * Location: phaseIII/frontend/src/types/
 */

// ============================================================================
// Better Auth Types
// ============================================================================

/**
 * Better Auth User Entity
 *
 * Represents a user from the Better Auth user table.
 * Maps to the database schema defined in data-model.md.
 */
export interface BetterAuthUser {
  id: string;
  email: string;
  emailVerified: boolean;
  name?: string;
  image?: string;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Better Auth Session (Extended with JWT Plugin)
 *
 * Session object returned by Better Auth when JWT plugin is enabled.
 * The jwt field is added by the JWT plugin configuration.
 */
export interface BetterAuthSession {
  user: BetterAuthUser;
  session: {
    id: string;
    userId: string;
    expiresAt: Date;
    token: string;
    ipAddress?: string;
    userAgent?: string;
    createdAt: Date;
    updatedAt: Date;
  };
  jwt?: string; // Added by JWT plugin
}

/**
 * Extended Session Type for React Hooks
 *
 * This module augmentation extends the Session type returned by
 * useSession() hook to include the JWT token field.
 *
 * Usage in components:
 * ```typescript
 * const { data: session } = useSession();
 * const token = session?.jwt; // TypeScript now knows jwt exists
 * ```
 */
declare module "better-auth/react" {
  interface Session {
    user: BetterAuthUser;
    jwt?: string; // JWT token when JWT plugin is enabled
  }
}


// ============================================================================
// API Response Types
// ============================================================================

/**
 * JWT Token Response
 *
 * Response from /api/auth/token endpoint.
 */
export interface JwtTokenResponse {
  token: string;
}

/**
 * Auth Error Response
 *
 * Standard error response from auth endpoints.
 */
export interface AuthErrorResponse {
  error: string;
  message?: string;
}

// ============================================================================
// Usage Examples
// ============================================================================

/**
 * Example: Using Better Auth with JWT plugin
 *
 * ```typescript
 * import { useSession } from "@/lib/auth";
 *
 * function MyComponent() {
 *   const { data: session, isPending } = useSession();
 *
 *   if (isPending) return <div>Loading...</div>;
 *   if (!session) return <div>Not authenticated</div>;
 *
 *   // TypeScript now knows session.jwt exists
 *   const token = session.jwt;
 *
 *   return <div>Token: {token}</div>;
 * }
 * ```
 */

/**
 * Example: Using ChatKit with authentication
 *
 * ```typescript
 * import { useChatKit, ChatKit } from "@openai/chatkit-react";
 * import { useSession } from "@/lib/auth";
 *
 * function ChatPage() {
 *   const { data: session } = useSession();
 *   const [authToken, setAuthToken] = useState<string | null>(null);
 *
 *   useEffect(() => {
 *     if (session?.jwt) {
 *       setAuthToken(session.jwt);
 *     }
 *   }, [session]);
 *
 *   const control = useChatKit({
 *     apiUrl: "http://localhost:8000/chatkit",
 *     authToken: authToken || undefined,
 *     onError: (error) => console.error(error),
 *     onResponseEnd: (response) => console.log("Response:", response),
 *   });
 *
 *   return <ChatKit control={control} className="h-full" />;
 * }
 * ```
 */

/**
 * Example: Fetching JWT token explicitly
 *
 * ```typescript
 * async function getJwtToken(): Promise<string | null> {
 *   try {
 *     const response = await fetch("/api/auth/token");
 *     if (!response.ok) return null;
 *
 *     const data: JwtTokenResponse = await response.json();
 *     return data.token;
 *   } catch (error) {
 *     console.error("Failed to fetch JWT token:", error);
 *     return null;
 *   }
 * }
 * ```
 */
