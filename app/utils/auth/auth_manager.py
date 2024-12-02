import jwt
from flask import request, g, jsonify, current_app
from functools import wraps
from .token_manager import TokenManager
from app.models import fetch_project_users


class AuthManager:
    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager

    # Authentication decorator
    def authenticate(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = self._get_token()
            if not token:
                current_app.logger.info("Authentication failed: Missing token.")
                return (
                    jsonify({"message": "Authentication required. Please log in."}),
                    401,
                )
            try:
                g.user_payload = self.token_manager.decode_token(token)
            except jwt.ExpiredSignatureError:
                current_app.logger.info("Authentication failed: Token expired.")
                return (
                    jsonify({"message": "Session expired. Please log in again."}),
                    401,
                )
            except jwt.InvalidTokenError:
                current_app.logger.info("Authentication failed: Invalid token.")
                return (
                    jsonify({"message": "Invalid session. Please log in again."}),
                    401,
                )
            except Exception as e:
                current_app.logger.error(
                    f"Unexpected error during token authentication: {e}", exc_info=True
                )
                return jsonify({"message": "Internal server error."}), 500

            return f(*args, **kwargs)

        return decorated_function

    # Root authorization decorator
    def authorize_root(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user_payload.get("is_root"):
                current_app.logger.debug("Root access granted.")
                return f(*args, **kwargs)

            current_app.logger.info(
                "Authorization failed: User lacks root permissions."
            )
            return (
                jsonify(
                    {
                        "message": (
                            "You do not have the necessary permissions "
                            "to perform this action."
                        )
                    }
                ),
                403,
            )

        return decorated_function

    # Project authorization decorator
    def authorize_project_access(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_uuid = g.user_payload.get("user_uuid")
            is_root = g.user_payload.get("is_root")
            project_uuid = kwargs.get("project_uuid")

            if not project_uuid:
                current_app.logger.error(
                    "Authorization failed: Missing project_uuid in request."
                )
                return jsonify({"message": "Project identifier is required."}), 400

            # Allow root users universal access
            if is_root:
                current_app.logger.debug(
                    f"Root access granted for project UUID={project_uuid}."
                )
                return f(*args, **kwargs)

            try:
                # Project-specific access for non-root users
                project_users = fetch_project_users(project_uuid)

                if user_uuid in project_users:
                    current_app.logger.debug(
                        (
                            f"Access granted to user UUID={user_uuid} for project "
                            f"UUID={project_uuid}."
                        )
                    )
                    return f(*args, **kwargs)

                current_app.logger.info(
                    (
                        f"Authorization failed: User UUID={user_uuid} not assigned to "
                        f"project UUID={project_uuid}."
                    )
                )
                return (
                    jsonify(
                        {
                            "message": (
                                "You do not have the necessary permissions to perform "
                                "this action."
                            )
                        }
                    ),
                    403,
                )
            except Exception as e:
                current_app.logger.error(
                    f"Unexpected error during project authorization: {e}", exc_info=True
                )
                return jsonify({"message": "Internal server error."}), 500

        return decorated_function

    # User-specific operation authorization decorator
    def authorize_user(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_uuid_in_path = kwargs.get("user_uuid")
            current_user_uuid = g.user_payload.get("user_uuid")

            if current_user_uuid == user_uuid_in_path:
                current_app.logger.debug(
                    f"Access granted for user UUID={current_user_uuid}."
                )
                return f(*args, **kwargs)

            current_app.logger.info(
                (
                    f"Authorization failed: User UUID={current_user_uuid} attempted to "
                    f"access another user's settings."
                )
            )
            return (
                jsonify(
                    {
                        "message": (
                            "You do not have the necessary permissions to perform "
                            "this action."
                        )
                    }
                ),
                403,
            )

        return decorated_function

    def _get_token(self):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            current_app.logger.warning("Authorization header missing.")
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            current_app.logger.warning("Malformed Authorization header.")
            return None

        return parts[1]
