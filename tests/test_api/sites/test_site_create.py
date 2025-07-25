"""
Tests for site creation operations.
"""

import pytest
from httpx import AsyncClient

from app.models.organization import Organization
from app.models.site import Site

pytestmark = pytest.mark.asyncio


async def test_create_site(
    client: AsyncClient, superuser_token_headers: dict, test_organization: Organization
):
    """Test creating a new site."""
    response = await client.post(
        "/api/v1/sites/",
        headers=superuser_token_headers,
        json={
            "name": "New Test Site",
            "url": "https://newtest.example.com",
            "description": "New test site description",
            "organization_id": test_organization.id,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Test Site"
    assert data["url"] == "https://newtest.example.com/"
    assert data["organization_id"] == test_organization.id
    assert data["is_active"] is True
    assert data["is_deleted"] is False


async def test_create_site_invalid_url(
    client: AsyncClient, superuser_token_headers: dict, test_organization: Organization
):
    """Test creating a site with invalid URL."""
    response = await client.post(
        "/api/v1/sites/",
        headers=superuser_token_headers,
        json={
            "name": "Invalid URL Site",
            "url": "not-a-valid-url",
            "description": "Site with invalid URL",
            "organization_id": test_organization.id,
        },
    )
    assert response.status_code == 422  # Validation error


async def test_create_site_duplicate_url(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    test_site: Site,
):
    """Test creating a site with duplicate URL."""
    # First, create a site via the API endpoint
    first_site_response = await client.post(
        "/api/v1/sites/",
        headers=superuser_token_headers,
        json={
            "name": "First Site",
            "url": "https://first.example.com",
            "description": "First site",
            "organization_id": test_organization.id,
        },
    )
    assert first_site_response.status_code == 201
    first_site = first_site_response.json()
    
    # Now test duplicate URL creation
    response = await client.post(
        "/api/v1/sites/",
        headers=superuser_token_headers,
        json={
            "name": "Duplicate URL Site",
            "url": first_site["url"],  # Using the same URL as the first site
            "description": "Site with duplicate URL",
            "organization_id": test_organization.id,
        },
    )
    
    assert response.status_code == 409
    assert "URL already exists" in response.json()["detail"]


async def test_create_site_invalid_organization(
    client: AsyncClient, superuser_token_headers: dict
):
    """Test creating a site with invalid organization ID."""
    response = await client.post(
        "/api/v1/sites/",
        headers=superuser_token_headers,
        json={
            "name": "Invalid Org Site",
            "url": "https://invalid-org.example.com",
            "description": "Site with invalid organization",
            "organization_id": 99999,  # Non-existent organization ID
        },
    )
    assert response.status_code == 404
    assert "Organization not found" in response.json()["detail"]


async def test_create_site_missing_required_fields(
    client: AsyncClient, superuser_token_headers: dict, test_organization: Organization
):
    """Test creating a site with missing required fields."""
    # Missing name
    response = await client.post(
        "/api/v1/sites/",
        headers=superuser_token_headers,
        json={
            "url": "https://noname.example.com",
            "organization_id": test_organization.id,
        },
    )
    assert response.status_code == 422

    # Missing URL
    response = await client.post(
        "/api/v1/sites/",
        headers=superuser_token_headers,
        json={"name": "No URL Site", "organization_id": test_organization.id},
    )
    assert response.status_code == 422


async def test_create_site_with_monitoring_config(
    client: AsyncClient, superuser_token_headers: dict, test_organization: Organization
):
    """Test creating a site with monitoring configuration."""
    response = await client.post(
        "/api/v1/sites/",
        headers=superuser_token_headers,
        json={
            "name": "Monitored Site",
            "url": "https://monitored.example.com",
            "description": "Site with monitoring config",
            "organization_id": test_organization.id,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Monitored Site"
    assert data["url"] == "https://monitored.example.com/"
    assert data["description"] == "Site with monitoring config"
    assert data["organization_id"] == test_organization.id
