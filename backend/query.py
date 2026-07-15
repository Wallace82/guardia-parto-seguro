import asyncio
from sqlalchemy import select
from app.database import get_db
from app.sessions.analysis_models import DocumentAnalysis

async def main():
    try:
        db_gen = get_db()
        db = await anext(db_gen)
        res = await db.execute(select(DocumentAnalysis).where(DocumentAnalysis.session_id==20, DocumentAnalysis.tipo_documento=='anotacoes'))
        doc = res.scalars().first()
        import json
        print(json.dumps(doc.fatores_identificados, indent=2) if doc else 'No doc')
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
