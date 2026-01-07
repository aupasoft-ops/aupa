# 🌐 Conector de Redes Sociales - Aupa Software

## 📋 Descripción

Este módulo permite que los usuarios de tu aplicación Aupa Software conecten sus cuentas de redes sociales (Facebook, Instagram y TikTok) de forma segura y centralizada a través de n8n.

## 📁 Archivos Creados

```
web_aupa/
├── social_media_connector.py          # Clase principal del conector
└── portal_integration_example.py      # Ejemplo de integración en portal.py

Documentacion/
├── social_media_setup.md              # Guía completa de configuración
└── database_schema.sql                # Scripts SQL para la BD

ia_aupa/
└── n8n_facebook_flow.json             # Flujo JSON de ejemplo para n8n

setup_social_media.sh                  # Script de instalación automática
```

## 🚀 Inicio Rápido

### 1. Ejecutar Script de Configuración

```bash
cd /Users/carltocv/Documents/aupa-software/aupa
chmod +x setup_social_media.sh
./setup_social_media.sh
```

### 2. Crear la Tabla en PostgreSQL

```bash
# Opción 1: Usar el script (durante setup)
./setup_social_media.sh

# Opción 2: Manualmente
docker exec postgres_db psql -U tu_usuario -d tu_db -f Documentacion/database_schema.sql
```

### 3. Integrar en portal.py

Modifica tu `web_aupa/portal.py` para incluir el conector:

```python
# Al inicio del archivo
from social_media_connector import render_social_connector_ui

# En la función main(), agregar opción al menú
opcion = st.sidebar.radio(
    "Seleccione una herramienta:",
    [
        "🏠 Inicio",
        "🗄️ Gestión de Comercios",
        "🤖 Gestión IA",
        "🌐 Redes Sociales",  # ← Nueva opción
        "🔍 Test de Conexión"
    ]
)

# Luego, agregar la condición
if opcion == "🌐 Redes Sociales":
    render_social_connector_ui()
```

Puedes usar el archivo `web_aupa/portal_integration_example.py` como referencia.

### 4. Configurar Variables de Entorno

Edita tu archivo `.env` con las credenciales:

```env
# Facebook
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
FACEBOOK_REDIRECT_URI=http://localhost:5678/callback/facebook

# Instagram
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id
INSTAGRAM_ACCESS_TOKEN=your_access_token

# TikTok
TIKTOK_CLIENT_ID=your_client_id
TIKTOK_CLIENT_SECRET=your_client_secret
TIKTOK_REDIRECT_URI=http://localhost:5678/callback/tiktok

# Base de datos (ya debería estar)
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
```

### 5. Crear Webhooks en n8n

1. Acceder a n8n: http://localhost:5678
2. Crear nuevo flujo para cada plataforma:
   - `facebook-connect`
   - `instagram-connect`
   - `tiktok-connect`
3. Importar el flujo JSON: `ia_aupa/n8n_facebook_flow.json` como base
4. Adaptar para Instagram y TikTok

### 6. Iniciar la Aplicación

```bash
cd web_aupa
streamlit run portal.py
```

## 📚 Documentación Detallada

Para información completa sobre:
- Configuración de credenciales OAuth
- Estructura de flujos n8n
- Seguridad y buenas prácticas
- Solución de problemas

Ver: `Documentacion/social_media_setup.md`

## 🔐 Seguridad

### ⚠️ Importante para Producción

1. **Usa HTTPS** en lugar de HTTP
2. **Encripta tokens** en la base de datos
3. **Valida state parameter** en OAuth
4. **Implementa rate limiting** en webhooks
5. **Almacena credenciales** en variables de entorno
6. **Usa refresh tokens** para renovar acceso

## 🏗️ Estructura de Datos

### Tabla: connection_requests
```sql
- id: ID único
- user_id: Identificador del usuario
- platform: 'facebook', 'instagram', 'tiktok'
- email: Email del usuario
- state: Token CSRF
- access_token: Token de acceso OAuth
- refresh_token: Token para renovar acceso
- status: 'pending', 'authorized', 'failed', 'revoked'
- connected_at: Timestamp de conexión
- token_expiry: Fecha de expiración del token
```

## 📱 Clase Principal: SocialMediaConnector

### Métodos Disponibles

```python
from social_media_connector import SocialMediaConnector

connector = SocialMediaConnector()

# Verificar disponibilidad de n8n
connector.check_n8n_health() → bool

# Iniciar flujo OAuth para el usuario
oauth_url = connector.trigger_oauth_flow(
    platform='facebook',
    user_id='user_001',
    user_email='user@example.com'
)

# Obtener estado de la conexión
status = connector.get_connection_status(
    user_id='user_001',
    platform='facebook'
)

# Desconectar una plataforma
connector.disconnect_platform(
    user_id='user_001',
    platform='facebook'
)
```

## 🧪 Testing

### Probar webhook manualmente

```bash
curl -X POST http://localhost:5678/webhook/facebook-connect \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "facebook",
    "user_id": "test_user",
    "user_email": "test@example.com",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S)'"
  }'
```

### Verificar n8n

```bash
# Revisar logs
docker logs n8n_aupa

# Revisar health
curl http://localhost:5678/api/v1/health

# Probar conexión a BD
docker exec postgres_db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT COUNT(*) FROM connection_requests;"
```

## 📊 Diagrama de Flujo

```
┌─────────────────────┐
│  Usuario en Portal  │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────────────────┐
│ Hace clic en "Conectar Facebook"│
└──────────┬──────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ social_media_connector.py         │
│ - Envía solicitud a n8n          │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ n8n (localhost:5678)             │
│ - Genera URL OAuth               │
│ - Guarda state en BD             │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ Usuario redirigido a Facebook    │
│ - Autoriza permisos              │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ Facebook redirige a n8n callback │
│ - Verifica state                 │
│ - Cambia código por token        │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ PostgreSQL                       │
│ - Guarda token de acceso         │
│ - Marca como conectado           │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ Portal muestra: ✅ Conectado     │
└──────────────────────────────────┘
```

## 🐛 Troubleshooting

### "n8n no está disponible"
```bash
docker-compose up -d n8n
docker logs -f n8n_aupa
```

### "Error de conexión a base de datos"
```bash
# Verificar que PostgreSQL está corriendo
docker ps | grep postgres

# Conectar a la BD
docker exec postgres_db psql -U $POSTGRES_USER -d $POSTGRES_DB
```

### "Tokens expirados"
- Implementar refresh tokens en n8n
- Guardar tanto `access_token` como `refresh_token`
- Validar tokens antes de cada uso

## 📝 Checklist de Implementación

- [ ] Ejecutar `setup_social_media.sh`
- [ ] Crear tablas en PostgreSQL
- [ ] Agregar credenciales en `.env`
- [ ] Crear webhooks en n8n
- [ ] Integrar en `portal.py`
- [ ] Probar flujo OAuth
- [ ] Validar almacenamiento de tokens
- [ ] Revisar logs en producción

## 📞 Soporte

- **n8n Docs**: https://docs.n8n.io/
- **Facebook Login**: https://developers.facebook.com/docs/facebook-login
- **Instagram Graph API**: https://developers.facebook.com/docs/instagram-api
- **TikTok OAuth**: https://developers.tiktok.com/doc/login-kit-web-oauth-guide

## 📄 Licencia

Este código es parte de Aupa Software.

---

**Última actualización**: 7 de enero de 2026
