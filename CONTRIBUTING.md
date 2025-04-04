# Contributing to ProblemSpotter

Thank you for considering contributing to ProblemSpotter! This document outlines the process for contributing to the project and the standards we uphold.

## Development Workflow

### 1. Setup Your Development Environment

Follow the setup instructions in the README.md file to ensure you have the correct development environment.

### 2. Choose an Issue

- Look for open issues in the GitHub issue tracker
- Comment on an issue to indicate you're working on it
- If you want to work on something not covered by an existing issue, create a new one first

### 3. Branching Strategy

- Create a new branch from `main` with a descriptive name:
  ```bash
  git checkout -b feature/your-feature-name
  # or
  git checkout -b fix/issue-you-are-fixing
  ```

### 4. Development Standards

#### Code Style

We use automated tools to enforce code style:

- **Black** for code formatting
- **isort** for import sorting
- **Ruff** for linting

These are enforced via pre-commit hooks. Run them manually with:

```bash
pre-commit run --all-files
```

#### Type Checking

We use strict type checking with:

- **pyright** in strict mode
- **mypy** with strict settings

All code must pass type checking without `# type: ignore` comments unless absolutely necessary.

#### Documentation

- All public functions, classes, and methods must have docstrings following Google style
- Complex logic should be explained with inline comments
- Type annotations must be used everywhere

#### Testing

- All new features must include tests
- All bug fixes must include a test that would have caught the bug
- Run tests with:
  ```bash
  pytest
  ```

### 5. Commit Guidelines

- Make small, focused commits
- Use descriptive commit messages:
  ```
  feat: Add new Reddit post filtering feature

  - Added support for filtering by post length
  - Updated documentation
  - Added tests
  ```
- Common prefixes:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation changes
  - `test:` for adding or modifying tests
  - `refactor:` for code refactoring
  - `chore:` for changes to build process or auxiliary tools

### 6. Pull Request Process

1. Push your branch to the repository
1. Create a pull request against the `main` branch
1. Ensure the CI pipeline passes
1. Request a review from a maintainer
1. Address any feedback from code review
1. Wait for approval and merge

## Adding New Dependencies

- Only add dependencies when necessary
- Document why the dependency is needed
- Update the project configuration in `pyproject.toml`
- If the dependency lacks type stubs, create them in the `typings/` directory

## Type Stubs

When adding or modifying type stubs:

1. Only include the parts of the API that we actually use
1. Follow the same style as existing stubs
1. Keep them minimal yet complete
1. Update the `pyproject.toml` configuration if necessary

## Handling Type Issues

If you encounter type checking issues:

1. **Do not** default to using `# type: ignore`
1. Try to fix the underlying issue first
1. Improve type annotations to be more specific
1. For third-party libraries, improve the type stub files
1. Only use `# type: ignore` as a last resort with a clear comment explaining why

## Release Process

1. Update version in `pyproject.toml`
1. Update CHANGELOG.md
1. Create a new tag with the version number
1. Push tag to GitHub
1. CI will build and publish the package

## Questions?

If you have any questions about contributing, feel free to open an issue for clarification.
