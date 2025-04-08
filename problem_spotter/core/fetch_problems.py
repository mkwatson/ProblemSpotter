"""ProblemSpotter: Reddit 'how do I' question finder.

This script queries Reddit for posts containing "how do I" phrases and stores the
results. It uses the PRAW library to interact with Reddit's API and handles filtering
and data processing.
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, TypedDict

import praw
from dotenv import load_dotenv
from pydantic import BaseModel

# Constants
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# Base directory for all Reddit data
REDDIT_DATA_DIR = os.path.join(PROJECT_ROOT, "reddit_data")
OUTPUT_DIR = REDDIT_DATA_DIR  # New name for clarity
SEARCH_PHRASE = "how do I"
SEARCH_LIMIT = 100
SEARCH_SORT = "new"
REDDIT_USER_AGENT = "ProblemSpotter:v1.0 (by /u/YourUsername)"


# Type definitions
class RedditCredentials(TypedDict):
    """Reddit API credentials type definition."""

    client_id: str
    client_secret: str


class RedditPostOutput(BaseModel):
    """Schema for the JSON output of Reddit posts."""

    id: str
    title: str
    selftext: str
    author: str
    created_utc: float
    subreddit: str
    permalink: str
    url: str
    score: int
    over_18: bool


def load_env_vars() -> RedditCredentials:
    """Load environment variables for Reddit API.

    Returns:
        A dictionary containing the Reddit API client ID and secret.

    Raises:
        ValueError: If required environment variables are not set.
    """
    # Check if variables exist before loading dotenv
    if "REDDIT_CLIENT_ID" not in os.environ or "REDDIT_CLIENT_SECRET" not in os.environ:
        load_dotenv()

    # Check if variables exist after loading dotenv
    if "REDDIT_CLIENT_ID" not in os.environ:
        error_msg = "Required environment variable REDDIT_CLIENT_ID must be " "set in .env file"
        raise ValueError(error_msg)

    if "REDDIT_CLIENT_SECRET" not in os.environ:
        error_msg = "Required environment variable REDDIT_CLIENT_SECRET must be " "set in .env file"
        raise ValueError(error_msg)

    client_id = os.environ["REDDIT_CLIENT_ID"]
    client_secret = os.environ["REDDIT_CLIENT_SECRET"]

    if client_id == "" or client_secret == "":
        error_msg = (
            "Required environment variables REDDIT_CLIENT_ID and "
            "REDDIT_CLIENT_SECRET must not be empty"
        )
        raise ValueError(error_msg)

    return {"client_id": client_id, "client_secret": client_secret}


def initialize_reddit_client(credentials: RedditCredentials) -> praw.Reddit:
    """Initialize the Reddit API client.

    Args:
        credentials: A dictionary containing the Reddit API client ID
            and secret.

    Returns:
        An initialized PRAW Reddit instance.
    """
    # Create the Reddit client with the provided credentials
    reddit = praw.Reddit(
        client_id=credentials["client_id"],
        client_secret=credentials["client_secret"],
        user_agent=REDDIT_USER_AGENT,
    )

    # Store credentials as attributes for testing purposes
    reddit.client_id = credentials["client_id"]
    reddit.client_secret = credentials["client_secret"]
    reddit.user_agent = REDDIT_USER_AGENT

    return reddit


def search_reddit_posts(reddit: praw.Reddit, search_phrase: str) -> list[Any]:
    """Search Reddit for posts containing the specified phrase.

    Args:
        reddit: An initialized PRAW Reddit instance.
        search_phrase: The phrase to search for.

    Returns:
        A list of Reddit submissions matching the search criteria.
    """
    # Set up the search parameters
    subreddit = reddit.subreddit("all")

    # Perform the search
    posts = list(subreddit.search(search_phrase, sort=SEARCH_SORT, limit=SEARCH_LIMIT))

    # Filter out NSFW posts
    sfw_posts = [post for post in posts if not post.over_18]

    print(f"Found {len(posts)} posts, {len(sfw_posts)} SFW")
    return sfw_posts


def create_output_directory(directory_path: str) -> None:
    """Create the output directory if it doesn't exist.

    Args:
        directory_path: The path to the directory to create.
    """
    os.makedirs(directory_path, exist_ok=True)


def generate_filename() -> str:
    """Generate a timestamped filename for the output file.

    Returns:
        A string representing the filename with timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"reddit_how_do_i_results_{timestamp}.json"


def save_search_results(posts: list[Any], output_dir: str, filename: str | None = None) -> str:
    """Save the search results to a JSON file.

    Args:
        posts: A list of Reddit submissions.
        output_dir: The directory to save the output file to.
        filename: Optional filename to use instead of generating one.

    Returns:
        The path to the saved file.
    """
    # Create the output directory if it doesn't exist
    create_output_directory(output_dir)

    # Generate a filename if one wasn't provided
    if filename is None:
        filename = generate_filename()

    # Full path to the output file
    output_path = os.path.join(output_dir, filename)

    # Convert posts to our output format
    output_data: list[dict[str, Any]] = []
    for post in posts:
        # Handle both string and Redditor object for author
        author_name = (
            "[deleted]"
            if post.author is None
            else (post.author.name if hasattr(post.author, "name") else str(post.author))
        )

        # Handle both string and Subreddit object for subreddit
        subreddit_name = (
            post.subreddit.display_name
            if hasattr(post.subreddit, "display_name")
            else str(post.subreddit)
        )

        post_data = RedditPostOutput(
            id=post.id,
            title=post.title,
            selftext=post.selftext,
            author=author_name,
            created_utc=post.created_utc,
            subreddit=subreddit_name,
            permalink=post.permalink,
            url=post.url,
            score=post.score,
            over_18=post.over_18,
        )

        # Handle Pydantic v1 vs v2 differences with proper typing
        # Use the getattr pattern to avoid static type checker issues
        model_dump_method = getattr(post_data, "model_dump", None)
        if model_dump_method is not None:
            # Pydantic v2
            post_dict = model_dump_method()
        else:
            # Pydantic v1 - use dict() method
            post_dict = post_data.dict()

        # Add to output data - the dict is correctly typed by the framework
        output_data.append(post_dict)

    # Write the data to the file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    post_count = len(output_data)
    print(f"Saved {post_count} posts to {output_path}")
    return output_path


def main() -> int:
    """Main function to run the Reddit search.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        # Load environment variables
        credentials = load_env_vars()

        # Initialize the Reddit API client
        reddit = initialize_reddit_client(credentials)

        # Search for posts
        posts = search_reddit_posts(reddit, SEARCH_PHRASE)

        # Save the results
        save_search_results(posts, OUTPUT_DIR)

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
