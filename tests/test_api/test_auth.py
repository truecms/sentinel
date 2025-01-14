import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User

pytestmark = pytest.mark.asyncio

async def test_login_success(client: AsyncClient, test_user: User):
    """Test successful login."""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "test123"  # This matches the hashed password in test_user fixture
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

async def test_login_wrong_password(client: AsyncClient, test_user: User):
    """Test login with wrong password."""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "access_token" not in response.json()

async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent user."""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "test123"
        }
    )
    assert response.status_code == 401
    assert "access_token" not in response.json()

async def test_get_current_user(
    client: AsyncClient, test_user: User, user_token_headers: dict
):
    """Test getting current user details."""
    response = await client.get(
        "/api/v1/auth/me",
        headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert "id" in data

async def test_get_current_user_no_auth(client: AsyncClient):
    """Test getting current user without authentication."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401

async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test getting current user with invalid token."""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

async def test_change_password(
    client: AsyncClient,
    test_user: User,
    user_token_headers: dict,
    db_session: AsyncSession
):
    """Test password change functionality."""
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=user_token_headers,
        json={
            "current_password": "test123",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 200
    
    # Verify login with new password works
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "newpassword123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

async def test_change_password_wrong_current(
    client: AsyncClient,
    user_token_headers: dict
):
    """Test password change with wrong current password."""
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=user_token_headers,
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 400
