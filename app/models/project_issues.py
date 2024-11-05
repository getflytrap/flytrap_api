from typing import Union, Dict, Optional, List
from app.utils import (
    get_db_connection,
    fetch_errors_by_project,
    fetch_rejections_by_project,
    calculate_total_error_pages,
)


def fetch_issues_by_project(
    pid: int,
    page: int,
    limit: int,
    handled: Optional[bool],
    time: Optional[str],
    resolved: Optional[bool],
) -> Dict[str, List[Dict[str, int]]]:
    connection = get_db_connection()
    errors = fetch_errors_by_project(
        connection, pid, page, limit, handled, time, resolved
    )
    rejections = fetch_rejections_by_project(
        connection, pid, page, limit, handled, time, resolved
    )

    combined_logs = sorted(
        errors + rejections, key=lambda x: x["created_at"], reverse=True
    )
    total_pages = calculate_total_error_pages(connection, pid, limit)

    connection.close()

    return {
        "errors": combined_logs[:limit],
        "total_pages": total_pages,
        "current_page": int(page),
    }


def delete_data_by_project(pid: int) -> Dict[str, Union[int, str, bool]]:
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "DELETE FROM error_logs WHERE project_id = %s"
    cursor.execute(query, (pid,))
    error_rows_deleted = cursor.rowcount

    rejection_query = "DELETE FROM rejection_logs WHERE project_id = %s"
    cursor.execute(rejection_query, (pid,))
    rejection_rows_deleted = cursor.rowcount

    connection.commit()
    cursor.close()
    connection.close()

    return {
        "success": True,
        "message": "Data deletion completed.",
        "error_rows_deleted": error_rows_deleted,
        "rejection_rows_deleted": rejection_rows_deleted,
    }


def fetch_error(eid: int) -> Optional[Dict[str, str]]:
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM error_logs WHERE error_id = %s"
    cursor.execute(query, [eid])
    error = cursor.fetchone()
    cursor.close()
    connection.close()

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


def fetch_rejection(rid: int) -> Optional[Dict[str, str]]:
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM rejection_logs WHERE error_id = %s"
    cursor.execute(query, [rid])
    rejection = cursor.fetchone()
    cursor.close()
    connection.close()

    if rejection:
        return {
            "value": rejection[0],
            "created_at": rejection[1],
            "project_id": rejection[2],
            "handled": rejection[3],
            "resolved": rejection[4],
        }

    return None


def update_error_resolved(eid: int, new_resolved_state: bool) -> bool:
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "UPDATE error_logs SET resolved = %s WHERE id = %s"
    cursor.execute(query, [new_resolved_state, eid])
    rows_updated = cursor.rowcount
    connection.commit()
    cursor.close()
    connection.close()

    return rows_updated > 0


def update_rejection_resolved(rid: int, new_resolved_state: bool) -> bool:
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "UPDATE rejection_logs SET resolved = %s WHERE id = %s"
    cursor.execute(query, [new_resolved_state, rid])
    rows_updated = cursor.rowcount
    connection.commit()
    cursor.close()
    connection.close()

    return rows_updated > 0


def delete_error_by_id(eid: int) -> bool:
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "DELETE FROM error_logs WHERE id = %s"
    cursor.execute(query, [eid])
    rows_deleted = cursor.rowcount
    connection.commit()
    cursor.close()
    connection.close()

    return rows_deleted > 0


def delete_rejection_by_id(rid: int) -> bool:
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "DELETE FROM rejection_logs WHERE id = %s"
    cursor.execute(query, [rid])
    rows_deleted = cursor.rowcount
    connection.commit()
    cursor.close()
    connection.close()

    return rows_deleted > 0
