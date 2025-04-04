import os
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Import the module we'll build (doesn't exist yet)
# This will fail initially, as expected in TDD
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fetch_problems import (
    load_env_vars,
    initialize_reddit_client,
    search_reddit_posts,
    save_search_results,
    create_output_directory,
    generate_filename
)

# Define expected schema using Pydantic for validation
class RedditPost(BaseModel):
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

class RedditSearchResults(BaseModel):
    posts: List[RedditPost]
    query_time: str
    search_phrase: str

# Test Environment Variables
class TestConfiguration:
    
    @patch.dict(os.environ, {"REDDIT_CLIENT_ID": "test_client_id", "REDDIT_CLIENT_SECRET": "test_client_secret"})
    def test_load_env_vars_success(self):
        """Test that environment variables are correctly loaded"""
        credentials = load_env_vars()
        assert credentials["client_id"] == "test_client_id"
        assert credentials["client_secret"] == "test_client_secret"
    
    @patch("fetch_problems.os.environ.get", return_value=None)
    def test_load_env_vars_missing(self, mock_env_get):
        """Test that an error is raised when environment variables are missing"""
        with pytest.raises(ValueError):
            load_env_vars()

# Test Reddit API Interface
class TestRedditAPI:
    
    @patch("praw.Reddit")
    def test_initialize_reddit_client(self, mock_reddit):
        """Test that the Reddit client is initialized with correct parameters"""
        credentials = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret"
        }
        
        initialize_reddit_client(credentials)
        
        mock_reddit.assert_called_once_with(
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            user_agent="ProblemSpotter:v1.0 (by /u/YourUsername)"
        )
    
    @patch("praw.Reddit")
    def test_search_reddit_posts(self, mock_reddit):
        """Test that the search query is correctly formed"""
        # Setup mock
        mock_client = MagicMock()
        mock_reddit.return_value = mock_client
        mock_subreddit = MagicMock()
        mock_client.subreddit.return_value = mock_subreddit
        
        # Mock posts
        mock_post1 = MagicMock()
        mock_post1.id = "abc123"
        mock_post1.title = "How do I learn Python?"
        mock_post1.selftext = "I want to learn Python"
        mock_post1.author.name = "user1"
        mock_post1.created_utc = 1612345678.0
        mock_post1.subreddit.display_name = "learnprogramming"
        mock_post1.permalink = "/r/learnprogramming/comments/abc123"
        mock_post1.url = "https://reddit.com/r/learnprogramming/comments/abc123"
        mock_post1.score = 10
        mock_post1.over_18 = False
        
        # This is the key change: set the return value directly to a list
        mock_subreddit.search.return_value = [mock_post1]
        
        # Call the function
        credentials = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret"
        }
        client = initialize_reddit_client(credentials)
        results = search_reddit_posts(client, "how do I")
        
        # Assertions
        mock_client.subreddit.assert_called_once_with("all")
        mock_subreddit.search.assert_called_once_with(
            "how do I", 
            sort="new", 
            limit=100
        )
        
        assert len(results) == 1
        assert results[0].id == "abc123"
        assert results[0].title == "How do I learn Python?"
        assert results[0].over_18 is False

# Test Data Storage
class TestDataStorage:
    
    def test_create_output_directory(self, tmp_path):
        """Test that the output directory is created if it doesn't exist"""
        output_dir = tmp_path / "reddit_data"
        create_output_directory(str(output_dir))
        assert output_dir.exists()
    
    def test_generate_filename(self):
        """Test that the filename is correctly generated with a timestamp"""
        filename = generate_filename()
        # Check format: reddit_how_do_i_results_YYYYMMDD_HHMMSS.json
        assert filename.startswith("reddit_how_do_i_results_")
        assert filename.endswith(".json")
        # Extract timestamp and verify format
        timestamp = filename[len("reddit_how_do_i_results_"):-len(".json")]
        datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
    
    def test_save_search_results(self, tmp_path):
        """Test that search results are saved correctly"""
        # Create mock data
        mock_post = RedditPost(
            id="abc123",
            title="How do I learn Python?",
            selftext="I want to learn Python",
            author="user1",
            created_utc=1612345678.0,
            subreddit="learnprogramming",
            permalink="/r/learnprogramming/comments/abc123",
            url="https://reddit.com/r/learnprogramming/comments/abc123",
            score=10,
            over_18=False
        )
        
        mock_results = [mock_post]
        
        # Setup output directory
        output_dir = tmp_path / "reddit_data"
        output_dir.mkdir()
        
        # Generate filename
        filename = "test_results.json"
        
        # Save results
        output_path = save_search_results(mock_results, str(output_dir), filename)
        
        # Assertions
        assert os.path.exists(output_path)
        
        # Verify content
        with open(output_path, "r") as f:
            saved_data = json.load(f)
            
        assert len(saved_data) == 1
        assert saved_data[0]["id"] == "abc123"
        assert saved_data[0]["title"] == "How do I learn Python?" 