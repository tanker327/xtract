import json
import os
import pytest
from unittest.mock import patch, MagicMock

from xtract.models.post import Post


@pytest.fixture
def quoted_tweet_response():
    """Load the quoted tweet response fixture."""
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'quoted_tweet_response.json')
    with open(fixture_path, 'r') as f:
        return json.load(f)


def test_quoted_tweet_included(quoted_tweet_response):
    """Test that a quoted tweet is properly included in the Post object."""
    # Extract the tweet data from the API response
    tweet_data = quoted_tweet_response['data']['tweetResult']['result']
    legacy = tweet_data.get('legacy', {})
    user = tweet_data.get('core', {}).get('user_results', {}).get('result', {}).get('legacy', {})
    note_tweet = tweet_data.get('note_tweet', {}).get('note_tweet_results', {}).get('result', {})
    
    # Create a Post object from the extracted data
    post = Post.from_api_data(tweet_data, legacy, user, note_tweet)
    
    # Convert the Post object to a dictionary
    post_dict = post.to_dict()
    
    # Assert that the quoted tweet is included in the dictionary
    assert 'quoted_tweet' in post_dict
    
    # Verify the main tweet details
    assert post_dict['tweet_id'] == "1895573480835539451"
    assert post_dict['username'] == "elonmusk"
    # Use unicode string comparison to avoid apostrophe issues
    assert post_dict['text'] == "That\u2019s the situation"
    
    # Verify that the quoted tweet has the correct data
    quoted_tweet = post_dict['quoted_tweet']
    assert quoted_tweet['tweet_id'] == "1895571173691494806"
    assert quoted_tweet['username'] == "AutismCapital"
    assert "Elon Musk talks with Joe Rogan about George Soros" in quoted_tweet['text']
    
    # Verify the quoted tweet has videos
    assert len(quoted_tweet['videos']) > 0


def test_quoted_tweet_from_tweet_location(quoted_tweet_response):
    """Test that a quoted tweet is found when it's in the tweet object (not legacy)."""
    # Extract and modify the tweet data to ensure it's only in the tweet object
    tweet_data = quoted_tweet_response['data']['tweetResult']['result']
    legacy = tweet_data.get('legacy', {}).copy()
    
    # Create copies to avoid modifying the original fixture
    tweet_data_copy = tweet_data.copy()
    legacy_copy = legacy.copy()
    
    # Make sure legacy doesn't have quoted_status_result
    if 'quoted_status_result' in legacy_copy:
        del legacy_copy['quoted_status_result']
    
    user = tweet_data.get('core', {}).get('user_results', {}).get('result', {}).get('legacy', {})
    note_tweet = tweet_data.get('note_tweet', {}).get('note_tweet_results', {}).get('result', {})
    
    # Create a Post object from the extracted data
    post = Post.from_api_data(tweet_data_copy, legacy_copy, user, note_tweet)
    
    # Convert the Post object to a dictionary
    post_dict = post.to_dict()
    
    # Assert that the quoted tweet is included in the dictionary
    assert 'quoted_tweet' in post_dict
    assert post_dict['quoted_tweet']['tweet_id'] == "1895571173691494806"


def test_quoted_tweet_from_legacy_location():
    """Test that a quoted tweet is found when it's in the legacy object."""
    # Create a mock response where the quoted tweet is in the legacy object
    tweet_data = {
        "rest_id": "123456",
        "views": {"count": "1000"},
        "source": "Twitter for iPhone",
        "is_translatable": False,
        "grok_analysis_button": True
    }
    
    legacy = {
        "created_at": "Fri Feb 28 20:35:10 +0000 2025",
        "full_text": "This is a test tweet",
        "is_quote_status": True,
        "favorite_count": 100,
        "retweet_count": 50,
        "quoted_status_result": {
            "result": {
                "rest_id": "789012",
                "views": {"count": "500"},
                "source": "Twitter Web App",
                "legacy": {
                    "created_at": "Fri Feb 28 20:00:00 +0000 2025",
                    "full_text": "This is the quoted tweet",
                    "favorite_count": 50,
                    "retweet_count": 25
                },
                "core": {
                    "user_results": {
                        "result": {
                            "legacy": {
                                "screen_name": "quoteduser",
                                "name": "Quoted User"
                            }
                        }
                    }
                }
            }
        }
    }
    
    user = {
        "screen_name": "testuser",
        "name": "Test User"
    }
    
    note_tweet = {}
    
    # Create a Post object from the mock data
    post = Post.from_api_data(tweet_data, legacy, user, note_tweet)
    
    # Convert the Post object to a dictionary
    post_dict = post.to_dict()
    
    # Assert that the quoted tweet is included in the dictionary
    assert 'quoted_tweet' in post_dict
    assert post_dict['quoted_tweet']['tweet_id'] == "789012"
    assert post_dict['quoted_tweet']['username'] == "quoteduser"
    assert post_dict['quoted_tweet']['text'] == "This is the quoted tweet"


def test_no_quoted_tweet():
    """Test that a tweet without a quoted tweet doesn't include the quoted_tweet field."""
    # Create a mock response without a quoted tweet
    tweet_data = {
        "rest_id": "123456",
        "views": {"count": "1000"},
        "source": "Twitter for iPhone",
        "is_translatable": False,
        "grok_analysis_button": True
    }
    
    legacy = {
        "created_at": "Fri Feb 28 20:35:10 +0000 2025",
        "full_text": "This is a test tweet",
        "is_quote_status": False,
        "favorite_count": 100,
        "retweet_count": 50
    }
    
    user = {
        "screen_name": "testuser",
        "name": "Test User"
    }
    
    note_tweet = {}
    
    # Create a Post object from the mock data
    post = Post.from_api_data(tweet_data, legacy, user, note_tweet)
    
    # Convert the Post object to a dictionary
    post_dict = post.to_dict()
    
    # Assert that the quoted tweet is not included in the dictionary
    assert 'quoted_tweet' not in post_dict 