# Branch Protection Application Design

**Date**: 2025-11-10
**Status**: Design Approved
**Purpose**: Extend the GitHub branch protection checker to apply protection rules that prevent force pushing to default branches

## Overview

This design adds a new `apply-protection` command that reads the JSON output from the existing branch protection checker and applies repository rulesets to protect default branches from force pushes and deletion.

**Key Principles**:
- Separate command from checker (clear read/write separation)
- Dry-run by default with explicit `--apply` flag (safety first)
- Minimal protection: only prevent force push and deletion
- Use modern GitHub Repository Rulesets API
- Fail-fast on systemic issues, continue with logging for individual failures

## Requirements Summary

**From User Discovery**:
- **Selection**: Dry-run with confirmation - show what would be protected, require `--apply` flag to actually do it
- **Protection Rules**: Prevent force push only (focused on core requirement)
- **API**: Use Repository Rulesets (newer GitHub API)
- **Error Handling**: Upfront sanity checks (fail fast), continue with logging during application, fail if too many consecutive errors

## Command Structure & Workflow

### Two-Step Process

1. **Check Phase** (existing tool):
   ```bash
   uv run python -m github_branch_protection_checker
   ```
   - Generates `unprotected-repos-YYYY-MM-DD-HHMMSS.json`
   - User reviews the file to see what repos need protection

2. **Dry-Run Phase** (new command, default):
   ```bash
   uv run apply-protection unprotected-repos-*.json
   ```
   - Shows what WOULD be done without making changes
   - Validates permissions and API availability
   - Displays table of repos with "Can Apply" status

3. **Apply Phase** (new command with flag):
   ```bash
   uv run apply-protection --apply unprotected-repos-*.json
   ```
   - Creates repository rulesets for each repo
   - Shows progress with success/failure per repo
   - Generates summary report

### CLI Arguments

```bash
apply-protection <json-file> [--apply] [--max-consecutive-failures N]
```

- `<json-file>`: Required. Path to JSON file exported by checker
- `--apply`: Optional. Actually apply changes (default is dry-run)
- `--max-consecutive-failures`: Optional. Stop after N consecutive failures (default: 5)

### pyproject.toml Entry

```toml
[project.scripts]
apply-protection = "github_branch_protection_checker.apply:main"
```

## GitHub Repository Rulesets API

### API Reference

**Documentation**: https://docs.github.com/en/rest/repos/rules

**Endpoint**: `POST /repos/{owner}/{repo}/rulesets`

**Requirements**:
- API Version: `2022-11-28` (header: `X-GitHub-Api-Version`)
- Authentication: Bearer token with admin permissions
- Permission Level: "Administration" repository permissions with write access

### Ruleset Configuration

```json
{
  "name": "Protect default branch from force push",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/{default_branch}"],
      "exclude": []
    }
  },
  "rules": [
    {
      "type": "non_fast_forward"
    },
    {
      "type": "deletion"
    }
  ]
}
```

### Rule Types

- **`non_fast_forward`**: Blocks force pushes to the branch
  - Reference: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets#block-force-pushes
  - No parameters required

- **`deletion`**: Prevents branch deletion (only bypass users can delete)
  - Reference: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets#restrict-deletions
  - No parameters required

### Constraints

- **Availability**: Public repos (all plans), private repos (GitHub Pro+ only)
- **Capacity**: Maximum 75 rulesets per repository
- **Permissions**: Requires admin access or "edit repository rules" permission

## Architecture

### New Modules

```
github_branch_protection_checker/
  apply.py           # Main application logic and CLI entry point
  rest_client.py     # REST API client for GitHub rulesets API

tests/
  test_apply.py      # Unit tests for apply logic
  test_rest_client.py # REST API client tests
  test_apply_e2e.py  # End-to-end test (optional, marked slow)
```

### Module Responsibilities

#### `rest_client.py` - REST API Wrapper

