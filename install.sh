#!/bin/bash
# Simple installation script for xtract

# Create and activate virtual environment
echo "Creating virtual environment..."
python -m venv .venv
source .venv/bin/activate

# Install the package in development mode with dev dependencies
echo "Installing xtract in development mode with dev dependencies..."
pip install -e ".[dev]"

# Run the test script
echo "Running test script..."
python test_xtract.py

echo "Installation complete! You can activate the virtual environment with:"
echo "source .venv/bin/activate" 