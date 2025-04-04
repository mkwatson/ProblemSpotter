#!/usr/bin/env python3
"""ProblemSpotter: Complete pipeline script.

This script runs the complete ProblemSpotter pipeline:
1. Fetches Reddit posts containing "how do I" phrases
2. Analyzes the posts to identify genuine user challenges

It can be used to run both steps in sequence or just one of them.
"""

import argparse
import os
import shutil
import sys

import analyze_problems
import fetch_problems


def setup_directories() -> None:
    """Set up directory structure for the pipeline."""
    # Create the base reddit_data directory if it doesn't exist
    if not os.path.exists(analyze_problems.RAW_DATA_DIR):
        os.makedirs(analyze_problems.RAW_DATA_DIR, exist_ok=True)

    # Create the analyzed and cache directories
    analyze_problems.create_directories()


def move_to_raw_dir(file_path: str) -> str:
    """Move a file to the raw directory.

    Args:
        file_path: Path to the file to move.

    Returns:
        New path of the moved file.
    """
    filename = os.path.basename(file_path)
    new_path = os.path.join(analyze_problems.RAW_DATA_DIR, filename)

    # If the file is not already in the raw directory, copy it there
    if os.path.abspath(file_path) != os.path.abspath(new_path):
        shutil.copy2(file_path, new_path)

    return new_path


def process_fetch(args: argparse.Namespace) -> tuple[int, str | None]:
    """Process the fetch part of the pipeline.

    Args:
        args: Command line arguments.

    Returns:
        Tuple of (exit_code, file_path) where file_path is the path to the file to analyze.
    """
    print("Fetching Reddit posts...")
    result = fetch_problems.main()
    if result != 0:
        print("Error fetching Reddit posts", file=sys.stderr)
        return result, None

    # Find the file that was just created
    json_files = [
        f for f in os.listdir(fetch_problems.OUTPUT_DIR) if f.endswith(".json") and f != ".gitkeep"
    ]
    if not json_files:
        print("Error: No JSON files found after fetching", file=sys.stderr)
        return 1, None

    # Sort by modification time (newest first)
    latest_file = max(
        json_files, key=lambda f: os.path.getmtime(os.path.join(fetch_problems.OUTPUT_DIR, f))
    )
    latest_path = os.path.join(fetch_problems.OUTPUT_DIR, latest_file)

    # Move the file to the raw directory
    raw_path = move_to_raw_dir(latest_path)
    print(f"Moved fetched data to {raw_path}")

    if args.fetch_only:
        return 0, None

    return 0, raw_path


def get_file_to_analyze(args: argparse.Namespace) -> tuple[int, str | None]:
    """Get the file to analyze.

    Args:
        args: Command line arguments.

    Returns:
        Tuple of (exit_code, file_path) where file_path is the path to the file to analyze.
    """
    if args.file:
        file_path = str(args.file)
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist", file=sys.stderr)
            return 1, None
        return 0, file_path

    # Find the latest file in the raw directory
    json_files = [
        f
        for f in os.listdir(analyze_problems.RAW_DATA_DIR)
        if f.endswith(".json") and f != ".gitkeep"
    ]
    if not json_files:
        err_msg = f"Error: No JSON files found in {analyze_problems.RAW_DATA_DIR}"
        print(err_msg, file=sys.stderr)
        return 1, None

    latest_file = max(
        json_files, key=lambda f: os.path.getmtime(os.path.join(analyze_problems.RAW_DATA_DIR, f))
    )
    return 0, os.path.join(analyze_problems.RAW_DATA_DIR, latest_file)


def main() -> int:
    """Run the complete ProblemSpotter pipeline.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="Run the complete ProblemSpotter pipeline (fetch and analyze)."
    )
    parser.add_argument(
        "--fetch-only", action="store_true", help="Only fetch Reddit posts, don't analyze them."
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze existing Reddit posts, don't fetch new ones.",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to a specific Reddit data file to analyze (only used with --analyze-only).",
    )
    args = parser.parse_args()

    # Validate arguments
    if args.fetch_only and args.analyze_only:
        print("Error: Cannot specify both --fetch-only and --analyze-only", file=sys.stderr)
        return 1

    if args.file and not args.analyze_only:
        print("Error: --file can only be used with --analyze-only", file=sys.stderr)
        return 1

    try:
        # Set up directory structure
        setup_directories()

        # Determine the file to analyze
        file_to_analyze: str | None = None
        if not args.analyze_only:
            # Fetch Reddit posts
            exit_code, file_path = process_fetch(args)
            if exit_code != 0 or args.fetch_only:
                return exit_code
            file_to_analyze = file_path
        elif args.analyze_only:
            # Analyze only mode
            exit_code, file_path = get_file_to_analyze(args)
            if exit_code != 0:
                return exit_code
            file_to_analyze = file_path

        # Analyze posts
        if file_to_analyze is None:
            print("Error: No file to analyze", file=sys.stderr)
            return 1

        print(f"Analyzing posts in {file_to_analyze}...")
        analyze_problems.load_env_vars()  # Load OpenAI API key
        analyze_problems.initialize_openai_client({"api_key": os.environ.get("OPENAI_API_KEY", "")})
        output_path = analyze_problems.analyze_file(file_to_analyze)
        print(f"Analysis complete. Results saved to {output_path}")

        return 0
    except Exception as e:
        print(f"Error in pipeline: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
