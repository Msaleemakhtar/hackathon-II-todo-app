# Next.js + Better Auth Setup Guide

Complete setup guide for integrating Better Auth with Next.js applications.

## Official Documentation

- **Installation**: https://www.better-auth.com/docs/installation
- **Email/Password Auth**: https://www.better-auth.com/docs/authentication/email-password
- **Basic Usage**: https://www.better-auth.com/docs/basic-usage
- **React Integration**: Better Auth React package documentation

## Installation

### 1. Install Better Auth

Using bun (recommended for this project):

```bash
cd frontend
bun add better-auth
```

Using other package managers:

```bash
npm install better-auth
# or
pnpm add better-auth
# or
yarn add better-auth
```

### 2. Install Better Auth React Client

For React/Next.js frontend:

```bash
bun add better-auth
```

The React client is included in the main `better-auth` package.

### 3. Install Database Dependencies

For Drizzle ORM with PostgreSQL:

```bash
bun add drizzle-orm pg
bun add -d drizzle-kit @types/pg
```

## Environment Variables

Create `.env.local` in your Next.js project:

```env
# Better Auth Configuration
BETTER_AUTH_SECRET=<generate-with-openssl-rand-base64-32>
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:password@host:5432/database

# For production
# BETTER_AUTH_URL=https://yourdomain.com
```

### Generate Secret

Generate a secure secret for `BETTER_AUTH_SECRET`:

```bash
openssl rand -base64 32
```

**Requirements**:
- Minimum 32 characters
- High entropy (use cryptographic random generation)
- Same secret must be used in both frontend and backend for JWT validation

## Backend Setup (Next.js API Routes)

### 1. Create Auth Server Instance

Create `lib/auth-server.ts`:

```ts
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { db } from "./db"; // Your Drizzle database instance

export const auth = betterAuth({
  // Database configuration
  database: drizzleAdapter(db, {
    provider: "pg", // PostgreSQL
  }),

  // Email and password authentication
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
    maxPasswordLength: 128,
  },

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days in seconds
    updateAge: 60 * 60 * 24, // Update session every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24, // 24 hours
    },
  },

  // Security settings
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.BETTER_AUTH_URL!,

  // Trusted origins (for CORS)
  trustedOrigins: [
    "http://localhost:3000",
    process.env.BETTER_AUTH_URL!,
  ],

  // Rate limiting
  rateLimit: {
    enabled: true,
    window: 60, // 1 minute
    max: 10, // 10 requests per minute
  },

  // Advanced security
  advanced: {
    cookiePrefix: "better-auth",
    useSecureCookies: process.env.NODE_ENV === "production",
  },
});
```

**Key Configuration Options**:

- **expiresIn**: How long sessions remain valid (7 days = 604800 seconds)
- **updateAge**: How often to refresh session timestamp (prevents expiry for active users)
- **cookieCache**: Reduces database queries by caching session data in cookie
- **rateLimit**: Prevents brute force attacks (10 requests per minute)
- **useSecureCookies**: Enables secure flag in production (HTTPS only)

### 2. Create API Route Handler

Create `app/api/auth/[...all]/route.ts`:

