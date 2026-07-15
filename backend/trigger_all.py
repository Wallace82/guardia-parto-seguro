import asyncio
from app.database import get_db
from app.sessions.service import SessionService
from app.auth.models import User # Fix relationship error
from app.sessions.models import Session
from sqlalchemy import select

async def main():
    try:
        db_gen = get_db()
        db = await anext(db_gen)
        
        service = SessionService(db)
        
        # Obter todas as sessões
        result = await db.execute(select(Session.id))
        session_ids = result.scalars().all()
        
        print(f"Encontradas {len(session_ids)} sessoes. Recalculando...")
        for s_id in session_ids:
            try:
                await service._recalculate_session_risk(s_id)
                print(f"Sessao {s_id} recalculada com sucesso.")
            except Exception as e:
                print(f"Erro na sessao {s_id}: {e}")
                
        print("Concluido!")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
