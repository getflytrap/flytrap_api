"""Utilities package initializer."""

from .db_config import db_read_connection, db_write_connection
from .db_helpers import (
    calculate_total_project_pages,
    fetch_errors_by_project,
    fetch_rejections_by_project,
    calculate_total_error_pages,
    calculate_total_user_project_pages,
)
from .uuid_generator import generate_uuid
from .validation import is_valid_email
from .aws_helpers import create_aws_client, associate_api_key_with_usage_plan

__all__ = [
    "db_read_connection",
    "db_write_connection" "calculate_total_project_pages",
    "fetch_errors_by_project",
    "fetch_rejections_by_project",
    "calculate_total_error_pages",
    "generate_uuid",
    "is_valid_email",
    "calculate_total_user_project_pages",
    "create_aws_client",
    "associate_api_key_with_usage_plan",
]
