"""Text processing utilities for tweet content."""

import re
from typing import Any, Dict, List

from xtract.config.logging import get_logger

logger = get_logger(__name__)


def expand_urls(text: str, url_entities: List[Dict[str, Any]]) -> str:
    """
    Replace t.co shortened URLs with their expanded versions.

    Twitter/X automatically shortens URLs in tweets to t.co links for tracking.
    This function replaces those shortened URLs with the original expanded URLs
    using the entity data provided by the X API.

    Args:
        text: Tweet text containing t.co URLs
        url_entities: List of URL entity objects from API response.
                     Each entity should have 'url' (t.co link) and
                     'expanded_url' (original URL) fields.

    Returns:
        str: Text with t.co URLs replaced by expanded URLs.
             Returns original text if expansion fails.

    Example:
        >>> entities = [{"url": "https://t.co/abc123", "expanded_url": "https://example.com"}]
        >>> expand_urls("Check this: https://t.co/abc123", entities)
        'Check this: https://example.com'
    """
    if not url_entities:
        logger.debug("No URL entities to expand")
        return text

    try:
        expanded_text = text

        # Process each URL entity
        for entity in url_entities:
            t_co_url = entity.get("url", "")
            expanded_url = entity.get("expanded_url", "")

            if not t_co_url or not expanded_url:
                logger.debug(f"Skipping entity with missing URL data: {entity}")
                continue

            # Escape special regex characters in the t.co URL
            t_co_pattern = re.escape(t_co_url)

            # Replace the t.co URL with expanded URL
            # The pattern ensures we match the URL but not trailing punctuation
            expanded_text = re.sub(t_co_pattern, expanded_url, expanded_text)

            logger.debug(f"Expanded URL: {t_co_url} -> {expanded_url}")

        logger.info(f"Expanded {len(url_entities)} URL(s) in tweet text")
        return expanded_text

    except Exception as e:
        logger.warning(f"Failed to expand URLs: {e}. Returning original text.")
        return text
