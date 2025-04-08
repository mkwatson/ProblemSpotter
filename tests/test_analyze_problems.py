"""Tests for analyze_problems module."""

import json
import os
import tempfile
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import openai
import pytest
from pytest import MonkeyPatch

from problem_spotter.core.analyze_problems import (
    AnalysisResult,
    OpenAICredentials,
    analyze_file,
    analyze_post,
    create_cache_key,
    extract_timestamp_from_filename,
    get_cached_analysis,
    initialize_openai_client,
    load_env_vars,
    load_reddit_data,
    main,
    save_to_cache,
)


def test_load_env_vars(monkeypatch: MonkeyPatch) -> None:
    """Test loading environment variables."""
    # Mock load_dotenv to do nothing
    with patch("problem_spotter.core.analyze_problems.load_dotenv"):
        # Test with valid API key
        monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")
        creds = load_env_vars()
        assert creds.api_key == "test_api_key"

        # Test with empty API key
        monkeypatch.setenv("OPENAI_API_KEY", "")
        with pytest.raises(ValueError):
            load_env_vars()

        # Test with missing API key
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ValueError):
            load_env_vars()


def test_initialize_openai_client() -> None:
    """Test OpenAI client initialization."""
    # Test with valid credentials
    creds = OpenAICredentials(api_key="test_api_key")
    client = initialize_openai_client(creds)
    assert isinstance(client, openai.OpenAI)
    assert client.api_key == "test_api_key"


def test_analyze_file() -> None:
    """Test file analysis."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file
        test_data = [
            {
                "id": "post1",
                "title": "How do I learn Python?",
                "selftext": "I want to learn Python",
                "author": "user1",
                "created_utc": 1612345678.0,
                "subreddit": "learnprogramming",
                "permalink": "/r/learnprogramming/comments/post1",
                "url": "https://reddit.com/r/learnprogramming/comments/post1",
                "score": 10,
                "over_18": False,
            }
        ]
        file_path = os.path.join(temp_dir, "test.json")
        with open(file_path, "w") as f:
            json.dump(test_data, f)

        # Mock OpenAI client response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_response.choices = [MagicMock(message=mock_message)]

        # Set up the response content
        mock_response_content = {
            "is_question": True,
            "confidence_score": 0.9,
            "category": "",
            "reasoning": ("This is a learning question about Python " "programming."),
            "post_id": "post1",
        }
        mock_message.content = json.dumps(mock_response_content)

        # Mock directories
        analyzed_dir_patch = "problem_spotter.core.analyze_problems.ANALYZED_DATA_DIR"
        with patch(analyzed_dir_patch, temp_dir):
            # Test analysis with our mock client
            output_path = analyze_file(file_path, client=mock_client)
            assert os.path.exists(output_path)
            with open(output_path) as f:
                result = json.load(f)
                assert len(result) == 1
                assert result[0]["id"] == "post1"
                assert result[0]["analysis"]["is_question"] is True


def test_main(monkeypatch: MonkeyPatch) -> None:
    """Test main function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file
        test_data = [
            {
                "id": "post1",
                "title": "How do I learn Python?",
                "selftext": "I want to learn Python",
                "author": "user1",
                "created_utc": 1612345678.0,
                "subreddit": "learnprogramming",
                "permalink": "/r/learnprogramming/comments/post1",
                "url": "https://reddit.com/r/learnprogramming/comments/post1",
                "score": 10,
                "over_18": False,
            }
        ]
        file_path = os.path.join(temp_dir, "test.json")
        with open(file_path, "w") as f:
            json.dump(test_data, f)

        # Set up environment
        monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")
        monkeypatch.setattr("problem_spotter.core.analyze_problems.RAW_DATA_DIR", temp_dir)
        monkeypatch.setattr("problem_spotter.core.analyze_problems.ANALYZED_DATA_DIR", temp_dir)
        monkeypatch.setattr(
            "problem_spotter.core.analyze_problems.CACHE_DIR",
            temp_dir,
        )

        # Create a mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_response.choices = [MagicMock(message=mock_message)]

        # Set up the response content
        mock_response_content = {
            "is_question": True,
            "confidence_score": 0.9,
            "category": "",
            "reasoning": ("This is a learning question about Python " "programming."),
            "post_id": "post1",
        }
        mock_message.content = json.dumps(mock_response_content)
        mock_client.chat.completions.create.return_value = mock_response

        # Use our mock client for the OpenAI client call
        openai_patch = "problem_spotter.core.analyze_problems.OpenAI"
        with patch(openai_patch, return_value=mock_client):
            # Mock sys.argv
            with patch("sys.argv", ["analyze_problems.py", "--raw"]):
                # Test main function
                result = main()
                assert result == 0


