import asyncio
from app.main import app # This forces all models to load!
from app.sessions.service import process_notes_background
from app.database import get_db
from sqlalchemy import select
from app.sessions.models import Session

async def main():
    try:
        db_gen = get_db()
        db = await anext(db_gen)
        res = await db.execute(select(Session).where(Session.id == 20))
        session = res.scalars().first()
        if session and session.notes:
            print(f"Reprocessando notas da sessao 20...")
            await process_notes_background(20, session.notes)
            print("Concluido!")
        else:
            print("Sessao 20 sem notas.")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
