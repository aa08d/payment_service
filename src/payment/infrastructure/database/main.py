from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import orjson
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .config import DBConfig


@asynccontextmanager
async def build_sa_engine(db_config: DBConfig) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(
        db_config.full_url,
        echo=db_config.echo,
        json_serializer=lambda data: orjson.dumps(data).decode(),
        json_deserializer=orjson.loads,
        pool_size=db_config.pool_size,
        pool_pre_ping=True,
    )
    yield engine

    await engine.dispose()


def build_sa_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
