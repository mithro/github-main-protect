# GitHub Actions Workflows

This directory contains CI/CD workflows for the github-branch-protection-checker project.

## Workflows

### CI Workflow (`ci.yml`)

Runs comprehensive quality checks on every push and pull request.

**Triggers:**
- Push to `master` or `main` branches
- Pull requests targeting `master` or `main` branches

**Jobs:**

1. **Lint and Format Check**
   - Runs ruff linting on all Python code
   - Verifies code formatting with ruff
   - Python 3.12 on Ubuntu

2. **Fast Tests** (Matrix across Python 3.8-3.12)
   - Runs quick unit tests (skips slow integration tests)
   - Verifies package can be imported
   - Tests CLI entry point
   - Runs on all supported Python versions

3. **All Tests Including Slow** (Matrix across Python 3.8-3.12)
   - Only runs on main branch pushes and PRs
   - Includes slow integration tests
   - Continues on error (may fail without GitHub authentication)

4. **Test Coverage**
   - Generates code coverage reports
   - Uploads to Codecov (if configured)
   - Python 3.12 on Ubuntu

5. **Package Installation**
   - Builds the package as a wheel
   - Tests installation from wheel
   - Verifies import works post-installation

6. **Type Checking** (Optional)
   - Runs mypy for static type checking
   - Continues on error (won't fail CI)

7. **Verify Clean Checkout**
   - Checks for merge conflict markers
   - Warns about debug statements (pdb, breakpoint, ipdb)

8. **All Checks Passed**
   - Summary job that depends on critical checks
   - Used as branch protection requirement

**Caching:**
- UV cache enabled for faster dependency installation
- Cache key based on `uv.lock` file

### Security Workflow (`security.yml`)

Comprehensive security scanning for secrets, vulnerabilities, and code security issues.

**Triggers:**
- Push to `master` or `main` branches
- Pull requests targeting `master` or `main` branches
- Weekly schedule (Mondays at 9am UTC)

**Jobs:**

1. **GitLeaks Secret Scanning**
   - Scans entire git history for secrets
   - Checks for API keys, tokens, passwords
   - Uses official gitleaks-action

2. **Dependency Review** (PRs only)
   - Reviews dependency changes in pull requests
   - Fails on moderate or higher severity vulnerabilities
   - Uses GitHub's dependency review action

3. **Python Dependency Safety Check**
   - Scans Python dependencies for known vulnerabilities
   - Uses safety database
   - Reports but doesn't fail CI

4. **Bandit Security Linting**
   - Static security analysis of Python code
   - Checks for common security issues
   - Uploads results as artifacts

5. **CodeQL Security Analysis**
   - Advanced security analysis by GitHub
   - Finds security vulnerabilities and coding errors
   - Uses extended security queries
   - Results visible in GitHub Security tab

## Badge Status

Add these badges to your README.md:

```markdown
![CI](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/CI/badge.svg)
![Security](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Security%20Scanning/badge.svg)
```

## Required Secrets

No secrets are required for basic functionality. Optional secrets:

- `CODECOV_TOKEN` - For uploading coverage reports to Codecov
- `GITLEAKS_LICENSE` - Only needed for GitLeaks Enterprise

## Branch Protection Rules

Recommended branch protection settings for `main`/`master`:

- Require status checks to pass before merging:
  - `All Checks Passed` (from ci.yml)
  - `GitLeaks Secret Scanning` (from security.yml)
- Require branches to be up to date before merging
- Require linear history
- Include administrators

## Local Testing

Test the same checks locally before pushing:

```bash
# Run linting
make lint

# Run fast tests
make test

# Run all tests
make test-all

# Run with coverage
make test-coverage

# Format code
make format

# Security scanning (requires tools installed)
gitleaks detect --source . --verbose
bandit -r github_branch_protection_checker/
```

## Dependency Updates

Development dependencies are defined in `pyproject.toml`:

```bash
# Sync dependencies (including dev)
uv sync --dev

# Update all dependencies
uv lock --upgrade
```

## Performance Optimizations

The workflows use several optimizations:

1. **UV Caching**: Dependencies are cached based on `uv.lock`
2. **Matrix Strategy**: Tests run in parallel across Python versions
3. **Fail-fast disabled**: All Python versions tested even if one fails
4. **Conditional runs**: Slow tests only on main/PRs to save CI time
5. **Continue-on-error**: Optional checks don't block CI

## Troubleshooting

### Tests failing locally but passing in CI

- Ensure you have latest dependencies: `uv sync --dev`
- Check Python version matches: `python --version`
- Clear pytest cache: `make clean`

### Slow tests timing out

- Slow tests require GitHub CLI authentication
- Set `continue-on-error: true` in workflow (already configured)
- Consider mocking GitHub API calls

### Linting failures

- Run `make format` to auto-fix formatting issues
- Check `ruff.toml` for configuration
- Run `make lint` locally before pushing

### Security scan false positives

- Update `.bandit` to skip specific tests
- Add exclusions to `ruff.toml` if needed
- Document why security warnings are false positives
