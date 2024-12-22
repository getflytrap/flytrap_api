"""Configuration module for loading environment variables."""

import os
import json


def load_config(app, overrides=None):
    """
    Dynamically load configuration into the Flask app.
    This includes environment variables and secrets from AWS Secrets Manager.
    """

    overrides = overrides or {}

    # Determine environment
    environment = overrides.get("FLASK_ENV", os.getenv("FLASK_ENV", "development"))
    app.config["ENVIRONMENT"] = environment

    # Load environment specific settings
    if environment in ["development", "testing"]:
        # Use dotenv for local environments
        from dotenv import load_dotenv

        load_dotenv()

        app.config["DB_PASSWORD"] = os.getenv("PGPASSWORD")
        app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    # Load shared variables
    app.config["AWS_REGION"] = os.getenv("AWS_REGION")
    app.config["USAGE_PLAN_ID"] = os.getenv("USAGE_PLAN_ID")
    app.config["DB_HOST"] = os.getenv("PGHOST")
    app.config["DB_NAME"] = overrides.get("PGDATABASE", os.getenv("PGDATABASE"))
    app.config["DB_USER"] = os.getenv("PGUSER")
    app.config["DB_PORT"] = os.getenv("PGPORT")
    app.config["HTTPONLY"] = os.getenv("HTTPONLY") == "True"
    app.config["SECURE"] = os.getenv("SECURE") == "True"
    app.config["SAMESITE"] = os.getenv("SAMESITE")

    # Load production specific secrets
    if environment == "production":
        from app.utils import get_secret

        try:
            # Load secrets from AWS Secrets Manager
            jwt_secret = get_secret("jwt_secret_key", app.config["AWS_REGION"])
            app.config["JWT_SECRET_KEY"] = json.loads(jwt_secret)["jwt_secret_key"]

            db_credentials = get_secret(
                "flytrap_db_credentials", app.config["AWS_REGION"]
            )
            app.config["DB_PASSWORD"] = json.loads(db_credentials)["password"]
        except Exception as e:
            app.logger.error(f"Failed to load secrets: {e}")
            app.config["DB_PASSWORD"] = None
            app.config["JWT_SECRET_KEY"] = None
            raise e
