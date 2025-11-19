"""
Client for interacting with X's API.
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any

from xtract.api.errors import APIError, TokenExpiredError
from xtract.config.constants import (
    DEFAULT_HEADERS,
    GUEST_TOKEN_URL,
    TWEET_DATA_URL,
    DEFAULT_FEATURES,
    DEFAULT_FIELD_TOGGLES,
)
from xtract.config.logging import get_logger
from xtract.models.post import Post
from xtract.utils.file import save_json, ensure_directory

# Get a logger for this module
logger = get_logger(__name__)


def get_guest_token(
    token_cache_dir: str = "/tmp/xtract/",
    token_cache_filename: str = "guest_token.json",
    force_refresh: bool = False,
) -> Optional[str]:
    """
    Fetch a guest token from X's API or retrieve from cache.

    Args:
        token_cache_dir: Directory to cache the guest token (default: "/tmp/xtract/")
        token_cache_filename: Filename for the token cache (default: "guest_token.json")
        force_refresh: If True, ignores cached token and fetches a new one (default: False)

    Returns:
        str: Guest token if successful, None otherwise

    Raises:
        APIError: If the API request fails
    """
    # Ensure cache directory exists
    ensure_directory(token_cache_dir)
    token_file_path = os.path.join(token_cache_dir, token_cache_filename)

    # Check if cached token exists and we're not forcing a refresh
    if not force_refresh and os.path.exists(token_file_path):
        try:
            with open(token_file_path, "r") as f:
                token_data = json.load(f)
                token = token_data.get("token")
                logger.info("Retrieved guest token from cache. Token: %s", token)
                return token
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to read cached token: {e}")
            # Continue to fetch a new token
    elif force_refresh:
        logger.info("Forcing token refresh, fetching new token")

    # Fetch new token
    headers = DEFAULT_HEADERS.copy()
    logger.debug("Requesting guest token from X API")
    try:
        response = requests.post(GUEST_TOKEN_URL, headers=headers)
        response.raise_for_status()
        token = response.json().get("guest_token")
        logger.info("Successfully obtained guest token. Token: %s", token)

        # Save token to cache
        try:
            with open(token_file_path, "w") as f:
                json.dump({"token": token, "timestamp": datetime.now().isoformat()}, f)
            logger.debug(f"Saved guest token to cache: {token_file_path}")
        except IOError as e:
            logger.warning(f"Failed to cache token: {e}")

        return token
    except requests.RequestException as e:
        logger.error(f"Failed to fetch guest token: {e}")
        raise APIError(f"Failed to fetch guest token: {e}")


def invalidate_guest_token(
    token_cache_dir: str = "/tmp/xtract/", token_cache_filename: str = "guest_token.json"
) -> None:
    """
    Invalidate (delete) a cached guest token.

    Args:
        token_cache_dir: Directory where the token is cached (default: "/tmp/xtract/")
        token_cache_filename: Filename for the token cache (default: "guest_token.json")
    """
    token_file_path = os.path.join(token_cache_dir, token_cache_filename)
    if os.path.exists(token_file_path):
        try:
            os.remove(token_file_path)
            logger.info(f"Invalidated guest token at: {token_file_path}")
        except OSError as e:
            logger.warning(f"Failed to invalidate token file: {e}")


def fetch_tweet_data(tweet_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Fetch tweet data using the GraphQL endpoint.

    Args:
        tweet_id: ID of the tweet to fetch
        headers: Headers for the API request

    Returns:
        Dict[str, Any]: Tweet data from the API

    Raises:
        TokenExpiredError: If the API returns a 403 error (typically means token expired)
        APIError: If the API request fails for other reasons
    """
    logger.debug(f"Preparing to fetch data for tweet ID: {tweet_id}")
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
        logger.debug(f"Sending request to {TWEET_DATA_URL}")
        response = requests.get(TWEET_DATA_URL, headers=headers, params=params)

        # Check specifically for 403 errors which typically indicate token expiration
        if response.status_code == 403:
            error_msg = (
                f"Token expired or invalid (403 Forbidden) for tweet {tweet_id}: {response.text}"
            )
            logger.warning(error_msg)
            raise TokenExpiredError(error_msg)

        response.raise_for_status()
        logger.debug(f"Successfully received response for tweet ID: {tweet_id}")
        return response.json()
    except requests.HTTPError as e:
        logger.error(f"HTTP error fetching tweet {tweet_id}: {e}")
        raise APIError(f"HTTP error fetching tweet {tweet_id}: {e}")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch tweet {tweet_id}: {e}")
        raise APIError(f"Failed to fetch tweet {tweet_id}: {e}")


