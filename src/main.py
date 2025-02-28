import requests
import os
import json
from urllib.parse import urlparse
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass

# Constants (could be moved to a config file)
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
DEFAULT_HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": f"Bearer {BEARER_TOKEN}",
    "content-type": "application/json",
    "origin": "https://x.com",
    "referer": "https://x.com/",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "x-twitter-active-user": "yes",
    "x-twitter-client-language": "en"
}

class APIError(Exception):
    """Custom exception for API-related errors"""
    pass

def get_guest_token() -> Optional[str]:
    """Fetch a guest token from X's API."""
    url = "https://api.x.com/1.1/guest/activate.json"
    headers = DEFAULT_HEADERS.copy()
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json().get("guest_token")
    except requests.RequestException as e:
        raise APIError(f"Failed to fetch guest token: {e}")

def fetch_tweet_data(tweet_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Fetch tweet data using the GraphQL endpoint."""
    url = "https://api.x.com/graphql/_y7SZqeOFfgEivILXIy3tQ/TweetResultByRestId"
    params = {
        "variables": json.dumps({
            "tweetId": tweet_id,
            "withCommunity": False,
            "includePromotedContent": False,
            "withVoice": False
        }),
        "features": json.dumps({
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "premium_content_api_read_enabled": False,
            "communities_web_enable_tweet_community_results_fetch": True,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
            "responsive_web_grok_analyze_post_followups_enabled": False,
            "responsive_web_jetfuel_frame": False,
            "responsive_web_grok_share_attachment_enabled": True,
            "articles_preview_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "responsive_web_grok_analysis_button_from_backend": True,
            "creator_subscriptions_quote_tweet_preview_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "rweb_video_timestamps_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "rweb_tipjar_consumption_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "responsive_web_grok_image_annotation_enabled": False,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_enhance_cards_enabled": False
        }),
        "fieldToggles": json.dumps({
            "withArticleRichContentState": True,
            "withArticlePlainText": False,
            "withGrokAnalyze": False,
            "withDisallowedReplyControls": False
        })
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise APIError(f"Failed to fetch tweet {tweet_id}: {e}")

def extract_media_urls(media: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """Extract images and videos from tweet media data."""
    images, videos = [], []
    for item in media or []:
        if item.get("type") == "photo":
            if url := item.get("media_url_https"):
                images.append(url)
        elif item.get("type") == "video":
            variants = item.get("video_info", {}).get("variants", [])
            if best_variant := max(variants, key=lambda x: x.get("bitrate", 0), default={}):
                if url := best_variant.get("url"):
                    videos.append(url)
    return images, videos

def save_json(data: Any, filepath: str) -> None:
    """Utility to save data as JSON with consistent formatting."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

@dataclass
class UserDetails:
    """Class to represent user information."""
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

@dataclass
class PostData:
    """Class to represent post metadata and analysis."""
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
        """Convert Post instance to dictionary for JSON serialization."""
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

def download_x_post(tweet_id: str, output_dir: str = "x_post_downloads",
                   cookies: Optional[str] = None, save_raw_response: bool = True) -> Optional[Post]:
    """Download X post content and return a Post object."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    post_dir = os.path.join(output_dir, f"tweet_{tweet_id}_{timestamp}")
    os.makedirs(post_dir, exist_ok=True)

    headers = DEFAULT_HEADERS.copy()
    if not cookies:
        try:
            headers["x-guest-token"] = get_guest_token()
            print(f"Using guest token: {headers['x-guest-token']}")
        except APIError as e:
            print(e)
            return None
    else:
        headers["Cookie"] = cookies
        print("Using provided cookies")

    print(f"Fetching data for tweet ID: {tweet_id}")
    try:
        data = fetch_tweet_data(tweet_id, headers)
    except APIError as e:
        print(e)
        return None

    if save_raw_response:
        raw_file = os.path.join(post_dir, "raw_response.json")
        save_json(data, raw_file)
        print(f"Raw response saved to: {raw_file}")

    tweet = data.get("data", {}).get("tweetResult", {}).get("result", {})
    legacy = tweet.get("legacy", {})
    user = tweet.get("core", {}).get("user_results", {}).get("result", {}).get("legacy", {})
    note_tweet = tweet.get("note_tweet", {}).get("note_tweet_results", {}).get("result", {})

    post = Post.from_api_data(tweet, legacy, user, note_tweet)
    json_file = os.path.join(post_dir, "tweet.json")
    save_json(post.to_dict(), json_file)
    print(f"Structured JSON saved to: {json_file}")
    return post

def main():
    cookies = ""  # Optional: Add cookies here if needed
    save_raw = True
    tweet_id = input("Enter the X post ID (e.g., 1892413385804792307): ").strip()
    if not tweet_id.isdigit():
        print("Please enter a valid numeric tweet ID.")
        return

    print(f"Downloading content for tweet ID: {tweet_id}")
    post = download_x_post(tweet_id, cookies=cookies if cookies else None, save_raw_response=save_raw)
    if post:
        print("Resulting JSON:")
        print(json.dumps(post.to_dict(), indent=2))

if __name__ == "__main__":
    main()