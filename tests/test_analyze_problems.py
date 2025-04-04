"""Tests for the analyze_problems module."""

import json
from unittest.mock import MagicMock, patch

from analyze_problems import analyze_post, create_cache_key


class TestAnalyzeProblems:
    """Test cases for the analyze_problems module."""

    @patch("analyze_problems.get_cached_analysis")
    @patch("analyze_problems.save_to_cache")
    @patch("openai.chat.completions.create")
    def test_analyze_post(
        self, mock_create: MagicMock, mock_save_to_cache: MagicMock, mock_get_cached: MagicMock
    ) -> None:
        """Test the analyze_post function with mocked OpenAI API."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        mock_message.content = json.dumps(
            {
                "is_question": True,
                "confidence_score": 0.95,
                "category": "tech",
                "reasoning": "This is a genuine technical question asking for help.",
            }
        )
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_create.return_value = mock_response

        # Mock cache to return None (no cached result)
        mock_get_cached.return_value = None

        # Create a test post
        test_post = {
            "id": "test123",
            "title": "How do I fix my computer?",
            "selftext": "It keeps crashing when I try to run this program.",
            "author": "test_user",
            "created_utc": 1612345678.0,
            "subreddit": "techsupport",
            "permalink": "/r/techsupport/comments/test123",
            "url": "https://reddit.com/r/techsupport/comments/test123",
            "score": 10,
            "over_18": False,
        }

        # Call the function
        result = analyze_post(test_post)

        # Verify the result
        assert result.post_id == "test123"
        assert result.is_question is True
        assert result.confidence_score == 0.95
        assert result.category == "tech"
        assert "genuine technical question" in result.reasoning

        # Verify the API was called correctly
        mock_create.assert_called_once()
        _, kwargs = mock_create.call_args
        assert kwargs["model"] == "gpt-4o"
        assert len(kwargs["messages"]) == 2
        assert kwargs["temperature"] == 0.0
        assert kwargs["response_format"] == {"type": "json_object"}

        # Verify cache was attempted to be retrieved
        mock_get_cached.assert_called_once()

        # Verify result was cached
        mock_save_to_cache.assert_called_once()

    def test_create_cache_key(self) -> None:
        """Test the create_cache_key function."""
        # Test with a simple string
        test_content = "This is a test"
        key1 = create_cache_key(test_content)

        # Verify it's a valid MD5 hash (32 hex characters)
        assert len(key1) == 32
        assert all(c in "0123456789abcdef" for c in key1)

        # Test determinism (same input, same output)
        key2 = create_cache_key(test_content)
        assert key1 == key2

        # Test different input produces different output
        different_content = "This is a different test"
        key3 = create_cache_key(different_content)
        assert key1 != key3

    @patch("analyze_problems.get_cached_analysis")
    @patch("analyze_problems.save_to_cache")
    @patch("openai.chat.completions.create")
    def test_analyze_post_with_cache(
        self, mock_create: MagicMock, mock_save_to_cache: MagicMock, mock_get_cached: MagicMock
    ) -> None:
        """Test analyze_post function using cached results."""
        # Mock cached result
        cached_result = {
            "is_question": True,
            "confidence_score": 0.9,
            "category": "tech",
            "reasoning": "Cached reasoning",
        }
        mock_get_cached.return_value = cached_result

        # Create a test post
        test_post = {
            "id": "test123",
            "title": "How do I fix my computer?",
            "selftext": "It keeps crashing when I try to run this program.",
            "author": "test_user",
            "created_utc": 1612345678.0,
            "subreddit": "techsupport",
            "permalink": "/r/techsupport/comments/test123",
            "url": "https://reddit.com/r/techsupport/comments/test123",
            "score": 10,
            "over_18": False,
        }

        # Call the function
        result = analyze_post(test_post)

        # Verify the result uses cached data
        assert result.post_id == "test123"
        assert result.is_question is True
        assert result.confidence_score == 0.9
        assert result.category == "tech"
        assert result.reasoning == "Cached reasoning"

        # Verify the API was NOT called
        mock_create.assert_not_called()

        # Verify cache was checked
        mock_get_cached.assert_called_once()

        # Verify result was NOT cached again
        mock_save_to_cache.assert_not_called()

    @patch("analyze_problems.get_cached_analysis")
    @patch("analyze_problems.save_to_cache")
    @patch("openai.chat.completions.create")
    def test_analyze_post_api_error(
        self, mock_create: MagicMock, mock_save_to_cache: MagicMock, mock_get_cached: MagicMock
    ) -> None:
        """Test analyze_post function handling API errors."""
        # Mock API error
        mock_create.side_effect = Exception("API Error")

        # Mock cache to return None
        mock_get_cached.return_value = None

        # Create a test post
        test_post = {
            "id": "test123",
            "title": "How do I fix my computer?",
            "selftext": "It keeps crashing when I try to run this program.",
            "author": "test_user",
            "created_utc": 1612345678.0,
            "subreddit": "techsupport",
            "permalink": "/r/techsupport/comments/test123",
            "url": "https://reddit.com/r/techsupport/comments/test123",
            "score": 10,
            "over_18": False,
        }

        # Call the function
        result = analyze_post(test_post)

        # Verify the result has default values
        assert result.post_id == "test123"
        assert result.is_question is False
        assert result.confidence_score == 0.0
        assert result.category == ""
        assert "Error during analysis" in result.reasoning

        # Verify the API was called
        mock_create.assert_called_once()

        # Verify cache was checked
        mock_get_cached.assert_called_once()

        # Verify no result was cached (since there was an error)
        mock_save_to_cache.assert_not_called()
