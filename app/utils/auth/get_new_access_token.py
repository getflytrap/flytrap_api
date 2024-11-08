"""Refresh token utility.

This module provides a function to handle access token refresh requests. It checks the
refresh token from the client's cookies, validates it, and issues a new access token if
the refresh token is valid. If the refresh token is expired or invalid, it returns an
appropriate error message.

Functions:
    refresh_token: Validates the refresh token and generates a new access token.
"""

import os
import jwt
import datetime
from typing import Tuple
from flask import request, jsonify, Response
from dotenv import load_dotenv
from app.models import get_user_root_info

load_dotenv()


def get_new_access_token() -> Tuple[Response, int]:
    """Generates a new access token using a valid refresh token.

    This function:
        - Extracts the refresh token from cookies.
        - Decodes and validates the refresh token.
        - Retrieves user information, including root status, from the cache.
        - Issues a new access token valid for a specified time.

    Returns:
        Tuple[Response, int]: A JSON response containing a new access token with a 200
        status code if successful, or an error message with a 401 status code if the
        refresh token is missing, expired, or invalid.

    Raises:
        Exception: Propagates unexpected errors during token processing.
    """
    refresh_token = request.cookies.get("refresh_token")
    print("coooooookies", request.cookies)
    if not refresh_token:
        return jsonify({"message": "Token is missing!"}), 401
    try:
        refresh_token_payload = jwt.decode(
            refresh_token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"]
        )

        print("refresh", refresh_token_payload)
        user_uuid = refresh_token_payload.get("user_uuid")
        is_root = get_user_root_info(user_uuid)
        print("new access token is root", is_root)

        access_token = jwt.encode(
            {
                "user_uuid": user_uuid,
                "is_root": is_root,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=20),
            },
            os.getenv("JWT_SECRET_KEY"),
            algorithm="HS256",
        )

        return jsonify({"access_token": access_token}), 200
    except jwt.ExpiredSignatureError:
        # the frontend should handle these responses by redirecting to the login view
        return jsonify({"message": "Token expired"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"message": "Invalid token", "error": str(e)}), 401
    except Exception as e:
        raise e
