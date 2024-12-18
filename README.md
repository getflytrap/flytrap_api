![Organization Logo](https://raw.githubusercontent.com/getflytrap/.github/main/profile/flytrap_logo.png)

# Flytrap API

The Flytrap API is the backend system that powers Flytrap, providing robust functionality for managing users, projects, and issues (errors/rejections). It supports user authentication, project management, and error tracking, along with near real-time notifications via WebSockets and Amazon SNS.

This guide explains how to set up the Flytrap API locally for development and testing purposes. If you want to use Flytrap in a production environment, refer to the [Flytrap Installation Guide](https://github.com/getflytrap/flytrap_terraform) for complete setup instructions.

To learn more about Flytrap, check out our [case study](https://getflytrap.github.io/).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🛠️ Key Features
- **User Authentication:** Secure authentication using JWT tokens.
- **Project Management:** Create, update, and manage projects within Flytrap.
- **Error Tracking:** Handle and analyze errors or rejections reported by applications.
- **Near Real-Time Notifications:** Receive updates via WebSockets and webhook integrations.
- **Scalable Design:** Built with Flask and PostgreSQL, designed for deployment on AWS EC2.

## 🚀 Getting Started
These instructions cover setting up Flytrap locally for development and testing. If you intend to use Flytrap for production, follow the specific deployment and infrastructure setup provided in the [installation guide](https://github.com/getflytrap/flytrap_terraform).

### Prerequisites

1. Python 3.8 or higher
2. PostgreSQL database and a PostgreSQL client (`psql`)
3. Docker (optional, for containerized setup)

### Installation Steps

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

### 🐳 Running with Docker
You can also run the API in a Docker container for a consistent development environment.

1. Build the Docker image:

    ```bash
    docker build -t flytrap-api .
    ```

2. Run the container:

    ```bash
    docker run -p 5000:5000 flytrap-api
    ```

## 🖥️ End-to-End Testing with the Flytrap Architecture
To test the Flytrap API as part of the complete Flytrap architecture, set up the necessary components to have the full system running locally. This includes installing the Flytrap Dashboard, Flytrap Processor, and integrating one of the Flytrap SDKs into your application.

### Prerequisites
1. **Install the Flytrap Dashboard:** Follow the instructions in the [Flytrap Dashboard Repository](https://github.com/getflytrap/flytrap_ui) to set up the dashboard locally. This will allow you to view and manage processed error data.

2. **Install the Flytrap Processor:** The Flytrap Processor handles error data sent from SDKs and stores it in the database. Refer to the [Flytrap Processor Repository](https://github.com/getflytrap/flytrap_processor) for setup instructions.

3. **Integrate Flytrap SDKs:** Add one of the Flytrap SDKs to your application to start collecting error data:

    [Flytrap React SDK](https://github.com/getflytrap/flytrap_react)  
    [Flytrap Vanilla JavaScript SDK](https://github.com/getflytrap/flytrap_javascript)  
    [Flytrap Express SDK](https://github.com/getflytrap/flytrap_express)  
    [Flytrap Flask SDK](https://github.com/getflytrap/flytrap_flask)  

4. **Generating Errors:** Trigger errors or promise rejections in your application integrated with the Flytrap SDK. The SDK will send error payloads via the Flytrap Processor to the Flytrap API. 

5. **Verifying Processing:** View in the Dashboard: Open the Flytrap Dashboard to verify that the errors are displayed correctly.

## 📂 API Endpoints
For detailed API routes, refer to the [API Documentation](https://github.com/getflytrap/flytrap_api/blob/main/docs/api.md).

## 🔧 Technologies Used
- Flask: Python web framework for building the API.
- PostgreSQL: Relational database used for storing data.
- JWT: JSON Web Tokens for user authentication and authorization.
- WebSocket: Real-time notifications for users.
- Docker: For containerizing the application.

For questions or issues, feel free to open an issue in this repository or contact the Flytrap team. 🚀

---

<div align="center">
  🪰🪤🪲🌱🚦🛠️🪴
</div>
