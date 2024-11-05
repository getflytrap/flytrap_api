from typing import List
from app.utils import db_read_connection, db_write_connection

@db_read_connection
def fetch_project_users(pid: int, **kwargs: dict) -> List[int]:
    cursor = kwargs['cursor']

    query = """
    SELECT pu.user_id
    FROM projects_users pu
    JOIN projects p
    ON pu.project_id = p.id
    WHERE p.pid = %s
    """

    cursor.execute(query, (pid,))
    user_ids = cursor.fetchall()

    return [user_id[0] for user_id in user_ids] if user_ids else []

@db_write_connection
def add_user_to_project(pid: int, user_id: int, **kwargs: dict) -> None:
    connection = kwargs['connection']
    cursor = kwargs['cursor']

    query = """
    INSERT INTO projects_users (project_id, user_id)
    SELECT p.id, %s
    FROM projects p
    WHERE p.pid = %s
    RETURNING id
    """

    cursor.execute(query, (user_id, pid))
    connection.commit()

@db_write_connection
def remove_user_from_project(project_pid: int, user_id: int, **kwargs: dict) -> bool:
    connection = kwargs['connection']
    cursor = kwargs['cursor']

    query = """
    DELETE FROM projects_users
    WHERE project_id = (
        SELECT p.id
        FROM projects p
        WHERE p.pid = %s
    )
    AND user_id = %s
    """

    cursor.execute(
        query,
        (
            project_pid,
            user_id,
        ),
    )
    connection.commit()
    return cursor.rowcount > 0
