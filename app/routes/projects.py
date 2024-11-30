"""Projects routes module.

This module provides routes for managing projects, including creating, fetching,
updating, and deleting project records. Each route enforces root access authorization.
"""

from flask import jsonify, request, Response, current_app
from flask import Blueprint
from app.models import (
    fetch_projects,
    add_project,
    delete_project_by_id,
    update_project_name,
)
from app.utils.auth import TokenManager, AuthManager
from app.utils import (
    generate_uuid,
    associate_api_key_with_usage_plan,
    delete_api_key_from_aws,
    create_sns_topic,
    delete_sns_topic_from_aws,
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

    current_app.logger.debug(f"Fetching projects with page={page}, limit={limit}")

    if page < 1 or (limit is not None and limit < 1):
        current_app.logger.error(f"Invalid pagination parameters: page={page}, limit={limit}")
        return (
            jsonify({"message": "Invalid pagination parameters."}),
            400,
        )

    try:
        project_data = fetch_projects(page, limit)
        current_app.logger.info(f"Fetched {len(project_data)} projects for page={page}, limit={limit}")
        return jsonify({"payload": project_data}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch projects: {e}", exc_info=True)
        return jsonify({"message": "Failed to fetch projects."}), 500


@bp.route("", methods=["POST"])
@auth_manager.authenticate
@auth_manager.authorize_root
def create_project() -> Response:
    """Creates a new project with a unique project ID."""
    data = request.get_json()
    current_app.logger.debug("Received request to create a project.")

    if not data:
        current_app.logger.error("Invalid request: No JSON payload.")
        return jsonify({"message": "Invalid request."}), 400

    name = data.get("name")
    platform = data.get("platform")

    if not name or not platform:
        current_app.logger.error(f"Missing project name or platform in request: name={name}, platform={platform}")
        return (
            jsonify({"message": "Missing project name or platform."}),
            400,
        )

    project_uuid = generate_uuid()
    api_key = generate_uuid()
    current_app.logger.debug(f"Generated UUID for project: {project_uuid} and API key: {api_key}")

    try:
        topic_arn = create_sns_topic(project_uuid)
        add_project(name, project_uuid, api_key, platform, topic_arn)
        associate_api_key_with_usage_plan(name, api_key)
        current_app.logger.info(f"Project created successfully: {name} ({project_uuid})")
        
        project_data = {
            "uuid": project_uuid,
            "name": name,
            "platform": platform,
            "api_key": api_key,
        }
        
        return jsonify({"payload": project_data}), 201
    except Exception as e:
        current_app.logger.error(f"Failed to create project: {e}", exc_info=True)
        return jsonify({"message": "Failed to create project."}), 500


@bp.route("/<project_uuid>", methods=["DELETE"])
@auth_manager.authenticate
@auth_manager.authorize_root
def delete_project(project_uuid: str) -> Response:
    """Deletes a specified project by its project UUID."""
    current_app.logger.debug(f"Received request to delete project: {project_uuid}")

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier required."}), 400

    try:
        delete_sns_topic_from_aws(project_uuid)
        api_key = delete_project_by_id(project_uuid)

        if api_key:
            delete_api_key_from_aws(api_key)
            current_app.logger.info(f"Deleted project: {project_uuid}")
            return "", 204
        else:
            current_app.logger.warning(f"Project not found: {project_uuid}")
            return jsonify({"message": "Project not found."}), 404
    except Exception as e:
        current_app.logger.error(f"Failed to delete project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to delete project."}), 500


@bp.route("/<project_uuid>", methods=["PATCH"])
@auth_manager.authenticate
@auth_manager.authorize_root
def update_project(project_uuid: str) -> Response:
    """Updates the name of a specified project."""
    current_app.logger.debug(f"Received request to update project: {project_uuid}")

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier required."}), 400
    
    data = request.get_json()

    if not data:
        current_app.logger.error("Invalid request: No JSON payload.")
        return jsonify({"message": "Invalid request."}), 400

    new_name = data.get("new_name")

    if not new_name:
        current_app.logger.error("New project name is required but missing.")
        return jsonify({"message": "New project name required."}), 400

    try:
        success = update_project_name(project_uuid, new_name)
        if success:
            current_app.logger.info(f"Updated project {project_uuid} with new name: {new_name}")
            return "", 204
        else:
            current_app.logger.warning(f"Project not found for update: {project_uuid}")
            return jsonify({"message": "Project not found."}), 404
    except Exception as e:
        current_app.logger.error(f"Failed to update project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to update project."}), 500