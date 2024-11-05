import redis
from app.models import get_user_root_info

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def get_user_root_info_from_cache(user_id):
    is_root = redis_client.get(f"is_root:{user_id}")

    if is_root is not None:
        return is_root == 'True'
    else:
        is_root = get_user_root_info(user_id)

        if is_root is not None:
            redis_client.setex(f"is_root:{user_id}", 900, 'True' if is_root == True else 'False')

        return is_root