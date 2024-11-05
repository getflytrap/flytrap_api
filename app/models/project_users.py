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

def add_user_to_project(pid, user_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO projects_users (project_id, user_id)
    SELECT p.id, %s
    FROM projects p
    WHERE p.pid = %s
    RETURNING id
    """

    cursor.execute(query, (user_id, pid))
    connection.commit()