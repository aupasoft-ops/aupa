"""
Módulo para conectar redes sociales (Facebook, Instagram, TikTok) a través de n8n.

Provee:
- `SocialMediaConnector`: clase que encapsula llamadas a webhooks de n8n
- `render_social_connector_ui()`: interfaz Streamlit para que un usuario conecte/desconecte cuentas

Requisitos:
- n8n corriendo en `N8N_BASE_URL` (por defecto http://localhost:5678)
- webhooks en n8n: `/webhook/facebook-connect`, `/webhook/instagram-connect`, `/webhook/tiktok-connect`
"""

from typing import Dict, Optional
import os
import requests
import streamlit as st
from datetime import datetime


N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://localhost:5678")
N8N_API_HEALTH = f"{N8N_BASE_URL}/api/v1/health"


class SocialMediaConnector:
	"""Gestor de conexiones con redes sociales vía n8n.

	Métodos principales:
	- check_n8n_health()
	- trigger_oauth_flow(platform, user_id, user_email)
	- get_connection_status(user_id, platform)
	- disconnect_platform(user_id, platform)
	"""

	def __init__(self, n8n_base_url: Optional[str] = None):
		self.n8n_url = n8n_base_url or N8N_BASE_URL
		self.api_health = f"{self.n8n_url}/api/v1/health"
		self.platforms: Dict[str, Dict] = {
			"facebook": {
				"name": "Facebook",
				"webhook": "facebook-connect",
				"scopes": ["pages_manage_metadata", "pages_read_engagement"],
			},
			"instagram": {
				"name": "Instagram",
				"webhook": "instagram-connect",
				"scopes": ["instagram_business_management", "pages_read_user_content"],
			},
			"tiktok": {
				"name": "TikTok",
				"webhook": "tiktok-connect",
				"scopes": ["user.info.basic", "video.list"],
			},
		}

	def check_n8n_health(self) -> bool:
		"""Comprueba si n8n responde en su endpoint de health."""
		try:
			resp = requests.get(self.api_health, timeout=4)
			return resp.status_code == 200
		except Exception:
			return False

	def get_webhook_url(self, platform: str) -> str:
		"""Devuelve la URL del webhook configurado en n8n para la plataforma."""
		p = self.platforms.get(platform)
		if not p:
			raise ValueError(f"Plataforma desconocida: {platform}")
		return f"{self.n8n_url}/webhook/{p['webhook']}"

	def create_connection_request(self, platform: str, user_id: str, user_email: str) -> Dict:
		"""Envía una solicitud al webhook de n8n para iniciar el flujo OAuth.

		Retorna un diccionario con keys: success (bool), message (str), data (opcional)
		"""
		try:
			payload = {
				"platform": platform,
				"user_id": user_id,
				"user_email": user_email,
				"timestamp": datetime.utcnow().isoformat(),
			}
			url = self.get_webhook_url(platform)
			resp = requests.post(url, json=payload, timeout=10)
			if resp.status_code in (200, 201):
				try:
					data = resp.json()
				except Exception:
					data = {"raw_text": resp.text}
				return {"success": True, "message": "Solicitud enviada", "data": data}
			else:
				return {"success": False, "message": f"HTTP {resp.status_code}", "error": resp.text}
		except Exception as e:
			return {"success": False, "message": "Exception", "error": str(e)}

	def trigger_oauth_flow(self, platform: str, user_id: str, user_email: str) -> Optional[str]:
		"""Inicia el flujo OAuth y devuelve la URL de redirección si está disponible."""
		result = self.create_connection_request(platform, user_id, user_email)
		if not result.get("success"):
			return None
		data = result.get("data") or {}
		oauth_url = data.get("oauth_url") if isinstance(data, dict) else None
		if oauth_url:
			return oauth_url
		# Si n8n no retorna oauth_url, proporcionar la URL del webhook como fallback
		return f"{self.get_webhook_url(platform)}?user_id={user_id}&ts={int(datetime.utcnow().timestamp())}"

	def get_connection_status(self, user_id: str, platform: str) -> Dict:
		"""Consulta un endpoint de estado en n8n. Espera JSON con 'connected' bool."""
		try:
			status_url = f"{self.get_webhook_url(platform)}/status"
			resp = requests.get(status_url, params={"user_id": user_id}, timeout=6)
			if resp.status_code == 200:
				try:
					return resp.json()
				except Exception:
					return {"connected": False, "status": "invalid_response"}
			return {"connected": False, "status": "not_found"}
		except Exception as e:
			return {"connected": False, "status": "error", "error": str(e)}

	def disconnect_platform(self, user_id: str, platform: str) -> bool:
		"""Pide a n8n desconectar la cuenta del usuario."""
		try:
			url = f"{self.get_webhook_url(platform)}/disconnect"
			resp = requests.post(url, json={"user_id": user_id}, timeout=8)
			return resp.status_code in (200, 201)
		except Exception:
			return False


def render_social_connector_ui():
	"""Interfaz Streamlit para conectar/desconectar plataformas.

	Usa `SocialMediaConnector` para comunicarse con n8n.
	"""
	st.title("🌐 Conectar Redes Sociales")
	connector = SocialMediaConnector()

	if not connector.check_n8n_health():
		st.error("⚠️ n8n no responde en: {}".format(connector.n8n_url))
		st.info("Inicia n8n: `docker-compose up -d n8n`")
		return

	st.subheader("👤 Datos del usuario")
	col1, col2 = st.columns(2)
	with col1:
		user_id = st.text_input("ID de usuario", value="user_001")
	with col2:
		user_email = st.text_input("Email", value="usuario@ejemplo.com")

	st.write("---")

	cols = st.columns(len(connector.platforms))
	for i, (key, cfg) in enumerate(connector.platforms.items()):
		with cols[i]:
			st.markdown(f"### {cfg['name']}")
			if st.button(f"Conectar {cfg['name']}", key=f"connect_{key}"):
				url = connector.trigger_oauth_flow(key, user_id, user_email)
				if url:
					st.success("URL de autorización generada")
					st.write(url)
				else:
					st.error("No se pudo iniciar el flujo OAuth")

			status = connector.get_connection_status(user_id, key)
			if status.get("connected"):
				st.success("✅ Conectado")
				if st.button(f"Desconectar {cfg['name']}", key=f"disconnect_{key}"):
					if connector.disconnect_platform(user_id, key):
						st.success("Desconectado")
						st.experimental_rerun()
					else:
						st.error("Fallo al desconectar")
			else:
				st.info("No conectado")

	st.write("---")
	with st.expander("ℹ️ Información / Permisos solicitados"):
		st.write(
			"Facebook: pages_manage_metadata, pages_read_engagement\n"
			"Instagram: instagram_business_management, pages_read_user_content\n"
			"TikTok: user.info.basic, video.list"
		)


if __name__ == "__main__":
	# Permite ejecutar el módulo de forma independiente para pruebas rápidas
	st.set_page_config(page_title="Conector Redes Sociales", layout="wide")
	render_social_connector_ui()
