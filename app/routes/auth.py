"""Authentication routes module.

This module provides authentication routes for user login and logout. It verifies user
credentials, generates access and refresh tokens, and manages token-based authentication
using JWT. Passwords are securely verified using bcrypt.

Routes:
    /login (POST): Authenticates a user, issuing JWT access and refresh tokens upon
    successful login.
    /logout (GET): Logs out a user by clearing the refresh token cookie.
    /refresh (POST): Refreshes a JWT Token

Attributes:
    bp (Blueprint): Blueprint for the authentication routes.
"""

import bcrypt
from flask import jsonify, request, make_response, Response
from flask import Blueprint
from app.config import HTTPONLY, SECURE, SAMESITE, PATH
from app.models import fetch_user_by_email
from app.utils.auth import TokenManager, AuthManager
token_manager = TokenManager()
auth_manager = AuthManager(token_manager)

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["POST"])
def login() -> Response:
    """Logs in a user by verifying credentials and issuing JWT tokens."""
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = fetch_user_by_email(email)

    if not user:
        return jsonify({"status": "error", "message": "User does not exist"}), 404

    uuid = user.get("uuid")
    password_hash = user.get("password_hash")
    is_root = user.get("is_root")

    if bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
        print("password matches")
        access_token = token_manager.create_access_token(uuid, is_root, expires_in=20)
        refresh_token = token_manager.create_refresh_token(uuid, is_root, expires_in=7)

        print(HTTPONLY, SECURE, SAMESITE, PATH)

        response = make_response(jsonify({"status": "success", "access_token": access_token}), 200)
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=HTTPONLY,
            secure=SECURE,
            samesite=SAMESITE,
            path="/",
            max_age=7 * 24 * 60 * 60
        )
        print("login response", response.headers)
        return response
    else:
        return jsonify({"status": "error", "message": "Invalid password"}), 401


@bp.route("/logout", methods=["GET"])
def logout() -> Response:
    """Logs out a user by clearing the refresh token cookie."""
    response = make_response(jsonify({"status": "success", "message": "Succesfully logged out"}), 200)
    response.set_cookie(
        "refresh_token",
        "",
        expires=0,
        httponly=HTTPONLY,
        secure=SECURE,
        samesite=SAMESITE,
        path="/",
    )

    return response


@bp.route("/refresh", methods=["POST"])
def refresh() -> Response:
    """Refreshes the user's access token."""
    new_access_token, error_response = token_manager.refresh_access_token()
    if error_response:
        return jsonify(error_response), 401
    return jsonify({"status": "success", "access_token": new_access_token}), 200


@bp.route('/status', methods=['GET'])
@auth_manager.authenticate
def auth_status():
    return jsonify({"status": "success", "message": "Authenticated"}), 200