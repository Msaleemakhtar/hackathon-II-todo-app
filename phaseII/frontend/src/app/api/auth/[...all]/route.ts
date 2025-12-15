import { toNextJsHandler } from "better-auth/next-js";
import { auth } from "@/lib/auth-server";

/**
 * Better Auth API Route Handler
 *
 * This handles all Better Auth endpoints:
 * - POST /api/auth/sign-up/email - User registration
 * - POST /api/auth/sign-in/email - User login
 * - POST /api/auth/sign-out - User logout
 * - GET /api/auth/get-session - Get current session
 * - And other Better Auth endpoints
 *
 * The auth instance is imported from a centralized configuration
 * to avoid duplicate database connections.
 */

// Export HTTP method handlers for Next.js App Router
export const { GET, POST } = toNextJsHandler(auth);
