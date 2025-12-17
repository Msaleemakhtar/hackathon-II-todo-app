# Database Schema Setup

Comprehensive guide for setting up database schema with Better Auth and Drizzle ORM.

## Official Documentation

- **Drizzle Adapter**: https://www.better-auth.com/docs/adapters/drizzle
- **Database Concepts**: https://www.better-auth.com/docs/concepts/database
- **CLI Tools**: https://www.better-auth.com/docs/cli

## Required Tables

Better Auth mandates four essential tables for user authentication and session management:

### 1. User Table

Stores user profiles and account information.

**Required Fields**:
- `id` (Primary Key) - Unique user identifier
- `name` (String, Optional) - User's display name
- `email` (String, Unique) - User's email address
- `emailVerified` (Boolean) - Email verification status
- `image` (String, Optional) - Profile image URL
- `createdAt` (DateTime) - Account creation timestamp
- `updatedAt` (DateTime) - Last update timestamp

### 2. Session Table

Manages active user sessions for authentication.

**Required Fields**:
- `id` (Primary Key) - Unique session identifier
- `userId` (Foreign Key → User.id) - Reference to user
- `token` (String, Unique) - Session token
- `expiresAt` (DateTime) - Session expiration time
- `ipAddress` (String, Optional) - Client IP address
- `userAgent` (String, Optional) - Client user agent
- `createdAt` (DateTime) - Session creation time
- `updatedAt` (DateTime) - Last session update

### 3. Account Table

Tracks authentication providers and credentials.

**Required Fields**:
- `id` (Primary Key) - Unique account identifier
- `userId` (Foreign Key → User.id) - Reference to user
- `accountId` (String) - Provider-specific account ID
- `providerId` (String) - Authentication provider name
- `accessToken` (String, Optional) - OAuth access token
- `refreshToken` (String, Optional) - OAuth refresh token
- `accessTokenExpiresAt` (DateTime, Optional) - Token expiration
- `refreshTokenExpiresAt` (DateTime, Optional) - Refresh expiration
- `scope` (String, Optional) - OAuth scopes
- `idToken` (String, Optional) - OpenID Connect ID token
- `password` (String, Optional) - Hashed password (email/password auth)
- `createdAt` (DateTime) - Account creation time
- `updatedAt` (DateTime) - Last update time

### 4. Verification Table

Handles email verification and password reset requests.

**Required Fields**:
- `id` (Primary Key) - Unique verification identifier
- `identifier` (String) - Email or user identifier
- `value` (String) - Verification token/code
- `expiresAt` (DateTime) - Token expiration time
- `createdAt` (DateTime) - Request creation time
- `updatedAt` (DateTime) - Last update time

## Drizzle Adapter Setup

### Installation

Install Better Auth and Drizzle ORM:

```bash
# Using bun (recommended for this project)
bun add better-auth drizzle-orm
bun add -d drizzle-kit

# Or using npm/pnpm/yarn
npm install better-auth drizzle-orm
npm install -D drizzle-kit
```

### Database Configuration

Configure Drizzle with PostgreSQL (Neon Serverless):

```ts
// lib/db.ts
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const db = drizzle(pool);
```

### Better Auth Adapter Integration

```ts
// lib/auth-server.ts
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { db } from "./db";

export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "pg", // PostgreSQL
  }),
  // ... other config
});
```

## Schema Generation

### Using Better Auth CLI

Generate Drizzle schema automatically:

```bash
# Generate schema for your project
npx @better-auth/cli@latest generate

# Or with bun
bun x @better-auth/cli@latest generate
```

The CLI will:
1. Detect your database adapter (Drizzle)
2. Generate schema files in `lib/db/schema.ts` (or your configured location)
3. Create all four required tables with proper relationships
4. Add indexes for performance optimization

### Manual Schema Migration

After generating the schema, create and apply migrations:

```bash
# Generate migration files
drizzle-kit generate

# Apply migrations to database
drizzle-kit migrate
```

## Schema Customization

### Custom Table Names

If you need different table names (e.g., plural forms):

```ts
database: drizzleAdapter(db, {
  provider: "pg",
  usePlural: true, // users, sessions, accounts, verifications
})
```

Or map individual tables:

```ts
database: drizzleAdapter(db, {
  provider: "pg",
  schema: {
    ...schema,
    user: schema.users, // Use 'users' instead of 'user'
  },
})
```

Alternatively, configure in Better Auth config:

```ts
user: {
  modelName: "users"
}
```

### Custom Field Names

Map database column names to Better Auth fields:

```ts
user: {
  fields: {
    email: "email_address", // DB column name
    name: "full_name",
  }
}
```

### Additional Fields

Extend user or session tables with custom fields:

```ts
user: {
  additionalFields: {
    role: {
      type: "string",
      defaultValue: "user",
    },
    preferences: {
      type: "json",
      defaultValue: {},
    },
  }
}
```

## Database Indexes

Better Auth automatically creates essential indexes:

