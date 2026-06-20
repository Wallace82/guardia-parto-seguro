import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from passlib.context import CryptContext
from sqlalchemy import text
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_admin():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        # Verifica se já existe um admin
        result = await session.execute(text("SELECT id FROM users WHERE email = 'admin@guardia.com'"))
        user = result.fetchone()
        
        if not user:
            hashed_pw = pwd_context.hash("Guardia@2026")
            query = text("""
                INSERT INTO users (email, full_name, hashed_password, role, is_active)
                VALUES ('admin@guardia.com', 'Administrador GuardIA', :pw, 'admin', true)
            """)
            await session.execute(query, {"pw": hashed_pw})
            await session.commit()
            print("Usuário 'admin@guardia.com' criado com sucesso com a senha 'Guardia@2026'")
        else:
            print("Usuário admin já existia no banco.")

if __name__ == "__main__":
    asyncio.run(seed_admin())
