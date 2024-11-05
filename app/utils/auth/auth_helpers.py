import jwt
from flask import request, jsonify
import datetime
from .redis_client import get_user_root_info_from_cache

def refresh_token():
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        return jsonify({"message": "Token is missing!"}), 401
    try:
        decoded_refresh_token = jwt.decode(refresh_token, 'SECRET', algorithms=["HS256"])
        user_id = decoded_refresh_token.get('user_id')
        is_root = get_user_root_info_from_cache(user_id)

        access_token = jwt.encode(
            {'user_id': user_id, 'is_root': is_root, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)},
            'SECRET', algorithm='HS256'
        )

        return jsonify({"access_token": access_token}), 200
    except jwt.ExpiredSignatureError:
        # the frontend should handle these responses by redirecting to the login view
        return jsonify({"message": "Token expired. Please log in again."}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"message": "Invalid token"}), 401
    except Exception as e:
        raise e