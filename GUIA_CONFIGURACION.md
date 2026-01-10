# 🚀 GUÍA DE CONFIGURACIÓN - Sistema de Auditoría OAuth AUPA

## 📋 Prerequisitos

- Python 3.9+
- PostgreSQL 12+
- pip
- Cuenta de Facebook Developer
- Variables de entorno configuradas

---

## 1️⃣ Preparar la Base de Datos

### Opción A: Crear tablas nuevas (primera vez)

```bash
cd /Users/carltocv/Documents/aupa-software/aupa
psql -U aupa -d aupa -f init.sql
```

### Opción B: Actualizar tablas existentes (si ya hay social_accounts)

```bash
# Crear solo las nuevas tablas de auditoría
psql -U aupa -d aupa -c "
CREATE TABLE IF NOT EXISTS token_exchange_logs (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    authorization_code VARCHAR(255),
    access_token VARCHAR(500),
    token_status VARCHAR(50) NOT NULL,
    error_message TEXT,
    error_code VARCHAR(100),
    facebook_user_id VARCHAR(255),
    token_obtained_at TIMESTAMP,
    token_expires_at TIMESTAMP,
    exchange_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

CREATE TABLE IF NOT EXISTS post_publish_logs (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts_queue(id),
    account_id INTEGER REFERENCES social_accounts(id),
    platform VARCHAR(50),
    facebook_post_id VARCHAR(255),
    publish_status VARCHAR(50),
    platform_response_code VARCHAR(50),
    error_details TEXT,
    retry_count INTEGER DEFAULT 0,
    published_at TIMESTAMP,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"
```

---

## 2️⃣ Configurar Variables de Entorno

Editar `.env`:

```bash
# Base de datos
DATABASE_URL=postgresql://aupa:Aupasoftware2025*?@localhost:5432/aupa

# Facebook OAuth - OBTENER DE: https://developers.facebook.com
FACEBOOK_CLIENT_ID=YOUR_FACEBOOK_APP_ID
FACEBOOK_CLIENT_SECRET=YOUR_FACEBOOK_APP_SECRET

# URL de redirección (debe coincidir con la registrada en Facebook)
REDIRECT_URI=https://localhost:8501/
# O si está en desarrollo local:
# REDIRECT_URI=http://localhost:8501/

# Otras plataformas (opcional)
INSTAGRAM_CLIENT_ID=YOUR_INSTAGRAM_APP_ID
TIKTOK_CLIENT_ID=YOUR_TIKTOK_CLIENT_ID
```

---

## 3️⃣ Obtener Credenciales de Facebook

### Paso 1: Crear una Aplicación de Facebook

1. Ir a https://developers.facebook.com/
2. Crear nueva aplicación
3. Seleccionar "Consumidor" como tipo
4. Rellenar nombre y email

### Paso 2: Configurar Facebook Login

1. En el dashboard, buscar "Productos"
2. Agregar "Facebook Login"
3. En Configuración → Facebook Login → Configuración:
   - **URI de redirección válidas**: `https://localhost:8501/` (desarrollo) o tu dominio real
   - **Dominios válidos**: `localhost` (desarrollo) o tu dominio
   - **Uris de redirección de OAuth válidas**: `https://localhost:8501/`

### Paso 3: Configurar Permisos

En Configuración → Permisos:

```
PERMISOS DE USUARIO:
- email        (leer email del usuario)

PERMISOS DE PÁGINA:
- pages_manage_posts      (publicar en páginas)
- publish_video           (video)
- pages_read_engagement   (leer engagement)
```

### Paso 4: Obtener Credenciales

En Configuración → Básica:
- **App ID**: Copiar a `FACEBOOK_CLIENT_ID`
- **App Secret**: Copiar a `FACEBOOK_CLIENT_SECRET`

---

## 4️⃣ Instalar Dependencias

```bash
cd web_aupa
pip install -r ../requirements.txt
```

Si no existe requirements.txt, instalar:

```bash
pip install streamlit psycopg2-binary requests python-dotenv
```

---

## 5️⃣ Validar Configuración

```bash
cd /Users/carltocv/Documents/aupa-software/aupa
python test_oauth_implementation.py
```

Debería mostrar:
- ✅ Variables de entorno configuradas
- ✅ Conexión a BD correcta
- ✅ Tablas de auditoría creadas
- ✅ Módulos Python instalados

---

## 6️⃣ Ejecutar la Aplicación

### Terminal 1: Aplicación Streamlit

```bash
cd /Users/carltocv/Documents/aupa-software/aupa
streamlit run web_aupa/app.py
```

La aplicación estará en: `http://localhost:8501`

### Terminal 2: Worker (en paralelo)

