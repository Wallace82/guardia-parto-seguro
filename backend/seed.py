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
        users_to_seed = [
            {"email": "admin@guardia.com", "full_name": "Administrador GuardIA", "role": "admin"},
            {"email": "medico@guardia.com", "full_name": "Dr. João Silva (Profissional)", "role": "profissional"},
            {"email": "gestor@guardia.com", "full_name": "Dra. Maria Helena (Gestora)", "role": "gestor"},
            {"email": "auditor@guardia.com", "full_name": "Auditor Carlos Drummond", "role": "auditor"}
        ]
        
        hashed_pw = pwd_context.hash("Guardia@2026")
        
        for u in users_to_seed:
            result = await session.execute(text("SELECT id FROM users WHERE email = :email"), {"email": u["email"]})
            user = result.fetchone()
            
            if not user:
                query = text("""
                    INSERT INTO users (email, full_name, hashed_password, role, is_active)
                    VALUES (:email, :full_name, :pw, :role, true)
                """)
                await session.execute(query, {
                    "email": u["email"],
                    "full_name": u["full_name"],
                    "role": u["role"],
                    "pw": hashed_pw
                })
                print(f"Usuário '{u['email']}' criado com sucesso com a senha 'Guardia@2026'")
            else:
                print(f"Usuário {u['email']} já existia no banco.")
        
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_admin())
