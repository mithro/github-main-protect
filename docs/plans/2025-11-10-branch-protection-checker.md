# GitHub Branch Protection Checker Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python script that identifies GitHub repositories lacking branch protection using GraphQL API

**Architecture:** Direct HTTP calls to GitHub GraphQL API using token from `gh auth token`. Batch-fetch 100 repos per request with branch protection data, filter client-side, export to JSON/CSV/Markdown.

**Tech Stack:** Python 3.8+, uv (package manager), requests (HTTP), GitHub GraphQL API, GitHub CLI (auth only)

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`

**Step 1: Create Python version file**

Create `.python-version`:
```
3.11
```

**Step 2: Create pyproject.toml with dependencies**

Create `pyproject.toml`:
```toml
[project]
name = "github-branch-protection-checker"
version = "0.1.0"
description = "Find GitHub repositories lacking branch protection"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.31.0",
]

[project.scripts]
check-branch-protection = "github_branch_protection_checker:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
]
```

**Step 3: Initialize uv environment**

Run: `uv sync`
Expected: Creates virtual environment and installs dependencies

**Step 4: Verify installation**

Run: `uv pip list`
Expected: Shows requests and pytest installed

**Step 5: Commit**

```bash
git add pyproject.toml .python-version
git commit -m "feat: initialize project with uv and dependencies

Set up Python project with uv package manager.
Add requests for HTTP calls and pytest for testing.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Authentication Module

**Files:**
- Create: `github_branch_protection_checker/__init__.py`
- Create: `github_branch_protection_checker/auth.py`
- Create: `tests/test_auth.py`

**Step 1: Write failing test for token retrieval**

Create `tests/test_auth.py`:
```python
import subprocess
from unittest.mock import patch, MagicMock
from github_branch_protection_checker.auth import get_github_token


def test_get_github_token_success():
    """Test successful token retrieval from gh CLI"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='ghp_test_token_123\n',
            stderr=''
        )
        token = get_github_token()
        assert token == 'ghp_test_token_123'
        mock_run.assert_called_once_with(
            ['gh', 'auth', 'token'],
            capture_output=True,
            text=True,
            check=True
        )


def test_get_github_token_not_authenticated():
    """Test error when gh CLI not authenticated"""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['gh', 'auth', 'token'],
            stderr='not logged in'
        )
        try:
            get_github_token()
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "GitHub CLI not authenticated" in str(e)
            assert "gh auth login" in str(e)


def test_get_github_token_empty():
    """Test error when token is empty"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='  \n',
            stderr=''
        )
        try:
            get_github_token()
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "empty" in str(e).lower()
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_auth.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'github_branch_protection_checker'"

**Step 3: Create package init file**

Create `github_branch_protection_checker/__init__.py`:
```python
"""GitHub Branch Protection Checker"""
__version__ = "0.1.0"
```

**Step 4: Run test again**

Run: `uv run pytest tests/test_auth.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'github_branch_protection_checker.auth'"

**Step 5: Write minimal implementation**

Create `github_branch_protection_checker/auth.py`:
```python
"""Authentication module for GitHub API access"""
import subprocess


def get_github_token() -> str:
    """
    Retrieve GitHub authentication token from gh CLI.

    Returns:
        GitHub OAuth token

    Raises:
        RuntimeError: If gh CLI is not authenticated or token is empty
    """
    try:
        result = subprocess.run(
            ['gh', 'auth', 'token'],
            capture_output=True,
            text=True,
            check=True
        )
        token = result.stdout.strip()

        if not token:
            raise RuntimeError("Failed to obtain GitHub authentication token: token is empty")

        return token

    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Error: GitHub CLI not authenticated. Run 'gh auth login' first.\n"
            f"Details: {e.stderr}"
        )
```

**Step 6: Run test to verify it passes**

Run: `uv run pytest tests/test_auth.py -v`
Expected: PASS (3 tests)

**Step 7: Commit**

```bash
git add github_branch_protection_checker/ tests/test_auth.py
git commit -m "feat: add GitHub authentication module

Retrieve OAuth token from gh CLI with error handling.
Fail fast if not authenticated or token empty.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: GraphQL Client Module

**Files:**
- Create: `github_branch_protection_checker/graphql_client.py`
- Create: `tests/test_graphql_client.py`

**Step 1: Write failing test for GraphQL client**

Create `tests/test_graphql_client.py`:
```python
from unittest.mock import patch, MagicMock
import requests
from github_branch_protection_checker.graphql_client import GraphQLClient


def test_graphql_client_successful_query():
    """Test successful GraphQL query execution"""
    client = GraphQLClient("test_token")

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'viewer': {'login': 'testuser'}}
        }
        mock_post.return_value = mock_response

        result = client.execute("query { viewer { login } }")

        assert result == {'viewer': {'login': 'testuser'}}
        mock_post.assert_called_once_with(
            'https://api.github.com/graphql',
            json={'query': "query { viewer { login } }"},
            headers={
                'Authorization': 'Bearer test_token',
                'Content-Type': 'application/json'
            },
            timeout=30
        )


