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


@bp.route("/", methods=["GET"])
@jwt_auth.check_session_and_authorization(root_required=True)
def get_project_users(pid: str) -> Response:
    """Fetches all users associated with a specified project.

    Args:
        pid (str): The project ID.

    Returns:
        Response: JSON response with a list of associated users and a 200 status code,
                  or an error message with a 500 status code if fetching fails.
    """

    try:
        users = fetch_project_users(pid)
        return jsonify({"status": "success", "data": users}), 200
    except Exception as e:
        print(f"Error in get_project_users: {e}")
        return (
            jsonify(
                {"status": "error", "message": "Failed to fetch users for project"}
            ),
            500,
        )


@bp.route("/", methods=["POST"])
@jwt_auth.check_session_and_authorization(root_required=True)
def add_project_user(pid: str) -> Response:
    """Adds a user to a specified project.

    Args:
        pid (str): The project ID.

    Returns:
        Response: JSON response with a success message and a 201 status code if
        successful, or an error message with a 400 status code if the user_id is
        missing.
    """
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "Missing user id"}), 400

    try:
        add_user_to_project(pid, user_id)
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


@bp.route("/<user_id>", methods=["DELETE"])
@jwt_auth.check_session_and_authorization(root_required=True)
def remove_project_user(pid: str, user_id: int) -> Response:
    """Removes a user from a specified project.

    Args:
        pid (str): The project ID.
        user_id (int): The ID of the user to remove.

    Returns:
        Response: JSON response with a 204 status code if successful,
                  or a 404 status code if the project or user is not found.
    """
    try:
        success = remove_user_from_project(pid, user_id)
        if success:
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": "Successfully removed user from project",
                    }
                ),
                204,
            )
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
