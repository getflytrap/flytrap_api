"""Database helper functions for projects and logs.

This module provides utility functions to assist with database operations,
including calculating pagination for projects, retrieving error and rejection logs with
filtering options, and calculating total pages for error logs. These functions
streamline data retrieval and pagination for project-specific information in the
database.

Functions:
    calculate_total_project_pages: Calculates the total number of pages for paginated
    project lists.
    fetch_errors_by_project: Retrieves error logs for a project with optional filters
    and pagination.
    fetch_rejections_by_project: Retrieves rejection logs for a project with optional
    filters and pagination.
    calculate_total_error_pages: Calculates the total pages for combined error and
    rejection logs for a project.
"""

import math
from typing import Optional, List, Dict
from psycopg2.extensions import cursor as Cursor


def calculate_total_project_pages(cursor: Cursor, limit: int) -> int:
    """Calculates the total number of pages for a paginated list of projects.

    Args:
        cursor (Cursor): The database cursor for executing SQL queries.
        limit (int): The number of projects per page.

    Returns:
        int: The total number of pages required to display all projects.
    """
    if not limit:
        return 1

    query = "SELECT COUNT(DISTINCT p.id) FROM projects p;"
    cursor.execute(query)
    total_count = cursor.fetchone()[0]
    total_pages = math.ceil(total_count / limit)

    return total_pages


def fetch_errors_by_project(
    cursor: Cursor,
    pid: int,
    page: int,
    limit: int,
    handled: Optional[bool],
    time: Optional[str],
    resolved: Optional[bool],
) -> List[Dict[str, int]]:
    """Retrieves error logs for a specific project, with optional filters and
    pagination.

    Args:
        cursor (Cursor): The database cursor for executing SQL queries.
        pid (int): The project ID.
        page (int): The page number for pagination.
        limit (int): The number of items per page.
        handled (Optional[bool]): Filter for handled errors.
        time (Optional[str]): Filter by time (e.g., recent).
        resolved (Optional[bool]): Filter for resolved errors.

    Returns:
        List[Dict[str, int]]: A list of dictionaries containing error log details.
    """

    # Base query
    query = """
    SELECT
        e.id, e.name, e.message, e.created_at, e.line_number,
        e.col_number, e.project_id, e.handled, e.resolved
    FROM error_logs e
    JOIN projects p ON e.project_id = p.id
    WHERE p.pid = %s
    """

    params = [pid]

    # Add optional filters to query
    if handled is not None:
        query += " AND e.handled = %s"
        params.append(handled)
    if resolved is not None:
        query += " AND e.resolved = %s"
        params.append(resolved)
    if time is not None:
        query += " AND e.created_at >= %s"
        params.append(time)

    # Add sorting and pagination
    offset = (page - 1) * limit
    query += " ORDER BY e.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()

    errors = [
        {
            "error_id": row[0],
            "name": row[1],
            "message": row[2],
            "created_at": row[3],
            "line_number": row[4],
            "col_number": row[5],
            "project_id": row[6],
            "handled": row[7],
            "resolved": row[8],
        }
        for row in rows
    ]

    return errors if errors else []


def fetch_rejections_by_project(
    cursor: Cursor,
    pid: int,
    page: int,
    limit: int,
    handled: Optional[bool],
    time: Optional[str],
    resolved: Optional[bool],
) -> List[Dict[str, int]]:
    """Retrieves rejection logs for a specific project, with optional filters and
    pagination.

    Args:
        cursor (Cursor): The database cursor for executing SQL queries.
        pid (int): The project ID.
        page (int): The page number for pagination.
        limit (int): The number of items per page.
        handled (Optional[bool]): Filter for handled rejections.
        time (Optional[str]): Filter by time (e.g., recent).
        resolved (Optional[bool]): Filter for resolved rejections.

    Returns:
        List[Dict[str, int]]: A list of dictionaries containing rejection log details.
    """

    # Base query
    query = """
    SELECT
        r.id, r.value, r.created_at, r.project_id, r.handled, r.resolved
    FROM rejection_logs r
    JOIN projects p ON r.project_id = p.id
    WHERE p.pid = %s
    """

    params = [pid]

    # Add optional filters to query
    if handled is not None:
        query += " AND r.handled = %s"
        params.append(handled)
    if resolved is not None:
        query += " AND r.resolved = %s"
        params.append(resolved)
    if time is not None:
        query += "AND r.created_at >= %s"
        query += " AND r.created_at >= %s"
        params.append(time)

    # Add sorting and pagination
    offset = (page - 1) * limit
    query += " ORDER BY r.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()

    rejections = [
        {
            "rejection_id": row[0],
            "value": row[1],
            "created_at": row[2],
            "pid": row[3],
            "handled": row[4],
            "resolved": row[5],
        }
        for row in rows
    ]

    return rejections if rejections else []


def calculate_total_error_pages(cursor: Cursor, pid: int, limit: int):
    """Calculates the total pages for combined error and rejection logs for a project.

    Args:
        cursor (Cursor): The database cursor for executing SQL queries.
        pid (int): The project ID.
        limit (int): The number of items per page.

    Returns:
        int: The total number of pages required to display all error and rejection logs.
    """
    error_count_query = """
    SELECT COUNT(*) FROM error_logs e
    JOIN projects p ON e.project_id = p.id
    WHERE p.pid = %s"
    """
    cursor.execute(error_count_query, [pid])
    error_count = cursor.fetchone()[0]

    rejection_count_query = """
    SELECT COUNT(*)
    FROM rejection_logs r
    JOIN projects p ON r.project_id = p.id
    WHERE p.pid = %s
    """
    cursor.execute(rejection_count_query, [pid])
    rejection_count = cursor.fetchone()[0]

    total_count = error_count + rejection_count
    total_pages = math.ceil(total_count / limit)

    cursor.close()
    return total_pages
