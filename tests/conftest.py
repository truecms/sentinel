import asyncio
import os
from typing import AsyncGenerator, Generator
import time

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text, select

from app.core.config import settings
from app.db.base_class import Base
from app.db.session import get_db
from app.main import app
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.organization import Organization
import itertools
from app.api.v1.api import api_router

# Test database URL
TEST_SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# Create async engine for tests
engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    echo=True,
    future=True
)

# Create async session factory
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
    asyncio.set_event_loop(None)

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create a test engine."""
    engine = create_async_engine(
        TEST_SQLALCHEMY_DATABASE_URL,
        echo=True,
        future=True,
        isolation_level="READ COMMITTED",
        poolclass=NullPool  # Use NullPool to avoid connection reuse
    )
    
    # Create tables at the start of the test session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop tables at the end of the test session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine) -> AsyncSession:
    """Create a clean database session for each test.
    
    This fixture ensures that each test starts with a clean database by:
    1. Creating a new session
    2. Preserving the superuser account
    3. Deleting all other data from tables in the correct order to handle foreign keys
    4. Yielding the session for test use
    5. Rolling back and closing the session after test
    """
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # First, get the superuser email from settings
        superuser_email = settings.SUPERUSER_EMAIL
        
        # Get the superuser's ID to preserve
        query = select(User).where(User.email == superuser_email)
        result = await session.execute(query)
        superuser = result.scalar_one_or_none()
        superuser_id = superuser.id if superuser else None

        # Delete all data from tables in correct order to handle foreign keys
        await session.execute(text("DELETE FROM user_organizations"))
        await session.execute(text("DELETE FROM sites"))
        # First set created_by and updated_by to NULL in organizations
        await session.execute(text("UPDATE organizations SET created_by = NULL, updated_by = NULL"))
        # Delete all users except superuser
        if superuser_id:
            await session.execute(text(f"DELETE FROM users WHERE id != {superuser_id}"))
        else:
            await session.execute(text("DELETE FROM users"))
        await session.execute(text("DELETE FROM organizations"))
        await session.commit()

        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with a clean database session."""
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db_session
        finally:
            await db_session.rollback()

    app = FastAPI(title=settings.PROJECT_NAME)
    app.include_router(api_router, prefix=settings.API_V1_STR)
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_user(request, db_session: AsyncSession) -> User:
    """Create a test user with a unique email."""
    timestamp = int(time.time() * 1000)  # Use milliseconds for more uniqueness
    test_name = request.node.name if request else "default"
    email = f"test_user_{test_name}_{timestamp}@example.com"
    
    user = User(
        email=email,
        hashed_password=get_password_hash("test123"),
        is_active=True,
        role="user"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_superuser(db_session: AsyncSession) -> User:
    """Create a test superuser."""
    user = User(
        email="test_super_user@example.com",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True,
        role="superuser"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_organization(db_session: AsyncSession, test_user: User) -> Organization:
    """Create a test organization."""
    org = Organization(
        name="Test Organization",
        created_by=test_user.id
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org

@pytest.fixture
def user_token_headers(test_user: User) -> dict:
    """Create authorization headers with user JWT token."""
    access_token = create_access_token(
        data={"sub": test_user.email}
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def superuser_token_headers(test_superuser: User) -> dict:
    """Create authorization headers with superuser JWT token."""
    access_token = create_access_token(
        data={"sub": test_superuser.email}
    )
    return {"Authorization": f"Bearer {access_token}"}
