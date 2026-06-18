"""
GuardIA — Video Domain Service Mock
"""
from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

app = FastAPI(title="GuardIA — Video Service", version="1.0.0")

class VideoAnalyzeRequest(BaseModel):
    session_id: str
    media_id: str
    blob_url: str
    options: Optional[dict] = None

class VideoAnalyzeResponse(BaseModel):
    job_id: str
    status: str
    estimated_duration_seconds: int

@app.get("/api/v1/video/health", status_code=status.HTTP_200_OK)
async def health():
    return {"status": "healthy", "domain": "video"}

@app.post("/api/v1/video/analyze", status_code=status.HTTP_202_ACCEPTED, response_model=VideoAnalyzeResponse)
async def analyze(data: VideoAnalyzeRequest):
    return VideoAnalyzeResponse(
        job_id="550e8400-e29b-41d4-a716-446655440020",
        status="queued",
        estimated_duration_seconds=900
    )

@app.get("/api/v1/video/results/{session_id}", status_code=status.HTTP_200_OK)
async def results(session_id: str):
    return {
        "session_id": session_id,
        "job_id": "550e8400-e29b-41d4-a716-446655440020",
        "status": "completed",
        "ira_score": 68.4,
        "components": {
            "emotion_score": 75.2,
            "pose_score": 60.1,
            "object_risk_score": 45.0,
            "bleeding_score": 0.0
        },
        "total_frames": 54000,
        "analyzed_frames": 1800,
        "key_findings": [
            {
                "type": "emotion",
                "timestamp_seconds": 135.5,
                "description": "Expressão de dor detectada com confiança 0.89",
                "confidence": 0.89
            }
        ],
        "completed_at": datetime.now(timezone.utc).isoformat()
    }
