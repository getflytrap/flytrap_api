"""Project Users routes module.

This module provides routes for managing user associations with specific projects.
It allows fetching users associated with a project, adding users to a project,
and removing users from a project. Access is restricted to users with root access.

Routes:
    / (GET): Fetches a list of users associated with a project.
    / (POST): Adds a user to a project.
    /<user_id> (DELETE): Removes a user from a project.

Attributes:
    bp (Blueprint): Blueprint for project users routes.
"""

from flask import jsonify, request, Response
from flask import Blueprint
from app.auth_manager import jwt_auth
from app.models import (
    fetch_project_users,
    add_user_to_project,
    remove_user_from_project,
)

bp = Blueprint("project_users", __name__)


@bp.route("", methods=["GET"])
@jwt_auth.check_session_and_authorization(root_required=True)
def get_project_users(project_uuid: str) -> Response:
    """Fetches all users associated with a specified project.

    Args:
        project_uuid (str): The project uuid.

    Returns:
        Response: JSON response with a list of associated users and a 200 status code,
                  or an error message with a 500 status code if fetching fails.
    """

    try:
        users = fetch_project_users(project_uuid)
        return jsonify({"status": "success", "data": users}), 200
    except Exception as e:
        print(f"Error in get_project_users: {e}")
        return (
            jsonify(
                {"status": "error", "message": "Failed to fetch users for project"}
            ),
            500,
        )


@bp.route("", methods=["POST"])
@jwt_auth.check_session_and_authorization(root_required=True)
def add_project_user(project_uuid: str) -> Response:
    """Adds a user to a specified project.

    Args:
        project_uuid (str): The project uuid.

    Returns:
        Response: JSON response with a success message and a 201 status code if
        successful, or an error message with a 400 status code if the user_id is
        missing.
    """
    data = request.get_json()
    user_uuid = data.get("user_uuid")

    if not user_uuid:
        return jsonify({"status": "error", "message": "Missing user uuid"}), 400

    try:
        add_user_to_project(project_uuid, user_uuid)
        return (
            jsonify(
                {"status": "success", "message": "Successfully added user to project"}
            ),
            201,
        )
    except Exception as e:
        print(f"Error in add_project_user: {e}")
        return (
            jsonify({"status": "error", "message": "Failed to add user to project"}),
            500,
        )


@bp.route("/<user_uuid>", methods=["DELETE"])
@jwt_auth.check_session_and_authorization(root_required=True)
def remove_project_user(project_uuid: str, user_uuid: str) -> Response:
    """Removes a user from a specified project.

    Args:
        project_uuid (str): The project uuid.
        user_uuid (str): The uuid of the user to remove.

    Returns:
        Response: JSON response with a 204 status code if successful,
                  or a 404 status code if the project or user is not found.
    """
    try:
        success = remove_user_from_project(project_uuid, user_uuid)
        if success:
            return "", 204
        else:
            return (
                jsonify({"status": "error", "message": "Project or user not found"}),
                404,
            )
    except Exception as e:
        print(f"Error in remove_project_user: {e}")
        return (
            jsonify(
                {"status": "error", "message": "Failed to remove user from project"}
            ),
            500,
        )
