"""
Tests for site pagination and filtering.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.site import Site
from app.models.organization import Organization

pytestmark = pytest.mark.asyncio

async def test_get_sites_pagination(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test site list pagination."""
    # Create multiple test sites
    for i in range(15):  # Create enough sites to test pagination
        site = Site(
            name=f"Test Site {i}",
            url=f"https://test{i}.example.com",
            description=f"Test site {i}",
            organization_id=test_organization.id,
            is_active=True,
            is_deleted=False
        )
        db_session.add(site)
    await db_session.commit()

    # Test first page
    response = await client.get(
        "/api/v1/sites/?skip=0&limit=10",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10

    # Test second page
    response = await client.get(
        "/api/v1/sites/?skip=10&limit=10",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert len(data) <= 10

async def test_get_sites_filter_active(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test filtering sites by active status."""
    # Create active and inactive sites
    active_site = Site(
        name="Active Site",
        url="https://active.example.com",
        description="Active test site",
        organization_id=test_organization.id,
        is_active=True,
        is_deleted=False
    )
    inactive_site = Site(
        name="Inactive Site",
        url="https://inactive.example.com",
        description="Inactive test site",
        organization_id=test_organization.id,
        is_active=False,
        is_deleted=False
    )
    db_session.add(active_site)
    db_session.add(inactive_site)
    await db_session.commit()

    # Test filtering active sites
    response = await client.get(
        "/api/v1/sites/?is_active=true",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(site["is_active"] for site in data)

    # Test filtering inactive sites
    response = await client.get(
        "/api/v1/sites/?is_active=false",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(not site["is_active"] for site in data)

async def test_get_sites_filter_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test filtering sites by organization."""
    # Create sites in different organizations
    for i in range(2):
        site = Site(
            name=f"Org Site {i}",
            url=f"https://org{i}.example.com",
            description=f"Organization site {i}",
            organization_id=test_organization.id + i,
            is_active=True,
            is_deleted=False
        )
        db_session.add(site)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/sites/?organization_id={test_organization.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(site["organization_id"] == test_organization.id for site in data)

async def test_get_sites_search(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test searching sites by name or URL."""
    # Create sites with specific names and URLs
    search_site = Site(
        name="Searchable Site",
        url="https://searchable.example.com",
        description="Site for search testing",
        organization_id=test_organization.id,
        is_active=True,
        is_deleted=False
    )
    other_site = Site(
        name="Other Site",
        url="https://other.example.com",
        description="Another site",
        organization_id=test_organization.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(search_site)
    db_session.add(other_site)
    await db_session.commit()

    # Test searching by name
    response = await client.get(
        "/api/v1/sites/?search=Searchable",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any("Searchable" in site["name"] for site in data)

    # Test searching by URL
    response = await client.get(
        "/api/v1/sites/?search=searchable.example",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any("searchable.example" in site["url"] for site in data)

async def test_get_sites_combined_filters(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test combining multiple filters."""
    # Create various sites
    site1 = Site(
        name="Active Org Site",
        url="https://active-org.example.com",
        description="Active site in organization",
        organization_id=test_organization.id,
        is_active=True,
        is_deleted=False
    )
    site2 = Site(
        name="Inactive Org Site",
        url="https://inactive-org.example.com",
        description="Inactive site in organization",
        organization_id=test_organization.id,
        is_active=False,
        is_deleted=False
    )
    db_session.add(site1)
    db_session.add(site2)
    await db_session.commit()

    # Test combining organization and active status filters
    response = await client.get(
        f"/api/v1/sites/?organization_id={test_organization.id}&is_active=true",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(site["organization_id"] == test_organization.id and site["is_active"] for site in data)

async def test_get_sites_sort(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test sorting sites by various fields."""
    # Create sites with different names and creation times
    sites = [
        Site(
            name="Site A",
            url="https://a.example.com",
            description="Site A description",
            organization_id=test_organization.id,
            is_active=True,
            is_deleted=False
        ),
        Site(
            name="Site B",
            url="https://b.example.com",
            description="Site B description",
            organization_id=test_organization.id,
            is_active=True,
            is_deleted=False
        )
    ]
    for site in sites:
        db_session.add(site)
    await db_session.commit()

    # Test sorting by name ascending
    response = await client.get(
        "/api/v1/sites/?sort=name",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    names = [site["name"] for site in data]
    assert names == sorted(names)

    # Test sorting by name descending
    response = await client.get(
        "/api/v1/sites/?sort=-name",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    names = [site["name"] for site in data]
    assert names == sorted(names, reverse=True) 