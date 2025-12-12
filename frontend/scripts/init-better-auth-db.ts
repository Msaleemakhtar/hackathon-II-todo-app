/**
 * Initialize Better Auth database tables
 *
 * This script creates the necessary tables for Better Auth in PostgreSQL
 * Run with: bun run scripts/init-better-auth-db.ts
 */

import { Pool } from 'pg';

// Create PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

async function initBetterAuthTables() {
  const client = await pool.connect();

  try {
    console.log('🚀 Initializing Better Auth database tables...');

    // Create users table (if not exists)
    await client.query(`
      CREATE TABLE IF NOT EXISTS "user" (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        "emailVerified" BOOLEAN NOT NULL DEFAULT false,
        name TEXT,
        "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
        "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
        image TEXT
      );
    `);
    console.log('✅ Created/verified "user" table');

    // Create accounts table (for password authentication)
    await client.query(`
      CREATE TABLE IF NOT EXISTS "account" (
        id TEXT PRIMARY KEY,
        "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
        "accountId" TEXT NOT NULL,
        "providerId" TEXT NOT NULL,
        "accessToken" TEXT,
        "refreshToken" TEXT,
        "expiresAt" TIMESTAMP,
        password TEXT,
        "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
        "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
      );
    `);
    console.log('✅ Created/verified "account" table');

    // Create sessions table
    await client.query(`
      CREATE TABLE IF NOT EXISTS "session" (
        id TEXT PRIMARY KEY,
        "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
        token TEXT UNIQUE NOT NULL,
        "expiresAt" TIMESTAMP NOT NULL,
        "ipAddress" TEXT,
        "userAgent" TEXT,
        "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
        "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
      );
    `);
    console.log('✅ Created/verified "session" table');

    // Create verification table (for email verification)
    await client.query(`
      CREATE TABLE IF NOT EXISTS "verification" (
        id TEXT PRIMARY KEY,
        identifier TEXT NOT NULL,
        value TEXT NOT NULL,
        "expiresAt" TIMESTAMP NOT NULL,
        "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
        "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
      );
    `);
    console.log('✅ Created/verified "verification" table');

    // Create indexes for better performance
    await client.query(`
      CREATE INDEX IF NOT EXISTS idx_session_user_id ON "session"("userId");
      CREATE INDEX IF NOT EXISTS idx_session_token ON "session"(token);
      CREATE INDEX IF NOT EXISTS idx_account_user_id ON "account"("userId");
    `);
    console.log('✅ Created indexes');

    console.log('✨ Better Auth database initialization complete!');
  } catch (error) {
    console.error('❌ Error initializing Better Auth tables:', error);
    throw error;
  } finally {
    client.release();
    await pool.end();
  }
}

// Run the initialization
initBetterAuthTables().catch((error) => {
  console.error('Failed to initialize database:', error);
  process.exit(1);
});
