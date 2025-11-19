"""
Utilities for handling media data from X posts.
"""

from typing import List, Dict, Any, Tuple

from xtract.config.logging import get_logger

# Get a logger for this module
logger = get_logger(__name__)


def extract_media_urls(media: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """
    Extract images and videos from tweet media data.

    Args:
        media: List of media items from the API

    Returns:
        Tuple[List[str], List[str]]: Tuple containing (images URLs, video URLs)
    """
    logger.debug(f"Extracting media URLs from {len(media) if media else 0} media items")
    images, videos = [], []
    for item in media or []:
        if item.get("type") == "photo":
            if url := item.get("media_url_https"):
                logger.debug(f"Found image URL: {url}")
                images.append(url)
        elif item.get("type") in ["video", "animated_gif"]:
            variants = item.get("video_info", {}).get("variants", [])
            logger.debug(f"Found {len(variants)} video variants for {item.get('type')}")
            if best_variant := max(variants, key=lambda x: x.get("bitrate", 0), default={}):
                if url := best_variant.get("url"):
                    logger.debug(f"Selected best video URL: {url}")
                    videos.append(url)

    logger.debug(f"Extracted {len(images)} images and {len(videos)} videos")
    return images, videos
