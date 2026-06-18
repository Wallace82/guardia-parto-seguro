"""
GuardIA — Audio Domain Service Mock
"""
from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="GuardIA — Audio Service", version="1.0.0")

class AudioAnalyzeRequest(BaseModel):
    session_id: str
    media_id: str
    blob_url: str
    language: Optional[str] = "pt-BR"
    options: Optional[dict] = None

class AudioAnalyzeResponse(BaseModel):
    job_id: str
    status: str

@app.get("/api/v1/audio/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "healthy", "domain": "audio"}

@app.post("/api/v1/audio/analyze", status_code=status.HTTP_202_ACCEPTED, response_model=AudioAnalyzeResponse)
async def analyze(data: AudioAnalyzeRequest):
    return AudioAnalyzeResponse(
        job_id="550e8400-e29b-41d4-a716-446655440021",
        status="queued"
    )

@app.get("/api/v1/audio/results/{session_id}", status_code=status.HTTP_200_OK)
async def results(session_id: str):
    return {
        "session_id": session_id,
        "ira_score": 55.2,
        "transcription": {
            "full_text": "Médico: Vamos fazer o procedimento agora. Paciente: Tá doendo muito, por favor...",
            "language": "pt-BR",
            "duration_seconds": 1823.5,
            "segments": [
                {
                    "speaker": "Speaker_0",
                    "role": "profissional",
                    "start": 0.0,
                    "end": 5.2,
                    "text": "Vamos fazer o procedimento agora.",
                    "sentiment": "neutral",
                    "sentiment_confidence": 0.78
                },
                {
                    "speaker": "Speaker_1",
                    "role": "paciente",
                    "start": 5.8,
                    "end": 10.1,
                    "text": "Tá doendo muito, por favor.",
                    "sentiment": "negative",
                    "sentiment_confidence": 0.94
                }
            ]
        },
        "risk_keywords": [
            {
                "keyword": "tá doendo muito",
                "category": "dor",
                "timestamp_seconds": 5.8,
                "speaker": "Speaker_1",
                "severity": "high"
            }
        ],
        "clinical_entities": [
            {"text": "procedimento", "category": "Procedimento", "confidence": 0.88}
        ]
    }
