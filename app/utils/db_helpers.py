"""Database helper functions for projects and logs."""

import math
from typing import Optional, List, Dict
from psycopg2.extensions import cursor as Cursor


def calculate_total_project_pages(cursor: Cursor, limit: int) -> int:
    """Calculates the total number of pages for a paginated list of projects."""
    if not limit:
        return 1

    query = "SELECT COUNT(DISTINCT p.id) FROM projects p;"
    cursor.execute(query)
    total_count = cursor.fetchone()[0]
    total_pages = math.ceil(total_count / limit)

    return total_pages


def calculate_total_user_project_pages(
    cursor: Cursor, user_uuid: int, limit: int
) -> int:
    """Calculates the total number of pages for a paginated list of projects
    a certain user is assigned to."""

    query = """
    SELECT COUNT(DISTINCT p.id)
    FROM projects p
    JOIN projects_users pu ON p.id = pu.project_id
    JOIN users u ON pu.user_id = u.id
    WHERE u.uuid = %s;
    """
    cursor.execute(query, (user_uuid,))
    total_count = cursor.fetchone()[0]
    total_pages = math.ceil(total_count / limit)

    return total_pages


def fetch_errors_by_project(
    cursor: Cursor,
    project_uuid: str,
    page: int,
    limit: int,
    handled: Optional[bool],
    time: Optional[str],
    resolved: Optional[bool],
) -> List[Dict[str, int]]:
    """Retrieves error logs for a specific project, with optional filters and
    pagination."""

    # Base query
    query = """
    SELECT
        e.uuid, e.name, e.message, e.created_at, e.line_number,
        e.col_number, e.handled, e.resolved
    FROM error_logs e
    JOIN projects p ON e.project_id = p.id
    WHERE p.uuid = %s
    """

    params = [project_uuid]

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
    errors = [
        {
            "uuid": row[0],
            "name": row[1],
            "message": row[2],
            "created_at": row[3],
            "line_number": row[4],
            "col_number": row[5],
            "project_uuid": project_uuid,
            "handled": row[6],
            "resolved": row[7],
            # TODO: add a type property to distinguish between errors and rejections?
        }
        for row in rows
    ]

    return errors


def fetch_rejections_by_project(
    cursor: Cursor,
    project_uuid: str,
    page: int,
    limit: int,
    handled: Optional[bool],
    time: Optional[str],
    resolved: Optional[bool],
) -> List[Dict[str, int]]:
    """Retrieves rejection logs for a specific project, with optional filters and
    pagination."""

    # Base query
    query = """
    SELECT
        r.uuid, r.value, r.created_at, r.handled, r.resolved
    FROM rejection_logs r
    JOIN projects p ON r.project_id = p.id
    WHERE p.uuid = %s
    """

    params = [project_uuid]

    # Add optional filters to query
    if handled is not None:
        query += " AND r.handled = %s"
        params.append(handled)
    if resolved is not None:
        query += " AND r.resolved = %s"
        params.append(resolved)
    if time is not None:
        query += " AND r.created_at >= %s"
        params.append(time)

    # Add sorting and pagination
    offset = (page - 1) * limit
    query += " ORDER BY r.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    rejections = [
        {
            "uuid": row[0],
            "value": row[1],
            "created_at": row[2],
            "project_uuid": project_uuid,
            "handled": row[3],
            "resolved": row[4],
        }
        for row in rows
    ]

    return rejections


def calculate_total_error_pages(
    cursor: Cursor,
    project_uuid: str,
    limit: int,
    handled: Optional[bool],
    time: Optional[str],
    resolved: Optional[bool],
) -> int:
    """Calculates the total pages for combined error & rejection logs for a project."""
    error_count_query = """
    SELECT COUNT(*) FROM error_logs e
    JOIN projects p ON e.project_id = p.id
    WHERE p.uuid = %s
    """

    params = [project_uuid]

    if handled is not None:
        error_count_query += " AND e.handled = %s"
        params.append(handled)
    if resolved is not None:
        error_count_query += " AND e.resolved = %s"
        params.append(resolved)
    if time is not None:
        error_count_query += " AND e.created_at >= %s"
        params.append(time)

    cursor.execute(error_count_query, params)
    error_count = cursor.fetchone()[0]

    rejection_count_query = """
    SELECT COUNT(*)
    FROM rejection_logs r
    JOIN projects p ON r.project_id = p.id
    WHERE p.uuid = %s
    """

    params = [project_uuid]

    # Add filters to the rejection count query
    if handled is not None:
        rejection_count_query += " AND r.handled = %s"
        params.append(handled)
    if resolved is not None:
        rejection_count_query += " AND r.resolved = %s"
        params.append(resolved)
    if time is not None:
        rejection_count_query += " AND r.created_at >= %s"
        params.append(time)

    cursor.execute(rejection_count_query, params)
    rejection_count = cursor.fetchone()[0]

    total_count = error_count + rejection_count
    total_pages = math.ceil(total_count / limit)

    return total_pages
