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
  "status": "success",
  "data": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "is_root": true,
      "created_at": "2023-10-01T12:00:00Z"
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
  "status": "success",
  "data": {
    "user_id": 1,
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### 1.3 DELETE /api/users/:user_id
Deletes a specific user by ID.

**Authorization**: Requires root access.

#### Example Response
Empty response with status 204 on success.


### 1.4 PATCH /api/users/:user_id
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
        "project_id": "6f4c2c48-bf42-4f8e-ae1c-f5c53e87bcd1",
        "project_name": "React Shopping Cart App",
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
  "status": "success",
  "data": {
    "project_id": "6e3f2a78-3c8f-4555-9f90-6c11a21c3b62",
    "project_name": "My Project Name"
  }
}
```

### 2.3 DELETE /api/projects/:pid
Deletes a project with the specified project ID.

**Authorization**: Requires root access.

#### Example Response
Empty response with status 204 on success.


### 2.4 PATCH /api/projects/:pid
Updates the name of a project.

**Authorization**: Requires root access.

#### Expected Payload
```json
{
  "new_name": "Updated Project Name"
}
```

#### Example Response
```json
{
  "status": "success",
  "data": {
    "project_id": "6e3f2a78-3c8f-4555-9f90-6c11a21c3b62",
    "project_name": "Updated Project Name"
  }
}
```

---
## 3. Issue Management for Projects

### 3.1 GET /api/projects/:pid/issues
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
  "status": "success",
  "data": {
    "errors": [
      {
        "error_id": 1,
        "name": "Database Connection Error",
        "message": "Unable to connect to the database.",
        "created_at": "2024-10-03T09:20:00Z",
        "line_number": 45,
        "col_number": 15,
        "project_id": "123e4567-e89b-12d3-a456-426614174000",
        "handled": false,
        "resolved": false
      }
    ],
    "total_pages": 1,
    "current_page": 1
  }
}
```

### 3.2 DELETE /api/projects/:pid/issues
Deletes all issues related to a project.

**Authorization**: Requires user access.

#### Example Response
Empty response with status 204 on success.

### 3.3 GET /api/projects/:pid/errors/:eid
Retrieves a specific error by ID.

**Authorization**: Requires user access.

#### Example Response
```json
{
  "status": "success",
  "data": {
    "error_id": 1,
    "name": "Database Connection Error",
    "message": "Unable to connect to the database.",
    "created_at": "2024-10-03T09:20:00Z",
    "line_number": 45,
    "col_number": 15,
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "stack_trace": "Traceback (most recent call last):...",
    "handled": false,
    "resolved": false
  }
}
```

### 3.4 GET /api/projects/:pid/rejections/:rid
Retrieves a specific rejection by ID.

**Authorization**: Requires user access.

#### Example Response
```json
{
  "status": "success",
  "data": {
    "rejection_id": 1,
    "value": "Promise rejected",
    "handled": false,
    "resolved": false
  }
}
```

### 3.5 PATCH /api/projects/:pid/errors/:eid
Updates the resolved state of an error.

**Authorization**: Requires user access.

#### Expected Payload
```json
{
  "resolved": true
}
```

#### Example Response
```json
{
  "status": "success",
  "message": "Error resolved state updated successfully"
}
```

### 3.6 PATCH /api/projects/:pid/rejections/:rid
Updates the resolved state of an error.

**Authorization**: Requires user access.

#### Expected Payload
```json
{
  "resolved": true
}
```

#### Example Response
```json
{
  "status": "success",
  "message": "Rejection resolved state updated successfully"
}
```

### 3.7 DELETE /api/projects/:pid/errors/:eid
Deletes a specific error by ID.

**Authorization**: Requires user access.

#### Example Response
Empty response with status 204 on success.

### 3.8 DELETE /api/projects/:pid/rejections/:rid
Deletes a specific rejection by ID.

**Authorization**: Requires user access.

#### Example Response
Empty response with status 204 on success.

---


## 4. Project-User Management

### 4.1 GET /api/projects/:pid/users
Fetches users associated with a project.

**Authorization**: Requires root access.

#### Example Response
```json
{
  "status": "success",
  "data": [1, 5, 7]
}
```

### 4.2 POST /api/projects/:pid/users
Adds a user to a project.

**Authorization**: Requires user access.

#### Expected Payload
```json
{
  "user_id": 1
}
```

#### Example Response
```json
{
  "status": "success",
  "message": "Successfully added user to project"
}
```

### 4.3 DELETE /api/projects/:pid/users/:id
Removes a user from a project.

**Authorization**: Requires user access.

#### Example Response
```json
{
  "status": "success",
  "message": "Successfully removed user from project"
}
```

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
  "status": "success",
  "access_token": "JWT_TOKEN"
}
```

### 5.2 GET /api/auth/logout
Logs out a user by clearing the refresh token cookie.

#### Example Response
Redirects to login page with refresh token cleared.

---