"""Authentication routes module.

This module provides authentication routes for user login and logout. It verifies user
credentials, generates access and refresh tokens, and manages token-based authentication
using JWT. Passwords are securely verified using bcrypt.
"""

import bcrypt
from flask import jsonify, request, make_response, Response, g
from flask import Blueprint
from app.config import HTTPONLY, SECURE, SAMESITE
from app.models import fetch_user_by_email, get_user_info
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
    first_name = user.get("first_name")
    last_name = user.get("last_name")
    password_hash = user.get("password_hash")
    is_root = user.get("is_root")

    if bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
        access_token = token_manager.create_access_token(uuid, is_root, expires_in=20)
        refresh_token = token_manager.create_refresh_token(uuid, expires_in=7)

        data = {
            "access_token": access_token,
            "user_uuid": uuid,
            "first_name": first_name,
            "last_name": last_name,
            "is_root": is_root,
        }

        response = make_response(
            jsonify({"status": "success", "data": data}), 200
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=HTTPONLY,
            secure=SECURE,
            samesite=SAMESITE,
            path="/",
            max_age=7 * 24 * 60 * 60,
        )
        return response
    else:
        return jsonify({"status": "error", "message": "Invalid password"}), 401


@bp.route("/logout", methods=["POST"])
def logout() -> Response:
    """Logs out a user by clearing the refresh token cookie."""
    response = make_response(
        jsonify({"status": "success", "message": "Succesfully logged out"}), 200
    )
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


@bp.route("/status", methods=["GET"])
@auth_manager.authenticate
def auth_status():
    user_uuid = g.user_payload.get("user_uuid")

    if not user_uuid:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    data = get_user_info(user_uuid)

    return jsonify({"status": "success", "data": data}), 200