```python
class RestClient:
    """
    REST API client for GitHub rulesets
    Reference: https://docs.github.com/en/rest/repos/rules
    """
    def __init__(self, token: str):
        """Initialize with GitHub token"""

    def create_ruleset(self, owner: str, repo: str, config: dict) -> dict:
        """
        Create a repository ruleset

        Args:
            owner: Repository owner
            repo: Repository name
            config: Ruleset configuration (see API reference)

        Returns:
            Created ruleset data

        Raises:
            requests.HTTPError: On API errors (403, 404, etc.)
        """

    def get_repo_permissions(self, owner: str, repo: str) -> dict:
        """
        Check user's permissions on repository

        Returns:
            Permissions dict with 'admin' boolean
        """

    def check_rulesets_available(self, owner: str, repo: str) -> bool:
        """
        Check if repository plan supports rulesets

        Returns:
            True if rulesets are available
        """
```

#### `apply.py` - Application Logic

```python
def validate_environment(token: str, repos: list) -> None:
    """
    Upfront sanity checks before processing any repos

    Checks:
    1. Token validity (simple API call)
    2. Token has admin scope
    3. API version compatibility

    Raises:
        RuntimeError: If validation fails
    """

def can_apply_ruleset(
    client: RestClient,
    owner: str,
    repo: str
) -> tuple[bool, str]:
    """
    Check if ruleset can be applied to specific repository

    Checks:
    1. User has admin permission on repo
    2. Repo plan supports rulesets
    3. Repo not at 75 ruleset limit

    Returns:
        (can_apply, reason) tuple
    """

def apply_protection(
    input_file: str,
    apply_flag: bool,
    max_consecutive_failures: int = 5
) -> int:
    """
    Main application logic

    Workflow:
    1. Load repos from JSON file
    2. Validate environment
    3. For each repo:
       - Check if can apply
       - If dry-run: record status
       - If apply: create ruleset, handle errors
    4. Display results

    Returns:
        Exit code (0 = success, 1 = failure)
    """

def main(args: list[str]) -> int:
    """CLI entry point"""
```

### Existing Code Changes

**None required** - the existing checker modules remain unchanged:
- `fetcher.py` - No changes
- `models.py` - No changes
- `formatters.py` - No changes
- `graphql_client.py` - No changes
- `__main__.py` - No changes

Only addition is the new script entry in `pyproject.toml`.

## Error Handling Strategy

### Upfront Sanity Checks (Fail-Fast)

Run BEFORE processing any repos:

```python
def validate_environment(token: str, repos: list) -> None:
    # 1. Test token validity with simple API call
    # 2. Check token has admin scope
    # 3. Verify API version compatibility (2022-11-28)
    # 4. Fail immediately if any check fails
```

**Philosophy**: Catch systemic issues early before touching any repositories.

### Per-Repository Validation

```python
def can_apply_ruleset(client, owner, repo) -> tuple[bool, str]:
    # 1. Verify user has admin permission on repo
    # 2. Check if repo plan supports rulesets
    # 3. Check if repo already at 75 ruleset limit
    # Returns: (can_apply: bool, reason: str)
```

**Philosophy**: Identify specific repo issues before attempting to apply.

### During Application (Continue with Logging)

```python
# Track consecutive failures
consecutive_failures = 0
MAX_CONSECUTIVE_FAILURES = 5

for each repo:
    if failed:
        consecutive_failures += 1
        failures.append((repo_name, error))

        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            raise RuntimeError(
                f"{MAX_CONSECUTIVE_FAILURES} consecutive failures, "
                f"likely systemic issue"
            )
    else:
        consecutive_failures = 0  # Reset on success
        success_count += 1
```

**Philosophy**: Individual repo failures are expected (permissions, plans), but consecutive failures indicate systemic problems (token expired, API down).

## User Experience

### Dry-Run Output

```
$ uv run apply-protection unprotected-repos-2025-11-10.json

Analyzing 15 repositories from unprotected-repos-2025-11-10.json...

Validation Results:
┌─────────────────────────┬────────────┬─────────────────────────┐
│ Repository              │ Can Apply  │ Reason                  │
├─────────────────────────┼────────────┼─────────────────────────┤
│ user/repo1              │ ✓ Yes      │ Ready                   │
│ user/repo2              │ ✓ Yes      │ Ready                   │
│ user/private-repo       │ ✗ No       │ Plan doesn't support    │
│ user/repo3              │ ✓ Yes      │ Ready                   │
└─────────────────────────┴────────────┴─────────────────────────┘

Summary: 14/15 repositories can have protection applied
Skipped: 1 (insufficient plan)

To apply protection, run with --apply flag:
  uv run apply-protection --apply unprotected-repos-2025-11-10.json
```

