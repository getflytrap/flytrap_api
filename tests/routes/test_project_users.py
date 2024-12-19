from moto import mock_aws
from tests.mock_data import processed_users
from tests.test_helpers import setup_mock_sns_topic

def test_get_project_users(root_client, regular_user, projects, user_project_assignment):
    """Test fetching users associated with a project."""
    project_uuid = projects[0]["uuid"]

    response = root_client.get(f"/api/projects/{project_uuid}/users")

    assert response.status_code == 200
    assert "payload" in response.json, "Response should contain 'payload' key."
    fetched_users = response.json["payload"]
    assert isinstance(fetched_users, list), "Payload should be a list of user UUIDs."
    assert len(fetched_users) > 0, "There should be at least one user associated with the project."
    assert fetched_users[0] == processed_users["regular_user"]["uuid"]

@mock_aws
def test_add_project_user(root_client, regular_user, projects, test_db):
    project_uuid = projects[0]["uuid"]
    user_uuid = regular_user[0]

    # Setup mocked SNS topic
    sns_topic_arn = setup_mock_sns_topic(project_uuid)
    test_db.execute(
        """
        UPDATE projects SET sns_topic_arn = %s WHERE uuid = %s
        """,
        (sns_topic_arn, project_uuid),
    )

    # Verify the user is not already associated
    test_db.execute(
        """
        SELECT * FROM projects_users
        WHERE project_id = (SELECT id FROM projects WHERE uuid = %s)
        AND user_id = (SELECT id FROM users WHERE uuid = %s)
        """,
        (project_uuid, user_uuid),
    )
    association = test_db.fetchone()
    assert association is None, "User should not be associated with the project initially."

    response = root_client.post(f"/api/projects/{project_uuid}/users", json={"user_uuid": user_uuid})

    assert response.status_code == 204

    # Verify the user is now associated
    test_db.execute(
        """
        SELECT * FROM projects_users
        WHERE project_id = (SELECT id FROM projects WHERE uuid = %s)
        AND user_id = (SELECT id FROM users WHERE uuid = %s)
        """,
        (project_uuid, user_uuid),
    )
    association = test_db.fetchone()
    assert association is not None, "User should be associated with the project after the request."


def test_add_project_user_invalid_user(root_client, projects):
    """Test attempting to add a non-existent user to a project."""
    project_uuid = projects[0]["uuid"]
    non_existent_user_uuid = "invalid-uuid-123-456"

    response = root_client.post(f"/api/projects/{project_uuid}/users", json={"user_uuid": non_existent_user_uuid})

    assert response.status_code == 404
    assert response.json["message"] == f"User with UUID={non_existent_user_uuid} does not exist."


@mock_aws
def test_remove_project_user(root_client, regular_user, projects, user_project_assignment, test_db):
    """Test removing a user from a project."""
    project_uuid = projects[0]["uuid"]
    user_uuid = regular_user[0]

    # Setup mocked SNS topic
    sns_topic_arn = setup_mock_sns_topic(project_uuid)
    test_db.execute(
        """
        UPDATE projects SET sns_topic_arn = %s WHERE uuid = %s
        """,
        (sns_topic_arn, project_uuid),
    )

    # Verify the user is associated
    test_db.execute(
        """
        SELECT * FROM projects_users
        WHERE project_id = (SELECT id FROM projects WHERE uuid = %s)
        AND user_id = (SELECT id FROM users WHERE uuid = %s)
        """,
        (project_uuid, user_uuid),
    )
    association = test_db.fetchone()
    assert association is not None, "User should be associated with the project before removal."

    response = root_client.delete(f"/api/projects/{project_uuid}/users/{user_uuid}")

    assert response.status_code == 204

    # Verify the user is no longer associated
    test_db.execute(
        """
        SELECT * FROM projects_users
        WHERE project_id = (SELECT id FROM projects WHERE uuid = %s)
        AND user_id = (SELECT id FROM users WHERE uuid = %s)
        """,
        (project_uuid, user_uuid),
    )
    association = test_db.fetchone()
    assert association is None, "User should no longer be associated with the project after removal."


def test_remove_project_user_invalid_user(root_client, projects):
    """Test attempting to remove a non-existent user from a project."""
    project_uuid = projects[0]["uuid"]
    non_existent_user_uuid = "invalid-uuid-123-456"

    response = root_client.delete(f"/api/projects/{project_uuid}/users/{non_existent_user_uuid}")

    assert response.status_code == 404
    assert response.json["message"] == "Project or user not found."