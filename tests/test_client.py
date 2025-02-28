import os
import pytest
import requests
from unittest.mock import patch, MagicMock

from xtract.api.client import get_guest_token, fetch_tweet_data, download_x_post
from xtract.api.errors import APIError
from xtract.models.post import Post


@pytest.fixture
def mock_response():
    """Create a mock response for requests."""
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json = MagicMock(return_value={"guest_token": "mock_token"})
    return mock


@patch("requests.post")
def test_get_guest_token_success(mock_post, mock_response):
    """Test successful guest token retrieval."""
    mock_post.return_value = mock_response
    
    token = get_guest_token()
    
    assert token == "mock_token"
    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()
    mock_response.json.assert_called_once()


@patch("requests.post")
def test_get_guest_token_error(mock_post):
    """Test error handling in guest token retrieval."""
    mock_post.side_effect = requests.RequestException("API error")
    
    with pytest.raises(APIError):
        get_guest_token()


@patch("requests.get")
def test_fetch_tweet_data_success(mock_get, mock_response):
    """Test successful tweet data fetching."""
    mock_response.json.return_value = {"data": {"tweetResult": {"result": {}}}}
    mock_get.return_value = mock_response
    
    headers = {"Authorization": "Bearer mock_token"}
    data = fetch_tweet_data("123456789", headers)
    
    assert data == {"data": {"tweetResult": {"result": {}}}}
    mock_get.assert_called_once()
    mock_response.raise_for_status.assert_called_once()
    mock_response.json.assert_called_once()


@patch("requests.get")
def test_fetch_tweet_data_error(mock_get):
    """Test error handling in tweet data fetching."""
    mock_get.side_effect = requests.RequestException("API error")
    
    with pytest.raises(APIError):
        fetch_tweet_data("123456789", {})


@patch("xtract.api.client.ensure_directory")
@patch("xtract.api.client.save_json")
@patch("xtract.api.client.get_guest_token")
@patch("xtract.api.client.fetch_tweet_data")
def test_download_x_post_success(mock_fetch, mock_token, mock_save, mock_dir):
    """Test successful tweet download."""
    # Mock the data returned by the API
    mock_token.return_value = "mock_token"
    mock_fetch.return_value = {
        "data": {
            "tweetResult": {
                "result": {
                    "rest_id": "123456789",
                    "legacy": {
                        "created_at": "Wed Feb 28 12:00:00 +0000 2024",
                        "full_text": "This is a test tweet",
                    },
                    "core": {
                        "user_results": {
                            "result": {
                                "legacy": {
                                    "screen_name": "testuser",
                                    "name": "Test User",
                                }
                            }
                        }
                    },
                    "views": {
                        "count": "500"
                    },
                    "note_tweet": {
                        "note_tweet_results": {
                            "result": {}
                        }
                    }
                }
            }
        }
    }
    
    # Call the function
    post = download_x_post("123456789")
    
    # Assertions
    assert isinstance(post, Post)
    assert post.tweet_id == "123456789"
    assert post.username == "testuser"
    assert post.text == "This is a test tweet"
    assert post.view_count == "500"
    
    # Verify mocks were called correctly
    mock_token.assert_called_once()
    mock_fetch.assert_called_once()
    assert mock_save.call_count == 1
    mock_dir.assert_called_once()


@patch("xtract.api.client.get_guest_token")
def test_download_x_post_guest_token_error(mock_token):
    """Test error handling when getting guest token fails."""
    mock_token.side_effect = APIError("Failed to fetch guest token")
    
    post = download_x_post("123456789")
    
    assert post is None
    mock_token.assert_called_once()


@patch("xtract.api.client.get_guest_token")
@patch("xtract.api.client.fetch_tweet_data")
def test_download_x_post_fetch_error(mock_fetch, mock_token):
    """Test error handling when fetching tweet data fails."""
    mock_token.return_value = "mock_token"
    mock_fetch.side_effect = APIError("Failed to fetch tweet")
    
    post = download_x_post("123456789")
    
    assert post is None
    mock_token.assert_called_once()
    mock_fetch.assert_called_once()


@patch("xtract.api.client.ensure_directory")
@patch("xtract.api.client.save_json")
@patch("xtract.api.client.fetch_tweet_data")
def test_download_x_post_with_cookies(mock_fetch, mock_save, mock_dir):
    """Test download with cookies instead of guest token."""
    # Mock the data returned by the API
    mock_fetch.return_value = {
        "data": {
            "tweetResult": {
                "result": {
                    "rest_id": "123456789",
                    "legacy": {
                        "created_at": "Wed Feb 28 12:00:00 +0000 2024",
                        "full_text": "This is a test tweet",
                    },
                    "core": {
                        "user_results": {
                            "result": {
                                "legacy": {
                                    "screen_name": "testuser",
                                    "name": "Test User",
                                }
                            }
                        }
                    },
                    "views": {
                        "count": "500"
                    },
                    "note_tweet": {
                        "note_tweet_results": {
                            "result": {}
                        }
                    }
                }
            }
        }
    }
    
    # Call the function with cookies
    post = download_x_post("123456789", cookies="mock_cookies")
    
    # Assertions
    assert isinstance(post, Post)
    assert post.tweet_id == "123456789"
    
    # Verify the cookie was used in headers
    headers = mock_fetch.call_args[0][1]
    assert "Cookie" in headers
    assert headers["Cookie"] == "mock_cookies" 