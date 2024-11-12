"""App initialization module.

This module defines the `create_app` function, which initializes and configures
the Flask application.
It sets up Cross-Origin Resource Sharing (CORS), registers route blueprints,
configures error handling,
and initializes authentication mechanisms.
"""

import traceback
from flask import Flask, jsonify
from flask_cors import CORS
from app.routes import (
    projects_bp,
    issues_bp,
    project_users_bp,
    users_bp,
    auth_bp,
    webhook_bp,
)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, supports_credentials=True, expose_headers=["New-Access-Token"])

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        print("Error: ", e)
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

    app.register_blueprint(projects_bp, url_prefix="/api/projects")
    app.register_blueprint(issues_bp, url_prefix="/api/projects/<project_uuid>/issues")
    app.register_blueprint(
        project_users_bp, url_prefix="/api/projects/<project_uuid>/users"
    )
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(webhook_bp, url_prefix="/api/webhook")

    return app
