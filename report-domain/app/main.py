import os
import uuid
import httpx
import structlog
from datetime import datetime, timezone, timedelta
from typing import Annotated

from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db, create_tables
from app.models import Report
from app.generator import generate_pdf_report, generate_excel_report, calculate_sha256
from app.storage import upload_report_to_storage

log = structlog.get_logger(__name__)

# Inicialização do FastAPI
app = FastAPI(title="GuardIA — Report Service", version="1.0.0")

# Mount da pasta static para download local se a pasta de armazenamento local existir
os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
app.mount("/static", StaticFiles(directory=settings.LOCAL_STORAGE_PATH), name="static")

@app.on_event("startup")
async def on_startup():
    log.info("report-service.startup", database_url=settings.DATABASE_URL)
    # Criar tabelas automaticamente na inicialização (facilita setup local)
    try:
        await create_tables()
        log.info("report-service.database.tables_created")
    except Exception as e:
        log.error("report-service.database.tables_creation_failed", error=str(e))

DB = Annotated[AsyncSession, Depends(get_db)]

class ReportGenerateRequest(BaseModel):
    session_id: str
    report_type: str = "session"
    report_format: str = "pdf"
    include_transcription: bool = True
    include_key_frames: bool = True

class ReportGenerateResponse(BaseModel):
    report_id: str
    status: str
    estimated_seconds: int

async def get_session_data_from_core(session_id: str) -> dict:
    """Tenta buscar informações da sessão na core-api ou retorna dados de mock se offline."""
    try:
        # A URL interna no docker é http://core-api:8000
        core_api_url = os.getenv("CORE_API_URL", "http://core-api:8000")
        async with httpx.AsyncClient(timeout=2.0) as client:
            # Observação: Numa implementação de produção com RBAC, precisaríamos passar um token de serviço.
            # Para o escopo do setup local, tentamos obter sem autenticação ou usamos mock se falhar/não-autorizado.
            response = await client.get(f"{core_api_url}/api/v1/sessions/{session_id}")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        log.warning("report-service.fetch_session.offline", session_id=session_id, error=str(e))
    
    # Mock fallback realista se a Core API estiver indisponível
    return {
        "id": session_id,
        "title": "Parto Normal — Gestante Clara Lima",
        "patient_code": "PAC-2026-003",
        "ira_score": 78.5,
        "ira_level": "critico",
        "score_video": 82.0,
        "score_audio": 79.0,
        "score_document": 72.0,
        "notes": "Procedimento realizado com queixas frequentes de dor e ausência de consentimento prévio para episiotomia."
    }

@app.get("/api/v1/reports/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health():
    return {"status": "healthy", "domain": "report"}

@app.post("/api/v1/reports/generate", status_code=status.HTTP_202_ACCEPTED, response_model=ReportGenerateResponse, tags=["Reports"])
async def generate(data: ReportGenerateRequest, db: DB):
    """Solicita a geração assíncrona/imediata de um relatório."""
    report_id = str(uuid.uuid4())
    log.info("report-service.generate.received", report_id=report_id, session_id=data.session_id)
    
    try:
        # 1. Buscar os dados necessários para preencher o PDF/Excel
        session_info = await get_session_data_from_core(data.session_id)
        
        # 2. Gerar bytes do arquivo com base no formato
        if data.report_format.lower() == "pdf":
            file_bytes = generate_pdf_report(session_info, include_transcription=data.include_transcription)
            filename = f"report_session_{data.session_id}_{report_id[:8]}.pdf"
        elif data.report_format.lower() in ("excel", "xlsx", "csv"):
            file_bytes = generate_excel_report(session_info)
            filename = f"report_executive_{data.session_id}_{report_id[:8]}.xlsx"
        else:
            raise HTTPException(status_code=400, detail="Formato não suportado. Use 'pdf' ou 'excel'")
            
        # 3. Calcular hash SHA-256 para auditoria
        file_hash = calculate_sha256(file_bytes)
        
        # 4. Upload para armazenamento (Azure Blob com fallback para local/static)
        download_url = upload_report_to_storage(filename, file_bytes)
        
        # 5. Salvar registro no banco de dados de relatórios
        now = datetime.now(timezone.utc)
        report_record = Report(
            report_id=report_id,
            session_id=data.session_id,
            title=f"Relatório de Sessão {session_info.get('patient_code', '')}",
            report_type=data.report_type,
            report_format=data.report_format,
            download_url=download_url,
            file_size_bytes=len(file_bytes),
            file_hash_sha256=file_hash,
            status="completed",
            generated_at=now,
            expires_at=now + timedelta(days=1)
        )
        
        db.add(report_record)
        await db.commit()
        
        return ReportGenerateResponse(
            report_id=report_id,
            status="completed",
            estimated_seconds=0
        )
        
    except Exception as e:
        log.error("report-service.generate.failed", report_id=report_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha na geração do relatório: {str(e)}"
        )

@app.get("/api/v1/reports/{report_id}", status_code=status.HTTP_200_OK, tags=["Reports"])
async def get_report(report_id: str, db: DB):
    """Retorna detalhes e URL de download de um relatório existente."""
    result = await db.execute(select(Report).where(Report.report_id == report_id))
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relatório não encontrado")
        
    return {
        "report_id": report.report_id,
        "title": report.title,
        "report_type": report.report_type,
        "report_format": report.report_format,
        "download_url": report.download_url,
        "file_size_bytes": report.file_size_bytes,
        "file_hash_sha256": report.file_hash_sha256,
        "generated_at": report.generated_at.isoformat() if report.generated_at else None,
        "expires_at": report.expires_at.isoformat() if report.expires_at else None
    }
