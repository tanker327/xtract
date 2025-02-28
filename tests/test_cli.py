import pytest
from unittest.mock import patch, MagicMock
import tempfile
import os
import sys

# Add a path to find the CLI module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from xtract.cli import main


@pytest.fixture
def mock_post():
    """Create a mock Post object."""
    post = MagicMock()
    post.tweet_id = "123456789"
    post.username = "testuser"
    post.text = "This is a test post"
    post.created_at = "Wed Feb 28 12:00:00 +0000 2024"
    post.view_count = "500"
    post.images = ["https://example.com/image.jpg"]
    post.videos = []

    post.user_details.name = "Test User"
    post.user_details.followers_count = 1000

    post.post_data.favorite_count = 50
    post.post_data.retweet_count = 20

    post.quoted_tweet = None

    # Configure to_dict to return a real dictionary
    post.to_dict.return_value = {
        "tweet_id": "123456789",
        "username": "testuser",
        "created_at": "Wed Feb 28 12:00:00 +0000 2024",
        "text": "This is a test post",
        "view_count": "500",
        "images": ["https://example.com/image.jpg"],
        "videos": [],
        "user_details": {"name": "Test User", "followers_count": 1000},
        "post_data": {"favorite_count": 50, "retweet_count": 20},
    }

    return post


@patch("xtract.cli.download_x_post")
@patch("xtract.cli.argparse.ArgumentParser.parse_args")
def test_cli_basic(mock_args, mock_download, mock_post):
    """Test CLI with basic usage."""
    # Setup mock arguments
    mock_args.return_value.tweet_id = "123456789"
    mock_args.return_value.output_dir = "x_post_downloads"  # Default value from CLI
    mock_args.return_value.cookies = None
    mock_args.return_value.save_raw = False
    mock_args.return_value.pretty = False
    mock_args.return_value.markdown = False  # Add the new markdown option

    # Setup mock download function
    mock_download.return_value = mock_post

    # Run the CLI
    with patch("sys.stdout"):  # Suppress output
        main()

    # Verify the download function was called with the correct parameters
    mock_download.assert_called_once_with(
        "123456789", output_dir="x_post_downloads", cookies=None, save_raw_response_to_file=False
    )


@patch("xtract.cli.download_x_post")
@patch("xtract.cli.argparse.ArgumentParser.parse_args")
def test_cli_custom_output_dir(mock_args, mock_download, mock_post):
    """Test CLI with custom output directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup mock arguments
        mock_args.return_value.tweet_id = "123456789"
        mock_args.return_value.output_dir = temp_dir
        mock_args.return_value.cookies = None
        mock_args.return_value.save_raw = False
        mock_args.return_value.pretty = False
        mock_args.return_value.markdown = False  # Add the new markdown option

        # Setup mock download function
        mock_download.return_value = mock_post

        # Run the CLI
        with patch("sys.stdout"):  # Suppress output
            main()

        # Verify the download function was called with the correct output dir
        mock_download.assert_called_once_with(
            "123456789", output_dir=temp_dir, cookies=None, save_raw_response_to_file=False
        )


@patch("xtract.cli.download_x_post")
@patch("xtract.cli.argparse.ArgumentParser.parse_args")
def test_cli_with_cookies(mock_args, mock_download, mock_post):
    """Test CLI with cookies provided."""
    # Setup mock arguments
    mock_args.return_value.tweet_id = "123456789"
    mock_args.return_value.output_dir = "x_post_downloads"  # Default value from CLI
    mock_args.return_value.cookies = "auth_token=abc; ct0=123"
    mock_args.return_value.save_raw = False
    mock_args.return_value.pretty = False
    mock_args.return_value.markdown = False  # Add the new markdown option

    # Setup mock download function
    mock_download.return_value = mock_post

    # Run the CLI
    with patch("sys.stdout"):  # Suppress output
        main()

    # Verify the download function was called with the cookies
    mock_download.assert_called_once_with(
        "123456789",
        output_dir="x_post_downloads",
        cookies="auth_token=abc; ct0=123",
        save_raw_response_to_file=False,
    )


@patch("xtract.cli.download_x_post")
@patch("xtract.cli.argparse.ArgumentParser.parse_args")
def test_cli_download_failure(mock_args, mock_download):
    """Test CLI behavior when download fails."""
    # Setup mock arguments
    mock_args.return_value.tweet_id = "123456789"
    mock_args.return_value.output_dir = "x_post_downloads"  # Default value from CLI
    mock_args.return_value.cookies = None
    mock_args.return_value.save_raw = False
    mock_args.return_value.pretty = False
    mock_args.return_value.markdown = False  # Add the new markdown option

    # Setup mock download function to return None (failure)
    mock_download.return_value = None

    # Run the CLI and check for non-zero exit code
    with patch("sys.stdout"):  # Suppress output
        with patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)


@patch("xtract.cli.download_x_post")
@patch("xtract.cli.argparse.ArgumentParser.parse_args")
def test_cli_save_raw_response_to_file(mock_args, mock_download, mock_post):
    """Test CLI with raw response saving enabled."""
    # Setup mock arguments
    mock_args.return_value.tweet_id = "123456789"
    mock_args.return_value.output_dir = "x_post_downloads"  # Default value from CLI
    mock_args.return_value.cookies = None
    mock_args.return_value.save_raw = True
    mock_args.return_value.pretty = False
    mock_args.return_value.markdown = False  # Add the new markdown option

    # Setup mock download function
    mock_download.return_value = mock_post

    # Run the CLI
    with patch("sys.stdout"):  # Suppress output
        main()

    # Verify the download function was called with save_raw_response_to_file=True
    mock_download.assert_called_once_with(
        "123456789", output_dir="x_post_downloads", cookies=None, save_raw_response_to_file=True
    )


@patch("xtract.cli.download_x_post")
@patch("xtract.cli.argparse.ArgumentParser.parse_args")
@patch("xtract.cli.save_post_as_markdown")
def test_cli_with_markdown(mock_save_markdown, mock_args, mock_download, mock_post):
    """Test CLI with Markdown generation enabled."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup mock arguments
        mock_args.return_value.tweet_id = "123456789"
        mock_args.return_value.output_dir = temp_dir
        mock_args.return_value.cookies = None
        mock_args.return_value.save_raw = False
        mock_args.return_value.pretty = False
        mock_args.return_value.markdown = True

        # Setup mock download function
        mock_download.return_value = mock_post
        
        # Setup mock save_post_as_markdown function
        mock_save_markdown.return_value = os.path.join(temp_dir, "x_post_123456789", "tweet_123456789.md")

        # Run the CLI
        with patch("sys.stdout"):  # Suppress output
            main()

        # Verify the download function was called with correct parameters
        mock_download.assert_called_once_with(
            "123456789", output_dir=temp_dir, cookies=None, save_raw_response_to_file=False
        )
        
        # Verify the save_post_as_markdown function was called with correct parameters
        expected_tweet_dir = os.path.join(temp_dir, "x_post_123456789")
        mock_save_markdown.assert_called_once_with(mock_post, output_dir=expected_tweet_dir)
