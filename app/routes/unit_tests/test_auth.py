import pytest
import bcrypt
from unittest.mock import patch
from mock_data import MOCK_DATA, status_codes
from app.utils.auth import TokenManager

access_token = None

@pytest.fixture
def token_manager():
    return TokenManager()

@pytest.fixture
@patch("app.routes.auth.fetch_user_by_email")
def authenticated_client(mock_fetch_user_by_email, client, token_manager):
    """ Fixture to log in and return a client with a refresh token cookie"""

    mock_fetch_user_by_email.return_value = {
        "uuid": "test-uuid",
        "first_name": "John",
        "last_name": "Doe",
        "password_hash": bcrypt.hashpw(b"testpassword", bcrypt.gensalt()).decode("utf-8"),
        "is_root": False,
    }

    # Perform login
    response = client.post(
        "/api/auth/login",
        json={"email": "john.doe@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200

    return client

# Tests for login route

@patch("app.routes.auth.fetch_user_by_email")
def test_login_success(mock_fetch_user_by_email, client):

    mock_fetch_user_by_email.return_value = {
        "uuid": "test-uuid",
        "first_name": "John",
        "last_name": "Doe",
        "password_hash": bcrypt.hashpw(b"testpassword", bcrypt.gensalt()).decode("utf-8"),
        "is_root": False,
    }

    response = client.post(
        "/api/auth/login",
        json={"email": "john.doe@example.com", "password": "testpassword"},
    )

    assert response.status_code == 200
    json_data = response.get_json()
    assert "access_token" in json_data["payload"]
    assert json_data["payload"]["user"]["first_name"] == "John"

    # Check the cookie is set in the response
    set_cookie_header = response.headers.get("Set-Cookie")
    assert set_cookie_header is not None
    assert "refresh_token=" in set_cookie_header

@patch("app.routes.auth.fetch_user_by_email")
def test_login_failure_invalid_email(mock_fetch_user_by_email, client):
    # Simulate no user found for the email
    mock_fetch_user_by_email.return_value = None

    response = client.post(
        "/api/auth/login",
        json={"email": "invalid@example.com", "password": "testpassword"},
    )

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["message"] == "Invalid email or password"

@patch("app.routes.auth.fetch_user_by_email")
def test_login_failure_invalid_password(mock_fetch_user_by_email, client):
    # Mock user data with a different password hash
    mock_fetch_user_by_email.return_value = {
        "uuid": "test-uuid",
        "first_name": "John",
        "last_name": "Doe",
        "password_hash": bcrypt.hashpw(b"wrongpassword", bcrypt.gensalt()).decode("utf-8"),
        "is_root": False,
    }

    response = client.post(
        "/api/auth/login",
        json={"email": "john.doe@example.com", "password": "testpassword"},
    )

    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["message"] == "Invalid email or password"

def test_login_failure_no_payload(client):
    response = client.post(
        "/api/auth/login",
        json={},
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["message"] == "Invalid request"


# Tests for token refresh route

def test_refresh_success(authenticated_client):
    response = authenticated_client.post(
        "/api/auth/refresh",
    )

    assert response.status_code == 200
    json_data = response.get_json()
    print('refresh response', json_data)
    access_token = json_data["payload"]
    assert access_token

def test_refresh_failure_invalid_token(client):
    invalid_token = "invalid-token"

    response = client.post(
        "/api/auth/refresh",
        headers={"Cookie": f"refresh_token={invalid_token}"}
    )

    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["message"] == "Authentication required. Please log in."

def test_refresh_failure_no_token(client):
    """Make a refresh request without providing a token"""
    response = client.post("/api/auth/refresh")

    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["message"] == "Authentication required. Please log in."

def test_refresh_failure_expired_token(client, token_manager):
    expired_token = token_manager.create_refresh_token("test-uuid", expires_in=-1)

    response = client.post(
        "/api/auth/refresh",
        headers={"Cookie": f"refresh_token={expired_token}"}
    )

    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["message"] == "Authentication required. Please log in."


# Tests for logout route

def test_successful_logout(authenticated_client):
    response = authenticated_client.post("/api/auth/logout")

    assert response.status_code == 204

    # Check if the cookie has been cleared
    set_cookie_header = response.headers.get("Set-Cookie")
    assert set_cookie_header is not None
    assert "refresh_token=;" in set_cookie_header
    assert "Expires=Thu, 01 Jan 1970" in set_cookie_header

def test_logout_failure_no_cookie(client):
    """Make a logout request without a refresh token cookie set"""
    response = client.post("/api/auth/logout")

    assert response.status_code == 204  # Logout should succeed even if there's no cookie
    set_cookie_header = response.headers.get("Set-Cookie")
    assert "refresh_token=;" in set_cookie_header  # Ensure the cookie is cleared

