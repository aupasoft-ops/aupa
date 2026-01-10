import time
import psycopg2
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import json
from audit_logger import audit_logger

load_dotenv()

def get_db_connection():
    """Establece conexión a la base de datos."""
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def validate_and_refresh_token(access_token):
    """Valida el token y verifica si está a punto de expirar."""
    try:
        url = "https://graph.facebook.com/v18.0/debug_token"
        params = {
            "input_token": access_token,
            "access_token": f"{os.getenv('FACEBOOK_CLIENT_ID')}|{os.getenv('FACEBOOK_CLIENT_SECRET')}"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json().get("data", {})
            is_valid = data.get("is_valid", False)
            expires_at = data.get("expires_at", 0)
            
            print(f"🔍 Token validado: válido={is_valid}, expira en {expires_at} segundos")
            return is_valid, expires_at
        else:
            return False, 0
    except Exception as e:
        print(f"⚠️ Error validando token: {e}")
        return False, 0

def publish_to_facebook(page_id, access_token, message, media_url=None):
    """Publica un post en Facebook usando Graph API.
    
    Args:
        page_id: ID de la página de Facebook
        access_token: Token de acceso válido
        message: Contenido del post
        media_url: URL del media (opcional)
    
    Returns:
        (success: bool, post_id: str, error_msg: str, response_code: str)
    """
    try:
        url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        
        data = {
            "message": message,
            "access_token": access_token
        }
        
        # Si hay media, agregarlo
        if media_url:
            data["source"] = media_url
        
        response = requests.post(url, data=data, timeout=15)
        
        print(f"📤 Respuesta de Facebook API: código {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            fb_post_id = response_data.get("id")
            print(f"✅ Post publicado exitosamente. ID: {fb_post_id}")
            return True, fb_post_id, None, "200"
        else:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", "Unknown error")
            error_type = error_data.get("error", {}).get("type", "UNKNOWN")
            print(f"❌ Error en publicación: {error_msg}")
            return False, None, error_msg, error_type
            
    except requests.exceptions.Timeout:
        return False, None, "Timeout en conexión con Facebook", "TIMEOUT"
    except requests.exceptions.RequestException as e:
        return False, None, str(e), "REQUEST_ERROR"
    except Exception as e:
        return False, None, str(e), "UNKNOWN_ERROR"

def process_posts():
    """Procesa posts pendientes y los publica en redes sociales."""
    while True:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Buscar posts pendientes con información de la cuenta
            cur.execute("""
                SELECT q.id, q.content, q.media_url, a.platform, a.access_token, 
                       a.platform_user_id, a.id as account_id
                FROM posts_queue q
                JOIN social_accounts a ON q.account_id = a.id
                WHERE q.status = 'pending'
                ORDER BY q.scheduled_at ASC
                LIMIT 5
            """)
            
            pending_posts = cur.fetchall()
            
            if not pending_posts:
                print(f"⏳ [{datetime.now()}] Sin posts pendientes. Esperando...")
            
            for post in pending_posts:
                post_id, content, media_url, platform, access_token, platform_user_id, account_id = post
                print(f"\n{'='*60}")
                print(f"📝 Procesando post {post_id} para {platform}")
                print(f"   Contenido: {content[:50]}...")
                print(f"{'='*60}")
                
                # Validar token antes de intentar publicar
                is_valid, _ = validate_and_refresh_token(access_token)
                
                if not is_valid:
                    print(f"❌ Token inválido para post {post_id}")
                    cur.execute("""
                        UPDATE posts_queue 
                        SET status = 'failed', error_message = %s 
                        WHERE id = %s
                    """, ("Token inválido o expirado", post_id))
                    
                    audit_logger.log_publish_event(
                        post_id, account_id, platform,
                        status="failed",
                        error_details="Token inválido o expirado",
                        platform_response_code="INVALID_TOKEN"
                    )
                    conn.commit()
                    continue
                
                # Publicar según la plataforma
                if platform == "Facebook":
                    success, fb_post_id, error_msg, error_code = publish_to_facebook(
                        platform_user_id, 
                        access_token, 
                        content,
                        media_url
                    )
                    
                    if success:
                        cur.execute("""
                            UPDATE posts_queue 
                            SET status = 'sent', sent_at = NOW() 
                            WHERE id = %s
                        """, (post_id,))
                        
                        audit_logger.log_publish_event(
                            post_id, account_id, platform,
                            fb_post_id=fb_post_id,
                            status="published",
                            platform_response_code="200"
                        )
                        print(f"✅ Post {post_id} enviado a Facebook")
                    else:
                        cur.execute("""
                            UPDATE posts_queue 
                            SET status = 'failed', error_message = %s 
                            WHERE id = %s
                        """, (error_msg, post_id))
                        
                        audit_logger.log_publish_event(
                            post_id, account_id, platform,
                            status="failed",
                            error_details=error_msg,
                            platform_response_code=error_code
                        )
                        print(f"❌ Post {post_id} falló: {error_msg}")
                
                elif platform == "Instagram":
                    # Lógica similar para Instagram (USA business_account_id)
                    print(f"⏳ Instagram no implementado aún para post {post_id}")
                    
                elif platform == "TikTok":
                    # Lógica para TikTok
                    print(f"⏳ TikTok no implementado aún para post {post_id}")
                
                conn.commit()
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error en worker: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        print("⏰ Próxima revisión en 10 segundos...")
        time.sleep(10)

if __name__ == "__main__":
    print("Worker activo y escuchando la base de datos...")
    process_posts()