"""
Models for post data from X.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple

from xtract.models.user import UserDetails


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
    def from_dict(cls, tweet: Dict[str, Any], legacy: Dict[str, Any]) -> 'PostData':
        """
        Create a PostData instance from tweet and legacy data.
        
        Args:
            tweet: Tweet data from the API
            legacy: Legacy data from the API
            
        Returns:
            PostData: Populated instance
        """
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
            grok_analysis_button=tweet.get("grok_analysis_button", False)
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
    quoted_tweet: Optional['Post'] = None

    @classmethod
    def from_api_data(cls, tweet: Dict[str, Any], legacy: Dict[str, Any], user: Dict[str, Any],
                     note_tweet: Dict[str, Any]) -> 'Post':
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
        
        images, videos = extract_media_urls(legacy.get("extended_entities", {}).get("media", []))
        post = cls(
            tweet_id=tweet.get("rest_id", ""),
            username=user.get("screen_name", ""),
            created_at=legacy.get("created_at", ""),
            text=note_tweet.get("text", legacy.get("full_text", "")),
            view_count=tweet.get("views", {}).get("count", "0"),
            images=images,
            videos=videos,
            user_details=UserDetails.from_dict(user),
            post_data=PostData.from_dict(tweet, legacy)
        )

        # Handle quoted tweet
        quoted_status = tweet.get("quoted_status_result", {}).get("result", {})
        if quoted_status and quoted_status.get("__typename") == "Tweet":
            quoted_legacy = quoted_status.get("legacy", {})
            quoted_user = quoted_status.get("core", {}).get("user_results", {}).get("result", {}).get("legacy", {})
            quoted_note_tweet = quoted_status.get("note_tweet", {}).get("note_tweet_results", {}).get("result", {})
            post.quoted_tweet = cls.from_api_data(quoted_status, quoted_legacy, quoted_user, quoted_note_tweet)

        return post

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Post instance to dictionary for JSON serialization.
        
        Returns:
            dict: Dictionary representation of the Post
        """
        result = {
            "tweet_id": self.tweet_id,
            "username": self.username,
            "created_at": self.created_at,
            "text": self.text,
            "view_count": self.view_count,
            "images": self.images,
            "videos": self.videos,
            "user_details": vars(self.user_details),
            "post_data": vars(self.post_data)
        }
        if self.quoted_tweet:
            result["quoted_tweet"] = self.quoted_tweet.to_dict()
        return result 