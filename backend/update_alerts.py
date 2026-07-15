import asyncio
from app.database import get_db
from sqlalchemy import text

async def main():
    try:
        db_gen = get_db()
        db = await anext(db_gen)
        
        await db.execute(text("UPDATE alerts SET title = REPLACE(title, 'IRA', 'IGA'), description = REPLACE(description, 'IRA', 'IGA');"))
        await db.commit()
        
        print("Alertas atualizados com sucesso.")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
