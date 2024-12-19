def test_get_issues_root(root_client, projects, errors, rejections):
    """Test fetching issues for a specific project authenticated as root user."""
    project_uuid = projects[0]["uuid"]

    response = root_client.get(f"/api/projects/{project_uuid}/issues", query_string={"page": 1, "limit": 10})
    
    assert response.status_code == 200
    assert "payload" in response.json
    assert len(response.json["payload"]["issues"]) == 2

    
def test_get_issues_regular(regular_client, projects, user_project_assignment, errors, rejections):
    """Test fetching issues for a specific project authenticated as regular user."""
    project_uuid = projects[0]["uuid"]

    response = regular_client.get(f"/api/projects/{project_uuid}/issues", query_string={"page": 1, "limit": 10})
    
    assert response.status_code == 200
    assert "payload" in response.json
    assert len(response.json["payload"]["issues"]) == 2


def test_get_issues_regular_unauthorized(regular_client, projects, user_project_assignment, errors, rejections):
    """Test fetching issues for a specific project authenticated as regular user not authorized for this project."""
    project_uuid = projects[1]["uuid"]

    response = regular_client.get(f"/api/projects/{project_uuid}/issues", query_string={"page": 1, "limit": 10})
    
    assert response.status_code == 403
    assert response.json["message"] == "You do not have the necessary permissions to perform this action."


def delete_issues(root_client, projects, errors, rejections, test_db):
    """Test deleting all issues for a specific project."""
    project_uuid = projects[0]["uuid"]

    # Verify issues exist prior to deletion
    test_db.execute("SELECT COUNT(*) FROM error_logs WHERE project_id = (SELECT id FROM projects WHERE uuid = %s)", (project_uuid,))
    assert test_db.fetchone()[0] > 0

    test_db.execute("SELECT COUNT(*) FROM rejection_logs WHERE project_id = (SELECT id FROM projects WHERE uuid = %s)", (project_uuid,))
    assert test_db.fetchone()[0] > 0

    response = root_client.delete(f"/api/projects/{project_uuid}/issues")
    
    assert response.status_code == 204

    # Verify issues were deleted
    test_db.execute("SELECT COUNT(*) FROM error_logs WHERE project_id = (SELECT id FROM projects WHERE uuid = %s)", (project_uuid,))
    assert test_db.fetchone()[0] == 0

    test_db.execute("SELECT COUNT(*) FROM rejection_logs WHERE project_id = (SELECT id FROM projects WHERE uuid = %s)", (project_uuid,))
    assert test_db.fetchone()[0] == 0


def test_get_error_root(root_client, projects, errors):
    """Test fetching a specific error authenticated as root user."""
    project_uuid = projects[0]["uuid"]
    error_uuid = errors[0]["uuid"]

    response = root_client.get(f"/api/projects/{project_uuid}/issues/errors/{error_uuid}")
    
    assert response.status_code == 200
    assert response.json["payload"]["uuid"] == error_uuid


def test_get_error_regular(regular_client, projects, user_project_assignment, errors):
    """Test fetching a specific error authenticated as regular user."""
    project_uuid = projects[0]["uuid"]
    error_uuid = errors[0]["uuid"]

    response = regular_client.get(f"/api/projects/{project_uuid}/issues/errors/{error_uuid}")
    
    assert response.status_code == 200
    assert response.json["payload"]["uuid"] == error_uuid


def test_get_error_regular_unauthorized(regular_client, projects, user_project_assignment, errors):
    """Test fetching a specific error authenticated as regular user not authorized for this project."""
    project_uuid = projects[1]["uuid"]
    error_uuid = errors[1]["uuid"]

    response = regular_client.get(f"/api/projects/{project_uuid}/issues/errors/{error_uuid}")
    
    assert response.status_code == 403
    assert response.json["message"] == "You do not have the necessary permissions to perform this action."


def test_get_error_invalid_uuid(root_client, projects):
    """Test fetching an error with an invalid UUID."""
    project_uuid = projects[0]["uuid"]
    invalid_error_uuid = "invalid-uuid-123-456"

    response = root_client.get(f"/api/projects/{project_uuid}/issues/errors/{invalid_error_uuid}")
    
    assert response.status_code == 404
    assert response.json["message"] == "Error not found."


