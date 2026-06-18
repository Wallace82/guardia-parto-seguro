"""
GuardIA — Multimodal Orchestration Service
Coordena o fluxo paralelo de análises, cálculo do IRA e disparo de alertas.
"""
import asyncio
import structlog
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.sessions.models import Session, SessionStatus, MediaFile, MediaStatus
from app.alerts.models import AlertSeverity, AlertType
from app.alerts.service import AlertService
from app.alerts.schemas import AlertCreateRequest
from app.orchestrator.domain_client import DomainClient

log = structlog.get_logger(__name__)

async def orchestrate_session_analysis(session_id: int) -> None:
    """
    Executa a orquestração multimodal da sessão em background:
    1. Chama serviços de vídeo, áudio e documento em paralelo (se as mídias existirem)
    2. Consolida os resultados individuais e chama o risk-service para calcular o IRA
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
            video_file = None
            audio_file = None
            doc_file = None
            
            for f in session.media_files:
                if f.media_type == "video" and f.status == MediaStatus.uploaded:
                    video_file = f
                elif f.media_type == "audio" and f.status == MediaStatus.uploaded:
                    audio_file = f
                elif f.media_type == "document" and f.status == MediaStatus.uploaded:
                    doc_file = f

            # Tasks de análise em paralelo
            tasks = []
            
            if video_file:
                video_file.status = MediaStatus.processing
                tasks.append(client.analyze_video(session_id, video_file.id, video_file.blob_url))
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
            video_score = None
            audio_score = None
            document_score = None
            
            result_idx = 0
            
            if video_file:
                video_res = analysis_results[result_idx]
                result_idx += 1
                if isinstance(video_res, Exception):
                    log.error("video_analysis_failed", session_id=session_id, error=str(video_res))
                    video_file.status = MediaStatus.error
                    video_file.error_message = str(video_res)
                else:
                    # Agora que a análise começou, no fluxo assíncrono nós obtemos os resultados (que no mock retorna imediatamente)
                    try:
                        results_data = await client.get_video_results(session_id)
                        video_score = results_data.get("ira_score")
                        video_file.analysis_score = video_score
                        video_file.status = MediaStatus.analyzed
                    except Exception as e:
                        log.error("video_get_results_failed", session_id=session_id, error=str(e))
                        video_file.status = MediaStatus.error
                        video_file.error_message = str(e)

            if audio_file:
                audio_res = analysis_results[result_idx]
                result_idx += 1
                if isinstance(audio_res, Exception):
                    log.error("audio_analysis_failed", session_id=session_id, error=str(audio_res))
                    audio_file.status = MediaStatus.error
                    audio_file.error_message = str(audio_res)
                else:
                    try:
                        results_data = await client.get_audio_results(session_id)
                        audio_score = results_data.get("ira_score")
                        audio_file.analysis_score = audio_score
                        audio_file.status = MediaStatus.analyzed
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
                    document_score = doc_res.get("ira_score")
                    doc_file.analysis_score = document_score
                    doc_file.status = MediaStatus.analyzed

            await db.commit()

            # Se todos os arquivos de mídia deram erro, a sessão falha
            any_success = (
                (video_file and video_file.status == MediaStatus.analyzed) or
                (audio_file and audio_file.status == MediaStatus.analyzed) or
                (doc_file and doc_file.status == MediaStatus.analyzed)
            )
            if not any_success:
                session.status = SessionStatus.error
                await db.commit()
                log.error("orchestration_failed_all_media_errored", session_id=session_id)
                return

            # Chamar Risk Service para calcular o IRA
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
            
            ira_score = risk_res.get("ira_score", 0.0)
            risk_level = risk_res.get("risk_level", "baixo")
            
            # Atualizar os scores na sessão
            session.ira_score = ira_score
            session.ira_level = risk_level
            session.score_video = video_score
            session.score_audio = audio_score
            session.score_document = document_score
            session.status = SessionStatus.completed
            
            await db.commit()
            log.info("orchestration_completed", session_id=session_id, ira_score=ira_score, level=risk_level)

            # Disparar Alertas se o risco for moderado ou crítico
            if risk_level in ("moderado", "critico"):
                log.info("triggering_alert", session_id=session_id, level=risk_level, score=ira_score)
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
                    title=f"Risco {risk_level.title()} — IRA composto {ira_score}",
                    description=" | ".join(desc_parts) if desc_parts else f"IRA composto atingiu o limiar de risco: {ira_score}.",
                    ira_score=ira_score
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
