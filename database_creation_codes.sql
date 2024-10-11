CREATE TABLE user_ratings (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255),
    rating INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE email_feedback (
    id SERIAL PRIMARY KEY,
    sender_email VARCHAR(255),
    body TEXT,
    sentiment VARCHAR(50)
);


CREATE TABLE user_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(255) UNIQUE NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    -- anonymized_id VARCHAR(255) NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_ratings2 (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) UNIQUE,
    service_rating INTEGER,
    prices_rating INTEGER,
    staff_rating INTEGER,
    timestamp TIMESTAMP
);

-- For resetting sequence of table
DELETE from user_tokens ; -- Optional step to clear the table
ALTER SEQUENCE user_tokens_id_seq RESTART WITH 1; 