# ABOUTME: Authentication utilities for password hashing and JWT tokens
# ABOUTME: Provides secure password handling and token generation/validation

from datetime import datetime, timedelta, timezone
from typing import Any, cast
import bcrypt
from jose import JWTError, jwt  # type: ignore[import-untyped]

# PASSWORD HASHING
# bcrypt automatically handles salt generation and secure hashing
# We use bcrypt directly (simpler than passlib)

# JWT CONFIGURATION
# In production, this should come from environment variables!
# For now, using a hardcoded secret for development/learning
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to env vars
ALGORITHM = "HS256"  # HMAC with SHA-256


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt.

    Args:
        password: Plain-text password to hash

    Returns:
        Hashed password string (includes salt)

    Example:
        >>> hashed = hash_password("mysecret123")
        >>> print(hashed)
        '$2b$12$...'  # bcrypt hash (60 characters)
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')

    # Generate salt and hash password
    # bcrypt.gensalt() creates a random salt
    # bcrypt.hashpw() hashes the password with the salt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string (decode from bytes)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a hashed password.

    Args:
        plain_password: Plain-text password to verify
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("mysecret123")
        >>> verify_password("mysecret123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    # Convert both to bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')

    # bcrypt.checkpw() verifies the password
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    """Create a JWT access token.

    Args:
        data: Dictionary of data to encode in token (e.g., user_id, username)
        expires_delta: How long until token expires

    Returns:
        JWT token string

    Example:
        >>> from datetime import timedelta
        >>> data = {"user_id": "uuid-123", "username": "alice"}
        >>> token = create_access_token(data, timedelta(minutes=30))
        >>> print(token)
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    # Copy data to avoid mutating original
    to_encode = data.copy()

    # Add expiration time
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode["exp"] = expire

    # Encode JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return cast(str, encoded_jwt)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT access token.

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary of decoded data if valid, None if invalid/expired

    Example:
        >>> token = create_access_token({"user_id": "123"}, timedelta(minutes=30))
        >>> decoded = decode_access_token(token)
        >>> print(decoded["user_id"])
        '123'
    """
    try:
        # Decode JWT token
        # This automatically validates expiration and signature
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return cast(dict[str, Any], payload)
    except JWTError:
        # Invalid token, expired token, or malformed token
        return None
