import time
import psycopg2
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def process_posts():
    while True:
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()
            
            # Buscar posts pendientes
            cur.execute("""
                SELECT q.id, q.content, a.platform, a.access_token 
                FROM posts_queue q
                JOIN social_accounts a ON q.account_id = a.id
                WHERE q.status = 'pending'
                LIMIT 5
            """)
            
            pending_posts = cur.fetchall()
            
            for post in pending_posts:
                post_id, content, platform, token = post
                print(f"Procesando post {post_id} para {platform}...")
                
                # Lógica de publicación real (Ejemplo simplificado)
                # response = requests.post(f"https://graph.facebook.com/me/feed", data={'message': content, 'access_token': token})
                
                success = True # Simulación
                
                if success:
                    cur.execute("UPDATE posts_queue SET status = 'sent', sent_at = NOW() WHERE id = %s", (post_id,))
                else:
                    cur.execute("UPDATE posts_queue SET status = 'failed' WHERE id = %s", (post_id,))
                
                conn.commit()
                print(f"Post {post_id} enviado.")

            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error en worker: {e}")
            
        time.sleep(10) # Revisa cada 10 segundos

if __name__ == "__main__":
    print("Worker activo y escuchando la base de datos...")
    process_posts()