import os
import pytest
import tempfile
import json
from unittest.mock import patch, mock_open

from xtract.utils.file import ensure_directory, save_json
from xtract.utils.media import extract_media_urls


def test_ensure_directory_new():
    """Test creating a new directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        new_dir = os.path.join(temp_dir, "new_dir")
        
        # Directory shouldn't exist yet
        assert not os.path.exists(new_dir)
        
        # Create the directory
        ensure_directory(new_dir)
        
        # Directory should now exist
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)


def test_ensure_directory_existing():
    """Test ensuring an existing directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Directory already exists
        assert os.path.exists(temp_dir)
        
        # Should not raise an error
        ensure_directory(temp_dir)
        
        # Directory should still exist
        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)


@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_save_json(mock_json_dump, mock_file):
    """Test saving JSON data to a file."""
    data = {"key": "value", "nested": {"sub": "data"}}
    filepath = "/tmp/test.json"
    
    save_json(data, filepath)
    
    mock_file.assert_called_once_with(filepath, 'w', encoding='utf-8')
    mock_json_dump.assert_called_once()
    # Check that the first positional argument to json.dump is the data
    assert mock_json_dump.call_args[0][0] == data
    # Check that the indent parameter is set for pretty printing
    assert mock_json_dump.call_args[1].get('indent') == 2


def test_extract_media_urls_no_media():
    """Test extracting media URLs with no media."""
    media = []
    images, videos = extract_media_urls(media)
    
    assert images == []
    assert videos == []


def test_extract_media_urls_images_only():
    """Test extracting media URLs with only images."""
    media = [
        {
            "type": "photo",
            "media_url_https": "https://example.com/image1.jpg"
        },
        {
            "type": "photo",
            "media_url_https": "https://example.com/image2.jpg"
        }
    ]
    
    images, videos = extract_media_urls(media)
    
    assert len(images) == 2
    assert "https://example.com/image1.jpg" in images
    assert "https://example.com/image2.jpg" in images
    assert videos == []


def test_extract_media_urls_videos_only():
    """Test extracting media URLs with only videos."""
    media = [
        {
            "type": "video",
            "video_info": {
                "variants": [
                    {
                        "content_type": "video/mp4",
                        "url": "https://example.com/video1_low.mp4",
                        "bitrate": 256000
                    },
                    {
                        "content_type": "video/mp4",
                        "url": "https://example.com/video1_high.mp4",
                        "bitrate": 832000
                    }
                ]
            }
        }
    ]
    
    images, videos = extract_media_urls(media)
    
    assert images == []
    assert len(videos) == 1
    # Should choose the highest bitrate
    assert videos[0] == "https://example.com/video1_high.mp4"


def test_extract_media_urls_mixed_media():
    """Test extracting media URLs with mixed media types."""
    media = [
        {
            "type": "photo",
            "media_url_https": "https://example.com/image1.jpg"
        },
        {
            "type": "video",
            "video_info": {
                "variants": [
                    {
                        "content_type": "video/mp4",
                        "url": "https://example.com/video1.mp4",
                        "bitrate": 832000
                    }
                ]
            }
        },
        {
            "type": "animated_gif",
            "video_info": {
                "variants": [
                    {
                        "url": "https://example.com/gif1.mp4"
                    }
                ]
            }
        }
    ]
    
    images, videos = extract_media_urls(media)
    
    assert len(images) == 1
    assert images[0] == "https://example.com/image1.jpg"
    assert len(videos) == 2
    assert "https://example.com/video1.mp4" in videos
    assert "https://example.com/gif1.mp4" in videos


def test_extract_media_urls_unsupported_type():
    """Test extracting media URLs with unsupported media types."""
    media = [
        {
            "type": "unsupported",
            "media_url_https": "https://example.com/unsupported.xyz"
        }
    ]
    
    images, videos = extract_media_urls(media)
    
    assert images == []
    assert videos == [] 