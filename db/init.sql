CREATE TABLE public.users (
    user_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.transactions (
    transaction_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    amount INT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type VARCHAR(20) CHECK (type IN ('income', 'expense', 'savings')) NOT NULL,
    emoji VARCHAR(10),
    user_id INT,
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES public.users(user_id)
        ON DELETE CASCADE
);
