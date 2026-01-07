# Guía de Configuración - Conector de Redes Sociales con n8n

## 📋 Descripción General
Este módulo permite que los usuarios conecten sus cuentas de Facebook, Instagram y TikTok a través de n8n, que está ejecutándose localmente en Docker.

## 🚀 Instalación

### 1. Agregar al requirements.txt
Asegúrate de tener `requests` instalado:
```bash
pip install -r requirements.txt
```

El archivo debe incluir:
```
requests>=2.31.0
streamlit>=1.28.0
```

### 2. Integración en portal.py
Agrega esta opción al menú de navegación en `portal.py`:

```python
opcion = st.sidebar.radio(
    "Seleccione una herramienta:",
    ["🏠 Inicio", "🗄️ Gestión de Comercios", "🤖 Gestión IA", "🌐 Redes Sociales", "🔍 Test de Conexión"]
)

# Luego en el main():
if opcion == "🌐 Redes Sociales":
    from social_media_connector import render_social_connector_ui
    render_social_connector_ui()
```

## 🔧 Configuración en n8n

### Crear webhooks en n8n para cada plataforma

#### 1. Facebook Connect Webhook
**Nombre**: facebook-connect
**Ruta**: `/webhook/facebook-connect`
**Método**: POST

Flujo recomendado:
1. **Webhook Trigger** → recibe solicitud del usuario
2. **Extract data** → obtiene platform, user_id, user_email
3. **Create OAuth URL** → genera URL de OAuth para Facebook
4. **Store connection request** → guarda en base de datos
5. **Return response** → devuelve URL de OAuth al usuario

#### 2. Instagram Connect Webhook
**Nombre**: instagram-connect
**Ruta**: `/webhook/instagram-connect`
**Método**: POST

Mismo flujo que Facebook pero con credenciales de Instagram

#### 3. TikTok Connect Webhook
**Nombre**: tiktok-connect
**Ruta**: `/webhook/tiktok-connect`
**Método**: POST

Mismo flujo que Facebook pero con credenciales de TikTok

### Endpoints adicionales (opcionales)

```
/webhook/facebook-connect/status → GET estado de conexión
/webhook/facebook-connect/disconnect → POST desconectar
(Igual para instagram y tiktok)
```

## 🔐 Variables de Entorno

Configura las siguientes variables en `docker-compose.yml` o `.env`:

```env
# Facebook
FACEBOOK_APP_ID=tu_app_id_facebook
FACEBOOK_APP_SECRET=tu_app_secret_facebook
FACEBOOK_REDIRECT_URI=http://localhost:5678/callback/facebook

# Instagram
INSTAGRAM_BUSINESS_ACCOUNT_ID=tu_account_id
INSTAGRAM_ACCESS_TOKEN=tu_access_token

# TikTok
TIKTOK_CLIENT_ID=tu_client_id_tiktok
TIKTOK_CLIENT_SECRET=tu_client_secret_tiktok
TIKTOK_REDIRECT_URI=http://localhost:5678/callback/tiktok
```

## 📊 Estructura de Datos

### Solicitud de conexión
```json
{
  "platform": "facebook|instagram|tiktok",
  "user_id": "user_001",
  "user_email": "usuario@ejemplo.com",
  "timestamp": "2026-01-07T10:30:00",
  "request_type": "social_connection"
}
```

### Respuesta exitosa
```json
{
  "success": true,
  "message": "Solicitud enviada a Facebook",
  "data": {
    "oauth_url": "https://www.facebook.com/v18.0/dialog/oauth?...",
    "state": "random_state_string",
    "request_id": "req_12345"
  }
}
```

## 🔄 Flujo de OAuth

1. **Usuario** hace clic en "Conectar [Red Social]"
2. **Python** envía solicitud POST a webhook de n8n
3. **n8n** crea URL de OAuth y la devuelve
4. **Usuario** es redirigido a la plataforma social
5. **Usuario** autoriza los permisos
6. **Plataforma** redirige a callback de n8n
7. **n8n** guarda el token de acceso en la BD
8. **Sistema** muestra "✅ Conectado"

## 📱 Clase Principal: SocialMediaConnector

### Métodos principales:

```python
# Verificar disponibilidad de n8n
connector.check_n8n_health() → bool

# Iniciar flujo OAuth
connector.trigger_oauth_flow(platform, user_id, user_email) → str | None

# Obtener estado de conexión
connector.get_connection_status(user_id, platform) → dict

# Desconectar plataforma
connector.disconnect_platform(user_id, platform) → bool
```

## 🧪 Testing

Puedes probar los webhooks manualmente:

```bash
# Test Facebook webhook
curl -X POST http://localhost:5678/webhook/facebook-connect \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "facebook",
    "user_id": "user_001",
    "user_email": "test@ejemplo.com",
    "timestamp": "2026-01-07T10:30:00"
  }'

# Test status endpoint
curl http://localhost:5678/webhook/facebook-connect/status?user_id=user_001
```

## ⚠️ Consideraciones de Seguridad

1. **HTTPS**: En producción, usa HTTPS en lugar de HTTP
2. **State Parameter**: n8n debe generar y validar parámetros de state
3. **Token Storage**: Guarda tokens en la BD de forma segura (encriptados)
4. **Rate Limiting**: Implementa rate limiting en los webhooks
5. **CSRF Protection**: Valida tokens CSRF en callbacks
6. **Scope Minimization**: Solicita solo los permisos necesarios

## 📚 Recursos

- [n8n Documentation](https://docs.n8n.io/)
- [Facebook Login](https://developers.facebook.com/docs/facebook-login)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [TikTok OAuth](https://developers.tiktok.com/doc/login-kit-web-oauth-guide)

## 🐛 Solución de Problemas

### "n8n no está disponible"
```bash
# Verificar que Docker está corriendo
docker ps

# Reiniciar servicios
docker-compose restart n8n
```

### "No se puede conectar a webhook"
- Verificar que n8n está en http://localhost:5678
- Validar que los webhooks están activados en n8n
- Revisar logs: `docker logs n8n_aupa`

### Tokens expirados
- Implementar refresh token en n8n
- Almacenar tanto access_token como refresh_token
- Validar tokens antes de cada uso
