"""
Tests for site read operations.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.site import Site

pytestmark = pytest.mark.asyncio


async def test_get_sites(
    client: AsyncClient, superuser_token_headers: dict, test_site: Site
):
    """Test getting list of sites."""
    response = await client.get("/api/v1/sites/", headers=superuser_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Debug output
    print(f"DEBUG: test_site.url = {test_site.url}")
    print(f"DEBUG: response data length = {len(data)}")
    if data:
        print(f"DEBUG: first site = {data[0]}")
        for site in data:
            print(f"DEBUG: site url = {site.get('url')}")
    
    assert len(data) > 0
    assert any(site["url"] == test_site.url + "/" for site in data)


async def test_get_site(
    client: AsyncClient, superuser_token_headers: dict, test_site: Site
):
    """Test getting site details."""
    response = await client.get(
        f"/api/v1/sites/{test_site.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_site.name
    assert data["url"] == test_site.url + "/"  # Pydantic HttpUrl adds trailing slash
    assert data["organization_id"] == test_site.organization_id


async def test_get_nonexistent_site(client: AsyncClient, superuser_token_headers: dict):
    """Test getting a non-existent site."""
    response = await client.get(
        "/api/v1/sites/99999", headers=superuser_token_headers  # Non-existent site ID
    )
    assert response.status_code == 404


async def test_get_organization_sites(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession,
):
    """Test getting all sites in an organization."""
    # Create additional sites in the organization
    for i in range(2):
        site = Site(
            name=f"Org Site {i}",
            url=f"https://orgsite{i}.example.com",
            description=f"Organization site {i}",
            organization_id=test_organization.id,
            is_active=True,
            is_deleted=False,
        )
        db_session.add(site)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}/sites",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


async def test_get_organization_sites_not_found(
    client: AsyncClient, superuser_token_headers: dict
):
    """Test getting sites from non-existent organization."""
    response = await client.get(
        "/api/v1/organizations/99999/sites",  # Non-existent organization ID
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


async def test_get_organization_sites_empty(
    client: AsyncClient, superuser_token_headers: dict, test_organization: Organization
):
    """Test getting sites from an empty organization."""
    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}/sites",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.skip(reason="Monitoring fields not implemented in Site model yet")
async def test_get_site_with_monitoring_data(
    client: AsyncClient, superuser_token_headers: dict, test_monitored_site: Site
):
    """Test getting site details including monitoring data."""
    response = await client.get(
        f"/api/v1/sites/{test_monitored_site.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_monitored_site.name
    assert data["url"] == test_monitored_site.url + "/"  # Pydantic HttpUrl adds trailing slash
    assert "last_check_time" in data
    assert "status" in data
    assert "response_time" in data
    assert "ssl_expiry" in data


@pytest.mark.skip(reason="test_inactive_site fixture not implemented yet")
async def test_get_inactive_site(
    client: AsyncClient, superuser_token_headers: dict, test_inactive_site: Site
):
    """Test getting an inactive site."""
    response = await client.get(
        f"/api/v1/sites/{test_inactive_site.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_inactive_site.name
    assert data["is_active"] is False


@pytest.mark.skip(reason="test_deleted_site fixture not implemented yet")
async def test_get_deleted_site(
    client: AsyncClient, superuser_token_headers: dict, test_deleted_site: Site
):
    """Test getting a deleted site."""
    response = await client.get(
        f"/api/v1/sites/{test_deleted_site.id}", headers=superuser_token_headers
    )
    assert response.status_code == 404  # Deleted sites should not be accessible
