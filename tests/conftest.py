"""
ProblemSpotter test configuration.

This module contains pytest fixtures and configuration for the test suite.
"""

import tempfile
from collections.abc import Iterator
from typing import Any

import pytest
from pytest import MonkeyPatch


# Mock PRAW data for testing
class MockRedditor:
    """Mock for PRAW Redditor class."""

    def __init__(self, name: str) -> None:
        self.name = name


class MockSubreddit:
    """Mock for PRAW Subreddit class."""

    def __init__(self, display_name: str) -> None:
        self.display_name = display_name

    def search(
        self, query: str, sort: str = "relevance", limit: int | None = None
    ) -> list["MockSubmission"]:
        """Mock search method."""
        # This would be populated with test data in fixtures
        return []


class MockSubmission:
    """Mock for PRAW Submission class."""

    def __init__(
        self,
        id: str,
        title: str,
        selftext: str,
        author: Any,
        created_utc: float,
        subreddit: Any,
        permalink: str,
        url: str,
        score: int,
        over_18: bool,
    ) -> None:
        self.id = id
        self.title = title
        self.selftext = selftext
        self.author = author
        self.created_utc = created_utc
        self.subreddit = subreddit
        self.permalink = permalink
        self.url = url
        self.score = score
        self.over_18 = over_18


class MockReddit:
    """Mock for PRAW Reddit class."""

    def __init__(self, client_id: str, client_secret: str, user_agent: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        # This will be populated with mock test data
        self._mock_data: list[MockSubmission] = []

    def set_mock_data(self, data: list[MockSubmission]) -> None:
        """Set mock data for testing."""
        self._mock_data = data

    def subreddit(self, display_name: str) -> MockSubreddit:
        """Mock subreddit method."""
        mock_subreddit = MockSubreddit(display_name)

        # Create the search method function
        def mock_search(
            query: str, sort: str = "relevance", limit: int | None = None
        ) -> list[MockSubmission]:
            return self._mock_data[:limit] if limit else self._mock_data

        # Directly assign the method to the MockSubreddit instance without type: ignore
        # We're intentionally overriding the search method for testing purposes
        # mypy doesn't like assigning to methods, but this is our test mock setup
        mock_subreddit.search = mock_search  # type: ignore[method-assign]
        return mock_subreddit


@pytest.fixture  # type: ignore[misc]
def mock_reddit() -> MockReddit:
    """Fixture providing a mock Reddit instance."""
    return MockReddit(
        client_id="mock_client_id",
        client_secret="mock_client_secret",  # This is a test password, not a real secret
        user_agent="MockAgent",
    )


@pytest.fixture  # type: ignore[misc]
def mock_reddit_with_data(mock_reddit: MockReddit) -> MockReddit:
    """Fixture providing a mock Reddit instance with sample data."""
    # Create mock data
    mock_data = [
        MockSubmission(
            id=f"post{i}",
            title=f"How do I learn Python? {i}",
            selftext=f"I want to learn Python programming. {i}",
            author=MockRedditor(f"user{i}"),
            created_utc=1612345678.0 + i,
            subreddit=MockSubreddit(f"subreddit{i}"),
            permalink=f"/r/subreddit{i}/comments/post{i}/title{i}",
            url=f"https://reddit.com/r/subreddit{i}/comments/post{i}/title{i}",
            score=10 + i,
            over_18=i % 5 == 0,  # Every 5th post is NSFW
        )
        for i in range(10)
    ]
    mock_reddit.set_mock_data(mock_data)
    return mock_reddit


@pytest.fixture  # type: ignore[misc]
def temp_output_dir() -> Iterator[str]:
    """Fixture providing a temporary directory for output files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture  # type: ignore[misc]
def mock_env_vars(monkeypatch: MonkeyPatch) -> None:
    """Fixture to set mock environment variables."""
    monkeypatch.setenv("REDDIT_CLIENT_ID", "mock_client_id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "mock_client_secret")
