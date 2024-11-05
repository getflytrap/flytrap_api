from flask import Flask
from flask_cors import CORS
from app.routes import projects_bp, issues_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(issues_bp, url_prefix='/api/projects/<pid>/issues')

    return app