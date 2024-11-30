"""Project Users routes module.

This module provides routes for managing user associations with specific projects.
It allows fetching users associated with a project, adding users to a project,
and removing users from a project. Access is restricted to users with root access.
"""

from flask import jsonify, request, Response, current_app
from flask import Blueprint
from app.models import (
    fetch_project_users,
    add_user_to_project,
    remove_user_from_project,
    user_is_root,
)
from app.utils.auth import TokenManager, AuthManager
from app.utils import create_sns_subscription, remove_sns_subscription

token_manager = TokenManager()
auth_manager = AuthManager(token_manager)

bp = Blueprint("project_users", __name__)


@bp.route("", methods=["GET"])
@auth_manager.authenticate
@auth_manager.authorize_root
def get_project_users(project_uuid: str) -> Response:
    """Fetches all user uuids associated with a specified project."""
    current_app.logger.debug(f"Fetching users for project UUID={project_uuid}.")
    
    if not project_uuid: 
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier required."}), 400
    
    try:
        users = fetch_project_users(project_uuid)
        current_app.logger.info(f"Fetched {len(users)} users for project UUID={project_uuid}.")
        return jsonify({"payload": users}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch users for project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to fetch users."}), 500
    

@bp.route("", methods=["POST"])
@auth_manager.authenticate
@auth_manager.authorize_root
def add_project_user(project_uuid: str) -> Response:
    """Adds a user to a specified project."""
    current_app.logger.debug(f"Adding user to project UUID={project_uuid}.")

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier required."}), 400

    data = request.get_json()
    if not data:
        current_app.logger.error("Invalid request: No JSON payload.")
        return jsonify({"message": "Invalid request."}), 400

    user_uuid = data.get("user_uuid")
    if not user_uuid:
        current_app.logger.error("User identifier is required but missing.")
        return jsonify({"message": "User identifier required."}), 400

    try:
        if user_is_root(user_uuid):
            current_app.logger.warning(f"Attempt to add root user UUID={user_uuid} to project UUID={project_uuid}.")
            return (
                jsonify(
                    {"message": "Admin cannot be added to projects."}
                ),
                400,
            )

        create_sns_subscription(project_uuid, user_uuid)
        success = add_user_to_project(project_uuid, user_uuid)
        if success:
            current_app.logger.info(f"User UUID={user_uuid} added to project UUID={project_uuid}.")
            return "", 204
        else:
            current_app.logger.warning(f"User UUID={user_uuid} is already associated with project UUID={project_uuid}.")
            return jsonify({"message": "User is already associated with the project."}), 400
    except ValueError as e:
        current_app.logger.error(e)
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Failed to add user UUID={user_uuid} to project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to add user to project."}), 500


@bp.route("/<user_uuid>", methods=["DELETE"])
@auth_manager.authenticate
@auth_manager.authorize_root
def remove_project_user(project_uuid: str, user_uuid: str) -> Response:
    """Removes a user from a specified project."""
    current_app.logger.debug(f"Removing user UUID={user_uuid} from project UUID={project_uuid}.")

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier required."}), 400

    if not user_uuid:
        current_app.logger.error("User identifier is required but missing.")
        return jsonify({"message": "User identifier required."}), 400

    try:
        remove_sns_subscription(project_uuid, user_uuid)
        success = remove_user_from_project(project_uuid, user_uuid)
        if success:
            current_app.logger.info(f"User UUID={user_uuid} removed from project UUID={project_uuid}.")
            return "", 204
        else:
            current_app.logger.warning(f"Project UUID={project_uuid} or user UUID={user_uuid} not found.")
            return (
                jsonify({"message": "Project or user not found."}),
                404,
            )
    except Exception as e:
        current_app.logger.error(f"Failed to remove user UUID={user_uuid} from project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to remove user from project."}), 500
