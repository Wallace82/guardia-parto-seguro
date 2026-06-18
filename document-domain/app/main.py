"""
GuardIA — Document Domain Service Mock
"""
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI(title="GuardIA — Document Service", version="1.0.0")

class DocumentAnalyzeRequest(BaseModel):
    session_id: str
    media_id: str
    blob_url: str
    document_type: str

@app.get("/api/v1/documents/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "healthy", "domain": "document"}

@app.post("/api/v1/documents/analyze", status_code=status.HTTP_200_OK)
async def analyze(data: DocumentAnalyzeRequest):
    return {
        "session_id": data.session_id,
        "ira_score": 35.0,
        "document_type": data.document_type,
        "extracted_fields": {
            "patient_name_hash": "abc123...",
            "medical_record": "HC-2024-001",
            "diagnosis_cid10": ["O26.8", "Z34.3"],
            "procedures": ["Exame obstétrico", "Cardiotocografia"],
            "medications": [
                {"name": "Ocitocina", "dose": "5 UI", "route": "IV"}
            ],
            "professional_signature": True,
            "professional_crm": "CRM-SP 123456",
            "attendance_date": "2024-01-15",
            "consent_present": False
        },
        "completeness_score": 78.5,
        "consistency_checks": [
            {
                "check": "consent_present",
                "passed": False,
                "severity": "high",
                "detail": "Consentimento informado ausente para procedimento invasivo"
            },
            {
                "check": "professional_signature",
                "passed": True,
                "severity": "none",
                "detail": "Assinatura e CRM presentes"
            }
        ]
    }
