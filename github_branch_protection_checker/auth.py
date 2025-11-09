"""Authentication module for GitHub API access"""
import subprocess


def get_github_token() -> str:
    """
    Retrieve GitHub authentication token from gh CLI.

    Returns:
        GitHub OAuth token

    Raises:
        RuntimeError: If gh CLI is not authenticated or token is empty
    """
    try:
        result = subprocess.run(
            ['gh', 'auth', 'token'],
            capture_output=True,
            text=True,
            check=True
        )
        token = result.stdout.strip()

        if not token:
            raise RuntimeError("Failed to obtain GitHub authentication token: token is empty")

        return token

    except subprocess.CalledProcessError as e:
        stderr_msg = getattr(e, 'stderr', 'No additional details available')
        raise RuntimeError(
            f"Error: GitHub CLI not authenticated. Run 'gh auth login' first.\n"
            f"Details: {stderr_msg}"
        ) from e
