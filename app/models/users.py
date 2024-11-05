from app.utils import get_db_connection

def fetch_all_users(cursor, connection):
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