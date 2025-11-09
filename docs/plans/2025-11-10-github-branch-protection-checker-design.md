# GitHub Branch Protection Checker - Design Document

**Date:** 2025-11-10
**Purpose:** Python script to identify GitHub repositories lacking branch protection on their default branch

## Overview

This script will use GitHub's GraphQL API to efficiently check all repositories owned by the authenticated user and identify those without branch protection on their default branch. It will output results to console and export to JSON, CSV, and Markdown formats.

## Requirements

### Functional Requirements
- Check all repositories owned by the authenticated user
- Identify repos where the default branch lacks protection (either old branch protection rules OR new repository rulesets)
- Skip archived repositories (read-only, protection less relevant)
- Output results to console in a readable format
- Export results to three file formats: JSON, CSV, and Markdown
- Fail fast on any errors (authentication, API, network)

### Authentication
- Use GitHub CLI (`gh`) to obtain OAuth token via `gh auth token`
- Use Python `requests` library to call GraphQL API directly with the token

### Protection Detection
The script must check BOTH protection systems:
1. **Old system:** Branch Protection Rules (`branchProtectionRule`)
2. **New system:** Repository Rulesets (`rules`)

A branch is considered protected if ANY of these are true:
- `branchProtectionRule` is not null
- `refUpdateRule` is not null (non-admin view of branch protection)
- `rules.totalCount > 0` (repository rulesets apply to this branch)

## Architecture

### Component Overview

1. **Authentication Module**
   - Execute `gh auth token` via subprocess
   - Validate token is non-empty
   - Fail fast if `gh` not authenticated

2. **GraphQL Client**
   - Wrapper around `requests.post()` to `https://api.github.com/graphql`
   - Add `Authorization: Bearer <token>` header
   - Parse JSON responses
   - Handle HTTP and GraphQL errors

3. **Query Builder**
   - Construct GraphQL queries with pagination support
   - Fetch 100 repositories per request (GitHub's maximum)
   - Include branch protection data in initial query

4. **Data Processor**
   - Parse GraphQL response JSON
   - Filter out archived repos and repos without default branch
   - Identify repos where default branch lacks protection
   - Track statistics (total, skipped, unprotected)

5. **Output Formatter**
   - Console: Text table with summary statistics
   - JSON: Complete structured data with timestamp
   - CSV: Spreadsheet-compatible format
   - Markdown: Human-readable report with table

## GraphQL Query Design

### Query Structure

```graphql
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
```

### Query Parameters

- `ownerAffiliations: OWNER` - Only fetch repositories owned by the user
- `first: 100` - Maximum repositories per request
- `after: $cursor` - Pagination cursor for next page

### Pagination Handling

1. Execute query with `cursor: null` for first page
2. Check `pageInfo.hasNextPage`
3. If true, execute next query with `cursor: pageInfo.endCursor`
4. Accumulate results from all pages
5. Continue until `hasNextPage` is false

## Data Processing

### Filtering Logic

For each repository in the response:

1. **Skip if archived:** `isArchived == true`
2. **Skip if no default branch:** `defaultBranchRef == null`
3. **Check protection status:**
   - Protected if: `branchProtectionRule != null` OR `refUpdateRule != null` OR `rules.totalCount > 0`
   - Unprotected if: ALL three conditions are null/zero

### Data Structure

Unprotected repositories will be stored as:

```python
{
    "name": "repo-name",
    "owner": "username",
    "url": "https://github.com/username/repo-name",
    "default_branch": "main",
    "is_private": false,
    "is_fork": false
}
```

### Statistics Tracking

- Total repositories owned
- Repositories skipped (archived)
- Repositories skipped (no default branch)
- Unprotected repositories found

## Output Formats

### Console Output

```
Checking repositories...
Found 150 repositories owned by you

Summary:
- Total repositories: 150
- Archived (skipped): 23
- No default branch (skipped): 5
- Unprotected repositories: 12

Unprotected Repositories:
┌─────────────────────────────┬──────────────┬─────────┬──────┐
│ Repository                  │ Branch       │ Private │ Fork │
├─────────────────────────────┼──────────────┼─────────┼──────┤
│ username/repo-name-1        │ main         │ Yes     │ No   │
│ username/repo-name-2        │ master       │ No      │ Yes  │
└─────────────────────────────┴──────────────┴─────────┴──────┘
```

### File Exports

All files written to current directory with timestamp:

1. **JSON:** `unprotected-repos-YYYY-MM-DD-HHMMSS.json`
   - Array of repository objects with complete metadata
   - Includes summary statistics

2. **CSV:** `unprotected-repos-YYYY-MM-DD-HHMMSS.csv`
   - Headers: name, owner, url, default_branch, is_private, is_fork
   - One row per unprotected repository

3. **Markdown:** `unprotected-repos-YYYY-MM-DD-HHMMSS.md`
   - Summary statistics at top
   - Table of unprotected repositories
   - Links to repository URLs

## Error Handling

### Fail Fast Approach

The script terminates immediately on ANY error with a clear message and non-zero exit code.

### Error Categories

**Authentication Errors:**
- `gh auth token` command fails → "Error: GitHub CLI not authenticated. Run 'gh auth login' first."
- Empty/invalid token → "Error: Failed to obtain GitHub authentication token"

**API Errors:**
- HTTP errors (non-200) → "Error: GitHub API request failed with status {code}: {message}"
- GraphQL errors → "Error: GitHub API returned error: {error_message}"
- Network failures → "Error: Failed to connect to GitHub API: {details}"

**Data Validation:**
- Unexpected response structure → "Error: Unexpected API response structure"
- Missing expected fields → "Error: Required field '{field}' missing from API response"

### Success Criteria

Exit with status code 0 only if:
- All repositories were successfully checked
- All output files were successfully written
- No errors occurred during execution

## Implementation Notes

### Dependencies

- Python 3.8+ (use `uv` for all Python commands)
- `requests` library for HTTP calls
- GitHub CLI (`gh`) must be installed and authenticated
- Standard library: `subprocess`, `json`, `csv`, `datetime`

### File Organization

```
github-branch-protection-checker.py    # Main script
```

### Development Approach

1. Use Test-Driven Development (TDD)
2. Write tests before implementation
3. Validate against real GitHub API responses
4. Handle edge cases (empty repos, no default branch, etc.)
