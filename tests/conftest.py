import asyncio
import os
from typing import AsyncGenerator, Generator
import time

import pytest
import pytest_asyncio
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

# Test database URL - use test database from environment, fallback to postgres DB
TEST_DATABASE = os.getenv("POSTGRES_DB", "test_db") if os.getenv("TESTING") else "test_db"
TEST_USER = os.getenv("POSTGRES_USER", "test_user") if os.getenv("TESTING") else "test_user"
TEST_PASSWORD = os.getenv("POSTGRES_PASSWORD", "test_password") if os.getenv("TESTING") else "test_password"
TEST_SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{TEST_USER}:{TEST_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{TEST_DATABASE}"

# Create async engine for tests - moved to test_engine fixture to ensure proper URL is used
# Global engine is not needed as we use the fixture

# Create async session factory - will be created in fixtures using test engine
TestingSessionLocal = None  # Defined in fixtures

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
    """Create a test engine and initialize the database with a superuser."""
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
    
    # Create a session to add the superuser
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check if superuser exists
        query = select(User).where(User.email == settings.SUPERUSER_EMAIL)
        result = await session.execute(query)
        superuser = result.scalar_one_or_none()
        
        if not superuser:
            # Create superuser if it doesn't exist
            superuser = User(
                email=settings.SUPERUSER_EMAIL,
                hashed_password=get_password_hash(settings.SUPERUSER_PASSWORD),
                is_active=True,
                is_superuser=True,
                role="superuser"
            )
            session.add(superuser)
            await session.commit()
    
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
        await session.execute(text("DELETE FROM site_modules"))  # Delete site-module associations first
        await session.execute(text("DELETE FROM sites"))
        await session.execute(text("DELETE FROM module_versions"))  # Delete versions before modules
        await session.execute(text("DELETE FROM modules"))  # Delete modules
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

    # Import the main app with all middleware
    from app.main import app as main_app
    main_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=main_app), base_url="http://test", follow_redirects=True) as client:
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

