#!/usr/bin/env bun
/**
 * Database initialization script for Better Auth
 *
 * This script creates all necessary tables for Better Auth using Drizzle ORM
 * with the Neon serverless driver.
 *
 * Run with: bun run scripts/init-db.ts
 */

import { neon } from "@neondatabase/serverless";

const databaseUrl = process.env.DATABASE_URL;

if (!databaseUrl) {
  console.error("❌ DATABASE_URL environment variable is not set");
  process.exit(1);
}

const sql = neon(databaseUrl);

async function initDatabase() {
  console.log("🚀 Initializing database for Better Auth...\n");

  try {
    // Create user table
    console.log("📝 Creating 'user' table...");
    await sql`
      CREATE TABLE IF NOT EXISTS "user" (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        "emailVerified" BOOLEAN DEFAULT false NOT NULL,
        name TEXT,
        image TEXT,
        "createdAt" TIMESTAMP DEFAULT NOW() NOT NULL,
        "updatedAt" TIMESTAMP DEFAULT NOW() NOT NULL
      );
    `;
    console.log("✅ User table created");

    // Create account table
    console.log("📝 Creating 'account' table...");
    await sql`
      CREATE TABLE IF NOT EXISTS "account" (
        id TEXT PRIMARY KEY,
        "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
        "accountId" TEXT NOT NULL,
        "providerId" TEXT NOT NULL,
        password TEXT,
        "createdAt" TIMESTAMP DEFAULT NOW() NOT NULL,
        "updatedAt" TIMESTAMP DEFAULT NOW() NOT NULL
      );
    `;
    console.log("✅ Account table created");

    // Create session table
    console.log("📝 Creating 'session' table...");
    await sql`
      CREATE TABLE IF NOT EXISTS "session" (
        id TEXT PRIMARY KEY,
        "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
        token TEXT UNIQUE NOT NULL,
        "expiresAt" TIMESTAMP NOT NULL,
        "ipAddress" TEXT,
        "userAgent" TEXT,
        "createdAt" TIMESTAMP DEFAULT NOW() NOT NULL,
        "updatedAt" TIMESTAMP DEFAULT NOW() NOT NULL
      );
    `;
    console.log("✅ Session table created");

    // Create verification table
    console.log("📝 Creating 'verification' table...");
    await sql`
      CREATE TABLE IF NOT EXISTS "verification" (
        id TEXT PRIMARY KEY,
        identifier TEXT NOT NULL,
        value TEXT NOT NULL,
        "expiresAt" TIMESTAMP NOT NULL,
        "createdAt" TIMESTAMP DEFAULT NOW() NOT NULL,
        "updatedAt" TIMESTAMP DEFAULT NOW() NOT NULL
      );
    `;
    console.log("✅ Verification table created");

    // Create indexes for better performance
    console.log("\n📝 Creating indexes...");
    await sql`CREATE INDEX IF NOT EXISTS idx_account_user_id ON "account"("userId");`;
    await sql`CREATE INDEX IF NOT EXISTS idx_session_user_id ON "session"("userId");`;
    await sql`CREATE INDEX IF NOT EXISTS idx_session_token ON "session"(token);`;
    await sql`CREATE INDEX IF NOT EXISTS idx_verification_identifier ON "verification"(identifier);`;
    console.log("✅ Indexes created");

    console.log("\n🎉 Database initialization complete!");
    console.log("\n📊 Tables created:");
    console.log("   - user");
    console.log("   - account");
    console.log("   - session");
    console.log("   - verification");
    console.log("\n✨ Your Better Auth database is ready to use!");
  } catch (error) {
    console.error("\n❌ Error initializing database:", error);
    process.exit(1);
  }
}

// Run the initialization
initDatabase();
