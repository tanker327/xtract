"""
Client for interacting with X's API.
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List
from urllib.parse import urlparse

from xtract.api.errors import APIError, TokenExpiredError
from xtract.config.constants import (
    DEFAULT_HEADERS,
    GUEST_TOKEN_URL,
    TWEET_DATA_URL,
    DEFAULT_FEATURES,
    DEFAULT_FIELD_TOGGLES,
    DEFAULT_OUTPUT_DIR,
)
from xtract.config.logging import get_logger
from xtract.models.post import Post
from xtract.utils.file import save_json, ensure_directory

# Get a logger for this module
logger = get_logger(__name__)


def get_guest_token(token_cache_dir: str = "/tmp/xtract/", token_cache_filename: str = "guest_token.json", force_refresh: bool = False) -> Optional[str]:
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
            with open(token_file_path, 'r') as f:
                token_data = json.load(f)
                token = token_data.get('token')
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
            with open(token_file_path, 'w') as f:
                json.dump({'token': token, 'timestamp': datetime.now().isoformat()}, f)
            logger.debug(f"Saved guest token to cache: {token_file_path}")
        except IOError as e:
            logger.warning(f"Failed to cache token: {e}")
        
        return token
    except requests.RequestException as e:
        logger.error(f"Failed to fetch guest token: {e}")
        raise APIError(f"Failed to fetch guest token: {e}")


def invalidate_guest_token(token_cache_dir: str = "/tmp/xtract/", token_cache_filename: str = "guest_token.json") -> None:
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
            error_msg = f"Token expired or invalid (403 Forbidden) for tweet {tweet_id}: {response.text}"
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


def fetch_tweet_replies(tweet_id: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Fetch raw reply data for a given tweet ID from the X API.
    This function focuses on fetching the first batch of replies and does not implement pagination.

    Args:
        tweet_id: ID of the tweet for which to fetch replies.
        headers: Headers for the API request, including authentication.

    Returns:
        List[Dict[str, Any]]: A list of raw reply tweet objects. Returns an empty list if
                              no replies are found or in case of an error during parsing.

    Raises:
        TokenExpiredError: If the API returns a 403 error (typically means token expired).
        APIError: If the API request fails for other reasons.
    """
    logger.info(f"Attempting to fetch replies for tweet ID: {tweet_id}")

    variables = {
        "focalTweetId": tweet_id,
        "withReplies": True,  # Key to fetch replies
        "withCommunity": False,
        "includePromotedContent": False,
        "withVoice": False,
        # Adding cursor might be necessary for pagination, but omitted for simplicity now
        # "cursor": None,
    }
    params = {
        "variables": json.dumps(variables),
        "features": json.dumps(DEFAULT_FEATURES),
        "fieldToggles": json.dumps(DEFAULT_FIELD_TOGGLES), # Ensure this matches other calls
    }

    try:
        logger.debug(f"Sending request to {TWEET_DATA_URL} for replies to tweet ID: {tweet_id}")
        response = requests.get(TWEET_DATA_URL, headers=headers, params=params)

        if response.status_code == 403:
            error_msg = f"Token expired or invalid (403 Forbidden) while fetching replies for tweet {tweet_id}: {response.text}"
            logger.warning(error_msg)
            raise TokenExpiredError(error_msg)

        response.raise_for_status()
        raw_json_response = response.json()
        logger.debug(f"Successfully received response for replies to tweet ID: {tweet_id}")

    except requests.HTTPError as e:
        logger.error(f"HTTP error fetching replies for tweet {tweet_id}: {e}")
        raise APIError(f"HTTP error fetching replies for tweet {tweet_id}: {e}")
    except requests.RequestException as e:
        logger.error(f"Request exception fetching replies for tweet {tweet_id}: {e}")
        raise APIError(f"Request exception fetching replies for tweet {tweet_id}: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response when fetching replies for {tweet_id}: {e}")
        raise APIError(f"Failed to decode JSON response for replies to {tweet_id}: {e}")

    replies_data = []
    try:
        # Speculative path to replies based on common API patterns for threaded conversations
        # The actual path might differ and need inspection of a live API response.
        # Common structures involve 'instructions' which contain 'entries' or 'items'.
        instructions = raw_json_response.get("data", {}).get("threaded_conversation_with_replies", {}).get("instructions", [])
        if not instructions: # Fallback for slightly different structures seen in some API versions
            instructions = raw_json_response.get("data", {}).get("tweetResult", {}).get("result", {}).get("tweet", {}).get("conversation_thread",{}).get("instructions",[])

        entries = []
        for instruction in instructions:
            # Entries can be directly under instruction or under typedInstruction
            if "entries" in instruction:
                entries.extend(instruction.get("entries", []))
            elif instruction.get("type") == "TimelineAddEntries" or "addEntries" in instruction: # Common instruction type
                 entries.extend(instruction.get("addEntries", {}).get("entries", []))


        if not entries:
            logger.warning(f"No 'entries' found in the expected path for tweet {tweet_id} replies. Full response snippet: {str(raw_json_response)[:500]}")
            return []

        for entry in entries:
            # Entries can have different structures. We are looking for those containing tweet data.
            # The 'entryId' often indicates the type of item, e.g., 'tweet-<id>', 'conversationthread-<id>', 'cursor-top', 'cursor-bottom'.
            entry_id_str = entry.get("entryId", "")

            if "tweet-" in entry_id_str or "conversationthread-" in entry_id_str : # Check if it's likely a tweet entry
                content = entry.get("content", {})
                item_content = content.get("itemContent", {})
                if not item_content and "items" in content: # Another possible structure where items are nested
                    for item_entry in content.get("items", []):
                        item_content_candidate = item_entry.get("item",{}).get("itemContent",{})
                        if item_content_candidate.get("tweet_results",{}).get("result"):
                            item_content = item_content_candidate
                            break # Take the first valid one

                tweet_result = item_content.get("tweet_results", {}).get("result")

                if not tweet_result: # Try another common path for conversation items (e.g. within "item" key)
                     tweet_result = content.get("items", [{}])[0].get("item", {}).get("itemContent", {}).get("tweet_results", {}).get("result")


                if tweet_result:
                    # Ensure it's a valid tweet object (e.g., has 'legacy' data and is not the focal tweet itself)
                    # The API might return the focal tweet as part of the conversation thread.
                    if tweet_result.get("legacy") and tweet_result.get("rest_id") != tweet_id:
                        logger.debug(f"Found reply: {tweet_result.get('rest_id')} for focal tweet {tweet_id}")
                        replies_data.append(tweet_result)
                    elif tweet_result.get("rest_id") == tweet_id:
                        logger.debug(f"Skipping entry for focal tweet {tweet_id} found within replies.")
                else:
                    logger.debug(f"Entry {entry_id_str} did not contain tweet_results.result in expected location. Keys: {item_content.keys()}")
            elif not ("cursor-top" in entry_id_str or "cursor-bottom" in entry_id_str or "who-to-follow" in entry_id_str or "profile-spotlight" in entry_id_str):
                 logger.debug(f"Skipping non-tweet/non-conversationthread entry: {entry_id_str}")


    except Exception as e:
        logger.warning(f"Error parsing replies for tweet {tweet_id}: {e}. Response snippet: {str(raw_json_response)[:500]}")
        # Return whatever was parsed so far, or an empty list
        return replies_data

    if not replies_data:
        logger.info(f"No replies found or extracted for tweet ID: {tweet_id}")
    else:
        logger.info(f"Successfully extracted {len(replies_data)} replies for tweet ID: {tweet_id}")

    return replies_data


