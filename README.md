# xtract

A Python library for extracting data.

## Installation

```bash
pip install -e .
```

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
2. Install the package in development mode: `pip install -e .`
3. Install development dependencies: `pip install pytest pytest-cov`
