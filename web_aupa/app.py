import streamlit as st
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Social Aupa Manager", layout="wide")

# Lógica de Navegación Simple
if "page" not in st.session_state:
    st.session_state.page = "home"

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

# Sidebar para navegar
with st.sidebar:
    st.title("Navegación")
    if st.button("🏠 Inicio"):
        st.session_state.page = "home"
    if st.button("⚖️ Política de Privacidad"):
        st.session_state.page = "privacy"

# --- RENDERIZADO DE PÁGINAS ---

if st.session_state.page == "privacy":
    st.title("Política de Privacidad - Aupa Manager")
    st.write(f"**Última actualización:** {datetime.now().strftime('%d/%m/%Y')}")
    
    st.markdown("""
    ### 1. Información que recopilamos
    Nuestra aplicación solicita acceso a sus cuentas de redes sociales mediante OAuth oficial. 
    Solo almacenamos tokens de acceso y datos necesarios para la publicación.
    
    ### 2. Uso de la información
    Los datos se utilizan para permitir la publicación programada y monitorear errores.
    
    ### 3. Protección de datos
    Sus credenciales se almacenan en una base de datos PostgreSQL privada.
    """)
    
    if st.button("Volver al Inicio"):
        st.session_state.page = "home"
        st.rerun()

elif st.session_state.page == "home":
    st.title("📱 Social Aupa Manager")

    # --- 1. CONFIGURACIÓN DE REDES SOCIALES (MODIFICADO) ---
    st.header("1. Conectar Redes Sociales")
    st.write("Selecciona una red social para autorizar el acceso:")
    
    col1, col2, col3 = st.columns(3)
    REDIRECT_URI = "https://localhost:8501/"

    with col1:
        fb_id = os.getenv("FACEBOOK_CLIENT_ID")
        fb_url = f"https://www.facebook.com/v18.0/dialog/oauth?client_id={fb_id}&redirect_uri={REDIRECT_URI}&scope=pages_manage_posts,publish_video"
        if st.link_button("🔵 Conectar Facebook", fb_url):
            st.session_state.last_platform = "Facebook"

    with col2:
        ig_id = os.getenv("INSTAGRAM_CLIENT_ID")
        ig_url = f"https://www.facebook.com/v18.0/dialog/oauth?client_id={ig_id}&redirect_uri={REDIRECT_URI}&scope=instagram_basic,instagram_content_publish"
        if st.link_button("📸 Conectar Instagram", ig_url):
            st.session_state.last_platform = "Instagram"

    with col3:
        tk_id = os.getenv("TIKTOK_CLIENT_ID")
        tk_url = f"https://www.tiktok.com/auth/authorize/?client_key={tk_id}&redirect_uri={REDIRECT_URI}&scope=video.upload,user.info.basic"
        if st.link_button("🎵 Conectar TikTok", tk_url):
            st.session_state.last_platform = "TikTok"

    # Captura de código y guardado automático
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        platform = st.session_state.get("last_platform", "Desconocida")
        
        st.warning(f"⚠️ Autorización detectada para {platform}.")
        if st.button("Confirmar Vinculación"):
            # NUEVO: Captura exhaustiva de excepciones durante el intercambio
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                
                # Simulación de inserción - Aquí es donde capturamos cualquier fallo de DB o lógica
                cur.execute(
                    "INSERT INTO social_accounts (user_email, platform, access_token) VALUES (%s, %s, %s)",
                    ("Usuario_Vinculado", platform, f"token_{code[:10]}")
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"¡{platform} configurado con éxito!")
                st.query_params.clear() 
                
            except psycopg2.Error as db_err:
                st.error(f"❌ Error de Base de Datos al vincular {platform}: {db_err}")
                st.info("Verifica la conexión con PostgreSQL y que la tabla 'social_accounts' exista.")
            except Exception as e:
                # Captura cualquier otro error (Red, errores de lógica, etc.)
                st.error(f"💥 Se rompió el intercambio de tokens para {platform}: {type(e).__name__}")
                st.exception(e) # Esto mostrará el rastro del error para debuggear mejor

    # --- 2. FORMULARIO DE PUBLICACIÓN ---
    st.divider()
    st.header("2. Crear Publicación")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, platform, created_at FROM social_accounts")
        accounts = cur.fetchall()
        
        if accounts:
            selected_acc = st.selectbox("Publicar desde:", accounts, format_func=lambda x: f"{x[1]} (ID: {x[0]})")
            post_content = st.text_area("¿Qué quieres publicar?")
            
            if st.button("Programar Publicación"):
                cur.execute(
                    "INSERT INTO posts_queue (account_id, content) VALUES (%s, %s)",
                    (selected_acc[0], post_content)
                )
                conn.commit()
                st.success("Post añadido a la cola de procesamiento.")
        else:
            st.warning("No hay cuentas conectadas.")
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Error de conexión: {e}")

    # --- 3. MONITOR DE ERRORES ---
    st.divider()
    st.header("3. Monitor de Publicaciones y Errores")
    if st.button("🔄 Actualizar logs"):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
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
                        if log[4]: st.error(f"**Error:** {log[4]}")
            else:
                st.write("No hay registros.")
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Error al cargar logs: {e}")