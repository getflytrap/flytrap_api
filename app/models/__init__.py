"""Models package initializer."""

from .projects import (
    fetch_projects,
    add_project,
    delete_project_by_id,
    update_project_name,
)
from .project_issues import (
    fetch_issues_by_project,
    delete_issues_by_project,
    fetch_error,
    fetch_rejection,
    update_error_resolved,
    update_rejection_resolved,
    delete_error_by_id,
    delete_rejection_by_id,
)
from .project_users import (
    fetch_project_users,
    add_user_to_project,
    remove_user_from_project,
)
from .users import (
    fetch_all_users,
    add_user,
    delete_user_by_id,
    update_password,
    fetch_user_by_email,
    user_is_root,
    fetch_projects_for_user,
    get_user_info
)

__all__ = [
    "fetch_projects",
    "add_project",
    "delete_project_by_id",
    "update_project_name",
    "fetch_issues_by_project",
    "delete_issues_by_project",
    "fetch_error",
    "fetch_rejection",
    "update_error_resolved",
    "update_rejection_resolved",
    "delete_error_by_id",
    "delete_rejection_by_id",
    "fetch_project_users",
    "add_user_to_project",
    "remove_user_from_project",
    "fetch_all_users",
    "add_user",
    "delete_user_by_id",
    "update_password",
    "fetch_user_by_email",
    "user_is_root",
    "fetch_projects_for_user",
    "get_user_info"
]
