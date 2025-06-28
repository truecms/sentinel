"""
Tests for site delete operations.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.site import Site
from app.models.organization import Organization

pytestmark = pytest.mark.asyncio

async def test_delete_site(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_site: Site
):
    """Test deleting a site."""
    response = await client.delete(
        f"/api/v1/sites/{test_site.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200

    # Verify site is deleted
    response = await client.get(
        f"/api/v1/sites/{test_site.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 404

async def test_delete_site_not_found(
    client: AsyncClient,
    superuser_token_headers: dict
):
    """Test deleting a non-existent site."""
    response = await client.delete(
        "/api/v1/sites/99999",  # Non-existent site ID
        headers=superuser_token_headers
    )
    assert response.status_code == 404

async def test_delete_site_unauthorized(
    client: AsyncClient,
    user_token_headers: dict,
    test_site: Site
):
    """Test deleting a site without proper permissions."""
    response = await client.delete(
        f"/api/v1/sites/{test_site.id}",
        headers=user_token_headers
    )
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]

async def test_delete_monitored_site(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_monitored_site: Site
):
    """Test deleting a site with monitoring data."""
    response = await client.delete(
        f"/api/v1/sites/{test_monitored_site.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200

    # Verify site and its monitoring data are deleted
    response = await client.get(
        f"/api/v1/sites/{test_monitored_site.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 404

async def test_delete_inactive_site(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_inactive_site: Site
):
    """Test deleting an inactive site."""
    response = await client.delete(
        f"/api/v1/sites/{test_inactive_site.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200

    # Verify site is deleted
    response = await client.get(
        f"/api/v1/sites/{test_inactive_site.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 404

async def test_delete_multiple_sites(
    client: AsyncClient,
    superuser_token_headers: dict,
    db_session: AsyncSession,
    test_organization: Organization
):
    """Test deleting multiple sites."""
    # Create multiple sites
    site_ids = []
    for i in range(3):
        site = Site(
            name=f"Site to Delete {i}",
            url=f"https://todelete{i}.example.com",
            description=f"Site {i} to be deleted",
            organization_id=test_organization.id,
            is_active=True,
            is_deleted=False
        )
        db_session.add(site)
        await db_session.commit()
        await db_session.refresh(site)
        site_ids.append(site.id)

    # Delete each site
    for site_id in site_ids:
        response = await client.delete(
            f"/api/v1/sites/{site_id}",
            headers=superuser_token_headers
        )
        assert response.status_code == 200

    # Verify all sites are deleted
    for site_id in site_ids:
        response = await client.get(
            f"/api/v1/sites/{site_id}",
            headers=superuser_token_headers
        )
        assert response.status_code == 404

async def test_delete_site_cascade(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_monitored_site: Site,
    db_session: AsyncSession
):
    """Test that deleting a site cascades to related monitoring data."""
    # Add some monitoring data
    monitoring_data = MonitoringData(
        site_id=test_monitored_site.id,
        status="up",
        response_time=100,
        check_time="2024-02-23T00:00:00Z"
    )
    db_session.add(monitoring_data)
    await db_session.commit()

    # Delete the site
    response = await client.delete(
        f"/api/v1/sites/{test_monitored_site.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200

    # Verify monitoring data is also deleted
    monitoring_data = await db_session.execute(
        select(MonitoringData).where(MonitoringData.site_id == test_monitored_site.id)
    )
    result = monitoring_data.scalar()
    assert result is None 