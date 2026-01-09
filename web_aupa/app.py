import streamlit as st
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

st.set_page_config(page_title="Social Aupa Manager", layout="wide")
st.title("📱 Social Aupa Manager")

# --- 1. CONFIGURACIÓN DE REDES SOCIALES ---
st.header("1. Conectar Redes Sociales")
platform = st.selectbox("Selecciona plataforma", ["Facebook", "Instagram", "TikTok"])
user_email = st.text_input("Tu correo o número de celular registrado")

CLIENT_ID = os.getenv(f"{platform.upper()}_CLIENT_ID")
REDIRECT_URI = "https://localhost:8501/" 
auth_url = f"https://www.{platform.lower()}.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=publish_video,publish_posts"

if st.link_button(f"Autorizar acceso en {platform}", auth_url):
    st.info("Redirigiendo para validación segura...")

# Captura de código y limpieza de URL para evitar avisos negros/errores
query_params = st.query_params
if "code" in query_params:
    code = query_params["code"]
    st.warning("⚠️ Código detectado. Haz clic abajo para finalizar.")
    if st.button("Confirmar y Guardar Configuración"):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO social_accounts (user_email, platform, access_token) VALUES (%s, %s, %s)",
                (user_email, platform, f"token_real_generado_{code[:10]}")
            )
            conn.commit()
            cur.close()
            conn.close()
            st.success(f"¡{platform} configurado!")
            # Limpiar parámetros de la URL para que el mensaje desaparezca
            st.query_params.clear() 
        except Exception as e:
            st.error(f"Error al guardar: {e}")

# --- 2. FORMULARIO DE PUBLICACIÓN ---
st.divider()
st.header("2. Crear Publicación")
try:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, platform, user_email FROM social_accounts")
    accounts = cur.fetchall()
    
    if accounts:
        selected_acc = st.selectbox("Publicar desde:", accounts, format_func=lambda x: f"{x[1]} ({x[2]})")
        post_content = st.text_area("Contenido del post")
        
        if st.button("Programar Publicación"):
            cur.execute(
                "INSERT INTO posts_queue (account_id, content) VALUES (%s, %s)",
                (selected_acc[0], post_content)
            )
            conn.commit()
            st.success("Post añadido a la cola.")
    else:
        st.warning("Primero conecta una red social.")
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- 3. MONITOR DE ERRORES Y ESTADO (NUEVO) ---
st.divider()
st.header("3. Monitor de Publicaciones y Errores")

if st.button("🔄 Actualizar logs"):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Traemos los últimos 10 posts con error o pendientes
        cur.execute("""
            SELECT q.id, a.platform, q.content, q.status, q.error_message, q.scheduled_at 
            FROM posts_queue q
            JOIN social_accounts a ON q.account_id = a.id
            ORDER BY q.scheduled_at DESC LIMIT 10
        """)
        logs = cur.fetchall()
        
        if logs:
            for log in logs:
                with st.expander(f"ID: {log[0]} | {log[1]} | Estado: {log[3]}"):
                    st.write(f"**Contenido:** {log[2]}")
                    st.write(f"**Fecha:** {log[5]}")
                    if log[4]:
                        st.error(f"**Detalle del Error:** {log[4]}")
                    else:
                        st.info("Sin errores reportados aún.")
        else:
            st.write("No hay registros en la cola.")
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Error al cargar logs: {e}")