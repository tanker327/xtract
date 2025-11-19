"""
Models for post data from X.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

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
    quoted_tweet_id: Optional[str] = None

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
        from xtract.utils.text import expand_urls

        logger.debug(f"Creating Post from API data for tweet ID: {tweet.get('rest_id', 'unknown')}")

        logger.debug("Extracting media URLs from extended entities")
        images, videos = extract_media_urls(legacy.get("extended_entities", {}).get("media", []))

        logger.debug("Creating UserDetails from user data")
        user_details = UserDetails.from_dict(user)

        logger.debug("Creating PostData from tweet and legacy data")
        post_data = PostData.from_dict(tweet, legacy)

        # Check for note tweet (longer form content)
        text = legacy.get("full_text", "")
        url_entities = legacy.get("entities", {}).get("urls", [])

        if note_tweet.get("text"):
            logger.debug("Using text from note_tweet (longer form content)")
            text = note_tweet.get("text", "")
            # Use URL entities from note_tweet entity_set if available
            note_urls = note_tweet.get("entity_set", {}).get("urls", [])
            if note_urls:
                logger.debug("Using URL entities from note_tweet entity_set")
                url_entities = note_urls

        # Expand t.co URLs to their original form
        try:
            if url_entities:
                logger.debug(f"Found {len(url_entities)} URL entities to expand")
                text = expand_urls(text, url_entities)
        except Exception as e:
            logger.warning(f"Failed to expand URLs for tweet {tweet.get('rest_id')}: {e}")

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

        # Handle quoted tweet if present - check multiple possible locations
        quoted = None
        quoted_tweet_id = None

        # Check in the tweet object (this is where it should be for most APIs)
        if "quoted_status_result" in tweet:
            quoted = tweet.get("quoted_status_result", {}).get("result", {})
        # Check in the legacy object as a fallback (older API responses may put it here)
        elif "quoted_status_result" in legacy:
            quoted = legacy.get("quoted_status_result", {}).get("result", {})

        # Also check for quotedRefResult (used for nested quotes with limited data)
        if quoted and "quotedRefResult" in quoted:
            nested_quoted = quoted.get("quotedRefResult", {}).get("result", {})
            # Store the nested quoted tweet ID from quotedRefResult
            if nested_quoted and "rest_id" in nested_quoted:
                logger.debug(
                    f"Found nested quoted tweet ID via quotedRefResult: {nested_quoted.get('rest_id')}"
                )

        # Extract quoted tweet ID from legacy if available
        if "quoted_status_id_str" in legacy:
            quoted_tweet_id = legacy.get("quoted_status_id_str")
            logger.debug(f"Found quoted_status_id_str in legacy: {quoted_tweet_id}")

        # Process quoted tweet if we have full data
        if quoted:
            # Check if we have full data (has legacy field) or just an ID
            if "legacy" in quoted:
                logger.debug(
                    f"Found quoted tweet with full data, ID: {quoted.get('rest_id', 'unknown')}"
                )
                quoted_legacy = quoted.get("legacy", {})
                quoted_user = (
                    quoted.get("core", {})
                    .get("user_results", {})
                    .get("result", {})
                    .get("legacy", {})
                )
                quoted_note = (
                    quoted.get("note_tweet", {}).get("note_tweet_results", {}).get("result", {})
                )
                post.quoted_tweet = cls.from_api_data(
                    quoted, quoted_legacy, quoted_user, quoted_note
                )
                # Store the quoted tweet ID (from the full data)
                post.quoted_tweet_id = quoted.get("rest_id")
            else:
                # Only have ID, no full data
                quoted_id = quoted.get("rest_id")
                if quoted_id:
                    logger.debug(f"Found quoted tweet with only ID: {quoted_id}")
                    post.quoted_tweet_id = quoted_id
        elif quoted_tweet_id:
            # Have ID from legacy but no quoted status result
            logger.debug(
                f"Have quoted tweet ID from legacy but no quoted status result: {quoted_tweet_id}"
            )
            post.quoted_tweet_id = quoted_tweet_id

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

        if self.quoted_tweet_id:
            result["quoted_tweet_id"] = self.quoted_tweet_id

        if self.quoted_tweet:
            logger.debug("Including quoted tweet in dictionary")
            result["quoted_tweet"] = self.quoted_tweet.to_dict()

        return result
