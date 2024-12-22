from moto import mock_aws
from tests.utils.mock_data import raw_projects
from tests.utils.test_db_queries import TestDBQueries


def test_get_projects(root_client, projects):
    response = root_client.get("/api/projects?page=1&limit=10")

    assert response.status_code == 200
    assert "payload" in response.json
    assert isinstance(response.json["payload"]["projects"], list)
    assert len(response.json["payload"]["projects"]) == len(projects)


@mock_aws
def test_create_project(root_client, test_db):
    new_project_data = raw_projects["new_project"]

    response = root_client.post("/api/projects", json=new_project_data)

    assert response.status_code == 201
    assert "payload" in response.json
    assert response.json["payload"]["name"] == "New Project"
    assert response.json["payload"]["platform"] == "React"
    assert "uuid" in response.json["payload"]
    assert "api_key" in response.json["payload"]

    # Verify the project exists in the database
    project_uuid = response.json["payload"]["uuid"]
    new_project = TestDBQueries.get_project_by_uuid(test_db, project_uuid)
    assert new_project is not None, "Project should exist in the database."
    assert new_project[2] == "New Project"


@mock_aws
def test_delete_project(root_client, projects, test_db):
    """Test deleting a project."""
    project_uuid = projects[0]["uuid"]

    # Verify the project exists in the database before deletion
    existing_project = TestDBQueries.get_project_by_uuid(test_db, project_uuid)
    assert (
        existing_project is not None
    ), "Project should exist in the database before deletion."

    response = root_client.delete(f"/api/projects/{project_uuid}")

    assert response.status_code == 204

    # Verify the project no longer exists in the database
    existing_project = TestDBQueries.get_project_by_uuid(test_db, project_uuid)
    assert existing_project is None, "Project should not exist in the database."


def test_update_project(root_client, projects, test_db):
    """Test updating the name of a project."""
    project_uuid = projects[0]["uuid"]
    new_name = "Updated Project 1"

    # Keep a reference to the old project name to verify it gets updated
    old_project_name = TestDBQueries.get_project_by_uuid(test_db, project_uuid)[2]
    assert (
        old_project_name is not None
    ), "Old project name should exist in the database."

    response = root_client.patch(
        f"/api/projects/{project_uuid}", json={"new_name": new_name}
    )

    assert response.status_code == 204

    # Verify the project name was updated in the database
    updated_project_name = TestDBQueries.get_project_by_uuid(test_db, project_uuid)[2]
    assert (
        updated_project_name is not None
    ), "Updated project name should exist in the database."
    assert (
        updated_project_name == new_name
    ), "Updated project name should be what was passed in."

    # Compare
    assert old_project_name != updated_project_name, "Project name should be updated."
