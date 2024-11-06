"""Database configuration and connection management.

This module provides utilities for managing PostgreSQL database connections, including
functions to establish connections and decorators to handle read-only and write database
operations. The decorators automatically manage connections and handle transactions
for both read and write queries.

Functions:
    get_db_connection: Establishes a new database connection.
    manage_db_connection: Creates decorators to manage read-only or write database
    connections.

Decorators:
    db_read_connection: Decorator for read-only database operations.
    db_write_connection: Decorator for write database operations with transaction
    handling.
"""

import functools
import psycopg2
from psycopg2.extensions import connection, cursor as Cursor
from typing import Any
from app.config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT


def get_db_connection() -> connection:
    """Establishes and returns a new connection to the PostgreSQL database.

    Uses configuration variables from `app.config` to connect to the specified
    database.

    Returns:
        connection: A new connection object for the PostgreSQL database.
    """
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
    )


def manage_db_connection(is_write: bool) -> callable:
    """Creates a decorator to manage a database connection.

    This decorator handles the connection and cursor lifecycle for database queries.
    It provides transaction management, rolling back on exceptions if `is_write` is
    True.

    Args:
        is_write (bool): If True, enables transaction handling for write operations.

    Returns:
        callable: A decorator function for managing database connections.
    """

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
