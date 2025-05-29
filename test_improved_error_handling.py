#!/usr/bin/env python3
"""
Test script to verify improved error handling for replies fetching.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from xtract import download_x_post

def test_replies_error_handling():
    """Test that the improved error handling works for replies fetching."""
    print("Testing improved error handling for replies fetching...")
    
    # Test with a real tweet ID but with include_replies=True to trigger the 404 error
    tweet_id = "1897892533616685238"
    
    print(f"Attempting to download tweet {tweet_id} with replies...")
    post = download_x_post(tweet_id, include_replies=True)
    
    if post:
        print(f"✅ Successfully downloaded tweet: {post.text[:100]}...")
        print(f"📊 Replies fetched: {len(post.replies) if post.replies else 0}")
        if post.replies is None:
            print("⚠️  Replies were not fetched (expected due to 404 error)")
        return True
    else:
        print("❌ Failed to download tweet")
        return False

if __name__ == "__main__":
    success = test_replies_error_handling()
    sys.exit(0 if success else 1)