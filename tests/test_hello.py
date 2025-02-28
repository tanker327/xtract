"""
Tests for the hello function in the xtract package.
"""
from xtract import hello


def test_hello():
    """Test that the hello function returns the expected string."""
    assert hello() == "Hello from xtract!"
    assert isinstance(hello(), str) 