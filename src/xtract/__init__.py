"""
xtract - A library for extracting data from X (formerly Twitter) posts.
"""

from xtract.api.client import download_x_post
from xtract.models.post import Post, PostData
from xtract.models.user import UserDetails
from xtract.utils.markdown import post_to_markdown, save_post_as_markdown

__version__ = "0.1.0"

__all__ = [
    "download_x_post", 
    "Post", 
    "PostData", 
    "UserDetails", 
    "post_to_markdown", 
    "save_post_as_markdown"
]
