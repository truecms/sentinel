"""
Tests for site module API endpoints.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.site_module import SiteModule
from app.models.site import Site
from app.models.organization import Organization
from app.models.user import User


class TestSiteModulesList:
    """Test GET /api/v1/sites/{id}/modules endpoint."""

    async def test_get_site_modules_success(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_site_module: SiteModule,
        org_user_token_headers: dict
    ):
        """Test successful site modules list retrieval."""
        response = await client.get(
            f"/api/v1/sites/{org_test_site.id}/modules",
            headers=org_user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "pages" in data
        
        assert data["total"] >= 1
        assert len(data["data"]) >= 1
        
        # Check site module structure
        site_module_data = data["data"][0]
        assert "id" in site_module_data
        assert "site_id" in site_module_data
        assert "module_id" in site_module_data
        assert "module" in site_module_data
        assert "current_version" in site_module_data
        assert "enabled" in site_module_data
        assert "update_available" in site_module_data

    async def test_get_site_modules_filter_updates(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_site_module: SiteModule,
        org_user_token_headers: dict
    ):
        """Test filtering site modules by updates available."""
        response = await client.get(
            f"/api/v1/sites/{org_test_site.id}/modules?updates_only=true",
            headers=org_user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # All returned modules should have updates available
        for module in data["data"]:
            assert module["update_available"] is True

    async def test_get_site_modules_filter_security(
        self,
        client: AsyncClient,
        org_test_site: Site,
        test_site_module_with_security: SiteModule,
        org_user_token_headers: dict
    ):
        """Test filtering site modules by security updates."""
        response = await client.get(
            f"/api/v1/sites/{org_test_site.id}/modules?security_only=true",
            headers=org_user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # All returned modules should have security updates available
        for module in data["data"]:
            assert module["security_update_available"] is True

    async def test_get_site_modules_filter_enabled(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_site_module: SiteModule,
        org_user_token_headers: dict
    ):
        """Test filtering site modules by enabled status."""
        response = await client.get(
            f"/api/v1/sites/{org_test_site.id}/modules?enabled_only=false",
            headers=org_user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # Should include both enabled and disabled modules

    async def test_get_site_modules_pagination(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_site_module: SiteModule,
        org_user_token_headers: dict
    ):
        """Test site modules pagination."""
        response = await client.get(
            f"/api/v1/sites/{org_test_site.id}/modules?skip=0&limit=1",
            headers=org_user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["data"]) <= 1
        assert data["page"] == 1
        assert data["per_page"] == 1

    async def test_get_site_modules_not_found(
        self,
        client: AsyncClient,
        org_user_token_headers: dict
    ):
        """Test getting modules for non-existent site."""
        response = await client.get(
            "/api/v1/sites/99999/modules",
            headers=org_user_token_headers
        )
        assert response.status_code == 404

    async def test_get_site_modules_org_permission(
        self,
        client: AsyncClient,
        test_organization_with_users: tuple[Organization, User, User],
        db_session: AsyncSession
    ):
        """Test organization-based access control for site modules."""
        org, org_admin, org_user = test_organization_with_users
        
        # Create a site in a different organization
        other_org = Organization(
            name="Other Org",
            created_by=org_admin.id
        )
        db_session.add(other_org)
        await db_session.commit()
        await db_session.refresh(other_org)
        
        other_site = Site(
            name="Other Site",
            url="https://other.example.com",
            organization_id=other_org.id,
            created_by=org_admin.id,
            updated_by=org_admin.id
        )
        db_session.add(other_site)
        await db_session.commit()
        await db_session.refresh(other_site)
        
        # Create token for user from first org
        from app.core.security import create_access_token
        user_token = create_access_token(data={"sub": org_user.email})
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Should not be able to access other org's site modules
        response = await client.get(
            f"/api/v1/sites/{other_site.id}/modules",
            headers=headers
        )
        assert response.status_code == 403

    async def test_get_site_modules_requires_auth(
        self,
        client: AsyncClient,
        org_test_site: Site
    ):
        """Test that site modules list requires authentication."""
        response = await client.get(f"/api/v1/sites/{org_test_site.id}/modules")
        assert response.status_code == 401


class TestSiteModuleCreate:
    """Test POST /api/v1/sites/{id}/modules endpoint."""

    async def test_add_site_module_success(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_module: Module,
        org_test_module_version: ModuleVersion,
        org_user_token_headers: dict
    ):
        """Test successful site module addition."""
        site_module_data = {
            "site_id": org_test_site.id,
            "module_id": org_test_module.id,
            "current_version_id": org_test_module_version.id,
            "enabled": True
        }
        
        response = await client.post(
            f"/api/v1/sites/{org_test_site.id}/modules",
            json=site_module_data,
            headers=org_user_token_headers
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["site_id"] == site_module_data["site_id"]
        assert data["module_id"] == site_module_data["module_id"]
        assert data["current_version_id"] == site_module_data["current_version_id"]
        assert data["enabled"] == site_module_data["enabled"]
        assert "module" in data
        assert "current_version" in data

    async def test_add_site_module_duplicate(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_site_module: SiteModule,
        org_user_token_headers: dict
    ):
        """Test adding duplicate site module association."""
        site_module_data = {
            "site_id": org_test_site.id,
            "module_id": org_test_site_module.module_id,
            "current_version_id": org_test_site_module.current_version_id,
            "enabled": True
        }
        
        response = await client.post(
            f"/api/v1/sites/{org_test_site.id}/modules",
            json=site_module_data,
            headers=org_user_token_headers
        )
        assert response.status_code == 400
        assert "already associated" in response.json()["detail"]

    async def test_add_site_module_invalid_version(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_module: Module,
        org_test_custom_module: Module,
        org_test_module_version: ModuleVersion,
        org_user_token_headers: dict
    ):
        """Test adding site module with wrong version for module."""
        site_module_data = {
            "site_id": org_test_site.id,
            "module_id": org_test_custom_module.id,  # Different module
            "current_version_id": org_test_module_version.id,  # Version for different module
            "enabled": True
        }
        
        response = await client.post(
            f"/api/v1/sites/{org_test_site.id}/modules",
            json=site_module_data,
            headers=org_user_token_headers
        )
        assert response.status_code == 400
        assert "Invalid version" in response.json()["detail"]

    async def test_add_site_module_site_id_mismatch(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_module: Module,
        org_test_module_version: ModuleVersion,
        org_user_token_headers: dict
    ):
        """Test adding site module with mismatched site ID."""
        site_module_data = {
            "site_id": 99999,  # Different from URL
            "module_id": org_test_module.id,
            "current_version_id": org_test_module_version.id,
            "enabled": True
        }
        
        response = await client.post(
            f"/api/v1/sites/{org_test_site.id}/modules",
            json=site_module_data,
            headers=org_user_token_headers
        )
        assert response.status_code == 400
        assert "Site ID in URL must match" in response.json()["detail"]

    async def test_add_site_module_requires_auth(
        self,
        client: AsyncClient,
        org_test_site: Site
    ):
        """Test that site module addition requires authentication."""
        site_module_data = {
            "site_id": org_test_site.id,
            "module_id": 1,
            "current_version_id": 1,
            "enabled": True
        }
        
        response = await client.post(
            f"/api/v1/sites/{org_test_site.id}/modules",
            json=site_module_data
        )
        assert response.status_code == 401


class TestSiteModuleUpdate:
    """Test PUT /api/v1/sites/{id}/modules/{module_id} endpoint."""

    async def test_update_site_module_success(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_site_module: SiteModule,
        org_test_latest_version: ModuleVersion,
        org_user_token_headers: dict
    ):
        """Test successful site module update."""
        update_data = {
            "enabled": False,
            "current_version_id": org_test_latest_version.id
        }
        
        response = await client.put(
            f"/api/v1/sites/{org_test_site.id}/modules/{org_test_site_module.module_id}",
            json=update_data,
            headers=org_user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["enabled"] == update_data["enabled"]
        assert data["current_version_id"] == update_data["current_version_id"]

    async def test_update_site_module_invalid_version(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_site_module: SiteModule,
        org_test_custom_module: Module,
        db_session: AsyncSession,
        test_organization_with_users: tuple[Organization, User, User],
        org_user_token_headers: dict
    ):
        """Test updating site module with invalid version."""
        org, org_admin, org_user = test_organization_with_users
        
        # Create a version for a different module
        other_version = ModuleVersion(
            module_id=org_test_custom_module.id,
            version_string="1.0.0",
            created_by=org_user.id,
            updated_by=org_user.id
        )
        db_session.add(other_version)
        await db_session.commit()
        await db_session.refresh(other_version)
        
        update_data = {
            "current_version_id": other_version.id
        }
        
        response = await client.put(
            f"/api/v1/sites/{org_test_site.id}/modules/{org_test_site_module.module_id}",
            json=update_data,
            headers=org_user_token_headers
        )
        assert response.status_code == 400
        assert "Invalid version" in response.json()["detail"]

    async def test_update_site_module_not_found(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_user_token_headers: dict
    ):
        """Test updating non-existent site module."""
        update_data = {"enabled": False}
        
        response = await client.put(
            f"/api/v1/sites/{org_test_site.id}/modules/99999",
            json=update_data,
            headers=org_user_token_headers
        )
        assert response.status_code == 404

    async def test_update_site_module_requires_auth(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_site_module: SiteModule
    ):
        """Test that site module update requires authentication."""
        update_data = {"enabled": False}
        
        response = await client.put(
            f"/api/v1/sites/{org_test_site.id}/modules/{org_test_site_module.module_id}",
            json=update_data
        )
        assert response.status_code == 401


class TestSiteModuleDelete:
    """Test DELETE /api/v1/sites/{id}/modules/{module_id} endpoint."""

    async def test_remove_site_module_success(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_site_module: SiteModule,
        org_user_token_headers: dict
    ):
        """Test successful site module removal."""
        response = await client.delete(
            f"/api/v1/sites/{org_test_site.id}/modules/{org_test_site_module.module_id}",
            headers=org_user_token_headers
        )
        assert response.status_code == 204

    async def test_remove_site_module_not_found(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_user_token_headers: dict
    ):
        """Test removing non-existent site module."""
        response = await client.delete(
            f"/api/v1/sites/{org_test_site.id}/modules/99999",
            headers=org_user_token_headers
        )
        assert response.status_code == 404

    async def test_remove_site_module_requires_auth(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_site_module: SiteModule
    ):
        """Test that site module removal requires authentication."""
        response = await client.delete(
            f"/api/v1/sites/{org_test_site.id}/modules/{org_test_site_module.module_id}"
        )
        assert response.status_code == 401


class TestSiteModuleStats:
    """Test GET /api/v1/sites/{id}/modules/stats endpoint."""

    async def test_get_site_module_stats_success(
        self,
        client: AsyncClient,
        org_test_site: Site,
        org_test_site_module: SiteModule,
        org_user_token_headers: dict
    ):
        """Test successful site module statistics retrieval."""
        response = await client.get(
            f"/api/v1/sites/{org_test_site.id}/modules/stats",
            headers=org_user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "total_modules" in data
        assert "enabled_modules" in data
        assert "disabled_modules" in data
        assert "modules_with_updates" in data
        assert "modules_with_security_updates" in data
        assert "contrib_modules" in data
        assert "custom_modules" in data
        assert "core_modules" in data
        
        assert data["total_modules"] >= 1
        assert isinstance(data["enabled_modules"], int)
        assert isinstance(data["disabled_modules"], int)

    async def test_get_site_module_stats_not_found(
        self,
        client: AsyncClient,
        org_user_token_headers: dict
    ):
        """Test getting stats for non-existent site."""
        response = await client.get(
            "/api/v1/sites/99999/modules/stats",
            headers=org_user_token_headers
        )
        assert response.status_code == 404

    async def test_get_site_module_stats_requires_auth(
        self,
        client: AsyncClient,
        org_test_site: Site
    ):
        """Test that site module stats require authentication."""
        response = await client.get(f"/api/v1/sites/{org_test_site.id}/modules/stats")
        assert response.status_code == 401


class TestModuleSites:
    """Test GET /api/v1/modules/{id}/sites endpoint."""

    async def test_get_module_sites_success(
        self,
        client: AsyncClient,
        org_test_module: Module,
        org_test_site_module: SiteModule,
        org_user_token_headers: dict
    ):
        """Test successful module sites list retrieval."""
        response = await client.get(
            f"/api/v1/modules/{org_test_module.id}/sites",
            headers=org_user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check site structure
        site_data = data[0]
        assert "id" in site_data
        assert "name" in site_data
        assert "url" in site_data
        assert "organization_id" in site_data

    async def test_get_module_sites_filter_by_version(
        self,
        client: AsyncClient,
        org_test_module: Module,
        org_test_module_version: ModuleVersion,
        org_test_site_module: SiteModule,
        org_user_token_headers: dict
    ):
        """Test filtering module sites by version."""
        response = await client.get(
            f"/api/v1/modules/{org_test_module.id}/sites?version_id={org_test_module_version.id}",
            headers=org_user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)

    async def test_get_module_sites_pagination(
        self,
        client: AsyncClient,
        org_test_module: Module,
        org_test_site_module: SiteModule,
        org_user_token_headers: dict
    ):
        """Test module sites pagination."""
        response = await client.get(
            f"/api/v1/modules/{org_test_module.id}/sites?skip=0&limit=1",
            headers=org_user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 1

    async def test_get_module_sites_not_found(
        self,
        client: AsyncClient,
        org_user_token_headers: dict
    ):
        """Test getting sites for non-existent module."""
        response = await client.get(
            "/api/v1/modules/99999/sites",
            headers=org_user_token_headers
        )
        assert response.status_code == 404

    async def test_get_module_sites_requires_auth(
        self,
        client: AsyncClient,
        org_test_module: Module
    ):
        """Test that module sites require authentication."""
        response = await client.get(f"/api/v1/modules/{org_test_module.id}/sites")
        assert response.status_code == 401


class TestModuleSiteModules:
    """Test GET /api/v1/modules/{id}/site-modules endpoint."""

    async def test_get_module_site_modules_success(
        self,
        client: AsyncClient,
        org_test_module: Module,
        org_test_site_module: SiteModule,
        org_user_token_headers: dict
    ):
        """Test successful module site-modules list retrieval."""
        response = await client.get(
            f"/api/v1/modules/{org_test_module.id}/site-modules",
            headers=org_user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check site module structure
        site_module_data = data[0]
        assert "id" in site_module_data
        assert "site_id" in site_module_data
        assert "module_id" in site_module_data
        assert "module" in site_module_data
        assert "current_version" in site_module_data
        assert "site_name" in site_module_data
        assert "site_url" in site_module_data

    async def test_get_module_site_modules_requires_auth(
        self,
        client: AsyncClient,
        org_test_module: Module
    ):
        """Test that module site-modules require authentication."""
        response = await client.get(f"/api/v1/modules/{org_test_module.id}/site-modules")
        assert response.status_code == 401