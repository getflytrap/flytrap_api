import os
from flask import jsonify, request, Response
from flask import Blueprint
from typing import Optional
from dotenv import load_dotenv
from app.utils.auth import JWTAuth
from app.models import (
    fetch_issues_by_project,
    delete_issues_by_project,
    fetch_error,
    fetch_rejection,
    update_error_resolved,
    update_rejection_resolved,
    delete_error_by_id,
    delete_rejection_by_id,
)

load_dotenv()

secret_key: Optional[str] = os.getenv('JWT_SECRET_KEY')
jwt_auth = JWTAuth(secret_key=secret_key)

bp = Blueprint("project_issues", __name__)


@bp.route("/", methods=["GET"])
@jwt_auth.check_session_and_authorization
def get_errors(pid: str) -> Response:
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    handled = request.args.get("handled", None)
    time = request.args.get("time", None)
    resolved = request.args.get("resolved", None)

    try:
        data = fetch_issues_by_project(pid, page, limit, handled, time, resolved)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch data", "error": str(e)}), 500


@bp.route("/", methods=["DELETE"])
@jwt_auth.check_session_and_authorization
def delete_errors(pid: str) -> Response:
    try:
        success = delete_issues_by_project(pid)
        if success:
            return "", 204
        else:
            return jsonify({"message": "No errors found for this project"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to delete errors", "error": str(e)}), 500


@bp.route("/errors/<eid>", methods=["GET"])
@jwt_auth.check_session_and_authorization
def get_error(_, eid: int) -> Response:
    try:
        error = fetch_error(eid)
        if error:
            return jsonify(error), 200
        else:
            return jsonify({"message": "Error not found"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to retrieve error", "error": str(e)}), 500


@bp.route("/rejections/<rid>", methods=["GET"])
@jwt_auth.check_session_and_authorization
def get_rejection(_, rid: int) -> Response:
    try:
        error = fetch_rejection(rid)
        if error:
            return jsonify(error), 200
        else:
            return jsonify({"message": "Error not found"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to retrieve error", "error": str(e)}), 500


@bp.route("/errors/<eid>", methods=["PATCH"])
@jwt_auth.check_session_and_authorization
def toggle_error(_, eid: int) -> Response:
    data = request.get_json()
    new_resolved_state = data.get("resolved")

    if new_resolved_state is None:
        return jsonify({"message": "Resolved state required"}), 400

    try:
        success = update_error_resolved(eid, new_resolved_state)
        if success:
            return jsonify({"message": "Error state updated successfully"}), 200
        else:
            return jsonify({"message": "Error not found"}), 404
    except Exception as e:
        return (
            jsonify({"message": "Failed to update error state", "error": str(e)}),
            500,
        )


@bp.route("/rejections/<rid>", methods=["PATCH"])
@jwt_auth.check_session_and_authorization
def toggle_rejection(_, rid: int) -> Response:
    data = request.get_json()
    new_resolved_state = data.get("resolved")

    if new_resolved_state is None:
        return jsonify({"message": "Resolved state required"}), 400

    try:
        success = update_rejection_resolved(rid, new_resolved_state)
        if success:
            return jsonify({"message": "Error state updated successfully"}), 200
        else:
            return jsonify({"message": "Error not found"}), 404
    except Exception as e:
        return (
            jsonify({"message": "Failed to update error state", "error": str(e)}),
            500,
        )


@bp.route("/errors/<eid>", methods=["DELETE"])
@jwt_auth.check_session_and_authorization
def delete_error(_, eid: int) -> Response:
    try:
        success = delete_error_by_id(eid)
        if success:
            return "", 204
        else:
            return jsonify({"message": "Error not found"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to delete error", "error": str(e)}), 500


@bp.route("/rejections/<rid>", methods=["DELETE"])
@jwt_auth.check_session_and_authorization
def delete_rejection(_, rid: int) -> Response:
    try:
        success = delete_rejection_by_id(rid)
        if success:
            return "", 204
        else:
            return jsonify({"message": "Error not found"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to delete error", "error": str(e)}), 500
