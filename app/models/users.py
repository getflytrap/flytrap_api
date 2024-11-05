from app.utils import get_db_connection

def fetch_all_users():
    connection = get_db_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM users;"
    cursor.execute(query)
    rows = cursor.fetchall()

    users = [
        {
            "id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "email": user[3],
            "is_root": user[5],
            "created_at": user[6]
         }
         for user in rows
    ]

    cursor.close()
    connection.close()

    return users if users else None

def add_user(first_name, last_name, email, password_hash):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO users
    (first_name, last_name, email, password_hash)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """
    cursor.execute(query, (first_name, last_name, email, password_hash))
    user_id = cursor.fetchone()[0]
    connection.commit()

    cursor.close()
    connection.close()
    return user_id

def delete_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "DELETE FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    rows_deleted = cursor.rowcount
    connection.commit()
    connection = get_db_connection()
    cursor = connection.cursor()

    return rows_deleted > 0

