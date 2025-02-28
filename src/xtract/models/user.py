"""
Models for user data from X posts.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class UserDetails:
    """Class to represent user information from X."""
    name: str = ""
    screen_name: str = ""
    description: str = ""
    followers_count: int = 0
    friends_count: int = 0
    location: str = ""
    created_at: str = ""
    profile_image_url: str = ""
    profile_banner_url: str = ""
    statuses_count: int = 0
    media_count: int = 0
    listed_count: int = 0
    is_verified: bool = False
    is_blue_verified: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserDetails':
        """
        Create a UserDetails instance from a dictionary.
        
        Args:
            data: Dictionary containing user data from the API
            
        Returns:
            UserDetails: Populated instance
        """
        return cls(
            name=data.get("name", ""),
            screen_name=data.get("screen_name", ""),
            description=data.get("description", ""),
            followers_count=data.get("followers_count", 0),
            friends_count=data.get("friends_count", 0),
            location=data.get("location", ""),
            created_at=data.get("created_at", ""),
            profile_image_url=data.get("profile_image_url_https", ""),
            profile_banner_url=data.get("profile_banner_url", ""),
            statuses_count=data.get("statuses_count", 0),
            media_count=data.get("media_count", 0),
            listed_count=data.get("listed_count", 0),
            is_verified=data.get("verified", False),
            is_blue_verified=data.get("is_blue_verified", False)
        ) 