def fetch_quoted_tweets_recursively(
    post: Post,
    headers: Dict[str, str],
    token_cache_dir: str = "/tmp/xtract/",
    token_cache_filename: str = "guest_token.json",
    max_retries: int = 3,
    max_depth: int = 5,
    current_depth: int = 0,
) -> Post:
    """
    Recursively fetch quoted tweets that only have IDs (no full data).

    Args:
        post: Post object that may have incomplete quoted tweets
        headers: Headers for API requests
        token_cache_dir: Directory to cache the guest token
        token_cache_filename: Filename for the token cache
        max_retries: Maximum number of retries for token expiration
        max_depth: Maximum depth to recursively fetch (default: 5)
        current_depth: Current recursion depth (default: 0)

    Returns:
        Post: Updated Post object with complete quoted tweet chain
    """
    # Check if we've reached max depth
    if current_depth >= max_depth:
        logger.info(f"Reached maximum recursion depth ({max_depth}), stopping recursive fetch")
        return post

    # Check if post has a quoted tweet ID but no quoted tweet data
    if post.quoted_tweet_id and not post.quoted_tweet:
        logger.info(
            f"Fetching missing quoted tweet data for ID: {post.quoted_tweet_id} (depth: {current_depth + 1}/{max_depth})"
        )

        # Try to fetch the quoted tweet with retry logic
        retries = 0
        force_refresh = False

        while retries < max_retries:
            try:
                # Update headers with guest token if needed
                if "x-guest-token" not in headers or force_refresh:
                    try:
                        headers["x-guest-token"] = get_guest_token(
                            token_cache_dir, token_cache_filename, force_refresh
                        )
                        logger.debug(
                            f"Using guest token for recursive fetch: {headers['x-guest-token']}"
                        )
                    except APIError as e:
                        logger.error(f"Failed to get guest token for recursive fetch: {e}")
                        break

                # Fetch the quoted tweet data
                data = fetch_tweet_data(post.quoted_tweet_id, headers)

                # Parse the response
                tweet = data.get("data", {}).get("tweetResult", {}).get("result", {})
                legacy = tweet.get("legacy", {})
                user = (
                    tweet.get("core", {})
                    .get("user_results", {})
                    .get("result", {})
                    .get("legacy", {})
                )
                note_tweet = (
                    tweet.get("note_tweet", {}).get("note_tweet_results", {}).get("result", {})
                )

                # Create Post object for the quoted tweet
                post.quoted_tweet = Post.from_api_data(tweet, legacy, user, note_tweet)
                logger.info(f"Successfully fetched quoted tweet: {post.quoted_tweet_id}")

                # Recursively fetch any quoted tweets in this quoted tweet
                post.quoted_tweet = fetch_quoted_tweets_recursively(
                    post.quoted_tweet,
                    headers,
                    token_cache_dir,
                    token_cache_filename,
                    max_retries,
                    max_depth,
                    current_depth + 1,
                )
                break

            except TokenExpiredError:
                retries += 1
                if retries >= max_retries:
                    logger.warning(
                        f"Failed to fetch quoted tweet {post.quoted_tweet_id} after {max_retries} retries (token expiration)"
                    )
                    break
                logger.warning(
                    f"Token expired while fetching quoted tweet, retrying ({retries}/{max_retries})"
                )
                invalidate_guest_token(token_cache_dir, token_cache_filename)
                force_refresh = True
                continue

            except APIError as e:
                logger.warning(f"Failed to fetch quoted tweet {post.quoted_tweet_id}: {e}")
                break

    # If post already has a quoted tweet, recursively process it
    elif post.quoted_tweet:
        logger.debug(f"Processing existing quoted tweet at depth {current_depth}")
        post.quoted_tweet = fetch_quoted_tweets_recursively(
            post.quoted_tweet,
            headers,
            token_cache_dir,
            token_cache_filename,
            max_retries,
            max_depth,
            current_depth + 1,
        )

    return post


