from app.utils import (
    get_db_connection,
    fetch_errors_by_project, 
    fetch_rejections_by_project, 
    calculate_total_error_pages
)

def fetch_issues_by_project(pid, page, limit, handled, time, resolved):
    connection = get_db_connection()
    errors = fetch_errors_by_project(connection, pid, page, limit, handled, time, resolved)
    rejections = fetch_rejections_by_project(connection, pid, page, limit, handled, time, resolved)

    combined_logs = sorted(errors + rejections, key=lambda x: x['created_at'], reverse=True)
    total_pages = calculate_total_error_pages(connection, pid, limit)

    connection.close()

    return {
        "errors": combined_logs[:limit],
        "total_pages": total_pages,
        "current_page": int(page),
    }

def delete_data_by_project(pid):
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
        "rejection_rows_deleted": rejection_rows_deleted
    }

def fetch_error(eid):
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