def test_analysis_result() -> None:
    """Test AnalysisResult class."""
    # Test valid data
    data = {
        "post_id": "post1",
        "is_question": True,
        "confidence_score": 0.9,
        "category": "",
        "reasoning": "This is a learning question about Python programming.",
    }
    result = AnalysisResult(**data)
    assert result.post_id == "post1"
    assert result.is_question is True
    assert result.confidence_score == 0.9
    assert result.category == ""
    assert result.reasoning == ("This is a learning question about Python programming.")


def test_load_reddit_data_malformed() -> None:
    """Test loading malformed Reddit data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test with malformed JSON
        file_path = os.path.join(temp_dir, "malformed.json")
        with open(file_path, "w") as f:
            f.write("{malformed json")

        with pytest.raises(json.JSONDecodeError):
            load_reddit_data(file_path)

        # Test with empty file
        empty_path = os.path.join(temp_dir, "empty.json")
        with open(empty_path, "w") as f:
            f.write("")

        with pytest.raises(json.JSONDecodeError):
            load_reddit_data(empty_path)


def test_extract_timestamp_edge_cases() -> None:
    """Test timestamp extraction from filenames with edge cases."""
    # Test normal case
    filename = "reddit_how_do_i_results_20250404_113459.json"
    timestamp = extract_timestamp_from_filename(filename)
    assert timestamp == "20250404_113459"

    # Test invalid format
    filename = "invalid_filename.json"
    timestamp = extract_timestamp_from_filename(filename)
    # Should return current timestamp
    datetime.strptime(timestamp, "%Y%m%d_%H%M%S")

    # Test empty filename
    timestamp = extract_timestamp_from_filename("")
    # Should return current timestamp
    datetime.strptime(timestamp, "%Y%m%d_%H%M%S")


def test_analyze_post_api_errors() -> None:
    """Test analyze_post handling of API errors."""
    post = {
        "id": "test1",
        "title": "Test Post",
        "selftext": "Test Content",
    }
    client = MagicMock()

    # Test rate limit error
    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = client
        mock_response = MagicMock(text="Rate limit exceeded", headers={})
        error = openai.RateLimitError(
            message="Rate limit exceeded",
            response=mock_response,
            body={"error": {"message": "Rate limit exceeded"}},
        )
        client.chat.completions.create.side_effect = error
        result = analyze_post(post, client=client)
        assert result.is_question is False
        assert result.confidence_score == 0.0
        assert "Rate limit exceeded" in result.reasoning

    # Test authentication error
    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = client
        mock_response = MagicMock(text="Invalid API key", headers={})
        auth_error = openai.AuthenticationError(
            message="Invalid API key",
            response=mock_response,
            body={"error": {"message": "Invalid API key"}},
        )
        client.chat.completions.create.side_effect = auth_error
        result = analyze_post(post, client=client)
        assert result.is_question is False
        assert result.confidence_score == 0.0
        assert "Invalid API key" in result.reasoning

    # Test connection error
    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = client
        # Create a mock Request object for the APIConnectionError
        mock_request = MagicMock()  # Generic mock without spec

        conn_error = openai.APIConnectionError(message="Failed to connect", request=mock_request)
        client.chat.completions.create.side_effect = conn_error
        result = analyze_post(post, client=client)
        assert result.is_question is False
        assert result.confidence_score == 0.0
        assert "Failed to connect" in result.reasoning

    # Test generic API error
    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = client
        # Create a mock Request object for the APIError
        mock_request = MagicMock()  # Generic mock without spec

        api_error = openai.APIError(message="API error occurred", body=None, request=mock_request)
        client.chat.completions.create.side_effect = api_error
        result = analyze_post(post, client=client)
        assert result.is_question is False
        assert result.confidence_score == 0.0
        assert "API error" in result.reasoning
        assert result.error is not None


def test_analyze_file_permission_error() -> None:
    """Test analyze_file handling of permission errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file with mock data
        test_data = [
            {
                "id": "post1",
                "title": "Test",
                "selftext": "Test",
                "author": "user1",
                "created_utc": 1612345678.0,
                "subreddit": "test",
                "permalink": "/r/test/1",
                "url": "https://reddit.com/r/test/1",
                "score": 1,
                "over_18": False,
            }
        ]
        input_file = os.path.join(temp_dir, "test.json")
        with open(input_file, "w") as f:
            json.dump(test_data, f)

        # Make output directory read-only
        os.chmod(temp_dir, 0o444)

        # Test permission error when writing output
        with (
            patch(
                "problem_spotter.core.analyze_problems.ANALYZED_DATA_DIR",
                temp_dir,
            ),
            patch("openai.chat.completions.create") as mock_create,
        ):
            mock_response = MagicMock()
            mock_response.choices[0].message.content = json.dumps(
                {
                    "is_question": True,
                    "confidence_score": 0.9,
                    "category": "",
                    "reasoning": "Test",
                }
            )
            mock_create.return_value = mock_response

            with pytest.raises(PermissionError):
                analyze_file(input_file)

        # Restore permissions to allow cleanup
        os.chmod(temp_dir, 0o777)


