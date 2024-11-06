from app.config import secret_key
from app.utils.auth import JWTAuth, RootAuth

jwt_auth = JWTAuth(secret_key=secret_key)
root_auth = RootAuth(secret_key=secret_key)
