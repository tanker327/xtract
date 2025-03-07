"""
Markdown utilities for X post data.
"""

import os
import logging
from typing import Optional
from datetime import datetime

from xtract.config.logging import get_logger
from xtract.models.post import Post

# Get a logger for this module
logger = get_logger(__name__)


def post_to_markdown(post: Post, include_stats: bool = True, include_metadata: bool = True) -> tuple[dict, str]:
    """
    Convert a Post object to a tuple of metadata dict and markdown content.

    Args:
        post: The Post object to convert
        include_stats: Whether to include post statistics (default: True)
        include_metadata: Whether to include YAML frontmatter metadata (default: True)

    Returns:
        tuple[dict, str]: Tuple containing metadata dict and markdown content
    """
    logger.info(f"Converting post {post.tweet_id} to Markdown")
    logger.debug(f"Markdown options: include_stats={include_stats}, include_metadata={include_metadata}")
    
    # Parse the date to a more readable format
    try:
        # X date format: "Wed Feb 28 12:00:00 +0000 2024"
        created_date = datetime.strptime(post.created_at, "%a %b %d %H:%M:%S %z %Y")
        formatted_date = created_date.strftime("%Y-%m-%d %H:%M:%S")
        logger.debug(f"Parsed date: {formatted_date}")
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse date '{post.created_at}': {e}")
        formatted_date = post.created_at

    md = []
    metadata = {}
    
    # Add YAML frontmatter metadata section
    if include_metadata:
        logger.debug("Adding YAML frontmatter metadata")
        metadata = {
            "tweet_id": post.tweet_id,
            "author": post.username,
            "display_name": post.user_details.name,
            "date": formatted_date,
            "is_verified": post.user_details.is_verified,
            "image_count": len(post.images),
            "video_count": len(post.videos),
            "views": post.view_count,
            "likes": post.post_data.favorite_count,
            "retweets": post.post_data.retweet_count,
            "replies": post.post_data.reply_count,
            "quotes": post.post_data.quote_count,
            "has_quoted_tweet": bool(post.quoted_tweet),
            "url": f"https://x.com/{post.username}/status/{post.tweet_id}",
            "downloaded_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "downloaded_by": "xtract"
        }
        
        if post.quoted_tweet:
            logger.debug(f"Including quoted tweet metadata for tweet ID: {post.quoted_tweet.tweet_id}")
            metadata.update({
                "quoted_tweet_id": post.quoted_tweet.tweet_id,
                "quoted_tweet_author": post.quoted_tweet.username
            })
    
    # Start with the post header - user info and timestamp
    verification_badge = "✓" if post.user_details.is_verified else ""
    
    logger.debug("Adding post header and content")
    md.append(f"# Post by @{post.username} {verification_badge}")
    md.append(f"**{post.user_details.name}** (@{post.username}) • {formatted_date}")
    md.append("")
    
    # Post content
    md.append(post.text)
    md.append("")
    
    # Images
    if post.images:
        logger.debug(f"Adding {len(post.images)} images to Markdown")
        md.append("## Images")
        for i, image_url in enumerate(post.images, 1):
            md.append(f"![Image {i}]({image_url})")
        md.append("")
    
    # Videos
    if post.videos:
        logger.debug(f"Adding {len(post.videos)} videos to Markdown")
        md.append("## Videos")
        for i, video_url in enumerate(post.videos, 1):
            md.append(f"[Video {i}]({video_url})")
        md.append("")
    
    # Quoted tweet if present
    if post.quoted_tweet:
        logger.debug(f"Processing quoted tweet {post.quoted_tweet.tweet_id}")
        md.append("## Quoted Tweet")
        md.append("---")
        # Recursively format the quoted tweet but without stats to keep it cleaner
        # Also skip metadata for quoted tweets
        quoted_md = post_to_markdown(post.quoted_tweet, include_stats=False, include_metadata=False)[1]
        # Indent the quoted tweet content to make it visually distinct
        quoted_md_indented = "\n".join([f"> {line}" for line in quoted_md.split("\n")])
        md.append(quoted_md_indented)
        md.append("---")
        md.append("")
        
    # Post stats if requested
    if include_stats:
        logger.debug("Adding post statistics")
        md.append("## Stats")
        md.append(f"* **Views:** {post.view_count}")
        md.append(f"* **Likes:** {post.post_data.favorite_count}")
        md.append(f"* **Retweets:** {post.post_data.retweet_count}")
        md.append(f"* **Replies:** {post.post_data.reply_count}")
        md.append(f"* **Quotes:** {post.post_data.quote_count}")
        md.append("")
    
    # Add a metadata footer with the tweet ID for reference
    md.append(f"*Tweet ID: {post.tweet_id}*")
    
    logger.debug("Markdown generation complete")
    return metadata, "\n".join(md)


def save_post_as_markdown(post: Post, output_dir: str = None, filename: str = None) -> str:
    """
    Save a Post as a Markdown file.

    Args:
        post: The Post object to save
        output_dir: Directory to save the Markdown file (default: cwd or tweet directory)
        filename: Name of the Markdown file (default: tweet_<tweet_id>.md)

    Returns:
        str: Path to the saved Markdown file
    """
    logger.info(f"Saving post {post.tweet_id} as Markdown")
    
    # Generate Markdown content and metadata
    logger.debug("Generating Markdown content and metadata")
    metadata, markdown_content = post_to_markdown(post)
    
    # Add YAML frontmatter if metadata exists
    if metadata:
        yaml_frontmatter = ["---"]
        for key, value in metadata.items():
            yaml_frontmatter.append(f"{key}: {value}")
        yaml_frontmatter.append("---\n")
        markdown_content = "\n".join(yaml_frontmatter) + markdown_content
    
    # Determine the output directory
    if output_dir is None:
        output_dir = os.getcwd()
        logger.debug(f"No output directory specified, using current directory: {output_dir}")
    else:
        logger.debug(f"Using specified output directory: {output_dir}")
    
    # Ensure the directory exists
    logger.debug(f"Ensuring directory exists: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine the filename
    if filename is None:
        filename = f"tweet_{post.tweet_id}.md"
        logger.debug(f"No filename specified, using default: {filename}")
    else:
        logger.debug(f"Using specified filename: {filename}")
    
    # Make sure the filename has the .md extension
    if not filename.endswith(".md"):
        filename += ".md"
        logger.debug(f"Added .md extension to filename: {filename}")
    
    # Create the full file path
    file_path = os.path.join(output_dir, filename)
    logger.debug(f"Full file path: {file_path}")
    
    # Write the Markdown content to the file
    logger.debug(f"Writing Markdown content to file: {file_path}")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    logger.info(f"Markdown file saved to: {file_path}")
    print(f"Markdown file saved to: {file_path}")
    return file_path 