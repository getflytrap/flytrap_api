"""Project Issues routes module.

This module provides routes for managing project-specific issues.
It includes routes for fetching, updating, and deleting issues related to projects, with
authorization enforced via JWT. Each route performs specific operations on errors or
rejections, such as resolving or deleting individual items.
"""

from flask import jsonify, request, Response, current_app
from flask import Blueprint
from app.models import (
    fetch_issues_by_project,
    delete_issues_by_project,
    fetch_error,
    fetch_rejection,
    update_error_resolved,
    update_rejection_resolved,
    delete_error_by_id,
    delete_rejection_by_id,
    get_issue_summary,
)
from app.utils.auth import TokenManager, AuthManager

token_manager = TokenManager()
auth_manager = AuthManager(token_manager)

bp = Blueprint("project_issues", __name__)


@bp.route("", methods=["GET"])
@auth_manager.authenticate
@auth_manager.authorize_project_access
def get_issues(project_uuid: str) -> Response:
    """Fetches a paginated list of issues for a specified project."""
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    handled = request.args.get("handled", None)
    time = request.args.get("time", None)
    resolved = request.args.get("resolved", None)
    
    current_app.logger.debug(f"Fetching issues for project UUID={project_uuid} with page={page}, limit={limit}")

    if page < 1 or limit < 1:
        current_app.logger.error(f"Invalid pagination parameters: page={page}, limit={limit}")
        return (
            jsonify({"message": "Invalid pagination parameters."}),
            400,
        )

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier is required."}), 400

    try:
        issue_data = fetch_issues_by_project(
            project_uuid, page, limit, handled, time, resolved
        )
        current_app.logger.info(f"Fetched {len(issue_data['issues'])} issues for project UUID={project_uuid}.")
        return jsonify({"payload": issue_data}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch issues for project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to fetch issues."}), 500


@bp.route("", methods=["DELETE"])
@auth_manager.authenticate
@auth_manager.authorize_project_access
def delete_issues(project_uuid: str) -> Response:
    """Deletes all issues for a specified project."""
    current_app.logger.debug(f"Deleting all issues for project UUID={project_uuid}.")

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier required."}), 400

    try:
        success = delete_issues_by_project(project_uuid)
        if success:
            current_app.logger.info(f"Deleted all issues for project UUID={project_uuid}.")
            return "", 204
        else:
            current_app.logger.warning(f"No issues found for project UUID={project_uuid}.")
            return (
                jsonify({"message": "No issues found for this project."}),
                404,
            )
    except Exception as e:
        current_app.logger.error(f"Failed to delete issues for project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to delete issues."}), 500


@bp.route("/errors/<error_uuid>", methods=["GET"])
@auth_manager.authenticate
@auth_manager.authorize_project_access
def get_error(project_uuid: str, error_uuid: str) -> Response:
    """Retrieves a specific error by its ID."""
    current_app.logger.debug(f"Fetching error UUID={error_uuid} for project UUID={project_uuid}.")

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier required."}), 400
        
    if not error_uuid:
        current_app.logger.error("Error identifier is required but missing.")
        return jsonify({"message": "Error identifier required."}), 400
    
    try:
        error = fetch_error(project_uuid, error_uuid)
        if error:
            current_app.logger.info(f"Error UUID={error_uuid} fetched for project UUID={project_uuid}.")
            return jsonify({"payload": error}), 200
        else:
            current_app.logger.warning(f"Error UUID={error_uuid} not found for project UUID={project_uuid}.")
            return jsonify({"message": "Error not found."}), 404
    except Exception as e:
        current_app.logger.error(f"Failed to fetch error UUID={error_uuid} for project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to fetch error."}), 500


@bp.route("/rejections/<rejection_uuid>", methods=["GET"])
@auth_manager.authenticate
@auth_manager.authorize_project_access
def get_rejection(project_uuid: str, rejection_uuid: str) -> Response:
    """Retrieves a specific rejection by its UUID."""
    current_app.logger.debug(f"Fetching rejection UUID={rejection_uuid} for project UUID={project_uuid}.")

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier required."}), 400
        
    if not rejection_uuid:
        current_app.logger.error("Rejection identifier is required but missing.")
        return jsonify({"message": "Rejection identifier required."}), 400
    
    try:
        rejection = fetch_rejection(project_uuid, rejection_uuid)
        if rejection:
            current_app.logger.info(f"Rejection UUID={rejection_uuid} fetched for project UUID={project_uuid}.")
            return jsonify({"payload": rejection}), 200
        else:
            current_app.logger.warning(f"Rejection UUID={rejection_uuid} not found for project UUID={project_uuid}.")
            return jsonify({"message": "Rejection not found."}), 404
    except Exception as e:
        current_app.logger.error(f"Failed to fetch rejection UUID={rejection_uuid} for project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to fetch rejection."}), 500


