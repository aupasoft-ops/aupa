import streamlit as st

def local_css(file_name):
    try:
        # Añadimos encoding="utf-8" para evitar errores de decodificación
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"⚠️ No se encontró el archivo en: {file_name}")
    except Exception as e:
        st.error(f"❌ Ocurrió un error al cargar los estilos: {e}")

# 1. Configuración de página (Debe ser lo primero)
st.set_page_config(
    page_title="Aupa Software",
    page_icon="🚀",
    layout="wide"
)
def mostrar_dashboard():
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
    
    # Hemos unificado el nombre a "🤖 Gestión IA"
    opcion = st.sidebar.radio(
        "Seleccione una herramienta:",
        ["🏠 Inicio", "🗄️ Gestión de Comercios", "🤖 Gestión IA"]
    )

    st.sidebar.divider()
    st.sidebar.info("Aupa Software - Solución Integral")

    # Lógica de navegación corregida
    if opcion == "🏠 Inicio":
        mostrar_dashboard()
    
    elif opcion == "🗄️ Gestión de Comercios":
        import admin_comercios
        
    elif opcion == "🤖 Gestión IA":
        # Ahora el nombre coincide exactamente con la opción del radio
        import gestion_ia

if __name__ == "__main__":
    main()