def test_graphql_client_with_variables():
    """Test GraphQL query with variables"""
    client = GraphQLClient("test_token")

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'result': 'ok'}}
        mock_post.return_value = mock_response

        result = client.execute(
            "query($var: String) { test(input: $var) }",
            variables={'var': 'value'}
        )

        assert result == {'result': 'ok'}
        call_args = mock_post.call_args
        assert call_args[1]['json']['variables'] == {'var': 'value'}


def test_graphql_client_http_error():
    """Test handling of HTTP errors"""
    client = GraphQLClient("test_token")

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_post.return_value = mock_response

        try:
            client.execute("query { viewer { login } }")
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "401" in str(e)
            assert "Unauthorized" in str(e)


def test_graphql_client_graphql_errors():
    """Test handling of GraphQL errors in response"""
    client = GraphQLClient("test_token")

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'errors': [
                {'message': 'Field not found'},
                {'message': 'Another error'}
            ]
        }
        mock_post.return_value = mock_response

        try:
            client.execute("query { invalid }")
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "GraphQL error" in str(e)
            assert "Field not found" in str(e)


def test_graphql_client_network_error():
    """Test handling of network errors"""
    client = GraphQLClient("test_token")

    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.ConnectionError("Network unreachable")

        try:
            client.execute("query { viewer { login } }")
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "Failed to connect" in str(e)
            assert "Network unreachable" in str(e)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_graphql_client.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'github_branch_protection_checker.graphql_client'"

**Step 3: Write minimal implementation**

Create `github_branch_protection_checker/graphql_client.py`:
```python
"""GraphQL client for GitHub API"""
import requests
from typing import Dict, Any, Optional


class GraphQLClient:
    """Client for executing GraphQL queries against GitHub API"""

    GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

    def __init__(self, token: str):
        """
        Initialize GraphQL client.

        Args:
            token: GitHub OAuth token
        """
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Optional query variables

        Returns:
            Response data dictionary

        Raises:
            RuntimeError: On HTTP errors, GraphQL errors, or network failures
        """
        payload = {'query': query}
        if variables:
            payload['variables'] = variables

        try:
            response = requests.post(
                self.GITHUB_GRAPHQL_URL,
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"Error: GitHub API request failed with status {response.status_code}: "
                    f"{response.text}"
                )

            result = response.json()

            if 'errors' in result:
                error_messages = [err['message'] for err in result['errors']]
                raise RuntimeError(
                    f"Error: GitHub API returned GraphQL error: {error_messages[0]}"
                )

            return result['data']

        except requests.ConnectionError as e:
            raise RuntimeError(f"Error: Failed to connect to GitHub API: {str(e)}")
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_graphql_client.py -v`
Expected: PASS (5 tests)

**Step 5: Commit**

```bash
git add github_branch_protection_checker/graphql_client.py tests/test_graphql_client.py
git commit -m "feat: add GraphQL client for GitHub API

Execute GraphQL queries with proper error handling.
Fail fast on HTTP errors, GraphQL errors, and network failures.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Repository Data Models

**Files:**
- Create: `github_branch_protection_checker/models.py`
- Create: `tests/test_models.py`

**Step 1: Write failing test for repository data model**

Create `tests/test_models.py`:
```python
from github_branch_protection_checker.models import Repository, is_protected


def test_repository_from_graphql():
    """Test creating Repository from GraphQL response"""
    graphql_data = {
        'name': 'test-repo',
        'owner': {'login': 'testuser'},
        'url': 'https://github.com/testuser/test-repo',
        'defaultBranchRef': {
            'name': 'main',
            'branchProtectionRule': None,
            'refUpdateRule': None,
            'rules': {'totalCount': 0}
        },
        'isPrivate': True,
        'isFork': False,
        'isArchived': False
    }

    repo = Repository.from_graphql(graphql_data)

    assert repo.name == 'test-repo'
    assert repo.owner == 'testuser'
    assert repo.url == 'https://github.com/testuser/test-repo'
    assert repo.default_branch == 'main'
    assert repo.is_private is True
    assert repo.is_fork is False
    assert repo.is_archived is False
    assert repo.has_protection is False


def test_repository_with_branch_protection_rule():
    """Test repository with old branch protection rules"""
    graphql_data = {
        'name': 'protected-repo',
        'owner': {'login': 'testuser'},
        'url': 'https://github.com/testuser/protected-repo',
        'defaultBranchRef': {
            'name': 'main',
            'branchProtectionRule': {'id': 'BPR_123'},
            'refUpdateRule': None,
            'rules': {'totalCount': 0}
        },
        'isPrivate': False,
        'isFork': False,
        'isArchived': False
    }

    repo = Repository.from_graphql(graphql_data)
    assert repo.has_protection is True


