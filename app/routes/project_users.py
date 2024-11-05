from flask import jsonify, request
from flask import Blueprint
from app.models import (
    fetch_project_users
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