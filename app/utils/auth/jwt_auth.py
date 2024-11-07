"""JWT Authentication utility.

This module provides the `JWTAuth` class, which handles JWT-based authentication and
authorization. The class includes methods for token validation, user authorization for
projects, and handling expired tokens by refreshing access tokens as needed.
This functionality is applied as decorators to routes that require authentication.

Classes:
    JWTAuth: Manages JWT-based authentication and authorization for project access.

Usage:
    jwt_auth = JWTAuth(secret_key="your_secret_key")
"""

import jwt
import json
from flask import request, jsonify, Response
from typing import Any
from functools import wraps
from app.models import fetch_project_users
from .get_new_access_token import get_new_access_token


class JWTAuth:
    """A class to manage JWT-based authentication and authorization.

    This class provides methods to validate and decode tokens, authorize users for
    specific projects, handle expired tokens by refreshing them, and apply
    authentication as decorators to routes.

    Attributes:
        secret_key (str): The secret key used to encode and decode JWT tokens.
    """

    def __init__(self, secret_key: str) -> None:
        """Initializes the JWTAuth class with a secret key for encoding and decoding
        tokens.

        Args:
            secret_key (str): The secret key for JWT token operations.
        """
        self.secret_key = secret_key
    
    def check_session_and_authorization(self, root_required: bool = False) -> callable:
        """Decorator factory to check JWT session token validity and user authorization.

        Args:
            f (callable): The function to wrap with session and authorization checks.

        Returns:
            callable: The wrapped function with added session and authorization checks.
        """

        def decorator(f: callable) -> callable:
            @wraps(f)
            def decorated_function(*args: tuple, **kwargs: dict) -> Response:                
                try:
                    token = self._get_token()
                    if not token:
                        return jsonify({"message": "Token is missing"}), 401

                    if root_required:
                        return self._authenticate_root(f, token, *args, **kwargs)
                    
                    if 'pid' in kwargs:
                        return self.authorize_user_for_project(f, token, *args, **kwargs)
                    elif 'user_id' in kwargs:
                        return self.authorize_for_user_specific_operation(f, token, *args, **kwargs)

                    # If no specific project or user authorization is required, proceed
                    return f(*args, **kwargs)
                
                except jwt.ExpiredSignatureError:
                    return self.handle_expired_access_token(f, *args, **kwargs)
                except jwt.InvalidTokenError:
                    return jsonify({"message": "Invalid token."}), 401
            
            return decorated_function
        
        return decorator

    def _authenticate_root(
        self, f: callable, token: str, *args: tuple, **kwargs: dict
    ) -> Response | Any:
        """Method to check whether the current user has root privileges necessary
        to perform sensitive operations.

        Args:
            f (callable): The function to wrap with authorization checks.
            token (str): The JWT access token.
            *args (tuple): Additional arguments for the wrapped function.
            **kwargs (dict): Keyword arguments, including the project ID (`pid`).

        Returns:
            Response | Any: The response from the wrapped function if authorized, or an
                            error response with status 403 or 404 if unauthorized
        """
        token_payload = self._decode_token(token)
        if token_payload.get("is_root") == True:
            return f(*args, **kwargs)
        else:
            return jsonify({"message": "Unathorized"}), 403
        
    def _get_token(self) -> str | None:
        """Extracts the token from the Authorization header.

        Returns:
            str | None: The token if present in the "Authorization" header, or None if
            not found.
        """
        auth_header = request.headers.get("Authorization")
        if auth_header and len(auth_header.split(" ")) == 2:
            return auth_header.split(" ")[1]  # Assuming "Bearer <token>"
        return None

    def _decode_token(self, token: str) -> dict:
        """Decodes a JWT token using the secret key.

        Args:
            token (str): The JWT token to decode.

        Returns:
            dict: The decoded token payload.
        """
        return jwt.decode(token, self.secret_key, algorithms=["HS256"])
    
    def authorize_for_user_specific_operation(
            self, f: callable, token: str, *args: tuple, **kwargs: dict
    ) -> Response | Any:
        """Authorizes a user to perform user-specific operations that cannot
        be performed by the root-user, such as updating their password.

        Args:
            f (callable): The function to wrap with authorization checks.
            token (str): The JWT access token.
            *args (tuple): Additional arguments for the wrapped function.
            **kwargs (dict): Keyword arguments, including the project ID (`pid`).
        
        Returns:
            Response | Any: The response from the wrapped function if authorized, or an
                            error response with status 403 or 404 if unauthorized.
        """
        token_payload = self._decode_token(token)
        user_id = kwargs.get("user_id")

        if user_id:
            current_user_id = token_payload.get('user_id')
            print('hereree', user_id, current_user_id)
            if str(current_user_id) != str(user_id):
                print('unequal')
                return jsonify({"message": "Unauthorized"}), 403
            else:
                return f(*args, **kwargs)

    def authorize_user_for_project(
        self, f: callable, token: str, *args: tuple, **kwargs: dict
    ) -> Response | Any:
        """Authorizes a user for access to a specific project by checking if the user ID
        is in the list of authorized users for the project.

        Args:
            f (callable): The function to wrap with authorization checks.
            token (str): The JWT access token.
            *args (tuple): Additional arguments for the wrapped function.
            **kwargs (dict): Keyword arguments, including the project ID (`pid`).

        Returns:
            Response | Any: The response from the wrapped function if authorized, or an
                            error response with status 403 or 404 if unauthorized.
        """
        token_payload = self._decode_token(token)
        user_uuid = token_payload.get("user_uuid")
        project_pid = kwargs.get("project_uuid")

        if project_pid:
            authorized_user_uuids = fetch_project_users(project_pid)

            if user_uuid in authorized_user_uuids or token_payload.get("is_root") is True:
                return f(*args, **kwargs)
            else:
                return jsonify({"message": "Unauthorized for this project"}), 403

        return f(*args, **kwargs)

    def handle_expired_access_token(
        self, f: callable, *args: tuple, **kwargs: dict
    ) -> Response:
        """Handles an expired access token by refreshing it and re-attempting
        authorization.

        Args:
            f (callable): The function to wrap with token refresh logic.
            *args (tuple): Additional arguments for the wrapped function.
            **kwargs (dict): Keyword arguments for the wrapped function.

        Returns:
            Response: A new access token response if refreshed, or an error message if
                      the refresh token is invalid or expired.
        """
        # error-handling is built-in in the refresh_token method definition
        parsed_json_data = json.loads(
            get_new_access_token()[0].get_data().decode("utf-8")
        )
        new_access_token = parsed_json_data.get("access_token")
        print('new', new_access_token)
        if new_access_token:
            try:
                return self.authorize_user_for_project(
                    f, new_access_token, *args, **kwargs
                )
            except jwt.ExpiredSignatureError:
                return self.handle_expired_access_token(f, *args, **kwargs)
            except jwt.InvalidTokenError:
                return jsonify({"message": "Invalid token."}), 401
        else:
            # return message for invalid or expired refresh token
            return parsed_json_data