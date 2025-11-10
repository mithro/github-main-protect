"""Output formatters for repository data"""
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List
from .models import Repository


def format_console_output(
    unprotected_repos: List[Repository],
    total_repos: int,
    archived_count: int,
    no_branch_count: int
) -> str:
    """
    Format repositories for console output.

    Args:
        unprotected_repos: List of unprotected repositories
        total_repos: Total number of repositories checked
        archived_count: Number of archived repos skipped
        no_branch_count: Number of repos without default branch

    Returns:
        Formatted string for console output
    """
    lines = []
    lines.append("\nSummary:")
    lines.append(f"- Total repositories: {total_repos}")
    lines.append(f"- Archived (skipped): {archived_count}")
    lines.append(f"- No default branch (skipped): {no_branch_count}")
    lines.append(f"- Unprotected repositories: {len(unprotected_repos)}")

    if unprotected_repos:
        lines.append("\nUnprotected Repositories:")
        lines.append("┌─────────────────────────────────────┬──────────────┬─────────┬──────┐")
        lines.append("│ Repository                          │ Branch       │ Private │ Fork │")
        lines.append("├─────────────────────────────────────┼──────────────┼─────────┼──────┤")

        for repo in unprotected_repos:
            full_name = f"{repo.owner}/{repo.name}"
            full_name_display = f"{full_name[:32]}..." if len(full_name) > 35 else f"{full_name:<35}"
            branch = repo.default_branch or "N/A"
            branch_display = f"{branch[:9]}..." if len(branch) > 12 else f"{branch:<12}"
            private = "Yes" if repo.is_private else "No"
            fork = "Yes" if repo.is_fork else "No"

            lines.append(
                f"│ {full_name_display} │ {branch_display} │ {private:<7} │ {fork:<4} │"
            )

        lines.append("└─────────────────────────────────────┴──────────────┴─────────┴──────┘")

    return "\n".join(lines)


def export_to_json(
    unprotected_repos: List[Repository],
    total_repos: int,
    archived_count: int,
    no_branch_count: int,
    output_dir: str = "."
) -> str:
    """
    Export repositories to JSON file.

    Args:
        unprotected_repos: List of unprotected repositories
        total_repos: Total number of repositories checked
        archived_count: Number of archived repos skipped
        no_branch_count: Number of repos without default branch
        output_dir: Directory to write file to

    Returns:
        Path to created file
    """
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S-%f")
    filename = f"unprotected-repos-{timestamp}.json"
    filepath = Path(output_dir) / filename

    data = {
        'summary': {
            'total_repositories': total_repos,
            'archived_skipped': archived_count,
            'no_branch_skipped': no_branch_count,
            'unprotected_count': len(unprotected_repos)
        },
        'unprotected_repositories': [repo.to_dict() for repo in unprotected_repos]
    }

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    return str(filepath)


def export_to_csv(unprotected_repos: List[Repository], output_dir: str = ".") -> str:
    """
    Export repositories to CSV file.

    Args:
        unprotected_repos: List of unprotected repositories
        output_dir: Directory to write file to

    Returns:
        Path to created file
    """
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S-%f")
    filename = f"unprotected-repos-{timestamp}.csv"
    filepath = Path(output_dir) / filename

    with open(filepath, 'w', newline='') as f:
        fieldnames = ['name', 'owner', 'url', 'default_branch', 'is_private', 'is_fork']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for repo in unprotected_repos:
            writer.writerow(repo.to_dict())

    return str(filepath)


def export_to_markdown(
    unprotected_repos: List[Repository],
    total_repos: int,
    archived_count: int,
    no_branch_count: int,
    output_dir: str = "."
) -> str:
    """
    Export repositories to Markdown file.

    Args:
        unprotected_repos: List of unprotected repositories
        total_repos: Total number of repositories checked
        archived_count: Number of archived repos skipped
        no_branch_count: Number of repos without default branch
        output_dir: Directory to write file to

    Returns:
        Path to created file
    """
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S-%f")
    filename = f"unprotected-repos-{timestamp}.md"
    filepath = Path(output_dir) / filename

    lines = []
    lines.append("# GitHub Branch Protection Report")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("\n## Summary")
    lines.append(f"\n- Total repositories: {total_repos}")
    lines.append(f"- Archived (skipped): {archived_count}")
    lines.append(f"- No default branch (skipped): {no_branch_count}")
    lines.append(f"- Unprotected repositories: {len(unprotected_repos)}")

    if unprotected_repos:
        lines.append("\n## Unprotected Repositories")
        lines.append("\n| Repository | Branch | Private | Fork | URL |")
        lines.append("|------------|--------|---------|------|-----|")

        for repo in unprotected_repos:
            full_name = f"{repo.owner}/{repo.name}"
            branch = repo.default_branch or "N/A"
            private = "Yes" if repo.is_private else "No"
            fork = "Yes" if repo.is_fork else "No"

            lines.append(
                f"| {full_name} | {branch} | {private} | {fork} | "
                f"[{full_name}]({repo.url}) |"
            )

    with open(filepath, 'w') as f:
        f.write("\n".join(lines))

    return str(filepath)
