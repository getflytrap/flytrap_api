from flask import jsonify, request, Response
from flask import Blueprint
from app import root_auth
from app.models import (
    fetch_project_users,
    add_user_to_project,
    remove_user_from_project,
)

bp = Blueprint("project_users", __name__)


@bp.route("/", methods=["GET"])
@root_auth.require_root_access
def get_project_users(pid: str) -> Response:
    try:
        users = fetch_project_users(pid)
        return jsonify({"status": "success", "data": users}), 200
    except Exception as e:
        print(f"Error in get_project_users: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch users for project"}), 500


@bp.route("/", methods=["POST"])
@root_auth.require_root_access
def add_project_user(pid: str, user_id: int) -> Response:
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "Missing user id"}), 400

    try:
        add_user_to_project(pid, user_id)
        return jsonify({"status": "success", "message": "Successfully added user to project"}), 201
    except Exception as e:
        print(f"Error in add_project_user: {e}")
        return jsonify({"status": "error", "message": "Failed to add user to project"}), 500


@bp.route("/<user_id>", methods=["DELETE"])
@root_auth.require_root_access
def remove_project_user(pid: str, user_id: int) -> Response:
    try:
        success = remove_user_from_project(pid, user_id)
        if success:
            return jsonify({"status": "success", "message": "Successfully removed user from project"}), 204
        else:
            return jsonify({"status": "error", "message": "Project or user not found"}), 404
    except Exception as e:
        print(f"Error in remove_project_user: {e}")
        return jsonify({"status": "error", "message": "failed to remove user from project"}), 500
