from github_branch_protection_checker.models import Repository, is_protected


def test_repository_from_graphql():
    """Test creating Repository from GraphQL response"""
    graphql_data = {
        "name": "test-repo",
        "owner": {"login": "testuser"},
        "url": "https://github.com/testuser/test-repo",
        "defaultBranchRef": {
            "name": "main",
            "branchProtectionRule": None,
            "refUpdateRule": None,
            "rules": {"totalCount": 0},
        },
        "isPrivate": True,
        "isFork": False,
        "isArchived": False,
    }

    repo = Repository.from_graphql(graphql_data)

    assert repo.name == "test-repo"
    assert repo.owner == "testuser"
    assert repo.url == "https://github.com/testuser/test-repo"
    assert repo.default_branch == "main"
    assert repo.is_private is True
    assert repo.is_fork is False
    assert repo.is_archived is False
    assert repo.has_protection is False


def test_repository_with_branch_protection_rule():
    """Test repository with old branch protection rules"""
    graphql_data = {
        "name": "protected-repo",
        "owner": {"login": "testuser"},
        "url": "https://github.com/testuser/protected-repo",
        "defaultBranchRef": {
            "name": "main",
            "branchProtectionRule": {"id": "BPR_123"},
            "refUpdateRule": None,
            "rules": {"totalCount": 0},
        },
        "isPrivate": False,
        "isFork": False,
        "isArchived": False,
    }

    repo = Repository.from_graphql(graphql_data)
    assert repo.has_protection is True


def test_repository_with_ref_update_rule():
    """Test repository with refUpdateRule protection"""
    graphql_data = {
        "name": "protected-repo",
        "owner": {"login": "testuser"},
        "url": "https://github.com/testuser/protected-repo",
        "defaultBranchRef": {
            "name": "main",
            "branchProtectionRule": None,
            "refUpdateRule": {"id": "RUR_123"},
            "rules": {"totalCount": 0},
        },
        "isPrivate": False,
        "isFork": False,
        "isArchived": False,
    }

    repo = Repository.from_graphql(graphql_data)
    assert repo.has_protection is True


def test_repository_with_rulesets():
    """Test repository with new ruleset protection"""
    graphql_data = {
        "name": "protected-repo",
        "owner": {"login": "testuser"},
        "url": "https://github.com/testuser/protected-repo",
        "defaultBranchRef": {
            "name": "main",
            "branchProtectionRule": None,
            "refUpdateRule": None,
            "rules": {"totalCount": 2},
        },
        "isPrivate": False,
        "isFork": False,
        "isArchived": False,
    }

    repo = Repository.from_graphql(graphql_data)
    assert repo.has_protection is True


def test_repository_no_default_branch():
    """Test repository without default branch"""
    graphql_data = {
        "name": "empty-repo",
        "owner": {"login": "testuser"},
        "url": "https://github.com/testuser/empty-repo",
        "defaultBranchRef": None,
        "isPrivate": False,
        "isFork": False,
        "isArchived": False,
    }

    repo = Repository.from_graphql(graphql_data)
    assert repo.default_branch is None
    assert repo.has_protection is False


def test_repository_to_dict():
    """Test converting repository to dictionary"""
    graphql_data = {
        "name": "test-repo",
        "owner": {"login": "testuser"},
        "url": "https://github.com/testuser/test-repo",
        "defaultBranchRef": {
            "name": "main",
            "branchProtectionRule": None,
            "refUpdateRule": None,
            "rules": {"totalCount": 0},
        },
        "isPrivate": True,
        "isFork": True,
        "isArchived": False,
    }

    repo = Repository.from_graphql(graphql_data)
    result = repo.to_dict()

    assert result == {
        "name": "test-repo",
        "owner": "testuser",
        "url": "https://github.com/testuser/test-repo",
        "default_branch": "main",
        "is_private": True,
        "is_fork": True,
    }


def test_is_protected_function():
    """Test standalone is_protected function"""
    # No protection
    ref = {"branchProtectionRule": None, "refUpdateRule": None, "rules": {"totalCount": 0}}
    assert is_protected(ref) is False

    # Has branch protection rule
    ref = {"branchProtectionRule": {"id": "123"}, "refUpdateRule": None, "rules": {"totalCount": 0}}
    assert is_protected(ref) is True

    # Has ref update rule
    ref = {"branchProtectionRule": None, "refUpdateRule": {"id": "123"}, "rules": {"totalCount": 0}}
    assert is_protected(ref) is True

    # Has rulesets
    ref = {"branchProtectionRule": None, "refUpdateRule": None, "rules": {"totalCount": 1}}
    assert is_protected(ref) is True
