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