"""Project Issues models module.

This module contains functions to interact with the database for project-specific
issues, including error and rejection logs. It allows fetching combined logs, updating
resolution status, and deleting records. Each function is decorated to ensure proper
database connection context for reading or writing.
"""

from datetime import datetime, timedelta
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
    """Retrieves a paginated list of issues (errors and rejections) for a project."""
    cursor = kwargs["cursor"]

    errors = fetch_errors_by_project(
        cursor, project_uuid, page, limit, handled, time, resolved
    )
    rejections = fetch_rejections_by_project(
        cursor, project_uuid, page, limit, handled, time, resolved
    )

    combined_logs = sorted(
        errors + rejections, key=lambda x: x["created_at"], reverse=True
    )
    total_pages = calculate_total_error_pages(
        cursor, project_uuid, limit, handled, time, resolved
    )

    return {
        "issues": combined_logs[:limit],
        "total_pages": total_pages,
        "current_page": int(page),
    }


@db_write_connection
def delete_issues_by_project(project_uuid: str, **kwargs: dict) -> bool:
    """Deletes all issues (errors and rejections) associated with a project."""
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
def fetch_error(
    project_uuid: str, error_uuid: str, **kwargs: dict
) -> Optional[Dict[str, str]]:
    """Retrieves a specific error log by its UUID."""
    cursor = kwargs["cursor"]

    query = """
    SELECT
        name, message, created_at, filename, line_number, col_number, stack_trace,
        handled, resolved, contexts, method, path, ip, os, browser, runtime, error_hash
    FROM error_logs
    WHERE uuid = %s
    """
    cursor.execute(query, [error_uuid])
    error = cursor.fetchone()

    if not error:
        return None

    error_hash = error[16]

    occurrence_query = """
    SELECT COUNT(*)
    FROM error_logs
    WHERE error_hash = %s AND project_id = (
        SELECT id FROM projects WHERE uuid = %s
    )
    """
    cursor.execute(occurrence_query, [error_hash, project_uuid])
    total_occurrences = cursor.fetchone()[0]

    user_count_query = """
    SELECT COUNT(DISTINCT ip)
    FROM error_logs
    WHERE error_hash = %s AND project_id = (
        SELECT id FROM projects WHERE uuid = %s
    )
    """
    cursor.execute(user_count_query, [error_hash, project_uuid])
    distinct_users = cursor.fetchone()[0]

    return {
        "uuid": error_uuid,
        "name": error[0],
        "message": error[1],
        "created_at": error[2],
        "file": error[3],
        "line_number": error[4],
        "col_number": error[5],
        "project_uuid": project_uuid,
        "stack_trace": error[6],
        "handled": error[7],
        "resolved": error[8],
        "contexts": error[9],
        "method": error[10],
        "path": error[11],
        "os": error[13],
        "browser": error[14],
        "runtime": error[15],
        "total_occurrences": total_occurrences,
        "distinct_users": distinct_users,
    }


@db_read_connection
def fetch_rejection(
    project_uuid: str, rejection_uuid: int, **kwargs: dict
) -> Optional[Dict[str, str]]:
    """Retrieves a specific rejection log by its UUID."""
    cursor = kwargs["cursor"]
    query = """
    SELECT value, created_at, handled, resolved, method, path, os, browser, runtime
    FROM rejection_logs
    WHERE uuid = %s
    """
    cursor.execute(query, [rejection_uuid])
    rejection = cursor.fetchone()

    if rejection:
        return {
            "uuid": rejection_uuid,
            "value": rejection[0],
            "created_at": rejection[1],
            "project_uuid": project_uuid,
            "handled": rejection[2],
            "resolved": rejection[3],
            "method": rejection[4],
            "path": rejection[5],
            "os": rejection[6],
            "browser": rejection[7],
            "runtime": rejection[8],
        }

    return None


@db_write_connection
def update_error_resolved(
    error_uuid: str, new_resolved_state: bool, **kwargs: dict
) -> bool:
    """Updates the resolved state of a specific error log."""
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
    """Updates the resolved state of a specific rejection log."""
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]
    query = "UPDATE rejection_logs SET resolved = %s WHERE uuid = %s"
    cursor.execute(query, [new_resolved_state, rejection_uuid])
    rows_updated = cursor.rowcount
    connection.commit()

    return rows_updated > 0


