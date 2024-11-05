import jwt
import json
from functools import wraps
from flask import request, jsonify, make_response
from .auth_helpers import refresh_token


class RootAuth:
    def __init__(self, secret_key: str) -> None:
        self.secret_key = secret_key

    def require_root_access(self, f):
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
        refresh_token_response_data = json.loads(
            refresh_token()[0].get_data().decode("utf-8")
        )
        new_access_token = refresh_token_response_data.get("access_token")
        return new_access_token

    def check_root_access(self, new_access_token, f, *args, **kwargs):
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
