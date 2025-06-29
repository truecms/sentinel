"""
Fixtures specific to module tests.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.site_module import SiteModule
from app.models.site import Site
from app.models.organization import Organization
from app.models.user import User


@pytest.fixture
async def test_module(
    db_session: AsyncSession,
    test_user: User
) -> Module:
    """Create a test module."""
    module = Module(
        machine_name="test_module",
        display_name="Test Module",
        drupal_org_link="https://drupal.org/project/test_module",
        module_type="contrib",
        description="A test module for testing purposes",
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)
    return module


@pytest.fixture
async def test_custom_module(
    db_session: AsyncSession,
    test_user: User
) -> Module:
    """Create a test custom module."""
    module = Module(
        machine_name="custom_test_module",
        display_name="Custom Test Module",
        module_type="custom",
        description="A custom test module",
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)
    return module


@pytest.fixture
async def test_core_module(
    db_session: AsyncSession,
    test_user: User
) -> Module:
    """Create a test core module."""
    module = Module(
        machine_name="system",
        display_name="System",
        module_type="core",
        description="Core system module",
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)
    return module


@pytest.fixture
async def test_module_version(
    db_session: AsyncSession,
    test_module: Module,
    test_user: User
) -> ModuleVersion:
    """Create a test module version."""
    version = ModuleVersion(
        module_id=test_module.id,
        version_string="1.0.0",
        semantic_version="1.0.0",
        release_date=datetime(2024, 1, 1),
        is_security_update=False,
        release_notes_link="https://drupal.org/project/test_module/releases/1.0.0",
        drupal_core_compatibility=["9.x", "10.x"],
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(version)
    await db_session.commit()
    await db_session.refresh(version)
    return version


@pytest.fixture
async def test_security_version(
    db_session: AsyncSession,
    test_module: Module,
    test_user: User
) -> ModuleVersion:
    """Create a test security module version."""
    version = ModuleVersion(
        module_id=test_module.id,
        version_string="1.1.0",
        semantic_version="1.1.0",
        release_date=datetime(2024, 2, 1),
        is_security_update=True,
        release_notes_link="https://drupal.org/project/test_module/releases/1.1.0",
        drupal_core_compatibility=["9.x", "10.x"],
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(version)
    await db_session.commit()
    await db_session.refresh(version)
    return version


@pytest.fixture
async def test_latest_version(
    db_session: AsyncSession,
    test_module: Module,
    test_user: User
) -> ModuleVersion:
    """Create the latest test module version."""
    version = ModuleVersion(
        module_id=test_module.id,
        version_string="2.0.0",
        semantic_version="2.0.0",
        release_date=datetime(2024, 6, 1),
        is_security_update=False,
        release_notes_link="https://drupal.org/project/test_module/releases/2.0.0",
        drupal_core_compatibility=["10.x", "11.x"],
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(version)
    await db_session.commit()
    await db_session.refresh(version)
    return version


@pytest.fixture
async def test_site_module(
    db_session: AsyncSession,
    test_site: Site,
    test_module: Module,
    test_module_version: ModuleVersion,
    test_latest_version: ModuleVersion,
    test_user: User
) -> SiteModule:
    """Create a test site-module association."""
    site_module = SiteModule(
        site_id=test_site.id,
        module_id=test_module.id,
        current_version_id=test_module_version.id,
        latest_version_id=test_latest_version.id,
        enabled=True,
        update_available=True,
        security_update_available=False,
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(site_module)
    await db_session.commit()
    await db_session.refresh(site_module)
    return site_module


@pytest.fixture
async def org_test_site(
    db_session: AsyncSession,
    test_organization_with_users
) -> Site:
    """Create a test site within the organization."""
    org, org_admin, org_user = test_organization_with_users
    
    site = Site(
        name="Org Test Site",
        url="https://orgtest.example.com",
        description="Site for organization testing",
        organization_id=org.id,
        created_by=org_admin.id,
        updated_by=org_admin.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    return site


@pytest.fixture
async def org_test_site_module(
    db_session: AsyncSession,
    org_test_site: Site,
    org_test_module: Module,
    org_test_module_version: ModuleVersion,
    org_test_latest_version: ModuleVersion,
    test_organization_with_users
) -> SiteModule:
    """Create a test site-module association for organization site."""
    org, org_admin, org_user = test_organization_with_users
    
    site_module = SiteModule(
        site_id=org_test_site.id,
        module_id=org_test_module.id,
        current_version_id=org_test_module_version.id,
        latest_version_id=org_test_latest_version.id,
        enabled=True,
        update_available=True,
        security_update_available=False,
        created_by=org_admin.id,
        updated_by=org_admin.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(site_module)
    await db_session.commit()
    await db_session.refresh(site_module)
    return site_module


@pytest.fixture
async def test_site_module_with_security(
    db_session: AsyncSession,
    test_site: Site,
    test_module: Module,
    test_module_version: ModuleVersion,
    test_security_version: ModuleVersion,
    test_user: User
) -> SiteModule:
    """Create a site-module association with security update available."""
    site_module = SiteModule(
        site_id=test_site.id,
        module_id=test_module.id,
        current_version_id=test_module_version.id,
        latest_version_id=test_security_version.id,
        enabled=True,
        update_available=True,
        security_update_available=True,
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(site_module)
    await db_session.commit()
    await db_session.refresh(site_module)
    return site_module


@pytest.fixture
async def test_disabled_module(
    db_session: AsyncSession,
    test_user: User
) -> Module:
    """Create a disabled test module."""
    module = Module(
        machine_name="disabled_module",
        display_name="Disabled Module",
        module_type="contrib",
        description="A disabled test module",
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=False,
        is_deleted=False
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)
    return module


@pytest.fixture
async def test_deleted_module(
    db_session: AsyncSession,
    test_user: User
) -> Module:
    """Create a deleted test module."""
    module = Module(
        machine_name="deleted_module",
        display_name="Deleted Module",
        module_type="contrib",
        description="A deleted test module",
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=True
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)
    return module


@pytest.fixture
async def multiple_test_modules(
    db_session: AsyncSession,
    test_user: User
) -> list[Module]:
    """Create multiple test modules for pagination and filtering tests."""
    modules = []
    
    # Create modules with different types and properties
    module_data = [
        ("admin_toolbar", "Admin Toolbar", "contrib", "Administrative toolbar"),
        ("ctools", "Chaos Tools", "contrib", "Chaos tools suite"),
        ("views", "Views", "core", "Core views module"),
        ("custom_module_1", "Custom Module 1", "custom", "First custom module"),
        ("custom_module_2", "Custom Module 2", "custom", "Second custom module"),
        ("webform", "Webform", "contrib", "Form builder module"),
        ("token", "Token", "contrib", "Token replacement system"),
        ("pathauto", "Pathauto", "contrib", "Automatic path aliases"),
    ]
    
    for i, (machine_name, display_name, module_type, description) in enumerate(module_data):
        module = Module(
            machine_name=machine_name,
            display_name=display_name,
            module_type=module_type,
            description=description,
            created_by=test_user.id,
            updated_by=test_user.id,
            is_active=True,
            is_deleted=False
        )
        db_session.add(module)
        modules.append(module)
    
    await db_session.commit()
    
    # Refresh all modules
    for module in modules:
        await db_session.refresh(module)
    
    return modules


@pytest.fixture
async def test_organization_with_users(
    db_session: AsyncSession,
    test_user: User
) -> tuple[Organization, User, User]:
    """Create organization with admin and regular user."""
    # Create organization
    org = Organization(
        name="Test Org with Users",
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    
    # Create org admin user
    org_admin = User(
        email="org_admin@test.com",
        hashed_password="hashed_password",
        organization_id=org.id,
        role="admin",
        is_active=True,
        is_superuser=False
    )
    db_session.add(org_admin)
    
    # Create org regular user
    org_user = User(
        email="org_user@test.com",
        hashed_password="hashed_password",
        organization_id=org.id,
        role="user",
        is_active=True,
        is_superuser=False
    )
    db_session.add(org_user)
    
    await db_session.commit()
    await db_session.refresh(org_admin)
    await db_session.refresh(org_user)
    
    return org, org_admin, org_user


@pytest.fixture
async def org_user_token_headers(test_organization_with_users) -> dict:
    """Create authorization headers with organization user JWT token."""
    from app.core.security import create_access_token
    
    org, org_admin, org_user = test_organization_with_users
    access_token = create_access_token(
        data={"sub": org_user.email}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def org_test_module(
    db_session: AsyncSession,
    test_organization_with_users
) -> Module:
    """Create a test module within the organization."""
    org, org_admin, org_user = test_organization_with_users
    
    module = Module(
        machine_name="org_test_module",
        display_name="Org Test Module",
        drupal_org_link="https://drupal.org/project/org_test_module",
        module_type="contrib",
        description="A test module for organization testing",
        created_by=org_admin.id,
        updated_by=org_admin.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)
    return module


@pytest.fixture
async def org_test_custom_module(
    db_session: AsyncSession,
    test_organization_with_users
) -> Module:
    """Create a test custom module within the organization."""
    org, org_admin, org_user = test_organization_with_users
    
    module = Module(
        machine_name="org_custom_test_module",
        display_name="Org Custom Test Module",
        module_type="custom",
        description="A custom test module for organization testing",
        created_by=org_admin.id,
        updated_by=org_admin.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)
    return module


@pytest.fixture
async def org_test_module_version(
    db_session: AsyncSession,
    org_test_module: Module,
    test_organization_with_users
) -> ModuleVersion:
    """Create a test module version within the organization."""
    org, org_admin, org_user = test_organization_with_users
    
    version = ModuleVersion(
        module_id=org_test_module.id,
        version_string="1.0.0",
        semantic_version="1.0.0",
        release_date=datetime(2024, 1, 1),
        is_security_update=False,
        release_notes_link="https://drupal.org/project/org_test_module/releases/1.0.0",
        drupal_core_compatibility=["9.x", "10.x"],
        created_by=org_admin.id,
        updated_by=org_admin.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(version)
    await db_session.commit()
    await db_session.refresh(version)
    return version


@pytest.fixture
async def org_test_latest_version(
    db_session: AsyncSession,
    org_test_module: Module,
    test_organization_with_users
) -> ModuleVersion:
    """Create the latest test module version within the organization."""
    org, org_admin, org_user = test_organization_with_users
    
    version = ModuleVersion(
        module_id=org_test_module.id,
        version_string="2.0.0",
        semantic_version="2.0.0",
        release_date=datetime(2024, 6, 1),
        is_security_update=False,
        release_notes_link="https://drupal.org/project/org_test_module/releases/2.0.0",
        drupal_core_compatibility=["10.x", "11.x"],
        created_by=org_admin.id,
        updated_by=org_admin.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(version)
    await db_session.commit()
    await db_session.refresh(version)
    return version