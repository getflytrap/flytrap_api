from flask import jsonify, Blueprint, Response, request, current_app
from flask_socketio import join_room
from app.socketio import socketio
from app.utils import send_sns_notification
from app.utils.auth import TokenManager, AuthManager
from app.models import fetch_project_users, get_project_name, fetch_most_recent_log

token_manager = TokenManager()
auth_manager = AuthManager(token_manager)

bp = Blueprint("notifications", __name__)


@bp.route("/webhook", methods=["POST"])
def receive_webhook() -> Response:
    """Receives a webhook POST request."""
    current_app.logger.debug("Webhook received.")
    data = request.get_json()

    if not data:
        current_app.logger.error("Invalid request: No JSON payload.")
        return jsonify({"message": "Invalid request"}), 400

    project_uuid = data.get("project_id")

    if not project_uuid:
        current_app.logger.error("Project identifier is required but missing.")
        return (
            jsonify({"message": "Project identifier required."}),
            400,
        )
    
    try:
        send_sns_notification(project_uuid)
        current_app.logger.info(f"SNS notification sent for project UUID={project_uuid}.")
        send_notification_to_frontend(project_uuid)
        current_app.logger.info(f"Frontend notifications sent for project UUID={project_uuid}.")
        return jsonify({"message": "Webhook received."}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to handle webhook for project UUID={project_uuid}: {e}", exc_info=True)
        return jsonify({"message": "Failed to process webhook."}), 500


@socketio.on("connect", namespace="/notifications")
def handle_connect():
    current_app.logger.debug("SocketIO connection attempt.")

    # TODO: send via headers instead of params?
    token = request.args.get("token")

    if not token:
        current_app.logger.warning("SocketIO connection failed: missing token.")
        return False

    try:
        if token_manager.validate_token(token):
            payload = token_manager.decode_token(token)
            user_uuid = payload["user_uuid"]

            if user_uuid:
                join_room(user_uuid)
                current_app.logger.info(f"User UUID={user_uuid} joined notifications room.")
                socketio.emit(
                    "authenticated",
                    {"message": "Connection authenticated"},
                    room=request.sid,
                    namespace="/notifications",
                )
            else:
                current_app.logger.error("Decoded token missing 'user_uuid'.")
                return False
        else:
            current_app.logger.warning("SocketIO connection failed: invalid token.")
            return False
    except Exception as e:
        current_app.logger.error(f"Failed to handle SocketIO connection: {e}", exc_info=True)
        return False


@socketio.on("disconnect", namespace="/notifications")
def handle_disconnect():
    """Handles user disconnection from the notifications namespace."""
    current_app.logger.info("SocketIO client disconnected from notifications namespace.")


def send_notification_to_frontend(project_uuid):
    current_app.logger.debug(f"Preparing frontend notifications for project UUID={project_uuid}.")

    try:
        project_users = fetch_project_users(project_uuid)
        project_name = get_project_name(project_uuid)
        latest_issue = fetch_most_recent_log(project_uuid)

        data = {
            "project_uuid": project_uuid,
            "project_name": project_name,
            "issue_data": latest_issue,
        }

        for user_uuid in project_users:
            current_app.logger.debug(f"Sending notification to user UUID={user_uuid}.")
            socketio.emit(
                "new_notification",
                data,
                namespace="/notifications",
                room=user_uuid,
            )
        
        current_app.logger.info(f"Notifications sent to {len(project_users)} users for project UUID={project_uuid}.")
    except Exception as e:
        current_app.logger.error(f"Failed to send notifications for project UUID={project_uuid}: {e}", exc_info=True)
        raise
