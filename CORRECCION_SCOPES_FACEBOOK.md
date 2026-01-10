# 🔧 Corrección de Scopes de Facebook OAuth

## 📋 Problema Identificado

**Error:** `Invalid Scopes: pages_manage_posts, publish_video, pages_show_list`

Esto ocurre porque los scopes `pages_manage_posts` y `publish_video` **no son válidos para Facebook Login** (user authentication). Estos son scopes de **página** que requieren un flujo diferente.

---

## ✅ Solución Implementada

### 1. Scopes Corregidos en app.py

**Antes (❌ Incorrecto):**
```
scope=pages_manage_posts,publish_video
```

**Después (✅ Correcto):**
```
scope=email,user_friends,pages_read_engagement,pages_read_user_content&state=facebook
```

### 2. Nuevo Flujo de Autenticación

El flujo ahora es:

```
┌─────────────────────────────────────────────────────────┐
│ 1. Usuario autoriza en Facebook (Facebook Login)        │
│    Scopes: email, user_friends, pages_read_*            │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Intercambio de código por USER ACCESS TOKEN          │
│    (Token para actuar como el usuario)                  │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Obtener PAGE ACCESS TOKEN                            │
│    - Llamar: GET /me/accounts con user token            │
│    - Resultado: Lista de páginas del usuario            │
│    - Usar: page_token para publicar                     │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Guardar PAGE TOKEN en BD                             │
│    - Este token se usa para publicar en la página       │
│    - Es el que se guarda en social_accounts             │
└─────────────────────────────────────────────────────────┘
```

---

## 🔑 Diferencia: User Token vs Page Token

| Token | Para Qué | Scopes | Duración |
|-------|----------|--------|----------|
| **User Token** | Actuar como usuario | `email`, `pages_read_*` | Corta (2h) |
| **Page Token** | Publicar en la página | N/A (derivado) | Larga (60+ días) |

El Page Token se obtiene del endpoint `/me/accounts` usando el User Token.

---

## 🎯 Scopes Válidos para Facebook Login

### Scopes Utilizados:

- **`email`** - Acceso al email del usuario
- **`user_friends`** - Acceso a lista de amigos
- **`pages_read_engagement`** - Leer engagement de páginas (reactions, comments)
- **`pages_read_user_content`** - Leer contenido que el usuario creó en páginas

### Scopes Adicionales (Opcionales):

- **`pages_read_phone_number`** - Leer número de teléfono de la página
- **`catalog_management`** - Gestionar catálogos de productos

---

## 🛠️ Configuración en Facebook Developer

### Pasos en Facebook Developers:

1. **Ir a:** https://developers.facebook.com/apps
2. **Seleccionar tu app** → Settings → Basic
3. **Copiar:** App ID y App Secret
4. **En:** Settings → Basic → App Domains
   - Agregar: `localhost` (sin protocolo)
5. **En:** Products → Facebook Login → Settings
   - **Valid OAuth Redirect URIs:**
     ```
     https://localhost:8501/
     https://localhost:8501
     ```
   - ⚠️ IMPORTANTE: Debe ser HTTPS, no HTTP
6. **En:** Products → Facebook Login → Settings → Scopes
   - Asegurarse que estén habilitados:
     - [ ] `email`
     - [ ] `user_friends`
     - [ ] `pages_read_engagement`
     - [ ] `pages_read_user_content`

### ⚠️ Verificación de App

Si tu aplicación está en **desarrollo**, algunos scopes están limitados:
- ✅ User tokens de cuentas de test
- ❌ User tokens de cuentas reales (requiere app review)

**Solución:** 
- Crear test account en Facebook Developers
- O esperar a que la app sea aprobada por Meta

---

## 🔐 Certificados HTTPS Locales

Ya que usas certificados en la carpeta `certs/`, asegúrate de:

### 1. Generar Certificados (si aún no lo hiciste):
```bash
cd certs/
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

### 2. Usar en Streamlit:

Editar `.streamlit/config.toml`:
```toml
[server]
sslKeyPath = "/Users/carltocv/Documents/aupa-software/aupa/certs/key.pem"
sslCertPath = "/Users/carltocv/Documents/aupa-software/aupa/certs/cert.pem"
```

### 3. Ejecutar Streamlit:
```bash
streamlit run web_aupa/app.py
```

Streamlit detectará automáticamente HTTPS si los certificados están configurados.

---

## 📝 Variables de Entorno (.env)

Actualizar `.env`:
```
DATABASE_URL=postgresql://aupa:password@localhost:5432/aupa
FACEBOOK_CLIENT_ID=YOUR_APP_ID
FACEBOOK_CLIENT_SECRET=YOUR_APP_SECRET
REDIRECT_URI=https://localhost:8501/
INSTAGRAM_CLIENT_ID=YOUR_INSTAGRAM_APP_ID
TIKTOK_CLIENT_ID=YOUR_TIKTOK_APP_ID
```

---

## ✨ Cambios en el Código

### Archivo: web_aupa/app.py

#### Cambio 1: Scopes en URL de OAuth
```python
# ❌ ANTES
scope=pages_manage_posts,publish_video

