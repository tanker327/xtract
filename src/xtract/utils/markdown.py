"""
Markdown utilities for X post data.
"""

import os
from typing import Optional
from datetime import datetime

from xtract.models.post import Post


def post_to_markdown(post: Post, include_stats: bool = True) -> str:
    """
    Convert a Post object to a Markdown string.

    Args:
        post: The Post object to convert
        include_stats: Whether to include post statistics (default: True)

    Returns:
        str: Markdown representation of the post
    """
    # Parse the date to a more readable format
    try:
        # X date format: "Wed Feb 28 12:00:00 +0000 2024"
        created_date = datetime.strptime(post.created_at, "%a %b %d %H:%M:%S %z %Y")
        formatted_date = created_date.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        formatted_date = post.created_at

    # Start with the post header - user info and timestamp
    verification_badge = "✓" if post.user_details.is_verified else ""
    
    md = []
    md.append(f"# Post by @{post.username} {verification_badge}")
    md.append(f"**{post.user_details.name}** (@{post.username}) • {formatted_date}")
    md.append("")
    
    # Post content
    md.append(post.text)
    md.append("")
    
    # Images
    if post.images:
        md.append("## Images")
        for i, image_url in enumerate(post.images, 1):
            md.append(f"![Image {i}]({image_url})")
        md.append("")
    
    # Videos
    if post.videos:
        md.append("## Videos")
        for i, video_url in enumerate(post.videos, 1):
            md.append(f"[Video {i}]({video_url})")
        md.append("")
    
    # Quoted tweet if present
    if post.quoted_tweet:
        md.append("## Quoted Tweet")
        md.append("---")
        # Recursively format the quoted tweet but without stats to keep it cleaner
        quoted_md = post_to_markdown(post.quoted_tweet, include_stats=False)
        # Indent the quoted tweet content to make it visually distinct
        quoted_md_indented = "\n".join([f"> {line}" for line in quoted_md.split("\n")])
        md.append(quoted_md_indented)
        md.append("---")
        md.append("")
        
    # Post stats if requested
    if include_stats:
        md.append("## Stats")
        md.append(f"* **Views:** {post.view_count}")
        md.append(f"* **Likes:** {post.post_data.favorite_count}")
        md.append(f"* **Retweets:** {post.post_data.retweet_count}")
        md.append(f"* **Replies:** {post.post_data.reply_count}")
        md.append(f"* **Quotes:** {post.post_data.quote_count}")
        md.append("")
    
    # Add a metadata footer with the tweet ID for reference
    md.append(f"*Tweet ID: {post.tweet_id}*")
    
    return "\n".join(md)


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
    # Generate Markdown content
    markdown_content = post_to_markdown(post)
    
    # Determine the output directory
    if output_dir is None:
        output_dir = os.getcwd()
    
    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine the filename
    if filename is None:
        filename = f"tweet_{post.tweet_id}.md"
    
    # Make sure the filename has the .md extension
    if not filename.endswith(".md"):
        filename += ".md"
    
    # Create the full file path
    file_path = os.path.join(output_dir, filename)
    
    # Write the Markdown content to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"Markdown file saved to: {file_path}")
    return file_path 