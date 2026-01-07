import streamlit as st


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

# 2. Inyección de CSS (Ocultar encabezado y pie de página)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def mostrar_dashboard():
    """Muestra la pantalla de inicio del portal."""
    st.markdown('<p class="main-title">Aupa Software</p>', unsafe_allow_html=True)
    st.write("Bienvenido al centro de mando. Desde aquí puedes orquestar toda tu estrategia digital.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Administración")
        st.write("Accede a la gestión de comercios para organizar tu base de datos.")
    with col2:
        st.subheader("✨ Marketing Digital")
        st.write("Utiliza la inteligencia artificial para crear contenido impactante.")

def main():
    # Menú de navegación lateral
    st.sidebar.title("🛠️ Panel de Control")
    st.sidebar.divider()
    
    opcion = st.sidebar.radio(
        "Seleccione una herramienta:",
        ["🏠 Inicio", "🗄️ Gestión de Comercios", "🤖 Gestión IA", "🌐 Redes Sociales", "🔍 Test de Conexión"]
    )

    st.sidebar.divider()
    st.sidebar.info("Aupa Software - Solución Integral")

    # Lógica de navegación
    if opcion == "🏠 Inicio":
        mostrar_dashboard()
    
    elif opcion == "🗄️ Gestión de Comercios":
        import admin_comercios
        admin_comercios.main()
        
    elif opcion == "🤖 Gestión IA":
        import gestion_ia
        # Asegúrate de que gestion_ia tenga una función main() o lógica de inicio
    
    elif opcion == "🌐 Redes Sociales":
        # Renderiza la interfaz del conector social
        render_social_connector_ui()
    elif opcion == "🔍 Test de Conexión":
        import test_db
        test_db.ejecutar_test() # Llamamos a la función del archivo de prueba

if __name__ == "__main__":
    main()