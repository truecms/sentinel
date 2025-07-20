"""Test that superusers can access organization users."""
import pytest
from httpx import AsyncClient

from app.models.organization import Organization


@pytest.mark.asyncio
async def test_superuser_can_view_organization_users(
    client: AsyncClient,
    test_organization: Organization,
    superuser_token_headers: dict,
):
    """Test that superusers can view organization users."""
    response = await client.get(
        f"/api/v1/users/organization/{test_organization.id}/users",
        headers=superuser_token_headers,
    )
    
    # Superusers should be able to access this endpoint
    assert response.status_code == 200
    assert isinstance(response.json(), list)