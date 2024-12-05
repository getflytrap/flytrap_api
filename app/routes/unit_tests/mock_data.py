MOCK_DATA = {
  "create_project": {
      "payload": {
          "uuid": "dajhew32876dcx79sd2332",
          "name": "testing123",
          "platform": "react",
          "api_key": "api_key_123"
      }
  },
  "fetch_projects": {
        "projects": [
            {
                "uuid": "dajhew32876dcx79sd2332",
                "issue_count": 0,
                "name": "testing123",
                "api_key": "api_key_123",
                "platform": "react"
            }
        ],
        "status": "success"
    },
    "add_project": {
      ""
    },
    "mock_user": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@doe.com",
        "password": "password123",
        "confirmed_password": "password123"
    }
}

class status_codes:
    HTTP_201_CREATED = 201
    HTTP_200_OK = 200
    HTTP_400_BAD_REQUEST = 400
    HTTP_204_NO_CONTENT = 204