MOCK_DATA = {
    "mock_project": {
        "payload": {
            "uuid": "dajhew32876dcx79sd2332",
            "name": "testing123",
            "platform": "react",
            "api_key": "api_key_123",
        }
    },
    "fetch_projects": {
        "projects": [
            {
                "uuid": "fdlkj432987jh43hjkds",
                "issue_count": 1,
                "name": "dummy_project",
                "api_key": "api_key_789",
                "platform": "flask",
            },
            {
                "uuid": "dajhew32876dcx79sd2332",
                "name": "testing123",
                "issue_count": 0,
                "platform": "react",
                "api_key": "api_key_123",
            },
        ],
        "status": "success",
    },
    "add_project": {""},
    "mock_user": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@doe.com",
        "password": "password123",
        "confirmed_password": "password123",
    },
    "fetch_user_projects": {
        "current_page": 1,
        "total_pages": 1,
        "projects": [
            {
                "api_key": "api_key_789",
                "issue_count": 1,
                "name": "dummy_project",
                "platform": "flask",
                "uuid": "fdlkj432987jh43hjkds",
            }
        ],
    },
    "mock_error": {
        "uuid": "jkhas894jhkchjkl",
        "name": "dummy error",
        "message": "dummy message",
        "created_at": "2023-07-14 15:23:45",
        "filename": "dummy.py",
        "line_number": 89,
        "col_number": 23,
        "project_id": 1,
        "stack_trace": "dummy stack",
        "handled": False,
        "resolved": False,
        "contexts": [
            {"file": "dummy.py", "line": 89, "column": 23, "context": "Dummy Context"}
        ],
        "method": "POST",
        "path": "/api/v1/resource",
        "ip": "123.4.3.5",
        "os": "MacOS",
        "browser": "Chrome 96",
        "runtime": "Python 3.9.7",
        "error_hash": "dslajl234lsjl4",
    },
}


class status_codes:
    HTTP_201_CREATED = 201
    HTTP_200_OK = 200
    HTTP_400_BAD_REQUEST = 400
    HTTP_204_NO_CONTENT = 204
    HTTP_500_SERVER_ERROR = 500
