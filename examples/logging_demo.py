#!/usr/bin/env python
"""
Demo script to show logging functionality in xtract.
"""

import sys
import logging
from xtract import download_x_post
from xtract.config.logging import configure_logging

# Configure logging to show DEBUG level messages
configure_logging(level=logging.DEBUG)

# Get a logger for this script
logger = logging.getLogger("xtract.examples.logging_demo")

def main():
    """Run the logging demo."""
    logger.info("Starting logging demo")
    
    # Check if a tweet ID or URL was provided
    if len(sys.argv) < 2:
        logger.error("No tweet ID or URL provided")
        print("Usage: python logging_demo.py <tweet_id_or_url>")
        return 1
    
    post_identifier = sys.argv[1]
    logger.info(f"Processing post identifier: {post_identifier}")
    
    # Download the post
    post = download_x_post(post_identifier)
    
    if post:
        logger.info(f"Successfully downloaded post by @{post.username}")
        logger.info(f"Post text: {post.text[:50]}...")
        logger.info(f"Post has {len(post.images)} images and {len(post.videos)} videos")
    else:
        logger.error("Failed to download post")
        return 1
    
    logger.info("Logging demo completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 