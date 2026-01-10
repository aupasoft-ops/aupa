"""
Script de prueba para validar la implementación de OAuth y auditoría.
Ejecutar: python test_oauth_implementation.py
"""

import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def check_database_tables():
    """Verifica que las tablas requeridas existan."""
    print("\n" + "="*60)
    print("🔍 VALIDACIÓN DE TABLAS DE BASE DE DATOS")
    print("="*60)
    
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        
        # Verificar tabla social_accounts
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'social_accounts'
        """)
        
        if cur.fetchall():
            print("✅ Tabla 'social_accounts' encontrada")
            cur.execute("SELECT * FROM social_accounts LIMIT 1")
            cols = [desc[0] for desc in cur.description]
            print(f"   Columnas: {', '.join(cols)}")
        else:
            print("❌ Tabla 'social_accounts' NO encontrada")
        
        # Verificar tabla token_exchange_logs
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'token_exchange_logs'
        """)
        
        if cur.fetchall():
            print("✅ Tabla 'token_exchange_logs' encontrada")
            cur.execute("SELECT COUNT(*) FROM token_exchange_logs")
            count = cur.fetchone()[0]
            print(f"   Registros: {count}")
        else:
            print("❌ Tabla 'token_exchange_logs' NO encontrada - EJECUTAR init.sql")
        
        # Verificar tabla post_publish_logs
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'post_publish_logs'
        """)
        
        if cur.fetchall():
            print("✅ Tabla 'post_publish_logs' encontrada")
            cur.execute("SELECT COUNT(*) FROM post_publish_logs")
            count = cur.fetchone()[0]
            print(f"   Registros: {count}")
        else:
            print("❌ Tabla 'post_publish_logs' NO encontrada - EJECUTAR init.sql")
        
        # Verificar tabla posts_queue
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'posts_queue'
        """)
        
        if cur.fetchall():
            print("✅ Tabla 'posts_queue' encontrada")
        else:
            print("❌ Tabla 'posts_queue' NO encontrada")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")

def check_environment_variables():
    """Verifica que las variables de entorno necesarias estén configuradas."""
    print("\n" + "="*60)
    print("🔐 VALIDACIÓN DE VARIABLES DE ENTORNO")
    print("="*60)
    
    required_vars = [
        "DATABASE_URL",
        "FACEBOOK_CLIENT_ID",
        "FACEBOOK_CLIENT_SECRET",
        "REDIRECT_URI"
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Ocultar valores sensibles
            if "CLIENT_SECRET" in var or "DATABASE_URL" in var:
                display = value[:5] + "..." if len(value) > 5 else "***"
            else:
                display = value
            print(f"✅ {var} = {display}")
        else:
            print(f"❌ {var} = NO CONFIGURADA")

def check_required_modules():
    """Verifica que los módulos Python necesarios estén instalados."""
    print("\n" + "="*60)
    print("📦 VALIDACIÓN DE MÓDULOS PYTHON")
    print("="*60)
    
    required_modules = [
        "psycopg2",
        "streamlit",
        "requests",
        "dotenv",
        "audit_logger"  # Nuestro módulo
    ]
    
    for module in required_modules:
        try:
            if module == "dotenv":
                __import__("dotenv")
            elif module == "audit_logger":
                # Verificar que el archivo existe
                if os.path.exists("web_aupa/audit_logger.py"):
                    print(f"✅ {module} encontrado (archivo local)")
                else:
                    print(f"❌ {module} NO encontrado")
            else:
                __import__(module)
            
            if module != "audit_logger":
                print(f"✅ {module} instalado")
        except ImportError:
            print(f"❌ {module} NO INSTALADO - ejecutar: pip install {module}")

def check_file_structure():
    """Verifica que los archivos estén en el lugar correcto."""
    print("\n" + "="*60)
    print("📁 VALIDACIÓN DE ESTRUCTURA DE ARCHIVOS")
    print("="*60)
    
    required_files = {
        "web_aupa/app.py": "Aplicación principal Streamlit",
        "web_aupa/worker.py": "Worker para publicaciones",
        "web_aupa/audit_logger.py": "Módulo de auditoría",
        "web_aupa/database_config.py": "Configuración de BD",
        "init.sql": "Script de inicialización de BD"
    }
    
    for filepath, description in required_files.items():
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✅ {filepath} ({size} bytes) - {description}")
        else:
            print(f"❌ {filepath} NO ENCONTRADO")

def check_database_connection():
    """Verifica la conexión a la base de datos."""
    print("\n" + "="*60)
    print("🗄️  VALIDACIÓN DE CONEXIÓN A BASE DE DATOS")
    print("="*60)
    
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        
        # Prueba de consulta simple
        cur.execute("SELECT NOW()")
        timestamp = cur.fetchone()[0]
        
        print(f"✅ Conexión exitosa a PostgreSQL")
        print(f"   Timestamp del servidor: {timestamp}")
        
        # Mostrar información de la BD
        cur.execute("SELECT current_database()")
        db_name = cur.fetchone()[0]
        print(f"   Base de datos: {db_name}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("   Verifica que PostgreSQL esté ejecutándose y las credenciales sean correctas")

def main():
    """Ejecuta todas las validaciones."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*12 + "VALIDACIÓN DEL SISTEMA AUPA" + " "*22 + "║")
    print("╚" + "="*58 + "╝")
    
    check_environment_variables()
    check_database_connection()
    check_database_tables()
    check_required_modules()
    check_file_structure()
    
    print("\n" + "="*60)
    print("📋 RESUMEN DE VALIDACIÓN")
    print("="*60)
    print("""
✅ Si todas las validaciones pasaron:
   - Las tablas de auditoría están creadas
   - Las variables de entorno están configuradas
   - Los módulos Python están instalados
   - La conexión a BD es correcta

❌ Si hay errores:
   1. Ejecuta: psql -f init.sql
   2. Configura variables de entorno en .env
   3. Instala módulos: pip install -r requirements.txt
   
🚀 Para iniciar la aplicación:
   streamlit run web_aupa/app.py

🐍 Para iniciar el worker:
   python web_aupa/worker.py
    """)

if __name__ == "__main__":
    main()
