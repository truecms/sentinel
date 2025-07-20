"""Test that registration assigns org_admin role"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import Role, UserRole
from app.models.user import User


@pytest.mark.asyncio
async def test_register_user_gets_org_admin_role(
    client: AsyncClient,
    db_session: AsyncSession
):
    """Test that registering a user assigns them org_admin role for their organization"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newadmin@example.com",
            "password": "Test123!",
            "full_name": "New Admin",
            "organization_name": "Admin Org"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Get the user with roles loaded
    user_query = (
        select(User)
        .options(selectinload(User.user_roles).selectinload(UserRole.role))
        .where(User.id == data["id"])
    )
    result = await db_session.execute(user_query)
    user = result.scalar_one()
    
    # Check if user has org_admin role
    has_role = user.has_role("org_admin", organization_id=user.organization_id)
    assert has_role is True