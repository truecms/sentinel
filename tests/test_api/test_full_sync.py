"""Tests for full sync functionality including removed module detection."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.schemas import ModuleCreate, ModuleVersionCreate, SiteModuleCreate
from app.core.security import create_access_token


@pytest.fixture
async def test_organization_dict(db_session):
    """Create a test organization and return as dict."""
    from app.models.organization import Organization
    
    org = Organization(
        name="Test Organization",
        description="Test organization for full sync tests",
        created_by=1,
        updated_by=1,
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    
    return {
        "id": org.id,
        "name": org.name,
    }


@pytest.fixture
async def test_site_dict(db_session, test_organization_dict):
    """Create a test site and return as dict."""
    from app.models.site import Site
    
    site = Site(
        name="Test Site",
        url="https://test-site.com",
        organization_id=test_organization_dict["id"],
        created_by=1,  # Use hardcoded ID to avoid circular dependency
        updated_by=1,
        is_active=True,
        is_deleted=False,
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    
    return {
        "id": site.id,
        "name": site.name,
        "url": site.url,
        "organization_id": site.organization_id,
    }


@pytest.fixture
async def test_user_dict():
    """Return test user as dict."""
    return {
        "id": 1,
        "email": "test@example.com",
        "is_superuser": True,
        "organization_id": 1,
    }


# Use different names to avoid conflicts with global fixtures
@pytest.fixture
async def test_site(test_site_dict):
    """Alias for test_site_dict."""
    return test_site_dict


@pytest.fixture
async def test_user(test_user_dict):
    """Alias for test_user_dict."""
    return test_user_dict


@pytest.fixture
def user_token_headers(test_user_dict):
    """Create authorization headers for test user."""
    access_token = create_access_token(data={"sub": test_user_dict["email"]})
    return {"Authorization": f"Bearer {access_token}"}


class TestFullSync:
    """Test full sync functionality."""

    @pytest.mark.asyncio
    async def test_full_sync_removes_missing_modules(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        user_token_headers: dict,
        test_site: dict,
        test_user: dict,
    ):
        """Test that full sync removes modules not in the payload."""
        # First, create some existing modules
        module1 = await crud.crud_module.create_module(
            db_session,
            ModuleCreate(
                machine_name="existing_module_1",
                display_name="Existing Module 1",
                module_type="contrib",
            ),
            test_user["id"],
        )

        module2 = await crud.crud_module.create_module(
            db_session,
            ModuleCreate(
                machine_name="existing_module_2",
                display_name="Existing Module 2",
                module_type="contrib",
            ),
            test_user["id"],
        )

        # Create versions for the modules
        version1 = await crud.crud_module_version.create_module_version(
            db_session,
            ModuleVersionCreate(module_id=module1.id, version_string="1.0.0"),
            test_user["id"],
        )

        version2 = await crud.crud_module_version.create_module_version(
            db_session,
            ModuleVersionCreate(module_id=module2.id, version_string="1.0.0"),
            test_user["id"],
        )

        # Associate modules with the site
        await crud.crud_site_module.create_site_module(
            db_session,
            SiteModuleCreate(
                site_id=test_site["id"],
                module_id=module1.id,
                current_version_id=version1.id,
                enabled=True,
            ),
            test_user["id"],
        )

        await crud.crud_site_module.create_site_module(
            db_session,
            SiteModuleCreate(
                site_id=test_site["id"],
                module_id=module2.id,
                current_version_id=version2.id,
                enabled=True,
            ),
            test_user["id"],
        )

        # Verify modules are associated
        modules_before, _ = await crud.crud_site_module.get_site_modules(
            db_session, site_id=test_site["id"]
        )
        assert len(modules_before) == 2

        # Now perform a full sync with only one module
        payload = {
            "site": {
                "url": test_site["url"],
                "name": test_site["name"],
                "token": "test-token",
            },
            "drupal_info": {
                "core_version": "10.3.8",
                "php_version": "8.3.2",
                "ip_address": "192.168.1.100",
            },
            "modules": [
                {
                    "machine_name": "existing_module_1",  # Only include module 1
                    "display_name": "Existing Module 1",
                    "module_type": "contrib",
                    "enabled": True,
                    "version": "1.0.0",
                }
            ],
            "full_sync": True,  # Enable full sync
        }

        response = await client.post(
            f"/api/v1/sites/{test_site['id']}/modules",
            json=payload,
            headers=user_token_headers,
        )

        assert response.status_code == 200

        # Check that module 2 was removed
        modules_after, _ = await crud.crud_site_module.get_site_modules(
            db_session, site_id=test_site["id"]
        )
        assert len(modules_after) == 1
        assert modules_after[0].module.machine_name == "existing_module_1"

        # Verify module 2 is soft deleted
        site_module = await crud.crud_site_module.get_site_module_by_site_and_module(
            db_session, test_site["id"], module2.id
        )
        assert site_module is None  # Should be None because it's soft deleted

    @pytest.mark.asyncio
    async def test_partial_sync_keeps_all_modules(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        user_token_headers: dict,
        test_site: dict,
        test_user: dict,
    ):
        """Test that partial sync (full_sync=False) keeps all existing modules."""
        # Create some existing modules
        module1 = await crud.crud_module.create_module(
            db_session,
            ModuleCreate(
                machine_name="partial_module_1",
                display_name="Partial Module 1",
                module_type="contrib",
            ),
            test_user["id"],
        )

        module2 = await crud.crud_module.create_module(
            db_session,
            ModuleCreate(
                machine_name="partial_module_2",
                display_name="Partial Module 2",
                module_type="contrib",
            ),
            test_user["id"],
        )

        # Create versions
        version1 = await crud.crud_module_version.create_module_version(
            db_session,
            ModuleVersionCreate(module_id=module1.id, version_string="1.0.0"),
            test_user["id"],
        )

        version2 = await crud.crud_module_version.create_module_version(
            db_session,
            ModuleVersionCreate(module_id=module2.id, version_string="1.0.0"),
            test_user["id"],
        )

        # Associate with site
        await crud.crud_site_module.create_site_module(
            db_session,
            SiteModuleCreate(
                site_id=test_site["id"],
                module_id=module1.id,
                current_version_id=version1.id,
                enabled=True,
            ),
            test_user["id"],
        )

        await crud.crud_site_module.create_site_module(
            db_session,
            SiteModuleCreate(
                site_id=test_site["id"],
                module_id=module2.id,
                module_version_id=version2.id,
                enabled=True,
            ),
            test_user["id"],
        )

        # Perform partial sync with only one module
        payload = {
            "site": {
                "url": test_site["url"],
                "name": test_site["name"],
                "token": "test-token",
            },
            "drupal_info": {
                "core_version": "10.3.8",
                "php_version": "8.3.2",
                "ip_address": "192.168.1.100",
            },
            "modules": [
                {
                    "machine_name": "partial_module_1",
                    "display_name": "Partial Module 1",
                    "module_type": "contrib",
                    "enabled": True,
                    "version": "1.0.0",
                }
            ],
            "full_sync": False,  # Partial sync
        }

        response = await client.post(
            f"/api/v1/sites/{test_site['id']}/modules",
            json=payload,
            headers=user_token_headers,
        )

        assert response.status_code == 200

        # Check that both modules are still associated
        modules_after, _ = await crud.crud_site_module.get_site_modules(
            db_session, site_id=test_site["id"]
        )
        assert len(modules_after) == 2
        module_names = {m.module.machine_name for m in modules_after}
        assert "partial_module_1" in module_names
        assert "partial_module_2" in module_names


