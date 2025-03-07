# Xtract

A Python library for extracting data from X (formerly Twitter) posts.

## Version

Current version: 1.2.3

## Features

- Download post content including text, media, and metadata
- Extract user information
- Support for quoted posts
- Save data as JSON
- Generate Markdown summaries of posts
- Command-line interface

## Installation

```bash
# Basic installation
pip install xtract

# Install with development dependencies
pip install xtract[dev]
```

Or install from source:

```bash
# Clone the repository
git clone https://github.com/yourusername/xtract.git
cd xtract

# Basic installation
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Dependencies

- Core dependencies:
  - requests>=2.31.0
  - urllib3>=2.0.7
  - certifi>=2023.7.22
  - charset-normalizer>=3.3.2
  - idna>=3.4

- Development dependencies:
  - pytest>=7.4.0
  - pytest-cov>=4.1.0
  - black>=23.7.0
  - isort>=5.12.0
  - mypy>=1.5.1
  - flake8>=6.1.0

## Usage

### Downloading a post

You can download a post by providing either the tweet ID or the full URL:

```python
from xtract import download_x_post

# Using tweet ID
post = download_x_post("1895573480835539451")

# Using URL
post = download_x_post("https://x.com/xuser/status/1895573480835539451")
```

Both methods will retrieve the same post. The URL format supports various variations:
- `https://x.com/username/status/ID`
- `https://twitter.com/username/status/ID`
- URLs with query parameters
- URLs with additional path segments

### Converting Posts to Markdown

You can convert a post to Markdown format:

```python
from xtract import download_x_post, post_to_markdown, save_post_as_markdown

# Download a post
post = download_x_post("1895573480835539451")

# Convert to Markdown string
markdown_content = post_to_markdown(post)
print(markdown_content)

# Skip metadata section if desired
markdown_without_metadata = post_to_markdown(post, include_metadata=False)

# Control stats and metadata separately
markdown_custom = post_to_markdown(post, include_stats=True, include_metadata=True)

# Save as Markdown file
markdown_path = save_post_as_markdown(post, output_dir="output")
print(f"Markdown saved to: {markdown_path}")
```

The Markdown output includes:
- YAML frontmatter with metadata (tweet ID, author, statistics, etc.)
- Post text and creation date
- Author information
- Post statistics (views, likes, retweets, etc.)
- Links to images and videos
- Quoted tweet content (if present, without metadata)

Example output format:
```markdown
---
tweet_id: 1895573480835539451
author: xuser
display_name: X User
date: 2024-03-28 12:34:56
is_verified: True
image_count: 1
video_count: 0
views: 1234567
likes: 12345
retweets: 1234
replies: 123
quotes: 12
has_quoted_tweet: false
url: https://x.com/xuser/status/1895573480835539451
---

# Post by @xuser ✓
**X User** (@xuser) • 2024-03-28 12:34:56

This is the post text content...
```

### Advanced Features

#### Token Expiration Handling

The library includes automatic token expiration handling with retry logic:

```python
from xtract import download_x_post

# Default behavior automatically retries on token expiration
post = download_x_post("1895573480835539451")

# Control maximum number of retries for token expiration
post = download_x_post("1895573480835539451", max_retries=3)

# Disable retries
post = download_x_post("1895573480835539451", max_retries=0)
```

#### Quoted Tweet Support

Xtract properly handles and includes quoted tweets in the downloaded data:

```python
from xtract import download_x_post

# Download a post with a quoted tweet
post = download_x_post("1895573480835539451")
post_dict = post.to_dict()

# Check if post contains a quoted tweet
if 'quoted_tweet' in post_dict:
    quoted_tweet = post_dict['quoted_tweet']
    print(f"Quoted tweet ID: {quoted_tweet['tweet_id']}")
    print(f"Quoted tweet author: {quoted_tweet['username']}")
    print(f"Quoted tweet text: {quoted_tweet['text']}")
```

The Markdown output includes:
- YAML frontmatter with metadata (tweet ID, author, statistics, etc.)

### Command Line Usage

```bash
# Basic usage with tweet ID
python -m xtract 1895573480835539451

# Using URL
python -m xtract https://x.com/xuser/status/1895573480835539451

# Save to custom directory
python -m xtract 1895573480835539451 --output-dir my_downloads

# Generate Markdown summary
python -m xtract 1895573480835539451 --markdown

# Save raw API response
python -m xtract 1895573480835539451 --save-raw

# Pretty-print JSON output to console
python -m xtract 1895573480835539451 --pretty
```

## Project Structure

```
.
├── install.sh              # Quick installation script
├── pyproject.toml          # Project configuration
├── README.md               # Project documentation
├── setup.py                # Package installation configuration
├── test_xtract.py          # Simple test script
└── xtract/                 # Main package
    ├── __init__.py         # Package exports
    ├── cli.py              # Command-line interface
    ├── api/                # API interaction
    │   ├── __init__.py
    │   ├── client.py       # API client functions
    │   └── errors.py       # Custom exceptions
    ├── config/             # Configuration
    │   ├── __init__.py
    │   └── constants.py    # Constants and defaults
    ├── models/             # Data models
    │   ├── __init__.py
    │   ├── post.py         # Post and PostData classes
    │   └── user.py         # UserDetails class
    └── utils/              # Utilities
        ├── __init__.py
        ├── file.py         # File handling
        ├── markdown.py     # Markdown generation
        └── media.py        # Media processing
```

## Running Tests

To verify the xtract library is working:

```bash
# Run the test script directly
python test_xtract.py

# Or use the install script which creates a venv and runs the test
./install.sh
```

The test script will:
1. Fetch a sample X post using the xtract library
2. Display the post details if successful
3. Save the post data to the x_post_downloads directory

## License

MIT

## Credits

Created by Eric Wu

## Testing

This project uses pytest for testing. To run the tests:

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=xtract

# Generate HTML coverage report
python -m pytest --cov=xtract --cov-report=html
```

After running the HTML coverage report, you can view the results by opening `htmlcov/index.html` in your browser.

## Development

To set up the development environment:

1. Clone the repository
2. Install the package with development dependencies: `pip install -e ".[dev]"`
3. Use the provided `install.sh` script for a quick setup
