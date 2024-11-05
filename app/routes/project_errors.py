from flask import jsonify, request
from flask import Blueprint
from app.models import (
    fetch_data_by_project,
    delete_data_by_project,
)

bp = Blueprint('project_errors', __name__)

@bp.route('/', methods=['GET'])
def get_errors(pid):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    handled = request.args.get('handled', None)
    time = request.args.get('time', None)
    resolved = request.args.get('resolved', None)

    try:
        data = fetch_data_by_project(pid, page, limit, handled, time, resolved)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch data", "error": str(e)}), 500
    
@bp.route('/', methods=['DELETE'])
def delete_errors(pid):
    try:
        success = delete_data_by_project(pid)
        if success:
            return '', 204
        else: 
            return jsonify({"message": "No errors found for this project"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to delete errors", "error": str(e)}), 500