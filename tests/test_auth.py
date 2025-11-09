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
