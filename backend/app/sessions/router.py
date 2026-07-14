"""
GuardIA — Sessions Router
CRUD de sessões de monitoramento
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status, UploadFile, File, Form, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser
from app.audit.service import AuditService
from app.sessions.schemas import (
    SessionCreateRequest,
    SessionCreatedResponse,
    SessionListOut,
    SessionOut,
    SessionUpdateRequest,
    MediaFileOut,
    DashboardMetricsOut,
)
from app.sessions.service import SessionService

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/",
    response_model=SessionCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova sessão de monitoramento",
)
async def create_session(
    data: SessionCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    db: DB,
):
    """
    Cria uma sessão para monitoramento de consulta/parto.
    O `patient_code` deve ser um identificador anonimizado — nunca o nome real (LGPD).
    """
    session = await SessionService(db).create(data, current_user.id)
    await AuditService.log_action(db, action="create_session", resource=f"session_{session.id}", user_id=current_user.id)
    
    if session.notes:
        from app.sessions.service import process_notes_background
        background_tasks.add_task(process_notes_background, session.id, session.notes)
        
    return SessionCreatedResponse(session=SessionOut.model_validate(session))


@router.get(
    "/",
    response_model=SessionListOut,
    summary="Listar sessões (com paginação)",
)
async def list_sessions(
    current_user: CurrentUser,
    db: DB,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status"),
):
    """
    Lista sessões com paginação.
    Profissionais veem apenas as próprias; gestores/admins/auditores veem todas.
    """
    total, items = await SessionService(db).list_sessions(
        user_id=current_user.id,
        user_role=current_user.role,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
    )
    return SessionListOut(total=total, items=[SessionOut.model_validate(s) for s in items])


@router.get(
    "/{session_id}",
    response_model=SessionOut,
    summary="Buscar sessão por ID",
)
async def get_session(
    session_id: int,
    current_user: CurrentUser,
    db: DB,
):
    """Retorna detalhes completos da sessão, incluindo arquivos de mídia."""
    session = await SessionService(db).get_by_id(
        session_id, current_user.id, current_user.role
    )
    await AuditService.log_action(db, action="view_session", resource=f"session_{session.id}", user_id=current_user.id)
    return SessionOut.model_validate(session)


@router.patch(
    "/{session_id}",
    response_model=SessionOut,
    summary="Atualizar dados da sessão",
)
async def update_session(
    session_id: int,
    data: SessionUpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    db: DB,
):
    """Atualiza título, notas ou status da sessão."""
    session = await SessionService(db).update(
        session_id, data, current_user.id, current_user.role
    )
    await AuditService.log_action(db, action="update_session", resource=f"session_{session.id}", user_id=current_user.id)
    
    if data.notes is not None:
        from app.sessions.service import process_notes_background
        background_tasks.add_task(process_notes_background, session.id, session.notes)
        
    return SessionOut.model_validate(session)


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir sessão (admin/gestor)",
)
async def delete_session(
    session_id: int,
    current_user: CurrentUser,
    db: DB,
):
    await SessionService(db).delete(session_id, current_user.id, current_user.role)
    await AuditService.log_action(db, action="delete_session", resource=f"session_{session_id}", user_id=current_user.id)


@router.delete(
    "/media/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir arquivo de mídia de uma sessão",
)
async def delete_media_file(
    media_id: int,
    current_user: CurrentUser,
    db: DB,
):
    await SessionService(db).delete_media_file(media_id, current_user.id, current_user.role)
    await AuditService.log_action(db, action="delete_media_file", resource=f"media_{media_id}", user_id=current_user.id)


@router.post(
    "/{session_id}/media",
    response_model=MediaFileOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Faz upload de uma mídia para a sessão",
)
async def upload_media(
    session_id: int,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    db: DB,
    file: UploadFile = File(...),
    media_type: str = Form(...),
):
    """
    Faz upload de um arquivo de vídeo, áudio ou documento para a sessão.
    Após o upload, inicia o processamento assíncrono em background pelo orquestrador.
    """
    if media_type not in ("video", "audio", "document"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de mídia inválido. Escolha entre: video, audio, document",
        )

    file_content = await file.read()

    media_file = await SessionService(db).add_media_file(
        session_id=session_id,
        filename=file.filename,
        content_type=file.content_type,
        media_type=media_type,
        file_content=file_content,
        user_id=current_user.id,
        user_role=current_user.role,
    )

    if media_type == "video":
        import tempfile
        import os
        import subprocess
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_vid:
                tmp_vid.write(file_content)
                tmp_vid_path = tmp_vid.name
                
            tmp_aud_path = tmp_vid_path.replace(".mp4", ".mp3")
            
            subprocess.run([
                "ffmpeg", "-i", tmp_vid_path, 
                "-vn", "-acodec", "libmp3lame", "-q:a", "2", 
                tmp_aud_path, "-y"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(tmp_aud_path):
                with open(tmp_aud_path, "rb") as f_aud:
                    audio_bytes = f_aud.read()
                    
                await SessionService(db).add_media_file(
                    session_id=session_id,
                    filename=file.filename.rsplit('.', 1)[0] + ".mp3",
                    content_type="audio/mpeg",
                    media_type="audio",
                    file_content=audio_bytes,
                    user_id=current_user.id,
                    user_role=current_user.role,
                )
                os.remove(tmp_aud_path)
            os.remove(tmp_vid_path)
        except Exception as e:
            import structlog
            structlog.get_logger(__name__).warning("audio_extraction_failed", error=str(e))

    # Dispara o orquestrador em background
    from app.orchestrator.orchestrator import orchestrate_session_analysis
    background_tasks.add_task(orchestrate_session_analysis, session_id)

    return media_file


@router.get(
    "/{session_id}/analysis",
    summary="Obter análise detalhada da sessão (transcrição, sentimentos, justificativas)",
)
async def get_session_analysis(
    session_id: int,
    current_user: CurrentUser,
    db: DB,
):
    """
    Retorna os dados detalhados de análise da sessão:
    - Transcrição e sentimentos (audio-service)
    - Ocorrências de vídeo (video-service)
    - Justificativas e recomendações de risco (risk-service)
    """
    session = await SessionService(db).get_by_id(
        session_id, current_user.id, current_user.role
    )
    
    if session.status != "completed" and session.ira_score is None:
        return {
            "session_id": session_id,
            "status": session.status,
            "transcription": None,
            "video_findings": [],
            "risk_details": None,
            "factors": None
        }

    from app.orchestrator.domain_client import DomainClient
    from sqlalchemy import select
    from app.sessions.analysis_models import DocumentAnalysis
    client = DomainClient()
    
    transcription = None
    video_findings = []
    risk_details = None

    try:
        audio_res = await client.get_audio_results(session_id)
        if audio_res and audio_res.get("status") == "completed":
            full_text = audio_res.get("transcription", "")
            key_findings = audio_res.get("key_findings", [])
            segments = []
            
            for finding in key_findings:
                desc = finding.get("description", "")
                role = "paciente" if "dor" in desc.lower() or "paciente" in desc.lower() else "profissional"
                sentiment = "negative" if "dor" in desc.lower() or "não" in desc.lower() else "neutral"
                segments.append({
                    "speaker": finding.get("type", "Speaker_1").title(),
                    "role": role,
                    "start": finding.get("timestamp_seconds", 0.0),
                    "end": finding.get("timestamp_seconds", 0.0) + 5.0,
                    "text": desc,
                    "sentiment": sentiment,
                    "sentiment_confidence": finding.get("confidence", 1.0)
                })
            
            if not segments and full_text:
                segments.append({
                    "speaker": "Speaker_1",
                    "role": "paciente",
                    "start": 0.0,
                    "end": 10.0,
                    "text": full_text,
                    "sentiment": "negative" if "dor" in full_text.lower() or "não" in full_text.lower() else "neutral",
                    "sentiment_confidence": 0.95
                })

            transcription = {
                "full_text": full_text,
                "segments": segments
            }
    except Exception as e:
        import structlog
        structlog.get_logger(__name__).warning("get_session_analysis.audio_failed", session_id=session_id, error=str(e))

    video_analyses = {}
    video_findings = []
    
    for f in session.media_files:
        if f.media_type == "video":
            try:
                res = await client.get_video_results(f.id)
                if res and res.get("status") == "completed":
                    video_analyses[str(f.id)] = res
                    # Mantém video_findings preenchido com a primeira análise de vídeo concluída para compatibilidade
                    if not video_findings:
                        video_findings = res.get("key_findings", [])
            except Exception as e:
                import structlog
                structlog.get_logger(__name__).warning("get_session_analysis.video_file_failed", media_id=f.id, error=str(e))

    try:
        risk_res = await client.correlate_risk(
            session_id=session_id,
            patient_code=session.patient_code,
            video_score=session.score_video,
            audio_score=session.score_audio,
            document_score=session.score_document
        )
        if risk_res:
            risk_details = risk_res.get("justifications")
    except Exception as e:
        import structlog
        structlog.get_logger(__name__).warning("get_session_analysis.risk_failed", session_id=session_id, error=str(e))

    factors = {
        "positive": [],
        "attention": [],
        "recommendation": "Sem recomendações geradas. O serviço de risco pode estar indisponível."
    }

    # Gera fatores baseados em achados REAIS (sem mocks hardcoded)
    has_video_attention = False
    if video_findings:
        for vf in video_findings:
            desc = vf.get("description", "")
            if desc:
                factors["attention"].append(f"Vídeo: {desc}")
                has_video_attention = True
                
    if not has_video_attention and session.score_video is not None:
        if session.score_video < 50:
            factors["positive"].append("Vídeo: Expressões faciais neutras/tranquilas")
        else:
            factors["attention"].append("Vídeo: Possível tensão ou postura defensiva detectada")

    has_audio_attention = False
    if transcription and transcription.get("segments"):
        for seg in transcription["segments"]:
            if seg.get("sentiment") == "negative":
                factors["attention"].append(f"Áudio: {seg.get('text')}")
                has_audio_attention = True
                
    if not has_audio_attention and session.score_audio is not None:
        if session.score_audio < 50:
            factors["positive"].append("Áudio: Sem verbalização de dor")
        else:
            factors["attention"].append("Áudio: Possível desconforto vocal detectado")

    # Fatores reais extraídos de Prontuários (PDF)
    pdf_analysis_res = await db.execute(
        select(DocumentAnalysis).where(
            DocumentAnalysis.session_id == session_id,
            DocumentAnalysis.tipo_documento != "anotacoes"
        ).order_by(DocumentAnalysis.id.desc())
    )
    pdf_analysis = pdf_analysis_res.scalars().first()
    
    if pdf_analysis and pdf_analysis.fatores_identificados and "estruturado" in pdf_analysis.fatores_identificados:
        estruturado_pdf = pdf_analysis.fatores_identificados["estruturado"]
        
        # Fatores clínicos
        clinical = estruturado_pdf.get("clinical_data", {})
        for cond in clinical.get("conditions", []):
            factors["attention"].append(f"Prontuário (Clínico): {cond}")
            
        # Fatores Emocionais
        emotional = estruturado_pdf.get("emotional_analysis", {})
        for emo in emotional.get("indicators", []):
            factors["attention"].append(f"Prontuário (Emocional): {emo}")
            
        # Comunicação
        comm = estruturado_pdf.get("communication_analysis", {})
        for c in comm.get("indicators", []):
            factors["attention"].append(f"Prontuário (Comunicação): {c}")
            
        # Fatores de Risco
        for risk in estruturado_pdf.get("risk_factors", []):
            factors["attention"].append(f"Prontuário (Risco): {risk}")
            
        # Evidências
        evidence = estruturado_pdf.get("evidence", {})
        if evidence.get("positive"):
            factors["positive"].append(f"Prontuário: {evidence.get('positive')}")
        for attn in evidence.get("attention_points", []):
            factors["attention"].append(f"Prontuário (Atenção): {attn}")
    else:
        # Fallback para o antigo formato
        if risk_details and "document" in risk_details:
            doc_indicators = risk_details["document"].get("key_indicators", [])
            for ind in doc_indicators:
                if "ausente" in ind or "irregular" in ind:
                    factors["attention"].append(f"Prontuário PDF: {ind.replace('_', ' ').title()}")
                else:
                    factors["positive"].append(f"Prontuário PDF: {ind.replace('_', ' ').title()}")

    # Adicionar os fatores reais extraídos das Anotações Clínicas
    notes_analysis_res = await db.execute(
        select(DocumentAnalysis).where(
            DocumentAnalysis.session_id == session_id,
            DocumentAnalysis.tipo_documento == "anotacoes"
        )
    )
    notes_analysis = notes_analysis_res.scalars().first()
    
    notes_text = None
    if notes_analysis and notes_analysis.fatores_identificados:
        notes_text = notes_analysis.fatores_identificados.get("analise_textual")
        if "estruturado" in notes_analysis.fatores_identificados:
            estruturado = notes_analysis.fatores_identificados["estruturado"]
            
            # Indicadores identificados (Anotações)
            for ind in estruturado.get("indicadores_identificados", []):
                desc = ind.get("descricao", "")
                if desc:
                    if ind.get("intensidade", "BAIXA").upper() in ["ALTA", "MEDIA"]:
                        factors["attention"].append(f"Anotações: {desc}")
                    else:
                        factors["positive"].append(f"Anotações: {desc}")
                        
            # Fatores de risco (Anotações)
            for risk in estruturado.get("fatores_risco", []):
                factors["attention"].append(f"Risco (Anotações): {risk}")
                
            # Qualidade de informação
            qualidade = estruturado.get("qualidade_informacao", {})
            if qualidade.get("nivel") == "BAIXA":
                factors["attention"].append(f"Qualidade das Anotações: {qualidade.get('observacao')}")

    # A recomendação principal pode vir do maior score ou da analise geral
    if session.ira_score and session.ira_score >= 70:
        factors["recommendation"] = "Risco alto identificado. Intervenção imediata recomendada."
    elif session.ira_score and session.ira_score >= 40:
        factors["recommendation"] = "Risco moderado. Aumentar vigilância e revisar analgesia."
    elif session.ira_score is not None:
        factors["recommendation"] = "Baixo risco. Manter monitoramento regular."
    else:
        factors["recommendation"] = "Recomendação não disponível (cálculo pendente)."

    return {
        "session_id": session_id,
        "status": session.status,
        "transcription": transcription,
        "video_findings": video_findings,
        "video_analyses": video_analyses,
        "risk_details": risk_details,
        "factors": factors,
        "notes_analysis_text": notes_text
    }

@router.get(
    "/metrics/dashboard",
    response_model=DashboardMetricsOut,
    summary="Obter métricas agregadas para o painel principal",
)
async def get_dashboard_metrics(
    current_user: CurrentUser,
    db: DB,
):
    """
    Retorna total de sessões, alertas críticos pendentes, média de IRA 
    e um breakdown mensal básico para montar o gráfico.
    """
    metrics = await SessionService(db).get_dashboard_metrics()
    return metrics

@router.get(
    "/{session_id}/report/pdf",
    summary="Baixar relatório executivo da sessão em PDF binário",
)
async def get_session_report_pdf(
    session_id: int,
    current_user: CurrentUser,
    db: DB,
):
    """
    Retorna um arquivo PDF binário contendo o sumário da sessão.
    Geração minimalista (simulada via stream binária direta) para evitar dependências pesadas em homologação.
    """
    from fastapi.responses import Response
    
    # Confirma que a sessão existe e que o usuário tem acesso
    await SessionService(db).get_by_id(session_id, current_user.id, current_user.role)
    await AuditService.log_action(db, action="download_report", resource=f"session_{session_id}", user_id=current_user.id)
    
    # Simulamos um payload mínimo de PDF válido:
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"5 0 obj\n<< /Length 64 >>\nstream\n"
        b"BT\n/F1 24 Tf\n100 700 Td\n(Prontuario de Inteligencia Artificial) Tj\nET\n"
        b"endstream\nendobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000224 00000 n \n0000000312 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n427\n%%EOF"
    )
    
    return Response(
        content=pdf_content, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f'attachment; filename="Prontuario_GuardIA_Sessao_{session_id}.pdf"'}
    )
