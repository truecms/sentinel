"""
Tests for combined user filtering.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_get_users_combined_filters(
    client: AsyncClient, superuser_token_headers: dict, db_session: AsyncSession
):
    """Test combining multiple filters."""
    # Create various users
    user1 = User(
        email="admin1@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        role="admin",
    )
    user2 = User(
        email="admin2@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=False,
        role="admin",
    )
    db_session.add(user1)
    db_session.add(user2)
    await db_session.commit()

    # Test combining role and active status filters
    response = await client.get(
        "/api/v1/users/?role=admin&is_active=true", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(user["role"] == "admin" and user["is_active"] for user in data)