import uuid


def generate_uuid() -> str:
    """Generates a new UUID."""
    return str(uuid.uuid4())
