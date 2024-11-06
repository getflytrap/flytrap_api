import bcrypt
from flask import jsonify, request, Response
from flask import Blueprint
from app import jwt_auth, root_auth
from app.models import fetch_all_users, add_user, delete_user_by_id, update_password
from app.utils import is_valid_email


bp = Blueprint("users", __name__)


@bp.route("/", methods=["GET"])
@root_auth.require_root_access
def get_users() -> Response:
    try:
        users = fetch_all_users()
        return jsonify({"status": "success", "data": users}), 200
    except Exception as e:
        print(f"Error in get_users: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch users"}), 500


@bp.route("/", methods=["POST"])
@root_auth.require_root_access
def create_user() -> Response:
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


@bp.route("/<user_id>", methods=["DELETE"])
@root_auth.require_root_access
def delete_user(user_id: int) -> Response:
    try:
        success = delete_user_by_id(user_id)
        if success:
            return "", 204
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404
    except Exception as e:
        print(f"Error in delete_user: {e}")
        return jsonify({"status": "error", "message": "Failed to delete user"}), 500


@bp.route("/<user_id>", methods=["PATCH"])
@jwt_auth.check_session_and_authorization
def update_user_password(user_id: int) -> Response:
    data = request.json
    new_password = data.get("password")

    if not new_password:
        return jsonify({"status": "error", "message": "Missing password"}), 400

    password_hash = bcrypt.hashpw(
        new_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    try:
        success = update_password(user_id, password_hash)
        if success:
            return "", 204
    except Exception as e:
        print(f"Error in update_user_password: {e}")
        return jsonify({"status": "error", "message": "Failed to update password"}), 500
