# X Post Replies Implementation

This document describes the implementation of reply fetching functionality in the xtract library.

## Overview

The xtract library has been extended to download X post replies and include them in the final JSON output. This feature allows users to fetch not just the original post, but also the conversation thread that follows it.

## Implementation Details

### 1. Constants and Configuration (`src/xtract/config/constants.py`)

Added new constants for conversation/reply fetching:

- `CONVERSATION_URL`: GraphQL endpoint for fetching conversation data
- `CONVERSATION_FEATURES`: Feature flags required for conversation API calls
- `CONVERSATION_FIELD_TOGGLES`: Field toggles for conversation data

### 2. Data Model Updates (`src/xtract/models/post.py`)

Extended the `Post` class with:

- `replies: Optional[List["Post"]] = None` field to store reply posts
- Updated `to_dict()` method to include replies in JSON serialization
- Recursive structure allows replies to have their own replies (nested conversations)

### 3. API Client Extensions (`src/xtract/api/client.py`)

Added two new functions:

#### `fetch_conversation_data(tweet_id: str, headers: Dict[str, str]) -> Dict[str, Any]`
- Fetches conversation data from X's GraphQL API
- Uses the TweetDetail endpoint with conversation-specific parameters
- Handles HTTP errors and API rate limiting

#### `parse_conversation_replies(conversation_data: Dict[str, str]) -> List[Post]`
- Parses the complex conversation response structure
- Extracts reply tweets from the timeline
- Filters out the original tweet to avoid duplication
- Creates Post objects for each reply using existing parsing logic

#### Updated `download_x_post()` function
- Added `include_replies: bool = False` parameter
- Integrates reply fetching into the main download workflow
- Saves raw conversation data when `save_raw_response_to_file=True`
- Gracefully handles reply fetching failures

### 4. Markdown Generation (`src/xtract/utils/markdown.py`)

Enhanced markdown output with:

- **Replies section**: Displays all fetched replies in a structured format
- **Indented formatting**: Replies are visually distinguished with `>` indentation
- **Metadata updates**: Added `has_replies` and `reply_count_fetched` to YAML frontmatter
- **Recursive formatting**: Replies can contain their own quoted tweets and media

### 5. CLI Interface (`src/xtract/cli.py`)

Added command-line support:

- `--include-replies` flag to enable reply fetching
- Integrates seamlessly with existing CLI options
- Works with all output formats (JSON, Markdown, raw data)

## Usage Examples

### Command Line Interface

```bash
# Download a post with replies
python -m xtract.cli 1234567890 --include-replies

# Download with replies and generate markdown
python -m xtract.cli 1234567890 --include-replies --markdown

# Download with replies and pretty-print JSON
python -m xtract.cli 1234567890 --include-replies --pretty
```

### Python API

```python
from xtract.api.client import download_x_post

# Download post without replies (default behavior)
post = download_x_post("1234567890")

# Download post with replies
post_with_replies = download_x_post("1234567890", include_replies=True)

# Access replies
if post_with_replies.replies:
    print(f"Found {len(post_with_replies.replies)} replies")
    for reply in post_with_replies.replies:
        print(f"@{reply.username}: {reply.text}")
```

## Data Structure

### JSON Output Structure

```json
{
  "tweet_id": "1234567890",
  "username": "example_user",
  "text": "Original tweet text",
  "replies": [
    {
      "tweet_id": "1234567891",
      "username": "replier1",
      "text": "First reply text",
      "replies": null
    },
    {
      "tweet_id": "1234567892", 
      "username": "replier2",
      "text": "Second reply text",
      "replies": []
    }
  ]
}
```

### Markdown Output Structure

```markdown
# Post by @example_user ✓
**User Name** (@example_user) • 2024-02-28 12:00:00

Original tweet text

## Replies
---
### Reply 1
> # Post by @replier1
> **Replier Name** (@replier1) • 2024-02-28 12:01:00
> 
> First reply text

### Reply 2
> # Post by @replier2  
> **Replier Name** (@replier2) • 2024-02-28 12:02:00
>
> Second reply text
---

## Stats
* **Views:** 1000
* **Likes:** 50
* **Retweets:** 10
* **Replies:** 25
* **Quotes:** 5
```

## Error Handling

The implementation includes robust error handling:

- **Network errors**: HTTP timeouts and connection issues are caught and logged
- **API errors**: 404s, rate limits, and authentication errors are handled gracefully
- **Parsing errors**: Malformed response data doesn't crash the application
- **Fallback behavior**: If reply fetching fails, the original post is still returned

## Performance Considerations

- **Optional feature**: Replies are only fetched when explicitly requested
- **Separate API call**: Reply fetching uses a different endpoint to avoid affecting main post download
- **Caching**: Guest tokens are reused between main post and reply requests
- **Graceful degradation**: Reply failures don't affect main post download

## File Output

When `save_raw_response_to_file=True`, the following files are created:

- `raw_response.json`: Original tweet API response
- `raw_conversation.json`: Conversation/replies API response (when `include_replies=True`)
- `tweet.json`: Structured JSON with replies included
- `tweet_<id>.md`: Markdown file with replies section (when `--markdown` flag is used)

## Testing

The implementation has been tested with:

- ✅ Syntax validation (all files compile without errors)
- ✅ Data structure integrity (Post model with replies field)
- ✅ API integration (conversation endpoint calls)
- ✅ CLI interface (new --include-replies flag)
- ✅ Error handling (graceful failure when replies unavailable)

## Future Enhancements

Potential improvements for future versions:

1. **Reply depth control**: Limit how deep to fetch nested replies
2. **Reply filtering**: Filter replies by user, date, or engagement metrics
3. **Pagination**: Handle large conversation threads with pagination
4. **Caching**: Cache conversation data to avoid repeated API calls
5. **Rate limiting**: Implement intelligent rate limiting for conversation requests