**User Table**:
- Unique index on `email`
- Index on `createdAt` for sorting

**Session Table**:
- Unique index on `token`
- Index on `userId` for user session lookup
- Index on `expiresAt` for cleanup queries

**Account Table**:
- Index on `userId` for user account lookup
- Composite index on `providerId` and `accountId`

**Verification Table**:
- Index on `identifier` for verification lookup
- Index on `expiresAt` for cleanup queries

## PostgreSQL-Specific Configuration

### Connection Pooling

For production with Neon Serverless PostgreSQL:

```ts
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10, // Maximum pool size
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

export const db = drizzle(pool);
```

### SSL Configuration

Neon requires SSL connections:

```ts
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});
```

## Migration Workflow

### Development

1. Generate schema with Better Auth CLI:
   ```bash
   bun x @better-auth/cli generate
   ```

2. Review generated schema in `lib/db/schema.ts`

3. Create migration:
   ```bash
   drizzle-kit generate
   ```

4. Apply to database:
   ```bash
   drizzle-kit migrate
   ```

### Production

1. Test migrations locally first
2. Backup production database
3. Run migrations:
   ```bash
   drizzle-kit migrate
   ```
4. Verify schema with Better Auth CLI:
   ```bash
   bun x @better-auth/cli migrate
   ```

## Experimental Features

### Database Joins

Enable joins to reduce query roundtrips (Better Auth v1.4+):

```ts
export const auth = betterAuth({
  experimental: {
    joins: true
  },
  database: drizzleAdapter(db, {
    provider: "pg",
  }),
});
```

This optimizes queries when fetching related data (user + session + account).

## Troubleshooting

### Table Not Found

If Better Auth reports missing tables:

```bash
# Check database connection
bun x @better-auth/cli migrate

# Regenerate and apply migrations
drizzle-kit generate
drizzle-kit migrate
```

### Schema Mismatch

If schema changes don't apply:

1. Verify `drizzle.config.ts` points to correct schema file
2. Regenerate migrations: `drizzle-kit generate`
3. Check `meta` folder for migration files
4. Apply migrations: `drizzle-kit migrate`

### Connection Issues

Verify environment variables:

```bash
# Required
DATABASE_URL=postgresql://user:password@host:5432/database

# For Neon
DATABASE_URL=postgresql://user:password@ep-xxxxx.region.neon.tech/database?sslmode=require
```

## Best Practices

1. **Version Control**: Commit migration files to repository
2. **Backup**: Always backup before running migrations in production
3. **Testing**: Test migrations in staging environment first
4. **Cleanup**: Regularly remove expired sessions and verifications
5. **Indexes**: Monitor query performance and add indexes as needed
6. **Security**: Never expose database credentials in client code

## Example Schema (Drizzle)

Complete example from Better Auth CLI generation:

```ts
// lib/db/schema.ts
import { pgTable, text, timestamp, boolean, uuid } from 'drizzle-orm/pg-core';

export const user = pgTable('user', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: text('name'),
  email: text('email').notNull().unique(),
  emailVerified: boolean('emailVerified').notNull().default(false),
  image: text('image'),
  createdAt: timestamp('createdAt').notNull().defaultNow(),
  updatedAt: timestamp('updatedAt').notNull().defaultNow(),
});

export const session = pgTable('session', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('userId').notNull().references(() => user.id),
  token: text('token').notNull().unique(),
  expiresAt: timestamp('expiresAt').notNull(),
  ipAddress: text('ipAddress'),
  userAgent: text('userAgent'),
  createdAt: timestamp('createdAt').notNull().defaultNow(),
  updatedAt: timestamp('updatedAt').notNull().defaultNow(),
});

export const account = pgTable('account', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('userId').notNull().references(() => user.id),
  accountId: text('accountId').notNull(),
  providerId: text('providerId').notNull(),
  accessToken: text('accessToken'),
  refreshToken: text('refreshToken'),
  accessTokenExpiresAt: timestamp('accessTokenExpiresAt'),
  refreshTokenExpiresAt: timestamp('refreshTokenExpiresAt'),
  scope: text('scope'),
  idToken: text('idToken'),
  password: text('password'),
  createdAt: timestamp('createdAt').notNull().defaultNow(),
  updatedAt: timestamp('updatedAt').notNull().defaultNow(),
});

export const verification = pgTable('verification', {
  id: uuid('id').primaryKey().defaultRandom(),
  identifier: text('identifier').notNull(),
  value: text('value').notNull(),
  expiresAt: timestamp('expiresAt').notNull(),
  createdAt: timestamp('createdAt').notNull().defaultNow(),
  updatedAt: timestamp('updatedAt').notNull().defaultNow(),
});
```

## Next Steps

After setting up the database schema:

1. Configure Better Auth server instance (see `nextjs-setup.md`)
2. Set up frontend client (see `nextjs-setup.md`)
3. Implement JWT token flow (see `jwt-token-flow.md`)
4. Add security configurations (see `security-patterns.md`)
