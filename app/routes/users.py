"""Users routes module.

This module provides routes for managing user accounts, including creating new users,
fetching all users, deleting users, and updating user passwords. Each route enforces
root access authorization, except for password updates, which require user session
authentication.

Routes:
    / (GET): Fetches a list of all users.
    / (POST): Creates a new user.
    /<user_id> (DELETE): Deletes a specified user by ID.
    /<user_id> (PATCH): Updates the password of a specified user.
    /<user_id>/projects (GET): Gets all projects a user is assigned to.

Attributes:
    bp (Blueprint): Blueprint for user management routes.
"""

import bcrypt
from flask import jsonify, request, Response
from flask import Blueprint
from app.auth_manager import jwt_auth
from app.models import (
    fetch_all_users,
    add_user,
    delete_user_by_id,
    update_password,
    fetch_projects_for_user,
)
from app.utils import is_valid_email


bp = Blueprint("users", __name__)


@bp.route("/", methods=["GET"])
@jwt_auth.check_session_and_authorization(root_required=True)
def get_users() -> Response:
    """Fetches a list of all users.

    Returns:
        Response: JSON response with a list of all users and a 200 status code,
                  or an error message with a 500 status code if fetching fails.
    """
    try:
        users = fetch_all_users()
        return jsonify({"status": "success", "data": users}), 200
    except Exception as e:
        print(f"Error in get_users: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch users"}), 500


@bp.route("/", methods=["POST"])
@jwt_auth.check_session_and_authorization(root_required=True)
def create_user() -> Response:
    """Creates a new user with specified attributes.

    JSON Payload:
        first_name (str): First name of the user.
        last_name (str): Last name of the user.
        email (str): Email address of the user.
        password (str): Password for the user.
        confirmed_password (str): Confirmation of the password.

    Returns:
        Response: JSON response with user data and a 201 status code if successful,
                  or error messages with a 400 status code if input validation fails.
    """
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
        user_id = add_user(first_name, last_name, email, password_hash.decode("utf-8"))
        data = {"user_id": user_id, "first_name": first_name, "last_name": last_name}
        return (
            jsonify({"status": "success", "data": data}),
            201,
        )
    except Exception as e:
        print(f"Error in create_user: {e}")
        return jsonify({"status": "error", "message": "Failed to create new user"}), 500


@bp.route("/<user_uuid>", methods=["DELETE"])
@jwt_auth.check_session_and_authorization(root_required=True)
def delete_user(user_uuid: str) -> Response:
    """Deletes a specified user by their user ID.

    Args:
        user_id (str): The user uuid of the user to delete.

    Returns:
        Response: 204 status code if successful, or a 404 status code if the user is not
        found.
    """
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
@jwt_auth.check_session_and_authorization()
def update_user_password(user_uuid: str) -> Response:
    """Updates the password of a specified user.

    Args:
        user_id (str): The user uuid of the user whose password is being updated.

    JSON Payload:
        password (str): The new password for the user.

    Returns:
        Response: 204 status code if the password update is successful,
                  or a 400 status code if the new password is missing.
    """
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
@jwt_auth.check_session_and_authorization()
def get_user_projects(user_uuid: str) -> Response:
    """
    Retrieves all projects assigned to a specific user by user ID.

    Args:
    - user_id (str): The uuid of the user for whom to retrieve projects.

    Returns:
        Response: 200 status code and the project data.
    """
    try:
        data = fetch_projects_for_user(user_uuid)
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        print(f"Error in get_user_projects: {e}")
        return (
            jsonify({"status": "error", "message": "Failed to get projects for user"}),
            500,
        )
