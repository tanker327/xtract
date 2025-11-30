"""Test that media URLs (t.co links in text) are properly expanded."""

from xtract.models.post import Post


def test_media_url_expansion_without_note_tweet():
    """Test that t.co media URLs are expanded when there's no note_tweet."""
    # Simulate a regular tweet with media URL in text but no note_tweet
    # This is what happens when a tweet has media and the full_text
    # ends with a t.co link to the media
    tweet = {
        "rest_id": "1234567890",
        "views": {"count": "1000"},
        "source": "Twitter for iPhone",
    }

    legacy = {
        "created_at": "Mon Jan 01 12:00:00 +0000 2024",
        "full_text": "Check out this amazing video! https://t.co/abc123xyz",
        "entities": {
            "urls": [],  # Regular URL entities (empty in this case)
            "hashtags": [],
            "user_mentions": [],
        },
        "extended_entities": {
            "media": [
                {
                    "type": "video",
                    "url": "https://t.co/abc123xyz",
                    "expanded_url": "https://x.com/user/status/1234567890/video/1",
                    "media_url_https": "https://pbs.twimg.com/ext_tw_video_thumb/123/pu/img/video.jpg",
                }
            ]
        },
        "favorite_count": 100,
        "retweet_count": 50,
    }

    user = {
        "screen_name": "testuser",
        "name": "Test User",
        "description": "Test account",
        "followers_count": 1000,
        "friends_count": 500,
        "location": "Test Location",
        "created_at": "Mon Jan 01 12:00:00 +0000 2020",
        "profile_image_url_https": "https://pbs.twimg.com/profile_images/test.jpg",
    }

    note_tweet = {}  # No note_tweet

    # Create Post object
    post = Post.from_api_data(tweet, legacy, user, note_tweet)

    # The t.co link should be expanded
    assert (
        "t.co/abc123xyz" not in post.text
    ), f"Media t.co URL should be expanded. Text: {post.text}"

    # Check that it was replaced with the direct media URL (media_url_https)
    assert (
        "pbs.twimg.com/ext_tw_video_thumb/123/pu/img/video.jpg" in post.text
    ), f"Media URL should be expanded to direct media URL. Text: {post.text}"


def test_note_tweet_already_clean():
    """Test that note_tweets already have clean text without media t.co links."""
    # For note tweets, the note_tweet.text is already complete and doesn't
    # have the truncated t.co link
    tweet = {
        "rest_id": "1234567890",
        "views": {"count": "1000"},
        "source": "Twitter for iPhone",
    }

    legacy = {
        "created_at": "Mon Jan 01 12:00:00 +0000 2024",
        # The legacy full_text is truncated and has t.co link
        "full_text": "This is a long tweet that gets truncated... https://t.co/abc123xyz",
        "entities": {"urls": [], "hashtags": [], "user_mentions": []},
        "extended_entities": {
            "media": [
                {
                    "type": "video",
                    "url": "https://t.co/abc123xyz",
                    "expanded_url": "https://x.com/user/status/1234567890/video/1",
                    "media_url_https": "https://pbs.twimg.com/ext_tw_video_thumb/123/pu/img/video.jpg",
                }
            ]
        },
        "favorite_count": 100,
        "retweet_count": 50,
    }

    user = {
        "screen_name": "testuser",
        "name": "Test User",
        "description": "Test account",
        "followers_count": 1000,
        "friends_count": 500,
        "location": "Test Location",
        "created_at": "Mon Jan 01 12:00:00 +0000 2020",
        "profile_image_url_https": "https://pbs.twimg.com/profile_images/test.jpg",
    }

    # note_tweet has the full complete text without truncation
    note_tweet = {
        "text": "This is a long tweet that gets truncated but here's the full text without the media URL at the end because it's a note tweet and the media is handled separately.",
        "entity_set": {"urls": []},
    }

    # Create Post object
    post = Post.from_api_data(tweet, legacy, user, note_tweet)

    # Should use the note_tweet text, which doesn't have t.co links
    assert "t.co" not in post.text
    assert "This is a long tweet that gets truncated but here's the full text" in post.text
