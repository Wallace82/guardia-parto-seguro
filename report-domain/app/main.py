"""
GuardIA — Report Domain Service Mock
"""
from fastapi import FastAPI, status
from pydantic import BaseModel
from datetime import datetime, timezone

app = FastAPI(title="GuardIA — Report Service", version="1.0.0")

class ReportGenerateRequest(BaseModel):
    session_id: str
    report_type: str
    report_format: str
    include_transcription: bool
    include_key_frames: bool

class ReportGenerateResponse(BaseModel):
    report_id: str
    status: str
    estimated_seconds: int

@app.get("/api/v1/reports/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "healthy", "domain": "report"}

@app.post("/api/v1/reports/generate", status_code=status.HTTP_202_ACCEPTED, response_model=ReportGenerateResponse)
async def generate(data: ReportGenerateRequest):
    return ReportGenerateResponse(
        report_id="550e8400-e29b-41d4-a716-446655440030",
        status="generating",
        estimated_seconds=30
    )

@app.get("/api/v1/reports/{report_id}", status_code=status.HTTP_200_OK)
async def get_report(report_id: str):
    return {
        "report_id": report_id,
        "title": f"Relatório de Sessão — {report_id}",
        "report_type": "session",
        "report_format": "pdf",
        "download_url": "https://storageaccount.blob.core.windows.net/reports/report.pdf?sas=mocked_url",
        "file_size_bytes": 245760,
        "file_hash_sha256": "a1b2c3d4e5f6g7h8",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": datetime.now(timezone.utc).isoformat()
    }
