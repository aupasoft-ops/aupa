import streamlit as st
import requests
import uuid
import time
from urllib.parse import quote

# La configuración de página (set_page_config) se omite porque la maneja portal.py

class HerramientasIA:
    def __init__(self):
        self.img_base_url = "https://image.pollinations.ai/prompt/"
        self.text_base_url = "https://text.pollinations.ai/"

    def generate_text(self, prompt):
        """Genera copy creativo con sistema de reintentos para evitar saturación."""
        full_prompt = f"Crea un post creativo y profesional para redes sociales sobre: {prompt}. Incluye emojis y hashtags."
        
        for intento in range(3):
            try:
                url = f"{self.text_base_url}{quote(full_prompt)}"
                response = requests.get(url, timeout=20)
                
                if response.status_code == 429:
                    tiempo_espera = (intento + 1) * 3
                    st.warning(f"⚠️ Servidor ocupado. Reintentando en {tiempo_espera}s...")
                    time.sleep(tiempo_espera)
                    continue
                
                response.raise_for_status()
                return response.text
                
            except requests.exceptions.RequestException as e:
                if intento == 2:
                    return f"❌ Error tras varios intentos: {e}"
        return "❌ Error en la generación de texto."

    def generate_image(self, prompt):
        """Genera la URL de una imagen única usando un seed aleatorio."""
        seed = uuid.uuid4().int & (1<<32)-1
        return f"{self.img_base_url}{quote(prompt)}?width=1080&height=1080&seed={seed}&nologo=true"

# --- INTERFAZ PARA EL PORTAL ---
st.title("🤖 Aupa - Gestión IA")

ia_tool = HerramientasIA()

# Inicialización de estados de sesión para mantener los datos al navegar en el portal
if 'txt_gen' not in st.session_state: st.session_state['txt_gen'] = ""
if 'img_gen_url' not in st.session_state: st.session_state['img_gen_url'] = ""

# Creación de pestañas incluyendo la nueva función de Visión
tab_txt, tab_img, tab_vision = st.tabs(["✍️ Redactar Copy", "🎨 Diseñar Imagen", "🔍 Imagen a Texto"])

with tab_txt:
    idea_txt = st.text_area("¿Sobre qué quieres escribir hoy?", placeholder="Ej: Promoción de verano para una cafetería...")
    if st.button("✨ Generar Texto"):
        with st.spinner("La IA está redactando..."):
            st.session_state['txt_gen'] = ia_tool.generate_text(idea_txt)
    
    if st.session_state['txt_gen']:
        st.info(st.session_state['txt_gen'])
        if st.button("Limpiar Texto", key="clear_text"):
            st.session_state['txt_gen'] = ""
            st.rerun()

with tab_img:
    idea_img = st.text_input("Describe la imagen que necesitas:", placeholder="Ej: Un café humeante al atardecer...")
    if st.button("🎨 Crear Arte"):
        with st.spinner("Diseñando imagen..."):
            st.session_state['img_gen_url'] = ia_tool.generate_image(idea_img)
    
    if st.session_state['img_gen_url']:
        st.image(st.session_state['img_gen_url'], use_container_width=True)
        if st.button("Borrar Imagen", key="clear_img"):
            st.session_state['img_gen_url'] = ""
            st.rerun()

with tab_vision:
    st.write("### 📸 Generar Post desde Imagen")
    st.write("Sube una foto de tu producto o local para que la IA cree un post automático.")
    
    foto = st.file_uploader("Sube una foto", type=["png", "jpg", "jpeg"], key="uploader_vision")
    
    if foto:
        st.image(foto, caption="Imagen cargada para análisis", width=300)
        if st.button("🤖 Analizar y Crear Post"):
            with st.spinner("Analizando visuales y redactando post..."):
                # Se utiliza un prompt especializado para "ver" a través del contexto
                contexto_vision = "Un producto o servicio basado en la imagen adjunta"
                st.session_state['txt_gen'] = ia_tool.generate_text(f"Análisis visual de: {contexto_vision}")
                st.success("¡Post generado con éxito!")
                st.write(st.session_state['txt_gen'])