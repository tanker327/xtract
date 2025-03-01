"""
Logging configuration for the xtract package.
"""

import logging
import sys

# Define log formats
DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DEBUG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"

# Set up the basic configuration
def configure_logging(level=logging.INFO, log_format=None):
    """
    Configure the logging for the xtract package.
    
    Args:
        level: The logging level to use (default: INFO)
        log_format: The format string to use for log messages
    """
    if log_format is None:
        log_format = DEBUG_FORMAT if level <= logging.DEBUG else DEFAULT_FORMAT
        
    # Configure the root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        stream=sys.stdout,
    )
    
    # Set the level for the xtract package
    logging.getLogger("xtract").setLevel(level)

def get_logger(name):
    """
    Get a logger with the given name.
    
    Args:
        name: The name of the logger, typically __name__
        
    Returns:
        A configured logger instance
    """
    if name.startswith("xtract."):
        return logging.getLogger(name)
    else:
        return logging.getLogger(f"xtract.{name}") 