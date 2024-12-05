import os
import pytest
import time
import psycopg2
from psycopg2 import OperationalError
from app import create_app
from config import load_config
from db import init_db_pool

pytest_plugins = ["pytest_docker.plugin"]

# Set the correct version of the docker-compose command
@pytest.fixture(scope="session")
def docker_compose_command() -> str:
    return "docker-compose"

@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "app/routes/unit_tests/docker-compose.yml")

@pytest.fixture(scope='session')
def postgres_container(docker_services):
    """Ensure the PostgreSQL container is up and return a verified connection."""
    postgres_port = docker_services.port_for("db", 5432)
    conn = None
    retries = 5

    for _ in range(retries):
        try:
            conn = psycopg2.connect(
                dbname="test_db",
                user="postgres",
                password="postgres",
                host="localhost",
                port=postgres_port,
            )
            break
        except OperationalError:
            time.sleep(6)

    if conn is None:
        raise Exception("Failed to connect to PostgreSQL after several retries")

    yield conn
    conn.close()

@pytest.fixture
def app(postgres_container):    
    os.environ["FLASK_ENV"] = "TESTING"
    app = create_app()
    load_config(app)
    init_db_pool(app)

    yield app           

@pytest.fixture
def client(app):
    return app.test_client()