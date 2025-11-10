# CI/CD Pipeline Setup and Usage

This document explains the GitHub Actions CI/CD pipeline for the github-branch-protection-checker project.

## Overview

The project uses two main GitHub Actions workflows:

1. **CI Workflow** - Tests, linting, and quality checks
2. **Security Workflow** - Secret scanning and vulnerability detection

## Quick Start

### For Contributors

1. **Install pre-commit hooks** (recommended):
   ```bash
   uv pip install pre-commit
   pre-commit install
   ```

2. **Run checks locally before pushing**:
   ```bash
   # Install dev dependencies
   uv sync --dev

   # Run all checks
   make lint          # Linting
   make test          # Fast tests
   make test-all      # All tests including slow
   ```

3. **Fix formatting issues automatically**:
   ```bash
   make format
   ```

### For Maintainers

1. **Enable GitHub Actions** in repository settings
2. **Set up branch protection** on `main`/`master`:
   - Require "All Checks Passed" status check
   - Require "GitLeaks Secret Scanning" status check
3. **Optional: Enable CodeQL** in Security tab
4. **Optional: Set up Codecov** for coverage reports

## CI Workflow Details

### Workflow File: `.github/workflows/ci.yml`

#### Jobs and Purpose

| Job | Purpose | Python Versions | When It Runs |
|-----|---------|----------------|--------------|
| `lint` | Code quality checks | 3.12 | Always |
| `test-fast` | Unit tests (fast) | 3.8-3.12 | Always |
| `test-all` | All tests including slow | 3.8-3.12 | Main branch + PRs |
| `coverage` | Coverage reporting | 3.12 | Always |
| `package-install` | Install verification | 3.12 | Always |
| `type-check` | Static type checking | 3.12 | Always (optional) |
| `verify-clean` | Code cleanliness | Latest | Always |
| `all-checks-passed` | Summary job | - | Always |

#### What Gets Tested

**Lint Job:**
- Ruff linting (code quality)
- Ruff formatting (code style)
- Enforces consistent code style

**Fast Tests Job:**
- Unit tests without slow markers
- Package import verification
- CLI entry point check
- Runs in ~30-60 seconds

**All Tests Job:**
- Includes slow integration tests
- May require GitHub authentication
- Runs in ~2-5 minutes
- Can fail on CI (continues on error)

**Coverage Job:**
- Generates code coverage report
- Uploads to Codecov (if configured)
- Shows which lines are tested

**Package Install Job:**
- Builds wheel package
- Tests installation
- Verifies import after install

**Type Check Job:**
- Runs mypy static analysis
- Checks type hints
- Non-blocking (continues on error)

**Verify Clean Job:**
- Checks for merge conflicts
- Detects debug statements (pdb, breakpoint)
- Warns if found

### Caching Strategy

The workflow uses UV's built-in caching:

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v3
  with:
    enable-cache: true
    cache-dependency-glob: "uv.lock"
```

Cache is invalidated when `uv.lock` changes, ensuring dependencies stay in sync.

### Matrix Testing

Tests run across Python 3.8, 3.9, 3.10, 3.11, and 3.12:

```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]
```

With `fail-fast: false`, all versions are tested even if one fails.

## Security Workflow Details

### Workflow File: `.github/workflows/security.yml`

#### Jobs and Purpose

| Job | Purpose | When It Runs |
|-----|---------|--------------|
| `gitleaks` | Secret scanning | Always + Weekly |
| `dependency-review` | Dependency vulnerability check | PRs only |
| `safety-check` | Python package vulnerabilities | Always |
| `bandit` | Security linting | Always |
| `codeql` | Advanced code analysis | Always |

#### Security Checks Explained

**GitLeaks:**
- Scans git history for secrets
- Checks for API keys, tokens, passwords
- Prevents credential leaks
- Runs on full git history (`fetch-depth: 0`)

**Dependency Review:**
- Only runs on pull requests
- Reviews changes to dependencies
- Fails if moderate+ severity vulnerabilities added
- Uses GitHub's vulnerability database

**Safety Check:**
- Scans Python dependencies for CVEs
- Checks against safety database
- Reports vulnerabilities but doesn't fail CI
- Results shown in workflow logs

**Bandit:**
- Static analysis for Python security issues
- Checks for common security anti-patterns
- Uploads results as artifacts
- Examples: SQL injection, hardcoded passwords, insecure functions

**CodeQL:**
- GitHub's advanced code analysis
- Finds security vulnerabilities automatically
- Results appear in Security tab
- Uses extended security query pack

### Scheduled Runs

Security scans run weekly on Monday at 9am UTC:

```yaml
schedule:
  - cron: '0 9 * * 1'
