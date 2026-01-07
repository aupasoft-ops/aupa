"""
Guía de Flujos n8n para Redes Sociales

Este archivo contiene ejemplos de cómo estructurar los flujos de OAuth
para cada plataforma (Facebook, Instagram, TikTok) en n8n.

Cada flujo debe:
1. Recibir la solicitud del usuario
2. Generar la URL de OAuth
3. Guardar el estado (state) en la BD
4. Retornar la URL de OAuth al usuario

Luego, separadamente, crear webhooks para los callbacks:
5. Recibir el callback con el código de autorización
6. Cambiar el código por un token de acceso
7. Guardar el token en la BD
8. Retornar respuesta de éxito
"""

# ==============================================================================
# FLUJO 1: FACEBOOK OAUTH REQUEST
# ==============================================================================
# Webhook: POST /webhook/facebook-connect
# Descripción: Inicia el flujo OAuth para Facebook

FACEBOOK_OAUTH_FLOW = {
    "name": "Facebook OAuth - Request",
    "description": "Inicia la autenticación OAuth con Facebook",
    
    "nodes": {
        "1_webhook": {
            "type": "n8n-nodes-base.webhook",
            "method": "POST",
            "path": "facebook-connect",
            "responseMode": "responseNode"
        },
        
        "2_extract_user_data": {
            "type": "n8n-nodes-base.set",
            "description": "Extrae datos del usuario de la solicitud",
            "operations": [
                {"name": "user_id", "value": "={{$json.user_id}}"},
                {"name": "user_email", "value": "={{$json.user_email}}"},
                {"name": "platform", "value": "facebook"}
            ]
        },
        
        "3_generate_state": {
            "type": "n8n-nodes-base.code",
            "language": "javascript",
            "description": "Genera un token de state aleatorio",
            "code": """
            const state = Math.random().toString(36).substring(2, 15) + 
                         Math.random().toString(36).substring(2, 15);
            return {state: state};
            """
        },
        
        "4_build_oauth_url": {
            "type": "n8n-nodes-base.set",
            "description": "Construye la URL de OAuth de Facebook",
            "operations": [
                {
                    "name": "oauth_url",
                    "value": "https://www.facebook.com/v18.0/dialog/oauth?client_id={{$env.FACEBOOK_APP_ID}}&redirect_uri={{$env.FACEBOOK_REDIRECT_URI}}&state={{$json.state}}&scope=pages_manage_metadata,pages_read_engagement"
                }
            ]
        },
        
        "5_save_state_postgres": {
            "type": "n8n-nodes-base.postgres",
            "operation": "insert",
            "table": "connection_requests",
            "fields": {
                "user_id": "={{$json.user_id}}",
                "platform": "facebook",
                "email": "={{$json.user_email}}",
                "state": "={{$json.state}}",
                "oauth_url": "={{$json.oauth_url}}",
                "status": "pending",
                "timestamp": "={{new Date().toISOString()}}"
            }
        },
        
        "6_return_oauth_url": {
            "type": "n8n-nodes-base.respondToWebhook",
            "responseData": {
                "success": true,
                "message": "Solicitud enviada a Facebook",
                "data": {
                    "oauth_url": "={{$json.oauth_url}}",
                    "state": "={{$json.state}}"
                }
            }
        }
    },
    
    "connections": {
        "webhook → extract": "1→2",
        "extract → generate": "2→3",
        "generate → build_url": "3→4",
        "build_url → save": "4→5",
        "save → response": "5→6"
    }
}


# ==============================================================================
# FLUJO 2: FACEBOOK OAUTH CALLBACK
# ==============================================================================
# Webhook: GET /callback/facebook
# Descripción: Recibe el código de autorización y lo cambia por un token

