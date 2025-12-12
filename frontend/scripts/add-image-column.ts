/**
 * Add missing image column to user table
 */

import { Pool } from 'pg';

// Create PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

async function addImageColumnToUserTable() {
  const client = await pool.connect();

  try {
    console.log('🚀 Adding image column to user table...');

    // Add image column if it doesn't exist
    await client.query(`
      ALTER TABLE "user" 
      ADD COLUMN IF NOT EXISTS image TEXT;
    `);
    
    console.log('✅ Added/verified "image" column in "user" table');

    console.log('✨ Image column addition complete!');
  } catch (error) {
    console.error('❌ Error adding image column to user table:', error);
    throw error;
  } finally {
    client.release();
    await pool.end();
  }
}

// Run the update
addImageColumnToUserTable().catch((error) => {
  console.error('Failed to add image column:', error);
  process.exit(1);
});
