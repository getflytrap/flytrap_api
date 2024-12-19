import json

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
    cursor.execute(
        query,
        (
            user_data["uuid"],
            user_data["first_name"],
            user_data["last_name"],
            user_data["email"],
            user_data["password_hash"],
            user_data["is_root"],
        ),
    )
    return cursor.fetchone()


def insert_project(cursor, project):
    """Insert a project into the database."""
    query = """
    INSERT INTO projects (uuid, name, api_key, platform, sns_topic_arn)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
    """
    cursor.execute(query, (
        project["uuid"],
        project["name"],
        project["api_key"],
        project["platform"],
        project["sns_topic_arn"],
    ))
    return cursor.fetchone()

def assign_user_to_project(cursor, user_uuid, project_uuid):
    """Assign a user to a project."""
    query = """
    INSERT INTO projects_users (project_id, user_id)
    SELECT p.id, u.id
    FROM projects p, users u
    WHERE p.uuid = %s AND u.uuid = %s
    """
    cursor.execute(query, (project_uuid, user_uuid))

def insert_error_log(cursor, error_data):
    """Insert an error log into the database."""
    query = """
    INSERT INTO error_logs (
        uuid, name, message, created_at, filename,
        line_number, col_number, project_id, stack_trace, handled, resolved,
        contexts, method, path, ip, os, browser, runtime, error_hash
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    cursor.execute(query, (
        error_data["uuid"],
        error_data["name"],
        error_data["message"],
        error_data["created_at"],
        error_data["filename"],
        error_data["line_number"],
        error_data["col_number"],
        error_data["project_id"],
        error_data["stack_trace"],
        error_data["handled"],
        error_data["resolved"],
        json.dumps(error_data["contexts"]),
        error_data["method"],
        error_data["path"],
        error_data["ip"],
        error_data["os"],
        error_data["browser"],
        error_data["runtime"],
        error_data["error_hash"],
    ))

def insert_rejection_log(cursor, rejection_data):
    """Insert a rejection log into the database."""
    query = """
    INSERT INTO rejection_logs (
        uuid, value, created_at, project_id, handled,
        resolved, method, path, ip, os, browser, runtime
    )
    VALUES (
        %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s
    )
    """
    cursor.execute(query, (
        rejection_data["uuid"],
        rejection_data["value"],
        rejection_data["created_at"],
        rejection_data["project_id"],
        rejection_data["handled"],
        rejection_data["resolved"],
        rejection_data["method"],
        rejection_data["path"],
        rejection_data["ip"],
        rejection_data["os"],
        rejection_data["browser"],
        rejection_data["runtime"],
    ))