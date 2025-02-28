#!/usr/bin/env python3
"""
Test script to verify the xtract package works correctly.
"""

from xtract import download_x_post

def main():
    """Test the xtract package."""
    # Replace with a valid tweet ID
    tweet_id = "1892413385804792307"
    
    print(f"Testing xtract package with tweet ID: {tweet_id}")
    post = download_x_post(tweet_id)
    
    if post:
        print("\nTest successful! Post details:")
        print(f"Username: {post.username}")
        print(f"Text: {post.text[:100]}...")
        print(f"Created at: {post.created_at}")
        print(f"View count: {post.view_count}")
        print(f"Images: {len(post.images)}")
        print(f"Videos: {len(post.videos)}")
        print(f"User followers: {post.user_details.followers_count}")
        print(f"Likes: {post.post_data.favorite_count}")
        print(f"Retweets: {post.post_data.retweet_count}")
        
        if post.quoted_tweet:
            print("\nQuoted tweet found!")
            print(f"Quoted username: {post.quoted_tweet.username}")
            print(f"Quoted text: {post.quoted_tweet.text[:100]}...")
            print(f"Quoted created at: {post.quoted_tweet.created_at}")
            print(f"Quoted view count: {post.quoted_tweet.view_count}")
            print(f"Quoted images: {len(post.quoted_tweet.images)}")
            print(f"Quoted videos: {len(post.quoted_tweet.videos)}")
    else:
        print("Test failed: Could not download post.")

if __name__ == "__main__":
    main() 