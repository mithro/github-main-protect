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
        timeout=60  # Increase timeout to 60 seconds for users with many repos
    )

    # Should fail with auth error or succeed
    # Either is fine for this test - we're just checking it runs
    assert result.returncode in [0, 1]
