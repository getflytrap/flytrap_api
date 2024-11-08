from flask import jsonify, Blueprint, Response

bp = Blueprint("webhook", __name__)


@bp.route("", methods=["POST"])
def receive_webhook() -> Response:
    """
    Receives a webhook POST request.

    This endpoint is a placeholder for handling incoming webhooks.
    Upon receiving a request, it will send a JSON response indicating success.
    Future implementation will involve using Server-Sent Events (SSE) to notify
    a connected dashboard.

    Returns:
        Response: JSON response containing a status and message, with HTTP status code
        200.
    """
    # TODO: implement SSE to notify dashboard
    return jsonify({"status": "success", "message": "Webhook received."}), 200
