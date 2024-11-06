"""Validation utility.

This module provides functions for validating input data, such as email addresses.

Functions:
    is_valid_email: Checks if a given email address is in a valid format.
"""

import re


def is_valid_email(email: str) -> bool:
    """Validates an email address format.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email address is valid, False otherwise.
    """
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None
