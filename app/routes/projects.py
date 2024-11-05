from flask import jsonify, request
from flask import Blueprint
from app.models import fetch_projects, add_project
from app.utils import generate_uuid

bp = Blueprint('projects', __name__)

@bp.route('/', methods=['GET'])
def get_projects():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    try:
        data = fetch_projects(page, limit)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch projects", "error": str(e)}), 500
    
@bp.route('/', methods=['POST'])
def create_project():
    data = request.get_json()
    project_name = data.get('name')

    if not project_name:
        return jsonify({ "message": "Project name is required"}), 400
    
    pid = generate_uuid()

    try:
        add_project(pid, project_name)
        return jsonify({"project_id": pid, "project_name": project_name}), 201
    except Exception as e:
        return jsonify({"message": "Failed to add new project", "error": str(e)}), 500