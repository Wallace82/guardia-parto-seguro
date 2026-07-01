import os
import time
import httpx
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
class StandardLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    def warning(self, event, **kwargs):
        self.logger.warning(f"{event} - {kwargs}")
    def info(self, event, **kwargs):
        self.logger.info(f"{event} - {kwargs}")
    def error(self, event, **kwargs):
        self.logger.error(f"{event} - {kwargs}")

log = StandardLogger(__name__)

class APIClient:
    def __init__(self):
        # Em ambiente docker compose, a URL será http://core-api:8000
        # Em ambiente local (fora do docker), pode ser http://localhost:8000
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
        # O report service pode ser chamado diretamente para downloads ou via API client se necessário
        self.report_service_url = os.getenv("REPORT_SERVICE_URL", "http://localhost:8005").rstrip("/")

    # ============ AUTHENTICATION ============
    def login(self, email, password):
        try:
            response = httpx.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": email, "password": password},
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                access_token = data["access_token"]
                me_response = httpx.get(
                    f"{self.base_url}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if me_response.status_code == 200:
                    data["user"] = me_response.json()
                else:
                    data["user"] = {
                        "id": 1,
                        "email": email,
                        "full_name": "Usuário",
                        "role": "profissional"
                    }
                return data
        except Exception as e:
            log.error("api_client.login.failed", error=str(e))
        return None

    def get_me(self, token):
        try:
            response = httpx.get(
                f"{self.base_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            log.error("api_client.get_me.failed", error=str(e))
        return None

    # ============ SESSÕES ============
    def get_sessions(self, token, role="profissional", status_filter=None):
        try:
            params = {}
            if status_filter:
                params["status"] = status_filter
            response = httpx.get(
                f"{self.base_url}/api/v1/sessions/",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()["items"]
        except Exception as e:
            log.error("api_client.get_sessions.failed", error=str(e))
        return []

    def get_session_details(self, token, session_id):
        try:
            response = httpx.get(
                f"{self.base_url}/api/v1/sessions/{session_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            log.error("api_client.get_session_details.failed", error=str(e))
        return None

    def create_session(self, token, title, patient_code, notes=""):
        try:
            response = httpx.post(
                f"{self.base_url}/api/v1/sessions/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "title": title,
                    "patient_code": patient_code,
                    "notes": notes
                },
                timeout=5.0
            )
            if response.status_code == 201:
                return response.json()["session"]
        except Exception as e:
            log.error("api_client.create_session.failed", error=str(e))
        return None

    def upload_media(self, token, session_id, file_name, file_bytes, media_type):
        try:
            files = {"file": (file_name, file_bytes, "application/octet-stream")}
            data = {"media_type": media_type}
            response = httpx.post(
                f"{self.base_url}/api/v1/sessions/{session_id}/media",
                headers={"Authorization": f"Bearer {token}"},
                files=files,
                data=data,
                timeout=10.0
            )
            if response.status_code == 202:
                return response.json()
        except Exception as e:
            log.error("api_client.upload_media.failed", error=str(e))
        return None

    # ============ ALERTAS ============
    def get_alerts(self, token, severity=None, unacknowledged_only=False):
        try:
            params = {}
            if severity:
                params["severity"] = severity
            if unacknowledged_only:
                params["unacknowledged_only"] = str(unacknowledged_only).lower()
                
            response = httpx.get(
                f"{self.base_url}/api/v1/alerts/",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()["items"]
        except Exception as e:
            log.error("api_client.get_alerts.failed", error=str(e))
        return []

    def acknowledge_alert(self, token, alert_id):
        try:
            response = httpx.patch(
                f"{self.base_url}/api/v1/alerts/{alert_id}/acknowledge",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            log.error("api_client.acknowledge_alert.failed", error=str(e))
        return None

    # ============ RELATÓRIOS ============
    def generate_report(self, token, session_id, format="pdf", include_transcription=True, include_key_frames=True):
        try:
            response = httpx.post(
                f"{self.report_service_url}/api/v1/reports/generate",
                json={
                    "session_id": str(session_id),
                    "report_type": "session",
                    "report_format": format,
                    "include_transcription": include_transcription,
                    "include_key_frames": include_key_frames
                },
                timeout=10.0
            )
            if response.status_code in (200, 202):
                return response.json()
        except Exception as e:
            log.error("api_client.generate_report.failed", error=str(e))
        return None

    def get_report_details(self, token, report_id):
        try:
            response = httpx.get(
                f"{self.report_service_url}/api/v1/reports/{report_id}",
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            log.error("api_client.get_report_details.failed", error=str(e))
        return None

    def download_report_file(self, token, download_url):
        try:
            internal_url = download_url
            if "localhost:8005" in download_url:
                internal_url = download_url.replace("http://localhost:8005", self.report_service_url)
            
            headers = {"Authorization": f"Bearer {token}"}
            response = httpx.get(internal_url, headers=headers, timeout=15.0)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            log.error("api_client.download_report_file.failed", url=download_url, error=str(e))
        return None

    # ============ ANÁLISE REAL DA SESSÃO ============
    def get_session_analysis(self, token, session_id):
        try:
            response = httpx.get(
                f"{self.base_url}/api/v1/sessions/{session_id}/analysis",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            log.error("api_client.get_session_analysis.failed", error=str(e))
        return None
