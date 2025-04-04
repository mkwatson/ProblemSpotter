# ProblemSpotter

A tool for fetching Reddit posts containing "how do I" phrases, designed to identify common questions and problems people are trying to solve.

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

1. **Create a .env file** with your Reddit API credentials:

   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   ```

   To obtain Reddit API credentials:

   - Visit https://www.reddit.com/prefs/apps
   - Click "create app" at the bottom
   - Fill in the details (name, select "script", etc.)
   - After creation, note the client ID (under the app name) and client secret

### Running the Application

```bash
python fetch_problems.py
```

This will:

1. Connect to the Reddit API
1. Search for recent posts containing "how do I" phrases
1. Filter out NSFW content
1. Save the results to a timestamped JSON file in the `./reddit_data/` directory

## Project Structure

- `fetch_problems.py`: Main script for fetching Reddit posts
- `typings/`: Type stub files for external libraries (praw, dotenv, pydantic)
- `.pre-commit-config.yaml`: Configuration for pre-commit hooks
- `pyproject.toml`: Project configuration and tool settings
- `.github/workflows/`: CI/CD pipeline definitions

## Code Standards

### Type Checking

We use both pyright and mypy for comprehensive type checking:

- **pyright**: Used in strict mode with comprehensive error reporting
- **mypy**: Additional type validation with pydantic plugin support
- **Custom Type Stubs**: Created for external libraries in the `typings/` directory

### Linting and Formatting

- **Black**: Code formatting with 100-character line length
- **isort**: Import sorting with Black compatibility
- **Ruff**: Comprehensive linting with multiple rule sets (E, F, I, C4, B, N, UP, D, PL, RUF, S)

### Testing

- **pytest**: For unit and integration testing
- **Coverage**: Tracking and reporting code coverage

## For New Engineers

1. **First commit preparation**:

   - After setting up the environment, run `pre-commit run --all-files` to ensure your environment is correctly configured
   - This will validate that all hooks are working correctly before you make your first commit

1. **Common issues**:

   - If you encounter type errors, check if you need to update the type stubs in the `typings/` directory
   - For linting errors, run `ruff check --fix` to automatically fix many common issues

1. **IDE configuration**:

   - VSCode: Use the Python extension with pyright and Black integration
   - PyCharm: Enable Black as an external tool and configure type checking

## License

This project is licensed under the MIT License - see the LICENSE file for details.
