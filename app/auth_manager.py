from app.config import secret_key
from app.utils.auth import JWTAuth

jwt_auth = JWTAuth(secret_key=secret_key)
