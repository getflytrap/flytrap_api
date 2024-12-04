import pytest
from flask import jsonify, current_app
from unittest.mock import patch, call
from mock_data import MOCK_DATA, status_codes

from flytrap import app
app.config["TESTING"] = True

@pytest.fixture
def client():
    return app.test_client()

@patch('app.routes.projects.associate_api_key_with_usage_plan')
@patch('app.routes.projects.create_sns_topic')
@patch('app.routes.projects.add_project')
@patch('app.routes.projects.generate_uuid')
def test_create_project(
        mock_generate_uuid, 
        mock_add_project, 
        mock_create_sns, 
        mock_associate_api_key, 
        client
    ):

    # the generate_uuid method is used twice, once to generate the project_uuid, once for the api_key

    mock_generate_uuid.side_effect = ["dajhew32876dcx79sd2332", "api_key_123"]
    mock_create_sns.return_value = "986723jgds23wkhdskh32"

    response = client.post('/api/projects', json={
        "name": "testing123",
        "platform": "react"
    })

    response_json = response.get_json()
    
    assert mock_generate_uuid.call_count == 2
    mock_create_sns.assert_called_once_with('dajhew32876dcx79sd2332')
    mock_add_project.assert_called_once_with(
        "testing123", 
        'dajhew32876dcx79sd2332', 
        'api_key_123', 
        "react", 
        mock_create_sns.return_value 
    )

    assert mock_associate_api_key.call_count == 1
    assert response_json == MOCK_DATA["create_project"]
    assert response.status_code == status_codes.HTTP_201_CREATED

@patch('app.routes.projects.fetch_projects')
def test_get_projects(mock_fetch, client):
    mock_fetch.return_value = MOCK_DATA["fetch_projects"]

    response = client.get('/api/projects')
    response_json = response.get_json()

    # the route handler's response should include the projects fetched from the db in its payload
    assert response_json['payload'] == MOCK_DATA["fetch_projects"]
    assert response.status_code == status_codes.HTTP_200_OK

@patch('app.routes.projects.delete_api_key_from_aws')
@patch('app.routes.projects.delete_sns_topic_from_aws')
@patch('app.routes.projects.delete_project_by_id')
def test_delete_project(
        mock_delete_project, 
        mock_delete_sns_topic, 
        mock_delete_api_key, 
        client
    ):

    # the delete_project_by_id model method should return the deleted project's api key
    mock_delete_project.return_value = MOCK_DATA['fetch_projects']['projects'][0]['api_key']

    response = client.delete(f"/api/projects/{MOCK_DATA['fetch_projects']['projects'][0]['uuid']}")
    
    mock_delete_sns_topic.assert_called_once_with(f"{MOCK_DATA['fetch_projects']['projects'][0]['uuid']}")

    # the delete_api_key AWS service call should be passed the deleted project's api key as an argument
    mock_delete_api_key.assert_called_once_with(mock_delete_project.return_value)
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT