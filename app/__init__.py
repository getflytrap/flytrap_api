from flask import Flask
from flask_cors import CORS
from app.routes import projects_bp, issues_bp, project_users_bp, users_bp, auth_bp
from app.config import secret_key
from app.utils.auth import JWTAuth, RootAuth


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

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
