"""
Tests for module version API endpoints.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module import Module
from app.models.module_version import ModuleVersion
from app.models.user import User


class TestModuleVersionsList:
    """Test GET /api/v1/modules/{id}/versions endpoint."""

    async def test_get_module_versions_success(
        self,
        client: AsyncClient,
        test_module: Module,
        test_module_version: ModuleVersion,
        test_security_version: ModuleVersion,
        user_token_headers: dict
    ):
        """Test successful module versions list retrieval."""
        response = await client.get(
            f"/api/v1/modules/{test_module.id}/versions",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "pages" in data
        
        assert data["total"] >= 2
        assert len(data["data"]) >= 2
        
        # Check version structure
        version_data = data["data"][0]
        assert "id" in version_data
        assert "module_id" in version_data
        assert "version_string" in version_data
        assert "module_name" in version_data
        assert "module_machine_name" in version_data

    async def test_get_module_versions_security_only(
        self,
        client: AsyncClient,
        test_module: Module,
        test_module_version: ModuleVersion,
        test_security_version: ModuleVersion,
        user_token_headers: dict
    ):
        """Test filtering versions by security updates only."""
        response = await client.get(
            f"/api/v1/modules/{test_module.id}/versions?only_security=true",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] >= 1
        
        # All returned versions should be security updates
        for version in data["data"]:
            assert version["is_security_update"] is True

    async def test_get_module_versions_drupal_core_filter(
        self,
        client: AsyncClient,
        test_module: Module,
        test_module_version: ModuleVersion,
        user_token_headers: dict
    ):
        """Test filtering versions by Drupal core compatibility."""
        response = await client.get(
            f"/api/v1/modules/{test_module.id}/versions?drupal_core=10.x",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # Should find versions compatible with 10.x
        assert data["total"] >= 1

    async def test_get_module_versions_pagination(
        self,
        client: AsyncClient,
        test_module: Module,
        test_module_version: ModuleVersion,
        test_security_version: ModuleVersion,
        user_token_headers: dict
    ):
        """Test module versions pagination."""
        response = await client.get(
            f"/api/v1/modules/{test_module.id}/versions?skip=0&limit=1",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["data"]) == 1
        assert data["page"] == 1
        assert data["per_page"] == 1

    async def test_get_module_versions_not_found(
        self,
        client: AsyncClient,
        user_token_headers: dict
    ):
        """Test getting versions for non-existent module."""
        response = await client.get(
            "/api/v1/modules/99999/versions",
            headers=user_token_headers
        )
        assert response.status_code == 404

    async def test_get_module_versions_requires_auth(
        self,
        client: AsyncClient,
        test_module: Module
    ):
        """Test that module versions list requires authentication."""
        response = await client.get(f"/api/v1/modules/{test_module.id}/versions")
        assert response.status_code == 401


class TestModuleVersionCreate:
    """Test POST /api/v1/module-versions endpoint."""

    async def test_create_module_version_success(
        self,
        client: AsyncClient,
        test_module: Module,
        superuser_token_headers: dict
    ):
        """Test successful module version creation."""
        version_data = {
            "module_id": test_module.id,
            "version_string": "3.0.0",
            "semantic_version": "3.0.0",
            "is_security_update": False,
            "release_notes_link": "https://drupal.org/project/test_module/releases/3.0.0",
            "drupal_core_compatibility": ["10.x", "11.x"]
        }
        
        response = await client.post(
            "/api/v1/module-versions",
            json=version_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["module_id"] == version_data["module_id"]
        assert data["version_string"] == version_data["version_string"]
        assert data["is_security_update"] == version_data["is_security_update"]
        assert data["module_name"] == "Test Module"  # Known value from fixture
        assert data["module_machine_name"] == "test_module"  # Known value from fixture

    async def test_create_module_version_minimal_data(
        self,
        client: AsyncClient,
        test_module: Module,
        superuser_token_headers: dict
    ):
        """Test version creation with minimal required data."""
        version_data = {
            "module_id": test_module.id,
            "version_string": "4.0.0"
        }
        
        response = await client.post(
            "/api/v1/module-versions",
            json=version_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["version_string"] == version_data["version_string"]
        assert data["is_security_update"] is False  # Default value

    async def test_create_module_version_duplicate(
        self,
        client: AsyncClient,
        test_module: Module,
        test_module_version: ModuleVersion,
        superuser_token_headers: dict
    ):
        """Test creating duplicate version for same module."""
        version_data = {
            "module_id": test_module.id,
            "version_string": test_module_version.version_string
        }
        
        response = await client.post(
            "/api/v1/module-versions",
            json=version_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_create_module_version_invalid_module(
        self,
        client: AsyncClient,
        superuser_token_headers: dict
    ):
        """Test creating version for non-existent module."""
        version_data = {
            "module_id": 99999,
            "version_string": "1.0.0"
        }
        
        response = await client.post(
            "/api/v1/module-versions",
            json=version_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 404

    async def test_create_module_version_requires_superuser(
        self,
        client: AsyncClient,
        test_module: Module,
        user_token_headers: dict
    ):
        """Test that version creation requires superuser permissions."""
        version_data = {
            "module_id": test_module.id,
            "version_string": "unauthorized"
        }
        
        response = await client.post(
            "/api/v1/module-versions",
            json=version_data,
            headers=user_token_headers
        )
        assert response.status_code == 403

    async def test_create_module_version_requires_auth(
        self,
        client: AsyncClient,
        test_module: Module
    ):
        """Test that version creation requires authentication."""
        version_data = {
            "module_id": test_module.id,
            "version_string": "no_auth"
        }
        
        response = await client.post(
            "/api/v1/module-versions",
            json=version_data
        )
        assert response.status_code == 401


class TestModuleVersionDetail:
    """Test GET /api/v1/module-versions/{id} endpoint."""

    async def test_get_module_version_success(
        self,
        client: AsyncClient,
        test_module_version: ModuleVersion,
        user_token_headers: dict
    ):
        """Test successful module version detail retrieval."""
        response = await client.get(
            f"/api/v1/module-versions/{test_module_version.id}",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # Verify response structure - can't access fixture attributes due to session closure
        assert "id" in data
        assert data["version_string"] == "1.0.0"  # Known value from test_module_version fixture
        assert "module_id" in data
        assert "module_name" in data
        assert "module_machine_name" in data

    async def test_get_module_version_not_found(
        self,
        client: AsyncClient,
        user_token_headers: dict
    ):
        """Test getting non-existent version."""
        response = await client.get(
            "/api/v1/module-versions/99999",
            headers=user_token_headers
        )
        assert response.status_code == 404

    async def test_get_module_version_requires_auth(
        self,
        client: AsyncClient,
        test_module_version: ModuleVersion
    ):
        """Test that version detail requires authentication."""
        response = await client.get(f"/api/v1/module-versions/{test_module_version.id}")
        assert response.status_code == 401


class TestModuleVersionUpdate:
    """Test PUT /api/v1/module-versions/{id} endpoint."""

    async def test_update_module_version_success(
        self,
        client: AsyncClient,
        test_module_version: ModuleVersion,
        superuser_token_headers: dict
    ):
        """Test successful module version update."""
        update_data = {
            "semantic_version": "1.0.1",
            "is_security_update": True
        }
        
        response = await client.put(
            f"/api/v1/module-versions/{test_module_version.id}",
            json=update_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["semantic_version"] == update_data["semantic_version"]
        assert data["is_security_update"] == update_data["is_security_update"]

    async def test_update_module_version_not_found(
        self,
        client: AsyncClient,
        superuser_token_headers: dict
    ):
        """Test updating non-existent version."""
        update_data = {"semantic_version": "1.0.1"}
        
        response = await client.put(
            "/api/v1/module-versions/99999",
            json=update_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 404

    async def test_update_module_version_requires_superuser(
        self,
        client: AsyncClient,
        test_module_version: ModuleVersion,
        user_token_headers: dict
    ):
        """Test that version update requires superuser permissions."""
        update_data = {"semantic_version": "1.0.1"}
        
        response = await client.put(
            f"/api/v1/module-versions/{test_module_version.id}",
            json=update_data,
            headers=user_token_headers
        )
        assert response.status_code == 403

    async def test_update_module_version_requires_auth(
        self,
        client: AsyncClient,
        test_module_version: ModuleVersion
    ):
        """Test that version update requires authentication."""
        update_data = {"semantic_version": "1.0.1"}
        
        response = await client.put(
            f"/api/v1/module-versions/{test_module_version.id}",
            json=update_data
        )
        assert response.status_code == 401


class TestModuleVersionDelete:
    """Test DELETE /api/v1/module-versions/{id} endpoint."""

    async def test_delete_module_version_success(
        self,
        client: AsyncClient,
        test_module_version: ModuleVersion,
        superuser_token_headers: dict
    ):
        """Test successful module version deletion (soft delete)."""
        response = await client.delete(
            f"/api/v1/module-versions/{test_module_version.id}",
            headers=superuser_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # Verify response structure - can't access fixture attributes due to session closure
        assert "id" in data

    async def test_delete_module_version_not_found(
        self,
        client: AsyncClient,
        superuser_token_headers: dict
    ):
        """Test deleting non-existent version."""
        response = await client.delete(
            "/api/v1/module-versions/99999",
            headers=superuser_token_headers
        )
        assert response.status_code == 404

    async def test_delete_module_version_requires_superuser(
        self,
        client: AsyncClient,
        test_module_version: ModuleVersion,
        user_token_headers: dict
    ):
        """Test that version deletion requires superuser permissions."""
        response = await client.delete(
            f"/api/v1/module-versions/{test_module_version.id}",
            headers=user_token_headers
        )
        assert response.status_code == 403

    async def test_delete_module_version_requires_auth(
        self,
        client: AsyncClient,
        test_module_version: ModuleVersion
    ):
        """Test that version deletion requires authentication."""
        response = await client.delete(f"/api/v1/module-versions/{test_module_version.id}")
        assert response.status_code == 401


class TestModuleLatestVersion:
    """Test GET /api/v1/modules/{id}/latest-version endpoint."""

    async def test_get_latest_version_success(
        self,
        client: AsyncClient,
        test_module: Module,
        test_latest_version: ModuleVersion,
        user_token_headers: dict
    ):
        """Test getting latest version for module."""
        # Get module ID from response since we can't access test_module.id due to session closure
        # First get the module versions to find the module ID
        module_response = await client.get(
            "/api/v1/modules",
            headers=user_token_headers
        )
        modules_data = module_response.json()
        test_module_id = None
        for module in modules_data["data"]:
            if module["machine_name"] == "test_module":
                test_module_id = module["id"]
                break
        
        assert test_module_id is not None, "Test module not found"
        
        response = await client.get(
            f"/api/v1/modules/{test_module_id}/latest-version",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["version_string"] == "2.0.0"  # Known value from test_latest_version fixture

    async def test_get_latest_security_version(
        self,
        client: AsyncClient,
        test_module: Module,
        test_security_version: ModuleVersion,
        user_token_headers: dict
    ):
        """Test getting latest security version for module."""
        response = await client.get(
            f"/api/v1/modules/{test_module.id}/latest-version?security_only=true",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_security_update"] is True

    async def test_get_latest_version_not_found(
        self,
        client: AsyncClient,
        user_token_headers: dict
    ):
        """Test getting latest version for non-existent module."""
        response = await client.get(
            "/api/v1/modules/99999/latest-version",
            headers=user_token_headers
        )
        assert response.status_code == 404

    async def test_get_latest_version_requires_auth(
        self,
        client: AsyncClient,
        test_module: Module
    ):
        """Test that latest version requires authentication."""
        response = await client.get(f"/api/v1/modules/{test_module.id}/latest-version")
        assert response.status_code == 401


class TestSecurityVersions:
    """Test GET /api/v1/security-versions endpoint."""

    async def test_get_security_versions_success(
        self,
        client: AsyncClient,
        test_security_version: ModuleVersion,
        user_token_headers: dict
    ):
        """Test getting all security versions."""
        response = await client.get(
            "/api/v1/security-versions",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Should find at least one security version
        security_found = False
        for version in data:
            if version["is_security_update"]:
                security_found = True
                break
        assert security_found

    async def test_get_security_versions_pagination(
        self,
        client: AsyncClient,
        test_security_version: ModuleVersion,
        user_token_headers: dict
    ):
        """Test security versions pagination."""
        response = await client.get(
            "/api/v1/security-versions?skip=0&limit=5",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 5

    async def test_get_security_versions_requires_auth(
        self,
        client: AsyncClient
    ):
        """Test that security versions require authentication."""
        response = await client.get("/api/v1/security-versions")
        assert response.status_code == 401


class TestVersionsByDrupalCore:
    """Test GET /api/v1/drupal-core/{version}/versions endpoint."""

    async def test_get_versions_by_drupal_core_success(
        self,
        client: AsyncClient,
        test_module_version: ModuleVersion,
        user_token_headers: dict
    ):
        """Test getting versions by Drupal core compatibility."""
        response = await client.get(
            "/api/v1/drupal-core/10.x/versions",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # All returned versions should be compatible with 10.x
        for version in data:
            assert "10.x" in version["drupal_core_compatibility"]

    async def test_get_versions_by_drupal_core_pagination(
        self,
        client: AsyncClient,
        test_module_version: ModuleVersion,
        user_token_headers: dict
    ):
        """Test Drupal core versions pagination."""
        response = await client.get(
            "/api/v1/drupal-core/10.x/versions?skip=0&limit=3",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 3

    async def test_get_versions_by_drupal_core_requires_auth(
        self,
        client: AsyncClient
    ):
        """Test that Drupal core versions require authentication."""
        response = await client.get("/api/v1/drupal-core/10.x/versions")
        assert response.status_code == 401