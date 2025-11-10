# GitHub Branch Protection Checker

Find GitHub repositories that lack branch protection on their default branch.

## Features

- ✅ Checks both old branch protection rules and new repository rulesets
- ✅ Efficient batch fetching via GitHub GraphQL API
- ✅ Exports to JSON, CSV, and Markdown formats
- ✅ Console table output with summary statistics
- ✅ Fail-fast error handling

## Requirements

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) package manager
- [GitHub CLI](https://cli.github.com/) (for authentication)

## Installation

1. Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install GitHub CLI and authenticate:
```bash
gh auth login
```

3. Clone this repository:
```bash
git clone <repository-url>
cd github-branch-protection-checker
```

4. Install dependencies:
```bash
uv sync
```

## Usage

Run the script:
```bash
uv run python -m github_branch_protection_checker
```

This will:
1. Fetch all repositories you own from GitHub
2. Check for branch protection on the default branch
3. Display results in console
4. Export to three files:
   - `unprotected-repos-YYYY-MM-DD-HHMMSS.json`
   - `unprotected-repos-YYYY-MM-DD-HHMMSS.csv`
   - `unprotected-repos-YYYY-MM-DD-HHMMSS.md`

## What Gets Checked

A repository is considered "protected" if its default branch has ANY of:
- Branch protection rules (old system)
- Ref update rules (old system, non-admin view)
- Repository rulesets (new system)

A repository is "unprotected" only if ALL three are absent.

## What Gets Skipped

- Archived repositories (read-only, so protection is less relevant)
- Repositories without a default branch (empty repos)

## Development

Run tests:
```bash
uv run pytest -v
```

Run specific test file:
```bash
uv run pytest tests/test_auth.py -v
```

## Architecture

- **auth.py** - Get OAuth token from GitHub CLI
- **graphql_client.py** - Execute GraphQL queries with error handling
- **fetcher.py** - Fetch repositories with pagination
- **models.py** - Repository data models
- **formatters.py** - Output formatting (console, JSON, CSV, Markdown)
- **__main__.py** - Main entry point

## License

MIT
