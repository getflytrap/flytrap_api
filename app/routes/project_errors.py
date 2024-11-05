from flask import jsonify, request
from flask import Blueprint
from app.models import (
    fetch_data,
)

bp = Blueprint('project_errors', __name__)

@bp.route('/projects/<pid>/errors', methods=['GET'])
def get_errors(pid):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    handled = request.args.get('handled', None)
    time = request.args.get('time', None)
    resolved = request.args.get('resolved', None)

    try:
        data = fetch_data(pid, page, limit, handled, time, resolved)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch data", "error": str(e)}), 500