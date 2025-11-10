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


def test_repo_query_contains_required_fields():
    """Test that REPO_QUERY contains all required fields for protection detection"""
    # Protection detection fields
    assert 'branchProtectionRule' in REPO_QUERY
    assert 'refUpdateRule' in REPO_QUERY
    assert 'rules(first: 1)' in REPO_QUERY
    assert 'totalCount' in REPO_QUERY

    # Pagination fields
    assert 'pageInfo' in REPO_QUERY
    assert 'hasNextPage' in REPO_QUERY
    assert 'endCursor' in REPO_QUERY

    # Filtering
    assert 'ownerAffiliations: OWNER' in REPO_QUERY