def test_get_rejection_root(root_client, projects, rejections):
    """Test fetching a specific rejection authenticated as the root user."""
    project_uuid = projects[0]["uuid"]
    rejections_uuid = rejections[0]["uuid"]

    response = root_client.get(f"/api/projects/{project_uuid}/issues/rejections/{rejections_uuid}")
    
    assert response.status_code == 200
    assert response.json["payload"]["uuid"] == rejections_uuid


def test_get_rejection_regular(regular_client, projects, user_project_assignment, rejections):
    """Test fetching a specific rejection authenticated as regular user."""
    project_uuid = projects[0]["uuid"]
    rejection_uuid = rejections[0]["uuid"]

    response = regular_client.get(f"/api/projects/{project_uuid}/issues/rejections/{rejection_uuid}")
    
    assert response.status_code == 200
    assert response.json["payload"]["uuid"] == rejection_uuid


def test_get_rejection_regular_unauthorized(regular_client, projects, user_project_assignment, rejections):
    """Test fetching a specific rejection authenticated as regular user not authorized."""
    project_uuid = projects[1]["uuid"]
    rejection_uuid = rejections[1]["uuid"]

    response = regular_client.get(f"/api/projects/{project_uuid}/issues/rejections/{rejection_uuid}")
    
    assert response.status_code == 403
    assert response.json["message"] == "You do not have the necessary permissions to perform this action."


def test_get_rejection_invalid_uuid(root_client, projects):
    """Test fetching an error with an invalid UUID."""
    project_uuid = projects[0]["uuid"]
    invalid_rejection_uuid = "invalid-uuid-123-456"

    response = root_client.get(f"/api/projects/{project_uuid}/issues/rejections/{invalid_rejection_uuid}")
    
    assert response.status_code == 404
    assert response.json["message"] == "Rejection not found."


def test_toggle_error_resolved_root(root_client, projects, errors, test_db):
    """Test toggling the resolved state of an error authenticated as the root user."""
    project_uuid = projects[0]["uuid"]
    error_uuid = errors[0]["uuid"]

    test_db.execute("SELECT resolved FROM error_logs WHERE uuid = %s", (error_uuid,))
    old_resolved_status = test_db.fetchone()[0]
    assert old_resolved_status is False, "Initial resolved status should be false."
    
    response = root_client.patch(f"/api/projects/{project_uuid}/issues/errors/{error_uuid}", json={"resolved": True})
    
    assert response.status_code == 204

    # Verify resolved state in the database
    test_db.execute("SELECT resolved FROM error_logs WHERE uuid = %s", (error_uuid,))
    updated_resolved_status = test_db.fetchone()[0]
    assert updated_resolved_status is True, "Resolved status should have been updated to True."
    assert old_resolved_status != updated_resolved_status


def test_toggle_error_resolved_regular(regular_client, projects, user_project_assignment, errors, test_db):
    """Test toggling the resolved state of an error authenticated as regular user."""
    project_uuid = projects[0]["uuid"]
    error_uuid = errors[0]["uuid"]

    test_db.execute("SELECT resolved FROM error_logs WHERE uuid = %s", (error_uuid,))
    old_resolved_status = test_db.fetchone()[0]
    assert old_resolved_status is False, "Initial resolved status should be false."
    
    response = regular_client.patch(f"/api/projects/{project_uuid}/issues/errors/{error_uuid}", json={"resolved": True})
    
    assert response.status_code == 204

    # Verify resolved state in the database
    test_db.execute("SELECT resolved FROM error_logs WHERE uuid = %s", (error_uuid,))
    updated_resolved_status = test_db.fetchone()[0]
    assert updated_resolved_status is True, "Resolved status should have been updated to True."
    assert old_resolved_status != updated_resolved_status


def test_toggle_error_resolved_regular_unauthorized(regular_client, projects, user_project_assignment, errors, test_db):
    """Test toggling the resolved state of an error authenticated as regular user not authorized."""
    project_uuid = projects[1]["uuid"]
    error_uuid = errors[1]["uuid"]
    
    response = regular_client.patch(f"/api/projects/{project_uuid}/issues/errors/{error_uuid}", json={"resolved": True})
    
    assert response.status_code == 403
    assert response.json["message"] == "You do not have the necessary permissions to perform this action."


