from unittest.mock import patch
from mock_data import MOCK_DATA, status_codes

def test_get_issues(client):
  project_uuid = MOCK_DATA['fetch_projects']['projects'][0]['uuid']
  response = client.get(f"/api/projects/{project_uuid}/issues")
  response_json = response.get_json()

  assert response_json["payload"]["issues"] == [{
      "uuid": MOCK_DATA['mock_error']['uuid'], 
      "name": MOCK_DATA['mock_error']['name'], 
      "message": MOCK_DATA['mock_error']['message'], 
      "created_at": "Fri, 14 Jul 2023 15:23:45 GMT", 
      "file": MOCK_DATA['mock_error']['filename'], 
      "line_number": MOCK_DATA['mock_error']['line_number'],
      "col_number": MOCK_DATA['mock_error']['col_number'], 
      "handled": MOCK_DATA['mock_error']['handled'], 
      "resolved": MOCK_DATA['mock_error']['resolved'], 
      "project_uuid": MOCK_DATA["fetch_projects"]["projects"][0]["uuid"],
      "distinct_users": 1,
      "total_occurrences": 1
  }]
  assert response.status_code == status_codes.HTTP_200_OK

def test_get_issues_invalid_pagination(client):
    project_uuid = MOCK_DATA['fetch_projects']['projects'][0]['uuid']
    response = client.get(f"/api/projects/{project_uuid}/issues?page=-1&limit=0")
    
    assert response.status_code == 400
    assert response.get_json() == {"message": "Invalid pagination parameters."}

def test_get_error_by_id(client):
    project_uuid = MOCK_DATA['fetch_projects']['projects'][0]['uuid']
    error_uuid = MOCK_DATA["mock_error"]["uuid"]
    response = client.get(f"api/projects/{project_uuid}/issues/errors/{error_uuid}")
    response_json = response.get_json()

    assert response.status_code == status_codes.HTTP_200_OK
    assert response_json['payload'] == {
        "uuid": error_uuid,
        "name": MOCK_DATA["mock_error"]["name"],
        "message": MOCK_DATA["mock_error"]["message"],
        "created_at": "Fri, 14 Jul 2023 15:23:45 GMT",
        "file": MOCK_DATA["mock_error"]["filename"],
        "line_number": MOCK_DATA["mock_error"]["line_number"],
        "col_number": MOCK_DATA["mock_error"]["col_number"],
        "project_uuid": MOCK_DATA["fetch_projects"]["projects"][0]["uuid"],
        "stack_trace": MOCK_DATA["mock_error"]["stack_trace"],
        "handled": MOCK_DATA["mock_error"]["handled"],
        "resolved": MOCK_DATA["mock_error"]["resolved"],
        "contexts": MOCK_DATA["mock_error"]["contexts"],
        "method": MOCK_DATA["mock_error"]["method"],
        "path": MOCK_DATA["mock_error"]["path"],
        "os": MOCK_DATA["mock_error"]["os"],
        "browser": MOCK_DATA["mock_error"]["browser"],
        "runtime": MOCK_DATA["mock_error"]["runtime"],
        "total_occurrences": 1,
        "distinct_users": 1,
    }

def test_get_error_invalid_uuid(client):
    project_uuid = MOCK_DATA['fetch_projects']['projects'][0]['uuid']
    invalid_error_uuid = "invalid-uuid"
    response = client.get(f"/api/projects/{project_uuid}/issues/errors/{invalid_error_uuid}")
    
    assert response.status_code == 404
    assert response.get_json() == {"message": "Error not found."}


def test_toggle_error_resolved_state(client):
    project_uuid = MOCK_DATA['fetch_projects']['projects'][0]['uuid']
    error_uuid = MOCK_DATA["mock_error"]["uuid"]

    response = client.patch(
       f"api/projects/{project_uuid}/issues/errors/{error_uuid}",
       json={"resolved": "true"}
    )

    assert response.status_code == status_codes.HTTP_204_NO_CONTENT

def test_toggle_error_missing_payload(client):
    project_uuid = MOCK_DATA['fetch_projects']['projects'][0]['uuid']
    error_uuid = MOCK_DATA["mock_error"]["uuid"]
    response = client.patch(f"/api/projects/{project_uuid}/issues/errors/{error_uuid}", json={})
    
    assert response.status_code == 400
    assert response.get_json() == {"message": "Invalid request."}

def test_delete_error(client):
    project_uuid = MOCK_DATA['fetch_projects']['projects'][0]['uuid']
    error_uuid = MOCK_DATA["mock_error"]["uuid"]

    response = client.delete(f"api/projects/{project_uuid}/issues/errors/{error_uuid}")

    assert response.status_code == status_codes.HTTP_204_NO_CONTENT