"""UUID generation utility.

This module provides a function for generating unique UUIDs, which can be used
as identifiers in various parts of the application.

Functions:
    generate_uuid: Generates a new UUID as a string.
"""

import uuid


def generate_uuid() -> str:
    """Generates a new UUID.

    Returns:
        str: A unique UUID string in the form of a version 4 UUID.
    """
    return str(uuid.uuid4())
