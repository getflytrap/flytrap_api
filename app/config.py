"""Configuration module for loading environment variables."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

DB_HOST: Optional[str] = os.getenv("PGHOST")
DB_NAME: Optional[str] = os.getenv("PGDATABASE")
DB_USER: Optional[str] = os.getenv("PGUSER")
DB_PASS: Optional[str] = os.getenv("PGPASSWORD")
DB_PORT: Optional[str] = os.getenv("PGPORT")

SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")

HTTPONLY = True if os.getenv("HTTPONLY") == "True" else False
SECURE = True if os.getenv("SECURE") == "True" else False
SAMESITE = os.getenv("SAMESITE")
PATH = os.getenv("PATH")
