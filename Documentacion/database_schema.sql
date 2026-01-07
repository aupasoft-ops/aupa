-- Script SQL para crear las tablas necesarias para el conector de redes sociales
-- Ejecutar en PostgreSQL

-- ============================================
-- Tabla principal: connection_requests
-- Almacena las solicitudes de conexión a redes sociales
-- ============================================
CREATE TABLE IF NOT EXISTS connection_requests (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,  -- 'facebook', 'instagram', 'tiktok'
    email VARCHAR(255) NOT NULL,
    state VARCHAR(255) UNIQUE NOT NULL,  -- Para validación OAuth
    oauth_url TEXT,
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'authorized', 'failed', 'revoked'
    connected_at TIMESTAMP,
    last_refresh TIMESTAMP,
    error_message TEXT,
    
    -- Restricción de unicidad: un usuario solo puede tener una conexión por plataforma
    UNIQUE(user_id, platform),
    
    -- Índices para búsquedas frecuentes
    CONSTRAINT fk_user_platform UNIQUE(user_id, platform)
);

CREATE INDEX IF NOT EXISTS idx_connection_requests_user_id 
    ON connection_requests(user_id);

CREATE INDEX IF NOT EXISTS idx_connection_requests_platform 
    ON connection_requests(platform);

CREATE INDEX IF NOT EXISTS idx_connection_requests_state 
    ON connection_requests(state);

CREATE INDEX IF NOT EXISTS idx_connection_requests_status 
    ON connection_requests(status);

CREATE INDEX IF NOT EXISTS idx_connection_requests_user_platform 
    ON connection_requests(user_id, platform);

