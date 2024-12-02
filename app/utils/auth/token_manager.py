import jwt
import datetime
from flask import request, current_app
from app.models import user_is_root


class TokenManager:
    def create_access_token(self, user_uuid, is_root, expires_in=20):
        token_payload = {
            "user_uuid": user_uuid,
            "is_root": is_root,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in),
        }

        token = jwt.encode(
            token_payload,
            current_app.config["JWT_SECRET_KEY"],
            algorithm="HS256",
        )
        current_app.logger.debug(f"Access token created for user_uuid={user_uuid}.")
        return token

    def create_refresh_token(self, user_uuid, expires_in=7):
        token_payload = {
            "user_uuid": user_uuid,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=expires_in),
        }

        token = jwt.encode(
            token_payload,
            current_app.config["JWT_SECRET_KEY"],
            algorithm="HS256",
        )
        current_app.logger.debug(f"Refresh token created for user_uuid={user_uuid}.")
        return token

    def decode_token(self, token):
        payload = jwt.decode(
            token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
        )
        current_app.logger.debug("Token decoded successfully.")
        return payload

    def refresh_access_token(self):
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            current_app.logger.info("Missing refresh token.")
            return None, {"message": "Authentication required. Please log in."}

        try:
            payload = self.decode_token(refresh_token)
            user_uuid = payload["user_uuid"]
            is_root = user_is_root(user_uuid)

            new_access_token = self.create_access_token(user_uuid, is_root)
            return new_access_token, None
        except jwt.ExpiredSignatureError:
            current_app.logger.info("Refresh token expired.")
            return None, {"message": "Session expired. Please log in again."}
        except jwt.InvalidTokenError:
            current_app.logger.info("Invalid refresh token.")
            return None, {"message": "Invalid session. Please log in again."}
