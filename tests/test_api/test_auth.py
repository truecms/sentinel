import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User

pytestmark = pytest.mark.asyncio

async def test_login_success(client: AsyncClient, test_user: User):
    """Test successful login."""
    response = await client.post(
        "/api/v1/auth/access-token",
        data={
            "username": test_user.email,
            "password": "test123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with nonexistent user."""
    response = await client.post(
        "/api/v1/auth/access-token",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

async def test_login_wrong_password(client: AsyncClient, test_user: User):
    """Test login with wrong password."""
    response = await client.post(
        "/api/v1/auth/access-token",
        data={
            "username": test_user.email,
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

async def test_get_current_user_success(
    client: AsyncClient,
    test_user: User,
    user_token_headers: dict
):
    """Test getting current user details."""
    # Store the email before making the request
    user_email = test_user.email
    user_id = test_user.id
    
    response = await client.get(
        "/api/v1/auth/me",
        headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_email
    assert data["id"] == user_id

async def test_get_current_user_no_auth(client: AsyncClient):
    """Test getting current user without authentication."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test getting current user with invalid token."""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

async def test_change_password_success(
    client: AsyncClient,
    test_user: User,
    user_token_headers: dict
):
    """Test successful password change."""
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=user_token_headers,
        json={
            "current_password": "test123",
            "new_password": "newpass123"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"

async def test_change_password_wrong_current(
    client: AsyncClient,
    test_user: User,
    user_token_headers: dict
):
    """Test password change with wrong current password."""
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=user_token_headers,
        json={
            "current_password": "wrongpass",
            "new_password": "newpass123"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid current password"