-- ============================================
-- Tabla: social_media_accounts
-- Almacena información de las cuentas conectadas
-- ============================================
CREATE TABLE IF NOT EXISTS social_media_accounts (
    id SERIAL PRIMARY KEY,
    connection_request_id INTEGER NOT NULL REFERENCES connection_requests(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    account_id VARCHAR(255),  -- ID de la cuenta en la red social
    account_name VARCHAR(255),
    account_email VARCHAR(255),
    profile_url VARCHAR(500),
    profile_picture_url VARCHAR(500),
    followers_count INTEGER DEFAULT 0,
    bio TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(platform, account_id)
);

CREATE INDEX IF NOT EXISTS idx_social_accounts_user_platform 
    ON social_media_accounts(user_id, platform);

CREATE INDEX IF NOT EXISTS idx_social_accounts_account_id 
    ON social_media_accounts(account_id);

-- ============================================
-- Tabla: oauth_logs
-- Registra todas las actividades de OAuth para auditoría
-- ============================================
CREATE TABLE IF NOT EXISTS oauth_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    action VARCHAR(100),  -- 'request_sent', 'authorization_granted', 'token_refreshed', 'revoked', 'failed'
    status_code VARCHAR(10),
    error_message TEXT,
    request_data JSONB,
    response_data JSONB,
    
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_oauth_logs_user_id 
    ON oauth_logs(user_id);

CREATE INDEX IF NOT EXISTS idx_oauth_logs_platform 
    ON oauth_logs(platform);

CREATE INDEX IF NOT EXISTS idx_oauth_logs_action 
    ON oauth_logs(action);

CREATE INDEX IF NOT EXISTS idx_oauth_logs_created_at 
    ON oauth_logs(created_at);

-- ============================================
-- Tabla: social_media_permissions
-- Almacena los permisos otorgados para cada plataforma
-- ============================================
CREATE TABLE IF NOT EXISTS social_media_permissions (
    id SERIAL PRIMARY KEY,
    connection_request_id INTEGER NOT NULL REFERENCES connection_requests(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    
    -- Permisos específicos
    permission_name VARCHAR(255),  -- 'pages_manage_metadata', 'instagram_business_management', etc.
    permission_status VARCHAR(50) DEFAULT 'granted',  -- 'granted', 'requested', 'denied', 'revoked'
    
    granted_at TIMESTAMP,
    revoked_at TIMESTAMP,
    
    UNIQUE(user_id, platform, permission_name)
);

CREATE INDEX IF NOT EXISTS idx_permissions_user_platform 
    ON social_media_permissions(user_id, platform);

-- ============================================
-- Función para actualizar last_updated automáticamente
-- ============================================
CREATE OR REPLACE FUNCTION update_last_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Crear trigger para social_media_accounts
DROP TRIGGER IF EXISTS update_social_media_accounts_timestamp ON social_media_accounts;
CREATE TRIGGER update_social_media_accounts_timestamp
    BEFORE UPDATE ON social_media_accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated_column();

-- ============================================
-- Vistas útiles
-- ============================================

-- Vista: Resumen de conexiones por usuario
CREATE OR REPLACE VIEW v_user_connections AS
SELECT 
    cr.user_id,
    cr.email,
    cr.platform,
    cr.status,
    sma.account_name,
    sma.followers_count,
    cr.connected_at,
    cr.last_refresh,
    (CURRENT_TIMESTAMP - cr.token_expiry) < INTERVAL '1 day' AS token_expiring_soon
FROM connection_requests cr
LEFT JOIN social_media_accounts sma ON cr.id = sma.connection_request_id
ORDER BY cr.user_id, cr.platform;

-- Vista: Historial de actividades OAuth
CREATE OR REPLACE VIEW v_oauth_activity_summary AS
SELECT 
    user_id,
    platform,
    COUNT(*) as total_events,
    COUNT(CASE WHEN action = 'authorization_granted' THEN 1 END) as authorizations,
    COUNT(CASE WHEN action = 'token_refreshed' THEN 1 END) as refreshes,
    COUNT(CASE WHEN action = 'failed' THEN 1 END) as failures,
    MAX(created_at) as last_activity
FROM oauth_logs
GROUP BY user_id, platform;

-- ============================================
-- Datos de ejemplo (comentados, descomenta para usar)
-- ============================================

/*
-- Insertar un registro de ejemplo
INSERT INTO connection_requests (user_id, platform, email, state, status)
VALUES 
    ('user_001', 'facebook', 'usuario@ejemplo.com', 'state_random_123', 'pending'),
    ('user_001', 'instagram', 'usuario@ejemplo.com', 'state_random_456', 'authorized'),
    ('user_001', 'tiktok', 'usuario@ejemplo.com', 'state_random_789', 'pending');

-- Insertar datos de cuenta de ejemplo
INSERT INTO social_media_accounts (connection_request_id, user_id, platform, account_id, account_name)
VALUES 
    (2, 'user_001', 'instagram', 'ig_12345', 'mi_instagram');

-- Insertar permisos de ejemplo
INSERT INTO social_media_permissions (connection_request_id, user_id, platform, permission_name, permission_status)
VALUES 
    (1, 'user_001', 'facebook', 'pages_manage_metadata', 'granted'),
    (1, 'user_001', 'facebook', 'pages_read_engagement', 'granted'),
    (2, 'user_001', 'instagram', 'instagram_business_management', 'granted');
*/

-- ============================================
-- Procedimiento almacenado para limpiar solicitudes antiguas
-- ============================================
CREATE OR REPLACE FUNCTION cleanup_old_requests()
RETURNS void AS $$
BEGIN
    DELETE FROM connection_requests
    WHERE status = 'pending'
    AND created_at < NOW() - INTERVAL '7 days';
    
    DELETE FROM connection_requests
    WHERE status = 'failed'
    AND created_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Triggers automáticos
-- ============================================

-- Registrar cambios en oauth_logs
CREATE OR REPLACE FUNCTION log_oauth_activity()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.status != OLD.status THEN
        INSERT INTO oauth_logs (user_id, platform, action, status_code)
        VALUES (NEW.user_id, NEW.platform, 'status_changed_to_' || NEW.status, '200');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_log_oauth_activity ON connection_requests;
CREATE TRIGGER trigger_log_oauth_activity
    AFTER UPDATE ON connection_requests
    FOR EACH ROW
    EXECUTE FUNCTION log_oauth_activity();

-- ============================================
-- Comentarios para documentación
-- ============================================
COMMENT ON TABLE connection_requests IS 'Almacena las solicitudes de conexión OAuth a redes sociales';
COMMENT ON TABLE social_media_accounts IS 'Información detallada de las cuentas de redes sociales conectadas';
COMMENT ON TABLE oauth_logs IS 'Registro de auditoría de todas las actividades OAuth';
COMMENT ON TABLE social_media_permissions IS 'Permisos específicos otorgados para cada conexión';

COMMENT ON COLUMN connection_requests.state IS 'Token CSRF para validar la respuesta de OAuth';
COMMENT ON COLUMN connection_requests.status IS 'Estado actual: pending, authorized, failed, revoked';
COMMENT ON COLUMN oauth_logs.request_data IS 'Datos de la solicitud en formato JSON';
COMMENT ON COLUMN oauth_logs.response_data IS 'Datos de la respuesta en formato JSON';
