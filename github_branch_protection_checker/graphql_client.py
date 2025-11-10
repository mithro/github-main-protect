"""GraphQL client for GitHub API"""

from typing import Any, Dict, Optional

import requests


class GraphQLClient:
    """Client for executing GraphQL queries against GitHub API"""

    GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

    def __init__(self, token: str):
        """
        Initialize GraphQL client.

        Args:
            token: GitHub OAuth token
        """
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Optional query variables

        Returns:
            Response data dictionary

        Raises:
            RuntimeError: On HTTP errors, GraphQL errors, or network failures
        """
        payload: Dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = requests.post(
                self.GITHUB_GRAPHQL_URL, json=payload, headers=self.headers, timeout=30
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"Error: GitHub API request failed with status {response.status_code}: "
                    f"{response.text}"
                )

            result = response.json()

            if "errors" in result:
                error_messages = [err["message"] for err in result["errors"]]
                raise RuntimeError(f"Error: GitHub API returned GraphQL error: {error_messages[0]}")

            return result["data"]

        except requests.ConnectionError as e:
            raise RuntimeError(f"Error: Failed to connect to GitHub API: {e!s}") from e
