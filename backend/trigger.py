import asyncio
from app.main import app 
from app.orchestrator.domain_client import DomainClient
from app.database import get_db
from sqlalchemy import select
from app.sessions.models import Session, MediaFile

async def main():
    try:
        db_gen = get_db()
        db = await anext(db_gen)
        
        # Get media for session 20
        res = await db.execute(select(MediaFile).where(MediaFile.session_id == 20, MediaFile.media_type == "audio"))
        audio_media = res.scalars().first()
        
        if audio_media:
            print(f"Reprocessando audio {audio_media.id} da sessao 20...")
            client = DomainClient()
            res = await client.analyze_audio(20, audio_media.id, audio_media.blob_url)
            print("Analyze Audio Response:", res)
            
            # Wait a few seconds for audio-service to process it in background
            print("Aguardando 10 segundos para o audio-service terminar...")
            await asyncio.sleep(10)
            
            # Now trigger the recalculation in core-api
            from app.sessions.service import SessionService
            service = SessionService(db)
            print("Recalculando risco da sessao...")
            await service._recalculate_session_risk(20)
            print("Concluido!")
        else:
            print("Sessao 20 sem audio.")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
