"""
Tests for module management API endpoints.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module import Module
from app.models.user import User


class TestModulesList:
    """Test GET /api/v1/modules endpoint."""

    async def test_get_modules_success(
        self,
        client: AsyncClient,
        test_module: Module,
        user_token_headers: dict
    ):
        """Test successful module list retrieval."""
        response = await client.get(
            "/api/v1/modules",
            headers=user_token_headers
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
        
        # Check first module structure
        module_data = data["data"][0]
        assert "id" in module_data
        assert "machine_name" in module_data
        assert "display_name" in module_data
        assert "module_type" in module_data
        assert "versions_count" in module_data
        assert "sites_count" in module_data

    async def test_get_modules_pagination(
        self,
        client: AsyncClient,
        multiple_test_modules: list[Module],
        user_token_headers: dict
    ):
        """Test module list pagination."""
        # Test first page
        response = await client.get(
            "/api/v1/modules?skip=0&limit=3",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["data"]) == 3
        assert data["page"] == 1
        assert data["per_page"] == 3
        assert data["total"] >= 8
        
        # Test second page
        response = await client.get(
            "/api/v1/modules?skip=3&limit=3",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["data"]) >= 3
        assert data["page"] == 2

    async def test_get_modules_search(
        self,
        client: AsyncClient,
        multiple_test_modules: list[Module],
        user_token_headers: dict
    ):
        """Test module search functionality."""
        # Search by machine name
        response = await client.get(
            "/api/v1/modules?search=admin_toolbar",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] >= 1
        
        found = False
        for module in data["data"]:
            if "admin_toolbar" in module["machine_name"].lower():
                found = True
                break
        assert found

        # Search by display name
        response = await client.get(
            "/api/v1/modules?search=Chaos",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] >= 1

    async def test_get_modules_filter_by_type(
        self,
        client: AsyncClient,
        multiple_test_modules: list[Module],
        user_token_headers: dict
    ):
        """Test filtering modules by type."""
        # Filter by contrib modules
        response = await client.get(
            "/api/v1/modules?module_type=contrib",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] >= 1
        
        for module in data["data"]:
            assert module["module_type"] == "contrib"

        # Filter by custom modules
        response = await client.get(
            "/api/v1/modules?module_type=custom",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        for module in data["data"]:
            assert module["module_type"] == "custom"

    async def test_get_modules_sorting(
        self,
        client: AsyncClient,
        multiple_test_modules: list[Module],
        user_token_headers: dict
    ):
        """Test module sorting."""
        # Sort by display name ascending
        response = await client.get(
            "/api/v1/modules?sort_by=display_name&sort_order=asc",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        names = [module["display_name"] for module in data["data"]]
        assert names == sorted(names)

        # Sort by machine name descending
        response = await client.get(
            "/api/v1/modules?sort_by=machine_name&sort_order=desc",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        names = [module["machine_name"] for module in data["data"]]
        assert names == sorted(names, reverse=True)

    async def test_get_modules_invalid_filters(
        self,
        client: AsyncClient,
        user_token_headers: dict
    ):
        """Test invalid filter parameters."""
        # Invalid module type
        response = await client.get(
            "/api/v1/modules?module_type=invalid",
            headers=user_token_headers
        )
        assert response.status_code == 422

        # Invalid sort field
        response = await client.get(
            "/api/v1/modules?sort_by=invalid_field",
            headers=user_token_headers
        )
        assert response.status_code == 422

        # Invalid sort order
        response = await client.get(
            "/api/v1/modules?sort_order=invalid",
            headers=user_token_headers
        )
        assert response.status_code == 422

    async def test_get_modules_requires_auth(self, client: AsyncClient):
        """Test that module list requires authentication."""
        response = await client.get("/api/v1/modules")
        assert response.status_code == 401


class TestModuleCreate:
    """Test POST /api/v1/modules endpoint."""

    async def test_create_module_success(
        self,
        client: AsyncClient,
        superuser_token_headers: dict
    ):
        """Test successful module creation."""
        module_data = {
            "machine_name": "new_test_module",
            "display_name": "New Test Module",
            "drupal_org_link": "https://drupal.org/project/new_test_module",
            "module_type": "contrib",
            "description": "A new test module"
        }
        
        response = await client.post(
            "/api/v1/modules",
            json=module_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["machine_name"] == module_data["machine_name"]
        assert data["display_name"] == module_data["display_name"]
        assert data["module_type"] == module_data["module_type"]
        assert data["description"] == module_data["description"]
        assert data["versions_count"] == 0
        assert data["sites_count"] == 0

    async def test_create_module_minimal_data(
        self,
        client: AsyncClient,
        superuser_token_headers: dict
    ):
        """Test module creation with minimal required data."""
        module_data = {
            "machine_name": "minimal_module",
            "display_name": "Minimal Module"
        }
        
        response = await client.post(
            "/api/v1/modules",
            json=module_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 201
        
        data = response.json()
        assert data["machine_name"] == module_data["machine_name"]
        assert data["display_name"] == module_data["display_name"]
        assert data["module_type"] == "contrib"  # Default value

    async def test_create_module_duplicate_machine_name(
        self,
        client: AsyncClient,
        test_module: Module,
        superuser_token_headers: dict
    ):
        """Test creating module with duplicate machine name."""
        module_data = {
            "machine_name": test_module.machine_name,
            "display_name": "Duplicate Module"
        }
        
        response = await client.post(
            "/api/v1/modules",
            json=module_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_create_module_requires_superuser(
        self,
        client: AsyncClient,
        user_token_headers: dict
    ):
        """Test that module creation requires superuser permissions."""
        module_data = {
            "machine_name": "unauthorized_module",
            "display_name": "Unauthorized Module"
        }
        
        response = await client.post(
            "/api/v1/modules",
            json=module_data,
            headers=user_token_headers
        )
        assert response.status_code == 403

    async def test_create_module_validation_errors(
        self,
        client: AsyncClient,
        superuser_token_headers: dict
    ):
        """Test module creation validation errors."""
        # Missing required fields
        response = await client.post(
            "/api/v1/modules",
            json={},
            headers=superuser_token_headers
        )
        assert response.status_code == 422

        # Invalid module type
        module_data = {
            "machine_name": "invalid_type_module",
            "display_name": "Invalid Type",
            "module_type": "invalid"
        }
        response = await client.post(
            "/api/v1/modules",
            json=module_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 422

    async def test_create_module_requires_auth(self, client: AsyncClient):
        """Test that module creation requires authentication."""
        module_data = {
            "machine_name": "no_auth_module",
            "display_name": "No Auth Module"
        }
        
        response = await client.post(
            "/api/v1/modules",
            json=module_data
        )
        assert response.status_code == 401


class TestModuleDetail:
    """Test GET /api/v1/modules/{id} endpoint."""

    async def test_get_module_success(
        self,
        client: AsyncClient,
        test_module: Module,
        user_token_headers: dict
    ):
        """Test successful module detail retrieval."""
        response = await client.get(
            f"/api/v1/modules/{test_module.id}",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == test_module.id
        assert data["machine_name"] == test_module.machine_name
        assert data["display_name"] == test_module.display_name
        assert data["module_type"] == test_module.module_type

    async def test_get_module_not_found(
        self,
        client: AsyncClient,
        user_token_headers: dict
    ):
        """Test module detail for non-existent module."""
        response = await client.get(
            "/api/v1/modules/99999",
            headers=user_token_headers
        )
        assert response.status_code == 404

    async def test_get_module_with_options(
        self,
        client: AsyncClient,
        test_module: Module,
        user_token_headers: dict
    ):
        """Test module detail with include options."""
        response = await client.get(
            f"/api/v1/modules/{test_module.id}?include_versions=true&include_sites=true",
            headers=user_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "versions_count" in data
        assert "sites_count" in data

    async def test_get_module_requires_auth(
        self,
        client: AsyncClient,
        test_module: Module
    ):
        """Test that module detail requires authentication."""
        response = await client.get(f"/api/v1/modules/{test_module.id}")
        assert response.status_code == 401


class TestModuleUpdate:
    """Test PUT /api/v1/modules/{id} endpoint."""

    async def test_update_module_success(
        self,
        client: AsyncClient,
        test_module: Module,
        superuser_token_headers: dict
    ):
        """Test successful module update."""
        update_data = {
            "display_name": "Updated Test Module",
            "description": "Updated description"
        }
        
        response = await client.put(
            f"/api/v1/modules/{test_module.id}",
            json=update_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["display_name"] == update_data["display_name"]
        assert data["description"] == update_data["description"]
        assert data["machine_name"] == test_module.machine_name  # Unchanged

    async def test_update_module_not_found(
        self,
        client: AsyncClient,
        superuser_token_headers: dict
    ):
        """Test updating non-existent module."""
        update_data = {"display_name": "Non-existent"}
        
        response = await client.put(
            "/api/v1/modules/99999",
            json=update_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 404

    async def test_update_module_requires_superuser(
        self,
        client: AsyncClient,
        test_module: Module,
        user_token_headers: dict
    ):
        """Test that module update requires superuser permissions."""
        update_data = {"display_name": "Unauthorized Update"}
        
        response = await client.put(
            f"/api/v1/modules/{test_module.id}",
            json=update_data,
            headers=user_token_headers
        )
        assert response.status_code == 403

    async def test_update_module_requires_auth(
        self,
        client: AsyncClient,
        test_module: Module
    ):
        """Test that module update requires authentication."""
        update_data = {"display_name": "No Auth Update"}
        
        response = await client.put(
            f"/api/v1/modules/{test_module.id}",
            json=update_data
        )
        assert response.status_code == 401


class TestModuleDelete:
    """Test DELETE /api/v1/modules/{id} endpoint."""

    async def test_delete_module_success(
        self,
        client: AsyncClient,
        test_module: Module,
        superuser_token_headers: dict
    ):
        """Test successful module deletion (soft delete)."""
        response = await client.delete(
            f"/api/v1/modules/{test_module.id}",
            headers=superuser_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == test_module.id

    async def test_delete_module_not_found(
        self,
        client: AsyncClient,
        superuser_token_headers: dict
    ):
        """Test deleting non-existent module."""
        response = await client.delete(
            "/api/v1/modules/99999",
            headers=superuser_token_headers
        )
        assert response.status_code == 404

    async def test_delete_module_requires_superuser(
        self,
        client: AsyncClient,
        test_module: Module,
        user_token_headers: dict
    ):
        """Test that module deletion requires superuser permissions."""
        response = await client.delete(
            f"/api/v1/modules/{test_module.id}",
            headers=user_token_headers
        )
        assert response.status_code == 403

    async def test_delete_module_requires_auth(
        self,
        client: AsyncClient,
        test_module: Module
    ):
        """Test that module deletion requires authentication."""
        response = await client.delete(f"/api/v1/modules/{test_module.id}")
        assert response.status_code == 401


class TestModuleBulkOperations:
    """Test POST /api/v1/modules/bulk endpoint."""

    async def test_bulk_create_modules_success(
        self,
        client: AsyncClient,
        superuser_token_headers: dict
    ):
        """Test successful bulk module creation."""
        modules_data = [
            {
                "machine_name": "bulk_module_1",
                "display_name": "Bulk Module 1",
                "module_type": "contrib"
            },
            {
                "machine_name": "bulk_module_2",
                "display_name": "Bulk Module 2",
                "module_type": "custom"
            }
        ]
        
        response = await client.post(
            "/api/v1/modules/bulk",
            json=modules_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["created"] == 2
        assert data["updated"] == 0
        assert data["failed"] == 0
        assert data["total_processed"] == 2

    async def test_bulk_update_modules(
        self,
        client: AsyncClient,
        test_module: Module,
        superuser_token_headers: dict
    ):
        """Test bulk module update."""
        modules_data = [
            {
                "machine_name": test_module.machine_name,
                "display_name": "Updated via Bulk",
                "description": "Updated description"
            }
        ]
        
        response = await client.post(
            "/api/v1/modules/bulk",
            json=modules_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["created"] == 0
        assert data["updated"] == 1
        assert data["failed"] == 0

    async def test_bulk_modules_limit_exceeded(
        self,
        client: AsyncClient,
        superuser_token_headers: dict
    ):
        """Test bulk operation with too many modules."""
        modules_data = [
            {
                "machine_name": f"bulk_module_{i}",
                "display_name": f"Bulk Module {i}"
            }
            for i in range(1001)  # Exceed 1000 limit
        ]
        
        response = await client.post(
            "/api/v1/modules/bulk",
            json=modules_data,
            headers=superuser_token_headers
        )
        assert response.status_code == 400
        assert "1000 modules" in response.json()["detail"]

    async def test_bulk_modules_requires_superuser(
        self,
        client: AsyncClient,
        user_token_headers: dict
    ):
        """Test that bulk operations require superuser permissions."""
        modules_data = [
            {
                "machine_name": "unauthorized_bulk",
                "display_name": "Unauthorized Bulk"
            }
        ]
        
        response = await client.post(
            "/api/v1/modules/bulk",
            json=modules_data,
            headers=user_token_headers
        )
        assert response.status_code == 403

    async def test_bulk_modules_requires_auth(self, client: AsyncClient):
        """Test that bulk operations require authentication."""
        modules_data = [
            {
                "machine_name": "no_auth_bulk",
                "display_name": "No Auth Bulk"
            }
        ]
        
        response = await client.post(
            "/api/v1/modules/bulk",
            json=modules_data
        )
        assert response.status_code == 401