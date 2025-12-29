import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "@neondatabase/serverless";

/**
 * Better Auth Server Instance
 *
 * This is the server-side Better Auth configuration used for API routes.
 * Uses Neon Pool directly for database operations with Better Auth.
 */

let authInstance: ReturnType<typeof betterAuth> | null = null;

export function getAuth() {
  if (authInstance) {
    return authInstance;
  }

  // Convert asyncpg URL to standard postgresql URL for Neon
  const dbUrl = process.env.DATABASE_URL
    ?.replace('postgresql+asyncpg://', 'postgresql://') || '';

  // Create Better Auth instance with Neon Pool directly
  // Better Auth accepts Pool for PostgreSQL connections
  authInstance = betterAuth({
    database: new Pool({ connectionString: dbUrl }),
    emailAndPassword: {
      enabled: true,
      autoSignIn: true,
    },
    secret: process.env.BETTER_AUTH_SECRET,
    baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
    plugins: [
      jwt(),
    ],
  });

  return authInstance;
}
