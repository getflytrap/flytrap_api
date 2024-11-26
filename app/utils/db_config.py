"""Database configuration and connection management."""

import functools
import psycopg2
from psycopg2.extensions import connection, cursor as Cursor
from flask import current_app
from typing import Any



def get_db_connection() -> connection:
    """Establishes and returns a new connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=current_app.config["DB_HOST"], database=current_app.config["DB_NAME"], user=current_app.config["DB_USER"], password=current_app.config["DB_PASSWORD"], port=current_app.config["DB_PORT"]
    )


def manage_db_connection(is_write: bool) -> callable:
    """Creates a decorator to manage a database connection."""

    def decorator(f: callable) -> callable:
        @functools.wraps(f)
        def wrapper(*args: tuple, **kwargs: dict) -> Any:
            connection = get_db_connection()
            cursor: Cursor = connection.cursor()
            try:
                kwargs["cursor"] = cursor
                kwargs["connection"] = connection
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
