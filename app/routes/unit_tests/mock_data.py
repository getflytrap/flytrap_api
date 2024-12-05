MOCK_DATA = {
  "mock_project": {
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
                "uuid": "fdlkj432987jh43hjkds",
                "issue_count": 0,
                "name": "dummy_project",
                "api_key": "api_key_789",
                "platform": "flask"
            },
            {
                "uuid": "dajhew32876dcx79sd2332",
                "name": "testing123",
                "issue_count": 0,
                "platform": "react",
                "api_key": "api_key_123"
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
    },
    "fetch_user_projects": {
        "current_page": 1,
        "total_pages": 1,
        "projects": [{
            'api_key': 'api_key_789',
            'issue_count': 0,
            'name': 'dummy_project',
            'platform': 'flask',
            'uuid': 'fdlkj432987jh43hjkds',
        }]
    }
}

class status_codes:
    HTTP_201_CREATED = 201
    HTTP_200_OK = 200
    HTTP_400_BAD_REQUEST = 400
    HTTP_204_NO_CONTENT = 204