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