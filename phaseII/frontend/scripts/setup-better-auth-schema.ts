/**
 * Better Auth schema setup
 * 
 * This script uses Better Auth's adapter to create the required database tables
 * instead of manually creating them.
 */

import { drizzle } from 'drizzle-orm/neon-http';
import { migrate } from 'drizzle-orm/neon-http/migrator';
import { neon } from '@neondatabase/serverless';

// Get database URL from environment
const databaseUrl = process.env.DATABASE_URL;

if (!databaseUrl) {
  throw new Error("DATABASE_URL environment variable is not set");
}

// Create Neon client and Drizzle instance
const sql = neon(databaseUrl);
const db = drizzle(sql);

async function setupBetterAuthSchema() {
  console.log('🚀 Setting up Better Auth schema...');

  try {
    // Run Better Auth schema migrations
    await migrate(db, { migrationsFolder: './drizzle' });
    
    console.log('✅ Better Auth schema setup complete!');
  } catch (error) {
    console.error('❌ Error setting up Better Auth schema:', error);
    throw error;
  }
}

// Run the setup
setupBetterAuthSchema().catch((error) => {
  console.error('Failed to setup Better Auth schema:', error);
  process.exit(1);
});