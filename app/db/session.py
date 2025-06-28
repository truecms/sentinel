from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Create async engine with connection pooling disabled
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=True,
    future=True,
    poolclass=NullPool  # Disable connection pooling
)

# Configure session with autocommit=False (the default)
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()  # Commit the transaction if no exceptions occurred
        except Exception:
            await session.rollback()  # Rollback in case of exceptions
            raise
        finally:
            await session.close()
