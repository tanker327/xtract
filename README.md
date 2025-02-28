# Xtract

A Python library for extracting data from X (formerly Twitter) posts.

## Features

- Download post content including text, media, and metadata
- Extract user information
- Support for quoted posts
- Save data as JSON
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

### As a Library

```python
from xtract import download_x_post

# Download a post by ID
post = download_x_post("1892413385804792307")

# Access post data
print(post.text)
print(post.images)
print(post.user_details.name)

# Convert to dictionary
post_dict = post.to_dict()
```

### Command Line

```bash
# Basic usage
xtract 1892413385804792307

# With options
xtract 1892413385804792307 --output-dir downloads --pretty
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
