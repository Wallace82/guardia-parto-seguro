"""
GuardIA — Document Domain Service (AWS Integration)
"""
import os
import re
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

    ocr_text_lower = ocr_text.lower()
    
    # 4. Check rule criteria based on actual text
    consent_present = "consentimento" in ocr_text_lower or "autorizado" in ocr_text_lower
    
    # Extract CRM using regex (e.g. CRM-SP 123456)
    crm_match = re.search(r'crm[-\s]?[a-z]{2}\s?\d+', ocr_text_lower)
    professional_crm = crm_match.group(0).upper() if crm_match else None
    
    # Signature is considered present if we found a CRM or the word "assinatura"
    professional_signature = bool(professional_crm) or "assinatura" in ocr_text_lower
    
    # Extract Medical Record (Prontuário) (e.g. Prontuário HC-2024-001)
    record_match = re.search(r'prontu[aá]rio\s*[:\-]?\s*([a-z0-9\-]+)', ocr_text_lower)
    medical_record = record_match.group(1).upper() if record_match else None
    
    # Extract CIDs (e.g. CID O26.8)
    cid_matches = re.findall(r'cid[- 10]*[:\s]*([a-z]\d{2}(?:\.\d)?)', ocr_text_lower)
    diagnosis_cid10 = [cid.upper() for cid in cid_matches]
    
    # Extract diagnoses, procedures, medications
    medications = []
    if "ocitocina" in ocr_text_lower:
        medications.append({"name": "Ocitocina", "dose": "Não extraída", "route": "Não extraída"})
        
    procedures = []
    if "exame obstétrico" in ocr_text_lower or "exame obstetrico" in ocr_text_lower:
        procedures.append("Exame obstétrico")
    if "episiotomia" in ocr_text_lower:
        procedures.append("Episiotomia")
    if "cardiotocografia" in ocr_text_lower:
        procedures.append("Cardiotocografia")

    # Complete extracted fields
    extracted_fields = ExtractedFields(
        patient_name_hash=None, # Cannot reliably extract without NLP
        medical_record=medical_record,
        diagnosis_cid10=diagnosis_cid10,
        procedures=procedures,
        medications=medications,
        professional_signature=professional_signature,
        professional_crm=professional_crm,
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
