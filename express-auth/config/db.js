const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  // Set default search_path for all connections
  options: '-c search_path=expense'
});

// Test database connection
pool.connect((err, client, release) => {
  if (err) {
    console.error('Error acquiring client:', err.stack);
    return;
  }
  
  // Verify the schema is set correctly
  client.query('SHOW search_path', (err2, result) => {
    if (err2) {
      console.error('Error checking search_path:', err2.stack);
    } else {
      console.log('Connected to PostgreSQL database');
      console.log('Current search_path:', result.rows[0].search_path);
    }
    release();
  });
});

// Add error handling for the pool
pool.on('error', (err) => {
  console.error('Unexpected error on idle client', err);
  process.exit(-1);
});

module.exports = pool;