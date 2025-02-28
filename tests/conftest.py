"""
Shared fixtures for pytest.
"""

import pytest
from unittest.mock import MagicMock

from xtract.models.post import Post, PostData
from xtract.models.user import UserDetails


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "name": "Test User",
        "screen_name": "testuser",
        "description": "This is a test user",
        "followers_count": 1000,
        "friends_count": 500,
        "location": "Test Location",
        "created_at": "Wed Feb 28 12:00:00 +0000 2024",
        "profile_image_url_https": "https://example.com/profile.jpg",
        "profile_banner_url": "https://example.com/banner.jpg",
        "statuses_count": 1500,
        "media_count": 100,
        "listed_count": 50,
        "verified": True,
        "is_blue_verified": True,
    }


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
                }
            }
        }
    }


@pytest.fixture
def sample_user_details():
    """Sample UserDetails instance for testing."""
    return UserDetails(
        name="Test User",
        screen_name="testuser",
        description="This is a test user",
        followers_count=1000,
        friends_count=500,
        location="Test Location",
        created_at="Wed Feb 28 12:00:00 +0000 2024",
        profile_image_url="https://example.com/profile.jpg",
        profile_banner_url="https://example.com/banner.jpg",
        statuses_count=1500,
        media_count=100,
        listed_count=50,
        is_verified=True,
        is_blue_verified=True,
    )


@pytest.fixture
def sample_post_data():
    """Sample PostData instance for testing."""
    return PostData(
        favorite_count=100,
        retweet_count=50,
        reply_count=25,
        quote_count=10,
        bookmark_count=5,
        is_quote_status=True,
        lang="en",
        source="Twitter Web App",
        possibly_sensitive=False,
        conversation_id="123456789",
        is_translatable=True,
        grok_analysis_button=False,
    )


@pytest.fixture
def sample_post(sample_user_details, sample_post_data):
    """Sample Post instance for testing."""
    return Post(
        tweet_id="123456789",
        username="testuser",
        created_at="Wed Feb 28 12:00:00 +0000 2024",
        text="This is a test post",
        view_count="5000",
        images=["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
        videos=[],
        user_details=sample_user_details,
        post_data=sample_post_data,
    )


@pytest.fixture
def mock_response():
    """Create a mock response for requests."""
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json = MagicMock(return_value={"guest_token": "mock_token"})
    return mock