def download_x_post(
    post_identifier: str,
    output_dir: str = None,
    cookies: str = None,
    save_raw_response_to_file: bool = False,
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
                logger.debug(f"No cookies provided, attempting to get guest token (retry {retries+1}/{max_retries})")
                headers["x-guest-token"] = get_guest_token(token_cache_dir, token_cache_filename, force_refresh)
                print(f"Using guest token: {headers['x-guest-token']}")
                logger.info(f"Using guest token: {headers['x-guest-token']} (retry {retries+1}/{max_retries})")
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
    tweet_result_data = data.get("data", {}).get("tweetResult", {}).get("result", {})

    if not tweet_result_data or not tweet_result_data.get("rest_id"):
        logger.error(f"Main tweet data is missing 'rest_id' or is malformed for original ID: {tweet_id}. Response snippet: {str(data)[:500]}")
        # Depending on desired strictness, one might return None or raise an error here.
        # For now, we'll log and attempt to proceed if possible, or let it fail at Post.from_api_data.
        # If tweet_result_data is empty, Post.from_api_data will likely fail, which is acceptable.

    # Fetch replies
    raw_replies = []
    try:
        logger.info(f"Fetching replies for tweet ID: {tweet_id}")
        # Use the same headers, which include the guest token if applicable
        raw_replies = fetch_tweet_replies(tweet_id, headers)
        if raw_replies:
            logger.info(f"Successfully fetched {len(raw_replies)} raw replies for tweet ID: {tweet_id}")
        else:
            logger.info(f"No replies found or fetched for tweet ID: {tweet_id}")
    except APIError as e: # Includes TokenExpiredError
        logger.warning(f"Could not fetch replies for tweet ID {tweet_id}: {e}. Continuing without replies.")
        # Optional: could trigger a retry or token refresh here if desired, but fetch_tweet_replies already has some handling
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching replies for tweet ID {tweet_id}: {e}. Continuing without replies.")

    reply_objects = []
    if raw_replies:
        logger.debug(f"Processing {len(raw_replies)} raw replies into Post objects for tweet ID: {tweet_id}")
        for i, raw_reply_data in enumerate(raw_replies):
            try:
                if not raw_reply_data or not raw_reply_data.get("rest_id"):
                    logger.warning(f"Skipping reply {i+1} for tweet {tweet_id} due to missing 'rest_id' or malformed data: {str(raw_reply_data)[:200]}")
                    continue

                logger.debug(f"Processing reply tweet ID: {raw_reply_data.get('rest_id')}")
                # The raw_reply_data itself is the 'tweet' part for Post.from_api_data
                reply_tweet_api_data = raw_reply_data
                reply_legacy_data = raw_reply_data.get("legacy", {})
                reply_user_data = raw_reply_data.get("core", {}).get("user_results", {}).get("result", {}).get("legacy", {})
                # Check if user_results.result itself is the user data, common in some API responses
                if not reply_user_data and raw_reply_data.get("core", {}).get("user_results", {}).get("result"):
                    reply_user_data = raw_reply_data.get("core", {}).get("user_results", {}).get("result") # No .legacy here

                reply_note_tweet_data = raw_reply_data.get("note_tweet", {}).get("note_tweet_results", {}).get("result", {})

                # Basic check to ensure essential data parts are present
                if not reply_legacy_data:
                    logger.warning(f"Skipping reply {raw_reply_data.get('rest_id')} due to missing 'legacy' data.")
                    continue
                if not reply_user_data: # User data is essential
                     logger.warning(f"Skipping reply {raw_reply_data.get('rest_id')} due to missing 'user' data (core.user_results.result.legacy).")
                     continue


                reply_post_obj = Post.from_api_data(
                    tweet=reply_tweet_api_data,
                    legacy=reply_legacy_data,
                    user=reply_user_data,
                    note_tweet=reply_note_tweet_data
                )
                reply_objects.append(reply_post_obj)
            except Exception as e:
                logger.error(f"Failed to process reply {i+1} (ID: {raw_reply_data.get('rest_id', 'unknown')}) for tweet {tweet_id}: {e}. Reply data snippet: {str(raw_reply_data)[:200]}")
                # Continue to the next reply

    # Definitions for the main post
    legacy = tweet_result_data.get("legacy", {})
    user = tweet_result_data.get("core", {}).get("user_results", {}).get("result", {}).get("legacy", {})
    # Check if user_results.result itself is the user data
    if not user and tweet_result_data.get("core", {}).get("user_results", {}).get("result"):
        user = tweet_result_data.get("core", {}).get("user_results", {}).get("result")


    note_tweet = tweet_result_data.get("note_tweet", {}).get("note_tweet_results", {}).get("result", {})

    logger.debug("Creating main Post object from API data")
    # Use tweet_result_data for the 'tweet' argument as it's the specific result for the main tweet
    main_post = Post.from_api_data(tweet_result_data, legacy, user, note_tweet)

    if reply_objects:
        main_post.replies = reply_objects
        logger.info(f"Successfully processed and attached {len(reply_objects)} replies to main post ID: {main_post.tweet_id}")

    if save_raw_response_to_file and tweet_dir:
        # Save raw response for the main tweet
        raw_file = os.path.join(tweet_dir, "raw_response.json")
        logger.debug(f"Saving raw response to: {raw_file}")
        save_json(data, raw_file) # 'data' contains the full response for the main tweet

        # Save structured tweet data (now including replies)
        json_file = os.path.join(tweet_dir, "tweet.json")
        logger.debug(f"Saving structured JSON to: {json_file}")
        save_json(main_post.to_dict(), json_file) # Use main_post here

    logger.info(f"Successfully downloaded and processed tweet ID: {tweet_id} (Main Post ID: {main_post.tweet_id})")
    return main_post
