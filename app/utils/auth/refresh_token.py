"""Refresh token utility.

This module provides a function to handle access token refresh requests. It checks the
refresh token from the client's cookies, validates it, and issues a new access token if
the refresh token is valid. If the refresh token is expired or invalid, it returns an
appropriate error message.

Functions:
    refresh_token: Validates the refresh token and generates a new access token.
"""

import jwt
import datetime
from typing import Tuple
from flask import request, jsonify, Response
from .redis_client import get_user_root_info_from_cache


def refresh_token() -> Tuple[Response, int]:
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
    if not refresh_token:
        return jsonify({"message": "Token is missing!"}), 401
    try:
        decoded_refresh_token = jwt.decode(
            refresh_token, "SECRET", algorithms=["HS256"]
        )
        user_id = decoded_refresh_token.get("user_id")
        is_root = get_user_root_info_from_cache(user_id)

        access_token = jwt.encode(
            {
                "user_id": user_id,
                "is_root": is_root,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
            },
            "SECRET",
            algorithm="HS256",
        )

        return jsonify({"access_token": access_token}), 200
    except jwt.ExpiredSignatureError:
        # the frontend should handle these responses by redirecting to the login view
        return jsonify({"message": "Token expired. Please log in again."}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"message": "Invalid token", "error": str(e)}), 401
    except Exception as e:
        raise e
