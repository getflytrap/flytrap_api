"""Project Users models module.

This module provides functions for managing the association between users and projects
in the database. It includes functions to fetch users associated with a project, add a
user to a project, and remove a user from a project. Each function is decorated to
ensure the correct database connection context for reading or writing.
"""

from typing import List
from app.utils import db_read_connection, db_write_connection


@db_read_connection
def fetch_project_users(project_uuid: str, **kwargs: dict) -> List[int]:
    """Retrieves a list of user IDs associated with a specific project."""
    cursor = kwargs["cursor"]

    query = """
    SELECT u.uuid, u.first_name, u.last_name
    FROM users u
    JOIN projects_users pu
    ON u.id = pu.user_id
    JOIN projects p
    ON pu.project_id = p.id
    WHERE p.uuid = %s
    """

    cursor.execute(query, (project_uuid,))
    rows = cursor.fetchall()

    users = [
        {"uuid": row[0], "first_name": row[1], "last_name": row[2]} for row in rows
    ]

    return users


@db_write_connection
def add_user_to_project(project_uuid: str, user_uuid: str, **kwargs: dict) -> None:
    """Adds a user to a specified project."""
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = """
    INSERT INTO projects_users (project_id, user_id)
    SELECT p.id, u.id
    FROM projects p, users u
    WHERE p.uuid = %s AND u.uuid = %s
    """

    cursor.execute(query, (project_uuid, user_uuid))
    connection.commit()


@db_write_connection
def remove_user_from_project(project_uuid: str, user_uuid: str, **kwargs: dict) -> bool:
    """Removes a user from a specified project."""
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = """
    DELETE FROM projects_users
    WHERE project_id = (
        SELECT p.id
        FROM projects p
        WHERE p.uuid = %s
    )
    AND user_id = (
        SELECT u.id
        FROM users u
        WHERE u.uuid = %s
    )
    """

    cursor.execute(
        query,
        (
            project_uuid,
            user_uuid,
        ),
    )
    connection.commit()
    return cursor.rowcount > 0