```ts
import { auth } from "@/lib/auth-server";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

This creates the authentication API at `/api/auth/*` with all Better Auth endpoints:

- `/api/auth/sign-in/email` - Email/password sign in
- `/api/auth/sign-up/email` - Email/password sign up
- `/api/auth/sign-out` - Sign out
- `/api/auth/session` - Get current session
- `/api/auth/send-verification-email` - Send verification email
- `/api/auth/verify-email` - Verify email
- `/api/auth/forgot-password` - Request password reset
- `/api/auth/reset-password` - Reset password

## Frontend Setup (React Client)

### 1. Create Auth Client

Create `lib/auth.ts`:

```ts
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
});

// Export client methods for easy access
export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient;
```

### 2. Create Auth Context (Optional but Recommended)

Create `contexts/AuthContext.tsx`:

```tsx
"use client";

import { createContext, useContext, ReactNode } from 'react';
import { useSession } from '@/lib/auth';

interface UserProfile {
  id: string;
  email: string;
  name: string | null;
}

interface AuthContextType {
  user: UserProfile | null;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: session, isPending } = useSession();

  const user = session?.user ? {
    id: session.user.id,
    email: session.user.email,
    name: session.user.name || null,
  } : null;

  return (
    <AuthContext.Provider value={{ user, loading: isPending }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuthContext = () => useContext(AuthContext);
```

### 3. Wrap App with AuthProvider

In `app/layout.tsx`:

```tsx
import { AuthProvider } from '@/contexts/AuthContext';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

## Authentication Flows

### Sign Up

```tsx
// components/auth/SignUpForm.tsx
"use client";

import { useState } from 'react';
import { signUp } from '@/lib/auth';
import { useRouter } from 'next/navigation';

export function SignUpForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const result = await signUp.email({
        email,
        password,
        name,
      });

      if (result.error) {
        setError(result.error.message);
        return;
      }

      // User is automatically signed in after sign up
      router.push('/dashboard');
    } catch (err) {
      setError('An error occurred during sign up');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password (min 8 chars)"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        minLength={8}
      />
      {error && <p className="error">{error}</p>}
      <button type="submit">Sign Up</button>
    </form>
  );
}
```

### Sign In

```tsx
// components/auth/SignInForm.tsx
"use client";

import { useState } from 'react';
import { signIn } from '@/lib/auth';
import { useRouter } from 'next/navigation';

export function SignInForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const result = await signIn.email({
        email,
        password,
        rememberMe,
      });

      if (result.error) {
        setError(result.error.message);
        return;
      }

      router.push('/dashboard');
    } catch (err) {
      setError('An error occurred during sign in');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <label>
        <input
          type="checkbox"
          checked={rememberMe}
          onChange={(e) => setRememberMe(e.target.checked)}
        />
        Remember me
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit">Sign In</button>
    </form>
  );
}
```

### Sign Out

```tsx
// components/auth/SignOutButton.tsx
"use client";

import { signOut } from '@/lib/auth';
import { useRouter } from 'next/navigation';

export function SignOutButton() {
  const router = useRouter();

  const handleSignOut = async () => {
    await signOut({
      fetchOptions: {
        onSuccess: () => {
          router.push('/login');
        },
      },
    });
  };

  return (
    <button onClick={handleSignOut}>
      Sign Out
    </button>
  );
}
```

### Protected Pages

```tsx
// app/dashboard/page.tsx
"use client";

import { useAuthContext } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function DashboardPage() {
  const { user, loading } = useAuthContext();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return null;
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome, {user.name || user.email}!</p>
    </div>
  );
}
```

## Session Management

### useSession Hook

Better Auth provides `useSession` hook for reactive session access:

```tsx
import { useSession } from '@/lib/auth';

export function UserProfile() {
  const { data: session, isPending, error } = useSession();

  if (isPending) return <div>Loading...</div>;
  if (error) return <div>Error loading session</div>;
  if (!session) return <div>Not logged in</div>;

  return (
    <div>
      <p>Email: {session.user.email}</p>
      <p>Name: {session.user.name}</p>
      <p>ID: {session.user.id}</p>
    </div>
  );
}
```

### getSession (Server-Side)

For server components or API routes:

```ts
import { auth } from '@/lib/auth-server';
import { headers } from 'next/headers';

export async function getServerSession() {
  const session = await auth.api.getSession({
    headers: headers(),
  });

  return session;
}
```

## Database Schema Generation

Generate the required database schema:

```bash
# Generate Drizzle schema for Better Auth
bun x @better-auth/cli generate

# Generate migrations
drizzle-kit generate

# Apply migrations
drizzle-kit migrate
```

This creates the four required tables: `user`, `account`, `session`, `verification`.

## Next Steps

After completing Next.js setup:

1. Create JWT token endpoint for backend API integration (see `jwt-token-flow.md`)
2. Set up API client with interceptors (see `api-client.md`)
3. Implement security best practices (see `security-patterns.md`)
4. Configure FastAPI backend validation (see `fastapi-integration.md`)

## Common Issues

See `troubleshooting.md` for solutions to common setup problems.
