# 🚀 Inicio Rápido - Conector de Redes Sociales

## ✅ Lo que se ha creado

```
✨ Archivos principales:
├── web_aupa/social_media_connector.py      # Clase principal (380 líneas)
├── web_aupa/test_social_media_connector.py # Tests unitarios
└── web_aupa/portal_integration_example.py  # Ejemplo de integración

📚 Documentación:
├── SOCIAL_MEDIA_README.md                  # README completo
├── Documentacion/social_media_setup.md     # Guía detallada
├── Documentacion/database_schema.sql       # Script SQL
├── Documentacion/n8n_flows_guide.py        # Guía de flujos n8n
└── .env.example                            # Ejemplo de variables

🔧 Configuración:
├── setup_social_media.sh                   # Script de instalación
├── ia_aupa/n8n_facebook_flow.json         # Flujo JSON para n8n
└── web_aupa/portal_integration_example.py  # Ejemplo de integración
```

## 📋 Pasos para implementar

### 1️⃣ Clonar variables de entorno
```bash
cd /Users/carltocv/Documents/aupa-software/aupa
cp .env.example .env
# Editar .env con tus credenciales de redes sociales
```

### 2️⃣ Ejecutar script de configuración
```bash
chmod +x setup_social_media.sh
./setup_social_media.sh
```

Este script:
- ✓ Verifica que Docker está corriendo
- ✓ Inicia n8n si no está corriendo
- ✓ Crea la tabla en PostgreSQL
- ✓ Valida conectividad

### 3️⃣ Crear webhooks en n8n

#### Opción A: Manualmente
1. Abrir http://localhost:5678
2. Crear nuevo flujo
3. Copiar estructura de: `Documentacion/n8n_flows_guide.py`
4. Crear para cada plataforma:
   - `facebook-connect`
   - `instagram-connect`
   - `tiktok-connect`

#### Opción B: Usar flujo JSON
1. Ir a http://localhost:5678
2. Click en "Import"
3. Cargar: `ia_aupa/n8n_facebook_flow.json`
4. Duplicar y adaptar para Instagram y TikTok

### 4️⃣ Integrar en portal.py

Opción más simple: Copiar del ejemplo

```python
# Agregar al inicio
from social_media_connector import render_social_connector_ui

# En la función main()
if opcion == "🌐 Redes Sociales":
    render_social_connector_ui()
```

Referencia completa: `web_aupa/portal_integration_example.py`

### 5️⃣ Iniciar la aplicación
```bash
cd web_aupa
streamlit run portal.py
```

Ir a: http://localhost:8501 → Menú lateral → 🌐 Redes Sociales

## 🔐 Obtener Credenciales

### Facebook
1. Ir a: https://developers.facebook.com/apps
2. Crear aplicación nueva → "Consumer" → "Other"
3. Settings → Basic → Copiar App ID y Secret
4. Settings → Basic → Agregar Platform → Website
5. Usar URL: `http://localhost:5678/callback/facebook`

### Instagram
- Usar la misma aplicación de Facebook
- En Settings → Roles → Instagram Testing Users
- Crear cuenta de prueba
- Usar en lugar de credenciales normales

### TikTok
1. Ir a: https://developers.tiktok.com
2. My Apps → Create an app
3. Select "Web" → Fill form
4. Get API Credentials
5. Copiar Client ID y Secret

## 🧪 Testing

### Test rápido
```bash
cd web_aupa
python test_social_media_connector.py
```

### Test completo con pytest
```bash
pip install pytest
pytest test_social_media_connector.py -v
```

### Test manual con curl
```bash
# Test Facebook webhook
curl -X POST http://localhost:5678/webhook/facebook-connect \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "facebook",
    "user_id": "test_user",
    "user_email": "test@ejemplo.com",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S)'"
  }'
```

## 📊 Estructura de carpetas después

```
aupa/
├── .env                                    # Variables de entorno
├── .env.example                            # Plantilla
├── docker-compose.yml                      # (sin cambios)
├── SOCIAL_MEDIA_README.md                 # ← LEER PRIMERO
├── setup_social_media.sh
│
├── web_aupa/
│   ├── portal.py                          # Tu archivo original
│   ├── social_media_connector.py           # ← NUEVO
│   ├── portal_integration_example.py       # ← Para referencia
│   ├── test_social_media_connector.py      # ← Para testing
│   ├── requirements.txt
│   └── ... (otros archivos)
│
├── Documentacion/
│   ├── social_media_setup.md              # ← DOCUMENTACIÓN DETALLADA
│   ├── database_schema.sql                # ← SQL para la BD
│   ├── n8n_flows_guide.py                 # ← Guía de flujos
│   └── ... (otros archivos)
│
└── ia_aupa/
    ├── n8n_facebook_flow.json             # ← Flujo de ejemplo
    └── ... (otros archivos)
```

## 🎯 Checklist Final

- [ ] `.env` configurado con credenciales
- [ ] Script `setup_social_media.sh` ejecutado
- [ ] Tabla de BD creada
- [ ] Webhooks n8n creados (facebook, instagram, tiktok)
- [ ] `social_media_connector.py` en web_aupa/
- [ ] `portal.py` actualizado con integración
- [ ] Tests pasando
- [ ] Portal iniciado y funcional

## ❓ ¿Qué hacer ahora?

### Si todo funciona:
```bash
cd web_aupa
streamlit run portal.py
# → Ir a "Redes Sociales" en el menú
# → Click en "Conectar Facebook"
# → Debería redirigir a Facebook
```

### Si hay errores:
1. Revisar logs de n8n: `docker logs n8n_aupa`
2. Revisar logs de PostgreSQL: `docker logs postgres_db`
3. Verificar `.env` tiene credenciales correctas
4. Ver documentación: `SOCIAL_MEDIA_README.md`

## 📞 Soporte Rápido

**"No aparece la opción de Redes Sociales"**
- Verificar que importaste `render_social_connector_ui`
- Ejecutar: `streamlit run portal.py --logger.level=debug`

**"n8n no está disponible"**
- `docker ps` para verificar contenedores
- `docker-compose up -d n8n` para iniciar

**"No se guarda en BD"**
- Verificar que PostgreSQL está corriendo: `docker ps | grep postgres`
- Verificar tabla existe: `docker exec postgres_db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT * FROM connection_requests;"`

**"Tokens expirados"**
- Implementar refresh tokens en n8n
- Ver: `Documentacion/n8n_flows_guide.py`

## 🎓 Arquitectura

```
Usuario (Streamlit)
    ↓
social_media_connector.py (Python)
    ↓
n8n (Webhooks)
    ↓
PostgreSQL (Almacenamiento)
    ↓
Redes Sociales (OAuth)
```

## 📈 Próximos pasos (opcional)

- [ ] Agregar gestión de permisos granulares
- [ ] Implementar refresh automático de tokens
- [ ] Crear dashboard de análisis de redes
- [ ] Agregar sincronización de contenido
- [ ] Implementar publicación automática
- [ ] Agregar webhooks de redes sociales en n8n

## 💡 Tips

1. **Desarrollo**: Usa `DEBUG=true` en `.env`
2. **Testing**: Crea usuarios de prueba en cada plataforma
3. **Seguridad**: Encripta tokens en producción
4. **Monitoreo**: Revisa los logs regularmente
5. **Rendimiento**: Implementa caching de conexiones

---

**¿Preguntas?** Revisa `SOCIAL_MEDIA_README.md` o `Documentacion/social_media_setup.md`

**Última actualización**: 7 de enero de 2026
