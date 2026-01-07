#!/bin/bash
# Script de configuración para conectar redes sociales con n8n
# Uso: ./setup_social_media.sh

set -e

echo "🚀 Iniciando configuración del conector de redes sociales..."
echo "==========================================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Verificar que Docker está corriendo
echo -e "${BLUE}1️⃣  Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker no está corriendo${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker está disponible${NC}"
echo ""

# 2. Verificar que n8n está corriendo
echo -e "${BLUE}2️⃣  Verificando n8n...${NC}"
if docker ps | grep -q "n8n_aupa"; then
    echo -e "${GREEN}✅ n8n está corriendo${NC}"
else
    echo -e "${YELLOW}⚠️  n8n no está corriendo${NC}"
    read -p "¿Deseas iniciar n8n? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        docker-compose up -d n8n
        echo "⏳ Esperando a que n8n se inicie..."
        sleep 10
        echo -e "${GREEN}✅ n8n iniciado${NC}"
    fi
fi
echo ""

# 3. Verificar conectividad con n8n
echo -e "${BLUE}3️⃣  Probando conectividad con n8n...${NC}"
if curl -s http://localhost:5678/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ n8n es accesible en http://localhost:5678${NC}"
else
    echo -e "${RED}❌ No se puede acceder a n8n${NC}"
    echo "   Verifica que n8n está corriendo: docker logs n8n_aupa"
    exit 1
fi
echo ""

# 4. Crear tabla en PostgreSQL (opcional)
echo -e "${BLUE}4️⃣  Configurando base de datos...${NC}"
read -p "¿Deseas crear la tabla 'connection_requests' en PostgreSQL? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    # Obtener credenciales del .env
    if [ -f .env ]; then
        export $(cat .env | xargs)
    fi
    
    docker exec postgres_db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
    CREATE TABLE IF NOT EXISTS connection_requests (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        platform VARCHAR(50) NOT NULL,
        email VARCHAR(255) NOT NULL,
        state VARCHAR(255) UNIQUE,
        oauth_url TEXT,
        access_token TEXT,
        refresh_token TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(50) DEFAULT 'pending',
        connected_at TIMESTAMP,
        UNIQUE(user_id, platform)
    );
    CREATE INDEX idx_user_platform ON connection_requests(user_id, platform);
    CREATE INDEX idx_state ON connection_requests(state);
    "
    echo -e "${GREEN}✅ Tabla creada/verificada en PostgreSQL${NC}"
else
    echo -e "${YELLOW}⏭️  Saltando creación de tabla${NC}"
fi
echo ""

# 5. Verificar que requirements.txt tiene requests
echo -e "${BLUE}5️⃣  Verificando dependencias Python...${NC}"
if ! grep -q "requests" web_aupa/requirements.txt; then
    echo -e "${YELLOW}⚠️  'requests' no está en requirements.txt${NC}"
    read -p "¿Deseas agregarlo? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "requests>=2.31.0" >> web_aupa/requirements.txt
        echo -e "${GREEN}✅ 'requests' agregado a requirements.txt${NC}"
    fi
else
    echo -e "${GREEN}✅ 'requests' ya está en requirements.txt${NC}"
fi
echo ""

# 6. Información sobre variables de entorno
echo -e "${BLUE}6️⃣  Variables de entorno necesarias...${NC}"
echo -e "${YELLOW}Asegúrate de tener estas variables en tu .env:${NC}"
echo "
  # Facebook
  FACEBOOK_APP_ID=tu_app_id
  FACEBOOK_APP_SECRET=tu_app_secret
  FACEBOOK_REDIRECT_URI=http://localhost:5678/callback/facebook

  # Instagram
  INSTAGRAM_BUSINESS_ACCOUNT_ID=tu_account_id
  INSTAGRAM_ACCESS_TOKEN=tu_access_token

  # TikTok
  TIKTOK_CLIENT_ID=tu_client_id
  TIKTOK_CLIENT_SECRET=tu_client_secret
  TIKTOK_REDIRECT_URI=http://localhost:5678/callback/tiktok
"
echo ""

# 7. Resumen
echo -e "${GREEN}==========================================================="
echo "✅ Configuración completada!"
echo "===========================================================${NC}"
echo ""
echo -e "${BLUE}📋 Próximos pasos:${NC}"
echo "1. Editar .env con las credenciales de tus redes sociales"
echo "2. Crear webhooks en n8n (http://localhost:5678)"
echo "3. Importar el flujo JSON: ia_aupa/n8n_facebook_flow.json"
echo "4. Iniciar la aplicación: streamlit run ./web_aupa/portal.py"
echo "5. Ir a 'Redes Sociales' en el menú lateral"
echo ""
echo -e "${BLUE}📚 Documentación: Documentacion/social_media_setup.md${NC}"
echo ""
