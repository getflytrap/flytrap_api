"""Utilities package initializer.

This module imports and aggregates utility functions and decorators from various utility
modules, making them accessible through `__all__` for use across the application.
These utilities include database connection decorators, helper functions for pagination,
UUID generation, and email validation.

Imported Functions and Decorators:
    - Database connection decorators: db_read_connection, db_write_connection
    - Database helper functions: calculate_total_project_pages, fetch_errors_by_project,
      fetch_rejections_by_project, calculate_total_error_pages
    - UUID generation: generate_uuid
    - Validation functions: is_valid_email
"""

from .db_config import db_read_connection, db_write_connection
from .db_helpers import (
    calculate_total_project_pages,
    fetch_errors_by_project,
    fetch_rejections_by_project,
    calculate_total_error_pages,
)
from .uuid_generator import generate_uuid
from .validation import is_valid_email

__all__ = [
    "db_read_connection",
    "db_write_connection" "calculate_total_project_pages",
    "fetch_errors_by_project",
    "fetch_rejections_by_project",
    "calculate_total_error_pages",
    "generate_uuid",
    "is_valid_email",
]
