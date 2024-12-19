from moto import mock_aws
from unittest.mock import patch
from tests.test_helpers import setup_mock_sns_topic

@mock_aws
@patch("app.routes.notifications.send_notification_to_frontend")
def test_webhook_success(mock_frontend, client, projects, webhook_payload, test_db):
    """Test successful webhook handling with mocked AWS SNS."""
    mock_frontend.return_value = None
    
    # Set up mocked SNS
    project_uuid = webhook_payload["project_id"]
    sns_topic_arn = setup_mock_sns_topic(project_uuid)
    test_db.execute(
        """
        UPDATE projects SET sns_topic_arn = %s WHERE uuid = %s
        """,
        (sns_topic_arn, project_uuid),
    )

    response = client.post("/api/notifications/webhook", json=webhook_payload)

    # Assertions
    assert response.status_code == 200
    assert response.json["message"] == "Webhook received."
    mock_frontend.assert_called_once_with(webhook_payload["project_id"])
    

def test_webhook_missing_payload(client):
    """Test webhook handling with a missing payload."""
    response = client.post(
        "/api/notifications/webhook", 
        json={},
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400
    assert response.json["message"] == "Invalid request"