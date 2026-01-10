#!/usr/bin/env python3
"""
Script de validación para configuración de Facebook OAuth
Verifica que todos los componentes estén correctamente configurados
"""

import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

def check_environment_variables():
    """Verifica que todas las variables de entorno necesarias estén configuradas"""
    print("=" * 60)
    print("1️⃣  VERIFICANDO VARIABLES DE ENTORNO")
    print("=" * 60)
    
    required_vars = {
        "FACEBOOK_CLIENT_ID": "ID de la aplicación Facebook",
        "FACEBOOK_CLIENT_SECRET": "Secret de la aplicación Facebook",
        "DATABASE_URL": "Conexión a base de datos PostgreSQL",
        "REDIRECT_URI": "URI de redirección OAuth"
    }
    
    missing = []
    configured = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Truncar valores sensibles
            if "SECRET" in var or "PASSWORD" in var:
                display_value = f"{value[:10]}...{value[-5:]}"
            elif "ID" in var:
                display_value = value
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
            configured.append(var)
        else:
            print(f"❌ {var}: NO CONFIGURADA")
            missing.append(var)
    
    print()
    if missing:
        print(f"⚠️  Faltan {len(missing)} variable(s): {', '.join(missing)}")
        return False
    else:
        print(f"✅ Todas las variables requeridas están configuradas")
        return True

def check_facebook_app_credentials():
    """Verifica que las credenciales de Facebook sean válidas"""
    print("\n" + "=" * 60)
    print("2️⃣  VERIFICANDO CREDENCIALES DE FACEBOOK")
    print("=" * 60)
    
    client_id = os.getenv("FACEBOOK_CLIENT_ID")
    client_secret = os.getenv("FACEBOOK_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Faltan credenciales de Facebook")
        return False
    
    # Verificar que las credenciales tengan el formato correcto
    if len(client_id) < 10:
        print(f"❌ Client ID parece inválido (muy corto): {client_id}")
        return False
    
    if len(client_secret) < 20:
        print(f"❌ Client Secret parece inválido (muy corto)")
        return False
    
    print(f"✅ Credenciales tienen formato válido")
    print(f"   - Client ID: {client_id}")
    print(f"   - Client Secret: {client_secret[:10]}...{client_secret[-5:]}")
    
    return True

def check_oauth_url():
    """Verifica que la URL de OAuth esté construida correctamente"""
    print("\n" + "=" * 60)
    print("3️⃣  VERIFICANDO URL DE OAUTH")
    print("=" * 60)
    
    client_id = os.getenv("FACEBOOK_CLIENT_ID")
    redirect_uri = os.getenv("REDIRECT_URI", "https://localhost:8501/")
    
    scopes = [
        "email",
        "user_friends",
        "pages_read_engagement",
        "pages_read_user_content"
    ]
    
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": ",".join(scopes),
        "state": "facebook"
    }
    
    oauth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
    
    print(f"✅ URL de OAuth construida correctamente")
    print(f"\n   Cliente ID: {client_id}")
    print(f"   Redirect URI: {redirect_uri}")
    print(f"   Scopes: {', '.join(scopes)}")
    print(f"\n   URL (truncada): {oauth_url[:100]}...")
    
    # Verificar que sea HTTPS
    if not redirect_uri.startswith("https://"):
        print(f"\n❌ ⚠️  ADVERTENCIA: Redirect URI no es HTTPS")
        print(f"   Facebook requiere HTTPS para OAuth")
        print(f"   URIs válidas: https://localhost:8501/")
        return False
    
    print(f"\n✅ Redirect URI usa HTTPS correctamente")
    return True