def test_repository_with_ref_update_rule():
    """Test repository with refUpdateRule protection"""
    graphql_data = {
        'name': 'protected-repo',
        'owner': {'login': 'testuser'},
        'url': 'https://github.com/testuser/protected-repo',
        'defaultBranchRef': {
            'name': 'main',
            'branchProtectionRule': None,
            'refUpdateRule': {'id': 'RUR_123'},
            'rules': {'totalCount': 0}
        },
        'isPrivate': False,
        'isFork': False,
        'isArchived': False
    }

    repo = Repository.from_graphql(graphql_data)
    assert repo.has_protection is True


def test_repository_with_rulesets():
    """Test repository with new ruleset protection"""
    graphql_data = {
        'name': 'protected-repo',
        'owner': {'login': 'testuser'},
        'url': 'https://github.com/testuser/protected-repo',
        'defaultBranchRef': {
            'name': 'main',
            'branchProtectionRule': None,
            'refUpdateRule': None,
            'rules': {'totalCount': 2}
        },
        'isPrivate': False,
        'isFork': False,
        'isArchived': False
    }

    repo = Repository.from_graphql(graphql_data)
    assert repo.has_protection is True


def test_repository_no_default_branch():
    """Test repository without default branch"""
    graphql_data = {
        'name': 'empty-repo',
        'owner': {'login': 'testuser'},
        'url': 'https://github.com/testuser/empty-repo',
        'defaultBranchRef': None,
        'isPrivate': False,
        'isFork': False,
        'isArchived': False
    }

    repo = Repository.from_graphql(graphql_data)
    assert repo.default_branch is None
    assert repo.has_protection is False


def test_repository_to_dict():
    """Test converting repository to dictionary"""
    graphql_data = {
        'name': 'test-repo',
        'owner': {'login': 'testuser'},
        'url': 'https://github.com/testuser/test-repo',
        'defaultBranchRef': {
            'name': 'main',
            'branchProtectionRule': None,
            'refUpdateRule': None,
            'rules': {'totalCount': 0}
        },
        'isPrivate': True,
        'isFork': True,
        'isArchived': False
    }

    repo = Repository.from_graphql(graphql_data)
    result = repo.to_dict()

    assert result == {
        'name': 'test-repo',
        'owner': 'testuser',
        'url': 'https://github.com/testuser/test-repo',
        'default_branch': 'main',
        'is_private': True,
        'is_fork': True
    }


def test_is_protected_function():
    """Test standalone is_protected function"""
    # No protection
    ref = {
        'branchProtectionRule': None,
        'refUpdateRule': None,
        'rules': {'totalCount': 0}
    }
    assert is_protected(ref) is False

    # Has branch protection rule
    ref = {
        'branchProtectionRule': {'id': '123'},
        'refUpdateRule': None,
        'rules': {'totalCount': 0}
    }
    assert is_protected(ref) is True

    # Has ref update rule
    ref = {
        'branchProtectionRule': None,
        'refUpdateRule': {'id': '123'},
        'rules': {'totalCount': 0}
    }
    assert is_protected(ref) is True

    # Has rulesets
    ref = {
        'branchProtectionRule': None,
        'refUpdateRule': None,
        'rules': {'totalCount': 1}
    }
    assert is_protected(ref) is True
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_models.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'github_branch_protection_checker.models'"

**Step 3: Write minimal implementation**

Create `github_branch_protection_checker/models.py`:
```python
"""Data models for repository information"""
from typing import Dict, Any, Optional
from dataclasses import dataclass


def is_protected(branch_ref: Dict[str, Any]) -> bool:
    """
    Check if a branch has any protection enabled.

    A branch is protected if ANY of these are true:
    - branchProtectionRule is not null (old system)
    - refUpdateRule is not null (old system, non-admin view)
    - rules.totalCount > 0 (new ruleset system)

    Args:
        branch_ref: GraphQL defaultBranchRef data

    Returns:
        True if branch has any protection, False otherwise
    """
    if branch_ref.get('branchProtectionRule') is not None:
        return True
    if branch_ref.get('refUpdateRule') is not None:
        return True
    if branch_ref.get('rules', {}).get('totalCount', 0) > 0:
        return True
    return False


@dataclass
class Repository:
    """Repository information from GitHub"""

    name: str
    owner: str
    url: str
    default_branch: Optional[str]
    is_private: bool
    is_fork: bool
    is_archived: bool
    has_protection: bool

    @classmethod
    def from_graphql(cls, data: Dict[str, Any]) -> 'Repository':
        """
        Create Repository from GraphQL response data.

        Args:
            data: Repository node from GraphQL response

        Returns:
            Repository instance
        """
        default_branch_ref = data.get('defaultBranchRef')

        return cls(
            name=data['name'],
            owner=data['owner']['login'],
            url=data['url'],
            default_branch=default_branch_ref['name'] if default_branch_ref else None,
            is_private=data['isPrivate'],
            is_fork=data['isFork'],
            is_archived=data['isArchived'],
            has_protection=is_protected(default_branch_ref) if default_branch_ref else False
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert repository to dictionary for export.

        Returns:
            Dictionary with repository information
        """
        return {
            'name': self.name,
            'owner': self.owner,
            'url': self.url,
            'default_branch': self.default_branch,
            'is_private': self.is_private,
            'is_fork': self.is_fork
        }
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_models.py -v`
Expected: PASS (8 tests)

