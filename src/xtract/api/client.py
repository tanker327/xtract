"""
Client for interacting with X's API.
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from xtract.api.errors import APIError
from xtract.config.constants import (
    DEFAULT_HEADERS,
    GUEST_TOKEN_URL,
    TWEET_DATA_URL,
    DEFAULT_FEATURES,
    DEFAULT_FIELD_TOGGLES,
    DEFAULT_OUTPUT_DIR,
)
from xtract.models.post import Post
from xtract.utils.file import save_json, ensure_directory


def get_guest_token() -> Optional[str]:
    """
    Fetch a guest token from X's API.

    Returns:
        str: Guest token if successful, None otherwise

    Raises:
        APIError: If the API request fails
    """
    headers = DEFAULT_HEADERS.copy()
    try:
        response = requests.post(GUEST_TOKEN_URL, headers=headers)
        response.raise_for_status()
        return response.json().get("guest_token")
    except requests.RequestException as e:
        raise APIError(f"Failed to fetch guest token: {e}")


def fetch_tweet_data(tweet_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Fetch tweet data using the GraphQL endpoint.

    Args:
        tweet_id: ID of the tweet to fetch
        headers: Headers for the API request

    Returns:
        Dict[str, Any]: Tweet data from the API

    Raises:
        APIError: If the API request fails
    """
    params = {
        "variables": json.dumps(
            {
                "tweetId": tweet_id,
                "withCommunity": False,
                "includePromotedContent": False,
                "withVoice": False,
            }
        ),
        "features": json.dumps(DEFAULT_FEATURES),
        "fieldToggles": json.dumps(DEFAULT_FIELD_TOGGLES),
    }
    try:
        response = requests.get(TWEET_DATA_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise APIError(f"Failed to fetch tweet {tweet_id}: {e}")


def download_x_post(
    post_identifier: str,
    output_dir: str = None,
    cookies: str = None,
    save_raw_response: bool = False,
) -> Optional[Post]:
    """
    Download an X (Twitter) post by its ID or URL.

    Args:
        post_identifier: Either a tweet ID or a URL containing the tweet ID
                        (e.g. "1234567890" or "https://x.com/username/status/1234567890")
        output_dir: Directory to save the tweet data (default: current directory)
        cookies: Cookies to use for authentication (optional)
        save_raw_response: Whether to save the raw API response (default: False)

    Returns:
        Post object if successful, None otherwise
    """
    # Extract tweet ID from URL if a URL is provided
    tweet_id = post_identifier
    if "/" in post_identifier and "status" in post_identifier:
        # Extract ID from URL like "https://x.com/username/status/1234567890"
        tweet_id = post_identifier.split("status/")[1].split("/")[0].split("?")[0]
        # Remove any non-numeric characters (in case of trailing text)
        tweet_id = "".join(c for c in tweet_id if c.isdigit())

    # Ensure output directory exists
    if output_dir is None:
        output_dir = os.getcwd()

    tweet_dir = os.path.join(output_dir, f"x_post_{tweet_id}")
    ensure_directory(tweet_dir)

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
        raw_file = os.path.join(tweet_dir, "raw_response.json")
        save_json(data, raw_file)
        print(f"Raw response saved to: {raw_file}")

    tweet = data.get("data", {}).get("tweetResult", {}).get("result", {})
    legacy = tweet.get("legacy", {})
    user = tweet.get("core", {}).get("user_results", {}).get("result", {}).get("legacy", {})
    note_tweet = tweet.get("note_tweet", {}).get("note_tweet_results", {}).get("result", {})

    post = Post.from_api_data(tweet, legacy, user, note_tweet)
    json_file = os.path.join(tweet_dir, "tweet.json")
    save_json(post.to_dict(), json_file)
    print(f"Structured JSON saved to: {json_file}")
    return post
