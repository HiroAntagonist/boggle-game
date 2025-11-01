# ABOUTME: Tests for authentication functions (password hashing, JWT tokens)
# ABOUTME: Verifies secure password handling and token generation/validation

import pytest
from datetime import timedelta

from src.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


# ============================================================================
# PASSWORD HASHING TESTS
# ============================================================================


def test_hash_password_returns_hashed_string() -> None:
    """Test that password hashing returns a different string."""
    password = "mysecretpassword123"
    hashed = hash_password(password)

    # Hashed password should be different from plain password
    assert hashed != password

    # Hashed password should be a non-empty string
    assert isinstance(hashed, str)
    assert len(hashed) > 0


def test_hash_password_same_password_different_hashes() -> None:
    """Test that hashing the same password twice produces different hashes.

    This is important for security - bcrypt uses a random salt.
    """
    password = "samepassword"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Should produce different hashes due to random salt
    assert hash1 != hash2


def test_verify_password_correct_password() -> None:
    """Test that verify_password returns True for correct password."""
    password = "correctpassword"
    hashed = hash_password(password)

    # Correct password should verify
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect_password() -> None:
    """Test that verify_password returns False for incorrect password."""
    correct_password = "correctpassword"
    wrong_password = "wrongpassword"
    hashed = hash_password(correct_password)

    # Wrong password should not verify
    assert verify_password(wrong_password, hashed) is False


def test_verify_password_empty_password() -> None:
    """Test that empty password doesn't verify against any hash."""
    password = "somepassword"
    hashed = hash_password(password)

    # Empty password should not verify
    assert verify_password("", hashed) is False


# ============================================================================
# JWT TOKEN TESTS
# ============================================================================


def test_create_access_token_returns_string() -> None:
    """Test that JWT token creation returns a string token."""
    data = {"user_id": "test-uuid-123", "username": "alice"}
    expires_delta = timedelta(minutes=30)

    token = create_access_token(data, expires_delta)

    # Token should be a non-empty string
    assert isinstance(token, str)
    assert len(token) > 0

    # JWT tokens have 3 parts separated by dots
    assert token.count(".") == 2


def test_decode_access_token_valid_token() -> None:
    """Test that valid JWT token can be decoded."""
    original_data = {"user_id": "test-uuid-456", "username": "bob"}
    expires_delta = timedelta(minutes=30)

    # Create token
    token = create_access_token(original_data, expires_delta)

    # Decode token
    decoded_data = decode_access_token(token)

    # Should successfully decode
    assert decoded_data is not None
    assert decoded_data["user_id"] == "test-uuid-456"
    assert decoded_data["username"] == "bob"


def test_decode_access_token_invalid_token() -> None:
    """Test that invalid JWT token returns None."""
    invalid_token = "this.is.not.a.valid.jwt.token"

    decoded_data = decode_access_token(invalid_token)

    # Should return None for invalid token
    assert decoded_data is None


def test_decode_access_token_expired_token() -> None:
    """Test that expired JWT token returns None."""
    data = {"user_id": "test-uuid-789", "username": "charlie"}
    # Token that expires immediately (negative timedelta)
    expires_delta = timedelta(seconds=-1)

    # Create already-expired token
    token = create_access_token(data, expires_delta)

    # Decode should fail for expired token
    decoded_data = decode_access_token(token)

    # Should return None for expired token
    assert decoded_data is None


def test_decode_access_token_malformed_token() -> None:
    """Test that malformed JWT token returns None."""
    malformed_tokens = [
        "",  # Empty string
        "not.a.token",  # Not enough parts
        "header.payload",  # Missing signature
        "a" * 100,  # Random string
    ]

    for malformed_token in malformed_tokens:
        decoded_data = decode_access_token(malformed_token)
        assert decoded_data is None, f"Should reject malformed token: {malformed_token}"
