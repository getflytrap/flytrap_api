from flask import jsonify, request, Response
from flask import Blueprint
from app.utils import generate_uuid
from app.models import (
    fetch_projects, 
    add_project,
    delete_project_by_id,
    update_project_name
)

bp = Blueprint('projects', __name__)

@bp.route('/', methods=['GET'])
def get_projects() -> Response:
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    try:
        data = fetch_projects(page, limit)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch projects", "error": str(e)}), 500
    
@bp.route('/', methods=['POST'])
def create_project() -> Response:
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
    
@bp.route('/<pid>', methods=['DELETE'])
def delete_project(pid: str) -> Response:
    try:
        success = delete_project_by_id(pid)
        if success:
            return '', 204
        else: 
            return jsonify({"message": "Project was not found"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to delete project", "error": str(e)}), 500

@bp.route('/<pid>', methods=['PATCH'])
def update_project(pid: str) -> Response:
    data = request.get_json()
    new_name = data.get('new_name')

    if not new_name:
        return jsonify({"message": "Project name is required"}), 400
    
    try:
        success = update_project_name(pid, new_name)
        if success:
            return jsonify({"project_id": pid, "project_name": new_name}), 200
        else:
            return jsonify({"message": "Project not found"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to update project", "error": str(e)}), 500