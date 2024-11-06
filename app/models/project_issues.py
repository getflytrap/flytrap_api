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
    pid: int,
    page: int,
    limit: int,
    handled: Optional[bool],
    time: Optional[str],
    resolved: Optional[bool],
    **kwargs: dict
) -> Dict[str, List[Dict[str, int]]]:
    """Retrieves a paginated list of issues (errors and rejections) for a project.

    Args:
        pid (int): The project ID.
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

    errors = fetch_errors_by_project(cursor, pid, page, limit, handled, time, resolved)
    rejections = fetch_rejections_by_project(
        cursor, pid, page, limit, handled, time, resolved
    )

    combined_logs = sorted(
        errors + rejections, key=lambda x: x["created_at"], reverse=True
    )
    total_pages = calculate_total_error_pages(cursor, pid, limit)

    return {
        "errors": combined_logs[:limit],
        "total_pages": total_pages,
        "current_page": int(page),
    }


@db_write_connection
def delete_issues_by_project(pid: int, **kwargs: dict) -> bool:
    """Deletes all issues (errors and rejections) associated with a specified project.

    Args:
        pid (int): The project ID.

    Returns:
        bool: True if any issues were deleted, False otherwise.
    """
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]

    query = """
    DELETE FROM error_logs
    WHERE project_id IN (SELECT id FROM projects WHERE pid = %s)
    """
    cursor.execute(query, (pid,))
    error_rows_deleted = cursor.rowcount

    rejection_query = """
    DELETE FROM rejection_logs 
    WHERE project_id IN (SELECT id FROM projects WHERE pid = %s)
    """
    cursor.execute(rejection_query, (pid,))
    rejection_rows_deleted = cursor.rowcount

    connection.commit()

    return error_rows_deleted > 0 or rejection_rows_deleted > 0


@db_read_connection
def fetch_error(eid: int, **kwargs: dict) -> Optional[Dict[str, str]]:
    """Retrieves a specific error log by its ID.

    Args:
        eid (int): The error log ID.

    Returns:
        Optional[Dict[str, str]]: Dictionary containing error log details if found, or
        None if not found.
    """
    cursor = kwargs["cursor"]

    query = "SELECT * FROM error_logs WHERE error_id = %s"
    cursor.execute(query, [eid])
    error = cursor.fetchone()

    if error:
        return {
            "error_id": error[0],
            "name": error[1],
            "message": error[2],
            "created_at": error[3],
            "line_number": error[4],
            "col_number": error[5],
            "project_id": error[6],
            "stack_trace": error[7],
            "handled": error[8],
            "resolved": error[9],
        }

    return None


@db_read_connection
def fetch_rejection(rid: int, **kwargs: dict) -> Optional[Dict[str, str]]:
    """Retrieves a specific rejection log by its ID.

    Args:
        rid (int): The rejection log ID.

    Returns:
        Optional[Dict[str, str]]: Dictionary containing rejection log details if found,
        or None if not found.
    """
    cursor = kwargs["cursor"]
    query = "SELECT * FROM rejection_logs WHERE error_id = %s"
    cursor.execute(query, [rid])
    rejection = cursor.fetchone()

    if rejection:
        return {
            "value": rejection[0],
            "created_at": rejection[1],
            "project_id": rejection[2],
            "handled": rejection[3],
            "resolved": rejection[4],
        }

    return None


@db_write_connection
def update_error_resolved(eid: int, new_resolved_state: bool, **kwargs: dict) -> bool:
    """Updates the resolved state of a specific error log.

    Args:
        eid (int): The error log ID.
        new_resolved_state (bool): The new resolved state.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]
    query = "UPDATE error_logs SET resolved = %s WHERE id = %s"
    cursor.execute(query, [new_resolved_state, eid])
    rows_updated = cursor.rowcount
    connection.commit()

    return rows_updated > 0


@db_write_connection
def update_rejection_resolved(
    rid: int, new_resolved_state: bool, **kwargs: dict
) -> bool:
    """Updates the resolved state of a specific rejection log.

    Args:
        rid (int): The rejection log ID.
        new_resolved_state (bool): The new resolved state.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]
    query = "UPDATE rejection_logs SET resolved = %s WHERE id = %s"
    cursor.execute(query, [new_resolved_state, rid])
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
