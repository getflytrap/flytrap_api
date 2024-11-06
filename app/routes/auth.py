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

import os
import bcrypt
import datetime
import jwt
from flask import jsonify, request, make_response, redirect, Response
from flask import Blueprint
from app.models import (
    fetch_user_by_email,
)
from app.utils.auth import get_new_access_token
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint("auth", __name__)

# secure: set to False for local testing
httponly = True if os.getenv("HTTPONLY") == "True" else False
secure = True if os.getenv("SECURE") == "True" else False
samesite = os.getenv("SAMESITE")
path = os.getenv("PATH")


@bp.route("/login", methods=["POST"])
def login() -> Response:
    """Logs in a user by verifying credentials and issuing JWT tokens.

    This endpoint:
        - Accepts a JSON payload with 'email' and 'password'.
        - Validates the email and password against stored user data.
        - Issues a short-lived JWT access token and a longer-lived refresh token if
          authentication succeeds.
        - Sets the refresh token in an HTTP-only cookie to improve security.

    Returns:
        Response: JSON response containing the access token with a 200 status if
        successful, or error messages with appropriate status codes if login fails.
    """
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = fetch_user_by_email(email)

    if not user:
        return jsonify({"message": "User does not exist"}), 404

    id = user.get("id")
    password_hash = user.get("password_hash")
    is_root = user.get("is_root")

    if bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
        print("password matches")
        access_token = jwt.encode(
            {
                "user_id": id,
                "is_root": is_root,
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(minutes=60),
            },
            os.getenv("JWT_SECRET_KEY"),
            algorithm="HS256",
        )

        refresh_token = jwt.encode(
            {
                "user_id": id,
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(days=7),
            },
            os.getenv("JWT_SECRET_KEY"),
            algorithm="HS256",
        )

        response = make_response(jsonify({"access_token": access_token}), 200)
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=httponly,
            secure=secure,
            samesite=samesite,
            path=path,
        )
        print(response.headers)
        return response
    else:
        return jsonify({"message": "Invalid password"}), 401


@bp.route("/logout", methods=["GET"])
def logout() -> Response:
    """Logs out a user by clearing the refresh token cookie.

    This endpoint:
        - Redirects the user to the login page.
        - Clears the refresh token from the cookie by setting its expiration date to the
          past.
        - Does not clear the access token, as it is typically stored in memory on the
          client side.

    Returns:
        Response: A redirection response to the login page with the refresh token cookie
        cleared.
    """
    response = make_response(redirect("/login"), 302)
    response.set_cookie(
        "refresh_token", "", expires=0, httponly=httponly, secure=secure, samesite=samesite, path=path
    )

    # Note: No access_token clearing needed since it's client-managed in memory
    return response


@bp.route("/refresh", methods=["POST"])
def refresh() -> Response:
    """
    Refreshes the user's access token.

    This endpoint uses the `refresh_token` function to generate a new access token
    based on the refresh token provided in the request. It is intended to be called
    when the user's access token has expired.

    Returns:
        Response: JSON response containing a new access token, or an error message if
        the refresh token is invalid or missing.
    """
    return get_new_access_token()
