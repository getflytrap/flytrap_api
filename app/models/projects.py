import os
import math
import psycopg2

DB_HOST = os.getenv('PGHOST')
DB_NAME = os.getenv('PGDATABASE')
DB_USER = os.getenv('PGUSER')
DB_PASS = os.getenv('PGPASSWORD')
DB_PORT = os.getenv('PGPORT')

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

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


# * --- Helpers --- * #
def calculate_total_project_pages(connection, limit):
    if not limit:
        return 1

    cursor = connection.cursor()
    query = "SELECT COUNT(DISTINCT p.id) FROM projects p;"
    cursor.execute(query)
    total_count = cursor.fetchone()[0]
    total_pages = math.ceil(total_count / limit)

    return total_pages