"""Database configuration and connection management with pooling."""

import functools
from psycopg2 import pool
from psycopg2.extensions import connection, cursor as Cursor
from typing import Any

connection_pool: pool.ThreadedConnectionPool = None


def init_db_pool(app) -> None:
    """Initialize the connection pool."""
    global connection_pool
    app.logger.debug("Initialising pool")
    if connection_pool is None:
        connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=app.config.get("DB_MAX_CONNECTIONS", 10),
            host=app.config["DB_HOST"],
            database=app.config["DB_NAME"],
            user=app.config["DB_USER"],
            password=app.config["DB_PASSWORD"],
            port=app.config["DB_PORT"],
        )


def get_db_connection_from_pool() -> connection:
    """Retrieve a connection from the pool."""
    global connection_pool
    if connection_pool is None:
        raise RuntimeError("Connection pool is not initialized.")
    return connection_pool.getconn()


def return_db_connection_to_pool(conn: connection) -> None:
    """Return a connection back to the pool."""
    global connection_pool
    if connection_pool:
        connection_pool.putconn(conn)


def close_db_pool() -> None:
    """Close all connections in the pool."""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        connection_pool = None


def manage_db_connection(is_write: bool) -> callable:
    """Creates a decorator to manage a database connection."""

    def decorator(f: callable) -> callable:
        @functools.wraps(f)
        def wrapper(*args: tuple, **kwargs: dict) -> Any:
            connection = get_db_connection_from_pool()
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
                return_db_connection_to_pool(connection)

        return wrapper

    return decorator


db_read_connection = manage_db_connection(is_write=False)
db_write_connection = manage_db_connection(is_write=True)
