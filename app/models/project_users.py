from app.utils import get_db_connection

def fetch_project_users(pid):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    query = """
    SELECT pu.user_id
    FROM projects_users pu
    JOIN projects p
    ON pu.project_id = p.id
    WHERE p.pid = %s
    """

    cursor.execute(query, (pid,))
    user_ids = cursor.fetchall()

    return [user_id[0] for user_id in user_ids] if user_ids else []