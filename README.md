# ProblemSpotter

ProblemSpotter is a data mining and analysis tool designed to identify real user problems and challenges from Reddit. By automatically extracting and analyzing "how do I" questions, it helps entrepreneurs, product managers, and researchers discover unmet needs and potential business opportunities.

## Project Motivation

### Why ProblemSpotter Exists

Finding genuine user problems is the foundation of successful product development and entrepreneurship. ProblemSpotter was created to:

1. **Automate problem discovery**: Instead of manually searching through forums to find problems worth solving, ProblemSpotter automates this process by fetching and analyzing Reddit posts.

1. **Identify genuine questions**: Not all posts containing "how do I" are actual questions seeking help. Using AI, ProblemSpotter distinguishes between rhetorical questions, discussion prompts, and genuine requests for solutions.

1. **Spot business opportunities**: By identifying clusters of similar problems, ProblemSpotter helps entrepreneurs discover niches where people need solutions.

1. **Validate product ideas**: Understanding what problems people are trying to solve provides validation for product ideas and directions for feature development.

## Current Capabilities

ProblemSpotter currently offers:

1. **Automated data collection**: Fetches recent posts from Reddit containing "how do I" phrases
1. **Content filtering**: Removes NSFW content to focus on appropriate problem statements
1. **AI-powered analysis**: Uses OpenAI's GPT-4o to determine if posts are genuine questions
1. **Confidence scoring**: Provides confidence scores and reasoning for each classification
1. **Efficient caching**: Minimizes API costs by caching all OpenAI responses
1. **Well-organized data**: Stores raw data, analysis results, and cache in a structured directory system

## Future Roadmap

- Problem categorization: Classify questions by domain (tech, health, finance, etc.)
- Pattern recognition: Identify common themes and trends across questions
- Sentiment analysis: Detect urgency and emotional context of problems
- Opportunity scoring: Rank problems by potential market size/impact
- Report generation: Create digestible summaries of discovered opportunities

## Development Standards

This project enforces strict development standards to ensure code quality and maintainability:

- **Type Checking**: Full static type checking with pyright and mypy in strict mode
- **Code Style**: Consistent formatting with Black and comprehensive linting with Ruff
- **Testing**: Comprehensive test coverage with pytest
- **Documentation**: Detailed docstrings following Google style conventions
- **CI/CD**: Automated testing and validation with GitHub Actions

## Getting Started

### Prerequisites

