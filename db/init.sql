CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    amount INT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type VARCHAR(20) CHECK (type IN ('income', 'expense')) NOT NULL,
    emoji VARCHAR(10),
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE
);