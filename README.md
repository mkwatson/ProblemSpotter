# ProblemSpotter

A Python script that queries Reddit for posts containing "how do I" phrases and stores the raw results in a JSON file.

## Project Overview

ProblemSpotter is a simple utility that:

1. Searches Reddit using PRAW for posts containing the phrase "how do I"
2. Filters for SFW content only
3. Saves the raw API results to a JSON file with a timestamp
4. Implements strict typing and automated testing

## Requirements

- Python 3.13
- Dependencies listed in `requirements.txt`
- Reddit API credentials (client ID and client secret)

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your Reddit API credentials:

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
```

## Usage

Run the script:

```bash
python fetch_problems.py
```

The script will:
- Search Reddit for posts containing "how do I"
- Filter out NSFW content
- Save up to 100 most recent posts to a timestamped JSON file in the `reddit_data` directory

## Project Structure

```
problemspotter/
├── reddit_data/
│   └── reddit_how_do_i_results_<YYYYMMDD_HHMMSS>.json
├── tests/
│   ├── test_reddit_query.py
│   └── test_integration.py
├── fetch_problems.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Testing

Run tests:

```bash
python -m pytest
```

The project follows a strict test-driven development approach with:
- Unit tests with mocked Reddit API responses
- Integration tests to validate the full workflow
- Pydantic models for schema validation

## Type Checking

Run the type checker:

```bash
pyright fetch_problems.py
```

The project enforces strict typing using pyright in its strictest mode.

## Output Format

The JSON output contains an array of Reddit post objects with the following structure:

```json
[
  {
    "id": "post_id",
    "title": "How do I learn Python?",
    "selftext": "Post content text...",
    "author": "username",
    "created_utc": 1612345678.0,
    "subreddit": "subreddit_name",
    "permalink": "/r/subreddit/comments/post_id/title",
    "url": "https://reddit.com/r/subreddit/comments/post_id/title",
    "score": 10,
    "over_18": false
  },
  // more posts...
]
``` 