@db_write_connection
def delete_error_by_id(error_uuid: str, **kwargs: dict) -> bool:
    """Deletes a specific error log by its UUID."""
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]
    query = "DELETE FROM error_logs WHERE uuid = %s"
    cursor.execute(query, [error_uuid])
    rows_deleted = cursor.rowcount
    connection.commit()

    return rows_deleted > 0


@db_write_connection
def delete_rejection_by_id(rejection_uuid: str, **kwargs: dict) -> bool:
    """Deletes a specific rejection log by its ID."""
    connection = kwargs["connection"]
    cursor = kwargs["cursor"]
    query = "DELETE FROM rejection_logs WHERE uuid = %s"
    cursor.execute(query, [rejection_uuid])
    rows_deleted = cursor.rowcount
    connection.commit()

    return rows_deleted > 0


@db_read_connection
def get_issue_summary(project_uuid: str, **kwargs: dict) -> bool:
    cursor = kwargs["cursor"]

    today = datetime.utcnow()
    start_of_week = today - timedelta(days=7)

    query = """
        SELECT DATE(created_at) AS day, COUNT(*) AS count
        FROM error_logs
        WHERE project_id IN (SELECT id FROM projects WHERE uuid = %s)
        AND created_at >= %s
        GROUP BY day
        ORDER BY day
        """

    cursor.execute(
        query,
        (
            project_uuid,
            start_of_week,
        ),
    )
    error_results = cursor.fetchall()

    query = """
        SELECT DATE(created_at) AS day, COUNT(*) AS count
        FROM rejection_logs
        WHERE project_id IN (SELECT id FROM projects WHERE uuid = %s)
        AND created_at >= %s
        GROUP BY day
        ORDER BY day
        """

    cursor.execute(query, (project_uuid, start_of_week))
    rejection_results = cursor.fetchall()

    issue_counts = issue_counts = [0] * 7

    for day, count in error_results:
        day_index = (today.date() - day).days
        if 0 <= day_index < 7:
            issue_counts[day_index] += count

    for day, count in rejection_results:
        day_index = (today.date() - day).days
        if 0 <= day_index < 7:
            issue_counts[day_index] += count

    return issue_counts[::-1]


@db_read_connection
def fetch_most_recent_log(
    project_uuid: str, **kwargs: dict
) -> Optional[Dict[str, str]]:
    """Fetches the most recent error or rejection log for a given project."""
    cursor = kwargs["cursor"]

    query_project = "SELECT id FROM projects WHERE uuid = %s"
    cursor.execute(query_project, [project_uuid])
    project = cursor.fetchone()
    project_id = project[0]

    # Query to get the most recent error log
    query_error = """
    SELECT uuid, 'error' AS log_type, name, message, created_at, filename, line_number,
           col_number, stack_trace, handled, resolved, contexts, method, path
    FROM error_logs
    WHERE project_id = %s
    ORDER BY created_at DESC
    LIMIT 1
    """
    cursor.execute(query_error, [project_id])
    error = cursor.fetchone()

    # Query to get the most recent rejection log
    query_rejection = """
    SELECT
        uuid, 'rejection' AS log_type, value, created_at, handled, resolved, method,
        path
    FROM rejection_logs
    WHERE project_id = %s
    ORDER BY created_at DESC
    LIMIT 1
    """
    cursor.execute(query_rejection, [project_id])
    rejection = cursor.fetchone()

    # Compare the most recent error and rejection logs
    most_recent = None

    if error and rejection:
        if error[4] > rejection[3]:
            most_recent = error
        else:
            most_recent = rejection
    elif error:
        most_recent = error
    elif rejection:
        most_recent = rejection

    if most_recent:
        if most_recent[1] == "error":
            return {
                "uuid": most_recent[0],
                "name": most_recent[2],
                "message": most_recent[3],
                "created_at": most_recent[4].isoformat(),
                "file": most_recent[5],
                "line_number": most_recent[6],
                "col_number": most_recent[7],
                "project_uuid": project_uuid,
                "stack_trace": most_recent[8],
                "handled": most_recent[9],
                "resolved": most_recent[10],
                "contexts": most_recent[11],
                "method": most_recent[12],
                "path": most_recent[13],
            }
        elif most_recent[1] == "rejection":
            return {
                "uuid": most_recent[0],
                "value": most_recent[2],
                "created_at": most_recent[3].isoformat(),
                "project_uuid": project_uuid,
                "handled": most_recent[4],
                "resolved": most_recent[5],
                "method": most_recent[6],
                "path": most_recent[7],
            }

    return None
