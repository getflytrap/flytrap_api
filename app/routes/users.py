import bcrypt
from flask import jsonify, request
from flask import Blueprint
from app.models import (
    fetch_all_users,
    add_user,
    delete_user
)
from app.utils import (
    is_valid_email
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
    
@bp.route('/', methods=['POST'])
def create_user():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    confirmed_password = data.get('confirmed_password')

    if not email or not password or not confirmed_password or not first_name or not last_name:
        return jsonify({"message": "first name, last name, email, password, and confirmed password are required"}), 400

    if password != confirmed_password:
        return jsonify({"message": "Passwords do not match"}), 400
    
    if not is_valid_email(email):
        return jsonify({"message": "invalid email format"}), 400

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    try:
        user_id = add_user(first_name, last_name, email, password_hash.decode('utf-8'))
        return jsonify({"message": "User created successfully", "user_id": user_id}), 201
    except Exception as e:
        print("error: " + str(e))
        return jsonify({"message": "Failed to create user"}), 500

@bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        success = delete_user(user_id)
        if success:
            return jsonify({"message:" "Successfully delete user"}), 204
        else:
            return jsonify({"message": "User was not found"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to delete user", "error": str(e)}), 500 