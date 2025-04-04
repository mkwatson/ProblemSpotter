"""
Tests for the fetch_problems module.

This module contains tests for the ProblemSpotter's main functionality.
"""

import json
import os
from typing import Any

import pytest

from fetch_problems import (
    RedditCredentials,
    create_output_directory,
    generate_filename,
    initialize_reddit_client,
    load_env_vars,
    save_search_results,
    search_reddit_posts,
)


def test_load_env_vars(mock_env_vars: Any) -> None:
    """Test loading environment variables."""
    # Act
    credentials = load_env_vars()

    # Assert
    assert credentials["client_id"] == "mock_client_id"
    assert credentials["client_secret"] == "mock_client_secret"


def test_initialize_reddit_client() -> None:
    """Test initializing the Reddit client."""
    # Arrange
    # Use type annotation to satisfy typing - this is an example password for tests only
    credentials: RedditCredentials = {"client_id": "test_id", "client_secret": "test_secret"}

    # Act
    reddit = initialize_reddit_client(credentials)

    # Assert - using direct attribute access (attributes added in the function for testing)
    assert reddit.client_id == "test_id"
    assert reddit.client_secret == "test_secret"
    assert "ProblemSpotter" in reddit.user_agent


def test_search_reddit_posts(mock_reddit_with_data: Any) -> None:
    """Test searching Reddit posts."""
    # Arrange
    search_phrase = "how do I"

    # Act
    posts = search_reddit_posts(mock_reddit_with_data, search_phrase)

    # Assert
    # We expect 8 posts because 2 of the 10 mock posts are marked as NSFW
    expected_count = 8
    assert len(posts) == expected_count
    for post in posts:
        assert not post.over_18
        assert "How do I" in post.title


def test_create_output_directory(temp_output_dir: str) -> None:
    """Test creating the output directory."""
    # Arrange
    test_dir = os.path.join(temp_output_dir, "test_dir")

    # Act
    create_output_directory(test_dir)

    # Assert
    assert os.path.exists(test_dir)
    assert os.path.isdir(test_dir)


def test_generate_filename() -> None:
    """Test generating a filename with timestamp."""
    # Act
    filename = generate_filename()

    # Assert
    assert filename.startswith("reddit_how_do_i_results_")
    assert filename.endswith(".json")
    # Format: reddit_how_do_i_results_YYYYMMDD_HHMMSS.json
    assert len(filename) == len("reddit_how_do_i_results_YYYYMMDD_HHMMSS.json")


def test_save_search_results(mock_reddit_with_data: Any, temp_output_dir: str) -> None:
    """Test saving search results to a JSON file."""
    # Arrange
    search_phrase = "how do I"
    posts = search_reddit_posts(mock_reddit_with_data, search_phrase)
    filename = "test_results.json"

    # Act
    output_path = save_search_results(posts, temp_output_dir, filename)

    # Assert
    assert os.path.exists(output_path)

    # Verify the content
    with open(output_path, encoding="utf-8") as f:
        data: list[dict[str, Any]] = json.load(f)

    assert isinstance(data, list)
    expected_count = 8  # 8 non-NSFW posts
    assert len(data) == expected_count

    # Check each post has the expected fields
    for post_data in data:
        assert isinstance(post_data, dict)
        assert "id" in post_data
        assert "title" in post_data
        assert "selftext" in post_data
        assert "author" in post_data
        assert "subreddit" in post_data
