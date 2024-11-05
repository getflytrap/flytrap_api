import os
import psycopg2
from flask import jsonify
from flask import Blueprint

bp = Blueprint('main', __name__)

DB_HOST = os.getenv('PGHOST')
DB_NAME = os.getenv('PGDATABASE')
DB_USER = os.getenv('PGUSER')
DB_PASS = os.getenv('PGPASSWORD')
DB_PORT = os.getenv('PGPORT')

def get_db_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    return connection

@bp.route('/errors', methods=['GET'])
def get_errors():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT
            id, name, message, created_at, line_number, col_number, project_id, stack_trace, handled
        FROM error_logs
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        error_log = []
        for row in rows:
            error_entry = {
                "error_id": row[0],
                "name": row[1],
                "message": row[2],
                "created_at": row[3],
                "line_number": row[4],
                "col_number": row[5],
                "project_id": row[6],
                "stack_trace": row[7],
                "handled": row[8]
            }

            error_log.append(error_entry)

    except Exception as e:
        return jsonify({"message": "Failed to fetch data", "error": str(e)}), 500

    return jsonify(error_log), 200