"""
Command-line interface for the xtract library.
"""

import argparse
import json
import sys
import os
import logging

from xtract.config.logging import get_logger, configure_logging
from xtract.api.client import download_x_post
from xtract.utils.markdown import save_post_as_markdown

# Create a logger for this module
logger = get_logger(__name__)

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Download content from X posts")
    parser.add_argument("tweet_id", help="X post ID or URL (e.g., 1892413385804792307 or https://x.com/username/status/1892413385804792307)")
    parser.add_argument(
        "--output-dir", default="x_post_downloads", help="Directory to save downloaded content"
    )
    parser.add_argument("--cookies", help="Cookies for authentication (optional)")
    parser.add_argument(
        "--save-raw", action="store_true", default=True, help="Save raw API response"
    )
    parser.add_argument(
        "--pretty", action="store_true", default=False, help="Pretty-print JSON output to console"
    )
    parser.add_argument(
        "--markdown", action="store_true", default=False, help="Generate a Markdown file of the post"
    )
    parser.add_argument(
        "--verbose", action="store_true", default=False, help="Enable verbose logging output"
    )
    parser.add_argument(
        "--include-replies", action="store_true", default=False, help="Fetch and include replies in the post data"
    )

    args = parser.parse_args()
    
    # Configure logging based on verbosity
    if args.verbose:
        configure_logging(level=logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    logger.info("Starting xtract CLI")

    # Check if input is a URL or ID
    if "/" in args.tweet_id and "status" in args.tweet_id:
        logger.info(f"Detected URL, extracting tweet ID from: {args.tweet_id}")
        print(f"Detected URL, extracting tweet ID from: {args.tweet_id}")
    elif not args.tweet_id.isdigit():
        error_msg = "Error: Please enter a valid numeric tweet ID or a valid X post URL."
        logger.error(error_msg)
        print(error_msg)
        sys.exit(1)

    logger.info(f"Downloading content for tweet: {args.tweet_id}")
    print(f"Downloading content for tweet: {args.tweet_id}")
    
    try:
        post = download_x_post(
            args.tweet_id,
            output_dir=args.output_dir,
            cookies=args.cookies,
            save_raw_response_to_file=args.save_raw,
            include_replies=args.include_replies,
        )

        if post:
            logger.info(f"Successfully downloaded content for tweet ID: {post.tweet_id}")
            
            if args.pretty:
                logger.debug("Pretty-printing JSON output")
                print("\nResulting JSON:")
                print(json.dumps(post.to_dict(), indent=2))
            else:
                print("Download completed successfully!")
                
            # Generate Markdown if requested
            if args.markdown:
                logger.info("Generating Markdown summary")
                tweet_dir = os.path.join(args.output_dir, f"x_post_{post.tweet_id}")
                markdown_path = save_post_as_markdown(post, output_dir=tweet_dir)
                logger.info(f"Markdown summary saved to: {markdown_path}")
                print(f"Markdown summary generated: {markdown_path}")
        else:
            error_msg = "Failed to download post content."
            logger.error(error_msg)
            print(error_msg)
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Error during download: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)
        
    logger.info("CLI execution completed successfully")


if __name__ == "__main__":
    main()
