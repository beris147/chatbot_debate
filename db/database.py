from contextlib import asynccontextmanager
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./chat.db"

engine = create_async_engine(DATABASE_URL, connect_args={
                             "check_same_thread": False})
SessionLocal = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


@asynccontextmanager
async def db_lifespan():
    if not os.getenv("TESTING"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield
    await engine.dispose()
    print("Database connections closed")


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
