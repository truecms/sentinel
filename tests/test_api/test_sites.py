import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site import Site
from app.models.organization import Organization

pytestmark = pytest.mark.asyncio

async def test_create_site(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization
):
    """Test creating a new site."""
    response = await client.post(
        "/api/v1/sites/",
        headers=user_token_headers,
        json={
            "name": "Test Drupal Site",
            "url": "https://test-drupal.example.com",
            "organization_id": test_organization.id
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Drupal Site"
    assert data["url"] == "https://test-drupal.example.com"
    assert "uuid" in data
    assert "id" in data

async def test_create_site_duplicate_url(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test creating site with duplicate URL."""
    # Create initial site
    site = Site(
        name="Existing Site",
        url="https://existing.example.com",
        organization_id=test_organization.id
    )
    db_session.add(site)
    await db_session.commit()

    # Try to create site with same URL
    response = await client.post(
        "/api/v1/sites/",
        headers=user_token_headers,
        json={
            "name": "Another Site",
            "url": "https://existing.example.com",
            "organization_id": test_organization.id
        }
    )
    assert response.status_code == 409

async def test_get_site(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test getting site details."""
    # Create test site
    site = Site(
        name="Test Site",
        url="https://test.example.com",
        organization_id=test_organization.id
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)

    response = await client.get(
        f"/api/v1/sites/{site.id}",
        headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == site.name
    assert data["url"] == site.url
    assert data["organization_id"] == test_organization.id

async def test_update_site_modules(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test updating site module information."""
    # Create test site
    site = Site(
        name="Module Test Site",
        url="https://modules.example.com",
        organization_id=test_organization.id
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)

    # Update module information
    response = await client.post(
        f"/api/v1/sites/{site.id}/modules",
        headers=user_token_headers,
        json={
            "modules": [
                {
                    "name": "drupal",
                    "version": "9.5.0",
                    "type": "core"
                },
                {
                    "name": "views",
                    "version": "8.x-3.0",
                    "type": "module"
                }
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["modules"]) == 2
    assert any(m["name"] == "drupal" and m["version"] == "9.5.0" for m in data["modules"])

async def test_get_site_modules(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test retrieving site module information."""
    # Create test site with modules
    site = Site(
        name="Module List Site",
        url="https://modulelist.example.com",
        organization_id=test_organization.id
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)

    # First update modules
    await client.post(
        f"/api/v1/sites/{site.id}/modules",
        headers=user_token_headers,
        json={
            "modules": [
                {
                    "name": "drupal",
                    "version": "9.5.0",
                    "type": "core"
                }
            ]
        }
    )

    # Then get modules
    response = await client.get(
        f"/api/v1/sites/{site.id}/modules",
        headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["modules"], list)
    assert len(data["modules"]) > 0
    assert any(m["name"] == "drupal" for m in data["modules"])

async def test_delete_site(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test deleting a site."""
    # Create test site
    site = Site(
        name="Delete Test Site",
        url="https://delete.example.com",
        organization_id=test_organization.id
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)

    response = await client.delete(
        f"/api/v1/sites/{site.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 204

    # Verify site is deleted
    response = await client.get(
        f"/api/v1/sites/{site.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 404

async def test_get_organization_sites(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test getting all sites for an organization."""
    # Create multiple test sites
    sites = [
        Site(
            name=f"Org Site {i}",
            url=f"https://site{i}.example.com",
            organization_id=test_organization.id
        )
        for i in range(3)
    ]
    for site in sites:
        db_session.add(site)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}/sites",
        headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # Could be more if other tests added sites
    assert all(site["organization_id"] == test_organization.id for site in data)
