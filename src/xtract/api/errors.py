"""
Custom exceptions for the xtract library.
"""


class APIError(Exception):
    """Base exception for API errors."""
    pass


class TokenExpiredError(APIError):
    """Exception raised when a token has expired or is invalid (typically 403 errors)."""
    pass
