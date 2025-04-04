MVP Requirements: RedditRadar

Goal

Run a single, local Python script exactly once to query Reddit using PRAW for posts containing the phrase "how do I". Store raw results in a descriptive JSON file. Enforce strict typing and implement robust automated tests. Use Python 3.13.

Functional Requirements

Query Definition
	•	Search Phrase: "how do I"
	•	Scope: Posts only, all subreddits
	•	Sorting: Most recent (new)
	•	Results Limit: Maximum per API request (100 posts)
	•	Content Filtering: Only SFW posts

Reddit API
	•	Library: PRAW
	•	Authentication: None (unauthenticated for this MVP)

Data Output
	•	Save raw API JSON responses without modification
	•	No deduplication or processing

File Storage
	•	Directory: ./reddit_data/
	•	Filename: reddit_how_do_i_results_<YYYYMMDD_HHMMSS>.json

Execution Constraints
	•	Single local manual execution
	•	No scheduling or automation at this stage

Typing & Code Quality
	•	Enforce strict static typing throughout (e.g., mypy or pyright)

Automated Testing Strategy
	•	Unit Tests: Mock Reddit API responses to validate logic, handling, and typing
	•	Schema Validation: Verify JSON output adheres strictly to expected schema and data types
	•	Tests must be deterministic, robust, and independent of external services

Project Directory Structure

reddit_radar/
├── reddit_data/
│   └── reddit_how_do_i_results_<YYYYMMDD_HHMMSS>.json
├── tests/
│   └── test_reddit_query.py
├── fetch_reddit_posts.py
├── requirements.txt
└── pyproject.toml