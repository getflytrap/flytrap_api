from flask import Flask, jsonify
from flask_cors import CORS
from psycopg2 import OperationalError
from app.routes import projects_bp, issues_bp, project_users_bp, users_bp, auth_bp
from app.config import secret_key
from app.utils.auth import JWTAuth, RootAuth


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    @app.errorhandler(OperationalError)
    def handle_db_error(e):
        return jsonify({"status": "error", "message": "A database error occurred"}), 500

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        return jsonify({"status": "error", "message": str(e)}), 500

    jwt_auth = JWTAuth(secret_key=secret_key)
    root_auth = RootAuth(secret_key=secret_key)
    app.jwt_auth = jwt_auth
    app.root_auth = root_auth

    app.register_blueprint(projects_bp, url_prefix="/api/projects")
    app.register_blueprint(issues_bp, url_prefix="/api/projects/<pid>/issues")
    app.register_blueprint(project_users_bp, url_prefix="/api/projects/<pid>/users")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    return app
