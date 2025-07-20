"""Test that organization users endpoint requires proper permissions."""
import pytest
from httpx import AsyncClient

from app.models.organization import Organization
from app.models.user import User


@pytest.mark.asyncio
async def test_regular_user_cannot_view_organization_users(
    client: AsyncClient,
    test_organization: Organization,
    user_token_headers: dict,
):
    """Test that regular users cannot view organization users."""
    response = await client.get(
        f"/api/v1/users/organization/{test_organization.id}/users",
        headers=user_token_headers,
    )
    
    # This test expects 403 but currently gets 200 (security issue)
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]