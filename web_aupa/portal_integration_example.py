"""
Ejemplo de integración del conector de redes sociales en portal.py

Copia y pega esta sección en tu archivo portal.py para agregar
la opción de "Redes Sociales" al menú lateral.
"""

# ======== AGREGAR ESTO EN portal.py ========

# En la sección de imports (al inicio del archivo):
# from social_media_connector import render_social_connector_ui

# En la función main(), cambiar:
# opcion = st.sidebar.radio(
#     "Seleccione una herramienta:",
#     ["🏠 Inicio", "🗄️ Gestión de Comercios", "🤖 Gestión IA", "🔍 Test de Conexión"] #
# )

# Por esto:
# opcion = st.sidebar.radio(
#     "Seleccione una herramienta:",
#     ["🏠 Inicio", "🗄️ Gestión de Comercios", "🤖 Gestión IA", "🌐 Redes Sociales", "🔍 Test de Conexión"] #
# )

# Luego en la sección de condiciones (después de las otras opciones):
# if opcion == "🌐 Redes Sociales":
#     render_social_connector_ui()

# =============================================

# Ejemplo de portal.py completo con integración:

import streamlit as st
from social_media_connector import render_social_connector_ui
from admin_comercios import mostrar_admin_comercios  # Ajusta según tus importaciones
from gestion_ia import mostrar_gestion_ia  # Ajusta según tus importaciones

def local_css(file_name):
    """Carga archivos CSS externos con codificación UTF-8."""
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ Error al cargar estilos: {e}")

# 1. Configuración de página
st.set_page_config(
    page_title="Aupa Software",
    page_icon="🚀",
    layout="wide"
)

# 2. Inyección de CSS
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Cargar CSS local si existe
local_css("style/style.css")

def mostrar_dashboard():
    """Muestra la pantalla de inicio del portal."""
    st.markdown('<p class="main-title">Aupa Software</p>', unsafe_allow_html=True)
    st.write("Bienvenido al centro de mando. Desde aquí puedes orquestar toda tu estrategia digital.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 Administración")
        st.write("Accede a la gestión de comercios para organizar tu base de datos.")
    
    with col2:
        st.subheader("✨ Marketing Digital")
        st.write("Utiliza la inteligencia artificial para crear contenido impactante.")
    
    with col3:
        st.subheader("🌐 Redes Sociales")
        st.write("Conecta tus cuentas de redes sociales de forma segura.")

def main():
    """Función principal del portal."""
    
    # Menú de navegación lateral
    st.sidebar.title("🛠️ Panel de Control")
    st.sidebar.divider()
    
    opcion = st.sidebar.radio(
        "Seleccione una herramienta:",
        [
            "🏠 Inicio",
            "🗄️ Gestión de Comercios",
            "🤖 Gestión IA",
            "🌐 Redes Sociales",
            "🔍 Test de Conexión"
        ]
    )
    
    st.sidebar.divider()
    st.sidebar.info("Aupa Software - Solución Integral")
    
    # Mostrar contenido según la opción seleccionada
    if opcion == "🏠 Inicio":
        mostrar_dashboard()
    
    elif opcion == "🗄️ Gestión de Comercios":
        mostrar_admin_comercios()  # Función que ya tienes
    
    elif opcion == "🤖 Gestión IA":
        mostrar_gestion_ia()  # Función que ya tienes
    
    elif opcion == "🌐 Redes Sociales":
        render_social_connector_ui()  # Nueva funcionalidad
    
    elif opcion == "🔍 Test de Conexión":
        st.title("🔍 Test de Conexión")
        st.write("Verifica la conexión con los servicios...")
        # Agregar tu código de test aquí

if __name__ == "__main__":
    main()
