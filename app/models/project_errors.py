from app.utils import (
    get_db_connection,
    fetch_errors_by_project, 
    fetch_rejections_by_project, 
    calculate_total_error_pages
)

def fetch_data(pid, page, limit, handled, time, resolved):
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