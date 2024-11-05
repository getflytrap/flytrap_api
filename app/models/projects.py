from app.utils import get_db_connection, calculate_total_project_pages

def fetch_projects(page, limit):
    connection = get_db_connection()
    cursor = connection.cursor()

    offset = (page - 1) * limit if limit else 0 

    query = """
    SELECT 
        p.pid, 
        p.name,
        COUNT(DISTINCT e.id) AS error_count,
        COUNT(DISTINCT r.id) AS rejection_count
    FROM 
        projects p
    LEFT JOIN 
        error_logs e ON e.project_id = p.id
    LEFT JOIN 
        rejection_logs r ON r.project_id = p.id
    GROUP BY 
        p.pid, p.name
    ORDER BY p.name
    LIMIT %s OFFSET %s
    """
    cursor.execute(query, [limit, offset])
    rows = cursor.fetchall()
    cursor.close()

    projects = [
        {
            "project_id": row[0],
            "project_name": row[1],
            "issue_count": row[2] + row[3],
        }
        for row in rows
    ]

    total_pages = calculate_total_project_pages(connection, limit)

    return {
        "projects": projects,
        "total_pages": total_pages,
        "current_page": int(page),
    }

def add_project(pid, name):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = "INSERT INTO projects (pid, name) VALUES (%s, %s)"
    cursor.execute(query, [pid, name])

    connection.commit()
    cursor.close()
    connection.close() 
