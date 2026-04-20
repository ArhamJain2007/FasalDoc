"""
Tests for /api/v1/auth/register and /api/v1/auth/login.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """New user registration returns 201 with JWT token."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "phone": "9123456789",
            "name": "Harjinder Singh",
            "region": "Punjab",
            "language": "pa",
            "primary_crops": ["wheat", "rice"],
            "password": "securepass123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["region"] == "Punjab"
    assert data["language"] == "pa"
    assert "user_id" in data


@pytest.mark.asyncio
async def test_register_invalid_phone(client: AsyncClient):
    """Invalid phone number format should return 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "phone": "1234567890",  # starts with 1 — invalid Indian number
            "name": "Test User",
            "region": "Delhi",
            "password": "pass123456",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_duplicate_phone(client: AsyncClient, test_user):
    """Registering with an existing phone number returns 409."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "phone": test_user.phone,
            "name": "Duplicate User",
            "region": "Haryana",
            "password": "anotherpass123",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"] == "PHONE_ALREADY_REGISTERED"


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    """Password shorter than 6 characters should return 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "phone": "8012345678",
            "name": "Test User",
            "region": "UP",
            "password": "abc",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Login with correct credentials returns JWT."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"phone": test_user.phone, "password": "testpassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user_id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Wrong password should return 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"phone": test_user.phone, "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_unknown_phone(client: AsyncClient):
    """Login with unregistered phone returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"phone": "9999999999", "password": "somepassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient):
    """Accessing protected endpoint without token returns 401."""
    response = await client.get("/api/v1/history")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token(client: AsyncClient, auth_headers: dict):
    """Accessing protected endpoint with valid token returns non-401."""
    response = await client.get("/api/v1/history", headers=auth_headers)
    assert response.status_code != 401
