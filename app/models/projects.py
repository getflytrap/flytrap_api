"""Projects models module.

This module provides functions for managing projects in the database, including
fetching a paginated list of projects with associated issues, adding a new project,
deleting a project, and updating a project’s name. Each function is decorated to ensure
the correct database connection context for reading or writing.

Functions:
    fetch_projects: Retrieves a paginated list of projects with issue counts.
    add_project: Adds a new project with a unique project ID.
    delete_project_by_id: Deletes a project by its unique project ID.
    update_project_name: Updates the name of a project by its unique project ID.
"""

from typing import List, Dict, Union
from app.utils import (
    db_read_connection,
    db_write_connection,
    calculate_total_project_pages,
    generate_uuid,
)


@db_read_connection
def fetch_projects(
    page: int, limit: int, **kwargs
) -> Dict[str, Union[List[Dict[str, Union[int, str]]], int]]:
    """Retrieves a paginated list of projects with the count of associated issues.

    Args:
        page (int): The page number for pagination.
        limit (int): The number of projects per page.

    Returns:
        Dict[str, Union[List[Dict[str, Union[int, str]]], int]]: A dictionary containing
        the list of projects with issue counts, the total number of pages, and the
        current page.
    """
    cursor = kwargs["cursor"]
    offset = (page - 1) * limit if limit else 0

    query = """
    SELECT
        p.uuid,
        p.name,
        COUNT(DISTINCT e.id) AS error_count,
        COUNT(DISTINCT r.id) AS rejection_count
    FROM
        projects p
    LEFT JOIN
        error_logs e ON e.project_id = p.id
    LEFT JOIN
        rejection_logs r ON r.project_id = p.id
    GROUP BY
        p.uuid, p.name
    ORDER BY p.name
    LIMIT %s OFFSET %s
    """
    cursor.execute(query, [limit, offset])
    rows = cursor.fetchall()

    projects = [
        {
            "uuid": row[0],
            "name": row[1],
            "issue_count": row[2] + row[3],
        }
        for row in rows
    ]

    total_pages = calculate_total_project_pages(cursor, limit)

    return {
        "projects": projects,
        "total_pages": total_pages,
        "current_page": int(page),
    }


@db_write_connection
def add_project(name: str, **kwargs) -> None:
    """Adds a new project with a specified unique ID and name.

    Args:
        name (str): The name of the project.

    Returns:
        None
    """
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    uuid = generate_uuid()

    query = "INSERT INTO projects (uuid, name) VALUES (%s, %s)"
    cursor.execute(query, [uuid, name])
    connection.commit()

    return uuid


@db_write_connection
def delete_project_by_id(uuid: str, **kwargs) -> bool:
    """Deletes a project by its unique project UUID.

    Args:
        uuid (str): The unique project uuid.

    Returns:
        bool: True if the project was deleted, False otherwise.
    """
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = "DELETE FROM projects WHERE uuid = %s"
    cursor.execute(query, [uuid])
    rows_deleted = cursor.rowcount
    connection.commit()

    return rows_deleted > 0


@db_write_connection
def update_project_name(uuid: str, new_name: str, **kwargs) -> bool:
    """Updates the name of a project by its unique project UUID.

    Args:
        uuid (int): The unique project uuid.
        new_name (str): The new name for the project.

    Returns:
        bool: True if the project name was updated, False otherwise.
    """
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = "UPDATE projects SET name = %s WHERE uuid = %s"

    cursor.execute(query, [new_name, uuid])
    rows_updated = cursor.rowcount
    connection.commit()

    return rows_updated > 0
