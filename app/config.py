"""Configuration module for loading environment variables."""

import os
import json
import boto3
from typing import Optional
from dotenv import load_dotenv
from botocore.exceptions import ClientError

def get_secret(secret_name, region_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    return get_secret_value_response['SecretString']

ENVIRONMENT = os.getenv("FLASK_ENV", "development")
USAGE_PLAN_ID = os.getenv("USAGE_PLAN_ID")
AWS_REGION = os.getenv("AWS_REGION")
DB_HOST: Optional[str] = os.getenv("PGHOST")
DB_NAME: Optional[str] = os.getenv("PGDATABASE")
DB_USER: Optional[str] = os.getenv("PGUSER")
DB_PORT: Optional[str] = os.getenv("PGPORT")
HTTPONLY = True if os.getenv("HTTPONLY") == "True" else False
SECURE = True if os.getenv("SECURE") == "True" else False
SAMESITE = os.getenv("SAMESITE")
PATH = os.getenv("PATH")


if ENVIRONMENT == "development":
  load_dotenv()
  DB_PASSWORD: Optional[str] = os.getenv("PGPASSWORD")
  JWT_SECRET_KEY: Optional[str] = os.getenv("JWT_SECRET_KEY")
else:
  try:
    jwt_secret = get_secret("jwt_secret_key", AWS_REGION)
    JWT_SECRET_KEY = json.loads(jwt_secret)["jwt_secret_key"]

    db_credentials = get_secret("flytrap_db_credentials", AWS_REGION)
    DB_PASSWORD = json.loads(db_credentials)["password"]
  except Exception as e:
    JWT_SECRET_KEY = None
    DB_PASSWORD = None