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
    ocr_text: Optional[str] = None
    raw_ai_analysis: Optional[dict] = None

class NotesAnalyzeRequest(BaseModel):
    session_id: str
    notes: str

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

    # 4. Análise semântica avançada com OpenAI (Substituindo Regex)
    import openai
    import json
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key or not ocr_text.strip():
        log.warning("openai_fallback", reason="Sem API KEY ou sem texto OCR")
        # Fallback (Regex antigo)
        ocr_text_lower = ocr_text.lower()
        consent_present = "consentimento" in ocr_text_lower or "autorizado" in ocr_text_lower
        crm_match = re.search(r'crm[-\s]?[a-z]{2}\s?\d+', ocr_text_lower)
        professional_crm = crm_match.group(0).upper() if crm_match else None
        professional_signature = bool(professional_crm) or "assinatura" in ocr_text_lower
        record_match = re.search(r'prontu[aá]rio\s*[:\-]?\s*([a-z0-9\-]+)', ocr_text_lower)
        medical_record = record_match.group(1).upper() if record_match else None
        cid_matches = re.findall(r'cid[- 10]*[:\s]*([a-z]\d{2}(?:\.\d)?)', ocr_text_lower)
        diagnosis_cid10 = [cid.upper() for cid in cid_matches]
        medications = [{"name": "Ocitocina", "dose": "Não extraída", "route": "Não extraída"}] if "ocitocina" in ocr_text_lower else []
        procedures = []
        if "exame obstétrico" in ocr_text_lower or "exame obstetrico" in ocr_text_lower: procedures.append("Exame obstétrico")
        if "episiotomia" in ocr_text_lower: procedures.append("Episiotomia")
        if "cardiotocografia" in ocr_text_lower: procedures.append("Cardiotocografia")
        
        extracted_fields = ExtractedFields(
            patient_name_hash=None, medical_record=medical_record, diagnosis_cid10=diagnosis_cid10,
            procedures=procedures, medications=medications, professional_signature=professional_signature,
            professional_crm=professional_crm, attendance_date=None, consent_present=consent_present
        )
        completeness_score = 95.0 if consent_present else 45.0
        ira_score = 15.0 if consent_present else 80.0
        consistency_checks = [
            ConsistencyCheck(check="consent_present", passed=consent_present, severity="none" if consent_present else "high", detail="Termo de consentimento verificado" if consent_present else "Consentimento ausente"),
            ConsistencyCheck(check="professional_signature", passed=professional_signature, severity="none" if professional_signature else "medium", detail="Assinatura e CRM presentes" if professional_signature else "Assinatura ausente")
        ]
    else:
        log.info("running_openai_document_analysis")
        client = openai.OpenAI(api_key=api_key)
        prompt = f"""
Você é um sistema especialista em auditoria médica e obstétrica.
Extraia os dados clínicos do seguinte texto extraído de um prontuário/documento via OCR:

Texto OCR: "{ocr_text}"

Retorne um JSON estritamente neste formato:
{{
  "medical_record": "Número do prontuário (ou null se não houver)",
  "diagnosis_cid10": ["Lista de CIDs (códigos) encontrados"],
  "procedures": ["Lista de procedimentos médicos identificados (escreva o nome correto e padronizado)"],
  "medications": [{{"name": "nome do remédio", "dose": "dose descrita ou 'Não extraída'", "route": "via descrita ou 'Não extraída'"}}],
  "professional_signature": true ou false (se há assinatura explícita, carimbo, ou número de registro médico como CRM),
  "professional_crm": "O CRM extraído com a sigla do estado se houver (ou null)",
  "consent_present": true ou false (se o documento menciona expressamente que o paciente consentiu, autorizou ou concordou com o tratamento/procedimentos)
}}
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" },
                temperature=0.1
            )
            data_json = json.loads(response.choices[0].message.content)
            raw_ai_analysis = data_json
            
            consent_present = bool(data_json.get("consent_present", False))
            professional_signature = bool(data_json.get("professional_signature", False))
            
            extracted_fields = ExtractedFields(
                patient_name_hash=None,
                medical_record=data_json.get("medical_record"),
                diagnosis_cid10=data_json.get("diagnosis_cid10", []),
                procedures=data_json.get("procedures", []),
                medications=data_json.get("medications", []),
                professional_signature=professional_signature,
                professional_crm=data_json.get("professional_crm"),
                attendance_date=None,
                consent_present=consent_present
            )
            
            # Define completeness and risk score (IRA)
            completeness_score = 95.0 if consent_present else 45.0
            ira_score = 15.0 if consent_present else 80.0
            
            consistency_checks = [
                ConsistencyCheck(
                    check="consent_present",
                    passed=consent_present,
                    severity="none" if consent_present else "high",
                    detail="IA: Consentimento informado e explícito identificado no texto" if consent_present else "IA: Sem evidência de consentimento explícito no texto"
                ),
                ConsistencyCheck(
                    check="professional_signature",
                    passed=professional_signature,
                    severity="none" if professional_signature else "medium",
                    detail="IA: Assinatura ou CRM do profissional presentes" if professional_signature else "IA: Assinatura profissional não detectada"
                )
            ]
            log.info("openai_document_analysis_success", ira=ira_score)
        except Exception as oai_err:
            log.error("openai_document_analysis_failed", error=str(oai_err))
            raw_ai_analysis = {"error": str(oai_err)}
            extracted_fields = ExtractedFields(consent_present=False)
            completeness_score = 40.0
            ira_score = 90.0
            consistency_checks = [ConsistencyCheck(check="error", passed=False, severity="high", detail="Falha na análise via IA (OpenAI)")]

    log.info("document.analyze.completed", session_id=data.session_id, ira_score=ira_score, consent=consent_present)

    return DocumentAnalyzeResponse(
        session_id=data.session_id,
        ira_score=ira_score,
        document_type=data.document_type,
        extracted_fields=extracted_fields,
        completeness_score=completeness_score,
        consistency_checks=consistency_checks,
        ocr_text=ocr_text,
        raw_ai_analysis=raw_ai_analysis if 'raw_ai_analysis' in locals() else None
    )

@app.post("/api/v1/documents/analyze-notes", status_code=status.HTTP_200_OK)
async def analyze_notes(data: NotesAnalyzeRequest):
    import openai
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API Key não configurada no document-domain")
        
    try:
        client = openai.OpenAI(api_key=api_key)
        prompt = f"""
Você é um auditor médico especialista. Leia as seguintes anotações clínicas de um atendimento obstétrico.
Forneça uma análise textual humanizada destacando os principais sinais de risco (psicológico, físico) e os fatores que precisam de atenção.
Seja conciso, direto e profissional. Formate o texto usando quebras de linha e tópicos marcados com hífen, sem introduções desnecessárias. Não retorne JSON, apenas o texto da análise.

Anotações Clínicas: "{data.notes}"
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        analysis_text = response.choices[0].message.content
        return {"analysis": analysis_text}
    except Exception as e:
        log.error("openai_notes_analysis_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Erro na OpenAI: {str(e)}")