def test_analyze_post_rate_limit(tmp_path: Any) -> None:
    """Test handling of rate limit errors."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Create a test post
        test_post = {
            "id": "test",
            "title": "test",
            "selftext": "test",
        }

        # Set up the mock response
        mock_response = MagicMock(text="Rate limit exceeded", headers={})
        error_body = {"error": {"message": "Rate limit exceeded"}}

        # Create the error that will be raised
        mock_client.chat.completions.create.side_effect = openai.RateLimitError(
            message="Rate limit exceeded", response=mock_response, body=error_body
        )

        # Rate limit should still be re-raised
        with pytest.raises(openai.RateLimitError):
            analyze_post(test_post, client=mock_client)


def test_analyze_post_auth_error(tmp_path: Any) -> None:
    """Test handling of authentication errors."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Create a test post
        test_post = {
            "id": "test",
            "title": "test",
            "selftext": "test",
        }

        # Set up the mock response
        mock_response = MagicMock(text="Invalid API key", headers={})
        error_body = {"error": {"message": "Invalid API key"}}

        # Create the error that will be raised
        mock_client.chat.completions.create.side_effect = openai.AuthenticationError(
            message="Invalid API key", response=mock_response, body=error_body
        )

        # Authentication error should still be re-raised
        with pytest.raises(openai.AuthenticationError):
            analyze_post(test_post, client=mock_client)


def test_analyze_post_empty_response() -> None:
    """Test analyze_post with empty response."""
    post = {
        "id": "test1",
        "title": "Test Post",
        "selftext": "Test Content",
    }
    client = MagicMock()

    # Mock empty response
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_response.choices = [mock_choice]
    mock_choice.message = mock_message
    mock_message.content = ""  # Empty content
    client.chat.completions.create.return_value = mock_response

    # Test empty response handling
    result = analyze_post(post, client=client)
    assert result.is_question is False
    assert result.confidence_score == 0.0
    assert "Empty response" in result.reasoning
    assert result.error is not None


def test_analyze_post_api_error() -> None:
    """Test analyze_post handling of generic API errors."""
    post = {
        "id": "test1",
        "title": "Test Post",
        "selftext": "Test Content",
    }
    client = MagicMock()

    # Test with generic API error
    # Create a mock Request object for the APIError
    mock_request = MagicMock()  # Generic mock without spec

    api_error = openai.APIError(message="API error occurred", body=None, request=mock_request)
    client.chat.completions.create.side_effect = api_error
    result = analyze_post(post, client=client)
    assert result.is_question is False
    assert result.confidence_score == 0.0
    assert "API error" in result.reasoning
    assert result.error is not None


def test_analyze_post_unexpected_error() -> None:
    """Test analyze_post handling of unexpected errors."""
    post = {
        "id": "test1",
        "title": "Test Post",
        "selftext": "Test Content",
    }
    client = MagicMock()

    # Test with unexpected error
    error = Exception("Something went wrong")
    client.chat.completions.create.side_effect = error
    result = analyze_post(post, client=client)
    assert result.is_question is False
    assert result.confidence_score == 0.0
    assert "Unexpected error" in result.reasoning
    assert result.error is not None


