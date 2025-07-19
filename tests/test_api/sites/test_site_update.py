"""
Tests for site update operations.
"""

import pytest
from httpx import AsyncClient

from app.models.organization import Organization
from app.models.site import Site

pytestmark = pytest.mark.asyncio


async def test_update_site(
    client: AsyncClient, superuser_token_headers: dict, test_site: Site
):
    """Test updating site details."""
    response = await client.put(
        f"/api/v1/sites/{test_site.id}",
        headers=superuser_token_headers,
        json={"name": "Updated Site Name", "description": "Updated description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Site Name"
    assert data["description"] == "Updated description"
    assert data["url"] == test_site.url + "/"  # URL should remain unchanged (Pydantic adds trailing slash)


async def test_update_site_url(
    client: AsyncClient, superuser_token_headers: dict, test_site: Site
):
    """Test updating site URL."""
    response = await client.put(
        f"/api/v1/sites/{test_site.id}",
        headers=superuser_token_headers,
        json={"url": "https://updated.example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://updated.example.com/"  # Pydantic HttpUrl adds trailing slash


async def test_update_site_invalid_url(
    client: AsyncClient, superuser_token_headers: dict, test_site: Site
):
    """Test updating site with invalid URL."""
    response = await client.put(
        f"/api/v1/sites/{test_site.id}",
        headers=superuser_token_headers,
        json={"url": "not-a-valid-url"},
    )
    assert response.status_code == 422  # Validation error


async def test_update_site_duplicate_url(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_site: Site,
    test_monitored_site: Site,
):
    """Test updating site with duplicate URL."""
    response = await client.put(
        f"/api/v1/sites/{test_site.id}",
        headers=superuser_token_headers,
        json={"url": test_monitored_site.url},  # Using another site's URL
    )
    assert response.status_code == 400
    assert "URL already exists" in response.json()["detail"]


async def test_update_site_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_site: Site,
    test_organization: Organization,
):
    """Test updating site's organization."""
    response = await client.put(
        f"/api/v1/sites/{test_site.id}",
        headers=superuser_token_headers,
        json={"organization_id": test_organization.id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["organization_id"] == test_organization.id


@pytest.mark.skip(reason="Monitoring fields not yet implemented in Site model")
async def test_update_site_monitoring_config(
    client: AsyncClient, superuser_token_headers: dict, test_site: Site
):
    """Test updating site's monitoring configuration."""
    response = await client.put(
        f"/api/v1/sites/{test_site.id}",
        headers=superuser_token_headers,
        json={
            "check_interval": 600,  # 10 minutes
            "timeout": 45,  # 45 seconds
            "expected_status_code": 201,
            "monitor_ssl": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["check_interval"] == 600
    assert data["timeout"] == 45
    assert data["expected_status_code"] == 201
    assert data["monitor_ssl"] is True


async def test_update_site_not_found(
    client: AsyncClient, superuser_token_headers: dict
):
    """Test updating a non-existent site."""
    response = await client.put(
        "/api/v1/sites/99999",  # Non-existent site ID
        headers=superuser_token_headers,
        json={"name": "Non-existent Site"},
    )
    assert response.status_code == 404


async def test_deactivate_site(
    client: AsyncClient, superuser_token_headers: dict, test_site: Site
):
    """Test deactivating a site."""
    response = await client.put(
        f"/api/v1/sites/{test_site.id}",
        headers=superuser_token_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


async def test_update_site_multiple_fields(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_site: Site,
    test_organization: Organization,
):
    """Test updating multiple site fields at once."""
    response = await client.put(
        f"/api/v1/sites/{test_site.id}",
        headers=superuser_token_headers,
        json={
            "name": "Multi Update Site",
            "url": "https://multiupdate.example.com",
            "description": "Updated with multiple fields",
            "organization_id": test_organization.id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Multi Update Site"
    assert data["url"] == "https://multiupdate.example.com/"  # Pydantic HttpUrl adds trailing slash
    assert data["description"] == "Updated with multiple fields"
    assert data["organization_id"] == test_organization.id
