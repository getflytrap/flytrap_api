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
from app.auth_manager import jwt_auth
from app.models import (
    fetch_projects,
    add_project,
    delete_project_by_id,
    update_project_name,
)

bp = Blueprint("projects", __name__)


@bp.route("", methods=["GET"])
@jwt_auth.check_session_and_authorization(root_required=True)
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


@bp.route("", methods=["POST"])
@jwt_auth.check_session_and_authorization(root_required=True)
def create_project() -> Response:
    """Creates a new project with a unique project ID.

    JSON Payload:
        name (str): The name of the new project.

    Returns:
        Response: JSON response containing the project ID and name with a 201 status
        code, or an error message with a 400 status code if project name is missing.
    """
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"status": "error", "message": "Missing project name"}), 400

    try:
        uuid = add_project(name)
        data = {"uuid": uuid, "name": name}
        return jsonify({"status": "success", "data": data}), 201
    except Exception as e:
        print(f"Error in create_project: {e}")
        return (
            jsonify({"status": "error", "message": "Failed to create new project"}),
            500,
        )


@bp.route("/<project_uuid>", methods=["DELETE"])
@jwt_auth.check_session_and_authorization(root_required=True)
def delete_project(project_uuid: str) -> Response:
    """Deletes a specified project by its project UUID.

    Args:
        project_uuid (str): The project uuid of the project to delete.

    Returns:
        Response: 204 status code if successful, or a 404 status code if the project is
        not found.
    """

    try:
        success = delete_project_by_id(project_uuid)
        if success:
            return "", 204
        else:
            return jsonify({"status": "error", "message": "Project not found"}), 404
    except Exception as e:
        print(f"Error in delete_project: {e}")
        return jsonify({"status": "error", "message": "Failed to delete project"}), 500


@bp.route("/<project_uuid>", methods=["PATCH"])
@jwt_auth.check_session_and_authorization(root_required=True)
def update_project(project_uuid: str) -> Response:
    """Updates the name of a specified project.

    Args:
        project_uuid (str): The project ID of the project to update.

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
        success = update_project_name(project_uuid, new_name)
        if success:
            data = {"uuid": project_uuid, "name": new_name}
            return jsonify({"status": "success", "data": data}), 200
        else:
            return jsonify({"status": "error", "message": "Project not found"}), 404
    except Exception as e:
        print(f"Error in update_project: {e}")
        return (
            jsonify({"status": "error", "message": "Failed to update project name"}),
            500,
        )