@bp.route("/errors/<error_uuid>", methods=["PATCH"])
@auth_manager.authenticate
@auth_manager.authorize_project_access
def toggle_error(project_uuid: str, error_uuid: str) -> Response:
    """Toggles the resolved state of a specific error."""
    current_app.logger.debug(f"Toggling resolved status of error UUID={error_uuid} for project UUID={project_uuid}.")

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier required."}), 400
        
    if not error_uuid:
        current_app.logger.error("Error identifier is required but missing.")
        return jsonify({"message": "Error identifier required."}), 400
    
    data = request.get_json()

    if not data:
        current_app.logger.error("Invalid request: No JSON payload.")
        return jsonify({"message": "Invalid request."}), 400
    
    new_resolved_state = data.get("resolved")

    if new_resolved_state is None:
        current_app.logger.error("New resolved state is required but missing.")
        return jsonify({"message": "Missing resolved state."}), 400

    try:
        success = update_error_resolved(error_uuid, new_resolved_state)
        if success:
            current_app.logger.info(f"Error UUID={error_uuid} resolved state updated in project UUID={project_uuid}.")
            return "", 204
        else:
            current_app.logger.warning(f"Error UUID={error_uuid} not found in project UUID={project_uuid}.")
            return jsonify({"message": "Error not found."}), 404
    except Exception as e:
        current_app.logger.error(f"Failed to toggle error UUID={error_uuid} for project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to toggle error resolved state."}), 500


@bp.route("/rejections/<rejection_uuid>", methods=["PATCH"])
@auth_manager.authenticate
@auth_manager.authorize_project_access
def toggle_rejection(project_uuid: str, rejection_uuid: str) -> Response:
    """Toggles the resolved state of a specific rejection."""
    current_app.logger.debug(f"Toggling resolved state of rejection UUID={rejection_uuid} for project UUID={project_uuid}.")

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier required."}), 400
        
    if not rejection_uuid:
        current_app.logger.error("Rejection identifier is required but missing.")
        return jsonify({"message": "Rejection identifier required."}), 400

    data = request.get_json()
    if not data:
        current_app.logger.error("Invalid request: No JSON payload.")
        return jsonify({"message": "Invalid request."}), 400
    
    new_resolved_state = data.get("resolved")

    if new_resolved_state is None:
        current_app.logger.error("New resolved state is required but missing.")
        return jsonify({"message": "Missing resolved state."}), 400

    try:
        success = update_rejection_resolved(rejection_uuid, new_resolved_state)
        if success:
            current_app.logger.info(f"Rejection UUID={rejection_uuid} resolved state updated in project UUID={project_uuid}.")
            return "", 204
        else:
            current_app.logger.warning(f"Rejection UUID={rejection_uuid} not found in project UUID={project_uuid}.")
            return jsonify({"message": "Rejection not found."}), 404
    except Exception as e:
        current_app.logger.error(f"Failed to toggle rejection UUID={rejection_uuid} for project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to toggle rejection resolved state."}), 500


@bp.route("/errors/<error_uuid>", methods=["DELETE"])
@auth_manager.authenticate
@auth_manager.authorize_project_access
def delete_error(project_uuid: str, error_uuid: str) -> Response:
    """Deletes a specific error by its UUID."""
    current_app.logger.debug(f"Deleting error UUID={error_uuid} from project UUID={project_uuid}.")

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier required."}), 400
        
    if not error_uuid:
        current_app.logger.error("Error identifier is required but missing.")
        return jsonify({"message": "Error identifier required."}), 400
    
    try:
        success = delete_error_by_id(error_uuid)
        if success:
            current_app.logger.info(f"Error UUID={error_uuid} deleted from project UUID={project_uuid}.")
            return "", 204
        else:
            current_app.logger.warning(f"Error UUID={error_uuid} not found in project UUID={project_uuid}.")
            return jsonify({"message": "Error not found."}), 404
    except Exception as e:
        current_app.logger.error(f"Failed to delete error UUID={error_uuid} from project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to delete error."}), 500


@bp.route("/rejections/<rejection_uuid>", methods=["DELETE"])
@auth_manager.authenticate
@auth_manager.authorize_project_access
def delete_rejection(project_uuid: str, rejection_uuid: str) -> Response:
    """Deletes a specific rejection by its UUID."""
    current_app.logger.debug(f"Deleting rejection UUID={rejection_uuid} from project UUID={project_uuid}.")

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier required."}), 400
        
    if not rejection_uuid:
        current_app.logger.error("Rejection identifier is required but missing.")
        return jsonify({"message": "Rejection identifier required."}), 400

    try:
        success = delete_rejection_by_id(rejection_uuid)
        if success:
            current_app.logger.info(f"Rejection UUID={rejection_uuid} deleted from project UUID={project_uuid}.")
            return "", 204
        else:
            current_app.logger.warning(f"Rejection UUID={rejection_uuid} not found in project UUID={project_uuid}.")
            return jsonify({"message": "Rejection not found."}), 404
    except Exception as e:
        current_app.logger.error(f"Failed to delete rejection UUID={rejection_uuid} from project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to delete rejection."}), 500


@bp.route("/summary", methods=["GET"])
@auth_manager.authenticate
@auth_manager.authorize_project_access
def get_summary(project_uuid: str) -> Response:
    """Gets issue count per day for the last 7 days for this project."""
    current_app.logger.debug(f"Fetching issue summary for project UUID={project_uuid}.")

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return jsonify({"message": "Project identifier required."}), 400

    try:
        daily_counts = get_issue_summary(project_uuid)
        current_app.logger.info(f"Fetched issue summary for project UUID={project_uuid}.")
        return jsonify({"payload": daily_counts}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch issue summary for project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to fetch issue summary."}), 500
