"""
ProblemSpotter: A tool for fetching Reddit posts containing 'how do I' phrases

This script queries Reddit using PRAW for posts containing the phrase "how do I",
and stores the raw results in a JSON file.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Sequence, TypeVar, Union, cast

import praw  # type: ignore # No type stubs available for praw
from dotenv import load_dotenv
from pydantic import BaseModel

# Constants
REDDIT_DATA_DIR = "./reddit_data"
SEARCH_PHRASE = "how do I"
SEARCH_LIMIT = 100
SEARCH_SORT = "new"


# Type definitions to handle PRAW objects
class RedditAuthor(Protocol):
    name: str


class RedditSubreddit(Protocol):
    display_name: str


class RedditSubmission(Protocol):
    id: str
    title: str
    selftext: str
    author: Union[RedditAuthor, str]
    created_utc: float
    subreddit: Union[RedditSubreddit, str]
    permalink: str
    url: str
    score: int
    over_18: bool


# Generic type for BaseModel subclasses
T = TypeVar("T", bound=BaseModel)
PostType = TypeVar("PostType", bound=Union[RedditSubmission, BaseModel])


def load_env_vars() -> Dict[str, str]:
    """
    Load Reddit API credentials from environment variables.

    Returns:
        Dict containing client_id and client_secret

    Raises:
        ValueError: If required environment variables are missing
    """
    load_dotenv()

    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")

    # In our patched test environment, the variables might appear to exist but be None
    # This ensures we raise the error either if they don't exist or are empty
    if not client_id or not client_secret:
        raise ValueError(
            "Required environment variables REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set"
        )

    return {"client_id": client_id, "client_secret": client_secret}


def initialize_reddit_client(credentials: Dict[str, str]) -> praw.Reddit:
    """
    Initialize and return a Reddit API client.

    Args:
        credentials: Dictionary containing client_id and client_secret

    Returns:
        Initialized Reddit client
    """
    return praw.Reddit(
        client_id=credentials["client_id"],
        client_secret=credentials["client_secret"],
        user_agent="ProblemSpotter:v1.0 (by /u/YourUsername)",
    )


def search_reddit_posts(
    reddit: praw.Reddit, search_phrase: str
) -> List[RedditSubmission]:
    """
    Search Reddit for posts containing the given phrase.

    Args:
        reddit: Initialized Reddit client
        search_phrase: Phrase to search for

    Returns:
        List of Reddit submission objects matching the search criteria
    """
    # Search across all subreddits
    subreddit = reddit.subreddit("all")  # type: ignore

    # Get the most recent posts containing the search phrase
    # Using explicit cast to tell the type checker this is a list of RedditSubmission
    search_results = cast(
        List[RedditSubmission],
        list(
            subreddit.search(  # type: ignore
                search_phrase, sort=SEARCH_SORT, limit=SEARCH_LIMIT
            )
        ),
    )

    # Filter out NSFW content
    posts = [post for post in search_results if not post.over_18]

    return posts


def create_output_directory(directory_path: str) -> None:
    """
    Create the output directory if it doesn't exist.

    Args:
        directory_path: Path to the directory to create
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def generate_filename() -> str:
    """
    Generate a timestamped filename for the JSON output.

    Returns:
        Formatted filename with current timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"reddit_how_do_i_results_{timestamp}.json"


def save_search_results(
    results: Sequence[Union[RedditSubmission, BaseModel]],
    output_dir: str,
    filename: Optional[str] = None,
) -> str:
    """
    Save the search results to a JSON file.

    Args:
        results: List of Reddit submission objects or Pydantic models
        output_dir: Directory to save the results in
        filename: Optional filename to use (generates one if not provided)

    Returns:
        Path to the saved file
    """
    if filename is None:
        filename = generate_filename()

    # Ensure the output directory exists
    create_output_directory(output_dir)

    # Create the full path
    output_path = os.path.join(output_dir, filename)

    # Convert the objects to dictionaries
    posts_data: List[Dict[str, Any]] = []
    for post in results:
        if isinstance(post, BaseModel):
            # If it's a Pydantic model, use its built-in dict conversion
            post_data = post.dict()
        else:
            # Use a type variable to help with typing
            post_data = {}

            # Extract the fields with proper type handling
            # Using getattr with a default for safer attribute access
            post_data["id"] = getattr(post, "id", "")
            post_data["title"] = getattr(post, "title", "")
            post_data["selftext"] = getattr(post, "selftext", "")

            # Handle author field which could be a string or an object with a name property
            author = getattr(post, "author", "")
            if hasattr(author, "name"):
                post_data["author"] = author.name  # type: ignore
            else:
                post_data["author"] = author

            post_data["created_utc"] = getattr(post, "created_utc", 0.0)

            # Handle subreddit field which could be a string or an object
            # with a display_name property
            subreddit = getattr(post, "subreddit", "")
            if hasattr(subreddit, "display_name"):
                post_data["subreddit"] = subreddit.display_name  # type: ignore
            else:
                post_data["subreddit"] = subreddit

            post_data["permalink"] = getattr(post, "permalink", "")
            post_data["url"] = getattr(post, "url", "")
            post_data["score"] = getattr(post, "score", 0)
            post_data["over_18"] = getattr(post, "over_18", False)

        posts_data.append(post_data)

    # Write the data to the JSON file
    with open(output_path, "w") as f:
        json.dump(posts_data, f, indent=2)

    return output_path


def main() -> None:
    """Main entry point for the script."""
    try:
        # Load environment variables
        credentials = load_env_vars()

        # Initialize the Reddit client
        reddit = initialize_reddit_client(credentials)

        # Search for Reddit posts containing the phrase
        posts = search_reddit_posts(reddit, SEARCH_PHRASE)

        # Create the output directory if it doesn't exist
        create_output_directory(REDDIT_DATA_DIR)

        # Generate the filename
        filename = generate_filename()

        # Save the results to a JSON file
        output_path = save_search_results(posts, REDDIT_DATA_DIR, filename)

        print(f"Successfully saved {len(posts)} Reddit posts to {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
