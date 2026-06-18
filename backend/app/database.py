"""
GuardIA Parto Seguro — Async Database Engine
SQLAlchemy 2.0 com asyncpg para PostgreSQL
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Engine assíncrono — pool de conexões compartilhado pela aplicação
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base declarativa compartilhada por todos os models do core."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency FastAPI: fornece sessão de banco e garante fechamento."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables() -> None:
    """Cria todas as tabelas — usar apenas em desenvolvimento/testes."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
