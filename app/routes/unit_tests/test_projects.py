from unittest.mock import patch
from mock_data import MOCK_DATA, status_codes

def test_get_projects(client):
    
    response = client.get('/api/projects', query_string={"page": "1", "limit": "10"})
    response_json = response.get_json()

    # the route handler's response should include the projects fetched from the db in its payload
    print('repsonse json', response_json)
    assert response_json['payload']['projects'] == [MOCK_DATA['fetch_projects']['projects'][0]]
    assert response.status_code == status_codes.HTTP_200_OK

@patch('app.routes.projects.associate_api_key_with_usage_plan')
@patch('app.routes.projects.create_sns_topic')
@patch('app.routes.projects.generate_uuid')
def test_create_project(
        mock_generate_uuid, 
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

    assert mock_associate_api_key.call_count == 1
    assert response_json == MOCK_DATA["mock_project"]
    assert response.status_code == status_codes.HTTP_201_CREATED

@patch('app.routes.projects.delete_api_key_from_aws')
@patch('app.routes.projects.delete_sns_topic_from_aws')
def test_delete_project(
        mock_delete_sns_topic,
        mock_delete_api_key, 
        client
    ):

    # the delete_project_by_id model method should return the deleted project's api key
    mock_project_uuid = MOCK_DATA['fetch_projects']['projects'][0]['uuid']
    response = client.delete(f"/api/projects/{mock_project_uuid}")
    
    # mock_delete_sns_topic.assert_called_once_with(MOCK_DATA['fetch_projects']['projects'][0]['uuid'])

    # the delete_api_key AWS service call should be passed the deleted project's api key as an argument
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT

def test_get_projects_no_results(client):
    """
    Test GET /api/projects when no projects are available.
    """
    with patch('app.routes.projects.fetch_projects', return_value={
        "projects": [],
        "total_pages": 1,
        "current_page": 1,
    }):
        response = client.get('/api/projects', query_string={"page": "1", "limit": "10"})
        response_json = response.get_json()
        
        assert response_json['payload']['projects'] == []
        assert response.status_code == status_codes.HTTP_200_OK


@patch('app.routes.projects.associate_api_key_with_usage_plan')
@patch('app.routes.projects.create_sns_topic')
@patch('app.routes.projects.generate_uuid')
def test_create_project_invalid_payload(
        mock_generate_uuid, 
        mock_create_sns, 
        mock_associate_api_key, 
        client
    ):
    """
    Test POST /api/projects with invalid payload.
    """
    response = client.post('/api/projects', json={})
    response_json = response.get_json()
    
    # assert response_json == {'message': 'Invalid request.'}
    assert response.status_code == status_codes.HTTP_400_BAD_REQUEST