```bash
cd /Users/carltocv/Documents/aupa-software/aupa/web_aupa
python worker.py
```

---

## 🧪 Flujo de Prueba

### 1. Probar Conexión de Facebook

1. Abrir aplicación Streamlit (http://localhost:8501)
2. Click en "Conectar Facebook"
3. Se redirige a Facebook para autorizar
4. Completar autorización
5. Volver a la aplicación
6. Ingresar email válido
7. Click "Confirmar Vinculación"

**Esperado:**
- ✅ Mensaje de éxito
- ✅ Registro en `token_exchange_logs` con status='success'
- ✅ Fila en `social_accounts` con token real (no simulado)
- ✅ Token tiene fecha de expiración

### 2. Probar Publicación

1. En sección "2. Crear Publicación"
2. Seleccionar cuenta de Facebook conectada
3. Escribir contenido
4. Click "Programar Publicación"

**Esperado:**
- ✅ Post agregado a `posts_queue`

### 3. Verificar que Worker Publica

1. Worker debe detectar post pendiente
2. Validar token antes de publicar
3. Publicar REALMENTE en Facebook
4. Si éxito:
   - ✅ Post aparece en Facebook
   - ✅ `posts_queue.status = 'sent'`
   - ✅ Registro en `post_publish_logs` con status='published'
   - ✅ facebook_post_id tiene valor

### 4. Revisar Auditoría

1. En tab "Auditoría de Tokens":
   - Ver historial de intercambios
   - IP registrada
   - Timestamp exacto

2. En tab "Errores":
   - Ver publicaciones fallidas
   - Detalles del error
   - Código de error de Facebook API

---

## 🐛 Troubleshooting

### Error: "FACEBOOK_CLIENT_ID no configurada"
```
Solución: Asegúrate que .env tiene FACEBOOK_CLIENT_ID
```

### Error: "Tabla social_accounts no existe"
```
Solución: Ejecutar: psql -U aupa -d aupa -f init.sql
```

### Error: "Token inválido"
```
Solución: 
- Verifica que App Secret sea correcto
- El token puede estar expirado (regenerar en Facebook)
- Verifica permisos en la app de Facebook
```

### Error: "Redirect URI mismatch"
```
Solución:
- El REDIRECT_URI en .env debe coincidir exactamente con Facebook
- Incluir protocolo: https:// o http://
- Incluir puerto: :8501
- Incluir trailing slash: /
```

### Error: "Post no se publica"
```
Solución:
- Verifica que el worker esté ejecutándose: ps aux | grep worker.py
- Ver logs del worker para errores
- Revisar token_exchange_logs si token es válido
- Verificar que página está vinculada (platform_user_id en social_accounts)
```

### Error: "psycopg2.OperationalError: could not connect to server"
```
Solución:
- Verificar PostgreSQL está ejecutándose: pg_isready
- Verificar DATABASE_URL es correcto
- Verificar credenciales de acceso
```

---

## 📊 Monitoreo y Logs

### Ver registros de intercambios de tokens:

```sql
SELECT * FROM token_exchange_logs 
ORDER BY exchange_timestamp DESC 
LIMIT 10;
```

### Ver registros de publicaciones:

```sql
SELECT * FROM post_publish_logs 
ORDER BY logged_at DESC 
LIMIT 10;
```

### Ver estadísticas:

```sql
-- Tokens exitosos por plataforma
SELECT platform, COUNT(*) as total, 
       COUNT(CASE WHEN token_status='success' THEN 1 END) as exitosos
FROM token_exchange_logs
WHERE exchange_timestamp > NOW() - INTERVAL '7 days'
GROUP BY platform;

-- Publicaciones exitosas
SELECT platform, COUNT(*) as total,
       COUNT(CASE WHEN publish_status='published' THEN 1 END) as publicadas
FROM post_publish_logs
WHERE logged_at > NOW() - INTERVAL '7 days'
GROUP BY platform;
```

---

## 🔒 Seguridad

✅ Los tokens se validan antes de guardar
✅ Se registra IP del cliente en cada operación
✅ Los tokens están truncados en logs (por seguridad)
✅ Se registran intentos fallidos para auditoría
✅ Los errores no exponen tokens completos

---

## 📞 Soporte

Si hay problemas:

1. Ejecutar: `python test_oauth_implementation.py`
2. Revisar logs del worker
3. Verificar `token_exchange_logs` para errores
4. Revisar consola de Streamlit para excepciones

---

## ✨ Próximos Pasos

- [ ] Configurar HTTPS para producción
- [ ] Agregar refresh automático de tokens
- [ ] Implementar publicación en Instagram
- [ ] Implementar publicación en TikTok
- [ ] Crear dashboard de reportes
- [ ] Agregar notificaciones por email de errores