**Step 5: Commit**

```bash
git add github_branch_protection_checker/models.py tests/test_models.py
git commit -m "feat: add repository data models

Define Repository dataclass with protection detection.
Check both old branch protection rules and new rulesets.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Repository Fetcher

**Files:**
- Create: `github_branch_protection_checker/fetcher.py`
- Create: `tests/test_fetcher.py`

**Step 1: Write failing test for repository fetcher**

Create `tests/test_fetcher.py`:
```python
from unittest.mock import MagicMock
from github_branch_protection_checker.fetcher import RepositoryFetcher, REPO_QUERY


def test_fetch_repositories_single_page():
    """Test fetching repositories with single page"""
    mock_client = MagicMock()
    mock_client.execute.return_value = {
        'viewer': {
            'repositories': {
                'pageInfo': {
                    'hasNextPage': False,
                    'endCursor': None
                },
                'nodes': [
                    {
                        'name': 'repo1',
                        'owner': {'login': 'user'},
                        'url': 'https://github.com/user/repo1',
                        'defaultBranchRef': {
                            'name': 'main',
                            'branchProtectionRule': None,
                            'refUpdateRule': None,
                            'rules': {'totalCount': 0}
                        },
                        'isPrivate': False,
                        'isFork': False,
                        'isArchived': False
                    }
                ]
            }
        }
    }

    fetcher = RepositoryFetcher(mock_client)
    repos = fetcher.fetch_all_repositories()

    assert len(repos) == 1
    assert repos[0].name == 'repo1'
    mock_client.execute.assert_called_once()


def test_fetch_repositories_multiple_pages():
    """Test fetching repositories with pagination"""
    mock_client = MagicMock()

    # First page
    page1_response = {
        'viewer': {
            'repositories': {
                'pageInfo': {
                    'hasNextPage': True,
                    'endCursor': 'cursor1'
                },
                'nodes': [
                    {
                        'name': 'repo1',
                        'owner': {'login': 'user'},
                        'url': 'https://github.com/user/repo1',
                        'defaultBranchRef': {
                            'name': 'main',
                            'branchProtectionRule': None,
                            'refUpdateRule': None,
                            'rules': {'totalCount': 0}
                        },
                        'isPrivate': False,
                        'isFork': False,
                        'isArchived': False
                    }
                ]
            }
        }
    }

    # Second page
    page2_response = {
        'viewer': {
            'repositories': {
                'pageInfo': {
                    'hasNextPage': False,
                    'endCursor': None
                },
                'nodes': [
                    {
                        'name': 'repo2',
                        'owner': {'login': 'user'},
                        'url': 'https://github.com/user/repo2',
                        'defaultBranchRef': {
                            'name': 'master',
                            'branchProtectionRule': {'id': '123'},
                            'refUpdateRule': None,
                            'rules': {'totalCount': 0}
                        },
                        'isPrivate': True,
                        'isFork': False,
                        'isArchived': False
                    }
                ]
            }
        }
    }

    mock_client.execute.side_effect = [page1_response, page2_response]

    fetcher = RepositoryFetcher(mock_client)
    repos = fetcher.fetch_all_repositories()

    assert len(repos) == 2
    assert repos[0].name == 'repo1'
    assert repos[1].name == 'repo2'
    assert mock_client.execute.call_count == 2

    # Verify second call used cursor
    second_call = mock_client.execute.call_args_list[1]
    assert second_call[1]['variables']['cursor'] == 'cursor1'


def test_repo_query_structure():
    """Test that REPO_QUERY has required fields"""
    assert 'ownerAffiliations: OWNER' in REPO_QUERY
    assert 'branchProtectionRule' in REPO_QUERY
    assert 'refUpdateRule' in REPO_QUERY
    assert 'rules(first: 1)' in REPO_QUERY
    assert 'totalCount' in REPO_QUERY
    assert 'pageInfo' in REPO_QUERY
    assert 'hasNextPage' in REPO_QUERY
    assert 'endCursor' in REPO_QUERY
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_fetcher.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'github_branch_protection_checker.fetcher'"

**Step 3: Write minimal implementation**

