"""Users routes module.

This module provides routes for managing user accounts, including creating new users,
fetching all users, deleting users, and updating user passwords. Each route enforces
root access authorization, except for password updates, which require user session
authentication.
"""

import bcrypt
from flask import jsonify, request, Response
from flask import Blueprint
from app.models import (
    fetch_all_users,
    add_user,
    delete_user_by_id,
    update_password,
    fetch_projects_for_user,
)
from app.utils import is_valid_email
from app.models import user_is_root
from app.routes.projects import get_projects
from app.utils.auth import TokenManager, AuthManager

token_manager = TokenManager()
auth_manager = AuthManager(token_manager)

bp = Blueprint("users", __name__)


@bp.route("", methods=["GET"])
@auth_manager.authenticate
@auth_manager.authorize_root
def get_users() -> Response:
    """Fetches a list of all users."""
    print("users cookies here", request.cookies)
    try:
        users = fetch_all_users()
        return jsonify({"status": "success", "data": users}), 200
    except Exception as e:
        print(f"Error in get_users: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch users"}), 500


@bp.route("", methods=["POST"])
@auth_manager.authenticate
@auth_manager.authorize_root
def create_user() -> Response:
    """Creates a new user with specified attributes."""
    data = request.json
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
        return (
            jsonify({"status": "error", "message": "Missing input data"}),
            400,
        )

    if password != confirmed_password:
        return jsonify({"status": "error", "message": "Passwords do not match"}), 400

    if not is_valid_email(email):
        return jsonify({"status": "error", "message": "Invalid email format"}), 400

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)

    try:
        uuid = add_user(first_name, last_name, email, password_hash.decode("utf-8"))
        data = {"uuid": uuid, "first_name": first_name, "last_name": last_name}
        return (
            jsonify({"status": "success", "data": data}),
            201,
        )
    except Exception as e:
        print(f"Error in create_user: {e}")
        return jsonify({"status": "error", "message": "Failed to create new user"}), 500


@bp.route("/<user_uuid>", methods=["DELETE"])
@auth_manager.authenticate
@auth_manager.authorize_root
def delete_user(user_uuid: str) -> Response:
    """Deletes a specified user by their user ID."""
    try:
        success = delete_user_by_id(user_uuid)
        if success:
            return "", 204
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404
    except Exception as e:
        print(f"Error in delete_user: {e}")
        return jsonify({"status": "error", "message": "Failed to delete user"}), 500


@bp.route("/<user_uuid>", methods=["PATCH"])
@auth_manager.authenticate
@auth_manager.authorize_user
def update_user_password(user_uuid: str) -> Response:
    """Updates the password of a specified user."""
    data = request.json
    new_password = data.get("password")

    if not new_password:
        return jsonify({"status": "error", "message": "Missing password"}), 400

    password_hash = bcrypt.hashpw(
        new_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    try:
        success = update_password(user_uuid, password_hash)
        if success:
            return "", 204
    except Exception as e:
        print(f"Error in update_user_password: {e}")
        return jsonify({"status": "error", "message": "Failed to update password"}), 500


@bp.route("/<user_uuid>/projects", methods=["GET"])
@auth_manager.authenticate
@auth_manager.authorize_user
def get_user_projects(user_uuid: str) -> Response:
    """Retrieves all projects assigned to a specific user by user ID."""
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    try:
        user_uuid_in_path_is_for_root_user = user_is_root(
            user_uuid
        )
  
        if user_uuid_in_path_is_for_root_user:
            return get_projects()

        data = fetch_projects_for_user(user_uuid, page, limit)
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        print(f"Error in get_user_projects: {e}")
        return (
            jsonify({"status": "error", "message": "Failed to get projects for user"}),
            500,
        )
