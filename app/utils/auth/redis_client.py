"""Redis caching utility for root access information.

This module provides a function to retrieve and cache user root access status
in Redis. It checks Redis for the cached data first; if not available, it retrieves
the information from the database and stores it in Redis for future requests.

Functions:
    get_user_root_info_from_cache: Retrieves the root access status of a user from
    the cache or database, caching the result in Redis.
"""

import redis
from typing import Optional
from app.models import get_user_root_info

redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)


def get_user_root_info_from_cache(user_uuid: str) -> Optional[bool]:
    """Retrieves the root access status of a user from Redis cache or the database.

    This function first checks Redis for the root access status of a user. If the
    information is not cached, it queries the database and stores the result in Redis
    with a 15-minute expiration for future requests.

    Args:
        user_uuid (str): The ID of the user whose root access status is being requested.

    Returns:
        Optional[bool]: True if the user has root access, False if not, and None if the
        user information is not found in the database.
    """
    is_root = redis_client.get(f"is_root:{user_uuid}")
    print("cache root", type(is_root))
    if is_root is not None:
        return is_root == "True"
    else:
        is_root = get_user_root_info(user_uuid)

        if is_root is not None:
            redis_client.setex(
                f"is_root:{user_uuid}", 900, "True" if is_root else "False"
            )

        return is_root
