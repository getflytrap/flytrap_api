from flask import Flask
from flask_cors import CORS
from app.routes import projects_bp, issues_bp, project_users_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(issues_bp, url_prefix='/api/projects/<pid>/issues')
    app.register_blueprint(project_users_bp, url_prefix='/api/projects/<pid>/users')

    return app