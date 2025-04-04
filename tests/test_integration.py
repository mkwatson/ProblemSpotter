"""Integration tests for the ProblemSpotter script."""

import json
import os
import sys
from typing import Any, Optional
from unittest.mock import MagicMock, patch

from pytest import MonkeyPatch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fetch_problems import main


class TestIntegration:
    @patch.dict(
        os.environ,
        {
            "REDDIT_CLIENT_ID": "test_client_id",
            "REDDIT_CLIENT_SECRET": "test_client_secret",
        },
    )
    @patch("praw.Reddit")
    def test_end_to_end_flow(
        self, mock_reddit: MagicMock, tmp_path: Any, monkeypatch: MonkeyPatch
    ) -> None:
        """Test the full script execution with mocked Reddit API responses"""
        # Set up the output directory to a temporary path
        output_dir = tmp_path / "reddit_data"
        output_dir.mkdir()
        monkeypatch.setattr("fetch_problems.create_output_directory", lambda _path: None)

        # Mock the Reddit API responses
        mock_client = MagicMock()
        mock_reddit.return_value = mock_client
        mock_subreddit = MagicMock()
        mock_client.subreddit.return_value = mock_subreddit

        # Create mock posts
        mock_post1 = MagicMock()
        mock_post1.id = "post1"
        mock_post1.title = "How do I learn Python?"
        mock_post1.selftext = "I want to learn Python"
        mock_post1.author.name = "user1"
        mock_post1.created_utc = 1612345678.0
        mock_post1.subreddit.display_name = "learnprogramming"
        mock_post1.permalink = "/r/learnprogramming/comments/post1"
        mock_post1.url = "https://reddit.com/r/learnprogramming/comments/post1"
        mock_post1.score = 10
        mock_post1.over_18 = False

        mock_post2 = MagicMock()
        mock_post2.id = "post2"
        mock_post2.title = "How do I fix this error?"
        mock_post2.selftext = "I'm getting this error..."
        mock_post2.author.name = "user2"
        mock_post2.created_utc = 1612345679.0
        mock_post2.subreddit.display_name = "programming"
        mock_post2.permalink = "/r/programming/comments/post2"
        mock_post2.url = "https://reddit.com/r/programming/comments/post2"
        mock_post2.score = 5
        mock_post2.over_18 = False

        # Set the return value directly to the list of mock posts
        mock_subreddit.search.return_value = [mock_post1, mock_post2]

        # Mock the save function to capture the output
        saved_file_path = str(output_dir / "test_output.json")

        def mock_save_results(results: list[Any], out_dir: str, filename: str | None = None) -> str:
            posts_data: list[dict[str, Any]] = []
            for post in results:
                post_data = {
                    "id": post.id,
                    "title": post.title,
                    "selftext": post.selftext,
                    "author": post.author.name,
                    "created_utc": post.created_utc,
                    "subreddit": post.subreddit.display_name,
                    "permalink": post.permalink,
                    "url": post.url,
                    "score": post.score,
                    "over_18": post.over_18,
                }
                posts_data.append(post_data)

            with open(saved_file_path, "w", encoding="utf-8") as f:
                json.dump(posts_data, f)

            return saved_file_path

        monkeypatch.setattr("fetch_problems.save_search_results", mock_save_results)

        # Override the filename generation to use a fixed name
        monkeypatch.setattr("fetch_problems.generate_filename", lambda: "test_output.json")

        # Run the main function
        with patch("fetch_problems.create_output_directory", lambda _path: None):
            monkeypatch.setattr("fetch_problems.REDDIT_DATA_DIR", str(output_dir))
            main()

        # Verify that the search was performed correctly
        mock_client.subreddit.assert_called_once_with("all")
        mock_subreddit.search.assert_called_once_with("how do I", sort="new", limit=100)

        # Verify that the results were saved correctly
        assert os.path.exists(saved_file_path)

        with open(saved_file_path, encoding="utf-8") as f:
            saved_data = json.load(f)

        # Add a constant for the expected number of posts to avoid magic number warning
        expected_posts_count = 2
        assert len(saved_data) == expected_posts_count
        assert saved_data[0]["id"] == "post1"
        assert saved_data[0]["title"] == "How do I learn Python?"
        assert saved_data[1]["id"] == "post2"
        assert saved_data[1]["title"] == "How do I fix this error?"

    @patch.dict(
        os.environ,
        {
            "REDDIT_CLIENT_ID": "test_client_id",
            "REDDIT_CLIENT_SECRET": "test_client_secret",
        },
    )
    @patch("praw.Reddit")
    def test_empty_results(
        self, mock_reddit: MagicMock, tmp_path: Any, monkeypatch: MonkeyPatch
    ) -> None:
        """Test the script behavior when no results are found"""
        # Set up the output directory to a temporary path
        output_dir = tmp_path / "reddit_data"
        output_dir.mkdir()

        # Mock the Reddit API to return empty results
        mock_client = MagicMock()
        mock_reddit.return_value = mock_client
        mock_subreddit = MagicMock()
        mock_client.subreddit.return_value = mock_subreddit
        mock_subreddit.search.return_value = []

        # Mock the save function
        saved_file_path = str(output_dir / "test_output.json")

        def mock_save_results(results: list[Any], out_dir: str, filename: str | None = None) -> str:
            with open(saved_file_path, "w", encoding="utf-8") as f:
                json.dump([], f)
            return saved_file_path

        monkeypatch.setattr("fetch_problems.save_search_results", mock_save_results)
        monkeypatch.setattr("fetch_problems.generate_filename", lambda: "test_output.json")
        monkeypatch.setattr("fetch_problems.create_output_directory", lambda _path: None)
        monkeypatch.setattr("fetch_problems.REDDIT_DATA_DIR", str(output_dir))

        # Run the main function
        main()

        # Verify that the search was performed correctly
        mock_client.subreddit.assert_called_once_with("all")
        mock_subreddit.search.assert_called_once_with("how do I", sort="new", limit=100)

        # Verify that an empty result set was saved
        assert os.path.exists(saved_file_path)

        with open(saved_file_path, encoding="utf-8") as f:
            saved_data = json.load(f)

        assert len(saved_data) == 0
