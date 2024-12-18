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

projects = [
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
        "platform": "Flask",
        "sns_topic_arn": "arn:aws:sns:us-east-1:123456789012:project2-topic",
    },
]

project_assignment = {
    "user_uuid": "user-uuid-123-456-789",
    "project_uuid": "project-uuid-123-456",
}

