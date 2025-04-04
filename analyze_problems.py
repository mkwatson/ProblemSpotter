"""ProblemSpotter: Reddit post analyzer.

This script analyzes Reddit posts to identify actual user challenges or problems.
It uses OpenAI's GPT-4o model to determine if a post is a genuine question
about how to do something.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from typing import Any, TypedDict

import openai
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Constants
RAW_DATA_DIR = "./reddit_data/raw/"
ANALYZED_DATA_DIR = "./reddit_data/analyzed/"
CACHE_DIR = "./reddit_data/cache/"
OPENAI_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.0  # Use 0 for deterministic responses


# Type definitions
class OpenAICredentials(TypedDict):
    """OpenAI API credentials type definition."""

    api_key: str


class AnalysisResult(BaseModel):
    """Schema for the analysis result of a post."""

    post_id: str
    is_question: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    category: str = ""
    reasoning: str


class AnalyzedPost(BaseModel):
    """Schema for a post with analysis results."""

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
    analysis: AnalysisResult


def load_env_vars() -> OpenAICredentials:
    """Load environment variables for OpenAI API.

    Returns:
        A dictionary containing the OpenAI API key.

    Raises:
        ValueError: If required environment variables are not set.
    """
    load_dotenv()

    api_key = os.environ.get("OPENAI_API_KEY")

    if api_key is None or api_key == "":
        error_msg = "Required environment variable OPENAI_API_KEY must be set in .env file"
        raise ValueError(error_msg)

    return {"api_key": api_key}


def initialize_openai_client(credentials: OpenAICredentials) -> None:
    """Initialize the OpenAI client.

    Args:
        credentials: A dictionary containing the OpenAI API key.
    """
    openai.api_key = credentials["api_key"]


def create_cache_key(post_content: str) -> str:
    """Create a deterministic cache key for a post.

    Args:
        post_content: The content to hash.

    Returns:
        A hash of the post content.
    """
    # Use a secure hash function (SHA-256) instead of MD5
    return hashlib.sha256(post_content.encode("utf-8")).hexdigest()


def create_directories() -> None:
    """Create necessary directories if they don't exist."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(ANALYZED_DATA_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)


def get_cached_analysis(cache_key: str) -> dict[str, Any] | None:
    """Get cached analysis result.

    Args:
        cache_key: The cache key to look up.

    Returns:
        The cached analysis result or None if not found.
    """
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_file):
        with open(cache_file, encoding="utf-8") as f:
            return json.load(f)
    return None


def save_to_cache(cache_key: str, analysis: dict[str, Any]) -> None:
    """Save analysis result to cache.

    Args:
        cache_key: The cache key to save under.
        analysis: The analysis result to cache.
    """
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)


def analyze_post(post: dict[str, Any]) -> AnalysisResult:
    """Analyze a post to determine if it's a genuine question.

    Args:
        post: The post to analyze.

    Returns:
        Analysis result.
    """
    # Combine title and selftext for analysis
    post_content = f"Title: {post['title']}\nContent: {post['selftext']}"

    # Create a cache key for this post
    cache_key = create_cache_key(post_content)

    # Check if analysis is already cached
    cached_result = get_cached_analysis(cache_key)
    if cached_result:
        return AnalysisResult(
            post_id=post["id"],
            is_question=cached_result["is_question"],
            confidence_score=cached_result["confidence_score"],
            category=cached_result.get("category", ""),
            reasoning=cached_result["reasoning"],
        )

    # Prepare the prompt for OpenAI
    system_prompt = """
    You are analyzing Reddit posts to identify genuine user challenges or problems.
    Your task is to determine if a post is asking a real "how-to" question or
    seeking help with a specific problem.

    A genuine question or problem:
    1. Contains a specific request for information or help
    2. Is phrased as a genuine question (not rhetorical)
    3. Describes a challenge the user is facing
    4. Seeks actionable advice or instructions

    Respond with a JSON object with the following fields:
    - is_question: boolean (true if it's a genuine question/problem, false otherwise)
    - confidence_score: float between 0 and 1
    - category: string (leave empty for now)
    - reasoning: brief explanation for your decision
    """

    user_prompt = f"""
    Please analyze this Reddit post to determine if it contains a genuine question or problem:

    {post_content}
    """

    try:
        # Call the OpenAI API
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=DEFAULT_TEMPERATURE,
            response_format={"type": "json_object"},
        )

        # Parse the response
        response_content = response.choices[0].message.content
        analysis = json.loads(response_content)

        # Save to cache
        save_to_cache(cache_key, analysis)

        return AnalysisResult(
            post_id=post["id"],
            is_question=analysis["is_question"],
            confidence_score=analysis["confidence_score"],
            category=analysis.get("category", ""),
            reasoning=analysis["reasoning"],
        )
    except Exception as e:
        # In case of API error, return a default result
        print(f"Error analyzing post {post['id']}: {e}", file=sys.stderr)
        return AnalysisResult(
            post_id=post["id"],
            is_question=False,
            confidence_score=0.0,
            category="",
            reasoning=f"Error during analysis: {e!s}",
        )


