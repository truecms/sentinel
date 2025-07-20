"""
Tests for basic user pagination.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_get_users_pagination(
    client: AsyncClient, superuser_token_headers: dict, db_session: AsyncSession
):
    """Test user list pagination."""
    # Create multiple test users
    for i in range(15):  # Create enough users to test pagination
        user = User(
            email=f"testuser{i}@example.com",
            hashed_password=get_password_hash("testpass123"),
            is_active=True,
            role="user",
        )
        db_session.add(user)
    await db_session.commit()

    # Test first page
    response = await client.get(
        "/api/v1/users/?skip=0&limit=10", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10

    # Test second page
    response = await client.get(
        "/api/v1/users/?skip=10&limit=10", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert len(data) <= 10