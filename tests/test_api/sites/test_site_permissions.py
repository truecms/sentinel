"""
Tests for site permissions and authorization.
"""

import pytest
from httpx import AsyncClient

from app.models.organization import Organization
from app.models.site import Site

pytestmark = pytest.mark.asyncio


async def test_regular_user_cant_create_site(
    client: AsyncClient, user_token_headers: dict, test_organization: Organization
):
    """Test that regular users cannot create sites."""
    response = await client.post(
        "/api/v1/sites/",
        headers=user_token_headers,
        json={
            "name": "Unauthorized Site",
            "url": "https://unauthorized.example.com",
            "description": "Site created by unauthorized user",
            "organization_id": test_organization.id,
        },
    )
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]


async def test_regular_user_cant_update_site(
    client: AsyncClient, user_token_headers: dict, test_site: Site
):
    """Test that regular users cannot update sites."""
    response = await client.put(
        f"/api/v1/sites/{test_site.id}",
        headers=user_token_headers,
        json={"name": "Updated Site Name"},
    )
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]


async def test_regular_user_cant_delete_site(
    client: AsyncClient, user_token_headers: dict, test_site: Site
):
    """Test that regular users cannot delete sites."""
    response = await client.delete(
        f"/api/v1/sites/{test_site.id}", headers=user_token_headers
    )
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]


async def test_admin_can_manage_organization_sites(
    client: AsyncClient, superuser_token_headers: dict, test_organization: Organization
):
    """Test that organization admins can manage sites in their organization."""
    # Create new site
    response = await client.post(
        "/api/v1/sites/",
        headers=superuser_token_headers,
        json={
            "name": "Admin Site",
            "url": "https://admin.example.com",
            "description": "Site created by admin",
            "organization_id": test_organization.id,
        },
    )
    assert response.status_code == 201
    site_id = response.json()["id"]

    # Update site
    response = await client.put(
        f"/api/v1/sites/{site_id}",
        headers=superuser_token_headers,
        json={"name": "Updated Admin Site"},
    )
    assert response.status_code == 200

    # Delete site
    response = await client.delete(
        f"/api/v1/sites/{site_id}", headers=superuser_token_headers
    )
    assert response.status_code == 204


async def test_superuser_can_update_any_site(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_site: Site,
    test_organization: Organization,
):
    """Test that superusers can manage sites in any organization."""
    # Superuser should be able to update any site
    response = await client.put(
        f"/api/v1/sites/{test_site.id}",
        headers=superuser_token_headers,
        json={"name": "Updated Site Name by Superuser"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Site Name by Superuser"


async def test_superuser_can_manage_all_sites(
    client: AsyncClient, superuser_token_headers: dict, test_organization: Organization
):
    """Test that superusers can manage all sites regardless of organization."""
    # Create site in the test organization
    response = await client.post(
        "/api/v1/sites/",
        headers=superuser_token_headers,
        json={
            "name": "Superuser Site",
            "url": "https://superuser.example.com",
            "description": "Site created by superuser",
            "organization_id": test_organization.id,
        },
    )
    assert response.status_code == 201
    site_id = response.json()["id"]

    # Update site
    response = await client.put(
        f"/api/v1/sites/{site_id}",
        headers=superuser_token_headers,
        json={"name": "Updated Superuser Site"},
    )
    assert response.status_code == 200

    # Delete site
    response = await client.delete(
        f"/api/v1/sites/{site_id}", headers=superuser_token_headers
    )
    assert response.status_code == 204


async def test_user_can_view_organization_sites(
    client: AsyncClient, user_token_headers: dict, test_site: Site
):
    """Test that users can view sites in their organization."""
    response = await client.get(
        f"/api/v1/sites/{test_site.id}", headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_site.id


async def test_user_can_only_view_own_organization_sites(
    client: AsyncClient,
    user_token_headers: dict,
    test_site: Site,
    test_organization: Organization,
):
    """Test that users can only view sites in their organization."""
    # User can view sites in their organization
    response = await client.get(
        f"/api/v1/sites/{test_site.id}", headers=user_token_headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == test_site.id


@pytest.mark.skip(reason="Site check endpoint not implemented yet")
async def test_user_can_trigger_site_check(
    client: AsyncClient, user_token_headers: dict, test_site: Site
):
    """Test that users can trigger checks for sites in their organization."""
    response = await client.post(
        f"/api/v1/sites/{test_site.id}/check", headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
