"""ProblemSpotter package."""

from problem_spotter.core.analyze_problems import (
    analyze_file,
    initialize_openai_client,
)
from problem_spotter.core.fetch_problems import (
    initialize_reddit_client,
    search_reddit_posts,
)
from problem_spotter.core.run_pipeline import main

__version__ = "0.1.0"

__all__ = [
    "analyze_file",
    "initialize_openai_client",
    "initialize_reddit_client",
    "main",
    "search_reddit_posts",
]
