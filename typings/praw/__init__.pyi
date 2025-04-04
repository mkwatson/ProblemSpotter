"""Type stubs for praw."""

from typing import Any, Dict, List, Optional, Union

class Reddit:
    """Reddit API client class."""

    def __init__(
        self, client_id: str, client_secret: str, user_agent: str, **kwargs: Any
    ) -> None: ...
    def subreddit(self, display_name: str) -> "Subreddit":
        """Return a Subreddit instance for the subreddit named display_name."""
        ...

class Subreddit:
    """A class for Subreddits."""

    display_name: str

    def search(
        self, query: str, sort: str = "relevance", limit: Optional[int] = None, **kwargs: Any
    ) -> List["Submission"]:
        """Search within a subreddit."""
        ...

class Submission:
    """A class for Reddit submissions."""

    id: str
    title: str
    selftext: str
    author: Union["Redditor", str]
    created_utc: float
    subreddit: Union["Subreddit", str]
    permalink: str
    url: str
    score: int
    over_18: bool

    def dict(self) -> Dict[str, Any]:
        """Return a dictionary of the submission's attributes."""
        ...

class Redditor:
    """A class for Redditor instances."""

    name: str
