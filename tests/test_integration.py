import os
import pytest
import tempfile
import json
from unittest.mock import patch, MagicMock

from xtract import download_x_post
from xtract.models.post import Post


@pytest.fixture
def sample_tweet_data():
    """Sample tweet data for testing."""
    return {
        "data": {
            "tweetResult": {
                "result": {
                    "rest_id": "123456789",
                    "views": {"count": "5000"},
                    "source": "Twitter Web App",
                    "is_translatable": True,
                    "legacy": {
                        "created_at": "Wed Feb 28 12:00:00 +0000 2024",
                        "full_text": "This is a test tweet with #hashtags and @mentions",
                        "favorite_count": 100,
                        "retweet_count": 50,
                        "reply_count": 25,
                        "quote_count": 10,
                        "is_quote_status": True,
                        "lang": "en",
                        "extended_entities": {
                            "media": [
                                {
                                    "type": "photo",
                                    "media_url_https": "https://example.com/image1.jpg",
                                },
                                {
                                    "type": "photo",
                                    "media_url_https": "https://example.com/image2.jpg",
                                },
                            ]
                        },
                    },
                    "core": {
                        "user_results": {
                            "result": {
                                "legacy": {
                                    "screen_name": "testuser",
                                    "name": "Test User",
                                    "description": "This is a test user account",
                                    "followers_count": 5000,
                                    "friends_count": 1000,
                                    "statuses_count": 1200,
                                    "verified": True,
                                }
                            }
                        }
                    },
                    "note_tweet": {"note_tweet_results": {"result": {}}},
                    "quoted_status_result": {
                        "result": {
                            "__typename": "Tweet",
                            "rest_id": "987654321",
                            "views": {"count": "3000"},
                            "legacy": {
                                "created_at": "Wed Feb 28 10:00:00 +0000 2024",
                                "full_text": "This is a quoted tweet",
                                "favorite_count": 50,
                                "retweet_count": 20,
                            },
                            "core": {
                                "user_results": {
                                    "result": {
                                        "legacy": {
                                            "screen_name": "quoteduser",
                                            "name": "Quoted User",
                                            "followers_count": 2000,
                                        }
                                    }
                                }
                            },
                            "note_tweet": {"note_tweet_results": {"result": {}}},
                        }
                    },
                }
            }
        }
    }


@patch("xtract.api.client.get_guest_token")
@patch("xtract.api.client.fetch_tweet_data")
def test_full_tweet_download_flow(mock_fetch, mock_token, sample_tweet_data):
    """Test the full tweet download flow with a rich tweet example."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup mocks
        mock_token.return_value = "mock_token"
        mock_fetch.return_value = sample_tweet_data

        # Download the tweet
        post = download_x_post("123456789", output_dir=temp_dir)

        # Check the main post details
        assert isinstance(post, Post)
        assert post.tweet_id == "123456789"
        assert post.username == "testuser"
        assert post.view_count == "5000"
        assert "This is a test tweet" in post.text
        assert len(post.images) == 2
        assert post.user_details.followers_count == 5000
        assert post.user_details.is_verified is True
        assert post.post_data.favorite_count == 100
        assert post.post_data.retweet_count == 50

        # Check the quoted tweet
        assert post.quoted_tweet is not None
        assert post.quoted_tweet.tweet_id == "987654321"
        assert post.quoted_tweet.username == "quoteduser"
        assert post.quoted_tweet.text == "This is a quoted tweet"
        assert post.quoted_tweet.user_details.followers_count == 2000

        # Check that files were created
        tweet_dir = os.listdir(temp_dir)[0]
        tweet_path = os.path.join(temp_dir, tweet_dir)
        assert os.path.exists(tweet_path)

        # Check the JSON file structure
        json_file = os.path.join(tweet_path, "tweet.json")
        assert os.path.exists(json_file)

        with open(json_file, "r") as f:
            saved_data = json.load(f)

        assert saved_data["tweet_id"] == "123456789"
        assert saved_data["username"] == "testuser"
        assert "user_details" in saved_data
        assert "post_data" in saved_data
        assert "quoted_tweet" in saved_data
        assert saved_data["quoted_tweet"]["tweet_id"] == "987654321"


@patch("xtract.api.client.fetch_tweet_data")
def test_download_with_custom_cookies(mock_fetch, sample_tweet_data):
    """Test tweet download with custom cookies."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup mock
        mock_fetch.return_value = sample_tweet_data

        # Custom cookies
        custom_cookies = "auth_token=123456; ct0=abcdef"

        # Download with cookies
        post = download_x_post("123456789", output_dir=temp_dir, cookies=custom_cookies)

        # Verify the cookies were used
        headers = mock_fetch.call_args[0][1]
        assert headers["Cookie"] == custom_cookies

        # Basic post validation
        assert isinstance(post, Post)
        assert post.tweet_id == "123456789"