def test_toggle_rejection_resolved_root(root_client, projects, rejections, test_db):
    """Test toggling the resolved state of a rejection authenticated as root user."""
    project_uuid = projects[0]["uuid"]
    rejection_uuid = rejections[0]["uuid"]

    test_db.execute("SELECT resolved FROM rejection_logs WHERE uuid = %s", (rejection_uuid,))
    old_resolved_status = test_db.fetchone()[0]
    assert old_resolved_status is False, "Initial resolved status should be false."
    
    response = root_client.patch(f"/api/projects/{project_uuid}/issues/rejections/{rejection_uuid}", json={"resolved": True})
    
    assert response.status_code == 204

    # Verify resolved state in the database
    test_db.execute("SELECT resolved FROM rejection_logs WHERE uuid = %s", (rejection_uuid,))
    updated_resolved_status = test_db.fetchone()[0]
    assert updated_resolved_status is True, "Resolved status should have been updated to True."
    assert old_resolved_status != updated_resolved_status


def test_toggle_rejection_resolved_regular(regular_client, projects, user_project_assignment, rejections, test_db):
    """Test toggling the resolved state of a rejection authenticated as regular user."""
    project_uuid = projects[0]["uuid"]
    rejection_uuid = rejections[0]["uuid"]

    test_db.execute("SELECT resolved FROM rejection_logs WHERE uuid = %s", (rejection_uuid,))
    old_resolved_status = test_db.fetchone()[0]
    assert old_resolved_status is False, "Initial resolved status should be false."
    
    response = regular_client.patch(f"/api/projects/{project_uuid}/issues/rejections/{rejection_uuid}", json={"resolved": True})
    
    assert response.status_code == 204

    # Verify resolved state in the database
    test_db.execute("SELECT resolved FROM rejection_logs WHERE uuid = %s", (rejection_uuid,))
    updated_resolved_status = test_db.fetchone()[0]
    assert updated_resolved_status is True, "Resolved status should have been updated to True."
    assert old_resolved_status != updated_resolved_status


def test_toggle_rejection_resolved_regular_unauthorized(regular_client, projects, user_project_assignment, rejections, test_db):
    """Test toggling the resolved state of a rejection authenticated as regular user not authorized."""
    project_uuid = projects[1]["uuid"]
    rejection_uuid = rejections[1]["uuid"]
    
    response = regular_client.patch(f"/api/projects/{project_uuid}/issues/rejections/{rejection_uuid}", json={"resolved": True})
    
    assert response.status_code == 403
    assert response.json["message"] == "You do not have the necessary permissions to perform this action."


def test_delete_error_root(root_client, projects, errors, test_db):
    """Test deleting an error as root user."""
    project_uuid = projects[0]["uuid"]
    error_uuid = errors[0]["uuid"]

    # Verify the error exists in the database
    test_db.execute("SELECT * FROM error_logs WHERE uuid = %s", (error_uuid,))
    error = test_db.fetchone()
    assert error is not None, "Error should exist in the database before deletion."

    response = root_client.delete(f"/api/projects/{project_uuid}/issues/errors/{error_uuid}")
    
    assert response.status_code == 204

    # Verify the error exists in the database
    test_db.execute("SELECT * FROM error_logs WHERE uuid = %s", (error_uuid,))
    error = test_db.fetchone()
    assert error is None, "Error should not exist in the database after deletion."
   
    
def test_delete_error_regular(regular_client, projects, user_project_assignment, errors, test_db):
    """Test deleting an error as regular user."""
    project_uuid = projects[0]["uuid"]
    error_uuid = errors[0]["uuid"]

    # Verify the error exists in the database
    test_db.execute("SELECT * FROM error_logs WHERE uuid = %s", (error_uuid,))
    error = test_db.fetchone()
    assert error is not None, "Error should exist in the database before deletion."

    response = regular_client.delete(f"/api/projects/{project_uuid}/issues/errors/{error_uuid}")
    
    assert response.status_code == 204

    # Verify the error exists in the database
    test_db.execute("SELECT * FROM error_logs WHERE uuid = %s", (error_uuid,))
    error = test_db.fetchone()
    assert error is None, "Error should not exist in the database after deletion."


