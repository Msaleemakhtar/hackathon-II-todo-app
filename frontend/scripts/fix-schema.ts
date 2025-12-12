#!/usr/bin/env bun
/**
 * Schema fix script - Adds missing columns to Better Auth tables
 *
 * Run with: bun run scripts/fix-schema.ts
 */

import { neon } from "@neondatabase/serverless";

const databaseUrl = process.env.DATABASE_URL;

if (!databaseUrl) {
  console.error("❌ DATABASE_URL environment variable is not set");
  process.exit(1);
}

const sql = neon(databaseUrl);

async function fixSchema() {
  console.log("🔧 Fixing database schema...\n");

  try {
    // Add missing 'image' column to user table if it doesn't exist
    console.log("📝 Adding 'image' column to user table...");
    await sql`
      ALTER TABLE "user"
      ADD COLUMN IF NOT EXISTS image TEXT;
    `;
    console.log("✅ Image column added/verified");

    console.log("\n🎉 Schema fix complete!");
  } catch (error) {
    console.error("\n❌ Error fixing schema:", error);
    process.exit(1);
  }
}

// Run the fix
fixSchema();
