"""
Command-line interface for the xtract library.
"""

import argparse
import json
import sys
import os

from xtract.api.client import download_x_post
from xtract.utils.markdown import save_post_as_markdown


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

    args = parser.parse_args()

    # Check if input is a URL or ID
    if "/" in args.tweet_id and "status" in args.tweet_id:
        print(f"Detected URL, extracting tweet ID from: {args.tweet_id}")
    elif not args.tweet_id.isdigit():
        print("Error: Please enter a valid numeric tweet ID or a valid X post URL.")
        sys.exit(1)

    print(f"Downloading content for tweet: {args.tweet_id}")
    post = download_x_post(
        args.tweet_id,
        output_dir=args.output_dir,
        cookies=args.cookies,
        save_raw_response_to_file=args.save_raw,
    )

    if post:
        if args.pretty:
            print("\nResulting JSON:")
            print(json.dumps(post.to_dict(), indent=2))
        else:
            print("Download completed successfully!")
            
        # Generate Markdown if requested
        if args.markdown:
            tweet_dir = os.path.join(args.output_dir, f"x_post_{post.tweet_id}")
            markdown_path = save_post_as_markdown(post, output_dir=tweet_dir)
            print(f"Markdown summary generated: {markdown_path}")
    else:
        print("Failed to download post content.")
        sys.exit(1)


if __name__ == "__main__":
    main()
