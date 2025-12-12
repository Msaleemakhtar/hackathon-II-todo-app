/**
 * Fix the account table schema to match Better Auth expectations
 * This drops and recreates the account table with proper column names
 */

import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

async function fixAccountTable() {
  const client = await pool.connect();

  try {
    console.log('🔧 Fixing account table schema...');

    // Drop the existing account table (this will cascade delete any accounts)
    await client.query(`DROP TABLE IF EXISTS "account" CASCADE;`);
    console.log('✅ Dropped existing account table');

    // Recreate the account table with correct column names
    await client.query(`
      CREATE TABLE "account" (
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
    console.log('✅ Created account table with correct schema');

    // Recreate index
    await client.query(`
      CREATE INDEX idx_account_user_id ON "account"("userId");
    `);
    console.log('✅ Created index');

    console.log('✨ Account table fix complete!');
  } catch (error) {
    console.error('❌ Error fixing account table:', error);
    throw error;
  } finally {
    client.release();
    await pool.end();
  }
}

fixAccountTable().catch((error) => {
  console.error('Failed to fix account table:', error);
  process.exit(1);
});