### Apply Mode Output

```
$ uv run apply-protection --apply unprotected-repos-2025-11-10.json

Applying protection to 14 repositories...

✓ user/repo1 - Ruleset created
✓ user/repo2 - Ruleset created
✗ user/repo3 - Failed: API error (403 Forbidden)
✓ user/repo4 - Ruleset created
...

Summary:
  ✓ Success: 13 repositories
  ✗ Failed: 1 repository
  ⊘ Skipped: 1 repository (from dry-run validation)

Failed repositories:
  - user/repo3: API error (403 Forbidden) - check admin permissions
```

### JSON Input Format

Uses the existing JSON format exported by the checker. Reads the `unprotected` array from:

```json
{
  "summary": { ... },
  "unprotected": [
    {
      "name": "repo-name",
      "owner": "owner-name",
      "default_branch": "main",
      ...
    }
  ]
}
```

No new format needed - seamless integration with existing exports.

## Testing Strategy

### Unit Tests

**test_rest_client.py**:
- Mock REST API calls with `responses` library
- Test successful ruleset creation
- Test error handling (403, 404, 422, 500)
- Test permission checking
- Test availability checking

**test_apply.py**:
- Mock RestClient
- Test validate_environment logic
- Test can_apply_ruleset validation
- Test consecutive failure detection
- Test dry-run vs apply modes
- Test JSON parsing

### Integration Tests (Marked as Slow)

**test_apply_e2e.py**:
- Requires real GitHub token (from environment)
- Test against real GitHub API
- Only runs validation checks (no destructive operations)
- Skipped by default (`pytest -m "not slow"`)

### No Destructive Tests in CI

- Won't create actual rulesets in automated tests
- Integration tests only validate permissions and API availability
- Destructive tests require manual execution with explicit flag

## Documentation Updates

### README.md Changes

Add new section after "Usage":

```markdown
## Applying Protection

After identifying unprotected repositories, you can apply branch protection rules:

1. Review the exported JSON file to see which repositories need protection
2. Run dry-run to validate:
   ```bash
   uv run apply-protection unprotected-repos-*.json
   ```
3. Apply protection to repositories:
   ```bash
   uv run apply-protection --apply unprotected-repos-*.json
   ```

### What Protection Gets Applied

Creates a repository ruleset that:
- Prevents force pushes to the default branch
- Prevents deletion of the default branch

### Requirements

- Admin permissions on repositories
- GitHub Pro plan or higher for private repositories (public repos supported on all plans)

### Limitations

- Maximum 75 rulesets per repository
- Requires "Administration" permission with write access
```

## Implementation Phases

1. **Phase 1**: Implement `rest_client.py` with basic API calls
2. **Phase 2**: Implement `apply.py` with validation and dry-run logic
3. **Phase 3**: Add apply mode with error handling
4. **Phase 4**: Add CLI argument parsing and main entry point
5. **Phase 5**: Write unit tests
6. **Phase 6**: Update documentation
7. **Phase 7**: Manual testing with real repositories

## Security Considerations

- Token requires admin permissions (write access to Administration)
- Dry-run by default prevents accidental application
- No token stored in code or logs
- Uses existing GitHub CLI authentication (same as checker)
- Fail-fast on permission issues

## Future Enhancements (Out of Scope)

- Support for additional ruleset rules (require PRs, status checks, etc.)
- Organization-level ruleset creation
- Batch operations with rate limiting
- Progress bar for large repository counts
- Rollback functionality to remove applied rulesets
- Support for branch protection rules API (older API) as fallback

## References

- [GitHub Repository Rulesets REST API](https://docs.github.com/en/rest/repos/rules)
- [About Repository Rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [Available Rules for Rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
