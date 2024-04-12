from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from config import settings

async_engine = create_async_engine(url=f'sqlite+aiosqlite:///{settings.db_filename}', echo=True)


async def init_db():
    """Create the database tables"""
    async with async_engine.begin() as conn:
        from .models import Specimen
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db_async_session() -> AsyncSession:
    """Dependency to provide the db session object"""
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