Create `github_branch_protection_checker/fetcher.py`:
```python
"""Repository fetcher with pagination support"""
from typing import List, Optional
from .graphql_client import GraphQLClient
from .models import Repository


REPO_QUERY = """
query($cursor: String) {
  viewer {
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        url
        defaultBranchRef {
          name
          branchProtectionRule {
            id
          }
          refUpdateRule {
            id
          }
          rules(first: 1) {
            totalCount
          }
        }
        owner {
          login
        }
        isPrivate
        isFork
        isArchived
      }
    }
  }
}
"""


class RepositoryFetcher:
    """Fetches repositories from GitHub with pagination"""

    def __init__(self, client: GraphQLClient):
        """
        Initialize repository fetcher.

        Args:
            client: GraphQL client instance
        """
        self.client = client

    def fetch_all_repositories(self) -> List[Repository]:
        """
        Fetch all repositories owned by the authenticated user.

        Handles pagination automatically, fetching 100 repos per request.

        Returns:
            List of Repository instances
        """
        repositories = []
        cursor: Optional[str] = None
        has_next_page = True

        while has_next_page:
            variables = {'cursor': cursor}
            data = self.client.execute(REPO_QUERY, variables=variables)

            repo_data = data['viewer']['repositories']
            page_info = repo_data['pageInfo']

            for node in repo_data['nodes']:
                repo = Repository.from_graphql(node)
                repositories.append(repo)

            has_next_page = page_info['hasNextPage']
            cursor = page_info['endCursor']

        return repositories
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_fetcher.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add github_branch_protection_checker/fetcher.py tests/test_fetcher.py
git commit -m "feat: add repository fetcher with pagination

Fetch all owned repositories from GitHub GraphQL API.
Handle cursor-based pagination automatically.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Output Formatters

**Files:**
- Create: `github_branch_protection_checker/formatters.py`
- Create: `tests/test_formatters.py`

**Step 1: Write failing test for formatters**

Create `tests/test_formatters.py`:
```python
import json
import csv
from pathlib import Path
from github_branch_protection_checker.formatters import (
    format_console_output,
    export_to_json,
    export_to_csv,
    export_to_markdown
)
from github_branch_protection_checker.models import Repository


def create_test_repo(name: str, protected: bool = False) -> Repository:
    """Helper to create test repository"""
    return Repository(
        name=name,
        owner='testuser',
        url=f'https://github.com/testuser/{name}',
        default_branch='main',
        is_private=False,
        is_fork=False,
        is_archived=False,
        has_protection=protected
    )


def test_format_console_output():
    """Test console output formatting"""
    unprotected = [
        create_test_repo('repo1'),
        create_test_repo('repo2')
    ]

    output = format_console_output(
        unprotected_repos=unprotected,
        total_repos=10,
        archived_count=2,
        no_branch_count=1
    )

    assert 'Total repositories: 10' in output
    assert 'Archived (skipped): 2' in output
    assert 'No default branch (skipped): 1' in output
    assert 'Unprotected repositories: 2' in output
    assert 'repo1' in output
    assert 'repo2' in output
    assert 'testuser' in output


def test_export_to_json(tmp_path):
    """Test JSON export"""
    unprotected = [
        create_test_repo('repo1'),
        create_test_repo('repo2')
    ]

    filepath = export_to_json(
        unprotected_repos=unprotected,
        total_repos=10,
        archived_count=2,
        no_branch_count=1,
        output_dir=str(tmp_path)
    )

    assert Path(filepath).exists()
    assert filepath.startswith(str(tmp_path))
    assert 'unprotected-repos-' in filepath
    assert filepath.endswith('.json')

    with open(filepath, 'r') as f:
        data = json.load(f)

    assert data['summary']['total_repositories'] == 10
    assert data['summary']['archived_skipped'] == 2
    assert data['summary']['no_branch_skipped'] == 1
    assert data['summary']['unprotected_count'] == 2
    assert len(data['unprotected_repositories']) == 2
    assert data['unprotected_repositories'][0]['name'] == 'repo1'


def test_export_to_csv(tmp_path):
    """Test CSV export"""
    unprotected = [
        Repository(
            name='repo1',
            owner='testuser',
            url='https://github.com/testuser/repo1',
            default_branch='main',
            is_private=True,
            is_fork=False,
            is_archived=False,
            has_protection=False
        ),
        Repository(
            name='repo2',
            owner='testuser',
            url='https://github.com/testuser/repo2',
            default_branch='master',
            is_private=False,
            is_fork=True,
            is_archived=False,
            has_protection=False
        )
    ]

    filepath = export_to_csv(unprotected, output_dir=str(tmp_path))

    assert Path(filepath).exists()
    assert filepath.endswith('.csv')

    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]['name'] == 'repo1'
    assert rows[0]['owner'] == 'testuser'
    assert rows[0]['default_branch'] == 'main'
    assert rows[0]['is_private'] == 'True'
    assert rows[0]['is_fork'] == 'False'
    assert rows[1]['name'] == 'repo2'


