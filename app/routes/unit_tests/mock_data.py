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
                "uuid": "12321312",
                "name": "project1",
                "api_key": "23423432432324",
                "platform": "flask"
            }
        ],
        "status": "success"
    },
    "add_project": {
      ""
    }
}

class status_codes:
    HTTP_201_CREATED = 201
    HTTP_200_OK = 200
    HTTP_400_BAD_REQUEST = 400
    HTTP_204_NO_CONTENT = 204