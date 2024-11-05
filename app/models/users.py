from typing import List, Dict, Optional, Union
from app.utils import db_read_connection, db_write_connection


@db_read_connection
def fetch_all_users(**kwargs) -> Optional[List[Dict[str, str]]]:
    cursor = kwargs["cursor"]

    query = "SELECT * FROM users;"
    cursor.execute(query)
    rows = cursor.fetchall()

    users = [
        {
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "email": user[3],
            "is_root": user[5],
            "created_at": user[6],
        }
        for user in rows
    ]

    return users if users else None


@db_write_connection
def add_user(
    first_name: str, last_name: str, email: str, password_hash: str, **kwargs
) -> int:
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = """
    INSERT INTO users
    (first_name, last_name, email, password_hash)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """
    cursor.execute(query, (first_name, last_name, email, password_hash))
    user_id = cursor.fetchone()[0]
    connection.commit()

    return user_id


@db_write_connection
def delete_user_by_id(user_id: int, **kwargs) -> bool:
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]
    query = "DELETE FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    rows_deleted = cursor.rowcount
    connection.commit()

    return rows_deleted > 0


@db_write_connection
def update_password(user_id: int, password_hash: str, **kwargs) -> None:
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = """
    UPDATE users
    SET password_hash = %s
    WHERE id = %s
    """

    cursor.execute(query, (password_hash, user_id))
    connection.commit()


@db_read_connection
def fetch_user_by_email(
    email: str, **kwargs
) -> Optional[Dict[str, Union[int, str, bool]]]:
    cursor = kwargs["cursor"]

    query = """
    SELECT
        u.id, u.password_hash, u.is_root
    FROM users u
    WHERE u.email = %s;
    """
    cursor.execute(query, (email,))
    user = cursor.fetchone()

    if user:
        return {
            "id": user[0],
            "password_hash": user[1],
            "is_root": user[2],
        }

    return None


@db_read_connection
def get_user_root_info(user_id, **kwargs):
    cursor = kwargs["cursor"]

    query = """
    SELECT is_root
    FROM users
    WHERE id = %s
    """
    cursor.execute(query, (user_id,))
    is_root = cursor.fetchone()[0]

    return is_root