def download_x_post(
    post_identifier: str,
    output_dir: str = None,
    cookies: str = None,
    save_raw_response_to_file: bool = False,
    fetch_quoted_tweets: bool = True,
    token_cache_dir: str = "/tmp/xtract/",
    token_cache_filename: str = "guest_token.json",
    max_retries: int = 3,
) -> Optional[Post]:
    """
    Download an X (Twitter) post by its ID or URL.

    Args:
        post_identifier: Either a tweet ID or a URL containing the tweet ID
                        (e.g. "1234567890" or "https://x.com/username/status/1234567890")
        output_dir: Directory to save the tweet data (default: current directory)
        cookies: Cookies to use for authentication (optional)
        save_raw_response_to_file: Whether to save the data to files (default: False)
        fetch_quoted_tweets: Whether to recursively fetch quoted tweets (default: True)
        token_cache_dir: Directory to cache the guest token (default: "/tmp/xtract/")
        token_cache_filename: Filename for the token cache (default: "guest_token.json")
        max_retries: Maximum number of retries for token expiration (default: 3)

    Returns:
        Post object if successful, None otherwise
    """
    logger.info(f"Processing post identifier: {post_identifier}")

    # Extract tweet ID from URL if a URL is provided
    tweet_id = post_identifier
    if "/" in post_identifier and "status" in post_identifier:
        # Extract ID from URL like "https://x.com/username/status/1234567890"
        tweet_id = post_identifier.split("status/")[1].split("/")[0].split("?")[0]
        # Remove any non-numeric characters (in case of trailing text)
        tweet_id = "".join(c for c in tweet_id if c.isdigit())
        logger.info(f"Extracted tweet ID '{tweet_id}' from URL")

    # Only setup directory if we're saving files
    tweet_dir = None
    if save_raw_response_to_file:
        # Ensure output directory exists
        if output_dir is None:
            output_dir = os.getcwd()
            logger.debug(f"No output directory specified, using current directory: {output_dir}")
        else:
            logger.debug(f"Using specified output directory: {output_dir}")

        tweet_dir = os.path.join(output_dir, f"x_post_{tweet_id}")
        logger.debug(f"Creating tweet directory: {tweet_dir}")
        ensure_directory(tweet_dir)

    # Try to fetch the tweet with retries for token expiration
    retries = 0
    force_refresh = False

    while retries < max_retries:
        headers = DEFAULT_HEADERS.copy()
        if not cookies:
            try:
                logger.debug(
                    f"No cookies provided, attempting to get guest token (retry {retries+1}/{max_retries})"
                )
                headers["x-guest-token"] = get_guest_token(
                    token_cache_dir, token_cache_filename, force_refresh
                )
                print(f"Using guest token: {headers['x-guest-token']}")
                logger.info(
                    f"Using guest token: {headers['x-guest-token']} (retry {retries+1}/{max_retries})"
                )
            except APIError as e:
                logger.error(f"Failed to get guest token: {e}")
                print(e)
                return None
        else:
            logger.info("Using provided cookies for authentication")
            headers["Cookie"] = cookies
            print("Using provided cookies")

        print(f"Fetching data for tweet ID: {tweet_id}")
        logger.info(f"Fetching data for tweet ID: {tweet_id}")
        try:
            data = fetch_tweet_data(tweet_id, headers)
            # If we get here, the request succeeded
            break
        except TokenExpiredError as e:
            retries += 1
            if retries >= max_retries:
                logger.error(f"Giving up after {max_retries} token expiration retries")
                print(f"Failed after {max_retries} attempts with token expiration: {e}")
                return None

            # Invalidate the token and try again with a fresh one
            logger.warning(f"Token expired, invalidating and retrying ({retries}/{max_retries})")
            print(f"Token expired, retrying with a fresh token (attempt {retries+1}/{max_retries})")
            invalidate_guest_token(token_cache_dir, token_cache_filename)
            force_refresh = True
            continue

        except APIError as e:
            logger.error(f"Failed to fetch tweet data: {e}")
            print(e)
            return None

    # Process the tweet data
    logger.debug("Processing retrieved tweet data")
    tweet = data.get("data", {}).get("tweetResult", {}).get("result", {})
    legacy = tweet.get("legacy", {})
    user = tweet.get("core", {}).get("user_results", {}).get("result", {}).get("legacy", {})
    note_tweet = tweet.get("note_tweet", {}).get("note_tweet_results", {}).get("result", {})

    logger.debug("Creating Post object from API data")
    post = Post.from_api_data(tweet, legacy, user, note_tweet)

    # Recursively fetch quoted tweets if enabled
    if fetch_quoted_tweets:
        logger.info("Recursively fetching quoted tweets if needed")
        post = fetch_quoted_tweets_recursively(
            post, headers, token_cache_dir, token_cache_filename, max_retries
        )

    if save_raw_response_to_file and tweet_dir:
        # Save raw response
        raw_file = os.path.join(tweet_dir, "raw_response.json")
        logger.debug(f"Saving raw response to: {raw_file}")
        save_json(data, raw_file)
        print(f"Raw response saved to: {raw_file}")

        # Save structured tweet data
        json_file = os.path.join(tweet_dir, "tweet.json")
        logger.debug(f"Saving structured JSON to: {json_file}")
        save_json(post.to_dict(), json_file)
        print(f"Structured JSON saved to: {json_file}")

    logger.info(f"Successfully downloaded and processed tweet ID: {tweet_id}")
    return post
