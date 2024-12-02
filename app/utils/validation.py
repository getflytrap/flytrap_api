"""Validation utility."""

import re


def is_valid_email(email: str) -> bool:
    """Validates an email address format."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None
