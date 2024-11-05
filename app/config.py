import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('PGHOST')
DB_NAME = os.getenv('PGDATABASE')
DB_USER = os.getenv('PGUSER')
DB_PASS = os.getenv('PGPASSWORD')
DB_PORT = os.getenv('PGPORT')