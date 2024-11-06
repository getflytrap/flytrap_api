"""Root-level Authentication utility.

This module provides the `RootAuth` class, which handles root-level authorization
for routes in a Flask application. The class includes methods for verifying JWTs
with root access, handling expired tokens by refreshing them, and validating new
access tokens for root privileges.

Classes:
    RootAuth: Manages root-level access authentication and authorization.

Usage:
    root_auth = RootAuth(secret_key="your_secret_key")
"""

import jwt
import json
from functools import wraps
from flask import request, jsonify, make_response
from .refresh_token import refresh_token


class RootAuth:
    """A class to manage root-level access authentication.

    This class provides methods to verify and refresh JWTs for root access,
    ensuring only users with root privileges can access certain routes.

    Attributes:
        secret_key (str): The secret key used to encode and decode JWT tokens.
    """

    def __init__(self, secret_key: str) -> None:
        """Initializes the RootAuth class with a secret key for JWT operations.

        Args:
            secret_key (str): The secret key for JWT token encoding and decoding.
        """
        self.secret_key = secret_key

    def require_root_access(self, f):
        """Decorator that restricts access to root users based on the JWT token.

        This decorator:
            - Checks the Authorization header for a valid token.
            - Decodes the token and verifies if the user has root access.
            - If the token is expired, it attempts to refresh it and re-check root
              access.

        Args:
            f (callable): The function to wrap with root access validation.

        Returns:
            callable: The wrapped function with root access validation.
        """

        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return jsonify({"message": "Token is missing"}), 401

            try:
                token_payload = jwt.decode(
                    auth_header.split(" ")[1], self.secret_key, algorithms=["HS256"]
                )
                if token_payload.get("is_root"):
                    return f(*args, **kwargs)
                else:
                    return jsonify({"message": "Invalid token"}), 401
            except jwt.ExpiredSignatureError:
                new_access_token = self.handle_expired_token(f, *args, **kwargs)
                return self.check_root_access(new_access_token, f, *args, **kwargs)
            except jwt.InvalidTokenError:
                return jsonify({"message": "Invalid token."}), 401

        return wrapper

    def handle_expired_token(self, f, *args, **kwargs):
        """Handles an expired token by attempting to refresh it.

        Args:
            f (callable): The function to wrap with token refresh logic.
            *args (tuple): Additional arguments for the wrapped function.
            **kwargs (dict): Keyword arguments for the wrapped function.

        Returns:
            str | None: The new access token if refreshed successfully, or None if the
                        refresh token is expired or invalid.
        """
        refresh_token_response_data = json.loads(
            refresh_token()[0].get_data().decode("utf-8")
        )
        new_access_token = refresh_token_response_data.get("access_token")
        return new_access_token

    def check_root_access(self, new_access_token, f, *args, **kwargs):
        """Validates root access for a new access token.

        Args:
            new_access_token (str): The refreshed access token.
            f (callable): The function to wrap with root access validation.
            *args (tuple): Additional arguments for the wrapped function.
            **kwargs (dict): Keyword arguments for the wrapped function.

        Returns:
            Response: The original response if root access is confirmed, or an error
            response if the user lacks root privileges or the token is invalid.
        """
        if new_access_token:
            is_root = (
                jwt.decode(new_access_token, self.secret_key, algorithms=["HS256"]).get(
                    "is_root"
                )
                is True
            )
            if is_root:
                response = make_response(f(*args, **kwargs))
                response.headers["Authorization"] = f"Bearer {new_access_token}"
                return response
            else:
                return jsonify({"message": "Unauthorized. Root users only"}), 403
        else:
            return jsonify({"message": "Refresh token expired or invalid."}), 401
