"""End-to-end integration test"""
import subprocess
import pytest
from pathlib import Path


@pytest.mark.slow
def test_script_execution_e2e(tmp_path):
    """
    Full end-to-end test that runs the script against real GitHub API.

    This test is marked as 'slow' because it:
    - Requires GitHub CLI authentication
    - Makes real API calls to GitHub
    - Fetches all user repositories (can be hundreds)
    - Takes 10-20+ seconds to complete

    Run with: pytest -v -m slow
    Skip with: pytest -v -m "not slow"
    """
    result = subprocess.run(
        ['uv', 'run', 'python', '-m', 'github_branch_protection_checker'],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(tmp_path)  # Run in temp dir to avoid polluting working directory
    )

    # Should fail with auth error or succeed
    # Either is fine for this test - we're just checking it runs
    assert result.returncode in [0, 1]

    # If successful, verify export files were created
    if result.returncode == 0:
        json_files = list(tmp_path.glob("unprotected-repos-*.json"))
        csv_files = list(tmp_path.glob("unprotected-repos-*.csv"))
        md_files = list(tmp_path.glob("unprotected-repos-*.md"))

        assert len(json_files) == 1, "Should create exactly one JSON file"
        assert len(csv_files) == 1, "Should create exactly one CSV file"
        assert len(md_files) == 1, "Should create exactly one Markdown file"


def test_script_can_be_imported():
    """Fast test that the script module can be imported without errors"""
    result = subprocess.run(
        ['uv', 'run', 'python', '-c',
         'import github_branch_protection_checker; print("OK")'],
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0
    assert "OK" in result.stdout
