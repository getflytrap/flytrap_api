import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.utils.auth.token_manager import TokenManager
from config import load_config
from db import init_db_pool, close_db_pool, get_db_connection_from_pool, return_db_connection_to_pool
from test_helpers import setup_schema, clean_up_database, insert_user

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
    user_data = (
        "root-uuid-123-456-789",
        "Flytrap",
        "Admin",
        "admin@admin.com",
        "$2b$12$5voKL8Dzp9muUhSZ/bsPL.JkWaDja.jrvBFk2wMfmOn.ILBLBvksW",
        True,
    )
    return insert_user(test_db, user_data)


@pytest.fixture
def regular_user(test_db):
    """Fixture to create and return a regular user."""
    user_data = (
        "user-uuid-123-456-789",
        "John",
        "Doe",
        "john@doe.com",
        "$2b$12$7Ze4nBXlTV04y8ls2PiHce0ecpBgjO.uOiuVx5WobS7SCQDELZzNS",
        False,
    )
    return insert_user(test_db, user_data)


@pytest.fixture
def client(test_app):
    return test_app.test_client()


@pytest.fixture
def auth_client(test_app, root_user):
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