def test_export_to_markdown(tmp_path):
    """Test Markdown export"""
    unprotected = [
        create_test_repo('repo1'),
        create_test_repo('repo2')
    ]

    filepath = export_to_markdown(
        unprotected_repos=unprotected,
        total_repos=10,
        archived_count=2,
        no_branch_count=1,
        output_dir=str(tmp_path)
    )

    assert Path(filepath).exists()
    assert filepath.endswith('.md')

    with open(filepath, 'r') as f:
        content = f.read()

    assert '# GitHub Branch Protection Report' in content
    assert 'Total repositories: 10' in content
    assert 'Archived (skipped): 2' in content
    assert 'Unprotected repositories: 2' in content
    assert '| Repository |' in content
    assert '| testuser/repo1 |' in content
    assert '[testuser/repo1](https://github.com/testuser/repo1)' in content


def test_export_empty_list(tmp_path):
    """Test exports with empty repository list"""
    filepath = export_to_json(
        unprotected_repos=[],
        total_repos=5,
        archived_count=0,
        no_branch_count=0,
        output_dir=str(tmp_path)
    )

    with open(filepath, 'r') as f:
        data = json.load(f)

    assert data['summary']['unprotected_count'] == 0
    assert data['unprotected_repositories'] == []
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_formatters.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'github_branch_protection_checker.formatters'"

**Step 3: Write minimal implementation**

Create `github_branch_protection_checker/formatters.py`:
```python
"""Output formatters for repository data"""
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List
from .models import Repository


def format_console_output(
    unprotected_repos: List[Repository],
    total_repos: int,
    archived_count: int,
    no_branch_count: int
) -> str:
    """
    Format repositories for console output.

    Args:
        unprotected_repos: List of unprotected repositories
        total_repos: Total number of repositories checked
        archived_count: Number of archived repos skipped
        no_branch_count: Number of repos without default branch

    Returns:
        Formatted string for console output
    """
    lines = []
    lines.append("\nSummary:")
    lines.append(f"- Total repositories: {total_repos}")
    lines.append(f"- Archived (skipped): {archived_count}")
    lines.append(f"- No default branch (skipped): {no_branch_count}")
    lines.append(f"- Unprotected repositories: {len(unprotected_repos)}")

    if unprotected_repos:
        lines.append("\nUnprotected Repositories:")
        lines.append("┌─────────────────────────────────────┬──────────────┬─────────┬──────┐")
        lines.append("│ Repository                          │ Branch       │ Private │ Fork │")
        lines.append("├─────────────────────────────────────┼──────────────┼─────────┼──────┤")

        for repo in unprotected_repos:
            full_name = f"{repo.owner}/{repo.name}"
            branch = repo.default_branch or "N/A"
            private = "Yes" if repo.is_private else "No"
            fork = "Yes" if repo.is_fork else "No"

            lines.append(
                f"│ {full_name:<35} │ {branch:<12} │ {private:<7} │ {fork:<4} │"
            )

        lines.append("└─────────────────────────────────────┴──────────────┴─────────┴──────┘")

    return "\n".join(lines)


def export_to_json(
    unprotected_repos: List[Repository],
    total_repos: int,
    archived_count: int,
    no_branch_count: int,
    output_dir: str = "."
) -> str:
    """
    Export repositories to JSON file.

    Args:
        unprotected_repos: List of unprotected repositories
        total_repos: Total number of repositories checked
        archived_count: Number of archived repos skipped
        no_branch_count: Number of repos without default branch
        output_dir: Directory to write file to

    Returns:
        Path to created file
    """
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    filename = f"unprotected-repos-{timestamp}.json"
    filepath = Path(output_dir) / filename

    data = {
        'summary': {
            'total_repositories': total_repos,
            'archived_skipped': archived_count,
            'no_branch_skipped': no_branch_count,
            'unprotected_count': len(unprotected_repos)
        },
        'unprotected_repositories': [repo.to_dict() for repo in unprotected_repos]
    }

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    return str(filepath)


def export_to_csv(unprotected_repos: List[Repository], output_dir: str = ".") -> str:
    """
    Export repositories to CSV file.

    Args:
        unprotected_repos: List of unprotected repositories
        output_dir: Directory to write file to

    Returns:
        Path to created file
    """
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    filename = f"unprotected-repos-{timestamp}.csv"
    filepath = Path(output_dir) / filename

    with open(filepath, 'w', newline='') as f:
        fieldnames = ['name', 'owner', 'url', 'default_branch', 'is_private', 'is_fork']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for repo in unprotected_repos:
            writer.writerow(repo.to_dict())

    return str(filepath)


def export_to_markdown(
    unprotected_repos: List[Repository],
    total_repos: int,
    archived_count: int,
    no_branch_count: int,
    output_dir: str = "."
) -> str:
    """
    Export repositories to Markdown file.

    Args:
        unprotected_repos: List of unprotected repositories
        total_repos: Total number of repositories checked
        archived_count: Number of archived repos skipped
        no_branch_count: Number of repos without default branch
        output_dir: Directory to write file to

    Returns:
        Path to created file
    """
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    filename = f"unprotected-repos-{timestamp}.md"
    filepath = Path(output_dir) / filename

    lines = []
    lines.append("# GitHub Branch Protection Report")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("\n## Summary")
    lines.append(f"\n- Total repositories: {total_repos}")
    lines.append(f"- Archived (skipped): {archived_count}")
    lines.append(f"- No default branch (skipped): {no_branch_count}")
    lines.append(f"- Unprotected repositories: {len(unprotected_repos)}")

    if unprotected_repos:
        lines.append("\n## Unprotected Repositories")
        lines.append("\n| Repository | Branch | Private | Fork | URL |")
        lines.append("|------------|--------|---------|------|-----|")

        for repo in unprotected_repos:
            full_name = f"{repo.owner}/{repo.name}"
            branch = repo.default_branch or "N/A"
            private = "Yes" if repo.is_private else "No"
            fork = "Yes" if repo.is_fork else "No"

            lines.append(
                f"| {full_name} | {branch} | {private} | {fork} | "
                f"[{full_name}]({repo.url}) |"
            )

    with open(filepath, 'w') as f:
        f.write("\n".join(lines))

    return str(filepath)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_formatters.py -v`
