# ⚡ Quick Fix - Error de Scopes en Facebook OAuth

## 🔴 El Problema

Facebook rechaza los scopes con este error:
```
Invalid Scopes: pages_manage_posts, publish_video, pages_show_list
This message is only shown to developers
```

## ✅ La Solución (3 pasos)

### Paso 1: Actualizar Código ✓ YA HECHO
Los scopes en `app.py` han sido corregidos de:
- ❌ `pages_manage_posts,publish_video` 
- ✅ `email,user_friends,pages_read_engagement,pages_read_user_content`

### Paso 2: Configurar Facebook Developers

1. Ir a: https://developers.facebook.com/apps
2. Seleccionar tu app
3. En **Settings → Basic:**
   - Copiar **App ID** → Variables de entorno
   - Copiar **App Secret** → Variables de entorno

4. En **Products → Facebook Login → Settings:**
   - **Valid OAuth Redirect URIs:**
     ```
     https://localhost:8501/
     ```

5. En **Products → Facebook Login → Settings → Scopes:**
   - Habilitar:
     - ✅ email
     - ✅ user_friends
     - ✅ pages_read_engagement
     - ✅ pages_read_user_content

### Paso 3: Verificar Configuración Local

```bash
# 1. Actualizar .env con credenciales de Facebook
cat > .env << 'EOF'
DATABASE_URL=postgresql://aupa:password@localhost:5432/aupa
FACEBOOK_CLIENT_ID=YOUR_APP_ID
FACEBOOK_CLIENT_SECRET=YOUR_APP_SECRET
REDIRECT_URI=https://localhost:8501/
EOF

# 2. Validar configuración
python validate_facebook_setup.py

# 3. Iniciar aplicación
streamlit run web_aupa/app.py
```

---

## 🔑 Lo que cambió en el código

### Nueva función: exchange_facebook_code()

Ahora el flujo es más robusto:

```python
1. Usuario autoriza en Facebook Login
   ↓ (Obtener User Token)
2. Intercambiar código por User Token
   ↓ (Validar User Token)
3. Obtener lista de páginas del usuario
   ↓ (Extraer Page Token)
4. Guardar Page Token en BD
   ↓ (Este se usa para publicar)
5. Publicar en Facebook con Page Token
```

### Por qué Page Token es necesario

| Token | Se Usa Para | Cómo Se Obtiene |
|-------|-------------|-----------------|
| User Token | Obtener info de usuario y páginas | Intercambiar código OAuth |
| Page Token | **Publicar en la página** | GET /me/accounts con user token |

**El Page Token es lo importante para publicar**, y se obtiene automáticamente en el código actualizado.

---

## 🧪 Validar que Funciona

```bash
# Script de validación (incluido)
python validate_facebook_setup.py

# Debería mostrar:
✅ Variables de Entorno
✅ Credenciales de Facebook
✅ URL de OAuth
✅ Scopes
✅ Graph API
✅ Base de Datos
```

---

## 📚 Archivos Actualizados

- `web_aupa/app.py` → Scopes corregidos + Page Token
- `CORRECCION_SCOPES_FACEBOOK.md` → Guía detallada
- `validate_facebook_setup.py` → Script de validación

---

## ⚠️ Errores Comunes

### "Invalid Redirect URI"
```
Solución: Asegurar que sea exactamente:
https://localhost:8501/
(con la / al final)
```

### "The user hasn't authorized the app"
```
Solución: En Facebook Developer, agregar a las cuentas de test
Ir a: Roles → Test Users → Crear
```

### "Certificate verify failed"
```
Si usas certificados locales, agregar en Streamlit:
[server]
sslKeyPath = "certs/key.pem"
sslCertPath = "certs/cert.pem"
```

---

## ✨ Próximos Pasos

1. ✅ Actualizar .env con credenciales reales
2. ✅ Configurar URLs en Facebook Developers
3. ✅ Ejecutar `python validate_facebook_setup.py`
4. ✅ Hacer clic en "Conectar Facebook" en la app
5. ✅ Autorizar permisos en Facebook
6. ✅ Crear un post y publicarlo
7. ✅ Verificar en Facebook que aparezca el post

---

**¿Listo para probar?**

```bash
python validate_facebook_setup.py
```

Si todo está verde ✅, ejecuta:

```bash
streamlit run web_aupa/app.py
```

