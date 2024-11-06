"""Routes module for organizing and exporting blueprints.

This module imports and aliases blueprints from individual route modules, making them
available for easy registration in the application setup (`app/__init__.py`).

Attributes:
    projects_bp (Blueprint): Blueprint for project-related routes.
    issues_bp (Blueprint): Blueprint for project issue-related routes.
    project_users_bp (Blueprint): Blueprint for project user-related routes.
    users_bp (Blueprint): Blueprint for user-related routes.
    auth_bp (Blueprint): Blueprint for authentication-related routes.
"""

from app.routes.projects import bp as projects_bp
from app.routes.project_issues import bp as issues_bp
from app.routes.project_users import bp as project_users_bp
from app.routes.users import bp as users_bp
from app.routes.auth import bp as auth_bp
