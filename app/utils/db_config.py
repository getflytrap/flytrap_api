import psycopg2
from psycopg2.extensions import connection
from app.config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT

def get_db_connection() -> connection:
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )