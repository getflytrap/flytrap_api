# API Documentation

## Table of Contents
1. [User Management](#1-user-management)
2. [Project Management](#2-project-management)
3. [Issue Management for Projects](#3-issue-management-for-projects)
4. [Project-User Management](#4-project-user-management)
5. [Authentication](#5-authentication)

# 1. User Management
### 1.1 GET /api/users
Fetches all users.

**Authorization**: Requires root access.

#### Example Response
```json
{
  "payload": [
    {
      "uuid": "056ec265-79e0-4c03-8017-895eccd2cc05",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "is_root": true,
    }
  ]
}
```

### 1.2 POST /api/users
Creates a new user.

**Authorization**: Requires root access.

#### Expected Payload
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "password": "password123",
  "confirmed_password": "password123"
}
```

#### Example Response
```json
{
  "payload": {
    "uuid": "056ec265-79e0-4c03-8017-895eccd2cc05",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "is_root": false,
  }
}
```

### 1.3 GET /api/users/me
Gets session info if current user is logged in.

#### Example Response
```json
{
  "payload": {
    "uuid": "056ec265-79e0-4c03-8017-895eccd2cc05",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "is_root": false,
  }
}
```

### 1.4 DELETE /api/users/:user_uuid
Deletes a specific user by UUID.

**Authorization**: Requires root access.

#### Example Response
Empty response with status 204 on success.


### 1.5 PATCH /api/users/:user_uuid
Updates a user's password.

**Authorization**: Requires user access.

#### Expected Payload
```json
{
  "password": "new_password123"
}
```

#### Example Response
Empty response with status 204 on success.

### 1.6 GET /api/:user_uuid/projects
Retrieves all projects assigned to a specific user by user UUID.

**Authorization**: Requires user access.

#### Query Parameters
| Parameter | Type    | Description                                            |
|-----------|---------|--------------------------------------------------------|
| `page`    | Integer | Page number for pagination. Defaults to 1.             |
| `limit`   | Integer | Number of items per page. Defaults to 10.              |

#### Example Response (Success)
```json
{
  "payload": {
    "projects": [
      {
        "uuid": "1234-5678-90ab-cdef",
        "name": "Project Alpha"
      },
      {
        "uuid": "abcd-1234-efgh-5678",
        "name": "Project Beta"
      }
    ],
    "total_pages": 1,
    "current_page": 1,
  }
}
```

---


## 2. Project Management

### 2.1 GET /api/projects
Fetches all projects from the database with pagination.

**Authorization**: Requires root access.

#### Query Parameters
| Parameter | Type    | Description                                            |
|-----------|---------|--------------------------------------------------------|
| `page`    | Integer | Page number for pagination. Defaults to 1.             |
| `limit`   | Integer | Number of items per page. Defaults to 10.              |

#### Example Response
```json
{
  "status": "success",
  "data": {
    "projects": [
      {
        "uuid": "6f4c2c48-bf42-4f8e-ae1c-f5c53e87bcd1",
        "name": "React Shopping Cart App",
        "api_key": "9f4c2c48-bf42-4f8e-ae1c-f5c53e87c8ed",
        "platform": "React",
        "issue_count": 3
      }
    ],
    "total_pages": 1,
    "current_page": 1
  }
}
```

### 2.2 POST /api/projects
Creates a new project.

**Authorization**: Requires root access.

#### Expected Payload
```json
{
  "name": "My Project Name"
}
```

#### Example Response
```json
{
  "payload": {
    "uuid": "6e3f2a78-3c8f-4555-9f90-6c11a21c3b62",
    "name": "My Project Name",
    "platform": "React",
    "api_key": "9f4c2c48-bf42-4f8e-ae1c-f5c53e87c8ed",
  }
}
```

### 2.3 DELETE /api/projects/:project_uuid
Deletes a project with the specified project UUID.

**Authorization**: Requires root access.

#### Example Response
Empty response with status 204 on success.


### 2.4 PATCH /api/projects/:project_uuid
Updates the name of a project.

**Authorization**: Requires root access.

#### Expected Payload
```json
{
  "new_name": "Updated Project Name"
}
```

#### Example Response
Empty response with status 204 on success.

---
## 3. Issue Management for Projects

### 3.1 GET /api/projects/:project_uuid/issues
Fetches issues (errors and rejections) associated with a project.

**Authorization**: Requires user access.

#### Query Parameters
| Parameter | Type    | Description                                  |
|-----------|---------|----------------------------------------------|
| `page`    | Integer | Page number for pagination (default 1).      |
| `limit`   | Integer | Number of items per page (default 10).       |
| `handled` | Boolean | Filter by handled/unhandled status.          |
| `resolved`| Boolean | Filter by resolved/unresolved status.        |
| `time`    | String  | Filters items created on/after specified time.|

#### Example Response
```json
{
  "payload": {
    "issues": [
      {
        "uuid": "789g4567-e89b-12d3-a456-4266141741111",
        "name": "Database Connection Error",
        "message": "Unable to connect to the database.",
        "created_at": "2024-10-03T09:20:00Z",
        "file": "app.js",
        "line_number": 45,
        "col_number": 15,
        "project_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "handled": false,
        "resolved": false,
        "total_occurrences": 3,
        "distinct_users": 2,
      }
    ],
    "total_pages": 1,
    "current_page": 1
  }
}
```

### 3.2 DELETE /api/projects/:project_uuid/issues
Deletes all issues related to a project.

**Authorization**: Requires user access.

#### Example Response
Empty response with status 204 on success.

### 3.3 GET /api/projects/:project_uuid/issues/errors/:error_uuid
Retrieves a specific error by ID.

**Authorization**: Requires user access.

#### Example Response
```json
{
  "payload": {
    "uuid": "sample-uuid-1234-5678",
    "name": "Database Connection Error",
    "message": "Unable to connect to the database.",
    "created_at": "2024-10-03T09:20:00Z",
    "line_number": 45,
    "col_number": 15,
    "project_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "stack_trace": "Traceback (most recent call last):...",
    "handled": false,
    "resolved": false,
    "contexts": [
                  {
                    "file": "src/app.js",
                    "line": 42,
                    "column": 18,
                    "context": "function handleError() { ... }"
                  },
                  {
                    "file": "src/utils/helpers.js",
                    "line": 58,
                    "column": 23,
                    "context": "const data = fetchData(url);"
                  }
                ],
    "method": "GET",
    "path": "/home",
    "os": "MacOS",
    "browser": "Chrome",
    "runtime": null, 
    "total_occurrences": 5,
    "distinct_users": 3,
  }
}
```

### 3.4 GET /api/projects/:project_uuid/issues/rejections/:rejection_uuid
Retrieves a specific rejection by ID.

**Authorization**: Requires user access.

#### Example Response
```json
{
  "payload": {
    "uuid": "sample-uuid-1234-5678",
    "value": "Promise rejected",
    "project_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "handled": false,
    "resolved": false,
    "method": "GET",
    "path": "/home",
    "os": "MacOS",
    "browser": "Chrome",
    "runtime": null, 
  }
}
```

### 3.5 PATCH /api/projects/:project_uuid/issues/errors/:error_uuid
Updates the resolved state of an error.

**Authorization**: Requires user access.

#### Expected Payload
```json
{
  "resolved": true
}
```

#### Example Response
Empty response with status 204 on success.

### 3.6 PATCH /api/projects/:project_uuid/issues/rejections/:rejection_uuid
Updates the resolved state of an error.

**Authorization**: Requires user access.

#### Expected Payload
```json
{
  "resolved": true
}
```

#### Example Response
Empty response with status 204 on success.

### 3.7 DELETE /api/projects/:project_uuid/issues/errors/:error_uuid
Deletes a specific error by ID.

**Authorization**: Requires user access.

#### Example Response
Empty response with status 204 on success.

### 3.8 DELETE /api/projects/:project_uuid/issues/rejections/:rejection_uuid
Deletes a specific rejection by ID.

**Authorization**: Requires user access.

#### Example Response
Empty response with status 204 on success.

### 3.9 GET /api/projects/:project_uuid/issues/summary
Gets a summary of issue counts for the last 7 days for the given project ID.

#### Example Response
```json 
{
  "payload": [10, 25, 7, 80, 76, 21, 17]
}

```

---


## 4. Project-User Management

### 4.1 GET /api/projects/:project_uuid/users
Fetches users associated with a project.

**Authorization**: Requires root access.

#### Example Response
```json
{
  "payload": ["d614a8c7-0288-4850-a9a8-a647b1133d1", "f614a8c7-0288-4850-a9a8-a647b113gh67"]
}
```

### 4.2 POST /api/projects/:project_uuid/users
Adds a user to a project.

**Authorization**: Requires user access.

#### Expected Payload
```json
{
  "user_uuid": "d614a8c7-0288-4850-a9a8-a647b1133d15"
}
```

#### Example Response
Empty response with 204 status on success.

### 4.3 DELETE /api/projects/:project_uuid/users/:user_uuid
Removes a user from a project.

**Authorization**: Requires user access.

#### Example Response
Empty response with 204 status on success.

---


## 5. Authentication

### 5.1 POST /api/auth/login
Logs in a user and issues JWT tokens.

#### Expected Payload
```json
{
  "email": "john.doe@example.com",
  "password": "password123"
}
```

#### Example Response
```json
{
  "payload": {
    "access_token": "JWT_TOKEN",
    "user": {
      "uuid": "d614a8c7-0288-4850-a9a8-a647b1133d15",
      "first_name": "John",
      "last_name": "Doe",
      "is_root": "False",
    }
  }
}
```

### 5.2 GET /api/auth/logout
Logs out a user by clearing the refresh token cookie.

#### Example Response
Empty response with 204 status on success. Refresh token cleared.

### 5.3 POST /api/auth/refresh
Refreshes the user's access token.

#### Example Response
```json
{
  "payload": "NEW_ACCESS_TOKEN"
}
```

---

## 6. Notifications

### 6.1 POST /api/notifications/webhook
Receives a webhook notification.

#### Expected Payload
```json
{
  "project_id": "d614a8c7-0288-4850-a9a8-a647b1133d15"
}
```

#### Example Response
```json
{
  "message": "Webhook received."
}