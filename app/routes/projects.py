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
    limit = request.args.get("limit", type=int)

    project_data = fetch_projects(page, limit)
    return jsonify({"result": "success", "payload": project_data}), 200


@bp.route("", methods=["POST"])
@auth_manager.authenticate
@auth_manager.authorize_root
def create_project() -> Response:
    """Creates a new project with a unique project ID."""
    data = request.get_json()

    if not data: 
        return jsonify({"result": "error", "message": "Invalid request"}), 400
    
    name = data.get("name")
    platform = data.get("platform")

    if not name or not platform:
        return jsonify({"result": "error", "message": "Missing project name or platform"}), 400
    

    result = add_project(name, platform)
    project_uuid = result["project_uuid"]
    api_key = result["api_key"]

    client = create_aws_client()
    if client:
        associate_api_key_with_usage_plan(client, name, api_key, USAGE_PLAN_ID)

    project_data = {"uuid": project_uuid, "name": name, "platform": platform, "api_key": api_key}
    return jsonify({"result": "success", "payload": project_data}), 201


@bp.route("/<project_uuid>", methods=["DELETE"])
@auth_manager.authenticate
@auth_manager.authorize_root
def delete_project(project_uuid: str) -> Response:
    """Deletes a specified project by its project UUID."""
    delete_sns_topic_from_aws(project_uuid)
    success = delete_project_by_id(project_uuid)
    if success:
        return "", 204
    else:
        return jsonify({"result": "error", "message": "Project not found"}), 404


@bp.route("/<project_uuid>", methods=["PATCH"])
@auth_manager.authenticate
@auth_manager.authorize_root
def update_project(project_uuid: str) -> Response:
    """Updates the name of a specified project."""
    data = request.get_json()

    if not data: 
        return jsonify({"result": "error", "message": "Invalid request"}), 400
    
    new_name = data.get("new_name")

    if not new_name:
        return jsonify({"result": "error", "message": "Missing project name"}), 400

    success = update_project_name(project_uuid, new_name)
    if success:
        return "", 204
    else:
        return jsonify({"result": "error", "message": "Project not found"}), 404

