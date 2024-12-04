# Flytrap API

The Flytrap API is Flytrap's backend system designed to manage projects, users, and issues (errors/rejections) related to projects. It provides an API for handling user authentication, project creation, and issue management, along with WebSocket and webhook-based notifications.

## Overview

Flytrap is built with Flask, deployed on AWS EC2. The project includes various endpoints for managing users, projects, and issues. It also integrates a notification system via WebSockets and webhooks to alert users about errors within their projects.

This guide provides setup instructions for running the Flytrap API locally for development purposes.

**Note:** For real-world use or deployment of Flytrap in a production environment, please refer to the official [Flytrap installation guide](#) for full instructions on setting up the product in a live environment.

## Getting Started
These instructions cover setting up Flytrap locally for development and testing. If you intend to use Flytrap for production, follow the specific deployment and infrastructure setup provided in the product documentation.

### Prerequisites

1. Python 3.8 or higher
2. PostgreSQL database and a PostgreSQL client (`psql`)
3. Docker (optional, for containerized setup)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/flytrap-api.git
    cd flytrap-api
    ```

2. Create a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up the .env file with the necessary environment variables (e.g., database URL, JWT secret, etc.). Example:

    ```bash
    FLASK_APP=flytrap.py
    FLASK_ENV=development
    PGUSER=<your_pg_user>
    PGHOST=localhost
    PGDATABASE=<your_pg_db>
    PGPASSWORD=<your_pg_password>
    PGPORT=5432
    JWT_SECRET_KEY=SECRET
    HTTPONLY=True
    SECURE=True
    SAMESITE=None
    USAGE_PLAN_ID=api-gateway-usage-plan-id
    AWS_REGION=us-east-1
    ```

5. Run the application:

    ```bash
    python flytrap.py
    ```

### Running with Docker
You can also run the API in a Docker container for a consistent development environment.

1. Build the Docker image:

    ```bash
    docker build -t flytrap-api .
    ```

2. Run the container:

    ```bash
    docker run -p 5000:5000 flytrap-api
    ```

## API Documentation
For detailed API routes, refer to the [API Documentation](#).

## Technologies Used
- Flask: Python web framework for building the API.
- PostgreSQL: Relational database used for storing data.
- JWT: JSON Web Tokens for user authentication and authorization.
- WebSocket: Real-time notifications for users.
- Docker: For containerizing the application.
