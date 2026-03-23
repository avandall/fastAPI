from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

load_dotenv()

DATABASE_URL = settings.DATABASE_URL or (
    f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}"
    f"@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
)

Base = declarative_base()


def _normalize_async_database_url(database_url: str) -> str:
    url = make_url(database_url)

    if url.drivername == "postgresql":
        return str(url.set(drivername="postgresql+asyncpg"))
    if url.drivername == "sqlite":
        return str(url.set(drivername="sqlite+aiosqlite"))

    return database_url


ASYNC_DATABASE_URL = _normalize_async_database_url(DATABASE_URL)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_engine = create_async_engine(ASYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db
