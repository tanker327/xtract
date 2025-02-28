"""
Utilities for handling media data from X posts.
"""

from typing import List, Dict, Any, Tuple


def extract_media_urls(media: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """
    Extract images and videos from tweet media data.
    
    Args:
        media: List of media items from the API
        
    Returns:
        Tuple[List[str], List[str]]: Tuple containing (images URLs, video URLs)
    """
    images, videos = [], []
    for item in media or []:
        if item.get("type") == "photo":
            if url := item.get("media_url_https"):
                images.append(url)
        elif item.get("type") == "video":
            variants = item.get("video_info", {}).get("variants", [])
            if best_variant := max(variants, key=lambda x: x.get("bitrate", 0), default={}):
                if url := best_variant.get("url"):
                    videos.append(url)
    return images, videos 