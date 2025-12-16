import { toNextJsHandler } from "better-auth/next-js";
import { getAuth } from "@/lib/auth-server";

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
 * The auth instance is retrieved via getAuth() which defers database initialization
 * until runtime to allow successful Docker builds.
 */

// Create a wrapper to initialize auth at runtime
const createAuthHandler = () => {
  let initialized = false;
  let handlers: { GET: any; POST: any } | null = null;

  return {
    GET: async (request: Request) => {
      if (!initialized) {
        const auth = getAuth();
        handlers = toNextJsHandler(auth);
        initialized = true;
      }
      return handlers!.GET(request);
    },
    POST: async (request: Request) => {
      if (!initialized) {
        const auth = getAuth();
        handlers = toNextJsHandler(auth);
        initialized = true;
      }
      return handlers!.POST(request);
    }
  };
};

export const { GET, POST } = createAuthHandler();