@pytest_asyncio.fixture
async def test_site(db_session: AsyncSession, test_organization: Organization, test_user: User):
    """Create a test site."""
    from app.models.site import Site
    site = Site(
        name="Test Site",
        url="https://test.example.com",
        organization_id=test_organization.id,
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    return site

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

@pytest_asyncio.fixture
async def test_regular_user(db_session: AsyncSession) -> User:
    """Create a regular (non-superuser) test user."""
    user = User(
        email="test_regular_user@example.com",
        hashed_password=get_password_hash("test123"),
        is_active=True,
        is_superuser=False,
        role="user"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def regular_user_token_headers(test_regular_user: User) -> dict:
    """Create authorization headers with regular user JWT token."""
    access_token = create_access_token(
        data={"sub": test_regular_user.email}
    )
    return {"Authorization": f"Bearer {access_token}"}


# Enhanced fixtures for comprehensive test data population (Issue #30)

@pytest_asyncio.fixture
async def sample_drupal_modules() -> list[dict]:
    """Sample module data from a typical Drupal site."""
    from tests.factories.data_factory import create_sample_drupal_modules
    
    # Create a temporary user for generating sample data
    temp_user = User(id=1, email="temp@example.com")
    return await create_sample_drupal_modules(temp_user)


@pytest_asyncio.fixture
async def security_update_modules() -> list[dict]:
    """Modules with security updates available for testing security scenarios."""
    return [
        {
            "machine_name": "views",
            "current_version": "10.2.0",
            "secure_version": "10.3.8",
            "severity": "critical",
            "advisory_id": "SA-CORE-2024-001",
            "description": "Views module security update for critical vulnerability"
        },
        {
            "machine_name": "webform",
            "current_version": "6.2.5",
            "secure_version": "6.2.8",
            "severity": "high",
            "advisory_id": "SA-CONTRIB-2024-015",
            "description": "Webform module security update for high-severity issue"
        },
        {
            "machine_name": "paragraphs",
            "current_version": "1.15.0",
            "secure_version": "1.18.0",
            "severity": "medium",
            "advisory_id": "SA-CONTRIB-2024-023",
            "description": "Paragraphs module security update for medium-severity issue"
        }
    ]


@pytest_asyncio.fixture
async def populated_database(
    db_session: AsyncSession,
    test_organization: Organization,
    test_user: User
) -> dict:
    """
    Database populated with comprehensive test data for integration testing.
    
    Creates:
    - Standard Drupal site with ~25 modules
    - Minimal site with core modules only
    - Security scenarios with vulnerable modules
    - Realistic module relationships and versions
    """
    from tests.factories.data_factory import create_populated_database
    
    return await create_populated_database(db_session, test_organization, test_user)


@pytest_asyncio.fixture
async def standard_drupal_site(
    db_session: AsyncSession,
    test_organization: Organization,
    test_user: User
) -> dict:
    """Create a standard Drupal site with realistic module inventory."""
    from tests.factories.data_factory import TestDataFactory
    
    factory = TestDataFactory(db_session)
    return await factory.create_standard_drupal_site(
        organization=test_organization,
        user=test_user,
        site_name="Standard Test Site",
        site_url="https://standard-test.example.com"
    )


@pytest_asyncio.fixture
async def enterprise_drupal_site(
    db_session: AsyncSession,
    test_organization: Organization,
    test_user: User
) -> dict:
    """Create an enterprise Drupal site with 200+ modules."""
    from tests.factories.data_factory import TestDataFactory
    
    factory = TestDataFactory(db_session)
    return await factory.create_large_enterprise_site(
        organization=test_organization,
        user=test_user,
        site_name="Enterprise Test Site",
        site_url="https://enterprise-test.example.com"
    )


@pytest_asyncio.fixture
async def minimal_drupal_site(
    db_session: AsyncSession,
    test_organization: Organization,
    test_user: User
) -> dict:
    """Create a minimal Drupal site with only core modules."""
    from tests.factories.data_factory import TestDataFactory
    
    factory = TestDataFactory(db_session)
    return await factory.create_minimal_site(
        organization=test_organization,
        user=test_user,
        site_name="Minimal Test Site",
        site_url="https://minimal-test.example.com"
    )


@pytest_asyncio.fixture
async def security_test_data(
    db_session: AsyncSession,
    test_user: User
) -> dict:
    """Create modules with security vulnerabilities and updates for security testing."""
    from tests.factories.data_factory import TestDataFactory
    
    factory = TestDataFactory(db_session)
    return await factory.populate_security_scenarios(test_user)


@pytest_asyncio.fixture
async def bulk_test_data(
    db_session: AsyncSession,
    test_organization: Organization,
    test_user: User
) -> dict:
    """Create bulk test data for performance testing (10 sites with modules)."""
    from tests.factories.data_factory import TestDataFactory
    
    factory = TestDataFactory(db_session)
    return await factory.create_bulk_test_data(
        organization=test_organization,
        user=test_user,
        num_sites=10,
        modules_per_site=50
    )


@pytest_asyncio.fixture 
async def site_with_outdated_modules(
    db_session: AsyncSession,
    test_organization: Organization,
    test_user: User
) -> dict:
    """Create a site with modules that have available updates for update testing."""
    from tests.factories.data_factory import TestDataFactory
    from app.models.site import Site
    from app.models.module import Module
    from app.models.module_version import ModuleVersion
    from app.models.site_module import SiteModule
    from datetime import datetime, timedelta
    
    factory = TestDataFactory(db_session)
    
    # Create site
    site = Site(
        name="Site with Outdated Modules",
        url="https://outdated.example.com",
        organization_id=test_organization.id,
        api_token="outdated_token_123",
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    
    # Create modules with old and new versions
    modules_data = [
        {
            "machine_name": "webform",
            "display_name": "Webform",
            "module_type": "contrib",
            "old_version": "6.2.5",
            "new_version": "6.2.8"
        },
        {
            "machine_name": "paragraphs", 
            "display_name": "Paragraphs",
            "module_type": "contrib",
            "old_version": "1.15.0",
            "new_version": "1.18.0"
        }
    ]
    
    site_modules = []
    for module_data in modules_data:
        # Create module
        module = await factory._get_or_create_module(module_data, test_user)
        
        # Create old version (currently installed)
        old_version = ModuleVersion(
            module_id=module.id,
            version_string=module_data["old_version"],
            release_date=datetime.utcnow() - timedelta(days=120),
            is_security_update=False,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db_session.add(old_version)
        
        # Create new version (available update)
        new_version = ModuleVersion(
            module_id=module.id,
            version_string=module_data["new_version"],
            release_date=datetime.utcnow() - timedelta(days=30),
            is_security_update=False,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db_session.add(new_version)
        
        await db_session.commit()
        await db_session.refresh(old_version)
        await db_session.refresh(new_version)
        
        # Create site-module association with old version
        site_module = SiteModule(
            site_id=site.id,
            module_id=module.id,
            current_version_id=old_version.id,
            enabled=True,
            update_available=True,  # Mark as having update available
            security_update_available=False,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db_session.add(site_module)
        site_modules.append(site_module)
    
    await db_session.commit()
    
    return {
        "site": site,
        "site_modules": site_modules,
        "updates_available": len(modules_data)
    }


@pytest_asyncio.fixture
async def site_with_security_issues(
    db_session: AsyncSession,
    test_organization: Organization,
    test_user: User,
    security_test_data: dict
) -> dict:
    """Create a site with security vulnerabilities for security testing."""
    from app.models.site import Site
    from app.models.site_module import SiteModule
    
    # Create site
    site = Site(
        name="Site with Security Issues",
        url="https://vulnerable.example.com",
        organization_id=test_organization.id,
        api_token="vulnerable_token_123",
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    
    # Associate vulnerable modules with site
    site_modules = []
    for module in security_test_data["security_modules"]:
        # Find the vulnerable version for this module
        vulnerable_version = None
        for version in security_test_data["security_versions"]:
            if version.module_id == module.id and not version.is_security_update:
                vulnerable_version = version
                break
        
        if vulnerable_version:
            site_module = SiteModule(
                site_id=site.id,
                module_id=module.id,
                current_version_id=vulnerable_version.id,
                enabled=True,
                update_available=True,
                security_update_available=True,  # Mark as having security update
                created_by=test_user.id,
                updated_by=test_user.id
            )
            db_session.add(site_module)
            site_modules.append(site_module)
    
    await db_session.commit()
    
    return {
        "site": site,
        "site_modules": site_modules,
        "security_modules": security_test_data["security_modules"],
        "advisory_data": security_test_data["advisory_data"]
    }
