import streamlit as st
import psycopg2
import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import socket
from audit_logger import audit_logger

load_dotenv()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Social Aupa Manager", layout="wide")

# Lógica de Navegación Simple
if "page" not in st.session_state:
    st.session_state.page = "home"

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def get_client_ip():
    """Obtiene la IP del cliente para auditoría."""
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "0.0.0.0"

def validate_facebook_token(access_token):
    """Valida que el token de Facebook sea válido y obtiene información del usuario."""
    try:
        url = "https://graph.facebook.com/v18.0/me"
        params = {
            "access_token": access_token,
            "fields": "id,name,email"
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, response.json()
    except Exception as e:
        return False, {"error": str(e)}

def exchange_facebook_code(code):
    """Realiza el intercambio del código de autorización por un access_token de Facebook.
    Primero obtiene el user token, luego obtiene el page access token para publicar."""
    try:
        fb_app_id = os.getenv("FACEBOOK_CLIENT_ID")
        fb_app_secret = os.getenv("FACEBOOK_CLIENT_SECRET")
        redirect_uri = os.getenv("REDIRECT_URI", "https://localhost:8501/")
        
        if not fb_app_id or not fb_app_secret:
            return None, "Faltan credenciales de Facebook en variables de entorno", "MISSING_CREDENTIALS"
        
        # Paso 1: Obtener USER ACCESS TOKEN
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            "client_id": fb_app_id,
            "client_secret": fb_app_secret,
            "redirect_uri": redirect_uri,
            "code": code
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", "Unknown error")
            error_code = error_data.get("error", {}).get("code", "UNKNOWN")
            return None, error_msg, error_code
        
        user_token_data = response.json()
        user_access_token = user_token_data.get("access_token")
        expires_in = user_token_data.get("expires_in")
        
        # Validar el user token obtenido
        is_valid, user_data = validate_facebook_token(user_access_token)
        if not is_valid:
            error_msg = user_data.get("error", {}).get("message", "Token validation failed")
            return None, error_msg, "VALIDATION_FAILED"
        
        # Paso 2: Obtener PAGE ACCESS TOKEN para publicar
        # Necesitamos obtener las páginas del usuario y un page token
        pages_url = "https://graph.facebook.com/v18.0/me/accounts"
        pages_params = {
            "access_token": user_access_token,
            "limit": 100
        }
        
        pages_response = requests.get(pages_url, params=pages_params, timeout=10)
        
        if pages_response.status_code == 200:
            pages_data = pages_response.json()
            pages = pages_data.get("data", [])
            
            if pages:
                # Usar la primera página disponible
                page_token = pages[0].get("access_token")
                page_id = pages[0].get("id")
                page_name = pages[0].get("name")
                
                # Guardar info de la página en session
                st.session_state.facebook_page_id = page_id
                st.session_state.facebook_page_name = page_name
                
                # Retornar el PAGE TOKEN (es el que usaremos para publicar)
                return page_token, None, None, expires_in, {
                    "name": user_data.get("name"),
                    "email": user_data.get("email"),
                    "id": user_data.get("id"),
                    "page_id": page_id,
                    "page_name": page_name
                }
            else:
                return None, "No se encontraron páginas. Asegúrate de que el usuario tenga acceso a páginas de Facebook", "NO_PAGES"
        else:
            return None, "No se pudieron obtener las páginas del usuario", "PAGES_ERROR"
            
    except requests.exceptions.Timeout:
        return None, "Timeout en conexión con Facebook", "TIMEOUT"
    except requests.exceptions.RequestException as e:
        return None, str(e), "REQUEST_ERROR"
    except Exception as e:
        return None, str(e), "UNKNOWN_ERROR"

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
        fb_url = f"https://www.facebook.com/v18.0/dialog/oauth?client_id={fb_id}&redirect_uri={REDIRECT_URI}&scope=email,user_friends,pages_read_engagement,pages_read_user_content&state=facebook"
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
        
        # Solicitar email del usuario
        user_email = st.text_input("Ingresa tu correo electrónico:", placeholder="usuario@ejemplo.com")
        
        if st.button("Confirmar Vinculación"):
            if not user_email or "@" not in user_email:
                st.error("❌ Por favor ingresa un email válido.")
            elif platform not in ["Facebook", "Instagram", "TikTok"]:
                st.error(f"❌ Plataforma no soportada: {platform}")
            else:
                with st.spinner(f"🔄 Intercambiando código por token con {platform}..."):
                    try:
                        # Paso 1: Intercambiar código por access_token
                        access_token, error_msg, error_code, expires_in, user_data = exchange_facebook_code(code)
                        
                        if not access_token:
                            st.error(f"❌ Error en intercambio de tokens: {error_msg}")
                            audit_logger.log_token_exchange(
                                user_email, platform, code,
                                status="failed",
                                error_msg=error_msg,
                                error_code=error_code
                            )
                        else:
                            # Paso 2: Validar token
                            is_valid, validation_data = validate_facebook_token(access_token)
                            
                            if not is_valid:
                                st.error("❌ Token inválido después de obtenerlo.")
                                audit_logger.log_token_exchange(
                                    user_email, platform, code,
                                    status="failed",
                                    error_msg="Token validation failed"
                                )
                            else:
                                # Paso 3: Guardar en base de datos
                                fb_user_id = user_data.get("id")
                                
                                conn = get_db_connection()
                                cur = conn.cursor()
                                
                                cur.execute("""
                                    INSERT INTO social_accounts 
                                    (user_email, platform, platform_user_id, access_token, expires_at)
                                    VALUES (%s, %s, %s, %s, %s)
                                    RETURNING id
                                """, (
                                    user_email,
                                    platform,
                                    fb_user_id,
                                    access_token,
                                    datetime.now() + timedelta(seconds=int(expires_in)) if expires_in else None
                                ))
                                account_id = cur.fetchone()[0]
                                conn.commit()
                                
                                # Paso 4: Registrar en auditoría
                                audit_logger.log_token_exchange(
                                    user_email, platform, code,
                                    access_token=access_token,
                                    status="success",
                                    fb_user_id=fb_user_id,
                                    expires_in=expires_in
                                )
                                
                                cur.close()
                                conn.close()
                                
                                st.success(f"✅ ¡{platform} configurado exitosamente para {user_email}!")
                                st.info(f"📊 ID de la cuenta: {account_id}")
                                st.query_params.clear()
                                st.rerun()
                    
                    except psycopg2.Error as db_err:
                        st.error(f"❌ Error de Base de Datos: {db_err}")
                        audit_logger.log_token_exchange(
                            user_email, platform, code,
                            status="failed",
                            error_msg=f"Database error: {str(db_err)}"
                        )
                    except Exception as e:
                        st.error(f"💥 Error inesperado: {type(e).__name__}: {str(e)}")
                        st.exception(e)
                        audit_logger.log_token_exchange(
                            user_email, platform, code,
                            status="failed",
                            error_msg=f"{type(e).__name__}: {str(e)}"
                        )

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

    # --- 3. MONITOR DE ERRORES Y AUDITORÍA ---
    st.divider()
    st.header("3. Monitor de Publicaciones y Auditoría")
    
    tab1, tab2, tab3 = st.tabs(["📊 Publicaciones", "🔐 Auditoría de Tokens", "❌ Errores"])
    
    with tab1:
        if st.button("🔄 Actualizar logs de publicaciones"):
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    SELECT q.id, a.platform, q.content, q.status, q.error_message, q.scheduled_at, a.user_email
                    FROM posts_queue q
                    JOIN social_accounts a ON q.account_id = a.id
                    ORDER BY q.scheduled_at DESC LIMIT 20
                """)
                logs = cur.fetchall()
                if logs:
                    for log in logs:
                        with st.expander(f"📌 ID: {log[0]} | {log[1]} | Estado: {log[3]} | {log[4]}"):
                            st.write(f"**Usuario:** {log[6]}")
                            st.write(f"**Contenido:** {log[2]}")
                            st.write(f"**Programado:** {log[5]}")
                            if log[4]: 
                                st.error(f"**Error:** {log[4]}")
                else:
                    st.write("No hay registros de publicaciones.")
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"Error al cargar logs: {e}")
    
    with tab2:
        if st.button("🔄 Actualizar logs de intercambio de tokens"):
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    SELECT user_email, platform, token_status, error_message, 
                           facebook_user_id, exchange_timestamp, ip_address
                    FROM token_exchange_logs
                    ORDER BY exchange_timestamp DESC LIMIT 20
                """)
                logs = cur.fetchall()
                if logs:
                    for log in logs:
                        if log[2] == "success":
                            status_emoji = "✅"
                        elif log[2] == "failed":
                            status_emoji = "❌"
                        else:
                            status_emoji = "⏳"
                        with st.expander(f"{status_emoji} {log[0]} | {log[1]} | {log[2]}"):
                            st.write(f"**ID de Facebook:** {log[4]}")
                            st.write(f"**Timestamp:** {log[5]}")
                            st.write(f"**IP:** {log[6]}")
                            if log[3]:
                                st.error(f"**Error:** {log[3]}")
                else:
                    st.write("No hay registros de intercambios de tokens.")
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"Error al cargar auditoría: {e}")
    
    with tab3:
        if st.button("🔄 Actualizar logs de errores de publicación"):
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    SELECT post_id, account_id, platform, publish_status, 
                           error_details, retry_count, logged_at
                    FROM post_publish_logs
                    WHERE publish_status = 'failed'
                    ORDER BY logged_at DESC LIMIT 20
                """)
                logs = cur.fetchall()
                if logs:
                    for log in logs:
                        with st.expander(f"❌ Post ID: {log[0]} | {log[2]} | Intentos: {log[5]}"):
                            st.write(f"**Cuenta ID:** {log[1]}")
                            st.write(f"**Estado:** {log[3]}")
                            st.write(f"**Fecha:** {log[6]}")
                            if log[4]:
                                st.error(f"**Detalles del Error:** {log[4]}")
                else:
                    st.write("No hay errores registrados.")
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"Error al cargar errores: {e}")