def load_reddit_data(file_path: str) -> list[dict[str, Any]]:
    """Load Reddit data from a JSON file.

    Args:
        file_path: Path to the JSON file.

    Returns:
        List of posts.
    """
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def extract_timestamp_from_filename(filename: str) -> str:
    """Extract timestamp from a filename.

    Args:
        filename: The filename to extract from.

    Returns:
        The extracted timestamp.
    """
    # Expected format: reddit_how_do_i_results_20250404_113459.json
    try:
        parts = filename.split("_")
        return "_".join(parts[-2:]).replace(".json", "")
    except (IndexError, ValueError):
        # If parsing fails, use current timestamp
        return datetime.now().strftime("%Y%m%d_%H%M%S")


def analyze_file(input_file: str) -> str:
    """Analyze all posts in a file.

    Args:
        input_file: Path to the input file.

    Returns:
        Path to the output file.
    """
    # Load Reddit data
    posts = load_reddit_data(input_file)

    # Analyze each post
    analyzed_posts = []
    for post in posts:
        analysis = analyze_post(post)
        # Handle both Pydantic v1 and v2
        analysis_dict = getattr(analysis, "model_dump", analysis.dict)()
        analyzed_post = {**post, "analysis": analysis_dict}
        analyzed_posts.append(analyzed_post)

    # Generate output filename
    input_filename = os.path.basename(input_file)
    timestamp = extract_timestamp_from_filename(input_filename)
    output_filename = f"analyzed_{timestamp}.json"
    output_path = os.path.join(ANALYZED_DATA_DIR, output_filename)

    # Save results
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analyzed_posts, f, indent=2)

    print(f"Analyzed {len(posts)} posts, saved to {output_path}")
    return output_path


def main() -> int:
    """Main function to run the Reddit post analyzer.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(description="Analyze Reddit posts for genuine questions.")
    parser.add_argument(
        "--file",
        type=str,
        help="Path to the Reddit data file to analyze. If not provided, latest file will be used.",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="If set, will look in the raw directory instead of the main directory.",
    )
    args = parser.parse_args()

    try:
        # Create necessary directories
        create_directories()

        # Load environment variables
        credentials = load_env_vars()

        # Initialize OpenAI client
        initialize_openai_client(credentials)

        # Determine the input file
        if args.file:
            if not os.path.exists(args.file):
                print(f"Error: File {args.file} does not exist", file=sys.stderr)
                return 1
            input_file = args.file
        else:
            # Find the latest file
            search_dir = RAW_DATA_DIR if args.raw else "./reddit_data/"
            json_files = [f for f in os.listdir(search_dir) if f.endswith(".json")]
            if not json_files:
                print(f"Error: No JSON files found in {search_dir}", file=sys.stderr)
                return 1

            # Get the most recently modified file
            latest_file = max(
                json_files, key=lambda f: os.path.getmtime(os.path.join(search_dir, f))
            )
            input_file = os.path.join(search_dir, latest_file)

        # Analyze the file
        analyze_file(input_file)

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
