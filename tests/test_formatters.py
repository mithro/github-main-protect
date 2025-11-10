import json
import csv
from pathlib import Path
from github_branch_protection_checker.formatters import (
    format_console_output,
    export_to_json,
    export_to_csv,
    export_to_markdown
)
from github_branch_protection_checker.models import Repository


def create_test_repo(name: str, protected: bool = False) -> Repository:
    """Helper to create test repository"""
    return Repository(
        name=name,
        owner='testuser',
        url=f'https://github.com/testuser/{name}',
        default_branch='main',
        is_private=False,
        is_fork=False,
        is_archived=False,
        has_protection=protected
    )


def test_format_console_output():
    """Test console output formatting"""
    unprotected = [
        create_test_repo('repo1'),
        create_test_repo('repo2')
    ]

    output = format_console_output(
        unprotected_repos=unprotected,
        total_repos=10,
        archived_count=2,
        no_branch_count=1
    )

    assert 'Total repositories: 10' in output
    assert 'Archived (skipped): 2' in output
    assert 'No default branch (skipped): 1' in output
    assert 'Unprotected repositories: 2' in output
    assert 'repo1' in output
    assert 'repo2' in output
    assert 'testuser' in output


def test_export_to_json(tmp_path):
    """Test JSON export"""
    unprotected = [
        create_test_repo('repo1'),
        create_test_repo('repo2')
    ]

    filepath = export_to_json(
        unprotected_repos=unprotected,
        total_repos=10,
        archived_count=2,
        no_branch_count=1,
        output_dir=str(tmp_path)
    )

    assert Path(filepath).exists()
    assert filepath.startswith(str(tmp_path))
    assert 'unprotected-repos-' in filepath
    assert filepath.endswith('.json')

    with open(filepath, 'r') as f:
        data = json.load(f)

    assert data['summary']['total_repositories'] == 10
    assert data['summary']['archived_skipped'] == 2
    assert data['summary']['no_branch_skipped'] == 1
    assert data['summary']['unprotected_count'] == 2
    assert len(data['unprotected_repositories']) == 2
    assert data['unprotected_repositories'][0]['name'] == 'repo1'


def test_export_to_csv(tmp_path):
    """Test CSV export"""
    unprotected = [
        Repository(
            name='repo1',
            owner='testuser',
            url='https://github.com/testuser/repo1',
            default_branch='main',
            is_private=True,
            is_fork=False,
            is_archived=False,
            has_protection=False
        ),
        Repository(
            name='repo2',
            owner='testuser',
            url='https://github.com/testuser/repo2',
            default_branch='master',
            is_private=False,
            is_fork=True,
            is_archived=False,
            has_protection=False
        )
    ]

    filepath = export_to_csv(unprotected, output_dir=str(tmp_path))

    assert Path(filepath).exists()
    assert filepath.endswith('.csv')

    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]['name'] == 'repo1'
    assert rows[0]['owner'] == 'testuser'
    assert rows[0]['default_branch'] == 'main'
    assert rows[0]['is_private'] == 'True'
    assert rows[0]['is_fork'] == 'False'
    assert rows[1]['name'] == 'repo2'


def test_export_to_markdown(tmp_path):
    """Test Markdown export"""
    unprotected = [
        create_test_repo('repo1'),
        create_test_repo('repo2')
    ]

    filepath = export_to_markdown(
        unprotected_repos=unprotected,
        total_repos=10,
        archived_count=2,
        no_branch_count=1,
        output_dir=str(tmp_path)
    )

    assert Path(filepath).exists()
    assert filepath.endswith('.md')

    with open(filepath, 'r') as f:
        content = f.read()

    assert '# GitHub Branch Protection Report' in content
    assert 'Total repositories: 10' in content
    assert 'Archived (skipped): 2' in content
    assert 'Unprotected repositories: 2' in content
    assert '| Repository |' in content
    assert '| testuser/repo1 |' in content
    assert '[testuser/repo1](https://github.com/testuser/repo1)' in content


def test_export_empty_list(tmp_path):
    """Test exports with empty repository list"""
    filepath = export_to_json(
        unprotected_repos=[],
        total_repos=5,
        archived_count=0,
        no_branch_count=0,
        output_dir=str(tmp_path)
    )

    with open(filepath, 'r') as f:
        data = json.load(f)

    assert data['summary']['unprotected_count'] == 0
    assert data['unprotected_repositories'] == []
