import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from functools import wraps

# Mocking the decorators to do nothing
def no_op_decorator(*args, **kwargs):
    """A decorator that does nothing."""
    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            print('decorator worked')  # This will print if the decorator is being applied
            return func(*args, **kwargs)
        return wrapped_function
    return decorator

from app.routes.projects import bp

# Create a simple Flask app with the Blueprint registered for testing purposes
@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(bp, url_prefix="/projects")
    return app

# Create a test client
@pytest.fixture
def client(app):
    return app.test_client()

@patch()
# Test for GET /projects
def test_get_projects(client):
    with patch("app.routes.projects.auth_manager.authenticate", no_op_decorator), \
         patch("app.routes.projects.auth_manager.authorize_root", no_op_decorator):
        with patch("app.routes.projects.fetch_projects") as mock_fetch:
            mock_fetch.return_value = [{"uuid": "123", "name": "Project 1", "platform": "Platform A"}]

            response = client.get("/projects")
            assert response.status_code == 200
            assert response.json["status"] == "success"
            assert len(response.json["data"]) == 1
            assert response.json["data"][0]["name"] == "Project 1"

# Test for POST /projects
def test_create_project(client):
    with patch("app.routes.projects.auth_manager.authenticate", no_op_decorator), \
         patch("app.routes.projects.auth_manager.authorize_root", no_op_decorator):
        with patch("app.routes.projects.add_project") as mock_add:
            mock_add.return_value = {"project_uuid": "123", "api_key": "abc123"}

            data = {"name": "New Project", "platform": "Platform A"}
            response = client.post("/projects", json=data)
            assert response.status_code == 201
            assert response.json["status"] == "success"
            assert response.json["data"]["name"] == "New Project"

# Test for DELETE /projects/<project_uuid>
def test_delete_project(client):
    with patch("app.routes.projects.auth_manager.authenticate", no_op_decorator), \
         patch("app.routes.projects.auth_manager.authorize_root", no_op_decorator):
        with patch("app.routes.projects.delete_project_by_id") as mock_delete:
            mock_delete.return_value = True

            response = client.delete("/projects/123")
            assert response.status_code == 204

# Test for PATCH /projects/<project_uuid>
def test_update_project(client):
    with patch("app.routes.projects.auth_manager.authenticate", no_op_decorator), \
         patch("app.routes.projects.auth_manager.authorize_root", no_op_decorator):
        with patch("app.routes.projects.update_project_name") as mock_update:
            mock_update.return_value = True

            data = {"new_name": "Updated Project Name"}
            response = client.patch("/projects/123", json=data)
            assert response.status_code == 200
            assert response.json["status"] == "success"
            assert response.json["data"]["name"] == "Updated Project Name"
