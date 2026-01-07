import streamlit as st
import requests
import os
import uuid
import time
from dotenv import load_dotenv
from urllib.parse import quote
from pathlib import Path

# 1. Configuración de Rutas y Entorno
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Prioridad: host.docker.internal para comunicación Host->Docker en Windows/Mac
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://host.docker.internal:5678/webhook/publicar-redes")

class MultiCommerceAI:
    def __init__(self):
        self.img_base_url = "https://image.pollinations.ai/prompt/"
        self.text_base_url = "https://text.pollinations.ai/"

    def generate_text(self, prompt, nombre_comercio):
        """Genera copy con sistema de reintentos y esperas para evitar el error 429."""
        full_prompt = f"Actúa como experto en marketing para '{nombre_comercio}'. Crea un post para redes sociales sobre: {prompt}. Incluye emojis y hashtags."
        
        for intento in range(3):
            try:
                url = f"{self.text_base_url}{quote(full_prompt)}"
                response = requests.get(url, timeout=20)
                
                if response.status_code == 429:
                    # Espera progresiva: 3s, 6s, 9s
                    tiempo_espera = (intento + 1) * 3
                    st.warning(f"⚠️ Servidor saturado. Reintentando en {tiempo_espera}s... (Intento {intento+1}/3)")
                    time.sleep(tiempo_espera)
                    continue
                
                response.raise_for_status()
                return response.text
                
            except requests.exceptions.RequestException as e:
                if intento == 2:
                    return f"❌ No se pudo generar el texto tras varios intentos. Error: {e}"
        return "❌ Error desconocido en la generación de texto."

    def generate_image(self, prompt):
        """Genera la URL de la imagen con un seed aleatorio para unicidad."""
        seed = uuid.uuid4().int & (1<<32)-1
        return f"{self.img_base_url}{quote(prompt)}?width=1080&height=1080&seed={seed}&nologo=true"

    def verify_or_link_social(self, comercio_id, action="verify"):
        """Envía señal a n8n con diagnóstico técnico para detectar errores 404 o de conexión."""
        payload = {
            "comercio_id": comercio_id,
            "action": action,
            "type": "connection_request"
        }
        try:
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=7)
            if response.status_code in [200, 204]:
                return True
            elif response.status_code == 404:
                st.error("❌ Error 404: El Webhook no está activo en n8n. Asegúrate de que el flujo esté en 'ON' y la URL sea correcta.")
            else:
                st.error(f"⚠️ n8n respondió {response.status_code}: {response.text}")
            return False
        except requests.exceptions.ConnectionError:
            st.error("❌ Error de Conexión: No se pudo conectar con n8n en Docker. Revisa si el contenedor está corriendo.")
            return False
        except Exception as e:
            st.error(f"❌ Error Inesperado: {e}")
            return False

    def post_to_n8n(self, post_text, image_url, platforms, comercio_id):
        """Publica el contenido final a través del flujo de n8n."""
        payload = {
            "comercio_id": comercio_id,
            "text": post_text,
            "image_url": image_url,
            "platforms": platforms,
            "timestamp": str(uuid.uuid4())
        }
        try:
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=15)
            if response.status_code in [200, 204]:
                return {"status": "success", "msg": "¡Publicación enviada con éxito!"}
            return {"status": "error", "msg": f"Código {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="AI Multi-Comercio Pro", page_icon="🏢", layout="wide")
st.title("🚀 AI Aupa Software")

ai = MultiCommerceAI()

# Base de datos simulada de comercios
COMERCIOS = {
    "comercio_001": "Panadería La Espiga",
    "comercio_002": "Ferretería Central",
    "comercio_003": "Café del Barrio"
}

if 'connected_id' not in st.session_state: 
    st.session_state['connected_id'] = None

# BARRA LATERAL: Control de Acceso y Configuración
with st.sidebar:
    st.header("🏢 1. Selección y Vinculación")
    id_sel = st.selectbox("Selecciona tu comercio:", options=list(COMERCIOS.keys()), format_func=lambda x: COMERCIOS[x])
    
    if st.button(f"🔗 Vincular Redes de {COMERCIOS[id_sel]}"):
        with st.spinner("Validando conexión con n8n..."):
            if ai.verify_or_link_social(id_sel, action="link"):
                st.session_state['connected_id'] = id_sel
                st.success(f"✅ {COMERCIOS[id_sel]} vinculado.")
    
    st.divider()
    if st.session_state['connected_id'] == id_sel:
        st.header("⚙️ 2. Configuración de Destino")
        redes = st.multiselect("Publicar en:", ["Instagram", "Facebook", "TikTok", "LinkedIn"], default=["Instagram"])
    else:
        st.warning("⚠️ Debes vincular este comercio para habilitar la creación.")

# CUERPO PRINCIPAL: Solo se activa si el comercio está vinculado
if st.session_state['connected_id'] == id_sel:
    tab1, tab2, tab3 = st.tabs(["✍️ Generar Texto", "🎨 Generar Imagen", "🔍 Análisis de Producto"])
    
    if 'txt' not in st.session_state: st.session_state['txt'] = ""
    if 'img_url' not in st.session_state: st.session_state['img_url'] = ""

    with tab1:
        idea = st.text_area(f"¿Qué quieres promocionar hoy en {COMERCIOS[id_sel]}?")
        if st.button("✨ Generar Copy"):
            with st.spinner("La IA está escribiendo..."):
                st.session_state['txt'] = ai.generate_text(idea, COMERCIOS[id_sel])
                st.info(st.session_state['txt'])

    with tab2:
        img_idea = st.text_input("Describe la imagen que imaginas:")
        if st.button("🎨 Crear Arte"):
            with st.spinner("Diseñando imagen..."):
                st.session_state['img_url'] = ai.generate_image(img_idea)
                st.image(st.session_state['img_url'], use_container_width=True)

    with tab3:
        st.write("Sube una foto de tu producto para crear un post automático.")
        foto = st.file_uploader("Subir imagen", type=["png", "jpg", "jpeg"])
        if foto:
            st.image(foto, width=300)
            if st.button("🤖 Analizar y Crear Post"):
                with st.spinner("Analizando visuales..."):
                    st.session_state['txt'] = ai.generate_text("Producto nuevo en tienda", COMERCIOS[id_sel])
                    st.success(st.session_state['txt'])

    # PANEL DE PUBLICACIÓN FINAL
    st.divider()
    if st.session_state['txt'] or st.session_state['img_url']:
        st.subheader(f"🚀 Revisión Final: {COMERCIOS[id_sel]}")
        col_t, col_i = st.columns([2, 1])
        
        with col_t:
            final_txt = st.text_area("Texto del post:", value=st.session_state['txt'], height=200)
        with col_i:
            if st.session_state['img_url']:
                st.image(st.session_state['img_url'], caption="Imagen seleccionada")

        if st.button("📤 ENVIAR A PUBLICACIÓN AUTOMÁTICA"):
            if not redes:
                st.error("Selecciona al menos una red social en la barra lateral.")
            else:
                with st.spinner("Enviando a n8n..."):
                    resultado = ai.post_to_n8n(final_txt, st.session_state['img_url'], redes, id_sel)
                    st.write(resultado)
else:
    st.info("👈 Selecciona un comercio y haz clic en 'Vincular Redes' en el menú lateral para comenzar.")