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
            if current_app.config.get('TESTING'):
                return f(*args, **kwargs)
            token = self._get_token()
            if not token:
                return jsonify({"message": "Token is missing"}), 401
            try:
                g.user_payload = self.token_manager.decode_token(token)
            except jwt.ExpiredSignatureError:
                return jsonify({"status": "error", "message": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"status": "error", "message": "Invalid token"}), 401
            return f(*args, **kwargs)

        return decorated_function

    # Root authorization decorator
    def authorize_root(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_app.config.get('TESTING'):
                return f(*args, **kwargs)
            
            if g.user_payload.get("is_root"):
                return f(*args, **kwargs)
            return jsonify({"message": "Unauthorized"}), 403

        return decorated_function

    # Project authorization decorator
    def authorize_project_access(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_uuid = g.user_payload.get("user_uuid")
            is_root = g.user_payload.get("is_root")

            # Allow root users universal access
            if is_root:
                return f(*args, **kwargs)

            # Project-specific access for non-root users
            project_uuid = kwargs.get("project_uuid")
            project_users = fetch_project_users(project_uuid)

            if project_uuid and user_uuid in project_users:
                return f(*args, **kwargs)
            # TODO: what if project_uuid doesnt exist in db
            return jsonify({"message": "Unauthorized for this project"}), 403

        return decorated_function

    # User-specific operation authorization decorator
    def authorize_user(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_uuid_in_path = kwargs.get("user_uuid")
            if g.user_payload.get("user_uuid") == user_uuid_in_path:
                return f(*args, **kwargs)
            return jsonify({"message": "Unauthorized"}), 403

        return decorated_function

    def _get_token(self):
        auth_header = request.headers.get("Authorization")
        return auth_header.split(" ")[1] if auth_header else None
