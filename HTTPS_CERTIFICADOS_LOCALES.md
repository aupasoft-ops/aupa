# 🔐 Configurar HTTPS Local con Certificados para Facebook OAuth

## ⚠️ Por qué HTTPS es Necesario

Facebook **obliga** HTTPS para OAuth. Los certificados locales te permiten usar HTTPS en desarrollo.

---

## 📋 Paso 1: Crear Certificados Autofirmados

### En macOS (Tu caso):

```bash
# Navegar a la carpeta certs
cd /Users/carltocv/Documents/aupa-software/aupa/certs

# Generar certificado privado (válido 365 días)
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365

# Te pedirá información (puedes dejar en blanco con Enter):
# Country Name (2 letter code) [AU]: [Enter]
# State or Province Name (full name) [Some-State]: [Enter]
# Locality Name (eg, city) []: [Enter]
# Organization Name (eg, company) [Internet Widgits Pty Ltd]: AUPA
# Organizational Unit Name (eg, section) []: Dev
# Common Name (eg, your name or your server's hostname) []: localhost
# Email Address []: dev@aupa.local

# Resultado:
# - cert.pem (certificado, ~2KB)
# - key.pem (llave privada, ~3KB)
```

### Verificar que se crearon:

```bash
ls -la /Users/carltocv/Documents/aupa-software/aupa/certs/

# Debería mostrar:
# -rw-r--r--  cert.pem
# -rw-r--r--  key.pem
```

---

## 📝 Paso 2: Configurar Streamlit para usar HTTPS

### Crear archivo `.streamlit/config.toml`

```bash
mkdir -p /Users/carltocv/Documents/aupa-software/aupa/.streamlit
```

### Crear el archivo de configuración:

```bash
cat > /Users/carltocv/Documents/aupa-software/aupa/.streamlit/config.toml << 'EOF'
[server]
# Puerto donde corre Streamlit
port = 8501

# Certificados HTTPS
sslKeyPath = "/Users/carltocv/Documents/aupa-software/aupa/certs/key.pem"
sslCertPath = "/Users/carltocv/Documents/aupa-software/aupa/certs/cert.pem"

# Permitir requests desde localhost
headless = false

[logger]
level = "info"

[client]
showErrorDetails = true
EOF
```

### Verificar que se creó:

```bash
cat /Users/carltocv/Documents/aupa-software/aupa/.streamlit/config.toml
```

---

## 🌐 Paso 3: Configurar Facebook Developers

### 1. Ir a Facebook Developers:
https://developers.facebook.com/apps

### 2. Seleccionar tu app

### 3. En **Products → Facebook Login → Settings**:

**Valid OAuth Redirect URIs:**
```
https://localhost:8501/
```

**⚠️ IMPORTANTE:** 
- Debe ser exactamente `https://` (no http)
- Incluir el `/` al final
- No agregar espacios

### 4. Guardar cambios

---

## 🔐 Paso 4: Confiar en el Certificado en macOS

Cuando Streamlit use HTTPS con certificado autofirmado, el navegador mostrará una advertencia. Para evitar esto:

### Opción A: Agregar Certificado a Keychain (Recomendado)

```bash
# Abrir Keychain Access
open /Applications/Utilities/Keychain\ Access.app

# O agregar directamente:
security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  /Users/carltocv/Documents/aupa-software/aupa/certs/cert.pem
```

### Opción B: Ignorar la advertencia en Chrome

1. Ir a `https://localhost:8501/`
2. Ver advertencia de seguridad
3. Clic en "Avanzado"
4. Clic en "Continuar a localhost (no seguro)"

---

## ▶️ Paso 5: Ejecutar Streamlit

### Terminal 1: Ejecutar la aplicación

```bash
cd /Users/carltocv/Documents/aupa-software/aupa
streamlit run web_aupa/app.py
```

### Debería mostrar:

```
  You can now view your Streamlit app in your browser.

  Local URL: https://localhost:8501
  Network URL: https://192.168.x.x:8501
```

### Terminal 2: Ejecutar el worker (en otra terminal)

```bash
cd /Users/carltocv/Documents/aupa-software/aupa
python web_aupa/worker.py
```

---

## 🧪 Paso 6: Probar OAuth con Facebook

### 1. Abrir navegador:
```
https://localhost:8501
```

### 2. En la app, clic en **"Conectar Facebook"**

### 3. Posibles resultados:

#### ✅ ÉXITO
```
- Redirige a Facebook Login
- Solicita permisos
- Retorna a la app con token válido
- Muestra email del usuario
```

#### ❌ Error: Invalid OAuth Redirect URI
```
Causa: URL no coincide exactamente en Facebook Developers
Solución: 
- Verificar que sea: https://localhost:8501/
- Incluir el / al final
- Sin espacios adicionales
```

