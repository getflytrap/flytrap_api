from flask import jsonify, request
from flask import Blueprint
from app.models import (
    fetch_issues_by_project,
    delete_issues_by_project,
    fetch_error,
    fetch_rejection,
)

bp = Blueprint('project_issues', __name__)

@bp.route('/', methods=['GET'])
def get_errors(pid):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    handled = request.args.get('handled', None)
    time = request.args.get('time', None)
    resolved = request.args.get('resolved', None)

    try:
        data = fetch_issues_by_project(pid, page, limit, handled, time, resolved)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch data", "error": str(e)}), 500
    
@bp.route('/', methods=['DELETE'])
def delete_errors(pid):
    try:
        success = delete_issues_by_project(pid)
        if success:
            return '', 204
        else: 
            return jsonify({"message": "No errors found for this project"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to delete errors", "error": str(e)}), 500
    
@bp.route('/errors/<eid>', methods=['GET'])
def get_error(_, eid):
    try:
        error = fetch_error(eid)
        if error:
            return jsonify(error), 200
        else:
            return jsonify({"message": "Error not found"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to retrieve error", "error": str(e)}), 500
    
@bp.route('/rejections/<rid>', methods=['GET'])
def get_rejection(_, rid):
    try:
        error = fetch_rejection(rid)
        if error:
            return jsonify(error), 200
        else:
            return jsonify({"message": "Error not found"}), 404
    except Exception as e:
        return jsonify({"message": "Failed to retrieve error", "error": str(e)}), 500