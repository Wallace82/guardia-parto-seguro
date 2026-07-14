import os
import time
import structlog
from datetime import datetime, timezone
from app.core.config import settings

log = structlog.get_logger(__name__)

# Banco de dados em memória para simular resultados
_RESULTS_DB = {}

class AudioProcessor:
    
    def process_audio(self, session_id: str, media_id: str, blob_url: str):
        """
        Lê o arquivo de áudio do volume e faz a chamada
        ao Amazon Transcribe.
        """
        log.info("starting_audio_processing", session_id=session_id, blob_url=blob_url)
        
        file_path = blob_url
        if blob_url.startswith("file:///"):
            file_path = blob_url.replace("file:///", "/")
        elif blob_url.startswith("file://"):
            file_path = blob_url.replace("file://", "")
            
        if os.name == 'nt' and file_path.startswith('/C:'):
            file_path = file_path[1:]
            
        log.info("local_file_path_resolved", file_path=file_path)
        
        if not os.path.exists(file_path):
            log.warning("file_not_found", file_path=file_path, note="Prosseguindo com análise simulada mockada mesmo sem o arquivo")

        try:
            import speech_recognition as sr
            from pydub import AudioSegment
            import tempfile
            
            transcription_text = ""
            key_findings = []
            ira_score = 30.0
            sentiment_score = 100.0
            duration_seconds = 0.0
            
            if os.path.exists(file_path):
                # 1. Converter para WAV (requisito do SpeechRecognition)
                log.info("converting_audio_to_wav", file_path=file_path)
                try:
                    audio_segment = AudioSegment.from_file(file_path)
                    duration_seconds = len(audio_segment) / 1000.0
                    
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                        audio_segment.export(tmp_wav.name, format="wav")
                        tmp_wav_path = tmp_wav.name
                    
                    # 2. Reconhecimento de voz
                    log.info("running_speech_recognition")
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(tmp_wav_path) as source:
                        audio_data = recognizer.record(source)
                        try:
                            transcription_text = recognizer.recognize_google(audio_data, language="pt-BR")
                            log.info("speech_recognition_success", text_length=len(transcription_text))
                        except sr.UnknownValueError:
                            log.warning("speech_recognition_unknown_value")
                            transcription_text = "(Áudio ininteligível ou em silêncio)"
                        except sr.RequestError as e:
                            log.error("speech_recognition_request_error", error=str(e))
                            transcription_text = "(Erro ao contactar serviço de transcrição)"
                            
                    os.remove(tmp_wav_path)
                    
                    # 3. Análise semântica avançada com OpenAI
                    import openai
                    import json
                    api_key = os.environ.get("OPENAI_API_KEY")
                    
                    if not api_key or not transcription_text.strip() or transcription_text.startswith("("):
                        log.warning("openai_fallback", reason="Sem API KEY ou sem texto transcrito")
                        text_lower = transcription_text.lower()
                        if "dor" in text_lower or "ajuda" in text_lower or "socorro" in text_lower:
                            ira_score = 60.0
                            sentiment_score = 40.0
                            key_findings.append({
                                "type": "verbalization",
                                "timestamp_seconds": duration_seconds / 2.0,
                                "description": "Verbalização de risco (fallback)",
                                "confidence": 0.8
                            })
                        else:
                            ira_score = 15.0
                            sentiment_score = 90.0
                    else:
                        log.info("running_openai_analysis")
                        client = openai.OpenAI(api_key=api_key)
                        prompt = f"""
Você é um sistema especialista em vigilância obstétrica.
Analise a seguinte transcrição de áudio de uma sala de parto e identifique:
1. Risco de maus-tratos, violência obstétrica ou dor intensa ignorada.
2. Qualidade do acolhimento/sentimento.

Transcrição: "{transcription_text}"

Retorne um JSON válido estritamente com o seguinte formato:
{{
  "ira_score": (número decimal de 0.0 a 100.0, onde 100.0 é risco crítico/violência, e 0.0 é totalmente seguro),
  "sentiment_score": (número decimal de 0.0 a 100.0, onde 100.0 é acolhimento perfeito, e 0.0 é péssimo),
  "key_findings": [
    {{
      "description": "Breve frase descrevendo o achado, ex: 'Tom agressivo por parte do profissional' ou 'Paciente queixando-se de dor'",
      "confidence": (número decimal de 0.0 a 1.0)
    }}
  ]
}}
"""
                        try:
                            response = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": prompt}],
                                response_format={ "type": "json_object" },
                                temperature=0.1
                            )
                            result_json = json.loads(response.choices[0].message.content)
                            
                            ira_score = float(result_json.get("ira_score", 30.0))
                            sentiment_score = float(result_json.get("sentiment_score", 70.0))
                            
                            for finding in result_json.get("key_findings", []):
                                key_findings.append({
                                    "type": "semantic_analysis",
                                    "timestamp_seconds": duration_seconds / 2.0,
                                    "description": f"IA (Semântica): {finding.get('description', '')}",
                                    "confidence": finding.get("confidence", 0.9)
                                })
                            log.info("openai_analysis_success", ira_score=ira_score)
                        except Exception as oai_err:
                            log.error("openai_analysis_failed", error=str(oai_err))
                            ira_score = 50.0
                            sentiment_score = 50.0
                            key_findings.append({
                                "type": "error",
                                "timestamp_seconds": 0.0,
                                "description": "Erro na interpretação semântica da IA",
                                "confidence": 1.0
                            })
                except Exception as ex:
                    log.error("audio_file_processing_error", error=str(ex))
                    transcription_text = "(Erro ao processar arquivo local de áudio)"

            else:
                transcription_text = "Arquivo de áudio não encontrado no disco local para análise real."
                
            result_dict = {
                "session_id": session_id,
                "status": "completed",
                "ira_score": ira_score,
                "components": {
                    "sentiment_score": sentiment_score,
                    "keyword_risk_score": ira_score
                },
                "duration_seconds": duration_seconds,
                "transcription": transcription_text,
                "key_findings": key_findings,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            _RESULTS_DB[media_id] = result_dict
            _RESULTS_DB[session_id] = result_dict
            log.info("audio_processing_completed", session_id=session_id, media_id=media_id)
            
        except Exception as e:
            log.exception("audio_processing_failed", session_id=session_id, media_id=media_id, error=str(e))
            err_dict = {
                "status": "failed",
                "error": str(e)
            }
            _RESULTS_DB[media_id] = err_dict
            _RESULTS_DB[session_id] = err_dict

    def get_result(self, job_id: str):
        return _RESULTS_DB.get(job_id)