FACEBOOK_CALLBACK_FLOW = {
    "name": "Facebook OAuth - Callback",
    "description": "Recibe el código de autorización de Facebook",
    
    "nodes": {
        "1_webhook": {
            "type": "n8n-nodes-base.webhook",
            "method": "GET",
            "path": "callback/facebook",
            "parameters": {
                "code": "{{$query.code}}",
                "state": "{{$query.state}}"
            }
        },
        
        "2_verify_state": {
            "type": "n8n-nodes-base.postgres",
            "operation": "select",
            "query": "SELECT * FROM connection_requests WHERE state = {{$json.state}} AND platform = 'facebook' AND status = 'pending'"
        },
        
        "3_if_valid_state": {
            "type": "n8n-nodes-base.if",
            "condition": "{{$json.length > 0}}",
            "description": "Verifica que el state es válido"
        },
        
        "4_exchange_code_for_token": {
            "type": "n8n-nodes-base.httpRequest",
            "method": "POST",
            "url": "https://graph.facebook.com/v18.0/oauth/access_token",
            "query": {
                "client_id": "={{$env.FACEBOOK_APP_ID}}",
                "client_secret": "={{$env.FACEBOOK_APP_SECRET}}",
                "code": "={{$json.code}}",
                "redirect_uri": "={{$env.FACEBOOK_REDIRECT_URI}}"
            }
        },
        
        "5_update_connection": {
            "type": "n8n-nodes-base.postgres",
            "operation": "update",
            "table": "connection_requests",
            "conditions": [
                {"field": "state", "operator": "=", "value": "={{$json.state}}"}
            ],
            "fields": {
                "access_token": "={{$json.access_token}}",
                "token_expiry": "={{new Date(Date.now() + $json.expires_in * 1000).toISOString()}}",
                "status": "authorized",
                "connected_at": "={{new Date().toISOString()}}"
            }
        },
        
        "6_log_success": {
            "type": "n8n-nodes-base.postgres",
            "operation": "insert",
            "table": "oauth_logs",
            "fields": {
                "user_id": "={{$json[0].user_id}}",
                "platform": "facebook",
                "action": "authorization_granted",
                "status_code": "200",
                "created_at": "={{new Date().toISOString()}}"
            }
        },
        
        "7_redirect_success": {
            "type": "n8n-nodes-base.respondToWebhook",
            "statusCode": 200,
            "responseData": {
                "success": true,
                "message": "✅ Facebook conectado exitosamente",
                "redirect_to": "http://localhost:8501/?section=connected&platform=facebook"
            }
        },
        
        "8_error_invalid_state": {
            "type": "n8n-nodes-base.respondToWebhook",
            "statusCode": 400,
            "responseData": {
                "success": false,
                "message": "❌ State inválido. Intenta de nuevo.",
                "error": "INVALID_STATE"
            }
        }
    }
}


# ==============================================================================
# FLUJO 3: INSTAGRAM OAUTH REQUEST
# ==============================================================================
# Similar a Facebook pero con credenciales de Instagram

INSTAGRAM_OAUTH_FLOW = {
    "name": "Instagram OAuth - Request",
    "description": "Inicia la autenticación OAuth con Instagram",
    
    "differences_from_facebook": {
        "scopes": "instagram_business_management,pages_read_user_content",
        "client_id_var": "INSTAGRAM_BUSINESS_ACCOUNT_ID",
        "redirect_uri_var": "INSTAGRAM_REDIRECT_URI"
    },
    
    "oauth_url_format": "https://www.instagram.com/oauth/authorize?client_id={{CLIENT_ID}}&redirect_uri={{REDIRECT_URI}}&scope={{SCOPES}}&response_type=code&state={{STATE}}"
}


# ==============================================================================
# FLUJO 4: INSTAGRAM OAUTH CALLBACK
# ==============================================================================

INSTAGRAM_CALLBACK_FLOW = {
    "name": "Instagram OAuth - Callback",
    "description": "Recibe el código de autorización de Instagram",
    
    "token_exchange_endpoint": "https://graph.instagram.com/v18.0/access_token",
    
    "note": "Proceso idéntico a Facebook, solo cambiar credenciales y endpoint"
}


# ==============================================================================
# FLUJO 5: TIKTOK OAUTH REQUEST
# ==============================================================================

TIKTOK_OAUTH_FLOW = {
    "name": "TikTok OAuth - Request",
    "description": "Inicia la autenticación OAuth con TikTok",
    
    "oauth_url_format": "https://www.tiktok.com/v1/oauth/authorize/?client_key={{CLIENT_ID}}&response_type=code&scope={{SCOPES}}&redirect_uri={{REDIRECT_URI}}&state={{STATE}}",
    
    "scopes": "user.info.basic,video.list",
    
    "differences": {
        "uses_client_key_instead_of_client_id": True,
        "different_oauth_endpoints": "https://www.tiktok.com/v1/oauth/",
        "requires_client_secret_in_callback": True
    }
}


# ==============================================================================
# FLUJO 6: TIKTOK OAUTH CALLBACK
# ==============================================================================

