import sys
import os
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.utils.auth.token_manager import TokenManager
from config import load_config
from db import init_db_pool, close_db_pool, get_db_connection_from_pool, return_db_connection_to_pool
from tests.utils.test_setup_helpers import setup_schema, clean_up_database, insert_user
from tests.utils.mock_data import processed_users, processed_projects, project_assignment, errors as mock_errors, rejections as mock_rejections

@pytest.fixture(scope="session")
def test_app():
    """Set up a Flask app instance configured for testing."""
    overrides = {
        "FLASK_ENV": "testing",
        "PGDATABASE": "flytrap_test_db",
    }

    app = create_app()
    load_config(app, overrides)
    init_db_pool(app)

    with app.app_context():
        yield app

    close_db_pool()

@pytest.fixture(scope="session")
def setup_test_db():
    connection = get_db_connection_from_pool()
    connection.autocommit = True
    cursor = connection.cursor()

    # Set up the database schema
    setup_schema(cursor)

    return_db_connection_to_pool(connection)

    yield

    # Drop the schema after tests
    connection = get_db_connection_from_pool()
    cursor = connection.cursor()
    cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    return_db_connection_to_pool(connection)


@pytest.fixture(scope="function")
def test_db(test_app):
    """Provide a database connection for testing and ensure cleanup."""
    connection = get_db_connection_from_pool()
    connection.autocommit = True
    cursor = connection.cursor()

    # Provide cursor for test use
    yield cursor 

    # Clean up after each test
    clean_up_database(cursor)
    return_db_connection_to_pool(connection)


@pytest.fixture
def root_user(test_db):
    """Fixture to create and return the root user."""
    user_data = processed_users["root_user"]
    return insert_user(test_db, user_data)


@pytest.fixture
def regular_user(test_db):
    """Fixture to create and return a regular user."""
    user_data = processed_users["regular_user"]
    return insert_user(test_db, user_data)


@pytest.fixture
def client(test_app):
    """Provides an unauthenticated test client."""
    return test_app.test_client()


@pytest.fixture
def root_client(test_app, root_user):
    """
    Provide a test client pre-configured with an authenticated user.
    Includes Authorization header and cookies using the actual TokenManager.
    """
    client = test_app.test_client()

    # Instantiate the TokenManager
    token_manager = TokenManager()

    # Generate a token for the root user
    with test_app.app_context():
        access_token = token_manager.create_access_token(root_user[0], is_root=True)
        refresh_token = token_manager.create_refresh_token(root_user[0])

    # Set Authorization header
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

    # Set cookies if required
    client.set_cookie("refresh_token", refresh_token)

    return client

@pytest.fixture
def regular_client(test_app, regular_user):
    """
    Provide a test client pre-configured with an authenticated user.
    Includes Authorization header and cookies using the actual TokenManager.
    """
    client = test_app.test_client()

    # Instantiate the TokenManager
    token_manager = TokenManager()

    # Generate a token for the root user
    with test_app.app_context():
        access_token = token_manager.create_access_token(regular_user[0], is_root=False)
        refresh_token = token_manager.create_refresh_token(regular_user[0])

    # Set Authorization header
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

    # Set cookies if required
    client.set_cookie("refresh_token", refresh_token)

    return client

@pytest.fixture
def projects(test_db):
    """Fixture to insert two projects into the database."""
    for project in processed_projects:
        test_db.execute(
            """
            INSERT INTO projects (uuid, name, api_key, platform, sns_topic_arn)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                project["uuid"],
                project["name"],
                project["api_key"],
                project["platform"],
                project["sns_topic_arn"],
            )
        )

    return processed_projects

@pytest.fixture
def user_project_assignment(test_db, regular_user, projects):
    """Fixture to assign a regular user to one of the projects."""
    project_uuid = project_assignment["project_uuid"]
    user_uuid = project_assignment["user_uuid"]

    test_db.execute(
        """
        INSERT INTO projects_users (project_id, user_id)
        SELECT p.id, u.id
        FROM projects p, users u
        WHERE p.uuid = %s AND u.uuid = %s
        """,
        (project_uuid, user_uuid),
    )

    return {"user_uuid": user_uuid, "project_uuid": project_uuid}

@pytest.fixture
def errors(test_db):
    """Fixture to insert mock error logs."""
    for error in mock_errors:
        test_db.execute(
            """
            INSERT INTO error_logs (
                uuid, name, message, created_at, filename,
                line_number, col_number, project_id, stack_trace, handled, resolved,
                contexts, method, path, ip, os, browser, runtime, error_hash
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                error["uuid"],
                error["name"],
                error["message"],
                error["created_at"],
                error["filename"],
                error["line_number"],
                error["col_number"],
                error["project_id"],
                error["stack_trace"],
                error["handled"],
                error["resolved"],
                json.dumps(error["contexts"]),
                error["method"],
                error["path"],
                error["ip"],
                error["os"],
                error["browser"],
                error["runtime"],
                error["error_hash"],
            )
    )
        
    return mock_errors
        
@pytest.fixture
def rejections(test_db):
    """Fixture to insert mock rejection logs."""
    for rejection in mock_rejections:
        test_db.execute(
            """
            INSERT INTO rejection_logs (
                uuid, value, created_at, project_id, handled, 
                resolved, method, path, ip, os, browser, runtime
            ) 
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            """,
            (
                rejection["uuid"],
                rejection["value"],
                rejection["created_at"],
                rejection["project_id"],
                rejection["handled"],
                rejection["resolved"],
                rejection["method"],
                rejection["path"],
                rejection["ip"],
                rejection["os"],
                rejection["browser"],
                rejection["runtime"],
            ),
        )
    return mock_rejections

@pytest.fixture
def webhook_payload():
    """Fixture for a valid webhook payload."""
    return {
        "project_id": "project-uuid-123-456",
    }
