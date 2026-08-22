from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.config import PostgresConfig


class PostgresClient:
    def __init__(self, config: PostgresConfig) -> None:
        self._engine: AsyncEngine = create_async_engine(
            config.url,
            echo=config.echo,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_pre_ping=config.pool_pre_ping,
        )
        self._session_maker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autoflush=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator["DatabaseManager"]:
        async with self._session_maker() as session:
            db = DatabaseManager(session, self._session_maker)
            try:
                yield db
            except Exception:
                await db.rollback()
                raise

    async def close(self) -> None:
        await self._engine.dispose()


class DatabaseManager:
    def __init__(self, session: AsyncSession, session_maker: async_sessionmaker) -> None:
        self.session = session
        self.session_maker = session_maker

    @asynccontextmanager
    async def transaction(self):
        async with self.session_maker() as new_session:
            db_manager = DatabaseManager(new_session, self.session_maker)
            try:
                yield db_manager
                await db_manager.commit()
            except:
                await db_manager.rollback()
                raise

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()