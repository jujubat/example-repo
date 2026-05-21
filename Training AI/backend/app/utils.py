from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """Return a hashed version of *password* suitable for storage."""
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored hash."""
    return check_password_hash(password_hash, password)
