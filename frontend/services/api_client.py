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
        
        # Dados mockados em memória para fallback se a API real estiver indisponível
        self._initialize_mocks()

    def _initialize_mocks(self):
        self._mock_users = {
            "medico@hospital.com": {
                "id": 1,
                "email": "medico@hospital.com",
                "full_name": "Dr. João Silva",
                "role": "profissional",
                "is_active": True,
                "created_at": "2024-01-15T09:00:00Z"
            },
            "gestor@hospital.com": {
                "id": 2,
                "email": "gestor@hospital.com",
                "full_name": "Dra. Maria Helena",
                "role": "gestor",
                "is_active": True,
                "created_at": "2024-01-15T09:00:00Z"
            },
            "auditor@hospital.com": {
                "id": 3,
                "email": "auditor@hospital.com",
                "full_name": "Auditor Carlos Drummond",
                "role": "auditor",
                "is_active": True,
                "created_at": "2024-01-15T09:00:00Z"
            },
            "admin@hospital.com": {
                "id": 4,
                "email": "admin@hospital.com",
                "full_name": "Admin GuardIA",
                "role": "admin",
                "is_active": True,
                "created_at": "2024-01-15T09:00:00Z"
            }
        }
        
        self._mock_sessions = [
            {
                "id": 101,
                "title": "Parto Normal — Gestante Clara Lima",
                "patient_code": "PAC-2026-003",
                "professional_id": 1,
                "status": "completed",
                "ira_score": 78.5,
                "ira_level": "critico",
                "score_video": 82.0,
                "score_audio": 79.0,
                "score_document": 72.0,
                "notes": "Procedimento realizado com queixas frequentes de dor e ausência de consentimento prévio para episiotomia.",
                "created_at": "2026-06-24T02:30:00Z",
                "updated_at": "2026-06-24T03:15:00Z",
                "media_files": [
                    {
                        "id": 501,
                        "media_type": "video",
                        "filename": "parto_clara_lima_core.mp4",
                        "blob_url": "https://storageaccount.blob.core.windows.net/media/101/parto_clara_lima_core.mp4",
                        "file_size_bytes": 145020120,
                        "status": "analyzed",
                        "analysis_score": 82.0,
                        "uploaded_at": "2026-06-24T02:32:00Z"
                    },
                    {
                        "id": 502,
                        "media_type": "audio",
                        "filename": "parto_clara_lima_audio.wav",
                        "blob_url": "https://storageaccount.blob.core.windows.net/media/101/parto_clara_lima_audio.wav",
                        "file_size_bytes": 45020120,
                        "status": "analyzed",
                        "analysis_score": 79.0,
                        "uploaded_at": "2026-06-24T02:32:00Z"
                    },
                    {
                        "id": 503,
                        "media_type": "document",
                        "filename": "prontuario_clara_lima.pdf",
                        "blob_url": "https://storageaccount.blob.core.windows.net/media/101/prontuario_clara_lima.pdf",
                        "file_size_bytes": 1045000,
                        "status": "analyzed",
                        "analysis_score": 72.0,
                        "uploaded_at": "2026-06-24T02:35:00Z"
                    }
                ]
            },
            {
                "id": 102,
                "title": "Consulta de Pré-Natal — Gestante Vanessa Souza",
                "patient_code": "PAC-2026-004",
                "professional_id": 1,
                "status": "completed",
                "ira_score": 45.2,
                "ira_level": "moderado",
                "score_video": 40.0,
                "score_audio": 52.0,
                "score_document": 42.0,
                "notes": "Paciente relatou desconforto leve nas costas, mas sem outros sintomas ou intercorrências significativas.",
                "created_at": "2026-06-24T04:10:00Z",
                "updated_at": "2026-06-24T04:40:00Z",
                "media_files": [
                    {
                        "id": 504,
                        "media_type": "video",
                        "filename": "consulta_vanessa.mp4",
                        "blob_url": "https://storageaccount.blob.core.windows.net/media/102/consulta_vanessa.mp4",
                        "file_size_bytes": 82030400,
                        "status": "analyzed",
                        "analysis_score": 40.0,
                        "uploaded_at": "2026-06-24T04:11:00Z"
                    }
                ]
            },
            {
                "id": 103,
                "title": "Procedimento Cesárea — Gestante Amanda Reis",
                "patient_code": "PAC-2026-005",
                "professional_id": 1,
                "status": "processing",
                "ira_score": None,
                "ira_level": None,
                "score_video": None,
                "score_audio": None,
                "score_document": None,
                "notes": "Procedimento cirúrgico programado. Aguardando processamento multimodal das mídias enviadas.",
                "created_at": "2026-06-24T05:55:00Z",
                "updated_at": "2026-06-24T06:05:00Z",
                "media_files": [
                    {
                        "id": 505,
                        "media_type": "video",
                        "filename": "cesarea_amanda.mp4",
                        "blob_url": None,
                        "file_size_bytes": 340102000,
                        "status": "processing",
                        "analysis_score": None,
                        "uploaded_at": "2026-06-24T06:00:00Z"
                    }
                ]
            },
            {
                "id": 104,
                "title": "Parto Normal — Gestante Beatriz Gomes",
                "patient_code": "PAC-2026-006",
                "professional_id": 1,
                "status": "completed",
                "ira_score": 22.1,
                "ira_level": "baixo",
                "score_video": 18.0,
                "score_audio": 24.0,
                "score_document": 26.0,
                "notes": "Parto tranquilo, comunicação positiva em todos os momentos, termo assinado e documentado.",
                "created_at": "2026-06-23T14:20:00Z",
                "updated_at": "2026-06-23T15:10:00Z",
                "media_files": []
            }
        ]

        self._mock_alerts = [
            {
                "id": 801,
                "session_id": 101,
                "alert_type": "expressao_sofrimento",
                "severity": "critical",
                "title": "Expressão de Dor Intensa",
                "description": "Detectadas expressões de dor extrema e sofrimento em 14 frames consecutivos durante o procedimento.",
                "ira_score": 82.0,
                "is_acknowledged": False,
                "acknowledged_by": None,
                "acknowledged_at": None,
                "email_sent": True,
                "created_at": "2026-06-24T03:15:00Z"
            },
            {
                "id": 802,
                "session_id": 101,
                "alert_type": "consentimento_ausente",
                "severity": "critical",
                "title": "Falta de Consentimento Informado",
                "description": "Ausência do termo de consentimento prévio para episiotomia identificada nos arquivos do prontuário.",
                "ira_score": 72.0,
                "is_acknowledged": False,
                "acknowledged_by": None,
                "acknowledged_at": None,
                "email_sent": True,
                "created_at": "2026-06-24T03:15:00Z"
            },
            {
                "id": 803,
                "session_id": 102,
                "alert_type": "sentimento_negativo",
                "severity": "moderate",
                "title": "Sentimento Negativo Relevante",
                "description": "Detecção de sentimento negativo elevado (0.76) na voz da gestante em trechos específicos de reclamação.",
                "ira_score": 52.0,
                "is_acknowledged": True,
                "acknowledged_by": 2,
                "acknowledged_at": "2026-06-24T05:30:00Z",
                "email_sent": False,
                "created_at": "2026-06-24T04:40:00Z"
            }
        ]

        self._mock_transcriptions = {
            101: {
                "full_text": "Profissional: Fica calma, já vamos terminar, não se mova. Paciente: Está doendo demais, para por favor! Eu não queria fazer isso agora. Profissional: É necessário para o bebê nascer, colabore.",
                "segments": [
                    {"speaker": "Speaker_0", "role": "profissional", "start": 12.5, "end": 18.2, "text": "Fica calma, já vamos terminar, não se mova.", "sentiment": "neutral", "sentiment_confidence": 0.82},
                    {"speaker": "Speaker_1", "role": "paciente", "start": 19.0, "end": 26.5, "text": "Está doendo demais, para por favor! Eu não queria fazer isso agora.", "sentiment": "negative", "sentiment_confidence": 0.98},
                    {"speaker": "Speaker_0", "role": "profissional", "start": 27.2, "end": 32.0, "text": "É necessário para o bebê nascer, colabore.", "sentiment": "neutral", "sentiment_confidence": 0.70}
                ]
            },
            102: {
                "full_text": "Profissional: Bom dia Vanessa, tudo bem? Sentiu alguma dor? Paciente: Bom dia Doutor. Só um desconforto leve nas costas ao deitar.",
                "segments": [
                    {"speaker": "Speaker_0", "role": "profissional", "start": 0.5, "end": 5.0, "text": "Bom dia Vanessa, tudo bem? Sentiu alguma dor?", "sentiment": "positive", "sentiment_confidence": 0.90},
                    {"speaker": "Speaker_1", "role": "paciente", "start": 6.2, "end": 11.8, "text": "Bom dia Doutor. Só um desconforto leve nas costas ao deitar.", "sentiment": "neutral", "sentiment_confidence": 0.85}
                ]
            }
        }
        
        self._mock_risk_details = {
            101: {
                "video": {
                    "text": "Detectadas expressões faciais de dor em múltiplos momentos (confiança média de 85%). Postura com braços contraídos identificada como indicativo de sofrimento físico.",
                    "key_indicators": ["dor_facial_alta_confianca", "postura_sofrimento"],
                    "recommendation": "Garantir a verificação imediata de conforto físico da gestante."
                },
                "audio": {
                    "text": "Sentimento de desespero e expressões 'tá doendo' e 'para' identificadas com alta intensidade. A voz do profissional manteve estabilidade sem entonações agressivas.",
                    "key_indicators": ["verbalizacao_dor", "sentimento_negativo"],
                    "recommendation": "Oferecer alternativas analgésicas ou suporte psicológico ativo."
                },
                "document": {
                    "text": "Verificação de inconsistência grave: termo de consentimento livre e esclarecido para episiotomia não foi digitalizado nem preenchido no prontuário eletrônico.",
                    "key_indicators": ["consentimento_ausente"],
                    "recommendation": "Solicitar preenchimento e assinatura obrigatória do formulário de consentimento."
                }
            },
            102: {
                "video": {
                    "text": "Expressões faciais tranquilas em 95% do tempo. Nenhuma detecção de alteração física ou postura de sofrimento.",
                    "key_indicators": [],
                    "recommendation": "Seguir acompanhamento padrão."
                },
                "audio": {
                    "text": "Sentimento predominante neutro-positivo. Sem falas indicativas de risco ou keywords de dor aguda.",
                    "key_indicators": [],
                    "recommendation": "Nenhuma ação corretiva de comunicação necessária."
                },
                "document": {
                    "text": "Prontuário completo. Todas as assinaturas do médico e termos de consentimento geral estão presentes.",
                    "key_indicators": [],
                    "recommendation": "Prontuário verificado e em conformidade."
                }
            }
        }

    # ============ AUTHENTICATION ============
    def login(self, email, password):
        try:
            # Tentar chamada real
            response = httpx.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": email, "password": password},
                timeout=2.0
            )
            if response.status_code == 200:
                data = response.json()
                # Buscar perfil para incluir no retorno
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
            log.warning("api_client.login.fallback", error=str(e))
        
        # Fallback Mock
        if email in self._mock_users:
            user = self._mock_users[email]
            return {
                "access_token": f"mocked_jwt_token_for_{user['role']}",
                "refresh_token": "mocked_refresh_token",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": user
            }
        return None

    def get_me(self, token):
        try:
            response = httpx.get(
                f"{self.base_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=2.0
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            log.warning("api_client.get_me.fallback", error=str(e))
            
        # Fallback Mock
        for user in self._mock_users.values():
            if token == f"mocked_jwt_token_for_{user['role']}":
                return user
        return {
            "id": 999,
            "email": "offline@guardia.com",
            "full_name": "Dr. Usuário Offline",
            "role": "profissional",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

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
                timeout=2.0
            )
            if response.status_code == 200:
                return response.json()["items"]
        except Exception as e:
            log.warning("api_client.get_sessions.fallback", error=str(e))
        
        # Fallback Mock
        # Se for profissional, filtra ou não dependendo da regra de negócio de exibir apenas as próprias (aqui mock_sessions pertencem a prof 1)
        sessions = self._mock_sessions
        if status_filter:
            sessions = [s for s in sessions if s["status"] == status_filter]
        return sessions

    def get_session_details(self, token, session_id):
        try:
            response = httpx.get(
                f"{self.base_url}/api/v1/sessions/{session_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=2.0
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            log.warning("api_client.get_session_details.fallback", error=str(e))
        
        # Fallback Mock
        for session in self._mock_sessions:
            if session["id"] == int(session_id):
                return session
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
                timeout=2.0
            )
            if response.status_code == 201:
                return response.json()["session"]
        except Exception as e:
            log.warning("api_client.create_session.fallback", error=str(e))
        
        # Fallback Mock
        new_id = max([s["id"] for s in self._mock_sessions]) + 1
        new_session = {
            "id": new_id,
            "title": title,
            "patient_code": patient_code,
            "professional_id": 1,
            "status": "created",
            "ira_score": None,
            "ira_level": None,
            "score_video": None,
            "score_audio": None,
            "score_document": None,
            "notes": notes,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "media_files": []
        }
        self._mock_sessions.insert(0, new_session)
        return new_session

    def upload_media(self, token, session_id, file_name, file_bytes, media_type):
        try:
            files = {"file": (file_name, file_bytes, "application/octet-stream")}
            data = {"media_type": media_type}
            response = httpx.post(
                f"{self.base_url}/api/v1/sessions/{session_id}/media",
                headers={"Authorization": f"Bearer {token}"},
                files=files,
                data=data,
                timeout=5.0
            )
            if response.status_code == 202:
                return response.json()
        except Exception as e:
            log.warning("api_client.upload_media.fallback", error=str(e))
        
        # Fallback Mock
        for session in self._mock_sessions:
            if session["id"] == int(session_id):
                # Criar nova mídia mockada
                new_media_id = 900 + len(session["media_files"])
                new_media = {
                    "id": new_media_id,
                    "media_type": media_type,
                    "filename": file_name,
                    "blob_url": f"https://storageaccount.blob.core.windows.net/media/{session_id}/{file_name}",
                    "file_size_bytes": len(file_bytes),
                    "status": "processing",
                    "analysis_score": None,
                    "uploaded_at": datetime.now(timezone.utc).isoformat()
                }
                session["media_files"].append(new_media)
                session["status"] = "processing"
                
                # Inicia um thread/timer simulando processamento (mas para UI instantâneo apenas retorna)
                return new_media
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
                timeout=2.0
            )
            if response.status_code == 200:
                return response.json()["items"]
        except Exception as e:
            log.warning("api_client.get_alerts.fallback", error=str(e))
        
        # Fallback Mock
        alerts = self._mock_alerts
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
        if unacknowledged_only:
            alerts = [a for a in alerts if not a["is_acknowledged"]]
        return alerts

    def acknowledge_alert(self, token, alert_id):
        try:
            response = httpx.patch(
                f"{self.base_url}/api/v1/alerts/{alert_id}/acknowledge",
                headers={"Authorization": f"Bearer {token}"},
                timeout=2.0
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            log.warning("api_client.acknowledge_alert.fallback", error=str(e))
        
        # Fallback Mock
        for alert in self._mock_alerts:
            if alert["id"] == int(alert_id):
                alert["is_acknowledged"] = True
                alert["acknowledged_by"] = 1 # João Silva
                alert["acknowledged_at"] = datetime.now(timezone.utc).isoformat()
                return alert
        return None

    # ============ RELATÓRIOS ============
    def generate_report(self, token, session_id, format="pdf", include_transcription=True, include_key_frames=True):
        try:
            # Relatório gerado no report-service ou gateway
            response = httpx.post(
                f"{self.report_service_url}/api/v1/reports/generate",
                json={
                    "session_id": str(session_id),
                    "report_type": "session",
                    "report_format": format,
                    "include_transcription": include_transcription,
                    "include_key_frames": include_key_frames
                },
                timeout=5.0
            )
            if response.status_code in (200, 202):
                return response.json()
        except Exception as e:
            log.warning("api_client.generate_report.fallback", error=str(e))
            
        # Fallback Mock
        return {
            "report_id": f"mock-rep-{session_id}-{int(time.time())}",
            "status": "completed", # retorna como finalizado imediatamente no mock
            "estimated_seconds": 0
        }

    def get_report_details(self, token, report_id):
        try:
            response = httpx.get(
                f"{self.report_service_url}/api/v1/reports/{report_id}",
                timeout=2.0
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            log.warning("api_client.get_report_details.fallback", error=str(e))
        
        # Fallback Mock
        return {
            "report_id": report_id,
            "title": f"Relatório de Sessão — Mock",
            "report_type": "session",
            "report_format": "pdf",
            # URL de download mockada que aponta para nosso report-service local se necessário, 
            # ou para um mock local no próprio frontend streamlit para efetuar o download.
            "download_url": f"http://localhost:8501/download_mock?report_id={report_id}",
            "file_size_bytes": 1024 * 150, # 150 KB
            "file_hash_sha256": "mock-hash-sha256-a1b2c3d4e5f6g7h8",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": datetime.now(timezone.utc).isoformat()
        }

    def download_report_file(self, token, download_url):
        try:
            internal_url = download_url
            if "localhost:8005" in download_url:
                internal_url = download_url.replace("http://localhost:8005", self.report_service_url)
            
            headers = {"Authorization": f"Bearer {token}"}
            response = httpx.get(internal_url, headers=headers, timeout=10.0)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            log.warning("api_client.download_report_file.failed", url=download_url, error=str(e))
        return None

    # Mocks para detalhes e transcrições adicionais
    def get_mock_transcription(self, session_id):
        return self._mock_transcriptions.get(int(session_id), None)

    def get_mock_risk_details(self, session_id):
        return self._mock_risk_details.get(int(session_id), None)