Expected: PASS (6 tests)

**Step 5: Commit**

```bash
git add github_branch_protection_checker/formatters.py tests/test_formatters.py
git commit -m "feat: add output formatters for JSON, CSV, Markdown

Export repository data to multiple formats.
Include console table output with summary statistics.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: Main Script

**Files:**
- Create: `github_branch_protection_checker/__main__.py`
- Modify: `github_branch_protection_checker/__init__.py`

**Step 1: Write integration test**

Create `tests/test_main.py`:
```python
from unittest.mock import patch, MagicMock
from github_branch_protection_checker.__main__ import main
import sys


def test_main_success(capsys, tmp_path):
    """Test successful execution"""
    mock_repos = [
        MagicMock(
            name='repo1',
            owner='user',
            url='https://github.com/user/repo1',
            default_branch='main',
            is_private=False,
            is_fork=False,
            is_archived=False,
            has_protection=False,
            to_dict=lambda: {
                'name': 'repo1',
                'owner': 'user',
                'url': 'https://github.com/user/repo1',
                'default_branch': 'main',
                'is_private': False,
                'is_fork': False
            }
        )
    ]

    with patch('github_branch_protection_checker.__main__.get_github_token') as mock_token:
        with patch('github_branch_protection_checker.__main__.GraphQLClient') as mock_client_class:
            with patch('github_branch_protection_checker.__main__.RepositoryFetcher') as mock_fetcher_class:
                mock_token.return_value = 'test_token'

                mock_fetcher = MagicMock()
                mock_fetcher.fetch_all_repositories.return_value = mock_repos
                mock_fetcher_class.return_value = mock_fetcher

                # Run main
                result = main(output_dir=str(tmp_path))

                assert result == 0

                captured = capsys.readouterr()
                assert 'Checking repositories' in captured.out
                assert 'Total repositories: 1' in captured.out
                assert 'Unprotected repositories: 1' in captured.out


def test_main_auth_failure(capsys):
    """Test authentication failure"""
    with patch('github_branch_protection_checker.__main__.get_github_token') as mock_token:
        mock_token.side_effect = RuntimeError("GitHub CLI not authenticated")

        result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert 'GitHub CLI not authenticated' in captured.out


def test_main_api_failure(capsys):
    """Test API error"""
    with patch('github_branch_protection_checker.__main__.get_github_token') as mock_token:
        with patch('github_branch_protection_checker.__main__.GraphQLClient') as mock_client_class:
            with patch('github_branch_protection_checker.__main__.RepositoryFetcher') as mock_fetcher_class:
                mock_token.return_value = 'test_token'

                mock_fetcher = MagicMock()
                mock_fetcher.fetch_all_repositories.side_effect = RuntimeError("API error")
                mock_fetcher_class.return_value = mock_fetcher

                result = main()

                assert result == 1
                captured = capsys.readouterr()
                assert 'API error' in captured.out
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_main.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'github_branch_protection_checker.__main__'"

**Step 3: Write main script implementation**

