import jwt
import datetime
from flask import request
from app.config import SECRET_KEY
from app.models import get_user_root_info


class TokenManager:
    def create_access_token(self, user_uuid, is_root, expires_in=20):
        return jwt.encode(
            {
                "user_uuid": user_uuid,
                "is_root": is_root,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in)
            },
            SECRET_KEY,
            algorithm="HS256",
        )

    def create_refresh_token(self, user_uuid, expires_in=7):
        return jwt.encode(
            {
                "user_uuid": user_uuid,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=expires_in),
            },
            SECRET_KEY,
            algorithm="HS256",
        )

    def decode_token(self, token):
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    def refresh_access_token(self):
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return None, {"status": "error", "message": "No refresh token found"}

        try:
            payload = self.decode_token(refresh_token)
            user_uuid = payload["user_uuid"]
            is_root = get_user_root_info(user_uuid)

            new_access_token = self.create_access_token(user_uuid, is_root)
            return new_access_token, None
        except jwt.ExpiredSignatureError:
            return None, {"status": "error", "message": "Token expired"}
        except jwt.InvalidTokenError:
            return None, {"status": "error", "message": "Invalid token"}