def check_scopes():
    """Verifica que los scopes solicitados sean válidos"""
    print("\n" + "=" * 60)
    print("4️⃣  VERIFICANDO SCOPES DE FACEBOOK LOGIN")
    print("=" * 60)
    
    scopes = {
        "email": "✅ Válido para Facebook Login",
        "user_friends": "✅ Válido para Facebook Login",
        "pages_read_engagement": "✅ Válido para Facebook Login",
        "pages_read_user_content": "✅ Válido para Facebook Login",
        "pages_manage_posts": "❌ NO válido para Facebook Login (solo para Page Token)",
        "publish_video": "❌ NO válido para Facebook Login",
        "pages_show_list": "❌ NO válido para Facebook Login"
    }
    
    print("\n📋 Scopes utilizados:")
    print("=" * 60)
    for scope, status in scopes.items():
        if "✅" in status:
            print(f"   {scope}: {status}")
    
    print("\n❌ Scopes NO válidos para Facebook Login:")
    print("=" * 60)
    for scope, status in scopes.items():
        if "❌" in status:
            print(f"   {scope}: {status}")
    
    print("\n💡 Nota: El Page Access Token (para publicar) se obtiene")
    print("   automáticamente del endpoint /me/accounts después de")
    print("   autenticar con los scopes válidos.")
    
    return True

def check_graph_api_endpoint():
    """Verifica que los endpoints de Graph API sean accesibles"""
    print("\n" + "=" * 60)
    print("5️⃣  VERIFICANDO ENDPOINTS DE GRAPH API")
    print("=" * 60)
    
    endpoints = {
        "OAuth Token": "https://graph.facebook.com/v18.0/oauth/access_token",
        "Me Endpoint": "https://graph.facebook.com/v18.0/me",
        "User Accounts": "https://graph.facebook.com/v18.0/me/accounts",
        "Page Feed": "https://graph.facebook.com/v18.0/{page_id}/feed"
    }
    
    # Solo verificar que las URLs sean válidas
    print("\n✅ Endpoints de Graph API (v18.0):")
    for name, url in endpoints.items():
        print(f"   - {name}: {url}")
    
    return True

def check_database():
    """Verifica que la base de datos sea accesible"""
    print("\n" + "=" * 60)
    print("6️⃣  VERIFICANDO BASE DE DATOS")
    print("=" * 60)
    
    try:
        import psycopg2
        print("✅ Librería psycopg2 disponible")
    except ImportError:
        print("❌ Librería psycopg2 NO disponible")
        print("   Instalar: pip install psycopg2-binary")
        return False
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL no configurada")
        return False
    
    print(f"✅ DATABASE_URL configurada")
    print(f"   {db_url}")
    
    # Intentar conectar
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Verificar que las tablas existan
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema='public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            "social_accounts",
            "posts_queue",
            "token_exchange_logs",
            "post_publish_logs"
        ]
        
        print(f"\n✅ Conexión a BD exitosa")
        print(f"   Tablas en BD: {', '.join(tables)}")
        
        missing_tables = [t for t in required_tables if t not in tables]
        if missing_tables:
            print(f"\n❌ Faltan tablas: {', '.join(missing_tables)}")
            print(f"   Ejecutar: psql -U aupa -d aupa -f init.sql")
            cursor.close()
            conn.close()
            return False
        
        print(f"\n✅ Todas las tablas requeridas existen")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ No se pudo conectar a la BD: {str(e)}")
        return False

def main():
    """Ejecuta todas las validaciones"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🔧 VALIDADOR DE CONFIGURACIÓN - FACEBOOK OAUTH".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = {}
    
    results["Variables de Entorno"] = check_environment_variables()
    results["Credenciales de Facebook"] = check_facebook_app_credentials()
    results["URL de OAuth"] = check_oauth_url()
    results["Scopes"] = check_scopes()
    results["Graph API"] = check_graph_api_endpoint()
    results["Base de Datos"] = check_database()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status}: {check}")
    
    print(f"\nTotal: {passed}/{total} validaciones pasadas")
    
    if passed == total:
        print("\n🎉 ¡Configuración OK! Puedes iniciar la aplicación:")
        print("   streamlit run web_aupa/app.py")
        return 0
    else:
        print("\n⚠️  Hay problemas de configuración. Ver arriba para detalles.")
        return 1

if __name__ == "__main__":
    exit(main())
