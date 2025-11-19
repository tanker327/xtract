"""
Configuration module for the xtract library.
"""

from xtract.config.logging import get_logger
from xtract.config.constants import (
    BEARER_TOKEN,
    DEFAULT_HEADERS,
    GUEST_TOKEN_URL,
    TWEET_DATA_URL,
    DEFAULT_FEATURES,
    DEFAULT_FIELD_TOGGLES,
    DEFAULT_OUTPUT_DIR,
)

# Create a logger for this module
logger = get_logger(__name__)
logger.debug("Config module initialized")

__all__ = [
    "BEARER_TOKEN",
    "DEFAULT_HEADERS",
    "GUEST_TOKEN_URL",
    "TWEET_DATA_URL",
    "DEFAULT_FEATURES",
    "DEFAULT_FIELD_TOGGLES",
    "DEFAULT_OUTPUT_DIR",
]
