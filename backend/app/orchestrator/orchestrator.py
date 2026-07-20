"""
GuardIA — Multimodal Orchestration Service
Coordena o fluxo paralelo de análises, cálculo do IGA e disparo de alertas.
"""
import asyncio
import structlog
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.sessions.models import Session, SessionStatus, MediaFile, MediaStatus
from app.sessions.analysis_models import VideoAnalysis, AudioAnalysis, DocumentAnalysis
from app.alerts.models import AlertSeverity, AlertType
from app.alerts.service import AlertService
from app.alerts.schemas import AlertCreateRequest
from app.orchestrator.domain_client import DomainClient

log = structlog.get_logger(__name__)

async def orchestrate_session_analysis(session_id: int) -> None:
    """
    Executa a orquestração multimodal da sessão em background:
    1. Chama serviços de vídeo, áudio e documento em paralelo (se as mídias existirem)
    2. Consolida os resultados individuais e chama o risk-service para calcular o IGA
    3. Registra os scores calculados na sessão
    4. Dispara alertas para a engine de alertas se o risco for moderado ou crítico
    5. Solicita a geração do relatório de sessão
    """
    client = DomainClient()
    
    async with AsyncSessionLocal() as db:
        try:
            log.info("orchestration_started", session_id=session_id)
            
            # Buscar sessão com seus arquivos de mídia
            result = await db.execute(
                select(Session)
                .options(selectinload(Session.media_files))
                .where(Session.id == session_id)
            )
            session = result.scalar_one_or_none()
            if not session:
                log.error("orchestration_failed_session_not_found", session_id=session_id)
                return

            # Atualiza status para processing
            session.status = SessionStatus.processing
            await db.commit()

            # Separar arquivos de mídia por tipo
            video_files = []
            audio_file = None
            doc_file = None
            
            for f in session.media_files:
                if f.media_type == "video" and f.status == MediaStatus.uploaded:
                    video_files.append(f)
                elif f.media_type == "audio" and f.status == MediaStatus.uploaded:
                    audio_file = f
                elif f.media_type == "document" and f.status == MediaStatus.uploaded:
                    doc_file = f

            # Tasks de análise em paralelo
            tasks = []
            
            for vf in video_files:
                vf.status = MediaStatus.processing
                tasks.append(client.analyze_video(session_id, vf.id, vf.blob_url))
            if audio_file:
                audio_file.status = MediaStatus.processing
                tasks.append(client.analyze_audio(session_id, audio_file.id, audio_file.blob_url))
            if doc_file:
                doc_file.status = MediaStatus.processing
                tasks.append(client.analyze_document(session_id, doc_file.id, doc_file.blob_url))

            await db.commit()

            if not tasks:
                log.warning("orchestration_no_media_to_process", session_id=session_id)
                session.status = SessionStatus.completed
                await db.commit()
                return

            # Executa requisições de análise em paralelo
            analysis_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Mapear os resultados de volta para os arquivos de mídia correspondentes
            result_idx = 0
            
            for vf in video_files:
                video_res = analysis_results[result_idx]
                result_idx += 1
                if isinstance(video_res, Exception):
                    log.error("video_analysis_failed", session_id=session_id, media_id=vf.id, error=str(video_res))
                    vf.status = MediaStatus.error
                    vf.error_message = str(video_res)
                else:
                    # Polling para aguardar a conclusão do processamento assíncrono do vídeo
                    try:
                        for _ in range(120):
                            results_data = await client.get_video_results(vf.id)
                            if results_data.get("status") == "completed":
                                vf.analysis_score = results_data.get("iga_score")
                                vf.status = MediaStatus.analyzed
                                
                                # Salva na tabela detalhada
                                v_analysis = VideoAnalysis(
                                    session_id=session_id,
                                    arquivo_video=vf.filename,
                                    duracao=results_data.get("duration_seconds", 0),
                                    modelo_utilizado="DeepFace + MediaPipe",
                                    emotion_score=results_data.get("components", {}).get("emotion_score"),
                                    body_language_score=results_data.get("components", {}).get("pose_score"),
                                    eventos_detectados={"key_findings": results_data.get("key_findings", [])}
                                )
                                db.add(v_analysis)
                                break
                            elif results_data.get("status") in ["error", "failed"]:
                                raise Exception(results_data.get("message") or results_data.get("error", "Video analysis error"))
                            await asyncio.sleep(5.0)
                        else:
                            raise Exception("Timeout aguardando processamento do vídeo")
                    except Exception as e:
                        log.error("video_get_results_failed", session_id=session_id, media_id=vf.id, error=str(e))
                        vf.status = MediaStatus.error
                        vf.error_message = str(e)

            if audio_file:
                audio_res = analysis_results[result_idx]
                result_idx += 1
                if isinstance(audio_res, Exception):
                    log.error("audio_analysis_failed", session_id=session_id, error=str(audio_res))
                    audio_file.status = MediaStatus.error
                    audio_file.error_message = str(audio_res)
                else:
                    # Polling para aguardar a conclusão do processamento assíncrono do áudio
                    try:
                        for _ in range(120):
                            results_data = await client.get_audio_results(audio_file.id)
                            if results_data.get("status") == "completed":
                                audio_file.analysis_score = results_data.get("iga_score", results_data.get("ira_score"))
                                audio_file.status = MediaStatus.analyzed
                                
                                # Salva na tabela detalhada
                                a_analysis = AudioAnalysis(
                                    session_id=session_id,
                                    arquivo_audio=audio_file.filename,
                                    transcricao=results_data.get("transcription"),
                                    sentiment_score=results_data.get("components", {}).get("sentiment_score"),
                                    anxiety_score=results_data.get("iga_score", results_data.get("ira_score")),
                                    eventos={"key_findings": results_data.get("key_findings", [])}
                                )
                                db.add(a_analysis)
                                break
                            elif results_data.get("status") in ["error", "failed"]:
                                raise Exception(results_data.get("message") or results_data.get("error", "Audio analysis error"))
                            await asyncio.sleep(5.0)
                        else:
                            raise Exception("Timeout aguardando processamento do áudio")
                    except Exception as e:
                        log.error("audio_get_results_failed", session_id=session_id, error=str(e))
                        audio_file.status = MediaStatus.error
                        audio_file.error_message = str(e)

            if doc_file:
                doc_res = analysis_results[result_idx]
                result_idx += 1
                if isinstance(doc_res, Exception):
                    log.error("document_analysis_failed", session_id=session_id, error=str(doc_res))
                    doc_file.status = MediaStatus.error
                    doc_file.error_message = str(doc_res)
                else:
                    doc_file.analysis_score = doc_res.get("iga_score")
                    doc_file.status = MediaStatus.analyzed
                    
                    # Salva na tabela detalhada
                    d_analysis = DocumentAnalysis(
                        session_id=session_id,
                        arquivo_documento=doc_file.filename,
                        tipo_documento=doc_res.get("document_type"),
                        texto_extraido=doc_res.get("ocr_text"),
                        entidades_detectadas=doc_res.get("extracted_fields"),
                        clinical_risk_score=doc_res.get("iga_score"),
                        fatores_identificados={
                            "consistency_checks": doc_res.get("consistency_checks"),
                            "estruturado": doc_res.get("extracted_fields"),
                            "raw_ai_analysis": doc_res.get("raw_ai_analysis")
                        },
                        confidence_score=doc_res.get("completeness_score")
                    )
                    db.add(d_analysis)

            await db.commit()

            # Se todos os arquivos de mídia deram erro, a sessão falha
            any_success = any(
                m.status == MediaStatus.analyzed for m in session.media_files
            )
            if not any_success:
                session.status = SessionStatus.error
                await db.commit()
                log.error("orchestration_failed_all_media_errored", session_id=session_id)
                return

            # Calcular os scores de vídeo, áudio e documento consolidados da sessão
            all_video_scores = [
                m.analysis_score for m in session.media_files
                if m.media_type == "video" and m.status == MediaStatus.analyzed and m.analysis_score is not None
            ]
            video_score = max(all_video_scores) if all_video_scores else None

            all_audio_scores = [
                m.analysis_score for m in session.media_files
                if m.media_type == "audio" and m.status == MediaStatus.analyzed and m.analysis_score is not None
            ]
            audio_score = max(all_audio_scores) if all_audio_scores else None

            all_doc_scores = [
                m.analysis_score for m in session.media_files
                if m.media_type == "document" and m.status == MediaStatus.analyzed and m.analysis_score is not None
            ]
            document_score = max(all_doc_scores) if all_doc_scores else None

            # Chamar Risk Service para calcular o IGA
            log.info("correlating_risk", session_id=session_id, scores={
                "video": video_score, "audio": audio_score, "document": document_score
            })
            
            risk_res = await client.correlate_risk(
                session_id=session_id,
                patient_code=session.patient_code,
                video_score=video_score,
                audio_score=audio_score,
                document_score=document_score
            )
            
            iga_score = risk_res.get("iga_score", 0.0)
            risk_level = risk_res.get("risk_level", "baixo")
            
            # Atualizar os scores provisoriamente
            session.iga_score = iga_score
            session.iga_level = risk_level
            session.score_video = video_score
            session.score_audio = audio_score
            session.score_document = document_score
            session.status = SessionStatus.completed
            
            await db.commit()
            
            # Recalcula localmente usando a RiskFusionEngine (para aplicar regras avançadas
            # de Correlação Transmodal e sincronizar os scores retroativos nos MediaFiles)
            try:
                from app.sessions.service import SessionService
                await SessionService(db)._recalculate_session_risk(session_id)
            except Exception as re_err:
                log.error("orchestrator_recalculate_failed", session_id=session_id, error=str(re_err))
            log.info("orchestration_completed", session_id=session_id, iga_score=iga_score, level=risk_level)

            # Disparar Alertas se o risco for moderado ou crítico
            if risk_level in ("moderado", "critico"):
                log.info("triggering_alert", session_id=session_id, level=risk_level, score=iga_score)
                alert_severity = AlertSeverity.critical if risk_level == "critico" else AlertSeverity.moderate
                
                # Consolidar justificativas em descrição
                justifications = risk_res.get("justifications", {})
                desc_parts = []
                for component, data in justifications.items():
                    if data.get("text"):
                        desc_parts.append(f"[{component.upper()}] {data['text']}")
                
                alert_req = AlertCreateRequest(
                    session_id=session_id,
                    alert_type=AlertType.ira_threshold.value,
                    severity=alert_severity.value,
                    title=f"Risco {risk_level.title()} — IGA composto {iga_score}",
                    description=" | ".join(desc_parts) if desc_parts else f"IGA composto atingiu o limiar de risco: {iga_score}.",
                    iga_score=iga_score
                )
                
                alert_service = AlertService(db)
                await alert_service.create_alert(alert_req)
                await db.commit()

            # Solicitar geração de relatório
            try:
                log.info("generating_session_report", session_id=session_id)
                await client.generate_report(session_id)
            except Exception as e:
                # Falha na geração do relatório não deve falhar a orquestração inteira
                log.error("report_generation_failed", session_id=session_id, error=str(e))

        except Exception as e:
            log.error("orchestration_unexpected_error", session_id=session_id, error=str(e))
            # Tenta marcar a sessão como erro
            try:
                result = await db.execute(select(Session).where(Session.id == session_id))
                sess = result.scalar_one_or_none()
                if sess:
                    sess.status = SessionStatus.error
                    await db.commit()
            except Exception as inner_e:
                log.error("orchestration_rollback_failed", error=str(inner_e))
                await db.rollback()
            raise e
