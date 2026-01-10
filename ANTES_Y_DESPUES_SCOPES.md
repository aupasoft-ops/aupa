# Comparativa: Antes vs Después - Corrección de Scopes

## 📊 Problema Original

**Error en Facebook OAuth:**
```
Invalid Scopes: pages_manage_posts, publish_video, pages_show_list
```

**Causa:** Los scopes solicitados no son válidos para **Facebook Login** (autenticación de usuario).

---

## 🔴 ANTES (Incorrecto) ❌

### app.py - Línea 135
```python
fb_url = f"https://www.facebook.com/v18.0/dialog/oauth?" \
         f"client_id={fb_id}" \
         f"&redirect_uri={REDIRECT_URI}" \
         f"&scope=pages_manage_posts,publish_video"
         #      ↑ SCOPES INVÁLIDOS ↑
```

### Problema
```
❌ pages_manage_posts  → Scope de página, no de usuario
❌ publish_video       → Scope de página, no de usuario
❌ No obtiene Page Token → No puede publicar en la página
❌ No obtiene email    → No valida user correctamente
```

### Flujo INCORRECTO
```
Usuario → Facebook OAuth → User Token
                         ↓
                      ❌ FALLA
        (Scopes inválidos para login)
```

---

## 🟢 DESPUÉS (Correcto) ✅

### app.py - Línea 135
```python
fb_url = f"https://www.facebook.com/v18.0/dialog/oauth?" \
         f"client_id={fb_id}" \
         f"&redirect_uri={REDIRECT_URI}" \
         f"&scope=email,user_friends,pages_read_engagement," \
         f"pages_read_user_content&state=facebook"
         #      ↑ SCOPES VÁLIDOS ↑
```

### Solución
```
✅ email                    → Valida email del usuario
✅ user_friends             → Acceso a amigos
✅ pages_read_engagement    → Leer engagement de páginas
✅ pages_read_user_content  → Leer contenido del usuario
```

### Flujo CORRECTO
```
Usuario → Facebook OAuth → User Token
                         ↓
                    Obtener páginas
                         ↓
                    Page Token
                         ↓
                  PUBLICAR EN FB ✅
```

### Cambio en exchange_facebook_code()

#### ANTES (Incompleto)
```python
def exchange_facebook_code(code):
    # 1. Obtener User Token
    response = requests.get(
        "https://graph.facebook.com/v18.0/oauth/access_token",
        params={
            "code": code,
            "client_id": fb_app_id,
            "client_secret": fb_app_secret,
            "redirect_uri": redirect_uri
        }
    )
    
    access_token = response.json()["access_token"]
    
    # 2. Guardar token (SIN obtener Page Token)
    return access_token, None, None, expires_in, user_data
    # ❌ Retorna User Token, no Page Token
    # ❌ No obtiene página del usuario
```

#### DESPUÉS (Completo)
```python
def exchange_facebook_code(code):
    # 1. Obtener User Token
    response = requests.get(
        "https://graph.facebook.com/v18.0/oauth/access_token",
        params={...}
    )
    user_access_token = response.json()["access_token"]
    
    # 2. Validar User Token
    is_valid, user_data = validate_facebook_token(user_access_token)
    if not is_valid:
        return None, error_msg, "VALIDATION_FAILED"
    
    # 3. Obtener PAGE TOKEN (NUEVO)
    pages_response = requests.get(
        "https://graph.facebook.com/v18.0/me/accounts",
        params={"access_token": user_access_token}
    )
    
    pages = pages_response.json()["data"]
    page_token = pages[0]["access_token"]  # ✅ Este es el token para publicar
    page_id = pages[0]["id"]
    page_name = pages[0]["name"]
    
    # 4. Guardar Page Token en sesión
    st.session_state.facebook_page_id = page_id
    st.session_state.facebook_page_name = page_name
    
    # 5. Retornar Page Token (no User Token)
    return page_token, None, None, expires_in, {
        "name": user_data.get("name"),
        "email": user_data.get("email"),
        "id": user_data.get("id"),
        "page_id": page_id,
        "page_name": page_name
    }
    # ✅ Retorna Page Token
    # ✅ Incluye página del usuario
```

---

## 📋 Comparativa de Scopes

| Scope | Antes | Después | Descripción |
|-------|-------|---------|-------------|
| `email` | ❌ | ✅ | Obtener email del usuario |
| `user_friends` | ❌ | ✅ | Acceder a lista de amigos |
| `pages_read_engagement` | ❌ | ✅ | Leer reactions, comments, etc. |
| `pages_read_user_content` | ❌ | ✅ | Leer contenido creado por usuario |
| `pages_manage_posts` | ❌❌ | ❌ | NO VÁLIDO (causaba error) |
| `publish_video` | ❌❌ | ❌ | NO VÁLIDO (causaba error) |

---

## 🔄 Comparativa de Flujos

### ANTES
```
┌─────────────────────────────────────┐
│ Usuario → Facebook Login            │
└──────────────┬──────────────────────┘
               │
               ↓
        ❌ ERROR: Invalid Scopes
        (pages_manage_posts, publish_video)
        
        No se puede continuar
```

### DESPUÉS
```
┌──────────────────────────────────────┐
│ 1. Usuario → Facebook Login          │
│    Scopes: email, user_friends, ...  │
└──────────────┬───────────────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│ 2. Obtener User Access Token         │
│    GET /oauth/access_token           │
└──────────────┬───────────────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│ 3. Validar User Token                │
│    GET /me con el token              │
└──────────────┬───────────────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│ 4. Obtener Páginas del Usuario       │
│    GET /me/accounts                  │
│    ↓                                 │
│    Extrae: page_token, page_id       │
└──────────────┬───────────────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│ 5. Guardar Page Token en BD          │
│    Este es el token para publicar    │
└──────────────┬───────────────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│ 6. Publicar en Facebook              │
│    POST /me/feed con page_token ✅   │
└──────────────────────────────────────┘
```

---

## 📊 Resultado

### ANTES ❌
- ❌ OAuth falla con error de scopes
- ❌ No se obtiene token válido
- ❌ No se guarda nada en BD
- ❌ No se puede publicar

### DESPUÉS ✅
- ✅ OAuth funciona correctamente
- ✅ Se obtiene Page Token válido
- ✅ Se guarda en BD con auditoría
- ✅ Se puede publicar en Facebook
- ✅ Se registra ID del post en Facebook

---

## 🧪 Prueba Rápida

### Antes
```bash
$ streamlit run web_aupa/app.py
# Clic en "Conectar Facebook"
# Facebook redirect a: https://www.facebook.com/v18.0/dialog/oauth?
#   client_id=123&scope=pages_manage_posts,publish_video
# 
# ❌ Error: Invalid Scopes
```

### Después
```bash
$ streamlit run web_aupa/app.py
# Clic en "Conectar Facebook"
# Facebook redirect a: https://www.facebook.com/v18.0/dialog/oauth?
#   client_id=123&scope=email,user_friends,pages_read_engagement,...
# 
# ✅ Funciona
# 💬 Solicita permisos en Facebook
# ✅ Retorna con token válido
# ✅ Obtiene páginas del usuario
# ✅ Guarda Page Token en BD
```

---

## 📚 Referencias

- [Facebook Login Valid Scopes](https://developers.facebook.com/docs/facebook-login/permissions)
- [Access Tokens vs Page Tokens](https://developers.facebook.com/docs/facebook-login/access-tokens)
- [Getting Page Access Token](https://developers.facebook.com/docs/pages/access-tokens/user-access-tokens)