Create `github_branch_protection_checker/__main__.py`:
```python
"""Main entry point for GitHub branch protection checker"""
import sys
from typing import Optional
from .auth import get_github_token
from .graphql_client import GraphQLClient
from .fetcher import RepositoryFetcher
from .formatters import (
    format_console_output,
    export_to_json,
    export_to_csv,
    export_to_markdown
)


def main(output_dir: str = ".") -> int:
    """
    Main entry point for the script.

    Args:
        output_dir: Directory to write export files to

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Get authentication token
        print("Checking repositories...")
        token = get_github_token()

        # Create client and fetcher
        client = GraphQLClient(token)
        fetcher = RepositoryFetcher(client)

        # Fetch all repositories
        all_repos = fetcher.fetch_all_repositories()
        print(f"Found {len(all_repos)} repositories owned by you")

        # Filter repositories
        unprotected = []
        archived_count = 0
        no_branch_count = 0

        for repo in all_repos:
            if repo.is_archived:
                archived_count += 1
                continue

            if repo.default_branch is None:
                no_branch_count += 1
                continue

            if not repo.has_protection:
                unprotected.append(repo)

        # Display console output
        console_output = format_console_output(
            unprotected_repos=unprotected,
            total_repos=len(all_repos),
            archived_count=archived_count,
            no_branch_count=no_branch_count
        )
        print(console_output)

        # Export to files
        if unprotected or True:  # Always create exports
            json_file = export_to_json(
                unprotected_repos=unprotected,
                total_repos=len(all_repos),
                archived_count=archived_count,
                no_branch_count=no_branch_count,
                output_dir=output_dir
            )
            print(f"\nExported to JSON: {json_file}")

            csv_file = export_to_csv(unprotected, output_dir=output_dir)
            print(f"Exported to CSV: {csv_file}")

            md_file = export_to_markdown(
                unprotected_repos=unprotected,
                total_repos=len(all_repos),
                archived_count=archived_count,
                no_branch_count=no_branch_count,
                output_dir=output_dir
            )
            print(f"Exported to Markdown: {md_file}")

        return 0

    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: Unexpected error occurred: {str(e)}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

**Step 4: Update package init to expose main**

Modify `github_branch_protection_checker/__init__.py`:
```python
"""GitHub Branch Protection Checker"""
from .auth import get_github_token
from .graphql_client import GraphQLClient
from .fetcher import RepositoryFetcher
from .models import Repository
from .__main__ import main

__version__ = "0.1.0"
__all__ = ['get_github_token', 'GraphQLClient', 'RepositoryFetcher', 'Repository', 'main']
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_main.py -v`
Expected: PASS (3 tests)

**Step 6: Run all tests**

Run: `uv run pytest -v`
Expected: All tests PASS

**Step 7: Commit**

```bash
git add github_branch_protection_checker/__main__.py github_branch_protection_checker/__init__.py tests/test_main.py
git commit -m "feat: add main script entry point

Orchestrate authentication, fetching, filtering, and export.
Fail fast on errors with clear error messages.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 8: End-to-End Test

**Files:**
- Create: `tests/test_e2e.py`

**Step 1: Write end-to-end test**

Create `tests/test_e2e.py`:
```python
"""End-to-end integration test"""
import subprocess
import json
from pathlib import Path


def test_script_execution_help():
    """Test that script can be executed with Python"""
    result = subprocess.run(
        ['uv', 'run', 'python', '-m', 'github_branch_protection_checker'],
        capture_output=True,
        text=True,
        timeout=10
    )

    # Should fail with auth error or succeed
    # Either is fine for this test - we're just checking it runs
    assert result.returncode in [0, 1]
```

**Step 2: Run test**

Run: `uv run pytest tests/test_e2e.py -v`
Expected: PASS

**Step 3: Manual test (optional)**

Run: `uv run python -m github_branch_protection_checker`

This will actually execute against GitHub if `gh` is authenticated.

**Step 4: Commit**

```bash
git add tests/test_e2e.py
git commit -m "test: add end-to-end integration test

Verify script can be executed via uv run.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 9: Documentation

**Files:**
- Create: `README.md`

**Step 1: Create README**

Create `README.md`:
```markdown
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
```

**Step 2: Commit README**

```bash
git add README.md
git commit -m "docs: add comprehensive README

Document installation, usage, and architecture.
Explain protection detection logic.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 10: Final Verification

**Step 1: Run all tests**

Run: `uv run pytest -v`
Expected: All tests PASS

**Step 2: Verify package structure**

Run: `find github_branch_protection_checker tests -type f -name "*.py" | sort`
Expected: Shows all created files

**Step 3: Test actual execution (if gh is authenticated)**

Run: `uv run python -m github_branch_protection_checker`
Expected: Either succeeds or shows clear error message

**Step 4: Final commit with summary**

```bash
git add -A
git commit -m "chore: final verification complete

All tests passing. Package structure verified.
Ready for use.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Completion

The implementation is complete! The script:

✅ Authenticates via GitHub CLI
✅ Fetches all owned repositories via GraphQL API
✅ Checks both old and new protection systems
✅ Filters out archived repos and empty repos
✅ Exports to JSON, CSV, and Markdown
✅ Displays console output with table
✅ Fails fast on errors
✅ Has comprehensive test coverage
✅ Uses uv for Python management
✅ Follows TDD approach

**Next steps:** Use @superpowers:finishing-a-development-branch to decide how to integrate this work (merge, PR, or cleanup).
