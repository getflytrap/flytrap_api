from datetime import datetime, timedelta

raw_users = {
    "root_user": {
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@admin.com",
        "password": "password",
        "confirmed_password": "password123",
    },
    "regular_user": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@doe.com",
        "password": "testpassword",
        "confirmed_password": "testpassword",
    },
    "new_user": {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@smith.com",
        "password": "securepassword",
        "confirmed_password": "securepassword",
    },
}

processed_users = {
    "root_user": {
        "uuid": "root-uuid-123-456-789",
        "first_name": "Flytrap",
        "last_name": "Admin",
        "email": "admin@admin.com",
        "password_hash": "$2b$12$5voKL8Dzp9muUhSZ/bsPL.JkWaDja.jrvBFk2wMfmOn.ILBLBvksW",
        "is_root": True,
    },
    "regular_user": {
        "uuid": "user-uuid-123-456-789",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@doe.com",
        "password_hash": "$2b$12$7Ze4nBXlTV04y8ls2PiHce0ecpBgjO.uOiuVx5WobS7SCQDELZzNS",
        "is_root": False,
    },
}

raw_projects = {
    "new_project": {
        "name": "New Project",
        "platform": "React"
    }
}

processed_projects = [
    {
        "uuid": "project-uuid-123-456",
        "name": "Project 1",
        "api_key": "test-api-key-123",
        "platform": "Express",
        "sns_topic_arn": "arn:aws:sns:us-east-1:123456789012:project1-topic",
    },
    {
        "uuid": "project-uuid-456-789",
        "name": "Project 2",
        "api_key": "test-api-key-456",
        "platform": "React",
        "sns_topic_arn": "arn:aws:sns:us-east-1:123456789012:project2-topic",
    },
]

project_assignment = {
    "user_uuid": "user-uuid-123-456-789",
    "project_uuid": "project-uuid-123-456",
}

errors = [
    {
        "uuid": "error-uuid-123-456",
        "name": "Dummy Error",
        "message": "Dummy Message",
        "created_at": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),  # Yesterday,
        "filename": "dummy.js",
        "line_number": 89,
        "col_number": 23,
        "project_id": 1,
        "stack_trace": "Dummy Stack",
        "handled": False,
        "resolved": False,
        "contexts": [
            {"file": "dummy.js", "line": 89, "column": 23, "context": "Dummy Context"}
        ],
        "method": "POST",
        "path": "/api/v1/resource",
        "ip": "7635fc03b5d6a1deda3b9312b5b3dhs65",
        "os": "macOS",
        "browser": None,
        "runtime": "Node.js 18.12.1",
        "error_hash": "5b499c03b5d6a1deda3b9312b5b3b72c",
    },
    {
        "uuid": "error-uuid-789-012",
        "name": "Dummy Error",
        "message": "Dummy Message",
        "created_at": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),  # Yesterday,
        "filename": "dummy.jsx",
        "line_number": 112,
        "col_number": 15,
        "project_id": 2,
        "stack_trace": "Dummy Stack",
        "handled": False,
        "resolved": False,
        "contexts": [
            {"file": "dummy.py", "line": 112, "column": 15, "context": "Dummy Context"}
        ],
        "method": "POST",
        "path": "/api/v1/resource",
        "ip": "7635fc03b5d6a1deda3b9312b5b3dhs65",
        "os": "macOS",
        "browser": "Chrome 119.0",
        "runtime": None,
        "error_hash": "5b499c03b5d6a1deda3b9312b5b3b72c",
    }
]

rejections = [
    {
        "uuid": "rejection-uuid-123",
        "value": "Dummy Rejection Value",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Today,
        "project_id": 1, 
        "handled": False,
        "resolved": False,
        "method": "POST",
        "path": "/submit-form",
        "ip": "7635fc03b5d6a1deda3b9312b5b3dhs65",
        "os": "macOS",
        "browser": None,
        "runtime": "Node.js 18.12.1",
    },
    {
        "uuid": "rejection-uuid-456",
        "value": "Dummy Rejection Value",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Today,
        "project_id": 2,  
        "handled": True,
        "resolved": False,
        "method": "PUT",
        "path": "/upload-file",
        "ip": "7635fc03b5d6a1deda3b9312b5b3dhs65",
        "os": "macOS",
        "browser": "Safari 17.0",
        "runtime": None,
    },
]
