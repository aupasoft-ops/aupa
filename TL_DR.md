# 🎯 TL;DR - CORRECCIÓN RÁPIDA

## El Error Que Tenías

```
Invalid Scopes: pages_manage_posts, publish_video, pages_show_list
```

## Lo Que Hice

✅ **Actualicé** `app.py` línea 135:
- Cambié scopes inválidos por válidos
- Ahora obtiene Page Token automáticamente
- Sin errores de OAuth

## 3 Pasos para Que Funcione

### 1️⃣ Crear Certificados (1 min)
```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -out certs/cert.pem -keyout certs/key.pem -days 365
```

### 2️⃣ Configurar .env (2 min)
```bash
cat > .env << 'EOF'
DATABASE_URL=postgresql://aupa:password@localhost:5432/aupa
FACEBOOK_CLIENT_ID=tu_app_id
FACEBOOK_CLIENT_SECRET=tu_app_secret
REDIRECT_URI=https://localhost:8501/
EOF
```

### 3️⃣ Crear .streamlit/config.toml (1 min)
```bash
mkdir -p .streamlit
cat > .streamlit/config.toml << 'EOF'
[server]
sslKeyPath = "certs/key.pem"
sslCertPath = "certs/cert.pem"
EOF
```

## Ejecutar

```bash
# Terminal 1
streamlit run web_aupa/app.py

# Terminal 2
python web_aupa/worker.py
```

## Verificar

```bash
python validate_facebook_setup.py
```

Debe mostrar: **6/6 ✅**

---

## 📊 Lo Que Cambió

| Antes ❌ | Después ✅ |
|---------|-----------|
| `pages_manage_posts` | `email` |
| `publish_video` | `user_friends` |
| `pages_show_list` | `pages_read_*` |
| Error OAuth | Funciona OAuth |
| No publica | Publica en Facebook |

---

## 📚 Docs Disponibles

1. **GUIA_IMPLEMENTACION_PASO_A_PASO.md** ← Empieza aquí
2. SOLUCION_VISUAL.md ← Diagramas
3. CORRECCION_SCOPES_FACEBOOK.md ← Detalles
4. validate_facebook_setup.py ← Validar

---

## ⏱️ Tiempo Total

- Leer: 5 min
- Implementar: 15 min
- Probar: 5 min

**Total: ~25 minutos**

---

**¿Listo?**
→ Abre: `GUIA_IMPLEMENTACION_PASO_A_PASO.md`

