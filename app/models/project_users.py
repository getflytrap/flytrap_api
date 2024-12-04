"""Project Users models module.

This module provides functions for managing the association between users and projects
in the database. It includes functions to fetch users associated with a project, add a
user to a project, and remove a user from a project. Each function is decorated to
ensure the correct database connection context for reading or writing.
"""

from typing import List
from db import db_read_connection, db_write_connection


@db_read_connection
def fetch_project_users(project_uuid: str, **kwargs: dict) -> List[int]:
    """Retrieves a list of user UUIDs associated with a specific project."""
    cursor = kwargs["cursor"]

    query = """
    SELECT u.uuid
    FROM users u
    JOIN projects_users pu
    ON u.id = pu.user_id
    JOIN projects p
    ON pu.project_id = p.id
    WHERE p.uuid = %s
    """

    cursor.execute(query, (project_uuid,))
    rows = cursor.fetchall()

    users = [row[0] for row in rows]

    return users


@db_write_connection
def add_user_to_project(project_uuid: str, user_uuid: str, **kwargs: dict) -> None:
    """Adds a user to a specified project."""
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    # Check if the project exists
    project_query = "SELECT id FROM projects WHERE uuid = %s"

    cursor.execute(project_query, [project_uuid])
    project = cursor.fetchone()

    if not project:
        raise ValueError(f"Project with UUID={project_uuid} does not exist.")

    project_id = project[0]

    # Check if the user exists
    user_query = "SELECT id FROM users WHERE uuid = %s"

    cursor.execute(user_query, [user_uuid])
    user = cursor.fetchone()

    if not user:
        raise ValueError(f"User with UUID={user_uuid} does not exist.")

    user_id = user[0]

    # Check if the user is already associated with the project
    association_query = """
    SELECT 1
    FROM projects_users
    WHERE project_id = %s AND user_id = %s
    """

    cursor.execute(association_query, [project_id, user_id])
    if cursor.fetchone():
        return False  # Indicate that the user was already added

    # Add the user to the project
    insert_query = """
    INSERT INTO projects_users (project_id, user_id)
    VALUES (%s, %s)
    """

    cursor.execute(insert_query, [project_id, user_id])
    connection.commit()

    return True  # Indicate that the user was successfully added


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


@db_write_connection
def save_sns_subscription_arn_to_db(
    user_uuid: str, project_uuid: str, arn: str, **kwargs
) -> None:
    """Update project_users record by adding a sns subscription arn"""

    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = """
    UPDATE projects_users
    SET sns_subscription_arn = %s
    WHERE user_id = (
        SELECT id FROM users WHERE uuid = %s
    )
    AND project_id = (
        SELECT id FROM projects WHERE uuid = %s
    )
    """

    cursor.execute(query, [arn, user_uuid, project_uuid])
    connection.commit()
