import functools
import psycopg2
from psycopg2.extensions import connection, cursor as Cursor
from typing import Any
from app.config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT


def get_db_connection() -> connection:
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
    )


def manage_db_connection(is_write: bool) -> callable:
    """Decorator to manage a read-only database connection."""

    def decorator(f: callable) -> callable:
        @functools.wraps(f)
        def wrapper(*args: tuple, **kwargs: dict) -> Any:
            connection = get_db_connection()
            cursor: Cursor = connection.cursor()
            try:
                kwargs['cursor'] = cursor
                kwargs['connection'] = connection
                return f(*args, **kwargs)
            except Exception as e:
                if is_write:
                    connection.rollback()
                raise e
            finally:
                cursor.close()
                connection.close()
        return wrapper
    return decorator

db_read_connection = manage_db_connection(is_write=False)
db_write_connection = manage_db_connection(is_write=True)
