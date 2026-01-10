# 🚀 GUÍA RÁPIDA: Corregir Error de Scopes Facebook

## El Error Que Recibiste

```
Este contenido no está disponible en este momento
Invalid Scopes: pages_manage_posts, publish_video, pages_show_list.
This message is only shown to developers.
```

## ✅ Ya Está Corregido

El código ya fue actualizado en `web_aupa/app.py`. Ahora necesitas:

---

## 📋 Pasos (Orden Exacto)

### PASO 1: Crear Certificados HTTPS (3 min)

**Abrir Terminal y ejecutar:**

```bash
cd /Users/carltocv/Documents/aupa-software/aupa/certs

# Generar certificado
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365

# Presionar Enter para cada pregunta (dejar por defecto)
# Cuando pida "Common Name" escribir: localhost
```

**Verificar:**
```bash
ls -la /Users/carltocv/Documents/aupa-software/aupa/certs/
# Debería ver: cert.pem y key.pem
```

---

### PASO 2: Configurar Streamlit

**Crear archivo de configuración:**

```bash
mkdir -p /Users/carltocv/Documents/aupa-software/aupa/.streamlit

cat > /Users/carltocv/Documents/aupa-software/aupa/.streamlit/config.toml << 'EOF'
[server]
port = 8501
sslKeyPath = "/Users/carltocv/Documents/aupa-software/aupa/certs/key.pem"
sslCertPath = "/Users/carltocv/Documents/aupa-software/aupa/certs/cert.pem"
EOF
```

---

### PASO 3: Crear Archivo .env

**Crear archivo `.env` en la raíz del proyecto:**

```bash
cd /Users/carltocv/Documents/aupa-software/aupa

cat > .env << 'EOF'
DATABASE_URL=postgresql://aupa:tu_password@localhost:5432/aupa
FACEBOOK_CLIENT_ID=tu_app_id
FACEBOOK_CLIENT_SECRET=tu_app_secret
REDIRECT_URI=https://localhost:8501/
EOF
```

---

### PASO 4: Obtener Credenciales de Facebook

**Ir a:** https://developers.facebook.com/apps

**4.1 Copiar credenciales:**
1. Seleccionar tu app
2. Settings → Basic
3. Copiar **App ID** → `.env` como `FACEBOOK_CLIENT_ID`
4. Copiar **App Secret** → `.env` como `FACEBOOK_CLIENT_SECRET`

**4.2 Configurar URLs:**
1. Settings → Basic
2. En **App Domains:** agregar `localhost`
3. En **Products → Facebook Login → Settings**
4. Valid OAuth Redirect URIs:
   ```
   https://localhost:8501/
   ```

---

### PASO 5: Instalar/Verificar Dependencias

```bash
cd /Users/carltocv/Documents/aupa-software/aupa

# Instalar requirements
pip install -r requirements.txt

# Verificar psycopg2
pip install psycopg2-binary
```

---

### PASO 6: Base de Datos

**Crear/actualizar tablas:**

```bash
psql -U aupa -d aupa -f /Users/carltocv/Documents/aupa-software/aupa/init.sql
```

---

### PASO 7: Validar Configuración

```bash
cd /Users/carltocv/Documents/aupa-software/aupa

python validate_facebook_setup.py
```

**Debería mostrar 6 items con ✅ verde**

---

### PASO 8: Ejecutar Aplicación

**Terminal 1 - Aplicación Streamlit:**
```bash
cd /Users/carltocv/Documents/aupa-software/aupa
streamlit run web_aupa/app.py
```

Debería mostrar:
```
Local URL: https://localhost:8501
```

**Terminal 2 - Worker (dejar ejecutándose):**
```bash
cd /Users/carltocv/Documents/aupa-software/aupa
python web_aupa/worker.py
```

---

### PASO 9: Probar en Navegador

**Abrir:** `https://localhost:8501`

**En el navegador:**
1. Ver advertencia de certificado (normal con local)
2. Clic en "Continuar a localhost (no seguro)"
3. Clic en **"🔵 Conectar Facebook"**
4. Redirige a Facebook Login
5. Autorizar permisos
6. Retorna a la app ✅

---

## ✨ Si Todo Funcionó

### Verificar en BD:

```bash
psql -U aupa -d aupa

# Ver token registrado
SELECT user_email, token_status, token_obtained_at 
FROM token_exchange_logs ORDER BY token_obtained_at DESC LIMIT 1;

# Debería mostrar:
# user_email | token_status | token_obtained_at
# test@... | success | 2026-01-09 ...
```

### Crear un Post:

1. En la app, crear un post
2. Programa para "Publicar ahora" o más tarde
3. Verifica que aparezca en Facebook
4. En BD:
```sql
SELECT publish_status, facebook_post_id 
FROM post_publish_logs ORDER BY published_at DESC LIMIT 1;
```

---

## ❌ Si Algo Falla

### Error: "Invalid Redirect URI"
```
Solución: En Facebook Developers, verificar:
- Valid OAuth Redirect URI: https://localhost:8501/
- Exactamente con la / al final
- Sin espacios
```

### Error: "The user hasn't authorized the app"
```
Solución: En Facebook Developers:
- Crear test user: Roles → Test Users → Create
- Usar ese test user para login
```

### Error: "Certificate verify failed"
```
Solución: En navegador:
1. Aceptar el warning de certificado
2. Clic en "Continuar a localhost (no seguro)"
3. Retry
```

### Error: "Connection refused"
```
Solución: Verificar que Streamlit esté corriendo:
Terminal 1: streamlit run web_aupa/app.py
```

---

## 📚 Documentación Disponible

Para más detalles, ver:
- `CORRECCION_SCOPES_FACEBOOK.md` - Explicación técnica
- `QUICK_FIX_SCOPES.md` - Resumen rápido
- `HTTPS_CERTIFICADOS_LOCALES.md` - Configurar HTTPS
- `ANTES_Y_DESPUES_SCOPES.md` - Comparativa de código

---

## ✅ Checklist de Verificación

- [ ] Certificados creados en `certs/`
- [ ] `.streamlit/config.toml` creado con rutas correctas
- [ ] `.env` configurado con credenciales reales
- [ ] Facebook Developers: App ID y Secret en `.env`
- [ ] Facebook Developers: Redirect URI = `https://localhost:8501/`
- [ ] Base de datos actualizada con `init.sql`
- [ ] `python validate_facebook_setup.py` muestra 6/6 ✅
- [ ] `streamlit run web_aupa/app.py` ejecutándose en HTTPS
- [ ] `python web_aupa/worker.py` ejecutándose
- [ ] Navegador: Conectar Facebook funciona ✅

---

## 🎉 Listo!

Una vez completados todos los pasos:

1. **App en:** `https://localhost:8501`
2. **Conectar Facebook:** Funciona sin errores
3. **Crear posts:** Se publican en Facebook automáticamente
4. **Auditoría:** Todo registrado en BD

**¡Sistema en producción!**

