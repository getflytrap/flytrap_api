"""Projects routes module.

This module provides routes for managing projects, including creating, fetching,
updating, and deleting project records. Each route enforces root access authorization.
"""

from flask import jsonify, request, Response, current_app
from flask import Blueprint
from app.config import USAGE_PLAN_ID
from app.models import (
    fetch_projects,
    add_project,
    delete_project_by_id,
    update_project_name,
)
from app.utils.auth import TokenManager, AuthManager
from app.utils import (
  associate_api_key_with_usage_plan, 
  delete_sns_topic_from_aws
)

token_manager = TokenManager()
auth_manager = AuthManager(token_manager)

bp = Blueprint("projects", __name__)


@bp.route("", methods=["GET"])
@auth_manager.authenticate
@auth_manager.authorize_root
def get_projects() -> Response:
    """Fetches a paginated list of all projects."""
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    try:
        data = fetch_projects(page, limit)
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        current_app.logger.debug(f"Error in get_projects: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch projects"}), 500


@bp.route("", methods=["POST"])
@auth_manager.authenticate
@auth_manager.authorize_root
def create_project() -> Response:
    """Creates a new project with a unique project ID."""
    data = request.get_json()
    name = data.get("name")
    platform = data.get("platform")

    if not name:
        return jsonify({"status": "error", "message": "Missing project name"}), 400

    if not platform:
        return jsonify({"status": "error", "message": "Missing project platform"}), 400

    try:
        result = add_project(name, platform)
        project_uuid = result["project_uuid"]
        api_key = result["api_key"]

        associate_api_key_with_usage_plan(name, api_key, USAGE_PLAN_ID)

        data = {"uuid": project_uuid, "name": name, "platform": platform, "api_key": api_key}

        return jsonify({"status": "success", "data": data}), 201
    except Exception as e:
        current_app.logger.debug(f"Error in create_project: {e}")
        return (
            jsonify({"status": "error", "message": "Failed to create new project"}),
            500,
        )


@bp.route("/<project_uuid>", methods=["DELETE"])
@auth_manager.authenticate
@auth_manager.authorize_root
def delete_project(project_uuid: str) -> Response:
    """Deletes a specified project by its project UUID, then deletes the api key from AWS"""

    try:
        delete_sns_topic_from_aws(project_uuid)
        success = delete_project_by_id(project_uuid)
        if success:
            return "", 204
        else:
            return jsonify({"status": "error", "message": "Project not found"}), 404
    except Exception as e:
        current_app.logger.debug(f"Error in delete_project: {e}")
        return jsonify({"status": "error", "message": "Failed to delete project"}), 500


@bp.route("/<project_uuid>", methods=["PATCH"])
@auth_manager.authenticate
@auth_manager.authorize_root
def update_project(project_uuid: str) -> Response:
    """Updates the name of a specified project."""
    data = request.get_json()
    new_name = data.get("new_name")

    if not new_name:
        return jsonify({"status": "error", "message": "Missing project name"}), 400

    try:
        success = update_project_name(project_uuid, new_name)
        if success:
            data = {"uuid": project_uuid, "name": new_name}
            return jsonify({"status": "success", "data": data}), 200
        else:
            return jsonify({"status": "error", "message": "Project not found"}), 404
    except Exception as e:
        current_app.logger.debug(f"Error in update_project: {e}")
        return (
            jsonify({"status": "error", "message": "Failed to update project name"}),
            500,
        )
