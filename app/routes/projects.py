from flask import jsonify, request, Response
from flask import Blueprint
from psycopg2 import IntegrityError, OperationalError
from app.utils import generate_uuid
from app import root_auth
from app.models import (
    fetch_projects,
    add_project,
    delete_project_by_id,
    update_project_name,
)

bp = Blueprint("projects", __name__)


@bp.route("/", methods=["GET"])
@root_auth.require_root_access
def get_projects() -> Response:
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    try:
        data = fetch_projects(page, limit)
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        print(f"Error in get_projects: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch projects"}), 500


@bp.route("/", methods=["POST"])
@root_auth.require_root_access
def create_project() -> Response:
    data = request.get_json()
    project_name = data.get("name")

    if not project_name:
        return jsonify({"status": "error", "message": "Missing project name"}), 400

    pid = generate_uuid()

    try:
        add_project(pid, project_name)
        data = {"project_id": pid, "project_name": project_name}
        return jsonify({"status": "success", "data": data}), 201
    except Exception as e:
        print(f"Error in create_project:", {e})
        return jsonify({"status": "error", "message": "Failed to create new project"}), 500


@bp.route("/<pid>", methods=["DELETE"])
@root_auth.require_root_access
def delete_project(pid: str) -> Response:
    try:
        success = delete_project_by_id(pid)
        if success:
            return "", 204
        else:
            return jsonify({"status": "error", "message": "Project not found"}), 404
    except Exception as e:
        print(f"Error in delete_project: {e}")
        return jsonify({"status": "error", "message": "Failed to delete project"}), 500


@bp.route("/<pid>", methods=["PATCH"])
@root_auth.require_root_access
def update_project(pid: str) -> Response:
    data = request.get_json()
    new_name = data.get("new_name")

    if not new_name:
        return jsonify({"status": "error", "message": "Missing project name"}), 400

    try:
        success = update_project_name(pid, new_name)
        if success:
            data = {"project_id": pid, "project_name": new_name}
            return jsonify({"status": "success", "data": data}), 200
        else:
            return jsonify({"status": "error", "message": "Project not found"}), 404
    except Exception as e:
        print(f"Error in update_project: {e}")
        return jsonify({"status": "error", "message": "Failed to update project name"}), 500
