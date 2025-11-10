"""Main entry point for GitHub branch protection checker"""
import sys
from typing import Optional
from .auth import get_github_token
from .graphql_client import GraphQLClient
from .fetcher import RepositoryFetcher
from .formatters import (
    format_console_output,
    export_to_json,
    export_to_csv,
    export_to_markdown
)


def main(output_dir: str = ".") -> int:
    """
    Main entry point for the script.

    Args:
        output_dir: Directory to write export files to

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Get authentication token
        print("Checking repositories...")
        token = get_github_token()

        # Create client and fetcher
        client = GraphQLClient(token)
        fetcher = RepositoryFetcher(client)

        # Fetch all repositories
        all_repos = fetcher.fetch_all_repositories()
        print(f"Found {len(all_repos)} repositories owned by you")

        # Filter repositories
        unprotected = []
        archived_count = 0
        no_branch_count = 0

        for repo in all_repos:
            if repo.is_archived:
                archived_count += 1
                continue

            if repo.default_branch is None:
                no_branch_count += 1
                continue

            if not repo.has_protection:
                unprotected.append(repo)

        # Display console output
        console_output = format_console_output(
            unprotected_repos=unprotected,
            total_repos=len(all_repos),
            archived_count=archived_count,
            no_branch_count=no_branch_count
        )
        print(console_output)

        # Export to files
        if unprotected or True:  # Always create exports
            json_file = export_to_json(
                unprotected_repos=unprotected,
                total_repos=len(all_repos),
                archived_count=archived_count,
                no_branch_count=no_branch_count,
                output_dir=output_dir
            )
            print(f"\nExported to JSON: {json_file}")

            csv_file = export_to_csv(unprotected, output_dir=output_dir)
            print(f"Exported to CSV: {csv_file}")

            md_file = export_to_markdown(
                unprotected_repos=unprotected,
                total_repos=len(all_repos),
                archived_count=archived_count,
                no_branch_count=no_branch_count,
                output_dir=output_dir
            )
            print(f"Exported to Markdown: {md_file}")

        return 0

    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: Unexpected error occurred: {str(e)}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
