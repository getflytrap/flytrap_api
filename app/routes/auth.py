"""Authentication routes module.

This module provides authentication routes for user login and logout. It verifies user
credentials, generates access and refresh tokens, and manages token-based authentication
using JWT. Passwords are securely verified using bcrypt.
"""

import bcrypt
from flask import jsonify, request, make_response, Response, Blueprint, current_app
from app.models import fetch_user_by_email
from app.utils.auth import TokenManager, AuthManager

token_manager = TokenManager()
auth_manager = AuthManager(token_manager)

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["POST"])
def login() -> Response:
    """Logs in a user by verifying credentials and issuing JWT tokens."""
    current_app.logger.debug("Login request received.")

    data = request.json

    if not data:
        current_app.logger.error("Invalid request: No JSON payload.")
        return jsonify({"message": "Invalid request"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        current_app.logger.error(f"Login request missing email or password: email={email}")
        return jsonify({"message": "Invalid email or password"}), 400

    try:
        user = fetch_user_by_email(email)

        if not user:
            current_app.logger.warning(f"Login failed: user with email {email} not found.")
            return jsonify({"message": "Invalid email or password"}), 400

        # Extract user details
        uuid = user.get("uuid")
        first_name = user.get("first_name")
        last_name = user.get("last_name")
        password_hash = user.get("password_hash")
        is_root = user.get("is_root")

        # Verify password
        if not bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
            current_app.logger.warning(f"Login failed: invalid password for email {email}.")
            return jsonify({"message": "Invalid email or password"}), 401
        
        access_token = token_manager.create_access_token(uuid, is_root, expires_in=20)
        refresh_token = token_manager.create_refresh_token(uuid, expires_in=7)

        # Construct response data
        user_info = {
            "user_uuid": uuid,
            "first_name": first_name,
            "last_name": last_name,
            "is_root": is_root,
        }

        # Attach refresh token as cookie
        response = make_response(
            jsonify({"payload": {"user": user_info, "access_token": access_token}}), 200
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=current_app.config["HTTPONLY"],
            secure=current_app.config["SECURE"],
            samesite=current_app.config["SAMESITE"],
            path="/",
            max_age=7 * 24 * 60 * 60,
        )
        return response
    except Exception as e:
        current_app.logger.error(f"Login failed for user {email}: {e}", exc_info=True)
        return jsonify({"message": "Login failed."}), 500
    

@bp.route("/logout", methods=["POST"])
def logout() -> Response:
    """Logs out a user by clearing the refresh token cookie."""
    current_app.logger.debug("Logout request received.")

    response = make_response("", 204)
    response.set_cookie(
        "refresh_token",
        "",
        expires=0,
        httponly=current_app.config["HTTPONLY"],
        secure=current_app.config["SECURE"],
        samesite=current_app.config["SAMESITE"],
        path="/",
    )

    current_app.logger.info("User logged out successfully.")
    return response


@bp.route("/refresh", methods=["POST"])
def refresh() -> Response:
    """Refreshes the user's access token."""
    current_app.logger.debug("Access token refresh request received.")

    try:
        new_access_token, error_response = token_manager.refresh_access_token()
        if error_response:
            current_app.logger.warning(f"Token refresh failed: {error_response["message"]}.")
            return jsonify(error_response), 401

        current_app.logger.info("Access token refreshed successfully.")
        return jsonify({"payload": new_access_token}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to refresh access token: {e}", exc_info=True)
        return jsonify({"message": "Unable to refresh session. Please log in again."}), 500