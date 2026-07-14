from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.sessions.models import Session
from app.sessions.analysis_models import VideoAnalysis, AudioAnalysis, DocumentAnalysis, RiskHistory
from app.sessions.analysis_schemas import (
    VideoAnalysisOut, VideoAnalysisCreate,
    AudioAnalysisOut, AudioAnalysisCreate,
    DocumentAnalysisOut, DocumentAnalysisCreate,
    SessionRiskSummaryOut, RiskSourcesOut
)
from app.risk_engine.fusion_service import RiskFusionEngine

router = APIRouter(tags=["Analysis"])

# =======================
# VIDEO ANALYSIS
# =======================
@router.post("/api/video-analysis", response_model=VideoAnalysisOut, status_code=status.HTTP_201_CREATED)
async def create_video_analysis(
    session_id: int,
    data: VideoAnalysisCreate,
    db: AsyncSession = Depends(get_db)
):
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    analysis = VideoAnalysis(session_id=session_id, **data.model_dump())
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis

@router.get("/api/video-analysis/{analysis_id}", response_model=VideoAnalysisOut)
async def get_video_analysis(analysis_id: int, db: AsyncSession = Depends(get_db)):
    analysis = await db.get(VideoAnalysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


# =======================
# AUDIO ANALYSIS
# =======================
@router.post("/api/audio-analysis", response_model=AudioAnalysisOut, status_code=status.HTTP_201_CREATED)
async def create_audio_analysis(
    session_id: int,
    data: AudioAnalysisCreate,
    db: AsyncSession = Depends(get_db)
):
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    analysis = AudioAnalysis(session_id=session_id, **data.model_dump())
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis

@router.get("/api/audio-analysis/{analysis_id}", response_model=AudioAnalysisOut)
async def get_audio_analysis(analysis_id: int, db: AsyncSession = Depends(get_db)):
    analysis = await db.get(AudioAnalysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


# =======================
# DOCUMENT ANALYSIS
# =======================
@router.post("/api/document-analysis", response_model=DocumentAnalysisOut, status_code=status.HTTP_201_CREATED)
async def create_document_analysis(
    session_id: int,
    data: DocumentAnalysisCreate,
    db: AsyncSession = Depends(get_db)
):
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    analysis = DocumentAnalysis(session_id=session_id, **data.model_dump())
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis

@router.get("/api/document-analysis/{analysis_id}", response_model=DocumentAnalysisOut)
async def get_document_analysis(analysis_id: int, db: AsyncSession = Depends(get_db)):
    analysis = await db.get(DocumentAnalysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


# =======================
# SESSION CONSOLIDATED
# =======================
@router.get("/api/session/{session_id}/risk-summary", response_model=SessionRiskSummaryOut)
async def get_session_risk_summary(session_id: int, db: AsyncSession = Depends(get_db)):
    # Buscar todas as análises vinculadas à sessão
    vid_res = await db.execute(select(VideoAnalysis).where(VideoAnalysis.session_id == session_id))
    videos = vid_res.scalars().all()
    
    aud_res = await db.execute(select(AudioAnalysis).where(AudioAnalysis.session_id == session_id))
    audios = aud_res.scalars().all()
    
    doc_res = await db.execute(select(DocumentAnalysis).where(DocumentAnalysis.session_id == session_id))
    docs = doc_res.scalars().all()
    
    # Calcular
    fusion_result = RiskFusionEngine.calculate_session_risk(videos, audios, docs)
    
    return SessionRiskSummaryOut(
        sessionId=session_id,
        globalScore=fusion_result["globalScore"],
        riskLevel=fusion_result["riskLevel"],
        sources=RiskSourcesOut(**fusion_result["sources"])
    )
