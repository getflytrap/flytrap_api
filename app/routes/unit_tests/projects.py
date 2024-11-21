import pytest
from flask import Flask
from app.routes.projects import bp
from unittest.mock import patch

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

# Test for GET /projects
def test_get_projects(client):
    # You can use patching to mock the fetch_projects function
    with patch("app.routes.projects.fetch_projects") as mock_fetch:
        mock_fetch.return_value = [{"uuid": "123", "name": "Project 1", "platform": "Platform A"}]
        
        # Send a GET request to the '/projects' route
        response = client.get("/projects")
        
        # Assert status code and response data
        assert response.status_code == 200
        assert response.json["status"] == "success"
        assert len(response.json["data"]) == 1
        assert response.json["data"][0]["name"] == "Project 1"

# Test for POST /projects
def test_create_project(client):
    # Mock the add_project function to simulate a successful response
    with patch("app.routes.projects.add_project") as mock_add:
        mock_add.return_value = {"project_uuid": "123", "api_key": "abc123"}
        
        # Prepare the data for the POST request
        data = {"name": "New Project", "platform": "Platform A"}
        
        # Send a POST request to the '/projects' route
        response = client.post("/projects", json=data)
        
        # Assert status code and response data
        assert response.status_code == 201
        assert response.json["status"] == "success"
        assert response.json["data"]["name"] == "New Project"

# Test for DELETE /projects/<project_uuid>
def test_delete_project(client):
    # Mock the delete_project_by_id function
    with patch("app.routes.projects.delete_project_by_id") as mock_delete:
        mock_delete.return_value = True
        
        # Send a DELETE request to the '/projects/<project_uuid>' route
        response = client.delete("/projects/123")
        
        # Assert status code (204 means no content)
        assert response.status_code == 204

# Test for PATCH /projects/<project_uuid>
def test_update_project(client):
    # Mock the update_project_name function
    with patch("app.routes.projects.update_project_name") as mock_update:
        mock_update.return_value = True
        
        # Prepare the data for the PATCH request
        data = {"new_name": "Updated Project Name"}
        
        # Send a PATCH request to the '/projects/<project_uuid>' route
        response = client.patch("/projects/123", json=data)
        
        # Assert status code and response data
        assert response.status_code == 200
        assert response.json["status"] == "success"
        assert response.json["data"]["name"] == "Updated Project Name"

