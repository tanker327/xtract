# Xtract Usage Guide

A comprehensive guide for using the Xtract library to extract data from X (formerly Twitter) posts.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Basic Usage](#basic-usage)
- [Parameters Reference](#parameters-reference)
- [Understanding the Output](#understanding-the-output)
- [Working with Media](#working-with-media)
- [Quoted Tweets](#quoted-tweets)
- [Markdown Generation](#markdown-generation)
- [Advanced Features](#advanced-features)
- [Error Handling](#error-handling)

## Installation

```bash
# Install from pip
pip install xtract

# Or install from source
git clone https://github.com/yourusername/xtract.git
cd xtract
pip install -e .
```

## Quick Start

The simplest way to download a post:

```python
from xtract import download_x_post

# Download a post by ID
post = download_x_post("1895573480835539451")

# Or use the full URL
post = download_x_post("https://x.com/username/status/1895573480835539451")

# Access the data
print(f"Text: {post.text}")
print(f"Author: @{post.username}")
print(f"Likes: {post.post_data.favorite_count}")
```

## Basic Usage

### Downloading a Post

```python
from xtract import download_x_post

# Method 1: Using tweet ID
post = download_x_post("1895573480835539451")

# Method 2: Using X.com URL
post = download_x_post("https://x.com/username/status/1895573480835539451")

# Method 3: Using Twitter.com URL (legacy)
post = download_x_post("https://twitter.com/username/status/1895573480835539451")
```

All URL formats are supported, including URLs with query parameters or additional path segments.

### Saving to Files

```python
from xtract import download_x_post

# Save raw API response and structured JSON to files
post = download_x_post(
    "1895573480835539451",
    output_dir="my_downloads",
    save_raw_response_to_file=True
)

# This creates the following directory structure:
# my_downloads/
#   └── x_post_1895573480835539451/
#       ├── raw_response.json     # Raw API response
#       └── tweet.json            # Structured tweet data
```

### Converting to Dictionary

```python
from xtract import download_x_post

post = download_x_post("1895573480835539451")

# Convert to dictionary for easy access
post_dict = post.to_dict()

# Access any field
print(post_dict['text'])
print(post_dict['images'])
print(post_dict['user_details']['name'])
```

## Parameters Reference

### `download_x_post()` Parameters

```python
def download_x_post(
    post_identifier: str,
    output_dir: str = None,
    cookies: str = None,
    save_raw_response_to_file: bool = False,
    token_cache_dir: str = "/tmp/xtract/",
    token_cache_filename: str = "guest_token.json",
    max_retries: int = 3,
) -> Optional[Post]:
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `post_identifier` | `str` | **Required** | Tweet ID (e.g., "1895573480835539451") or URL (e.g., "https://x.com/user/status/1895573480835539451") |
| `output_dir` | `str` | `None` (current directory) | Directory where files will be saved when `save_raw_response_to_file=True` |
| `cookies` | `str` | `None` | Optional cookies for authentication. If not provided, uses guest token authentication |
| `save_raw_response_to_file` | `bool` | `False` | Whether to save raw API response and structured JSON to files |
| `token_cache_dir` | `str` | `"/tmp/xtract/"` | Directory to cache guest tokens |
| `token_cache_filename` | `str` | `"guest_token.json"` | Filename for the cached token |
| `max_retries` | `int` | `3` | Maximum number of retries when token expires (use `0` to disable retries) |

**Returns:** `Post` object if successful, `None` if failed

### `post_to_markdown()` Parameters

```python
def post_to_markdown(
    post: Post,
    include_stats: bool = True,
    include_metadata: bool = True
) -> tuple[dict, str]:
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `post` | `Post` | **Required** | The Post object to convert |
| `include_stats` | `bool` | `True` | Whether to include post statistics (views, likes, retweets, etc.) |
| `include_metadata` | `bool` | `True` | Whether to include YAML frontmatter metadata |

**Returns:** Tuple of `(metadata_dict, markdown_content)`

### `save_post_as_markdown()` Parameters

```python
def save_post_as_markdown(
    post: Post,
    output_dir: str = None,
    filename: str = None
) -> str:
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `post` | `Post` | **Required** | The Post object to save |
| `output_dir` | `str` | `None` (current directory) | Directory to save the Markdown file |
| `filename` | `str` | `"tweet_{tweet_id}.md"` | Name of the Markdown file |

**Returns:** Path to the saved Markdown file

## Understanding the Output

### Post Object Structure

When you download a post, you get a `Post` object with the following structure:

```python
from xtract import download_x_post

post = download_x_post("1895573480835539451")

# Basic post information
post.tweet_id           # str: "1895573480835539451"
post.username           # str: "xuser"
post.text               # str: The full text of the post
post.created_at         # str: "Wed Feb 28 12:00:00 +0000 2024"
post.view_count         # str: "1234567"

# Media URLs (where images and videos are located)
post.images             # List[str]: ["https://pbs.twimg.com/media/...", ...]
post.videos             # List[str]: ["https://video.twimg.com/...", ...]

# User information
post.user_details       # UserDetails object
post.user_details.name              # str: "Display Name"
post.user_details.screen_name       # str: "xuser"
post.user_details.description       # str: User bio
post.user_details.followers_count   # int: Number of followers
post.user_details.following_count   # int: Number of following
post.user_details.is_verified       # bool: Verification status
post.user_details.profile_image_url # str: Profile image URL
post.user_details.profile_banner_url # str: Banner image URL

# Post statistics and metadata
post.post_data                      # PostData object
post.post_data.favorite_count       # int: Number of likes
post.post_data.retweet_count        # int: Number of retweets
post.post_data.reply_count          # int: Number of replies
post.post_data.quote_count          # int: Number of quote tweets
post.post_data.bookmark_count       # int: Number of bookmarks
post.post_data.lang                 # str: Language code (e.g., "en")
post.post_data.is_quote_status      # bool: Whether this is a quote tweet

# Quoted tweet (if present)
post.quoted_tweet       # Post object or None
```

### Complete Output Example

```python
from xtract import download_x_post
import json

post = download_x_post("1895573480835539451")

# Convert to dictionary for inspection
post_dict = post.to_dict()

# Example output structure:
{
    "tweet_id": "1895573480835539451",
    "username": "xuser",
    "created_at": "Wed Feb 28 12:00:00 +0000 2024",
    "text": "This is the full text of the post...",
    "view_count": "1234567",

    # Images are stored as URLs in this array
    "images": [
        "https://pbs.twimg.com/media/GJxyz123_abc.jpg",
        "https://pbs.twimg.com/media/GJxyz456_def.jpg"
    ],

    # Videos are stored as URLs in this array
    "videos": [
        "https://video.twimg.com/ext_tw_video/1234567890/pu/vid/720x1280/example.mp4"
    ],

    "user_details": {
        "name": "Display Name",
        "screen_name": "xuser",
        "description": "User bio goes here",
        "followers_count": 10000,
        "following_count": 500,
        "is_verified": true,
        "profile_image_url": "https://pbs.twimg.com/profile_images/...",
        "profile_banner_url": "https://pbs.twimg.com/profile_banners/..."
    },

    "post_data": {
        "favorite_count": 12345,
        "retweet_count": 1234,
        "reply_count": 123,
        "quote_count": 12,
        "bookmark_count": 234,
        "is_quote_status": false,
        "lang": "en",
        "source": "",
        "possibly_sensitive": false,
        "conversation_id": "1895573480835539451",
        "is_translatable": true,
        "grok_analysis_button": false
    },

    # If the post quotes another tweet, it appears here
    "quoted_tweet": {
        "tweet_id": "1234567890123456789",
        "username": "quoteduser",
        "text": "This is the quoted tweet...",
        "images": [...],
        "videos": [...],
        // ... (same structure as parent post)
    }
}
```

## Working with Media

### Accessing Images

Images are **NOT downloaded** by the library. Instead, the library provides you with direct URLs to the images hosted on X's servers.

```python
from xtract import download_x_post

post = download_x_post("1895573480835539451")

# Check if post has images
if post.images:
    print(f"This post has {len(post.images)} image(s)")

    # Access image URLs
    for i, image_url in enumerate(post.images, 1):
        print(f"Image {i}: {image_url}")
        # Example output:
        # Image 1: https://pbs.twimg.com/media/GJxyz123_abc.jpg
        # Image 2: https://pbs.twimg.com/media/GJxyz456_def.jpg

# Download images yourself if needed
import requests

for i, image_url in enumerate(post.images):
    response = requests.get(image_url)
    with open(f"image_{i}.jpg", "wb") as f:
        f.write(response.content)
    print(f"Downloaded image_{i}.jpg")
```

### Accessing Videos

Videos work the same way as images - you get URLs, not downloaded files.

```python
from xtract import download_x_post

post = download_x_post("1895573480835539451")

# Check if post has videos
if post.videos:
    print(f"This post has {len(post.videos)} video(s)")

    # Access video URLs
    for i, video_url in enumerate(post.videos, 1):
        print(f"Video {i}: {video_url}")
        # Example output:
        # Video 1: https://video.twimg.com/ext_tw_video/1234567890/pu/vid/720x1280/example.mp4

# Download videos yourself if needed
import requests

for i, video_url in enumerate(post.videos):
    response = requests.get(video_url)
    with open(f"video_{i}.mp4", "wb") as f:
        f.write(response.content)
    print(f"Downloaded video_{i}.mp4")
```

### Media in Quoted Tweets

If a post quotes another tweet that contains media, those media URLs are accessible through the `quoted_tweet` property:

```python
from xtract import download_x_post

post = download_x_post("1895573480835539451")

# Check if there's a quoted tweet
if post.quoted_tweet:
    print("This post quotes another tweet")

    # Access quoted tweet's images
    if post.quoted_tweet.images:
        print(f"Quoted tweet has {len(post.quoted_tweet.images)} image(s)")
        for image_url in post.quoted_tweet.images:
            print(f"  - {image_url}")

    # Access quoted tweet's videos
    if post.quoted_tweet.videos:
        print(f"Quoted tweet has {len(post.quoted_tweet.videos)} video(s)")
        for video_url in post.quoted_tweet.videos:
            print(f"  - {video_url}")
```

## Quoted Tweets

Posts can quote (reference) other tweets. When this happens, the quoted tweet is included in the output.

### Checking for Quoted Tweets

```python
from xtract import download_x_post

post = download_x_post("1895573480835539451")

# Method 1: Check if quoted_tweet exists
if post.quoted_tweet:
    print("This post quotes another tweet")
    print(f"Quoted tweet by: @{post.quoted_tweet.username}")
    print(f"Quoted tweet text: {post.quoted_tweet.text}")

# Method 2: Check using post_data
if post.post_data.is_quote_status:
    print("This is a quote tweet")
```

### Accessing Quoted Tweet Data

The quoted tweet is a complete `Post` object with the same structure:

```python
from xtract import download_x_post

post = download_x_post("1895573480835539451")

if post.quoted_tweet:
    quoted = post.quoted_tweet

    # All the same fields are available
    print(f"Quoted Tweet ID: {quoted.tweet_id}")
    print(f"Quoted by: @{quoted.username}")
    print(f"Text: {quoted.text}")
    print(f"Created: {quoted.created_at}")
    print(f"Likes: {quoted.post_data.favorite_count}")
    print(f"Retweets: {quoted.post_data.retweet_count}")

    # Images and videos from quoted tweet
    if quoted.images:
        print(f"Images in quoted tweet: {quoted.images}")
    if quoted.videos:
        print(f"Videos in quoted tweet: {quoted.videos}")
```

### Complete Example with Quoted Tweet

```python
from xtract import download_x_post

post = download_x_post("1895573480835539451")

# Display main post
print("=" * 50)
print("MAIN POST")
print("=" * 50)
print(f"Author: @{post.username}")
print(f"Text: {post.text}")
print(f"Images: {len(post.images)}")
print(f"Videos: {len(post.videos)}")

# Display quoted tweet if present
if post.quoted_tweet:
    print("\n" + "=" * 50)
    print("QUOTED TWEET")
    print("=" * 50)
    print(f"Author: @{post.quoted_tweet.username}")
    print(f"Text: {post.quoted_tweet.text}")
    print(f"Images: {len(post.quoted_tweet.images)}")
    print(f"Videos: {len(post.quoted_tweet.videos)}")
```

## Markdown Generation

### Basic Markdown Conversion

```python
from xtract import download_x_post, post_to_markdown

post = download_x_post("1895573480835539451")

# Convert to markdown
metadata, markdown_content = post_to_markdown(post)

# metadata is a dictionary with YAML frontmatter data
print("Metadata:")
print(metadata)

# markdown_content is a string with the formatted markdown
print("\nMarkdown Content:")
print(markdown_content)
```

### Saving as Markdown File

```python
from xtract import download_x_post, save_post_as_markdown

post = download_x_post("1895573480835539451")

# Save with default filename (tweet_{tweet_id}.md)
file_path = save_post_as_markdown(post)
print(f"Saved to: {file_path}")

# Save to specific directory
file_path = save_post_as_markdown(post, output_dir="my_markdown_files")

# Save with custom filename
file_path = save_post_as_markdown(
    post,
    output_dir="my_markdown_files",
    filename="my_custom_name.md"
)
```

### Markdown Output Structure

The generated Markdown includes:

1. **YAML Frontmatter** (if `include_metadata=True`):
   - Tweet ID, author, date, verification status
   - Media counts (images, videos)
   - Statistics (views, likes, retweets, replies, quotes)
   - URLs and quoted tweet information

2. **Post Header**:
   - Author display name and username
   - Timestamp
   - Verification badge

3. **Post Content**:
   - Full text

4. **Images Section** (if present):
   - Markdown image links

5. **Videos Section** (if present):
   - Markdown links to videos

6. **Quoted Tweet Section** (if present):
   - Recursively formatted quoted tweet
   - Indented with `>` for visual distinction

7. **Stats Section** (if `include_stats=True`):
   - Views, likes, retweets, replies, quotes

Example Markdown output:

```markdown
---
tweet_id: 1895573480835539451
author: xuser
display_name: X User
date: 2024-02-28 12:00:00
is_verified: True
image_count: 2
video_count: 0
views: 1234567
likes: 12345
retweets: 1234
replies: 123
quotes: 12
has_quoted_tweet: false
url: https://x.com/xuser/status/1895573480835539451
downloaded_at: 2024-03-15 10:30:00
downloaded_by: xtract
---

# Post by @xuser ✓
**X User** (@xuser) • 2024-02-28 12:00:00

This is the post text content...

## Images
![Image 1](https://pbs.twimg.com/media/GJxyz123_abc.jpg)
![Image 2](https://pbs.twimg.com/media/GJxyz456_def.jpg)

## Stats
* **Views:** 1234567
* **Likes:** 12345
* **Retweets:** 1234
* **Replies:** 123
* **Quotes:** 12

*Tweet ID: 1895573480835539451*
```

### Customizing Markdown Output

```python
from xtract import download_x_post, post_to_markdown

post = download_x_post("1895573480835539451")

# Without stats
metadata, markdown = post_to_markdown(post, include_stats=False)

# Without metadata (no YAML frontmatter)
metadata, markdown = post_to_markdown(post, include_metadata=False)

# Minimal markdown (no stats, no metadata)
metadata, markdown = post_to_markdown(
    post,
    include_stats=False,
    include_metadata=False
)
```

## Advanced Features

### Token Expiration Handling

The library automatically handles token expiration with configurable retry logic:

```python
from xtract import download_x_post

# Default: 3 retries on token expiration
post = download_x_post("1895573480835539451")

# Custom retry count
post = download_x_post("1895573480835539451", max_retries=5)

# Disable retries (fail immediately on token expiration)
post = download_x_post("1895573480835539451", max_retries=0)
```

### Custom Token Cache Location

```python
from xtract import download_x_post

# Use custom cache directory
post = download_x_post(
    "1895573480835539451",
    token_cache_dir="/path/to/cache/",
    token_cache_filename="my_token.json"
)
```

### Using Custom Cookies

If you have authentication cookies, you can use them instead of guest tokens:

```python
from xtract import download_x_post

cookies = "your_cookies_here"

post = download_x_post(
    "1895573480835539451",
    cookies=cookies
)
```

### Batch Processing Multiple Posts

```python
from xtract import download_x_post
import time

tweet_ids = [
    "1895573480835539451",
    "1895573480835539452",
    "1895573480835539453",
]

posts = []
for tweet_id in tweet_ids:
    print(f"Downloading {tweet_id}...")
    post = download_x_post(tweet_id)

    if post:
        posts.append(post)
        print(f"  ✓ Success: @{post.username}")
    else:
        print(f"  ✗ Failed")

    # Be nice to the API - add a small delay
    time.sleep(1)

print(f"\nSuccessfully downloaded {len(posts)} posts")
```

## Error Handling

### Handling Download Failures

```python
from xtract import download_x_post

post = download_x_post("1895573480835539451")

if post is None:
    print("Failed to download post")
    # Handle the error (e.g., log, retry, skip)
else:
    print(f"Successfully downloaded post by @{post.username}")
```

### Handling API Errors

```python
from xtract import download_x_post
from xtract.api.errors import APIError, TokenExpiredError

try:
    post = download_x_post("1895573480835539451")
    if post:
        print(f"Downloaded: {post.text}")
except APIError as e:
    print(f"API Error: {e}")
except TokenExpiredError as e:
    print(f"Token Expired: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Checking for Missing Data

```python
from xtract import download_x_post

post = download_x_post("1895573480835539451")

if post:
    # Check for text
    if post.text:
        print(f"Text: {post.text}")
    else:
        print("No text content")

    # Check for media
    if post.images:
        print(f"Found {len(post.images)} image(s)")
    else:
        print("No images")

    if post.videos:
        print(f"Found {len(post.videos)} video(s)")
    else:
        print("No videos")

    # Check for quoted tweet
    if post.quoted_tweet:
        print(f"Quotes: @{post.quoted_tweet.username}")
    else:
        print("No quoted tweet")
```

## Summary

### Key Points to Remember

1. **Media URLs, Not Files**: The library provides URLs to images and videos, it does not download the media files themselves.

2. **Output Location**:
   - **Post content** → `post.text`
   - **Images** → `post.images` (list of URLs)
   - **Videos** → `post.videos` (list of URLs)
   - **Quoted post** → `post.quoted_tweet` (another Post object)
   - **User info** → `post.user_details`
   - **Statistics** → `post.post_data`

3. **File Saving** (when `save_raw_response_to_file=True`):
   - Creates directory: `{output_dir}/x_post_{tweet_id}/`
   - `raw_response.json` - Raw API response
   - `tweet.json` - Structured data

4. **Quoted Tweets**: Have the same structure as main posts and are fully accessible through `post.quoted_tweet`

5. **Token Management**: Automatic with configurable retry logic (default: 3 retries)

### Quick Reference

```python
# Import
from xtract import download_x_post, post_to_markdown, save_post_as_markdown

# Download
post = download_x_post("tweet_id_or_url")

# Access data
post.text                          # Post content
post.images                        # List of image URLs
post.videos                        # List of video URLs
post.quoted_tweet                  # Quoted post (or None)
post.user_details.name             # Author name
post.post_data.favorite_count      # Likes

# Convert to dictionary
data = post.to_dict()

# Generate markdown
metadata, markdown = post_to_markdown(post)
file_path = save_post_as_markdown(post)
```
