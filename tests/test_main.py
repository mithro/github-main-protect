from unittest.mock import MagicMock, patch

from github_branch_protection_checker.__main__ import main


def test_main_success(capsys, tmp_path):
    """Test successful execution"""
    mock_repos = [
        MagicMock(
            name="repo1",
            owner="user",
            url="https://github.com/user/repo1",
            default_branch="main",
            is_private=False,
            is_fork=False,
            is_archived=False,
            has_protection=False,
            to_dict=lambda: {
                "name": "repo1",
                "owner": "user",
                "url": "https://github.com/user/repo1",
                "default_branch": "main",
                "is_private": False,
                "is_fork": False,
            },
        )
    ]

    with patch("github_branch_protection_checker.__main__.get_github_token") as mock_token:
        with patch("github_branch_protection_checker.__main__.GraphQLClient"):
            with patch(
                "github_branch_protection_checker.__main__.RepositoryFetcher"
            ) as mock_fetcher_class:
                mock_token.return_value = "test_token"

                mock_fetcher = MagicMock()
                mock_fetcher.fetch_all_repositories.return_value = mock_repos
                mock_fetcher_class.return_value = mock_fetcher

                # Run main
                result = main(output_dir=str(tmp_path))

                assert result == 0

                captured = capsys.readouterr()
                assert "Checking repositories" in captured.out
                assert "Total repositories: 1" in captured.out
                assert "Unprotected repositories: 1" in captured.out


def test_main_auth_failure(capsys):
    """Test authentication failure"""
    with patch("github_branch_protection_checker.__main__.get_github_token") as mock_token:
        mock_token.side_effect = RuntimeError("GitHub CLI not authenticated")

        result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "GitHub CLI not authenticated" in captured.err


def test_main_api_failure(capsys):
    """Test API error"""
    with patch("github_branch_protection_checker.__main__.get_github_token") as mock_token:
        with patch("github_branch_protection_checker.__main__.GraphQLClient"):
            with patch(
                "github_branch_protection_checker.__main__.RepositoryFetcher"
            ) as mock_fetcher_class:
                mock_token.return_value = "test_token"

                mock_fetcher = MagicMock()
                mock_fetcher.fetch_all_repositories.side_effect = RuntimeError("API error")
                mock_fetcher_class.return_value = mock_fetcher

                result = main()

                assert result == 1
                captured = capsys.readouterr()
                assert "API error" in captured.err
