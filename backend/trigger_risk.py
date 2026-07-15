import asyncio
from app.database import get_db
from app.sessions.service import SessionService
from app.auth.models import User # Fix relationship error
from sqlalchemy import text

async def main():
    try:
        db_gen = get_db()
        db = await anext(db_gen)
        
        print("Corrigindo banco de dados (backfill anxiety_score)...")
        # Update audio_analysis.anxiety_score from media_files.analysis_score
        query = text("""
            UPDATE audio_analysis
            SET anxiety_score = mf.analysis_score
            FROM media_files mf
            WHERE audio_analysis.session_id = mf.session_id
              AND mf.media_type = 'audio'
              AND mf.analysis_score IS NOT NULL
        """)
        await db.execute(query)
        await db.commit()
        
        service = SessionService(db)
        
        print("Recalculando risco da sessao 19...")
        await service._recalculate_session_risk(19)
        
        print("Recalculando risco da sessao 20...")
        await service._recalculate_session_risk(20)
        
        print("Concluido!")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
