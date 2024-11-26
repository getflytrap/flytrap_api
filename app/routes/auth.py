"""Authentication routes module.

This module provides authentication routes for user login and logout. It verifies user
credentials, generates access and refresh tokens, and manages token-based authentication
using JWT. Passwords are securely verified using bcrypt.
"""

import bcrypt
from flask import jsonify, request, make_response, Response, g, Blueprint, current_app
from app.models import fetch_user_by_email, get_user_info
from app.utils.auth import TokenManager, AuthManager

token_manager = TokenManager()
auth_manager = AuthManager(token_manager)

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["POST"])
def login() -> Response:
    """Logs in a user by verifying credentials and issuing JWT tokens."""
    data = request.json

    if not data:
        return jsonify({"result": "error", "message": "Invalid request"}), 400
    

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"result": "error", "message": "Invalid request"}), 400


    user = fetch_user_by_email(email)

    if not user:
        return jsonify({"result": "error", "message": "Invalid email or password"}), 403


    # Extract user details
    uuid = user.get("uuid")
    first_name = user.get("first_name")
    last_name = user.get("last_name")
    password_hash = user.get("password_hash")
    is_root = user.get("is_root")

    # Verify password
    if bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
        access_token = token_manager.create_access_token(uuid, is_root, expires_in=20)
        refresh_token = token_manager.create_refresh_token(uuid, expires_in=7)

        # Construct response data
        user_info = {
            "access_token": access_token,
            "user_uuid": uuid,
            "first_name": first_name,
            "last_name": last_name,
            "is_root": is_root,
        }

        # Attach refresh token as cookie
        response = make_response(jsonify({"result": "success", "payload": user_info}), 200)
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
    else:
        # Handle invalid password
        return jsonify({"result": "error", "message": "Invalid email or password"}), 403


@bp.route("/logout", methods=["POST"])
def logout() -> Response:
    """Logs out a user by clearing the refresh token cookie."""
    response = make_response('', 204)
    response.set_cookie(
        "refresh_token",
        "",
        expires=0,
        httponly=current_app.config["HTTPONLY"],
        secure=current_app.config["SECURE"],
        samesite=current_app.config["SAMESITE"],
        path="/",
    )

    return response


@bp.route("/refresh", methods=["POST"])
def refresh() -> Response:
    """Refreshes the user's access token."""
    new_access_token, error_response = token_manager.refresh_access_token()
    if error_response:
        return jsonify(error_response), 401

    return jsonify({"result": "success", "payload": new_access_token}), 200


@bp.route("/status", methods=["GET"])
@auth_manager.authenticate
def auth_status():
    user_uuid = g.user_payload.get("user_uuid")

    if not user_uuid:
        return jsonify({"result": "error", "message": "User not found"}), 404

    user_info = get_user_info(user_uuid)

    return jsonify({"result": "success", "payload": user_info}), 200
