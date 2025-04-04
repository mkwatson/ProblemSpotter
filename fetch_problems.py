"""
ProblemSpotter: A tool for fetching Reddit posts containing 'how do I' phrases

This module is the core of the ProblemSpotter project, responsible for:

1. Connecting to the Reddit API using PRAW
2. Searching for posts containing "how do I" phrases
3. Storing the results in a structured JSON format
4. Filtering out inappropriate content (NSFW)

It operates as a standalone script that can be run directly. When executed,
it fetches up to 100 of the most recent posts matching the search criteria and
saves them to a timestamped file in the './reddit_data/' directory.

Usage:
    $ python fetch_problems.py

Requirements:
    - Reddit API credentials in environment variables (or .env file):
        - REDDIT_CLIENT_ID
        - REDDIT_CLIENT_SECRET
    - Python packages:
        - praw
        - python-dotenv
        - pydantic

Created with strict type checking in mind, using Protocol classes to define
interfaces for the PRAW objects we interact with.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Sequence, TypeVar, Union, cast

import praw
from dotenv import load_dotenv
from pydantic import BaseModel

# Constants
REDDIT_DATA_DIR = "./reddit_data"
SEARCH_PHRASE = "how do I"
SEARCH_LIMIT = 100
SEARCH_SORT = "new"


# Type definitions to handle PRAW objects
class RedditAuthor(Protocol):
    """
    Protocol defining the expected interface for a Reddit author.

    This protocol declares the minimal required structure that a Reddit author
    object must implement for our code to work with it. The actual PRAW
    implementation may have more fields and methods, but this is what we need.

    Attributes:
        name: The username of the Reddit author
    """

    name: str


class RedditSubreddit(Protocol):
    """
    Protocol defining the expected interface for a Reddit subreddit.

    This protocol defines the minimal structure required from a subreddit
    object for our code to work with it. The actual PRAW implementation may
    have more fields and methods, but this is what we need.

    Attributes:
        display_name: The name of the subreddit without the "r/" prefix
    """

    display_name: str


class RedditSubmission(Protocol):
    """
    Protocol defining the expected interface for a Reddit submission (post).

    This protocol defines all the properties we need to extract from a
    Reddit post. Using a Protocol allows us to work with PRAW's objects
    without needing to implement all their complexity, just the parts
    we need to use.

    Attributes:
        id: The unique identifier of the post
        title: The title of the post
        selftext: The body text content of the post
        author: Either a RedditAuthor object or a string with the author's name
        created_utc: Unix timestamp (float) when the post was created
        subreddit: Either a RedditSubreddit object or a string with the subreddit name
        permalink: The path portion of the URL (without domain) to the post
        url: The full URL to the post
        score: The net upvote count of the post
        over_18: Boolean indicating whether the post is marked as NSFW (Not Safe For Work)
    """

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


"""
Type Variables Explanation:

T:
    A type variable bound to BaseModel. This allows us to create generic functions
    that work with any Pydantic model while maintaining type safety.

PostType:
    A type variable that can represent either a RedditSubmission Protocol or a BaseModel.
    This helps us handle both raw Reddit API responses and our own model objects
    in a type-safe way.
"""


def load_env_vars() -> Dict[str, str]:
    """
    Load Reddit API credentials from environment variables.

    This function reads the REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET from
    environment variables set in a .env file. It verifies that both variables
    exist and are not empty.

    Returns:
        Dict containing client_id and client_secret keys with their values

    Raises:
        ValueError: If required environment variables are missing or empty
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

    Creates a PRAW Reddit client instance using the provided credentials.
    This client is configured for read-only access (no login required)
    and identifies itself with a custom user agent.

    Args:
        credentials: Dictionary containing client_id and client_secret keys

    Returns:
        Initialized Reddit client ready to make API requests
    """
    return praw.Reddit(
        client_id=credentials["client_id"],
        client_secret=credentials["client_secret"],
        user_agent="ProblemSpotter:v1.0 (by /u/YourUsername)",
    )


def search_reddit_posts(reddit: praw.Reddit, search_phrase: str) -> List[RedditSubmission]:
    """
    Search Reddit for posts containing the given phrase.

    Uses the Reddit API to search all subreddits for posts containing the specified
    search phrase. The search results are sorted by newest first and limited to a
    maximum number defined by SEARCH_LIMIT. NSFW content is filtered out.

    Args:
        reddit: Initialized Reddit client from initialize_reddit_client()
        search_phrase: The text phrase to search for in Reddit posts

    Returns:
        List of Reddit submission objects matching the search criteria with NSFW content removed
    """
    # Search across all subreddits
    subreddit = reddit.subreddit("all")

    # Get the most recent posts containing the search phrase
    # Using explicit cast to tell the type checker this is a list of RedditSubmission
    search_results = cast(
        List[RedditSubmission],
        list(subreddit.search(search_phrase, sort=SEARCH_SORT, limit=SEARCH_LIMIT)),
    )

    # Filter out NSFW content
    posts = [post for post in search_results if not post.over_18]

    return posts


def create_output_directory(directory_path: str) -> None:
    """
    Create the output directory if it doesn't exist.

    This is a helper function that ensures the specified directory exists,
    creating it and any necessary parent directories if they don't.

    Args:
        directory_path: Path to the directory to create
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def generate_filename() -> str:
    """
    Generate a timestamped filename for the JSON output.

    Creates a standardized filename with the current date and time appended
    to make each file unique. Format follows the pattern:
    "reddit_how_do_i_results_YYYYMMDD_HHMMSS.json"

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

    Converts Reddit submission objects or Pydantic models to a JSON-serializable
    format and saves them to a file. Handles both Pydantic models (which have
    a built-in dict conversion) and Reddit PRAW objects (which require attribute
    extraction).

    Args:
        results: List of Reddit submission objects or Pydantic models
        output_dir: Directory to save the results in
        filename: Optional custom filename to use (generates one if not provided)

    Returns:
        Absolute path to the saved file
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
            # Check if author is a Redditor object with a name attribute
            if isinstance(author, str):
                post_data["author"] = author
            else:
                # It's a Redditor object, access the name attribute
                post_data["author"] = getattr(author, "name", "")

            post_data["created_utc"] = getattr(post, "created_utc", 0.0)

            # Handle subreddit field which could be a string or an object
            # with a display_name property
            subreddit = getattr(post, "subreddit", "")
            # Check if subreddit is a Subreddit object with a display_name attribute
            if isinstance(subreddit, str):
                post_data["subreddit"] = subreddit
            else:
                # It's a Subreddit object, access the display_name attribute
                post_data["subreddit"] = getattr(subreddit, "display_name", "")

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
    """
    Main entry point for the script.

    Coordinates the full workflow:
    1. Loads environment variables for Reddit API credentials
    2. Initializes the Reddit client
    3. Searches for posts containing the search phrase
    4. Creates the output directory if needed
    5. Saves the results to a JSON file

    Handles exceptions by printing an error message and re-raising
    to maintain the stack trace.
    """
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
