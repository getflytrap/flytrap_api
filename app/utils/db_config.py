import os
import psycopg2

DB_HOST = os.getenv('PGHOST')
DB_NAME = os.getenv('PGDATABASE')
DB_USER = os.getenv('PGUSER')
DB_PASS = os.getenv('PGPASSWORD')
DB_PORT = os.getenv('PGPORT')

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )