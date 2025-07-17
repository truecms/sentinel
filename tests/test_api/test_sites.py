import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site import Site
from app.models.organization import Organization
from app.models.user import User
from app import crud

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
    assert "id" in data

async def test_create_site_duplicate_url(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test creating site with duplicate URL."""
    # Create initial site using CRUD
    from app.schemas.site import SiteCreate
    site_in = SiteCreate(
        name="Existing Site",
        url="https://existing.example.com",
        organization_id=test_organization.id
    )
    site = await crud.create_site(db_session, site_in, 1)  # Use default user ID

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
    test_user: User,
    db_session: AsyncSession
):
    """Test getting site details."""
    # Assign user to organization using direct SQL to avoid session issues
    from sqlalchemy import update
    from app.models.user import User as UserModel
    
    stmt = update(UserModel).where(UserModel.id == test_user.id).values(organization_id=test_organization.id)
    await db_session.execute(stmt)
    await db_session.commit()
    
    # Create test site using CRUD
    from app.schemas.site import SiteCreate
    site_in = SiteCreate(
        name="Test Site",
        url="https://test.example.com",
        organization_id=test_organization.id
    )
    site = await crud.create_site(db_session, site_in, test_user.id)

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
    test_user: User,
    db_session: AsyncSession
):
    """Test syncing site module information from Drupal."""
    # Assign user to organization using direct SQL to avoid session issues
    from sqlalchemy import update
    from app.models.user import User as UserModel
    
    stmt = update(UserModel).where(UserModel.id == test_user.id).values(organization_id=test_organization.id)
    await db_session.execute(stmt)
    await db_session.commit()
    
    # Create test site using CRUD
    from app.schemas.site import SiteCreate
    site_in = SiteCreate(
        name="Module Test Site",
        url="https://modules.example.com",
        organization_id=test_organization.id
    )
    site = await crud.create_site(db_session, site_in, test_user.id)

    # Sync module information using DrupalSiteSync payload
    response = await client.post(
        f"/api/v1/sites/{site.id}/modules",
        headers=user_token_headers,
        json={
            "site": {
                "url": "https://modules.example.com",
                "name": "Module Test Site",
                "token": "site-auth-token-123"
            },
            "drupal_info": {
                "core_version": "10.3.8",
                "php_version": "8.3.2",
                "ip_address": "192.168.1.100"
            },
            "modules": [
                {
                    "machine_name": "node",
                    "display_name": "Node",
                    "module_type": "core",
                    "enabled": True,
                    "version": "10.3.8"
                },
                {
                    "machine_name": "views",
                    "display_name": "Views",
                    "module_type": "core", 
                    "enabled": True,
                    "version": "10.3.8"
                }
            ]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["modules_processed"] == 2
    assert data["site_id"] == site.id
    assert "message" in data

async def test_get_site_modules(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization,
    test_user: User,
    db_session: AsyncSession
):
    """Test retrieving site module information."""
    # Assign user to organization using direct SQL to avoid session issues
    from sqlalchemy import update
    from app.models.user import User as UserModel
    
    stmt = update(UserModel).where(UserModel.id == test_user.id).values(organization_id=test_organization.id)
    await db_session.execute(stmt)
    await db_session.commit()
    
    # Create test site using CRUD
    from app.schemas.site import SiteCreate
    site_in = SiteCreate(
        name="Module List Site",
        url="https://modulelist.example.com",
        organization_id=test_organization.id
    )
    site = await crud.create_site(db_session, site_in, test_user.id)

    # First sync modules using DrupalSiteSync payload
    await client.post(
        f"/api/v1/sites/{site.id}/modules",
        headers=user_token_headers,
        json={
            "site": {
                "url": "https://modulelist.example.com",
                "name": "Module List Site",
                "token": "site-auth-token-123"
            },
            "drupal_info": {
                "core_version": "10.3.8",
                "php_version": "8.3.2",
                "ip_address": "192.168.1.100"
            },
            "modules": [
                {
                    "machine_name": "node",
                    "display_name": "Node",
                    "module_type": "core",
                    "enabled": True,
                    "version": "10.3.8"
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
    assert "data" in data  # SiteModuleListResponse has a 'data' field
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0
    # Check that module information is present
    module_found = False
    for module in data["data"]:
        if module["module"]["machine_name"] == "node":
            module_found = True
            break
    assert module_found

async def test_delete_site(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    test_user: User,
    db_session: AsyncSession
):
    """Test deleting a site."""
    # Create test site using CRUD
    from app.schemas.site import SiteCreate
    site_in = SiteCreate(
        name="Delete Test Site",
        url="https://delete.example.com",
        organization_id=test_organization.id
    )
    site = await crud.create_site(db_session, site_in, test_user.id)

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
    test_user: User,
    db_session: AsyncSession
):
    """Test getting all sites for an organization."""
    # Assign user to organization using direct SQL to avoid session issues
    from sqlalchemy import update
    from app.models.user import User as UserModel
    
    stmt = update(UserModel).where(UserModel.id == test_user.id).values(organization_id=test_organization.id)
    await db_session.execute(stmt)
    await db_session.commit()
    
    # Create multiple test sites using CRUD
    from app.schemas.site import SiteCreate
    sites = []
    for i in range(3):
        site_in = SiteCreate(
            name=f"Org Site {i}",
            url=f"https://site{i}.example.com",
            organization_id=test_organization.id
        )
        site = await crud.create_site(db_session, site_in, test_user.id)
        sites.append(site)

    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}/sites",
        headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # Could be more if other tests added sites
    assert all(site["organization_id"] == test_organization.id for site in data)
