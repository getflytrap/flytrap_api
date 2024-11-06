"""Authentication utilities initializer.

This module imports and exposes authentication classes for handling JWT-based user
authentication and root access authorization. By aggregating these classes, the module
simplifies access to authentication-related functionality across the application.

Imported Classes:
    - JWTAuth: Manages JWT-based user authentication.
    - RootAuth: Handles root-level access authorization.

Attributes:
    __all__ (list): List of public classes available for import from the auth utilities.
"""

from .jwt_auth import JWTAuth

__all__ = ["JWTAuth"]