# ✅ DESPUÉS
scope=email,user_friends,pages_read_engagement,pages_read_user_content&state=facebook
```

#### Cambio 2: Función exchange_facebook_code()

Ahora el flujo es:
1. Obtener User Token del código de autorización
2. Validar User Token
3. Usar User Token para obtener Page Token (del endpoint `/me/accounts`)
4. Guardar Page Token en BD (es el que se usa para publicar)

```python
def exchange_facebook_code(code):
    # 1. Obtener User Token
    response = requests.get(url, params=params)
    user_token = response.json()["access_token"]
    
    # 2. Validar User Token
    is_valid, user_data = validate_facebook_token(user_token)
    
    # 3. Obtener Page Token
    pages_url = "https://graph.facebook.com/v18.0/me/accounts"
    pages_response = requests.get(pages_url, params={
        "access_token": user_token
    })
    pages = pages_response.json()["data"]
    page_token = pages[0]["access_token"]  # ← Este se guarda en BD
    
    # 4. Retornar Page Token
    return page_token, None, None, expires_in, user_data
```

---

## 🧪 Pruebas

### Prueba 1: Conectar Facebook
1. Ejecutar: `streamlit run web_aupa/app.py`
2. Hacer clic en "Conectar Facebook"
3. Debería redirigir a Facebook Login (sin errores de scopes)
4. Autorizar permisos
5. Debería regresar a la app sin errores

### Prueba 2: Verificar Token en BD
```sql
SELECT user_email, facebook_user_id, token_obtained_at, token_status 
FROM token_exchange_logs 
ORDER BY token_obtained_at DESC LIMIT 1;
```

Debería mostrar `token_status = 'success'`

### Prueba 3: Publicar en Facebook
1. Crear un post en la app
2. Ejecutar: `python web_aupa/worker.py`
3. Verificar que el post aparezca en Facebook
4. Verificar en BD:
```sql
SELECT publish_status, facebook_post_id, platform_response_code 
FROM post_publish_logs 
ORDER BY published_at DESC LIMIT 1;
```

---

## 🆘 Troubleshooting

### Error: "Invalid Redirect URI"
**Causa:** La URL de redirección no coincide exactamente
**Solución:** 
- Asegurarse que sea: `https://localhost:8501/`
- Coincidir exactamente en .env y en Facebook Developers

### Error: "Unsupported get request"
**Causa:** El endpoint GET no es correcto
**Solución:** Verificar versión de Graph API (v18.0 en el código)

### Error: "The user hasn't authorized the app"
**Causa:** Usuario no autorizó los permisos
**Solución:** Volver a intentar y autorizar todos los permisos

### Error: "No se encontraron páginas"
**Causa:** El usuario no es administrador de ninguna página
**Solución:** 
- Crear una página en Facebook
- Hacerse administrador de la página
- Reintentar el login

### Error: "HTTPS Certificate Error"
**Causa:** Certificados autofirmados no son confiables
**Solución:** 
- Aceptar la excepción en el navegador
- Usar `--insecure` en curl si es necesario

---

## 📚 Referencias

- [Facebook Login Permissions](https://developers.facebook.com/docs/facebook-login/permissions)
- [Graph API Access Tokens](https://developers.facebook.com/docs/facebook-login/access-tokens)
- [Page Access Tokens](https://developers.facebook.com/docs/pages/access-tokens)
- [Streamlit HTTPS](https://docs.streamlit.io/library/advanced-features/configuration#serve-ssl-certificates)

---

## ✅ Checklist de Configuración

- [ ] Variables de entorno actualizadas (.env)
- [ ] App Facebook creada en developers.facebook.com
- [ ] App ID y Secret en variables de entorno
- [ ] Redirect URI configurada exactamente en Facebook Developers
- [ ] Scopes habilitados en Facebook Developers
- [ ] Certificados HTTPS generados (en certs/)
- [ ] Config de Streamlit actualizada con rutas de certificados
- [ ] Base de datos actualizada (init.sql ejecutado)
- [ ] Prueba de login con Facebook sin errores
- [ ] Prueba de publicación en Facebook

