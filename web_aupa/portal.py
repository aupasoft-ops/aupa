import streamlit as st

def local_css(file_name):
    """Carga archivos CSS externos con codificación UTF-8."""
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ Error al cargar estilos: {e}")

# 1. Configuración de página (Debe ser lo primero)
st.set_page_config(
    page_title="Aupa Software",
    page_icon="🚀",
    layout="wide"
)


# 3. Inyección de CSS para ocultar la barra superior "Deploy" y menú
st.markdown("""
    <style>
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0%;
    }
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
        if st.button("Ir a Administración"):
            st.info("Selecciona '🗄️ Gestión de Comercios' en el menú lateral.")
            
    with col2:
        st.subheader("✨ Marketing Digital")
        st.write("Utiliza la inteligencia artificial para crear contenido impactante.")
        if st.button("Ir a Gestión IA"):
            st.info("Selecciona '🤖 Gestión IA' en el menú lateral.")

def main():
    # Menú de navegación lateral
    st.sidebar.title("🛠️ Panel de Control")
    st.sidebar.divider()
    
    opcion = st.sidebar.radio(
        "Seleccione una herramienta:",
        ["🏠 Inicio", "🗄️ Gestión de Comercios", "🤖 Gestión IA"]
    )

    st.sidebar.divider()
    st.sidebar.info("Aupa Software - Solución Integral")

    # Lógica de navegación con ejecución de funciones main()
    if opcion == "🏠 Inicio":
        mostrar_dashboard()
    
    elif opcion == "🗄️ Gestión de Comercios":
        import admin_comercios
        # Ejecutamos la función principal del archivo de administración
        admin_comercios.main()
        
    elif opcion == "🤖 Gestión IA":
        # Nota: Asegúrate de que gestion_ia.py también tenga una función main() 
        # o se ejecutará directamente al importar.
        import gestion_ia

if __name__ == "__main__":
    main()