- Python 3.12+
- [Git](https://git-scm.com/)
- Reddit API credentials (see below)
- OpenAI API credentials (for analysis feature)

### Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/ProblemSpotter.git
   cd ProblemSpotter
   ```

1. **Set up a virtual environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

1. **Install dependencies**:

   ```bash
   pip install -e ".[dev]"
   ```

1. **Set up pre-commit hooks**:

   ```bash
   pre-commit install
   ```

1. **Create a .env file** with your API credentials:

   ```
   # Reddit API credentials
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret

   # OpenAI API credentials (for analysis feature)
   OPENAI_API_KEY=your_openai_api_key
   ```

#### Obtaining API Credentials

**Reddit API credentials:**

- Visit https://www.reddit.com/prefs/apps
- Click "create app" at the bottom
- Fill in the details (name, select "script", etc.)
- After creation, note the client ID (under the app name) and client secret

**OpenAI API credentials:**

- Visit https://platform.openai.com/api-keys
- Create a new API key
- Save it securely (it will only be shown once)

### Running the Application

ProblemSpotter offers a flexible command-line interface with several usage options:

#### Complete Pipeline

Run the complete pipeline (fetch and analyze):

```bash
python run_pipeline.py
```

This will:

1. Connect to the Reddit API
1. Search for recent posts containing "how do I" phrases
1. Filter out NSFW content
1. Save the results to a timestamped JSON file in `./data/raw/`
1. Analyze the posts using OpenAI GPT-4o to identify actual questions
1. Save the analysis results to `./data/analyzed/`

#### Fetch Only

To only fetch new posts without analyzing them:

```bash
python run_pipeline.py --fetch-only
```

#### Analyze Only

To analyze an existing dataset:

```bash
python run_pipeline.py --analyze-only
```

Or to analyze a specific file:

```bash
python run_pipeline.py --analyze-only --file ./data/raw/your_file.json
```

#### Individual Scripts

You can also run each script separately:

```bash
python fetch_problems.py  # Fetch posts only
python analyze_problems.py  # Analyze the latest fetched posts
```

## Understanding the Output

After running the analysis, you'll find the results in `./data/analyzed/`. The output is a JSON file containing the original posts with added analysis:

```json
{
  "id": "post_id",
  "title": "Post title",
  "selftext": "Post content",
  ...
  "analysis": {
    "post_id": "post_id",
    "is_question": true,
    "confidence_score": 0.95,
    "category": "",
    "reasoning": "This is a genuine question asking for specific advice..."
  }
}
```

### Key Fields in the Analysis

- **is_question**: Boolean indicating if the post contains a genuine problem/question
- **confidence_score**: Number between 0-1 indicating certainty of the classification
- **reasoning**: Explanation of why the post was classified as a question or not
- **category**: Reserved for future category tagging

### Processing Your Results

You can use standard command-line tools to explore the results:

```bash
# Count how many genuine questions were found
grep -c "\"is_question\": true" ./data/analyzed/your_file.json

# Find posts with high confidence scores
grep -A 20 "confidence_score\": 0.9" ./data/analyzed/your_file.json
```

## Project Structure

```
ProblemSpotter/
├── fetch_problems.py         # Script for fetching Reddit posts
├── analyze_problems.py       # Script for analyzing posts with GPT-4o
├── run_pipeline.py           # Script to run the complete pipeline
├── pyproject.toml            # Project configuration and tool settings
├── requirements.txt          # Package dependencies
├── typings/                  # Type stub files for external libraries
├── tests/                    # Test files
└── data/              # Data directory
    ├── raw/                  # Raw Reddit data files
    ├── analyzed/             # Analyzed data files
    └── cache/                # Cache for API responses
```

## File Descriptions

- **fetch_problems.py**: Connects to Reddit API and fetches posts containing "how do I" phrases
- **analyze_problems.py**: Uses OpenAI's GPT-4o to determine if posts contain genuine questions
- **run_pipeline.py**: Orchestrates the complete pipeline of fetching and analyzing posts
- **requirements.txt**: Lists all Python package dependencies
- **.env**: Stores API credentials (not in version control)
- **data/**: Directory structure that organizes raw data, analysis results, and API response caches

## For Developers

### Key Design Patterns

1. **Caching System**: All OpenAI API responses are cached based on post content hash, minimizing API costs
1. **Pipeline Architecture**: Modular design allows running components separately or together
1. **Type Safety**: Comprehensive type annotations throughout the codebase
1. **Error Handling**: Robust error handling for API failures, file access issues, etc.

### Making Contributions

If you'd like to contribute to ProblemSpotter:

1. Fork the repository and create a feature branch
1. Make your changes with appropriate test coverage
1. Ensure all tests pass and linting standards are met
1. Submit a pull request with a clear description of your changes

### Development Workflow

1. **First commit preparation**:

   - After setting up the environment, run `pre-commit run --all-files` to ensure your environment is correctly configured
   - This will validate that all hooks are working correctly before you make your first commit

1. **Common issues**:

   - If you encounter type errors, check if you need to update the type stubs in the `typings/` directory
   - For linting errors, run `ruff check --fix` to automatically fix many common issues

1. **IDE configuration**:

   - VSCode: Use the Python extension with pyright and Black integration
   - PyCharm: Enable Black as an external tool and configure type checking

### Testing

Run the test suite to ensure your changes don't break existing functionality:

```bash
pytest
```

Or with coverage reporting:

```bash
pytest --cov=.
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
