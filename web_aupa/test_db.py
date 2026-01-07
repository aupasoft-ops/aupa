import streamlit as st
from database_config import get_connection

def ejecutar_test():
    """Realiza una prueba técnica de comunicación con PostgreSQL."""
    st.subheader("🔍 Diagnóstico de Base de Datos")
    
    with st.status("Verificando parámetros...", expanded=True) as status:
        st.write("Intentando conectar al servidor...")
        conn = get_connection() #
        
        if conn:
            try:
                cur = conn.cursor()
                # Ejecutamos una consulta simple para verificar respuesta del motor SQL
                cur.execute('SELECT version();')
                db_version = cur.fetchone()
                
                st.write("✅ Conexión establecida exitosamente.")
                st.info(f"Versión del servidor: {db_version[0]}")
                
                cur.close()
                status.update(label="Prueba completada con éxito", state="complete", expanded=False)
            except Exception as e:
                st.error(f"❌ Error al ejecutar consulta de prueba: {e}")
                status.update(label="Error en ejecución", state="error")
            finally:
                conn.close()
        else:
            st.error("❌ No se pudo establecer la conexión inicial.")
            status.update(label="Fallo de conexión", state="error")

if __name__ == "__main__":
    ejecutar_test()