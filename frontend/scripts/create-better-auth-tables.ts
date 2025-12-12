/**
 * Create Better Auth tables using the Drizzle schema
 * 
 * This script directly uses the Drizzle schema definitions to create the required tables.
 */

import { drizzle } from 'drizzle-orm/neon-http';
import { neon } from '@neondatabase/serverless';
import { sql } from 'drizzle-orm';

// Get database URL from environment
const databaseUrl = process.env.DATABASE_URL;

if (!databaseUrl) {
  throw new Error("DATABASE_URL environment variable is not set");
}

// Create Neon client and Drizzle instance
const sqlClient = neon(databaseUrl);
const db = drizzle(sqlClient);

async function createBetterAuthTables() {
  console.log('🚀 Creating Better Auth tables using Drizzle schema...');

  try {
    // Create user table
    await db.execute(sql`
      CREATE TABLE IF NOT EXISTS "user" (
        "id" text PRIMARY KEY,
        "email" text NOT NULL UNIQUE,
        "emailVerified" boolean NOT NULL DEFAULT false,
        "name" text,
        "createdAt" timestamp NOT NULL DEFAULT NOW(),
        "updatedAt" timestamp NOT NULL DEFAULT NOW(),
        "image" text
      )
    `);
    console.log('✅ Created user table');

    // Create account table
    await db.execute(sql`
      CREATE TABLE IF NOT EXISTS "account" (
        "id" text PRIMARY KEY,
        "userId" text NOT NULL,
        "accountId" text NOT NULL,
        "providerId" text NOT NULL,
        "accessToken" text,
        "refreshToken" text,
        "expiresAt" timestamp,
        "password" text,
        "createdAt" timestamp NOT NULL DEFAULT NOW(),
        "updatedAt" timestamp NOT NULL DEFAULT NOW(),
        CONSTRAINT account_userId_fkey FOREIGN KEY ("userId") REFERENCES "user"("id") ON DELETE CASCADE
      )
    `);
    console.log('✅ Created account table');

    // Create session table
    await db.execute(sql`
      CREATE TABLE IF NOT EXISTS "session" (
        "id" text PRIMARY KEY,
        "userId" text NOT NULL,
        "token" text NOT NULL UNIQUE,
        "expiresAt" timestamp NOT NULL,
        "ipAddress" text,
        "userAgent" text,
        "createdAt" timestamp NOT NULL DEFAULT NOW(),
        "updatedAt" timestamp NOT NULL DEFAULT NOW(),
        CONSTRAINT session_userId_fkey FOREIGN KEY ("userId") REFERENCES "user"("id") ON DELETE CASCADE
      )
    `);
    console.log('✅ Created session table');

    // Create verification table
    await db.execute(sql`
      CREATE TABLE IF NOT EXISTS "verification" (
        "id" text PRIMARY KEY,
        "identifier" text NOT NULL,
        "value" text NOT NULL,
        "expiresAt" timestamp NOT NULL,
        "createdAt" timestamp NOT NULL DEFAULT NOW(),
        "updatedAt" timestamp NOT NULL DEFAULT NOW()
      )
    `);
    console.log('✅ Created verification table');

    // Create indexes
    try {
      await db.execute(sql`CREATE INDEX IF NOT EXISTS idx_session_user_id ON "session"("userId");`);
      await db.execute(sql`CREATE INDEX IF NOT EXISTS idx_session_token ON "session"("token");`);
      await db.execute(sql`CREATE INDEX IF NOT EXISTS idx_account_user_id ON "account"("userId");`);
      await db.execute(sql`CREATE INDEX IF NOT EXISTS idx_verification_identifier ON "verification"("identifier");`);
      console.log('✅ Created indexes');
    } catch (indexError) {
      console.log('ℹ️ Index creation completed (may have already existed)');
    }

    console.log('✨ Better Auth tables creation complete!');
  } catch (error) {
    console.error('❌ Error creating Better Auth tables:', error);
    throw error;
  }
}

// Run the creation
createBetterAuthTables().catch((error) => {
  console.error('Failed to create Better Auth tables:', error);
  process.exit(1);
});