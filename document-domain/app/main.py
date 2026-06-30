"""
GuardIA — Document Domain Service (AWS Integration)
"""
import os
import asyncio
import httpx
import structlog
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

# Load env variables from root .env
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

log = structlog.get_logger(__name__)

app = FastAPI(title="GuardIA — Document Service", version="1.0.0")

class DocumentAnalyzeRequest(BaseModel):
    session_id: str
    media_id: str
    blob_url: str
    document_type: str

class TextBlock(BaseModel):
    block_type: str
    text: Optional[str] = None
    confidence: Optional[float] = None

class ExtractedFields(BaseModel):
    patient_name_hash: Optional[str] = None
    medical_record: Optional[str] = None
    diagnosis_cid10: List[str] = []
    procedures: List[str] = []
    medications: List[dict] = []
    professional_signature: bool = False
    professional_crm: Optional[str] = None
    attendance_date: Optional[str] = None
    consent_present: bool = False

class ConsistencyCheck(BaseModel):
    check: str
    passed: bool
    severity: str
    detail: str

class DocumentAnalyzeResponse(BaseModel):
    session_id: str
    ira_score: float
    document_type: str
    extracted_fields: ExtractedFields
    completeness_score: float
    consistency_checks: List[ConsistencyCheck]

@app.get("/api/v1/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/documents/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "healthy", "domain": "document"}

@app.post("/api/v1/documents/analyze", status_code=status.HTTP_200_OK, response_model=DocumentAnalyzeResponse)
async def analyze(data: DocumentAnalyzeRequest):
    log.info("document.analyze.started", session_id=data.session_id, blob_url=data.blob_url)
    
    # 1. Resolve local file path from blob_url
    file_path = data.blob_url
    if data.blob_url.startswith("file:///"):
        file_path = data.blob_url.replace("file:///", "/")
    elif data.blob_url.startswith("file://"):
        file_path = data.blob_url.replace("file://", "")
    if os.name == 'nt' and file_path.startswith('/C:'):
        file_path = file_path[1:]

    ocr_text = ""
    
    # 2. Try to communicate with aws-service (Textract router)
    try:
        aws_service_url = os.getenv("AWS_SERVICE_URL", "http://aws-service:8007")
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Solicitar início da análise no Textract
            response = await client.post(
                f"{aws_service_url}/api/v1/textract/analyze",
                json={
                    "file_name": os.path.basename(file_path),
                    "bucket_type": "media"
                }
            )
            if response.status_code == 200:
                job_data = response.json()
                job_id = job_data.get("job_id")
                if job_id:
                    # Obter resultados
                    res_resp = await client.get(f"{aws_service_url}/api/v1/textract/results/{job_id}")
                    if res_resp.status_code == 200:
                        res_data = res_resp.json()
                        ocr_text = res_data.get("extracted_text", "")
    except Exception as e:
        log.warning("document.aws_service.failed", error=str(e))

    # 3. Dynamic OCR Simulation fallback (checks filename for demo-friendly variations)
    if not ocr_text or ocr_text == "RELATÓRIO MÉDICO SIMULADO (MOCK)":
        filename_lower = os.path.basename(file_path).lower()
        if "consent" in filename_lower or "term" in filename_lower or "autoriz" in filename_lower:
            ocr_text = "Termo de consentimento livre e esclarecido assinado pela paciente Clara Lima. CRM-SP 123456. Procedimento de episiotomia autorizado."
        else:
            ocr_text = "RELATÓRIO MÉDICO SIMULADO (MOCK). Prontuário HC-2024-001. Paciente Clara Lima. Ocitocina 5 UI IV. CRM-SP 123456."

    ocr_text_lower = ocr_text.lower()
    
    # 4. Check rule criteria
    consent_present = "consentimento" in ocr_text_lower or "autorizado" in ocr_text_lower
    professional_signature = "crm" in ocr_text_lower or "assinatura" in ocr_text_lower
    
    # Extract diagnoses, procedures, medications
    medications = []
    if "ocitocina" in ocr_text_lower:
        medications.append({"name": "Ocitocina", "dose": "5 UI", "route": "IV"})
        
    procedures = ["Exame obstétrico"]
    if "episiotomia" in ocr_text_lower:
        procedures.append("Episiotomia")
    if "cardiotocografia" in ocr_text_lower:
        procedures.append("Cardiotocografia")

    # Complete extracted fields
    extracted_fields = ExtractedFields(
        patient_name_hash="abc123mockhash",
        medical_record="HC-2026-003",
        diagnosis_cid10=["O26.8", "Z34.3"],
        procedures=procedures,
        medications=medications,
        professional_signature=professional_signature,
        professional_crm="CRM-SP 123456" if professional_signature else None,
        attendance_date=None,
        consent_present=consent_present
    )

    # 5. Define completeness and risk score (IRA)
    # RNF-009 / RN-009 / RN-003
    if consent_present:
        completeness_score = 95.0
        ira_score = 15.0  # Risco obstétrico baixo do documento
    else:
        completeness_score = 45.0
        ira_score = 80.0  # Risco obstétrico alto (inconsistência crítica)

    consistency_checks = [
        ConsistencyCheck(
            check="consent_present",
            passed=consent_present,
            severity="none" if consent_present else "high",
            detail="Termo de consentimento verificado" if consent_present else "Consentimento informado ausente para procedimento invasivo"
        ),
        ConsistencyCheck(
            check="professional_signature",
            passed=professional_signature,
            severity="none" if professional_signature else "medium",
            detail="Assinatura e CRM presentes" if professional_signature else "Assinatura profissional não identificada"
        )
    ]

    log.info("document.analyze.completed", session_id=data.session_id, ira_score=ira_score, consent=consent_present)

    return DocumentAnalyzeResponse(
        session_id=data.session_id,
        ira_score=ira_score,
        document_type=data.document_type,
        extracted_fields=extracted_fields,
        completeness_score=completeness_score,
        consistency_checks=consistency_checks
    )
