from tests.utils.mock_data import raw_users

def test_login_success(client, regular_user):
    """Test successful login as regular user."""
    user_data = raw_users["regular_user"]
    
    response = client.post(
        "/api/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )

    assert response.status_code == 200
    assert "payload" in response.json, "Response should contain 'payload' key."
    assert "access_token" in response.json["payload"]
    assert "user" in response.json["payload"]
    
    refresh_token_cookie = response.headers.get("Set-Cookie")
    assert refresh_token_cookie is not None
    assert "refresh_token=" in refresh_token_cookie, "Refresh token should be set as a cookie."


def test_login_invalid_password(client, regular_user):
    """Test login with an invalid password."""
    user_data = raw_users["regular_user"]
    
    response = client.post(
        "/api/auth/login",
        json={"email": user_data["email"], "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert response.json["message"] == "Invalid email or password"


def test_login_nonexistent_user(client):
    """Test login with a nonexistent user."""
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@user.com", "password": "password"},
    )

    assert response.status_code == 400
    assert response.json["message"] == "Invalid email or password"


def test_login_no_payload(client):
    response = client.post("/api/auth/login", json={})

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["message"] == "Invalid request"


def test_logout_success(root_client):
    """Test successful logout."""
    response = root_client.post("/api/auth/logout")

    assert response.status_code == 204
    refresh_token_cookie = response.headers.get("Set-Cookie")
    assert refresh_token_cookie is not None
    assert "refresh_token=;" in refresh_token_cookie
    assert "Expires=Thu, 01 Jan 1970" in refresh_token_cookie


def test_refresh_success(regular_client):
    """Test successful token refresh."""
    response = regular_client.post("/api/auth/refresh")

    assert response.status_code == 200
    assert "payload" in response.json, "Response should contain 'payload' key."


def test_refresh_no_token(client):
    """Test token refresh with no refresh token provided."""
    response = client.post("/api/auth/refresh")

    assert response.status_code == 401
    assert response.json["message"] == "Authentication required. Please log in."


def test_refresh_invalid_token(root_client):
    """Test token refresh with an invalid refresh token."""
    root_client.set_cookie("refresh_token", "invalidtoken")
    response = root_client.post("/api/auth/refresh")

    assert response.status_code == 401
    assert response.json["message"] == "Invalid session. Please log in again."
