from unittest.mock import patch
from mock_data import MOCK_DATA, status_codes


@patch("app.routes.users.bcrypt.hashpw")
@patch("app.routes.users.generate_uuid")
def test_create_user(mock_generate_uuid, mock_hashpw, client):
    mock_generate_uuid.return_value = "dkfhjk32ds62hj2d323d"
    expected_hash = b"$2b$12$FzBxHWuR10BbrKgR99CfGuMyNxpSBBVpgacAb3lNktLgEAO9NmwTa"
    mock_hashpw.return_value = expected_hash

    response = client.post("/api/users", json=MOCK_DATA["mock_user"])
    response_json = response.get_json()

    assert response.status_code == status_codes.HTTP_201_CREATED
    assert response_json["payload"] == {
        "uuid": mock_generate_uuid.return_value,
        "first_name": MOCK_DATA["mock_user"]["first_name"],
        "last_name": MOCK_DATA["mock_user"]["last_name"],
        "email": MOCK_DATA["mock_user"]["email"],
        "is_root": False,
    }


def test_change_user_password(client):
    response = client.patch(
        "/api/users/dkfhjk32ds62hj2d323d", json={"password": "new_password"}
    )

    assert response.status_code == status_codes.HTTP_204_NO_CONTENT


@patch("app.routes.project_users.create_sns_subscription")
def test_add_user_to_project(mock_create_sns_subscription, client):
    response = client.post(
        "/api/projects/fdlkj432987jh43hjkds/users",
        json={"user_uuid": "dkfhjk32ds62hj2d323d"},
    )

    assert response.status_code == status_codes.HTTP_204_NO_CONTENT


def test_get_user_projects(client):
    response = client.get("/api/users/dkfhjk32ds62hj2d323d/projects")
    response_json = response.get_json()

    assert response_json["payload"] == MOCK_DATA["fetch_user_projects"]
    assert response.status_code == status_codes.HTTP_200_OK


@patch("app.routes.project_users.remove_sns_subscription")
def test_remove_user_from_project(mock_remove_sns_subscription, client):
    response = client.delete(
        "api/projects/fdlkj432987jh43hjkds/users/dkfhjk32ds62hj2d323d"
    )

    assert response.status_code == status_codes.HTTP_204_NO_CONTENT


def test_cannot_add_root_user_to_project(client):
    response = client.post(
        "api/projects/fdlkj432987jh43hjkds/users",
        json={"user_uuid": "root-uuid-123-456-789"},
    )
    response_json = response.get_json()

    assert response_json["message"] == "Admin cannot be added to projects."
    assert response.status_code == status_codes.HTTP_400_BAD_REQUEST


def test_delete_user(client):
    response = client.delete("api/users/dkfhjk32ds62hj2d323d")

    assert response.status_code == status_codes.HTTP_204_NO_CONTENT
