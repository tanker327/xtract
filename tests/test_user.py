import pytest
from xtract.models.user import UserDetails


def test_user_details_initialization():
    """Test UserDetails initialization with default values."""
    user = UserDetails()
    assert user.name == ""
    assert user.screen_name == ""
    assert user.description == ""
    assert user.followers_count == 0
    assert user.friends_count == 0
    assert user.location == ""
    assert user.created_at == ""
    assert user.profile_image_url == ""
    assert user.profile_banner_url == ""
    assert user.statuses_count == 0
    assert user.media_count == 0
    assert user.listed_count == 0
    assert user.is_verified is False
    assert user.is_blue_verified is False


def test_user_details_custom_initialization():
    """Test UserDetails initialization with custom values."""
    user = UserDetails(
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

    assert user.name == "Test User"
    assert user.screen_name == "testuser"
    assert user.description == "This is a test user"
    assert user.followers_count == 1000
    assert user.friends_count == 500
    assert user.location == "Test Location"
    assert user.created_at == "Wed Feb 28 12:00:00 +0000 2024"
    assert user.profile_image_url == "https://example.com/profile.jpg"
    assert user.profile_banner_url == "https://example.com/banner.jpg"
    assert user.statuses_count == 1500
    assert user.media_count == 100
    assert user.listed_count == 50
    assert user.is_verified is True
    assert user.is_blue_verified is True


def test_user_details_from_dict():
    """Test UserDetails creation from dictionary."""
    user_data = {
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

    user = UserDetails.from_dict(user_data)

    assert user.name == "Test User"
    assert user.screen_name == "testuser"
    assert user.description == "This is a test user"
    assert user.followers_count == 1000
    assert user.friends_count == 500
    assert user.location == "Test Location"
    assert user.created_at == "Wed Feb 28 12:00:00 +0000 2024"
    assert user.profile_image_url == "https://example.com/profile.jpg"
    assert user.profile_banner_url == "https://example.com/banner.jpg"
    assert user.statuses_count == 1500
    assert user.media_count == 100
    assert user.listed_count == 50
    assert user.is_verified is True
    assert user.is_blue_verified is True


def test_user_details_from_dict_missing_values():
    """Test UserDetails creation from dictionary with missing values."""
    user_data = {"name": "Test User", "screen_name": "testuser"}

    user = UserDetails.from_dict(user_data)

    assert user.name == "Test User"
    assert user.screen_name == "testuser"
    assert user.description == ""
    assert user.followers_count == 0
    assert user.friends_count == 0
    assert user.location == ""
    assert user.created_at == ""
    assert user.profile_image_url == ""
    assert user.profile_banner_url == ""
    assert user.statuses_count == 0
    assert user.media_count == 0
    assert user.listed_count == 0
    assert user.is_verified is False
    assert user.is_blue_verified is False
