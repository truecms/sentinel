import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User

pytestmark = pytest.mark.asyncio

TEST_PASSWORD = "test123"  # Match the password from conftest.py


async def test_login_access_token(client: AsyncClient, test_user: User):
    """Test login with valid credentials."""
    response = await client.post(
        "/api/v1/auth/access-token",
        data={
            "username": test_user.email,
            "password": TEST_PASSWORD,  # Use the correct password
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_password(client: AsyncClient, test_user: User):
    """Test login with invalid password."""
    response = await client.post(
        "/api/v1/auth/access-token",
        data={"username": test_user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


async def test_login_invalid_email(client: AsyncClient):
    """Test login with non-existent email."""
    response = await client.post(
        "/api/v1/auth/access-token",
        data={"username": "nonexistent@example.com", "password": TEST_PASSWORD},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


async def test_login_inactive_user(client: AsyncClient, db_session: AsyncSession):
    """Test login with inactive user."""
    # Create an inactive user
    inactive_user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=False,
    )
    db_session.add(inactive_user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/access-token",
        data={"username": "inactive@example.com", "password": TEST_PASSWORD},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Inactive user"


async def test_test_token(
    client: AsyncClient,
    user_token_headers: dict,
    test_user: User,
    db_session: AsyncSession,
):
    """Test token validation endpoint."""
    # Store email before async operations
    user_email = test_user.email

    response = await client.post("/api/v1/auth/test-token", headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_email


async def test_test_token_invalid(client: AsyncClient):
    """Test token validation with invalid token."""
    response = await client.post(
        "/api/v1/auth/test-token", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


async def test_change_password(
    client: AsyncClient,
    user_token_headers: dict,
    test_user: User,
    db_session: AsyncSession,
):
    """Test password change with valid current password."""
    # Store email before async operations
    user_email = test_user.email

    response = await client.post(
        "/api/v1/auth/change-password",
        headers=user_token_headers,
        json={"current_password": TEST_PASSWORD, "new_password": "newtestpass123"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"

    # Verify can login with new password
    response = await client.post(
        "/api/v1/auth/access-token",
        data={"username": user_email, "password": "newtestpass123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_change_password_invalid_current(
    client: AsyncClient, user_token_headers: dict
):
    """Test password change with invalid current password."""
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=user_token_headers,
        json={"current_password": "wrongpassword", "new_password": "newtestpass123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid current password"


async def test_get_current_user(
    client: AsyncClient,
    user_token_headers: dict,
    test_user: User,
    db_session: AsyncSession,
):
    """Test getting current user details."""
    # Store email before async operations
    user_email = test_user.email

    response = await client.get("/api/v1/auth/me", headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_email


async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test getting current user with invalid token."""
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


async def test_logout_success(
    client: AsyncClient, user_token_headers: dict, test_user: User
):
    """Test successful logout with valid token."""
    response = await client.post("/api/v1/auth/logout", headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Successfully logged out"


async def test_logout_invalid_token(client: AsyncClient):
    """Test logout with invalid token."""
    response = await client.post(
        "/api/v1/auth/logout", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


async def test_logout_no_token(client: AsyncClient):
    """Test logout without authentication token."""
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
