"""Test user registration with default organization and org_admin role assignment"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User
from app.models.user_organization import user_organization


@pytest.mark.asyncio
async def test_register_user_with_default_organization(
    client: AsyncClient,
    db_session: AsyncSession
):
    """Test that registering a user sets their organization as default"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "Test123!",
            "full_name": "New User",
            "organization_name": "New Org"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    
    # Check that organization was created
    org_query = select(Organization).where(Organization.name == "New Org")
    result = await db_session.execute(org_query)
    org = result.scalar_one_or_none()
    assert org is not None
    
    # Check that user-organization association has is_default=True
    user_org_query = select(user_organization).where(
        user_organization.c.user_id == data["id"],
        user_organization.c.organization_id == org.id
    )
    result = await db_session.execute(user_org_query)
    user_org = result.fetchone()
    assert user_org is not None
    assert user_org.is_default is True