#### ❌ Error: Certificate Verify Failed
```
Causa: Certificado autofirmado no es confiable
Solución:
- Abrir navegador en https://localhost:8501
- Aceptar advertencia de seguridad
- Retry
```

#### ❌ Error: Invalid Scopes
```
Causa: Scopes incorrectos en app.py
Solución: Ya está corregido, actualizar app.py
```

---

## 📊 Estructura de Archivos

```
aupa/
├── .streamlit/
│   └── config.toml          ← Configuración de HTTPS
├── certs/
│   ├── cert.pem             ← Certificado (crear con openssl)
│   └── key.pem              ← Llave privada (crear con openssl)
├── web_aupa/
│   ├── app.py               ← App principal Streamlit
│   ├── worker.py            ← Worker de publicación
│   └── audit_logger.py      ← Logger centralizado
├── .env                     ← Variables de entorno
├── init.sql                 ← Script BD
└── README.md
```

---

## 🔍 Debugging

### Ver logs de Streamlit:

```bash
# Terminal donde corre streamlit
# Ver en tiempo real los logs

# Buscar errores de HTTPS:
grep -i "ssl\|certificate\|https" /path/to/logs
```

### Ver si puerto 8501 está en uso:

```bash
lsof -i :8501

# Si hay algo, matar:
kill -9 <PID>
```

### Verificar certificados:

```bash
# Ver contenido del certificado
openssl x509 -in certs/cert.pem -text -noout

# Verificar que private key existe
openssl rsa -in certs/key.pem -check
```

---

## 📝 Variables de Entorno (.env)

Crear archivo `.env` en la raíz:

```bash
cat > /Users/carltocv/Documents/aupa-software/aupa/.env << 'EOF'
# Base de Datos
DATABASE_URL=postgresql://aupa:tu_password@localhost:5432/aupa

# Facebook
FACEBOOK_CLIENT_ID=tu_app_id_aqui
FACEBOOK_CLIENT_SECRET=tu_app_secret_aqui
REDIRECT_URI=https://localhost:8501/

# Instagram (opcional)
INSTAGRAM_CLIENT_ID=tu_instagram_app_id

# TikTok (opcional)
TIKTOK_CLIENT_ID=tu_tiktok_app_id
EOF

# Verificar
cat .env
```

---

## ✅ Checklist Completo

- [ ] Certificados creados en `certs/`
  ```bash
  ls -la certs/cert.pem certs/key.pem
  ```

- [ ] Archivo `.streamlit/config.toml` creado con rutas correctas

- [ ] Variables de entorno configuradas en `.env`:
  - [ ] DATABASE_URL
  - [ ] FACEBOOK_CLIENT_ID
  - [ ] FACEBOOK_CLIENT_SECRET
  - [ ] REDIRECT_URI=https://localhost:8501/

- [ ] Facebook Developers configurado:
  - [ ] Valid OAuth Redirect URI: `https://localhost:8501/`
  - [ ] Scopes habilitados: email, user_friends, pages_read_*

- [ ] Streamlit ejecutándose en HTTPS:
  ```bash
  streamlit run web_aupa/app.py
  # Debería mostrar: Local URL: https://localhost:8501
  ```

- [ ] OAuth funcionando:
  - [ ] Clic en "Conectar Facebook"
  - [ ] Redirige a Facebook sin errores
  - [ ] Retorna a la app con token

- [ ] Publicación funcionando:
  - [ ] Crear post en la app
  - [ ] Ejecutar worker
  - [ ] Verificar post en Facebook

---

## 🆘 Troubleshooting Final

### "ERR_SSL_PROTOCOL_ERROR" en navegador

```
Causa: Certificado no válido para el navegador
Solución:
1. Aceptar advertencia de seguridad
2. O agregar a Keychain (ver Paso 4)
```

### "Connection refused"

```
Causa: Streamlit no está ejecutándose
Solución: Ejecutar en Terminal 1:
streamlit run web_aupa/app.py
```

### "Port already in use"

```
Causa: Ya hay algo usando puerto 8501
Solución:
kill -9 $(lsof -ti :8501)
streamlit run web_aupa/app.py --server.port 8502
```

---

## 📚 Referencias

- [Streamlit SSL Config](https://docs.streamlit.io/library/advanced-features/configuration)
- [Facebook OAuth Docs](https://developers.facebook.com/docs/facebook-login/)
- [OpenSSL Certificates](https://www.openssl.org/)

---

**Listo para probar:**

```bash
# 1. Crear certificados
openssl req -x509 -newkey rsa:4096 -nodes -out certs/cert.pem -keyout certs/key.pem -days 365

# 2. Configurar Streamlit
cat > .streamlit/config.toml << 'EOF'
[server]
sslKeyPath = "/Users/carltocv/Documents/aupa-software/aupa/certs/key.pem"
sslCertPath = "/Users/carltocv/Documents/aupa-software/aupa/certs/cert.pem"
EOF

# 3. Ejecutar
streamlit run web_aupa/app.py
```

