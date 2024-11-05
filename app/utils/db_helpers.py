import math

def calculate_total_project_pages(connection, limit):
    if not limit:
        return 1

    cursor = connection.cursor()
    query = "SELECT COUNT(DISTINCT p.id) FROM projects p;"
    cursor.execute(query)
    total_count = cursor.fetchone()[0]
    total_pages = math.ceil(total_count / limit)

    return total_pages

def fetch_errors_by_project(connection, pid, page, limit, handled, time, resolved):
    cursor = connection.cursor()

    # Base query
    query = """
    SELECT
        e.id, e.name, e.message, e.created_at, e.line_number, e.col_number, e.project_id, e.handled, e.resolved
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

def fetch_rejections_by_project(connection, pid, page, limit, handled, time, resolved):
    cursor = connection.cursor()

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

def calculate_total_error_pages(connection, pid, limit):
    cursor = connection.cursor()
    error_count_query = "SELECT COUNT(*) FROM error_logs WHERE pid = %s"
    error_count_query = "SELECT COUNT(*) FROM error_logs WHERE project_id = %s"
    cursor.execute(error_count_query, [pid])
    error_count = cursor.fetchone()[0]

    rejection_count_query = "SELECT COUNT(*) FROM rejection_logs WHERE pid = %s"
    rejection_count_query = "SELECT COUNT(*) FROM rejection_logs WHERE project_id = %s"
    cursor.execute(rejection_count_query, [pid])
    rejection_count = cursor.fetchone()[0]

    total_count = error_count + rejection_count
    total_pages = math.ceil(total_count / limit)

    cursor.close()
    return total_pages