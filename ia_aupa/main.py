import streamlit as st
import requests
import os
import uuid
from dotenv import load_dotenv
from urllib.parse import quote
from pathlib import Path

# 1. Configuración de Rutas y Entorno
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Configuración de n8n (Docker Local)
# Por defecto n8n en Docker usa el puerto 5678
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook-test/publicar-redes")
DEFAULT_OUTPUT = Path(os.getenv("OUTPUT_FOLDER", "./generations"))

if not DEFAULT_OUTPUT.exists():
    DEFAULT_OUTPUT.mkdir(parents=True, exist_ok=True)

class CommerceAI:
    def __init__(self):
        self.img_base_url = "https://image.pollinations.ai/prompt/"
        self.text_base_url = "https://text.pollinations.ai/"

    def generate_text(self, prompt, context="general"):
        """Genera copy persuasivo para redes sociales."""
        prefix = "Actúa como un experto en marketing."
        if context == "vision":
            full_prompt = f"{prefix} Basado en esta descripción de imagen: '{prompt}', crea un post atractivo con emojis y hashtags."
        else:
            full_prompt = f"{prefix} Crea un post para redes sociales sobre: {prompt}. Incluye emojis y hashtags."
        
        try:
            response = requests.get(f"{self.text_base_url}{quote(full_prompt)}", timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"❌ Error en texto: {e}"

    def generate_image(self, prompt):
        """Genera imagen y devuelve la URL y el contenido."""
        seed = uuid.uuid4().int & (1<<32)-1
        width = "1080"
        height = "1080"
        enhanced_prompt = f"{prompt}, professional commercial photography, high quality, social media style"
        image_url = f"{self.img_base_url}{quote(enhanced_prompt)}?width={width}&height={height}&seed={seed}&nologo=true"

        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            filename = f"AI_Gen_{uuid.uuid4().hex[:6]}.png"
            filepath = DEFAULT_OUTPUT / filename
            with open(filepath, "wb") as f:
                f.write(response.content)
            return image_url, response.content
        except Exception as e:
            return None, None

    def post_to_n8n(self, post_text, image_url, platforms):
        """Envía los datos al contenedor de n8n."""
        payload = {
            "text": post_text,
            "image_url": image_url,
            "platforms": platforms,
            "timestamp": str(uuid.uuid4())
        }
        try:
            # Enviamos a la URL del Webhook de n8n
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code in [200, 204]:
                return {"status": "success", "message": "¡Datos enviados a n8n con éxito!"}
            else:
                return {"status": "error", "message": f"n8n respondió: {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# --- INTERFAZ WEB ---
st.set_page_config(page_title="AI Content Studio", page_icon="🚀", layout="wide")
st.title("🚀 AI Aupa Software")

ai = CommerceAI()

with st.sidebar:
    st.header("⚙️ Configuración n8n")
    st.write(f"URL Webhook: `{N8N_WEBHOOK_URL}`")
    redes = st.multiselect("Redes Destino:", ["Instagram", "Facebook", "LinkedIn", "Telegram"], default=["Instagram"])

tab1, tab2, tab3 = st.tabs(["✍️ Texto", "🎨 Imagen", "🔍 Texto desde Imagen"])

if 'txt' not in st.session_state: st.session_state['txt'] = ""
if 'img' not in st.session_state: st.session_state['img'] = ""

# Lógica de generación simplificada para las pestañas
with tab1:
    idea = st.text_area("Idea del post:")
    if st.button("Generar Texto"):
        st.session_state['txt'] = ai.generate_text(idea)
        st.info(st.session_state['txt'])

with tab2:
    img_idea = st.text_input("Descripción de imagen:")
    if st.button("Generar Imagen"):
        url, cont = ai.generate_image(img_idea)
        if url:
            st.session_state['img'] = url
            st.image(cont)

with tab3:
    foto = st.file_uploader("Sube una foto")
    if foto:
        st.image(foto, width=200)
        desc = st.text_input("¿Qué ves en la foto?")
        if st.button("Generar desde Vision"):
            st.session_state['txt'] = ai.generate_text(desc, context="vision")
            st.success(st.session_state['txt'])

st.divider()
if st.session_state['txt'] or st.session_state['img']:
    st.subheader("🚀 Publicar mediante Automatización Local")
    f_text = st.text_area("Texto final:", value=st.session_state['txt'])
    if st.button("📤 ENVIAR A N8N"):
        res = ai.post_to_n8n(f_text, st.session_state['img'], redes)
        st.write(res)