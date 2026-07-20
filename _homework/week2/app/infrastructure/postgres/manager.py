from contextlib import asynccontextmanager
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.infrastructure.postgres.repositories.event import EventRepository
from app.config import settings


class DatabaseManager:
    def __init__(self) -> None:
        self._engine = create_async_engine(
            settings.postgres.url,
            echo=settings.postgres.echo,
            pool_size=settings.postgres.pool_size,
            max_overflow=settings.postgres.max_overflow,
            pool_pre_ping=settings.postgres.pool_pre_ping,
        )
        self._session_maker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autoflush=False,
        )
    
    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self) -> None:
        await self._engine.dispose()
