/**
 * Drop Better Auth tables to allow Better Auth to recreate them properly
 */

import { Pool } from 'pg';

// Create PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

async function dropBetterAuthTables() {
  const client = await pool.connect();

  try {
    console.log('🚀 Dropping Better Auth tables...');

    // Drop indexes first
    await client.query('DROP INDEX IF EXISTS idx_verification_identifier;');
    await client.query('DROP INDEX IF EXISTS idx_account_user_id;');
    await client.query('DROP INDEX IF EXISTS idx_session_token;');
    await client.query('DROP INDEX IF EXISTS idx_session_user_id;');

    // Drop tables (in correct order to respect foreign key constraints)
    await client.query('DROP TABLE IF EXISTS "verification";');
    await client.query('DROP TABLE IF EXISTS "session";');
    await client.query('DROP TABLE IF EXISTS "account";');
    await client.query('DROP TABLE IF EXISTS "user";');
    
    console.log('✅ Better Auth tables dropped');
    console.log('✨ Better Auth will recreate these tables on first use');

  } catch (error) {
    console.error('❌ Error dropping Better Auth tables:', error);
    throw error;
  } finally {
    client.release();
    await pool.end();
  }
}

// Run the drop
dropBetterAuthTables().catch((error) => {
  console.error('Failed to drop Better Auth tables:', error);
  process.exit(1);
});
