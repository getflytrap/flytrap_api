from flask import jsonify, Blueprint, Response, request
from flask_socketio import join_room
from app.socketio_instance import socketio
from app.utils import send_sns_notification
from app.utils.auth import TokenManager, AuthManager
from app.models import fetch_project_users, get_project_name

token_manager = TokenManager()
auth_manager = AuthManager(token_manager)

bp = Blueprint("notifications", __name__)


@bp.route("/webhook", methods=["POST"])
def receive_webhook() -> Response:
    """Receives a webhook POST request."""
    data = request.get_json()
    project_uuid = data.get("project_id")

    if project_uuid:
        send_sns_notification(project_uuid)
        send_notification_to_frontend(project_uuid)
        return jsonify({"status": "success", "message": "Webhook received."}), 200
    else:
        return (
            jsonify({"status": "error", "message": "project_id missing in request."}),
            400,
        )


@socketio.on("connect", namespace="/notifications")
def handle_connect():
    token = request.args.get("token")

    if token and token_manager.validate_token(token):
        payload = token_manager.decode_token(token)
        user_uuid = payload["user_uuid"]

        if user_uuid:
            join_room(user_uuid)
            socketio.emit(
                "authenticated",
                {"message": "Connection authenticated"},
                room=request.sid,
                namespace="/notifications",
            )
        else:
            return False
    else:
        return False


@socketio.on("disconnect", namespace="/notifications")
def handle_disconnect():
    pass


def send_notification_to_frontend(project_uuid):
    project_users = fetch_project_users(project_uuid)
    project_name = get_project_name(project_uuid)

    for user_uuid in project_users:
        socketio.emit(
            "new_notification",
            {"project_name": project_name},
            namespace="/notifications",
            room=user_uuid,
        )
