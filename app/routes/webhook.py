from flask import jsonify, request, Blueprint, Response
from app.utils.aws_helpers import send_sns_notification

bp = Blueprint("webhook", __name__)


@bp.route("", methods=["POST"])
def receive_webhook() -> Response:
    """Receives a webhook POST request."""
    data = request.get_json()
    project_id = data.get('project_id')

    if project_id:
        send_sns_notification(project_id)

    return jsonify({"status": "success", "message": "Webhook received."}), 200
