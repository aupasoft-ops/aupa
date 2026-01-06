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

# Configuración de APIs
AYRSHARE_API_KEY = os.getenv("AYRSHARE_API_KEY") # Agrega esto a tu .env
DEFAULT_OUTPUT = Path(os.getenv("OUTPUT_FOLDER", "./generations"))

if not DEFAULT_OUTPUT.exists():
    DEFAULT_OUTPUT.mkdir(parents=True, exist_ok=True)

class CommerceAI:
    def __init__(self):
        self.img_base_url = "https://image.pollinations.ai/prompt/"
        self.text_base_url = "https://text.pollinations.ai/"
        self.ayrshare_url = "https://app.ayrshare.com/api/post" # URL de publicación

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
        width = os.getenv("IMAGE_WIDTH", "1080")
        height = os.getenv("IMAGE_HEIGHT", "1080")
        
        enhanced_prompt = f"{prompt}, professional commercial photography, high quality, social media style"
        # Pollinations devuelve la imagen directamente en la URL
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

    def post_to_social(self, post_text, image_url, platforms):
        """Publica el contenido generado a través de Ayrshare."""
        if not AYRSHARE_API_KEY:
            return {"status": "error", "message": "API Key de Ayrshare no encontrada en .env"}

        headers = {
            "Authorization": f"Bearer {AYRSHARE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "post": post_text,
            "platforms": platforms,
            "mediaUrls": [image_url]
        }

        try:
            response = requests.post(self.ayrshare_url, json=payload, headers=headers)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

# --- INTERFAZ WEB STREAMLIT ---
st.set_page_config(page_title="AI Content Studio", page_icon="🚀", layout="wide")

st.title("🚀 AI Aupa Software")
st.markdown("Crea contenido y publícalo en tus redes sociales automáticamente.")

ai = CommerceAI()

# Barra lateral para redes sociales
with st.sidebar:
    st.header("🎯 Publicación")
    selected_platforms = st.multiselect(
        "Selecciona Plataformas:",
        ["instagram", "facebook", "tiktok", "twitter", "linkedin"],
        default=["instagram"]
    )
    st.info(f"📁 Almacenamiento local: `{os.path.abspath(DEFAULT_OUTPUT)}`")

tab1, tab2, tab3 = st.tabs(["✍️ Generar Texto", "🎨 Generar Imagen", "🔍 Texto desde Imagen"])

# Manejo de estado para publicación cruzada
if 'last_text' not in st.session_state: st.session_state['last_text'] = ""
if 'last_img_url' not in st.session_state: st.session_state['last_img_url'] = ""

with tab1:
    st.subheader("Redacción de Posts")
    tema_texto = st.text_area("¿De qué trata tu publicaciòn?")
    if st.button("✨ Generar Copy"):
        if tema_texto:
            with st.spinner("Escribiendo..."):
                st.session_state['last_text'] = ai.generate_text(tema_texto)
                st.info(st.session_state['last_text'])

with tab2:
    st.subheader("Creación de Imágenes")
    tema_img = st.text_input("Describe la imagen:")
    if st.button("🎨 Crear Imagen"):
        if tema_img:
            with st.spinner("Generando arte..."):
                url, contenido = ai.generate_image(tema_img)
                if url:
                    st.session_state['last_img_url'] = url
                    st.image(contenido, caption="Imagen Generada")
                    st.download_button("⬇️ Descargar", data=contenido, file_name="AI_Image.png")

with tab3:
    st.subheader("Análisis de Imagen (Vision)")
    foto = st.file_uploader("Elige una imagen", type=["jpg", "png", "jpeg"])
    if foto:
        st.image(foto, width=300)
        detalle = st.text_input("¿Agrega descripcion de tu publicaciòn?")
        if st.button("🤖 Generar Post para esta foto"):
            with st.spinner("Analizando..."):
                st.session_state['last_text'] = ai.generate_text(detalle, context="vision")
                st.success(st.session_state['last_text'])

# Sección de publicación global
st.divider()
st.subheader("🚀 Panel de Publicación Directa")
if st.session_state['last_text'] or st.session_state['last_img_url']:
    col1, col2 = st.columns([2, 1])
    with col1:
        final_post = st.text_area("Texto final a publicar:", value=st.session_state['last_text'], height=150)
    with col2:
        if st.session_state['last_img_url']:
            st.image(st.session_state['last_img_url'], width=200, caption="Imagen seleccionada")
        
    if st.button("📤 PUBLICAR EN REDES SOCIALES"):
        if not selected_platforms:
            st.error("Selecciona al menos una plataforma en la barra lateral.")
        else:
            with st.spinner("Publicando en redes..."):
                resultado = ai.post_to_social(final_post, st.session_state['last_img_url'], selected_platforms)
                st.write(resultado)
else:
    st.info("Genera texto o una imagen arriba para habilitar la publicación.")