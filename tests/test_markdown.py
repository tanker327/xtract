"""
Tests for Markdown utilities.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from xtract.utils.markdown import post_to_markdown, save_post_as_markdown


def test_post_to_markdown(sample_post):
    """Test converting a post to Markdown."""
    # Call the function
    markdown = post_to_markdown(sample_post)
    
    # Check the result
    assert markdown is not None
    assert isinstance(markdown, str)
    
    # Check that it contains the expected elements
    assert f"# Post by @{sample_post.username}" in markdown
    assert sample_post.text in markdown
    assert "## Stats" in markdown
    assert f"**Views:** {sample_post.view_count}" in markdown
    assert f"**Likes:** {sample_post.post_data.favorite_count}" in markdown
    
    # Check image inclusion
    for img in sample_post.images:
        assert img in markdown


def test_post_to_markdown_with_quoted_tweet(sample_post):
    """Test converting a post with a quoted tweet to Markdown."""
    # Create a quoted tweet
    quoted_post = MagicMock()
    quoted_post.tweet_id = "987654321"
    quoted_post.username = "quoteduser"
    quoted_post.text = "This is a quoted tweet"
    quoted_post.created_at = "Wed Feb 28 10:00:00 +0000 2024"
    quoted_post.user_details.name = "Quoted User"
    quoted_post.user_details.is_verified = False
    quoted_post.images = []
    quoted_post.videos = []
    quoted_post.view_count = "100"
    quoted_post.post_data.favorite_count = 10
    quoted_post.post_data.retweet_count = 5
    quoted_post.post_data.reply_count = 2
    quoted_post.post_data.quote_count = 1
    quoted_post.quoted_tweet = None
    
    # Set the quoted tweet
    sample_post.quoted_tweet = quoted_post
    
    # Patch post_to_markdown for the quoted tweet to avoid recursion issues with the mock
    with patch("xtract.utils.markdown.post_to_markdown", side_effect=[
        "Quoted tweet markdown", "Main post with quoted tweet"
    ]):
        # Call the function
        markdown = post_to_markdown(sample_post)
        
        # Check that it references the quoted tweet
        assert "## Quoted Tweet" in markdown


def test_save_post_as_markdown(sample_post):
    """Test saving a post as a Markdown file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Patch post_to_markdown to return a known value
        with patch("xtract.utils.markdown.post_to_markdown", return_value="# Test Markdown"):
            # Call the function
            file_path = save_post_as_markdown(sample_post, output_dir=temp_dir)
            
            # Verify the file exists
            assert os.path.exists(file_path)
            
            # Verify the file has the correct name
            assert file_path.endswith(f"tweet_{sample_post.tweet_id}.md")
            
            # Verify the file contains the expected content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert content == "# Test Markdown" 