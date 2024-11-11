from flask import jsonify, Blueprint, Response

bp = Blueprint("webhook", __name__)


@bp.route("", methods=["POST"])
def receive_webhook() -> Response:
    """Receives a webhook POST request."""
    return jsonify({"status": "success", "message": "Webhook received."}), 200
