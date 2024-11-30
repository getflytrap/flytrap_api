"""Projects models module.

This module provides functions for managing projects in the database, including
fetching a paginated list of projects with associated issues, adding a new project,
deleting a project, and updating a project's name. Each function is decorated to ensure
the correct database connection context for reading or writing.
"""

from flask import current_app
from typing import List, Dict, Union, Optional
from app.utils import (
    db_read_connection,
    db_write_connection,
    calculate_total_project_pages,
)


@db_read_connection
def fetch_projects(
    page: int, limit: int, **kwargs
) -> Dict[str, Union[List[Dict[str, Union[int, str]]], int]]:
    """Retrieves a paginated list of projects with the count of associated issues."""
    cursor = kwargs["cursor"]
    offset = (page - 1) * limit if limit else 0

    query = """
    SELECT
        p.uuid,
        p.name,
        p.api_key,
        p.platform,
        COUNT(DISTINCT e.id) AS error_count,
        COUNT(DISTINCT r.id) AS rejection_count
    FROM
        projects p
    LEFT JOIN
        error_logs e ON e.project_id = p.id
    LEFT JOIN
        rejection_logs r ON r.project_id = p.id
    GROUP BY
        p.uuid, p.name, p.api_key, p.platform
    ORDER BY p.name
    LIMIT %s OFFSET %s
    """

    current_app.logger.debug(f"Executing query: {query}")
    cursor.execute(query, [limit, offset])
    rows = cursor.fetchall()

    if not rows:
        current_app.logger.info("No projects found for the given page and limit.")
    
    projects = [
        {
            "uuid": row[0],
            "name": row[1],
            "api_key": row[2],
            "platform": row[3],
            "issue_count": row[4] + row[5],
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
def add_project(
    name: str, project_uuid: str, api_key: str, platform: str, topic_arn: str, **kwargs
) -> None:
    """Adds a new project with a specified unique ID and name."""
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = """
    INSERT INTO
        projects (uuid, name, api_key, platform, sns_topic_arn)
    VALUES
        (%s, %s, %s, %s, %s)
    """

    current_app.logger.debug(f"Executing query: {query}")
    cursor.execute(query, [project_uuid, name, api_key, platform, topic_arn])
    connection.commit()


@db_write_connection
def delete_project_by_id(project_uuid: str, **kwargs) -> bool:
    """Deletes a project by its unique project UUID, and returns the api_key"""
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = "DELETE FROM projects WHERE uuid = %s RETURNING api_key"

    current_app.logger.debug(f"Executing query: {query}")
    cursor.execute(query, [project_uuid])
    result = cursor.fetchone()[0]
    connection.commit()

    if result:
        return result[0]
    else:
        return None


@db_write_connection
def update_project_name(uuid: str, new_name: str, **kwargs) -> bool:
    """Updates the name of a project by its unique project UUID."""
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = "UPDATE projects SET name = %s WHERE uuid = %s"

    current_app.logger.debug(f"Executing query: {query}")
    cursor.execute(query, [new_name, uuid])
    rows_updated = cursor.rowcount
    connection.commit()

    return rows_updated > 0


@db_read_connection
def get_project_name(uuid: str, **kwargs) -> Optional[str]:
    """Gets the name of a project given its unique UUId."""
    cursor = kwargs["cursor"]

    query = "SELECT name FROM projects WHERE uuid = %s"

    current_app.logger.debug(f"Executing query: {query}")
    cursor.execute(query, [uuid])
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        return None


@db_read_connection
def get_topic_arn(project_uuid: str, **kwargs) -> Optional[str]:
    """Retrieves the SNS topic arn associated with a project"""
    cursor = kwargs["cursor"]

    query = "SELECT sns_topic_arn FROM projects WHERE uuid = %s"
    
    current_app.logger.debug(f"Executing query: {query}")
    cursor.execute(query, [project_uuid])
    result = cursor.fetchone()

    if result:
        result[0]
    else:
        return None


@db_read_connection
def get_all_sns_subscription_arns_for_project(project_uuid: str, **kwargs) -> list:
    """return a list of sns subscriptions ARNs associated with a project"""
    cursor = kwargs["cursor"]

    query = """
    SELECT sns_subscription_arn
    FROM projects_users
    WHERE project_id = (SELECT id FROM projects WHERE uuid = %s)
    """

    current_app.logger.debug(f"Executing query: {query}")
    cursor.execute(query, [project_uuid])
    rows = cursor.fetchall()

    return [row[0] for row in rows]
