from flask import jsonify, request
from flask import Blueprint
from app.models import (
    fetch_all_users,
)

bp = Blueprint('users', __name__)

@bp.route('/', methods=['GET'])
def get_users():
    try:
        users = fetch_all_users()
        return jsonify({"message": "Successfully fetched all users", "users": users}), 200
    except Exception as e:
        print("Error: " + str(e))
        return jsonify({"message": "Failed to fetch data"}), 500