-- Tabla para almacenar los tokens de acceso de las redes sociales
CREATE TABLE social_accounts (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL, -- 'facebook', 'instagram', 'tiktok'
    platform_user_id VARCHAR(255),
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para la cola de publicaciones (el worker monitorea esta tabla)
CREATE TABLE posts_queue (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES social_accounts(id),
    content TEXT NOT NULL,
    media_url TEXT,
    scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'sent', 'failed'
    error_message TEXT,
    sent_at TIMESTAMP
);

-- Tabla para auditoría y seguimiento de intercambios de tokens
CREATE TABLE token_exchange_logs (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    authorization_code VARCHAR(255),
    access_token VARCHAR(500),
    token_status VARCHAR(50) NOT NULL, -- 'success', 'failed', 'expired', 'pending'
    error_message TEXT,
    error_code VARCHAR(100),
    facebook_user_id VARCHAR(255),
    token_obtained_at TIMESTAMP,
    token_expires_at TIMESTAMP,
    exchange_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

-- Tabla para logs de publicaciones exitosas y fallidas
CREATE TABLE post_publish_logs (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts_queue(id),
    account_id INTEGER REFERENCES social_accounts(id),
    platform VARCHAR(50),
    facebook_post_id VARCHAR(255),
    publish_status VARCHAR(50), -- 'published', 'failed', 'rejected'
    platform_response_code VARCHAR(50),
    error_details TEXT,
    retry_count INTEGER DEFAULT 0,
    published_at TIMESTAMP,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);