"""
Módulo centralizado para auditoría y logging de eventos.
Registra todos los eventos críticos del sistema en la base de datos.
"""

import psycopg2
import os
from datetime import datetime, timedelta
import socket
import json
from dotenv import load_dotenv

load_dotenv()

class AuditLogger:
    """Clase para gestionar toda la auditoría del sistema."""
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
    
    def get_connection(self):
        """Obtiene conexión a la base de datos."""
        try:
            return psycopg2.connect(self.db_url)
        except Exception as e:
            print(f"❌ Error de conexión a BD: {e}")
            return None
    
    def get_client_ip(self):
        """Obtiene la IP del cliente."""
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "0.0.0.0"
    
    def log_token_exchange(self, user_email, platform, code, access_token=None, 
                          status="pending", error_msg=None, error_code=None, 
                          fb_user_id=None, expires_in=None):
        """
        Registra un intercambio de tokens.
        
        Args:
            user_email: Email del usuario
            platform: 'Facebook', 'Instagram', 'TikTok'
            code: Código de autorización de OAuth
            access_token: Token obtenido (None si falló)
            status: 'pending', 'success', 'failed', 'expired'
            error_msg: Mensaje de error (si aplica)
            error_code: Código de error de API
            fb_user_id: ID del usuario en la plataforma
            expires_in: Segundos hasta expiración del token
        """
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor()
            expires_at = None
            
            if expires_in:
                expires_at = datetime.now() + timedelta(seconds=int(expires_in))
            
            cur.execute("""
                INSERT INTO token_exchange_logs 
                (user_email, platform, authorization_code, access_token, token_status, 
                 error_message, error_code, facebook_user_id, token_obtained_at, 
                 token_expires_at, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_email,
                platform,
                code[:100] if code else None,  # Truncar para seguridad
                access_token[:200] if access_token else None,
                status,
                error_msg[:500] if error_msg else None,
                error_code,
                fb_user_id,
                datetime.now() if access_token else None,
                expires_at,
                self.get_client_ip()
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            if status == "success":
                status_symbol = "✅"
            elif status == "failed":
                status_symbol = "❌"
            else:
                status_symbol = "⏳"
            print(f"{status_symbol} [AUDITORÍA] Token exchange: {user_email} | {platform} | {status}")
            return True
            
        except Exception as e:
            print(f"❌ Error registrando token exchange: {e}")
            return False
    
    def log_publish_event(self, post_id, account_id, platform, fb_post_id=None,
                         status="failed", platform_response_code=None, 
                         error_details=None, retry_count=0):
        """
        Registra un evento de publicación.
        
        Args:
            post_id: ID del post en posts_queue
            account_id: ID de la cuenta social
            platform: Red social destino
            fb_post_id: ID del post generado por Facebook (si éxito)
            status: 'published', 'failed', 'rejected'
            platform_response_code: Código de respuesta de la API
            error_details: Detalles del error
            retry_count: Número de reintentos
        """
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO post_publish_logs 
                (post_id, account_id, platform, facebook_post_id, publish_status, 
                 platform_response_code, error_details, retry_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                post_id,
                account_id,
                platform,
                fb_post_id,
                status,
                platform_response_code,
                error_details[:1000] if error_details else None,
                retry_count
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            status_symbol = "✅" if status == "published" else "❌"
            print(f"{status_symbol} [AUDITORÍA] Post publish: ID={post_id} | {platform} | {status}")
            return True
            
        except Exception as e:
            print(f"❌ Error registrando evento de publicación: {e}")
            return False
    
    def log_validation_event(self, access_token, is_valid, expires_at, account_id, platform):
        """
        Registra la validación de un token.
        
        Args:
            access_token: Token validado
            is_valid: Booleano si es válido
            expires_at: Timestamp de expiración
            account_id: ID de la cuenta
            platform: Red social
        """
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor()
            
            # Registrar como evento en token_exchange_logs
            cur.execute("""
                INSERT INTO token_exchange_logs 
                (user_email, platform, access_token, token_status, 
                 token_expires_at, exchange_timestamp, ip_address)
                SELECT user_email, platform, %s, %s, %s, NOW(), %s
                FROM social_accounts
                WHERE id = %s
            """, (
                access_token[:200],
                "valid" if is_valid else "invalid",
                expires_at,
                self.get_client_ip(),
                account_id
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            status_symbol = "✅" if is_valid else "⚠️"
            print(f"{status_symbol} [AUDITORÍA] Token validation: Account={account_id} | {platform} | valid={is_valid}")
            return True
            
        except Exception as e:
            print(f"❌ Error registrando validación: {e}")
            return False
    
    def get_token_exchange_history(self, user_email=None, platform=None, limit=50):
        """
        Obtiene el historial de intercambios de tokens.
        
        Args:
            user_email: Filtrar por email (opcional)
            platform: Filtrar por plataforma (opcional)
            limit: Número máximo de registros
        
        Returns:
            Lista de registros o None si error
        """
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor()
            
            query = "SELECT * FROM token_exchange_logs WHERE 1=1"
            params = []
            
            if user_email:
                query += " AND user_email = %s"
                params.append(user_email)
            
            if platform:
                query += " AND platform = %s"
                params.append(platform)
            
            query += " ORDER BY exchange_timestamp DESC LIMIT %s"
            params.append(limit)
            
            cur.execute(query, params)
            records = cur.fetchall()
            
            cur.close()
            conn.close()
            
            return records
            
        except Exception as e:
            print(f"❌ Error obteniendo historial: {e}")
            return None
    
    def get_failed_publications(self, limit=20):
        """
        Obtiene las publicaciones fallidas.
        
        Returns:
            Lista de publicaciones fallidas
        """
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT * FROM post_publish_logs
                WHERE publish_status = 'failed'
                ORDER BY logged_at DESC
                LIMIT %s
            """, (limit,))
            
            records = cur.fetchall()
            cur.close()
            conn.close()
            
            return records
            
        except Exception as e:
            print(f"❌ Error obteniendo publicaciones fallidas: {e}")
            return None
    
    def generate_audit_report(self, days=7):
        """
        Genera un reporte de auditoría de los últimos N días.
        
        Returns:
            Diccionario con estadísticas
        """
        conn = self.get_connection()
        if not conn:
            return {}
        
        try:
            cur = conn.cursor()
            
            # Estadísticas de intercambios
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN token_status = 'success' THEN 1 END) as exitosos,
                    COUNT(CASE WHEN token_status = 'failed' THEN 1 END) as fallidos,
                    platform
                FROM token_exchange_logs
                WHERE exchange_timestamp >= NOW() - INTERVAL '%s days'
                GROUP BY platform
            """, (days,))
            
            token_stats = cur.fetchall()
            
            # Estadísticas de publicaciones
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN publish_status = 'published' THEN 1 END) as exitosas,
                    COUNT(CASE WHEN publish_status = 'failed' THEN 1 END) as fallidas,
                    platform
                FROM post_publish_logs
                WHERE logged_at >= NOW() - INTERVAL '%s days'
                GROUP BY platform
            """, (days,))
            
            publish_stats = cur.fetchall()
            
            cur.close()
            conn.close()
            
            return {
                "token_exchanges": token_stats,
                "publications": publish_stats,
                "period_days": days,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error generando reporte: {e}")
            return {}


# Instancia global del logger
audit_logger = AuditLogger()
