"""App initialization module.

This module defines the `create_app` function, which initializes and configures
the Flask application.
It sets up Cross-Origin Resource Sharing (CORS), registers route blueprints,
configures error handling,
and initializes authentication mechanisms.
"""
import logging
import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS
from .socketio_instance import socketio
from app.routes import (
    projects_bp,
    issues_bp,
    project_users_bp,
    users_bp,
    auth_bp,
    notifications_bp,
)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, supports_credentials=True, expose_headers=["New-Access-Token"])
    socketio.init_app(app)

    handler = logging.StreamHandler()  # Send logs to stderr (console)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)
    app.config['LOGGER_HANDLER_POLICY'] = 'always'
    logging.getLogger('botocore').setLevel(logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.DEBUG)
    logging.getLogger('boto3').setLevel(logging.DEBUG)

    @app.before_request
    def log_request_info():
        app.logger.info(f"Request path: {request.path}")

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        app.logger.error(f"Unexpected error: {e}", exc_info=True)
        traceback.print_exc()
        return jsonify({"result": "error", "message": "Internal Server Error"}), 500

    app.register_blueprint(projects_bp, url_prefix="/api/projects")
    app.register_blueprint(issues_bp, url_prefix="/api/projects/<project_uuid>/issues")
    app.register_blueprint(
        project_users_bp, url_prefix="/api/projects/<project_uuid>/users"
    )
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")

    return app
