"""Users routes module.

This module provides routes for managing user accounts, including creating new users,
fetching all users, deleting users, and updating user passwords. Each route enforces
root access authorization, except for password updates, which require user session
authentication.
"""

import bcrypt
from flask import Blueprint, jsonify, request, Response, g, current_app
from app.models import (
    fetch_all_users,
    add_user,
    delete_user_by_id,
    update_password,
    fetch_projects_for_user,
    fetch_projects,
    fetch_user
)
from app.utils import is_valid_email, generate_uuid
from app.models import user_is_root
from app.utils.auth import TokenManager, AuthManager

token_manager = TokenManager()
auth_manager = AuthManager(token_manager)

bp = Blueprint("users", __name__)


@bp.route("", methods=["GET"])
@auth_manager.authenticate
@auth_manager.authorize_root
def get_users() -> Response:
    """Fetches a list of all users."""
    current_app.logger.debug("Fetching all users.")
    try:
        users = fetch_all_users()
        current_app.logger.info(f"Fetched {len(users)} users.")
        return jsonify({"payload": users}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch users: {e}", exc_info=True)
        return jsonify({"message": "Failed to fetch users."}), 500



@bp.route("", methods=["POST"])
@auth_manager.authenticate
@auth_manager.authorize_root
def create_user() -> Response:
    """Creates a new user with specified attributes."""
    current_app.logger.debug("Received request to create a new user.")
    data = request.json

    if not data:
        current_app.logger.error("Invalid request: No JSON payload.")
        return jsonify({"message": "Invalid request."}), 400

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")
    confirmed_password = data.get("confirmed_password")

    if (
        not email
        or not password
        or not confirmed_password
        or not first_name
        or not last_name
    ):
        current_app.logger.error("Missing input data for user creation.")
        return (
            jsonify({"message": "Missing input data."}),
            400,
        )

    if password != confirmed_password:
        current_app.logger.error("Password mismatch during user creation.")
        return jsonify({"message": "Passwords do not match."}), 400

    if not is_valid_email(email):
        current_app.logger.error(f"Invalid email format: {email}")
        return jsonify({"message": "Invalid email format."}), 400

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)
    user_uuid = generate_uuid()

    try:
        add_user(user_uuid, first_name, last_name, email, password_hash.decode("utf-8"))
        user_info = {"uuid": user_uuid, "first_name": first_name, "last_name": last_name, "email": email, "is_root": False}
        current_app.logger.info(f"User {first_name} {last_name} created successfully with UUID={user_uuid}.")
        return (
            jsonify({"payload": user_info}),
            201,
        )
    except Exception as e:
        current_app.logger.error(f"Failed to create user {email}: {e}", exc_info=True)
        return jsonify({"message": "Failed to create user."}), 500


@bp.route("/me", methods=["GET"])
@auth_manager.authenticate
def get_session_info() -> Response:
    user_uuid = g.user_payload.get("user_uuid")
    current_app.logger.debug(f"Fetching session info for user UUID={user_uuid}.")

    if not user_uuid:
        current_app.logger.error("User not found in session payload.")
        return jsonify({"message":"User not found."}), 404

    try:
        user_info = fetch_user(user_uuid)

        if not user_info:
            current_app.logger.error(f"User not found in database for UUID={user_uuid}.")
            return jsonify({"message":"User not found."}), 404

        current_app.logger.info(f"Fetched session info for user UUID={user_uuid}.")
        return jsonify({"payload": user_info}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch session info for user UUID={user_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to fetch session info."}), 500


@bp.route("/<user_uuid>", methods=["DELETE"])
@auth_manager.authenticate
@auth_manager.authorize_root
def delete_user(user_uuid: str) -> Response:
    """Deletes a specified user by their user ID."""
    current_app.logger.debug(f"Received request to delete user UUID={user_uuid}.")

    if not user_uuid:
        current_app.logger.error("User identifier is required but missing.")
        return jsonify({"message": "User identifier required."}), 400

    try:
        success = delete_user_by_id(user_uuid)
        if success:
            current_app.logger.info(f"User UUID={user_uuid} deleted successfully.")
            return "", 204
        else:
            current_app.logger.warning(f"User UUID={user_uuid} not found for deletion.")
            return jsonify("User not found"), 404
    except Exception as e:
        current_app.logger.error(f"Failed to delete user UUID={user_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to delete user."}), 500


@bp.route("/<user_uuid>", methods=["PATCH"])
@auth_manager.authenticate
@auth_manager.authorize_user
def update_user_password(user_uuid: str) -> Response:
    """Updates the password of a specified user."""
    current_app.logger.debug(f"Received request to update password for user UUID={user_uuid}.")

    if not user_uuid:
        current_app.logger.error("User identifier is required but missing.")
        return jsonify({"message": "User identifier required."})

    data = request.json
    if not data:
        current_app.logger.error("Invalid request: No JSON payload.")
        return jsonify({"message": "Invalid request."}), 400

    new_password = data.get("password")

    if not new_password:
        current_app.logger.error("New password is required but missing.")
        return jsonify({"message": "New password required."}), 400

    password_hash = bcrypt.hashpw(
        new_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    try:
        success = update_password(user_uuid, password_hash)
        if success:
            current_app.logger.info(f"Password updated successfully for user UUID={user_uuid}.")
            return "", 204
        else:
            current_app.logger.warning(f"User UUID={user_uuid} not found for password update.")
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Failed to update password for user UUID={user_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to update password."}), 500


@bp.route("/<user_uuid>/projects", methods=["GET"])
@auth_manager.authenticate
@auth_manager.authorize_user
def get_user_projects(user_uuid: str) -> Response:
    """Retrieves all projects assigned to a specific user by user ID."""
    current_app.logger.debug(f"Fetching projects for user UUID={user_uuid}.")

    if not user_uuid:
        current_app.logger.error("User identifier is required but missing.")
        return jsonify({"message": "User identifier required."}), 400
    
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    
    current_app.logger.debug(f"Fetching user projects with page={page}, limit={limit}")

    if page < 1 or limit < 1:
        current_app.logger.error(f"Invalid pagination parameters: page={page}, limit={limit}")
        return (
            jsonify({"message": "Invalid pagination parameters."}),
            400,
        )

    try:
        is_root = user_is_root(user_uuid)
        current_app.logger.debug(f"User UUID={user_uuid} is_root={is_root}.")

        if is_root:
            project_data = fetch_projects(page, limit)
        else:
            project_data = fetch_projects_for_user(user_uuid, page, limit)

        current_app.logger.info(f"Fetched {len(project_data['projects'])} projects for user UUID={user_uuid}.") 
        return jsonify({"payload": project_data}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch projects for user UUID={user_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to fetch user projects."}), 500