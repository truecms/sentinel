"""
Tests for user search functionality.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_get_users_search(
    client: AsyncClient, superuser_token_headers: dict, db_session: AsyncSession
):
    """Test searching users by email."""
    # Create users with specific emails
    search_user = User(
        email="searchable@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        role="user",
    )
    other_user = User(
        email="other@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        role="user",
    )
    db_session.add(search_user)
    db_session.add(other_user)
    await db_session.commit()

    # Test searching by email
    response = await client.get(
        "/api/v1/users/?search=searchable", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any("searchable" in user["email"] for user in data)