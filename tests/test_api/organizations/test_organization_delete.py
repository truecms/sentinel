import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_delete_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession,
):
    """Test deleting an organization."""
    org_id = test_organization.id
    response = await client.delete(
        f"/api/v1/organizations/{org_id}", headers=superuser_token_headers
    )
    assert response.status_code == 200

    # Verify organization is deleted
    response = await client.get(
        f"/api/v1/organizations/{org_id}", headers=superuser_token_headers
    )
    assert response.status_code == 404


async def test_delete_organization_regular_user(
    client: AsyncClient, user_token_headers: dict, test_organization: Organization
):
    """Test that regular users cannot delete organizations."""
    org_id = test_organization.id
    response = await client.delete(
        f"/api/v1/organizations/{org_id}", headers=user_token_headers
    )
    assert response.status_code == 403


async def test_delete_organization_not_found(
    client: AsyncClient, superuser_token_headers: dict
):
    """Test deleting non-existent organization."""
    response = await client.delete(
        "/api/v1/organizations/99999", headers=superuser_token_headers
    )
    assert response.status_code == 404


async def test_delete_organization_with_resources(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    test_regular_user: User,
    db_session: AsyncSession,
):
    """Test deleting organization with associated resources."""
    # Add user to organization
    test_regular_user.organization_id = test_organization.id
    db_session.add(test_regular_user)
    await db_session.commit()

    response = await client.delete(
        f"/api/v1/organizations/{test_organization.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200

    # Verify user's organization_id is cleared
    async with async_session_maker() as session:
        user = await session.get(User, test_regular_user.id)
        assert user.organization_id is None


async def test_delete_organization_cleanup(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    test_user: User,
    db_session: AsyncSession,
):
    """Test proper cleanup after organization deletion."""
    # Associate user with organization
    test_user.organization_id = test_organization.id
    db_session.add(test_user)
    await db_session.commit()

    response = await client.delete(
        f"/api/v1/organizations/{test_organization.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200

    # Verify organization is deleted
    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}", headers=superuser_token_headers
    )
    assert response.status_code == 404

    # Verify user's organization association is removed
    async with async_session_maker() as session:
        user = await session.get(User, test_user.id)
        assert user.organization_id is None


async def test_organization_soft_delete(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession,
):
    """Test soft deletion of organization."""
    response = await client.delete(
        f"/api/v1/organizations/{test_organization.id}",
        headers=superuser_token_headers,
        params={"soft_delete": True},
    )
    assert response.status_code == 200

    # Verify organization is marked as deleted but still exists
    async with async_session_maker() as session:
        org = await session.get(Organization, test_organization.id)
        assert org is not None
        assert org.is_deleted == True
