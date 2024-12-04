import pytest
from flask import jsonify, current_app
from unittest.mock import patch
from mock_data import MOCK_DATA

class status:
    HTTP_201_CREATED = 201
    HTTP_200_OK = 200
    HTTP_400_BAD_REQUEST = 400
    HTTP_204_NO_CONTENT = 204

from flytrap import app
app.config["TESTING"] = True

@pytest.fixture
def client():
    return app.test_client()

@patch('app.routes.projects.generate_uuid')
def test_create_project(mock_generate_uuid, client):
    mock_generate_uuid.return_value = "dajhew32876dcx79sd2332"

    response = client.post('/api/projects', json={
        "name": "testing123",
        "platform": "react"
    })

    response_json = response.get_json()

    assert response_json == MOCK_DATA["create_project"]
    assert response.status_code == status.HTTP_201_CREATED

@patch('app.routes.projects.fetch_projects')
def test_get_projects(mock_fetch, client):
    mock_fetch.return_value = MOCK_DATA["fetch_projects"]

    response = client.get('/api/projects')
    response_json = response.get_json()

    assert response_json['payload'] == MOCK_DATA["fetch_projects"]
    assert response.status_code == status.HTTP_200_OK

@patch('app.routes.projects.delete_project_by_id')
def test_delete_project(mock_delete, client):
    mock_delete.return_value = "3987dsfsd20734"

    response = client.delete(f"/api/projects/{MOCK_DATA['fetch_projects']['projects'][0]['uuid']}")

    assert response.status_code == status.HTTP_204_NO_CONTENT