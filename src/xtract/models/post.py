"""
Models for post data from X.
"""

from dataclasses import dataclass
import logging
from typing import Dict, List, Any, Optional, Tuple

from xtract.config.logging import get_logger
from xtract.models.user import UserDetails

# Get a logger for this module
logger = get_logger(__name__)

@dataclass
class PostData:
    """Class to represent post metadata and analytics."""

    favorite_count: int = 0
    retweet_count: int = 0
    reply_count: int = 0
    quote_count: int = 0
    bookmark_count: int = 0
    is_quote_status: bool = False
    lang: str = ""
    source: str = ""
    possibly_sensitive: bool = False
    conversation_id: str = ""
    is_translatable: bool = False
    grok_analysis_button: bool = False

    @classmethod
    def from_dict(cls, tweet: Dict[str, Any], legacy: Dict[str, Any]) -> "PostData":
        """
        Create a PostData instance from tweet and legacy data.

        Args:
            tweet: Tweet data from the API
            legacy: Legacy data from the API

        Returns:
            PostData: Populated instance
        """
        logger.debug("Creating PostData from API response")
        return cls(
            favorite_count=legacy.get("favorite_count", 0),
            retweet_count=legacy.get("retweet_count", 0),
            reply_count=legacy.get("reply_count", 0),
            quote_count=legacy.get("quote_count", 0),
            bookmark_count=legacy.get("bookmark_count", 0),
            is_quote_status=legacy.get("is_quote_status", False),
            lang=legacy.get("lang", ""),
            source=tweet.get("source", ""),
            possibly_sensitive=legacy.get("possibly_sensitive", False),
            conversation_id=legacy.get("conversation_id_str", ""),
            is_translatable=tweet.get("is_translatable", False),
            grok_analysis_button=tweet.get("grok_analysis_button", False),
        )


@dataclass
class Post:
    """Class to represent an X post, including optional quoted post."""

    tweet_id: str
    username: str
    created_at: str
    text: str
    view_count: str
    images: List[str]
    videos: List[str]
    user_details: UserDetails
    post_data: PostData
    quoted_tweet: Optional["Post"] = None

    @classmethod
    def from_api_data(
        cls,
        tweet: Dict[str, Any],
        legacy: Dict[str, Any],
        user: Dict[str, Any],
        note_tweet: Dict[str, Any],
    ) -> "Post":
        """
        Create a Post instance from API data.

        Args:
            tweet: Tweet data from the API
            legacy: Legacy data from the API
            user: User data from the API
            note_tweet: Note tweet data from the API

        Returns:
            Post: Populated instance
        """
        from xtract.utils.media import extract_media_urls

        logger.debug(f"Creating Post from API data for tweet ID: {tweet.get('rest_id', 'unknown')}")
        
        logger.debug("Extracting media URLs from extended entities")
        images, videos = extract_media_urls(legacy.get("extended_entities", {}).get("media", []))
        
        logger.debug("Creating UserDetails from user data")
        user_details = UserDetails.from_dict(user)
        
        logger.debug("Creating PostData from tweet and legacy data")
        post_data = PostData.from_dict(tweet, legacy)
        
        # Check for note tweet (longer form content)
        text = legacy.get("full_text", "")
        if note_tweet.get("text"):
            logger.debug("Using text from note_tweet (longer form content)")
            text = note_tweet.get("text", "")
            
        post = cls(
            tweet_id=tweet.get("rest_id", ""),
            username=user.get("screen_name", ""),
            created_at=legacy.get("created_at", ""),
            text=text,
            view_count=tweet.get("views", {}).get("count", "0"),
            images=images,
            videos=videos,
            user_details=user_details,
            post_data=post_data,
        )

        # Handle quoted tweet if present - check both possible locations
        quoted = None
        # Check in the tweet object (this is where it should be for most APIs)
        if "quoted_status_result" in tweet:
            quoted = tweet.get("quoted_status_result", {}).get("result", {})
        # Check in the legacy object as a fallback (older API responses may put it here)
        elif "quoted_status_result" in legacy:
            quoted = legacy.get("quoted_status_result", {}).get("result", {})
            
        if quoted:
            logger.debug(f"Found quoted tweet with ID: {quoted.get('rest_id', 'unknown')}")
            quoted_legacy = quoted.get("legacy", {})
            quoted_user = (
                quoted.get("core", {})
                .get("user_results", {})
                .get("result", {})
                .get("legacy", {})
            )
            quoted_note = (
                quoted.get("note_tweet", {})
                .get("note_tweet_results", {})
                .get("result", {})
            )
            post.quoted_tweet = cls.from_api_data(
                quoted, quoted_legacy, quoted_user, quoted_note
            )
        
        logger.debug(f"Successfully created Post object for tweet ID: {post.tweet_id}")
        return post

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Post to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the Post
        """
        logger.debug(f"Converting Post to dictionary for tweet ID: {self.tweet_id}")
        result = {
            "tweet_id": self.tweet_id,
            "username": self.username,
            "created_at": self.created_at,
            "text": self.text,
            "view_count": self.view_count,
            "images": self.images,
            "videos": self.videos,
            "user_details": self.user_details.__dict__,
            "post_data": self.post_data.__dict__,
        }

        if self.quoted_tweet:
            logger.debug("Including quoted tweet in dictionary")
            result["quoted_tweet"] = self.quoted_tweet.to_dict()

        return result
