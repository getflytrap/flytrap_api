from flask import jsonify, request
from flask import Blueprint
from app.models import (
    fetch_project_users,
    add_user_to_project
)

bp = Blueprint('project_users', __name__)

@bp.route('/', methods=['GET'])
def get_project_users(pid):
    try:
        users = fetch_project_users(pid)
        if users:
            return jsonify(users), 200
        else:
            return jsonify({"message": "No users found for this project"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to fetch users", "error": str(e)}), 500
    
@bp.route('/', methods=['POST'])
def add_project_user(pid, user_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    try:
        add_user_to_project(pid, user_id)
        return jsonify({"message": "Successfully added user to project"}), 201
    except Exception as e:
        return jsonify({"message": "Failed to add user to project", "error": str(e)}), 500