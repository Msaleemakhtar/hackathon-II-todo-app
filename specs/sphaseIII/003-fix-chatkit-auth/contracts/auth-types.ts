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
// ChatKit Types
// ============================================================================

/**
 * ChatKit useChatKit Hook Options
 *
 * Configuration options for the useChatKit hook.
 * NOTE: The 'options' wrapper does NOT exist in the actual API.
 * Pass these properties directly to useChatKit.
 *
 * Correct Usage:
 * ```typescript
 * const control = useChatKit({
 *   apiUrl: "http://localhost:8000/chatkit",
 *   authToken: token,
 *   onError: (error) => console.error(error),
 * });
 * ```
 *
 * Incorrect Usage (causes TypeScript error):
 * ```typescript
 * const control = useChatKit({
 *   options: {  // ❌ 'options' does not exist
 *     apiUrl: "...",
 *     authToken: "...",
 *   }
 * });
 * ```
 */
export interface UseChatKitOptions {
  /**
   * Backend API endpoint for ChatKit adapter
   * Example: "http://localhost:8000/chatkit"
   */
  apiUrl: string;

  /**
   * Optional JWT authentication token
   * Sent as Authorization: Bearer <token> header
   */
  authToken?: string;

  /**
   * Optional error handler
   * Called when chat operations fail
   */
  onError?: (error: Error) => void;

  /**
   * Optional response end handler
   * Called when AI response generation completes
   */
  onResponseEnd?: (response: ChatKitResponse) => void;

  /**
   * Optional thread change handler
   * Called when conversation thread changes
   */
  onThreadChange?: (thread: ChatKitThread) => void;
}

/**
 * ChatKit Control Object
 *
 * Object returned by useChatKit hook for controlling chat operations.
 */
export interface ChatKitControl {
  /**
   * Send a message to the chat
   */
  sendMessage: (message: string) => Promise<void>;

  /**
   * Get current thread/conversation ID
   */
  getThreadId: () => string | null;

  /**
   * Set thread/conversation ID
   */
  setThreadId: (threadId: string | null) => void;

  /**
   * Check if chat is currently processing
   */
  isLoading: boolean;

  /**
   * Get current chat history
   */
  messages: ChatKitMessage[];
}

/**
 * ChatKit Message
 *
 * Represents a single message in the chat history.
 */
export interface ChatKitMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: Date;
}

/**
 * ChatKit Response
 *
 * Response object passed to onResponseEnd handler.
 */
export interface ChatKitResponse {
  messageId: string;
  content: string;
  toolCalls?: Array<{
    name: string;
    arguments: Record<string, any>;
    result?: any;
  }>;
}

/**
 * ChatKit Thread
 *
 * Thread/conversation object passed to onThreadChange handler.
 */
export interface ChatKitThread {
  id: string;
  createdAt: Date;
  messageCount: number;
}

/**
 * ChatKit Component Props
 *
 * Props for the ChatKit React component.
 */
export interface ChatKitProps {
  /**
   * Control object from useChatKit hook
   */
  control: ChatKitControl;

  /**
   * Optional CSS class name
   */
  className?: string;

  /**
   * Optional custom styles
   */
  style?: React.CSSProperties;
}

/**
 * Module declaration for @openai/chatkit-react
 *
 * Provides type definitions for the ChatKit package to resolve
 * TypeScript compilation errors.
 */
declare module "@openai/chatkit-react" {
  export function useChatKit(options: UseChatKitOptions): ChatKitControl;

  export function ChatKit(props: ChatKitProps): JSX.Element;

  export type {
    UseChatKitOptions,
    ChatKitControl,
    ChatKitMessage,
    ChatKitResponse,
    ChatKitThread,
    ChatKitProps,
  };
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