def test_delete_error_regular_unauthorized(regular_client, projects, user_project_assignment, errors, test_db):
    """Test deleting an error as regular user unauthorized."""
    project_uuid = projects[1]["uuid"]
    error_uuid = errors[1]["uuid"]

    # Verify the error exists in the database
    test_db.execute("SELECT * FROM error_logs WHERE uuid = %s", (error_uuid,))
    error = test_db.fetchone()
    assert error is not None, "Error should exist in the database before deletion."

    response = regular_client.delete(f"/api/projects/{project_uuid}/issues/errors/{error_uuid}")
    
    assert response.status_code == 403
    assert response.json["message"] == "You do not have the necessary permissions to perform this action."


def test_delete_rejection_root(root_client, projects, rejections, test_db):
    """Test deleting an rejection as root user."""
    project_uuid = projects[0]["uuid"]
    rejection_uuid = rejections[0]["uuid"]

    # Verify the error exists in the database
    test_db.execute("SELECT * FROM rejection_logs WHERE uuid = %s", (rejection_uuid,))
    rejection = test_db.fetchone()
    assert rejection is not None, "Rejection should exist in the database before deletion."

    response = root_client.delete(f"/api/projects/{project_uuid}/issues/rejections/{rejection_uuid}")
    
    assert response.status_code == 204

    # Verify the error exists in the database
    test_db.execute("SELECT * FROM rejection_logs WHERE uuid = %s", (rejection_uuid,))
    rejection = test_db.fetchone()
    assert rejection is None, "Rejection should not exist in the database after deletion."


def test_delete_rejection_regular(regular_client, projects, user_project_assignment, rejections, test_db):
    """Test deleting an error as regular user."""
    project_uuid = projects[0]["uuid"]
    rejection_uuid = rejections[0]["uuid"]

    # Verify the error exists in the database
    test_db.execute("SELECT * FROM rejection_logs WHERE uuid = %s", (rejection_uuid,))
    rejection = test_db.fetchone()
    assert rejection is not None, "Error should exist in the database before deletion."

    response = regular_client.delete(f"/api/projects/{project_uuid}/issues/rejections/{rejection_uuid}")
    
    assert response.status_code == 204

    # Verify the error exists in the database
    test_db.execute("SELECT * FROM rejection_logs WHERE uuid = %s", (rejection_uuid,))
    error = test_db.fetchone()
    assert error is None, "rejection should not exist in the database after deletion."


def test_delete_error_regular_unauthorized(regular_client, projects, user_project_assignment, rejections, test_db):
    """Test deleting an error as regular user unauthorized."""
    project_uuid = projects[1]["uuid"]
    rejection_uuid = rejections[1]["uuid"]

    # Verify the error exists in the database
    test_db.execute("SELECT * FROM rejection_logs WHERE uuid = %s", (rejection_uuid,))
    rejection = test_db.fetchone()
    assert rejection is not None, "Error should exist in the database before deletion."

    response = regular_client.delete(f"/api/projects/{project_uuid}/issues/rejections/{rejection_uuid}")
    
    assert response.status_code == 403
    assert response.json["message"] == "You do not have the necessary permissions to perform this action."


def test_get_summary(root_client, projects, errors, rejections):
    """Test fetching the issue summary for a project."""
    project_uuid = projects[0]["uuid"]

    response = root_client.get(f"/api/projects/{project_uuid}/issues/summary")
    
    assert response.status_code == 200
    assert "payload" in response.json
    assert isinstance(response.json["payload"], list), "Payload should be a list."
    assert len(response.json["payload"]) == 7, "Payload should contain exactly 7 items."

    expected_summary = [0, 0, 0, 0, 0, 1, 1]
    actual_summary =response.json["payload"]

    assert actual_summary == expected_summary, f"Expected {expected_summary}, but got {actual_summary}."