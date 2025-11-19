#!/usr/bin/env python
"""
Example script demonstrating the Markdown generation feature with metadata.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from xtract import download_x_post, post_to_markdown, save_post_as_markdown


def main():
    """Main function to demonstrate Markdown generation."""
    # You can use any post ID or URL
    tweet_id = "1895573480835539451"  # Example post ID

    print(f"Downloading post {tweet_id}...")
    post = download_x_post(tweet_id)

    if post:
        print("Post downloaded successfully!")

        # Generate markdown string with metadata
        markdown = post_to_markdown(post, include_metadata=True)

        # Print the markdown content
        print("\nMarkdown Content (with metadata):")
        print("-" * 40)

        # Print just the first 15 lines to show metadata
        lines = markdown.split("\n")
        print("\n".join(lines[:15]))
        print("...")
        print("-" * 40)

        # Generate markdown string without metadata
        markdown_no_meta = post_to_markdown(post, include_metadata=False)

        # Print the markdown content without metadata
        print("\nMarkdown Content (without metadata):")
        print("-" * 40)

        # Print just the first 5 lines
        lines = markdown_no_meta.split("\n")
        print("\n".join(lines[:5]))
        print("...")
        print("-" * 40)

        # Save to files
        output_dir = "markdown_output"

        # Save with metadata
        file_path = save_post_as_markdown(post, output_dir=output_dir)
        print(f"\nComplete markdown with metadata saved to: {file_path}")

        # Save without metadata
        without_meta_filename = f"tweet_{post.tweet_id}_no_meta.md"

        # Create a custom version without metadata and save it
        file_path_no_meta = os.path.join(output_dir, without_meta_filename)
        os.makedirs(output_dir, exist_ok=True)

        with open(file_path_no_meta, "w", encoding="utf-8") as f:
            f.write(markdown_no_meta)

        print(f"Markdown without metadata saved to: {file_path_no_meta}")
        print("\nUse a text editor or markdown viewer to see the full content")
    else:
        print("Failed to download post.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
