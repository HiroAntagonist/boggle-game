# ABOUTME: Authentication utilities for password hashing and JWT tokens
# ABOUTME: Provides secure password handling and token generation/validation

from datetime import datetime, timedelta, timezone
from typing import Any, cast
import bcrypt
from jose import JWTError, jwt  # type: ignore[import-untyped]
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PASSWORD HASHING
# bcrypt automatically handles salt generation and secure hashing
# We use bcrypt directly (simpler than passlib)

# JWT CONFIGURATION
# SECRET_KEY must be set in environment variables or .env file
# In development: use .env file
# In production: use environment variables (never commit secrets to git)
SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError(
        "SECRET_KEY environment variable is not set. "
        "Create a .env file with SECRET_KEY=your-secret-key-here"
    )
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


# JWT TOKEN VALIDATION FOR PROTECTED ENDPOINTS

# HTTPBearer is a FastAPI security scheme that extracts the token from
# the Authorization header (expects "Bearer <token>" format)
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Dependency that validates JWT token and returns user ID.

    This extracts and validates the JWT token, returning the user_id.
    Use get_current_user_from_db() if you need the full User object.

    Args:
        credentials: HTTP Authorization credentials (Bearer token)

    Returns:
        User ID from validated token

    Raises:
        HTTPException: 401 if token is invalid or expired

    Example:
        @app.get("/protected")
        def protected_route(user_id: str = Depends(get_current_user)):
            return {"user_id": user_id}
    """
    # Extract token from credentials
    token = credentials.credentials

    # Decode and validate token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from token
    user_id: str | None = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def make_get_current_user_from_db() -> Any:
    """Factory function that creates the get_current_user_from_db dependency.

    This is needed to lazily import get_db and avoid circular imports.
    """
    from src.database import get_db
    from src.models import User

    def get_current_user_from_db(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),  # NOW this works!
    ) -> Any:
        """Get full User object from database for authenticated user.

        This is the MAIN authentication dependency to use in protected endpoints.
        It validates the JWT token and returns the User object from the database.

        Args:
            credentials: HTTP Authorization credentials (Bearer token)
            db: Database session (injected by FastAPI, respects overrides)

        Returns:
            User object from database

        Raises:
            HTTPException: 401 if token is invalid, expired, or user not found
        """
        # Extract and validate token
        token = credentials.credentials

        # Decode and validate token
        payload = decode_access_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract user_id from token
        user_id: str | None = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    return get_current_user_from_db


# Create the actual dependency
get_current_user_from_db = make_get_current_user_from_db()


def make_get_current_user_from_db_optional() -> Any:
    """Factory function for optional authentication dependency.

    Returns None if no token provided or token is invalid.
    Use this for endpoints that work for both authenticated and anonymous users.
    """
    from src.database import get_db
    from src.models import User

    def get_current_user_from_db_optional(
        credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
        db: Session = Depends(get_db),
    ) -> Any:
        """Get User object if authenticated, None otherwise.

        Args:
            credentials: Optional HTTP Authorization credentials
            db: Database session

        Returns:
            User object if authenticated, None otherwise
        """
        # No credentials provided - return None
        if credentials is None:
            return None

        # Extract token
        token = credentials.credentials

        # Decode and validate token
        payload = decode_access_token(token)
        if payload is None:
            return None

        # Extract user_id
        user_id: str | None = payload.get("user_id")
        if user_id is None:
            return None

        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        return user  # Could be None if user not found

    return get_current_user_from_db_optional


# Create the optional dependency
get_current_user_from_db_optional = make_get_current_user_from_db_optional()
