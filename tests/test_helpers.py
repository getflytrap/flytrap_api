def setup_schema(cursor):
    """Set up the database schema and add an admin user."""
    cursor.execute(open("tests/schema.sql", "r").read())


def clean_up_database(cursor):
    """Truncate all tables to ensure a clean state."""
    cursor.execute(
        """
        TRUNCATE TABLE 
            error_logs,
            rejection_logs,
            projects_users,
            projects,
            users
        RESTART IDENTITY CASCADE;
        """
    )

def insert_user(cursor, user_data):
    """Insert a user into the database and return the inserted row."""
    query = """
    INSERT INTO users (uuid, first_name, last_name, email, password_hash, is_root) 
    VALUES (%s, %s, %s, %s, %s, %s) 
    RETURNING uuid, first_name, last_name, email, is_root
    """
    cursor.execute(query, 
                (
        user_data["uuid"],
        user_data["first_name"],
        user_data["last_name"],
        user_data["email"],
        user_data["password_hash"],
        user_data["is_root"],
    ))
    return cursor.fetchone()