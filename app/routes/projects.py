from flask import jsonify, request
from flask import Blueprint
from app.models import fetch_projects

bp = Blueprint('projects', __name__)

@bp.route('/', methods=['GET'])
def get_projects():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    try:
        data = fetch_projects(page, limit)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch projects", "error": str(e)}), 500
    
