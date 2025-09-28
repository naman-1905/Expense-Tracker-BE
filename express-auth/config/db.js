const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});

// Test database connection and set schema
pool.connect((err, client, release) => {
  if (err) {
    console.error('Error acquiring client:', err.stack);
    return;
  }
  client.query('SET search_path TO expense', (err2) => {
    if (err2) {
      console.error('Error setting search_path:', err2.stack);
    } else {
      console.log('Connected to PostgreSQL database (schema: expense)');
    }
    release();
  });
});

module.exports = pool;