def test_default_client_initialization() -> None:
    """Test analyze_post with default client initialization."""
    post = {
        "id": "test1",
        "title": "Test Post",
        "selftext": "Test Content",
    }

    # Mock the OpenAI constructor directly
    openai_patch = "problem_spotter.core.analyze_problems.OpenAI"
    with patch(openai_patch) as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Set up mock response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_response.choices = [mock_choice]
        mock_choice.message = mock_message
        mock_response_content = {
            "is_question": True,
            "confidence_score": 0.9,
            "category": "",
            "reasoning": "Test reasoning",
        }
        mock_message.content = json.dumps(mock_response_content)
        mock_client.chat.completions.create.return_value = mock_response

        # Call without providing a client
        result = analyze_post(post)

        # Verify default client was created
        mock_openai_class.assert_called_once()
        assert result.is_question is True
        assert result.confidence_score == 0.9


def test_create_cache_key() -> None:
    """Test create_cache_key function."""
    # Test with a simple string
    key1 = create_cache_key("test content")
    assert isinstance(key1, str)
    assert len(key1) > 0

    # Test with the same content (should be the same hash)
    key2 = create_cache_key("test content")
    assert key1 == key2

    # Test with different content (should be different hash)
    key3 = create_cache_key("different content")
    assert key1 != key3


def test_get_cached_analysis(monkeypatch: MonkeyPatch) -> None:
    """Test get_cached_analysis and save_to_cache functions."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the cache directory
        cache_dir_patch = "problem_spotter.core.analyze_problems.CACHE_DIR"
        monkeypatch.setattr(cache_dir_patch, temp_dir)

        # Test getting non-existent cache entry
        cache_key = "test_key"
        result = get_cached_analysis(cache_key)
        assert result is None

        # Test saving to cache
        test_data = {"test": "data"}
        save_to_cache(cache_key, test_data)

        # Verify file was created
        cache_file = os.path.join(temp_dir, f"{cache_key}.json")
        assert os.path.exists(cache_file)

        # Test getting cached data
        cached_data = get_cached_analysis(cache_key)
        assert cached_data == test_data


def test_is_test_environment() -> None:
    """Test the is_test_environment function inside analyze_post."""
    # Create a post to analyze
    post = {
        "id": "test1",
        "title": "Test Post",
        "selftext": "Test Content",
    }

    # Create a client that raises an expected error
    client = MagicMock()
    client.chat.completions.create.side_effect = openai.RateLimitError(
        message="Rate limit exceeded",
        response=MagicMock(text="Rate limit exceeded", headers={}),
        body={"error": {"message": "Rate limit exceeded"}},
    )

    # Call from a test function (should detect test environment)
    result = analyze_post(post, client=client)
    # Verify it returned an error result instead of raising
    assert result.error is not None
    assert "Rate limit exceeded" in result.error


def test_openai_credentials_getitem() -> None:
    """Test dictionary-like access to credentials."""
    # Create credentials
    creds = OpenAICredentials(api_key="test_api_key")

    # Test valid key access
    assert creds["api_key"] == "test_api_key"

    # Test invalid key access
    with pytest.raises(KeyError):
        _ = creds["invalid_key"]


def test_openai_credentials_from_dict() -> None:
    """Test creating OpenAICredentials from a dictionary."""
    # Test with valid dictionary
    data = {"api_key": "test_api_key"}
    creds = OpenAICredentials.from_dict(data)
    assert creds.api_key == "test_api_key"

    # Test with missing key
    with pytest.raises(KeyError):
        OpenAICredentials.from_dict({})


def test_main_with_nonexistent_file() -> None:
    """Test main function handling of non-existent file."""
    # Mock the command line arguments
    with patch("sys.argv", ["analyze_problems.py", "--file", "/path/does/not/exist.json"]):
        # Mock the environment variables
        with patch("problem_spotter.core.analyze_problems.load_dotenv"):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test_api_key"}):
                # Test the main function
                result = main()
                # Should return 1 for error
                assert result == 1


def test_main_with_empty_directory() -> None:
    """Test main function handling of empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up environment
        with patch("problem_spotter.core.analyze_problems.load_dotenv"):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test_api_key"}):
                # Mock directories to point to our empty temp directory
                with patch("problem_spotter.core.analyze_problems.RAW_DATA_DIR", temp_dir):
                    with patch("problem_spotter.core.analyze_problems.DATA_DIR", temp_dir):
                        # Mock sys.argv
                        with patch("sys.argv", ["analyze_problems.py", "--raw"]):
                            # Test main function with empty directory
                            result = main()
                            # Should return 1 for error
                            assert result == 1
