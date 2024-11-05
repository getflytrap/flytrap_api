import bcrypt
import datetime
import jwt
from flask import jsonify, request, make_response, redirect, Response
from flask import Blueprint
from app.models import (
    fetch_user_by_email,
)

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login() -> Response:
    data = request.json
    email = data.get('email')
    password = data.get('password')
  
    user = fetch_user_by_email(email)

    if not user:
        return jsonify({"message": "User does not exist"}), 404
  
    user_id, password_hash, is_root = user

    if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
        access_token = jwt.encode({
            'user_id': user_id, 'is_root': is_root, 'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=1) 
        }, 'SECRET', algorithm='HS256')

        refresh_token = jwt.encode(
            {'user_id': user_id, 'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)},
            'SECRET', algorithm='HS256'
        )

        response = make_response(jsonify({"access_token": access_token}), 200)
        # secure: set to False for local testing
        response.set_cookie('refresh_token', refresh_token, httponly=True, secure=False, samesite='Strict')
        return response
    else:
        return jsonify({"message": "Invalid password"}), 401

@bp.route('/logout', methods=['GET'])
def logout() -> Response:
    response = make_response(redirect('/login'), 302)
    response.set_cookie('refresh_token', '', expires=0, httponly=True, secure=True)

    # Note: No access_token clearing needed since it's client-managed in memory
    return response