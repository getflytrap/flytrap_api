"""Project Users routes module.

This module provides routes for managing user associations with specific projects.
It allows fetching users associated with a project, adding users to a project,
and removing users from a project. Access is restricted to users with root access.
"""

from flask import jsonify, request, Response
from flask import Blueprint, current_app
from app.models import (
    fetch_project_users,
    add_user_to_project,
    remove_user_from_project,
    user_is_root,
)
from app.utils.auth import TokenManager, AuthManager
from app.utils.aws_helpers import create_sns_subscription

token_manager = TokenManager()
auth_manager = AuthManager(token_manager)

bp = Blueprint("project_users", __name__)


@bp.route("", methods=["GET"])
@auth_manager.authenticate
@auth_manager.authorize_root
def get_project_users(project_uuid: str) -> Response:
    """Fetches all user uuids associated with a specified project."""
    users = fetch_project_users(project_uuid)
    return jsonify({"result": "success", "payload": users}), 200


@bp.route("", methods=["POST"])
@auth_manager.authenticate
@auth_manager.authorize_root
def add_project_user(project_uuid: str) -> Response:
    """Adds a user to a specified project."""
    data = request.get_json()
    if not data: 
        return jsonify({"result": "error", "message": "Invalid request"}), 400
    
    user_uuid = data.get("user_uuid")
    if not user_uuid:
        return jsonify({"result": "error", "message": "Missing user uuid"}), 400

    if user_is_root(user_uuid):
        return (
            jsonify(
                {"result": "error", "message": "Root users cannot be added to projects"}
            ),
            400,
        )

    create_sns_subscription(project_uuid, user_uuid)
    add_user_to_project(project_uuid, user_uuid)
    return "", 204


@bp.route("/<user_uuid>", methods=["DELETE"])
@auth_manager.authenticate
@auth_manager.authorize_root
def remove_project_user(project_uuid: str, user_uuid: str) -> Response:
    """Removes a user from a specified project."""
    success = remove_user_from_project(project_uuid, user_uuid)
    if success:
        return "", 204
    else:
        return (
            jsonify({"result": "error", "message": "Project or user not found"}),
            404,
        )
