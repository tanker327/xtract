"""
Command-line interface for the xtract library.
"""

import argparse
import json
import sys

from xtract.api.client import download_x_post


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description='Download content from X posts')
    parser.add_argument('tweet_id', help='X post ID (e.g., 1892413385804792307)')
    parser.add_argument('--output-dir', default='x_post_downloads',
                        help='Directory to save downloaded content')
    parser.add_argument('--cookies', help='Cookies for authentication (optional)')
    parser.add_argument('--save-raw', action='store_true', default=True,
                        help='Save raw API response')
    parser.add_argument('--pretty', action='store_true', default=False,
                        help='Pretty-print JSON output to console')

    args = parser.parse_args()

    if not args.tweet_id.isdigit():
        print("Error: Please enter a valid numeric tweet ID.")
        sys.exit(1)

    print(f"Downloading content for tweet ID: {args.tweet_id}")
    post = download_x_post(
        args.tweet_id,
        output_dir=args.output_dir,
        cookies=args.cookies,
        save_raw_response=args.save_raw
    )

    if post:
        if args.pretty:
            print("\nResulting JSON:")
            print(json.dumps(post.to_dict(), indent=2))
        else:
            print("Download completed successfully!")
    else:
        print("Failed to download post content.")
        sys.exit(1)


if __name__ == "__main__":
    main() 