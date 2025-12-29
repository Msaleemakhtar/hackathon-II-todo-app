import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

/**
 * Better Auth Client
 *
 * This is the client-side Better Auth instance used for authentication
 * in React components. It provides hooks like useSession() for accessing
 * user session data.
 */
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
  plugins: [jwtClient()],
});

export const { useSession, signIn, signOut, signUp } = authClient;
