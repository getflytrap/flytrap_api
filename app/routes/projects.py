"""Projects routes module.

This module provides routes for managing projects, including creating, fetching,
updating, and deleting project records. Each route enforces root access authorization.

Routes:
    / (GET): Fetches a paginated list of projects.
    / (POST): Creates a new project.
    /<pid> (DELETE): Deletes a specified project by ID.
    /<pid> (PATCH): Updates the name of a specified project by ID.

Attributes:
    bp (Blueprint): Blueprint for project management routes.
"""

from flask import jsonify, request, Response
from flask import Blueprint
from app.utils import generate_uuid
from app.auth_manager import root_auth
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
    """Fetches a paginated list of all projects.

    Query Parameters:
        page (int): The page number for pagination (default is 1).
        limit (int): The number of projects per page (default is 10).

    Returns:
        Response: JSON response containing the list of projects with a 200 status code,
                  or an error message with a 500 status code if fetching fails.
    """
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
    """Creates a new project with a unique project ID.

    JSON Payload:
        name (str): The name of the new project.

    Returns:
        Response: JSON response containing the project ID and name with a 201 status
        code, or an error message with a 400 status code if project name is missing.
    """
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
        print(f"Error in create_project: {e}")
        return (
            jsonify({"status": "error", "message": "Failed to create new project"}),
            500,
        )


@bp.route("/<pid>", methods=["DELETE"])
@root_auth.require_root_access
def delete_project(pid: str) -> Response:
    """Deletes a specified project by its project ID.

    Args:
        pid (str): The project ID of the project to delete.

    Returns:
        Response: 204 status code if successful, or a 404 status code if the project is
        not found.
    """

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
    """Updates the name of a specified project.

    Args:
        pid (str): The project ID of the project to update.

    JSON Payload:
        new_name (str): The new name for the project.

    Returns:
        Response: JSON response with the updated project name and a 200 status code if
        successful, or a 404 status code if the project is not found.
    """
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
        return (
            jsonify({"status": "error", "message": "Failed to update project name"}),
            500,
        )
