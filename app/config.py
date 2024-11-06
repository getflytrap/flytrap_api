"""Configuration module for loading environment variables.

This module loads essential environment variables from a `.env` file
(or system environment)for configuring database connections and JWT authentication.
Environment variables are accessed using the `dotenv` package, which simplifies
configuration management for different environments.

Attributes:
    DB_HOST (Optional[str]): Host address of the PostgreSQL database.
    DB_NAME (Optional[str]): Name of the PostgreSQL database.
    DB_USER (Optional[str]): Username for the PostgreSQL database.
    DB_PASS (Optional[str]): Password for the PostgreSQL database user.
    DB_PORT (Optional[str]): Port number on which the PostgreSQL database is running.
    secret_key (str): Secret key for JWT authentication.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

DB_HOST: Optional[str] = os.getenv("PGHOST")
DB_NAME: Optional[str] = os.getenv("PGDATABASE")
DB_USER: Optional[str] = os.getenv("PGUSER")
DB_PASS: Optional[str] = os.getenv("PGPASSWORD")
DB_PORT: Optional[str] = os.getenv("PGPORT")

secret_key: str = os.getenv("JWT_SECRET_KEY")