```

This catches new vulnerabilities in dependencies even without code changes.

## Development Workflow

### Typical Development Flow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes and test locally**:
   ```bash
   # Run fast tests frequently
   make test

   # Run linter
   make lint

   # Auto-fix formatting
   make format
   ```

3. **Commit changes**:
   ```bash
   git add .
   git commit -m "Add feature X"
   ```
   Pre-commit hooks will run automatically if installed.

4. **Push and create PR**:
   ```bash
   git push origin feature/my-feature
   ```

5. **GitHub Actions runs**:
   - CI workflow runs all checks
   - Security workflow scans for issues
   - Status checks appear on PR

6. **Fix any failures**:
   - Check workflow logs for errors
   - Fix locally and push again
   - Workflows re-run automatically

7. **Merge when green**:
   - All checks must pass
   - Branch protection enforces this

### Interpreting CI Results

**Green checkmark (✓)**: All checks passed
- Safe to merge
- Code meets quality standards

**Red X (✗)**: Some checks failed
- Click "Details" to see logs
- Common issues:
  - Linting errors: Run `make format` and `make lint`
  - Test failures: Check test output, fix bugs
  - Type errors: Add type hints or update mypy config

**Yellow dot (●)**: Checks running
- Wait for completion
- Usually takes 3-5 minutes

**Gray dash (-)**: Check skipped
- Some checks only run on PRs or main branch
- Normal behavior

## Local Development Tools

### Makefile Targets

```bash
make help          # Show all available targets
make install       # Install dependencies
make test          # Run fast tests
make test-all      # Run all tests including slow
make test-slow     # Run only slow tests
make test-coverage # Run tests with coverage
make lint          # Run linting checks
make format        # Auto-format code
make check         # Run tests + lint
make clean         # Remove cache files
make clean-exports # Remove export files
```

### Pre-commit Hooks

Install once:
```bash
uv pip install pre-commit
pre-commit install
```

Runs automatically on `git commit`:
- Trailing whitespace removal
- End of file fixer
- YAML validation
- Large file check
- Merge conflict detection
- Debug statement detection
- Ruff linting and formatting
- Mypy type checking
- GitLeaks secret scanning

Run manually on all files:
```bash
pre-commit run --all-files
```

## Configuration Files

### `pyproject.toml`
- Project metadata
- Dependencies
- Pytest configuration
- Test markers (slow)

### `ruff.toml`
- Ruff linter configuration
- Code style rules
- Import sorting
- Line length (100)

### `.bandit`
- Bandit security scanner config
- Severity levels
- Excluded directories

### `.pre-commit-config.yaml`
- Pre-commit hook configuration
- Hook versions
- Hook arguments

## Troubleshooting

### "All Tests" Job Failing

The `test-all` job includes slow integration tests that may fail without GitHub authentication:

```yaml
continue-on-error: true  # This is expected
```

This is normal and won't block merging. The job runs to catch issues but doesn't fail CI.

### Linting Failures

**Problem**: Ruff reports formatting issues

**Solution**:
```bash
make format  # Auto-fix most issues
make lint    # Check what remains
```

**Common issues**:
- Line too long: Break into multiple lines
- Import sorting: Auto-fixed by ruff
- Unused imports: Remove or add `# noqa: F401`

### Coverage Too Low

**Problem**: Coverage check fails

**Solution**:
1. Add tests for untested code
2. Check coverage report: `make test-coverage`
3. Open `htmlcov/index.html` in browser
4. See which lines are uncovered

### Type Checking Failures

**Problem**: Mypy reports type errors

**Solution**:
1. Add type hints to function signatures
2. Import types: `from typing import List, Dict, Optional`
3. Or add `# type: ignore` comment (last resort)

The type-check job is optional (`continue-on-error: true`), so it won't block CI.

### Security Scan False Positives

**Problem**: Bandit reports false security issues

**Solution**:
1. Review the finding carefully
2. If truly false positive, add to `.bandit`:
   ```ini
   skips = B101,B601  # Skip assert_used, paramiko_calls
   ```
3. Document why it's safe in code comments

### Dependency Vulnerabilities

**Problem**: Safety or dependency-review finds CVEs

**Solution**:
1. Update affected package: `uv lock --upgrade`
2. Check if newer version fixes issue
3. If no fix available, assess risk
4. Consider alternative package
5. Document risk acceptance if needed

## Best Practices

### For Contributors

1. **Run tests locally before pushing**
   - Saves CI time
   - Faster feedback loop
   - `make test` is quick

2. **Use pre-commit hooks**
   - Catches issues before commit
   - Automatic formatting
   - Prevents pushing broken code

3. **Keep PRs small and focused**
   - Easier to review
   - Faster to merge
   - Less likely to fail CI

4. **Fix CI failures promptly**
   - Don't push more commits on failing PR
   - Fix the issue first
   - Keeps history clean

### For Maintainers

1. **Enforce branch protection**
   - Require "All Checks Passed"
   - Require up-to-date branches
   - Include administrators

2. **Review security findings**
   - Check Security tab weekly
   - Address CodeQL findings
   - Update vulnerable dependencies

3. **Monitor CI performance**
   - Check workflow run times
   - Optimize slow tests
   - Adjust caching strategy

4. **Keep actions up to date**
   - Dependabot for GitHub Actions
   - Update action versions quarterly
   - Test after updates

## Advanced Topics

### Adding New Checks

To add a new linting tool:

1. Add to `pyproject.toml` dev dependencies
2. Add job to `.github/workflows/ci.yml`
3. Add to `Makefile` for local use
4. Update documentation

Example:
```yaml
- name: Run new-tool
  run: uv run new-tool check .
```

### Customizing Test Matrix

To test additional Python versions:

```yaml
matrix:
  python-version: ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]
```

To test on multiple OS:

```yaml
matrix:
  os: [ubuntu-latest, macos-latest, windows-latest]
  python-version: ["3.8", "3.12"]
```

### Conditional Workflows

Run specific jobs only on certain conditions:

```yaml
if: github.event_name == 'pull_request'
if: github.ref == 'refs/heads/main'
if: contains(github.event.head_commit.message, '[skip-ci]')
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
- [pre-commit Documentation](https://pre-commit.com/)

## Support

For issues with CI/CD:

1. Check workflow logs for error messages
2. Review this documentation
3. Search GitHub Issues for similar problems
4. Open new issue with:
   - Workflow run URL
   - Error message
   - Steps to reproduce