TIKTOK_CALLBACK_FLOW = {
    "name": "TikTok OAuth - Callback",
    "description": "Recibe el código de autorización de TikTok",
    
    "token_exchange_endpoint": "https://open.tiktokapis.com/v1/oauth/token/",
    
    "request_body": {
        "client_key": "{{$env.TIKTOK_CLIENT_ID}}",
        "client_secret": "{{$env.TIKTOK_CLIENT_SECRET}}",
        "code": "{{$json.code}}",
        "grant_type": "authorization_code"
    }
}


# ==============================================================================
# FLUJO 7: DESCONECTAR PLATAFORMA
# ==============================================================================
# Webhook: POST /webhook/{platform}-connect/disconnect

DISCONNECT_FLOW = {
    "name": "Disconnect Social Platform",
    "description": "Revoca la conexión a una plataforma social",
    
    "nodes": {
        "1_webhook": {
            "type": "n8n-nodes-base.webhook",
            "method": "POST",
            "path": "{{platform}}-connect/disconnect"
        },
        
        "2_update_status": {
            "type": "n8n-nodes-base.postgres",
            "operation": "update",
            "table": "connection_requests",
            "conditions": [
                {"field": "user_id", "operator": "=", "value": "={{$json.user_id}}"},
                {"field": "platform", "operator": "=", "value": "={{$json.platform}}"}
            ],
            "fields": {
                "status": "revoked",
                "access_token": None,
                "refresh_token": None
            }
        },
        
        "3_revoke_token": {
            "type": "n8n-nodes-base.httpRequest",
            "method": "POST",
            "url": "https://graph.{{platform}}.com/v18.0/debug_token?input_token={{$json.access_token}}&access_token={{$env.FACEBOOK_APP_TOKEN}}"
        },
        
        "4_log_disconnection": {
            "type": "n8n-nodes-base.postgres",
            "operation": "insert",
            "table": "oauth_logs",
            "fields": {
                "user_id": "={{$json.user_id}}",
                "platform": "={{$json.platform}}",
                "action": "revoked",
                "status_code": "200"
            }
        },
        
        "5_return_success": {
            "type": "n8n-nodes-base.respondToWebhook",
            "responseData": {
                "success": true,
                "message": "Desconectado exitosamente"
            }
        }
    }
}


# ==============================================================================
# FLUJO 8: VERIFICAR ESTADO DE CONEXIÓN
# ==============================================================================
# Webhook: GET /webhook/{platform}-connect/status

CHECK_STATUS_FLOW = {
    "name": "Check Connection Status",
    "description": "Verifica si una conexión está activa",
    
    "nodes": {
        "1_webhook": {
            "type": "n8n-nodes-base.webhook",
            "method": "GET",
            "path": "{{platform}}-connect/status",
            "parameters": {
                "user_id": "{{$query.user_id}}"
            }
        },
        
        "2_query_status": {
            "type": "n8n-nodes-base.postgres",
            "operation": "select",
            "query": "SELECT status, connected_at, token_expiry FROM connection_requests WHERE user_id = {{$json.user_id}} AND platform = {{$json.platform}}"
        },
        
        "3_return_status": {
            "type": "n8n-nodes-base.respondToWebhook",
            "responseData": {
                "connected": "={{$json[0]?.status === 'authorized'}}",
                "status": "={{$json[0]?.status || 'not_connected'}}",
                "connected_at": "={{$json[0]?.connected_at}}",
                "token_expires_at": "={{$json[0]?.token_expiry}}"
            }
        }
    }
}


"""
==============================================================================
INSTRUCCIONES DE IMPLEMENTACIÓN
==============================================================================

1. CREAR FLUJOS EN n8n:
   - Acceder a http://localhost:5678
   - Crear nuevo flujo para cada plataforma
   - Copiar los nodos según la estructura anterior
   - Configurar variables de entorno

2. CONFIGURAR WEBHOOKS:
   - Cada flujo debe tener un webhook como punto de entrada
   - Activar los webhooks
   - Guardar las URLs de webhook

3. PROBAR FLUJOS:
   - Usar curl para probar los webhooks
   - Verificar que los datos se guardan en PostgreSQL
   - Validar que los URLs de OAuth son correctos

4. AJUSTAR SEGÚN NECESIDAD:
   - Cada plataforma tiene endpoints ligeramente diferentes
   - Revisar documentación oficial de OAuth para cada una
   - Validar que los scopes solicitados son los correctos

5. SEGURIDAD:
   - Validar siempre el state parameter
   - Encriptar tokens en la BD
   - Usar HTTPS en producción
   - Implementar rate limiting
   - Registrar todas las actividades en oauth_logs
"""
