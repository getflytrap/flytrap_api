"""Project Issues models module.

This module contains functions to interact with the database for project-specific
issues, including error and rejection logs. It allows fetching combined logs, updating
resolution status, and deleting records. Each function is decorated to ensure proper
database connection context for reading or writing.

Functions:
    fetch_issues_by_project: Retrieves paginated issues (errors and rejections) for a
    project.
    delete_issues_by_project: Deletes all issues (errors and rejections) associated with
    a project.
    fetch_error: Retrieves a specific error log by its ID.
    fetch_rejection: Retrieves a specific rejection log by its ID.
    update_error_resolved: Updates the resolved state of an error log.
    update_rejection_resolved: Updates the resolved state of a rejection log.
    delete_error_by_id: Deletes a specific error log by its ID.
    delete_rejection_by_id: Deletes a specific rejection log by its ID.
"""

from typing import Dict, Optional, List
from app.utils import (
    db_read_connection,
    db_write_connection,
    fetch_errors_by_project,
    fetch_rejections_by_project,
    calculate_total_error_pages,
)


@db_read_connection
def fetch_issues_by_project(
    project_uuid: str,
    page: int,
    limit: int,
    handled: Optional[bool],
    time: Optional[str],
    resolved: Optional[bool],
    **kwargs: dict
) -> Dict[str, List[Dict[str, int]]]:
    """Retrieves a paginated list of issues (errors and rejections) for a project.

    Args:
        project_uuid (str): The project uuid.
        page (int): The page number for pagination.
        limit (int): The number of items per page.
        handled (Optional[bool]): Filter for handled issues.
        time (Optional[str]): Filter by time (e.g., recent).
        resolved (Optional[bool]): Filter for resolved issues.

    Returns:
        Dict[str, List[Dict[str, int]]]: Dictionary containing combined logs, total
        pages, and current page.
    """
    cursor = kwargs["cursor"]

    errors = fetch_errors_by_project(cursor, project_uuid, page, limit, handled, time, resolved)
    rejections = fetch_rejections_by_project(
        cursor, project_uuid, page, limit, handled, time, resolved
    )

    combined_logs = sorted(
        errors + rejections, key=lambda x: x["created_at"], reverse=True
    )
    total_pages = calculate_total_error_pages(cursor, project_uuid, limit)

    return {
        "issues": combined_logs[:limit],
        "total_pages": total_pages,
        "current_page": int(page),
    }


@db_write_connection
def delete_issues_by_project(project_uuid: str, **kwargs: dict) -> bool:
    """Deletes all issues (errors and rejections) associated with a specified project.

    Args:
        project_uuid (str): The project uuid.

    Returns:
        bool: True if any issues were deleted, False otherwise.
    """
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = """
    DELETE FROM error_logs
    WHERE project_id IN (SELECT id FROM projects WHERE uuid = %s)
    """
    cursor.execute(query, (project_uuid,))
    error_rows_deleted = cursor.rowcount

    rejection_query = """
    DELETE FROM rejection_logs
    WHERE project_id IN (SELECT id FROM projects WHERE uuid = %s)
    """
    cursor.execute(rejection_query, (project_uuid,))
    rejection_rows_deleted = cursor.rowcount

    connection.commit()

    return error_rows_deleted > 0 or rejection_rows_deleted > 0


@db_read_connection
def fetch_error(project_uuid: str, error_uuid: str, **kwargs: dict) -> Optional[Dict[str, str]]:
    """Retrieves a specific error log by its UUID.

    Args:
        project_uuid (str): The project uuid.
        error_uuid (str): The error uuid.

    Returns:
        Optional[Dict[str, str]]: Dictionary containing error log details if found, or
        None if not found.
    """
    cursor = kwargs["cursor"]

    query = "SELECT name, message, created_at, line_number, col_number, stack_trace, handled, resolved FROM error_logs WHERE uuid = %s"
    cursor.execute(query, [error_uuid])
    error = cursor.fetchone()

    if error:
        return {
            "uuid": error_uuid,
            "name": error[0],
            "message": error[1],
            "created_at": error[2],
            "line_number": error[3],
            "col_number": error[4],
            "project_uuid": project_uuid,
            "stack_trace": error[5],
            "handled": error[6],
            "resolved": error[7],
        }

    return None


@db_read_connection
def fetch_rejection(project_uuid: str, rejection_uuid: int, **kwargs: dict) -> Optional[Dict[str, str]]:
    """Retrieves a specific rejection log by its UUID.

    Args:
        project_uuid (str): The project uuid.
        rejection_uuid (str): The rejection uuid.

    Returns:
        Optional[Dict[str, str]]: Dictionary containing rejection log details if found,
        or None if not found.
    """
    cursor = kwargs["cursor"]
    query = "SELECT value, created_at, handled, resolved FROM rejection_logs WHERE uuid = %s"
    cursor.execute(query, [rejection_uuid])
    rejection = cursor.fetchone()

    if rejection:
        return {
            "uuid": rejection_uuid,
            "value": rejection[0],
            "created_at": rejection[1],
            "project_id": project_uuid,
            "handled": rejection[2],
            "resolved": rejection[3],
        }

    return None


@db_write_connection
def update_error_resolved(error_uuid: str, new_resolved_state: bool, **kwargs: dict) -> bool:
    """Updates the resolved state of a specific error log.

    Args:
        error_uuid (str): The error uuid.
        new_resolved_state (bool): The new resolved state.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]
    query = "UPDATE error_logs SET resolved = %s WHERE uuid = %s"
    cursor.execute(query, [new_resolved_state, error_uuid])
    rows_updated = cursor.rowcount
    connection.commit()

    return rows_updated > 0


@db_write_connection
def update_rejection_resolved(
    rejection_uuid: int, new_resolved_state: bool, **kwargs: dict
) -> bool:
    """Updates the resolved state of a specific rejection log.

    Args:
        rejection_uuid (str): The rejection uuid.
        new_resolved_state (bool): The new resolved state.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]
    query = "UPDATE rejection_logs SET resolved = %s WHERE uuid = %s"
    cursor.execute(query, [new_resolved_state, rejection_uuid])
    rows_updated = cursor.rowcount
    connection.commit()

    return rows_updated > 0


@db_write_connection
def delete_error_by_id(eid: int, **kwargs: dict) -> bool:
    """Deletes a specific error log by its ID.

    Args:
        eid (int): The error log ID.

    Returns:
        bool: True if the error log was deleted, False otherwise.
    """
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]
    query = "DELETE FROM error_logs WHERE id = %s"
    cursor.execute(query, [eid])
    rows_deleted = cursor.rowcount
    connection.commit()

    return rows_deleted > 0


@db_write_connection
def delete_rejection_by_id(rid: int, **kwargs: dict) -> bool:
    """Deletes a specific rejection log by its ID.

    Args:
        rid (int): The rejection log ID.

    Returns:
        bool: True if the rejection log was deleted, False otherwise.
    """

    connection = kwargs["connection"]
    cursor = kwargs["cursor"]
    query = "DELETE FROM rejection_logs WHERE id = %s"
    cursor.execute(query, [rid])
    rows_deleted = cursor.rowcount
    connection.commit()

    return rows_deleted > 0
